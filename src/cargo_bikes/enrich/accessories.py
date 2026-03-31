"""Extract and generate accessory notes from bike note markdown tables."""

from __future__ import annotations

import asyncio
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from cargo_bikes.enrich.agent import call_agent, run_concurrent
from cargo_bikes.enrich.prompts import ACCESSORY_NOTE_SYSTEM
from cargo_bikes.enrich.review import ReviewItem, run_review_session


def _slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


# Keyword → category mapping
_CATEGORY_KEYWORDS = {
    "child-seats": [
        "child seat",
        "baby seat",
        "yepp",
        "maxi",
        "mini seat",
        "passenger seat",
    ],
    "panniers": ["pannier", "side bag", "cargo hold"],
    "racks": ["rack", "hauler", "transporteur", "front rack", "rear rack"],
    "weather-protection": [
        "rain",
        "storm",
        "shelter",
        "shield",
        "canopy",
        "weather",
        "pop shelter",
    ],
    "cargo-bags": ["cargo bag", "basket", "cargo net", "carry all", "boards"],
    "pet-carriers": ["pet", "ruffhouse", "dog"],
    "towing": ["tow", "hitch", "trailer"],
    "lighting": ["light", "nitelite", "lamp"],
    "footrests": ["footrest", "foot peg", "monkey bar", "sidekick"],
    "safety": ["harness", "safety", "seat belt", "strap"],
}


# Words that indicate a row is a spec/feature, not an accessory
_EXCLUDE_KEYWORDS = [
    "motor",
    "battery",
    "range",
    "weight",
    "frame",
    "brakes",
    "wheel",
    "drivetrain",
    "transmission",
    "suspension",
    "display",
    "charger",
    "charging",
    "specification",
    "category",
    "feature",
    "durability",
    "maneuverability",
    "capacity",
    "recency",
    "information",
    "limited",
    "component",
    "manufacturer",
    "delivery",
    "warranty",
    "return",
    "certification",
    "parking",
    "learning",
    "comfort",
    "urban",
    "total load",
    "total equipped",
    "total investment",
    "assist level",
    "simplicity",
    "long wheelbase",
    "shipping",
    "attachment",
    "strong power",
    "seamless",
    "excellent",
    "durable",
    "high-load",
    "high-capacity",
    "space-efficient",
    "well-equipped",
    "no front",
    "long-term",
    "limited community",
    "og ",
    "shorty ",
]

# Generic labels that are categories, not specific products
_GENERIC_NAMES = {
    "lighting",
    "lights",
    "cargo basket",
    "cargo bags",
    "child seat",
    "child seats",
    "weather protection",
    "rear rack",
    "front rack",
    "panniers",
    "footrests",
    "safety",
    "comfort",
    "racks",
}


def _categorize_accessory(name: str) -> str:
    """Guess accessory category from its name. Returns empty string to exclude."""
    name_lower = name.lower()

    # Exclude non-accessories
    for excl in _EXCLUDE_KEYWORDS:
        if excl in name_lower:
            return ""

    # Exclude generic category labels (not specific products)
    if name_lower.strip() in _GENERIC_NAMES:
        return ""

    for category, keywords in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return category
    return ""  # Return empty to exclude uncategorized items


def _parse_accessory_table(content: str) -> list[dict[str, str]]:
    """Parse markdown tables in accessory sections.

    Looks for tables after headings containing 'Accessories' or 'Options'.
    Returns list of {name, price, description} dicts.
    """
    accessories: list[dict[str, str]] = []

    # Find sections with accessories
    section_pattern = re.compile(
        r"##\s+.*(?:Accessories|Options|Customization).*?\n(.*?)(?=\n##\s|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    for section_match in section_pattern.finditer(content):
        section_text = section_match.group(1)

        # Parse markdown table rows: | Name | Price | Description |
        table_row_pattern = re.compile(
            r"^\|\s*\*?\*?([^|]+?)\*?\*?\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|",
            re.MULTILINE,
        )

        for row_match in table_row_pattern.finditer(section_text):
            name = row_match.group(1).strip().strip("*")
            price = row_match.group(2).strip()
            desc = row_match.group(3).strip()

            # Skip header rows and separators
            if name.lower() in ("accessory", "option", "name", "---", ""):
                continue
            if set(name) <= {"-", " ", "|"}:
                continue

            accessories.append(
                {
                    "name": name,
                    "price": price,
                    "description": desc,
                }
            )

        # Also parse list items: - **Name:** Description (~€Price)
        list_pattern = re.compile(
            r"^\s*[-*]\s+\*\*([^*]+)\*\*[:\s]*([^(]*?)(?:\(~?([€$£]?\d[\d,.]*)\))?$",
            re.MULTILINE,
        )

        for list_match in list_pattern.finditer(section_text):
            name = list_match.group(1).strip()
            desc = list_match.group(2).strip().rstrip("—- ")
            price = list_match.group(3) or ""

            if name.lower() not in ("accessory", "option", "note"):
                accessories.append(
                    {
                        "name": name,
                        "price": price.strip(),
                        "description": desc,
                    }
                )

    return accessories


def scan_accessories(
    vault_path: Path,
    brand: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Scan bike notes for accessories, grouping by accessory name.

    Returns dict of {accessory_name: {name, category, prices, bikes, descriptions}}.
    """
    bikes_dir = vault_path / "notes" / "bikes"
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "name": "",
            "category": "",
            "prices": [],
            "bikes": [],
            "brands": [],
            "descriptions": [],
        }
    )

    dirs = [bikes_dir / brand] if brand else sorted(bikes_dir.iterdir())

    for brand_dir in dirs:
        if not brand_dir.is_dir():
            continue

        for md_file in sorted(brand_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Get bike title from frontmatter
            title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
            bike_title = (
                title_match.group(1).strip().strip("\"'")
                if title_match
                else md_file.stem
            )

            accessories = _parse_accessory_table(content)
            for acc in accessories:
                cat = _categorize_accessory(acc["name"])
                if not cat:  # Skip non-accessories
                    continue
                key = acc["name"]
                entry = grouped[key]
                entry["name"] = acc["name"]
                entry["category"] = entry["category"] or cat
                if acc["price"]:
                    entry["prices"].append(acc["price"])
                entry["bikes"].append(bike_title)
                entry["brands"].append(brand_dir.name)
                if (
                    acc["description"]
                    and acc["description"] not in entry["descriptions"]
                ):
                    entry["descriptions"].append(acc["description"])

    return dict(grouped)


# Known third-party accessory manufacturers — always universal
_THIRD_PARTY_BRANDS = {
    "yepp",
    "bobike",
    "thule",
    "polisport",
    "urban iki",
    "guppy",
    "abus",
    "kryptonite",
    "schwalbe",
    "ortlieb",
    "basil",
    "klickfix",
    "mik",
    "shimano",
    "bosch",
    "supernova",
}


def _is_brand_specific(data: dict[str, Any]) -> tuple[bool, str]:
    """Determine if accessory is brand-specific or universal.

    An accessory is universal if:
    - Used by bikes from multiple brands, OR
    - Its name contains a known third-party accessory brand

    Returns (is_brand_specific, brand_folder_name).
    """
    name_lower = data.get("name", "").lower()

    # Check for third-party brand names in the accessory name
    for tp_brand in _THIRD_PARTY_BRANDS:
        if tp_brand in name_lower:
            return False, ""

    unique_brands = list(set(data.get("brands", [])))
    if len(unique_brands) == 1:
        return True, unique_brands[0]
    return False, ""


async def _generate_accessory_note(
    name: str,
    data: dict[str, Any],
    model: str,
) -> dict[str, str]:
    """Generate a single accessory note."""
    bikes_list = "\n".join(f"- [[{b}]]" for b in data["bikes"][:10])
    prices = ", ".join(data["prices"][:5]) if data["prices"] else "Unknown"
    descs = (
        "; ".join(data["descriptions"][:3])
        if data["descriptions"]
        else "No description"
    )

    is_specific, brand_folder = _is_brand_specific(data)
    acc_type = "brand-specific" if is_specific else "universal"
    manufacturer_hint = (
        f"Manufacturer: {brand_folder.replace('-', ' ').title()} (bike brand)"
        if is_specific
        else "Manufacturer: third-party accessory maker"
    )

    prompt = f"""Create an accessory note:

Title: {name}
Category: {data["category"]}
Type: accessory
Accessory type: {acc_type}
{manufacturer_hint}
Prices found: {prices}
Description: {descs}

Compatible bikes:
{bikes_list}

Generate a complete Obsidian markdown note with flat frontmatter.
"""

    result = await call_agent(
        prompt=prompt,
        system=ACCESSORY_NOTE_SYSTEM,
        model=model,
        max_turns=4,
    )

    return {
        "name": name,
        "slug": _slugify(name),
        "category": data["category"],
        "content": result.strip(),
        "brand_specific": is_specific,
        "brand_folder": brand_folder,
    }


def generate_accessories(
    vault_path: Path = Path("vault"),
    brand: str | None = None,
    category: str = "all",
    auto: bool = False,
    dry_run: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    """Extract accessories from bike notes and generate individual notes.

    Args:
        vault_path: Path to vault root.
        brand: If set, only scan this brand.
        category: Filter by category or "all".
        auto: Skip interactive review.
        dry_run: Show what would be generated.
        model: Claude model to use.
    """
    from rich.console import Console

    console = Console()

    # Scan bike notes for accessories
    console.print("[bold]Scanning bike notes for accessories...[/bold]")
    all_accessories = scan_accessories(vault_path, brand=brand)

    if category != "all":
        all_accessories = {
            k: v for k, v in all_accessories.items() if v["category"] == category
        }

    console.print(f"Found [bold]{len(all_accessories)}[/bold] unique accessories")

    if not all_accessories:
        return

    # Skip existing notes
    def _note_exists(data: dict[str, Any], slug: str) -> bool:
        is_specific, brand_folder = _is_brand_specific(data)
        if is_specific:
            path = (
                vault_path
                / "notes"
                / "bikes"
                / brand_folder
                / "accessories"
                / f"{slug}.md"
            )
        else:
            path = (
                vault_path / "notes" / "accessories" / data["category"] / f"{slug}.md"
            )
        return path.exists() and path.stat().st_size > 10

    to_generate = {
        k: v for k, v in all_accessories.items() if not _note_exists(v, _slugify(k))
    }

    console.print(
        f"  {len(to_generate)} new, {len(all_accessories) - len(to_generate)} already exist"
    )

    if dry_run:
        for name, data in sorted(to_generate.items()):
            console.print(
                f"  [dim]Would create: {data['category']}/{_slugify(name)}.md "
                f"(used by {len(data['bikes'])} bikes)[/dim]"
            )
        return

    if not to_generate:
        return

    # Generate notes
    async def _generate_all() -> list[dict[str, str]]:
        items = list(to_generate.items())

        async def gen(item: tuple[str, dict[str, Any]]) -> dict[str, str]:
            name, data = item
            return await _generate_accessory_note(name, data, model)

        return await run_concurrent(
            items=items,
            worker_fn=gen,
            concurrency=3,
            on_progress=lambda: console.print(".", end=""),
        )

    console.print(f"Generating {len(to_generate)} accessory notes...")
    notes = asyncio.run(_generate_all())
    console.print()

    # Filter out empty results
    notes = [n for n in notes if n["content"]]

    if not notes:
        console.print("[yellow]No notes generated (all empty)[/yellow]")
        return

    # Review
    if auto:
        accepted = notes
    else:
        review_items = [
            ReviewItem(
                data=note,
                label=f"{note['category']}/{note['name']}",
                diff=note["content"][:300] + "...",
            )
            for note in notes
        ]
        accepted, _ = run_review_session(
            review_items, console=console, entity_label="accessory"
        )

    # Write accepted notes to correct location
    brand_count = 0
    universal_count = 0
    for note in accepted:
        if note.get("brand_specific") and note.get("brand_folder"):
            # Brand-specific: vault/notes/bikes/<brand>/accessories/<slug>.md
            out_dir = (
                vault_path / "notes" / "bikes" / note["brand_folder"] / "accessories"
            )
            brand_count += 1
        else:
            # Universal: vault/notes/accessories/<category>/<slug>.md
            out_dir = vault_path / "notes" / "accessories" / note["category"]
            universal_count += 1

        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{note['slug']}.md"
        output_path.write_text(note["content"] + "\n", encoding="utf-8")
        console.print(f"[green]✓ {output_path}[/green]")

    console.print(
        f"  [dim]{brand_count} brand-specific, {universal_count} universal[/dim]"
    )

    console.print(f"\n[bold]Generated {len(accepted)} accessory notes[/bold]")
