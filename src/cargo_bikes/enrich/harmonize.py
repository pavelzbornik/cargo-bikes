"""Harmonize vault notes: extract missing frontmatter fields + convert wikilinks.

Two-pass approach:
1. Field extraction (Claude structured output) — fills missing frontmatter from body
2. Wikilink conversion (deterministic regex) — converts [text](path.md) to [[title]]
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from cargo_bikes.enrich.agent import extract_structured
from cargo_bikes.enrich.prompts import EXTRACT_SYSTEM
from cargo_bikes.enrich.schemas import BikeExtraction, BrandExtraction
from cargo_bikes.vault.frontmatter import extract_frontmatter


def _strip_frontmatter(content: str) -> str:
    """Return body content without YAML frontmatter."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    return content[match.end() :] if match else content


def _extract_one(
    file_path: Path,
    model: str,
) -> dict[str, Any] | None:
    """Extract missing fields from a single note using Claude structured output.

    Returns dict with file_path, extracted fields, and title, or None if nothing to extract.
    """
    content = file_path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        return None

    note_type = frontmatter.get("type", "")
    if note_type == "bike":
        schema = BikeExtraction
    elif note_type in ("brand", "brand-index"):
        schema = BrandExtraction
    else:
        return None

    # Find which fields are already filled
    filled = {
        k for k, v in frontmatter.items() if v is not None and v != "" and v != []
    }

    body = _strip_frontmatter(content)
    if not body.strip():
        return None

    # Truncate body to avoid Agent SDK issues with very long content
    body_truncated = body[:6000] if len(body) > 6000 else body

    prompt = f"""Extract data from this cargo bike note body.
Only extract fields you find clear evidence for. Leave as null if not found.

Fields already filled (skip these): {", ".join(sorted(filled))}

Note body:
{body_truncated}
"""

    try:
        extracted = extract_structured(
            prompt=prompt,
            system=EXTRACT_SYSTEM,
            output_schema=schema,
            model=model,
        )
    except Exception as e:
        print(f"  [WARN] Extraction failed for {file_path.name}: {e}")
        return None

    # Get only non-null fields that aren't already in frontmatter
    raw = extracted.model_dump()
    new_fields = {}
    for k, v in raw.items():
        if v is not None and k not in filled:
            # Normalize: if schema expects list but got string, split on comma
            if isinstance(v, str) and k in ("categories",):
                v = [x.strip() for x in v.split(",")]
            new_fields[k] = v

    if not new_fields:
        return None

    return {
        "file_path": file_path,
        "extracted": new_fields,
        "title": frontmatter.get("title", file_path.stem),
    }


def _apply_extracted_fields(file_path: Path, extracted: dict[str, Any]) -> None:
    """Merge extracted fields into existing frontmatter without touching body."""
    content = file_path.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        return

    fm = yaml.safe_load(fm_match.group(1))
    if not isinstance(fm, dict):
        return

    body = content[fm_match.end() :]

    # Merge: only add fields that don't already exist or are empty
    for key, value in extracted.items():
        if key not in fm or fm[key] is None or fm[key] == "":
            fm[key] = value

    new_fm = yaml.dump(
        fm, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    file_path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")


def _convert_wikilinks(file_path: Path) -> bool:
    """Convert internal markdown links to wikilinks in body only.

    Converts [text](relative/path.md) → [[text]]
    Preserves external URLs (http/https).
    Returns True if any changes were made.
    """
    content = file_path.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        return False

    header = content[: fm_match.end()]
    body = content[fm_match.end() :]

    # Convert [text](path.md) to [[text]] — only for relative .md links
    new_body = re.sub(
        r"\[([^\]]+)\]\((?!https?://|mailto:)([^)]+\.md)\)",
        lambda m: f"[[{m.group(1)}]]",
        body,
    )

    if new_body == body:
        return False

    file_path.write_text(header + new_body, encoding="utf-8")
    return True


def harmonize_notes(
    vault_path: Path,
    brand: str | None = None,
    dry_run: bool = False,
    auto: bool = False,
    wikilinks: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    """Harmonize vault notes: extract missing fields + optionally convert wikilinks.

    Args:
        vault_path: Path to vault root.
        brand: If set, only process this brand.
        dry_run: Show what would change without writing.
        auto: Skip interactive review.
        wikilinks: Also convert markdown links to wikilinks in body.
        model: Claude model to use.
    """
    from rich.console import Console

    from cargo_bikes.enrich.review import ReviewItem, run_review_session

    console = Console()

    # Collect notes
    bikes_dir = vault_path / "notes" / "bikes"
    notes: list[Path] = []

    if brand:
        brand_dir = bikes_dir / brand
        if brand_dir.exists():
            notes.extend(sorted(brand_dir.glob("*.md")))
            acc_dir = brand_dir / "accessories"
            if acc_dir.exists():
                notes.extend(sorted(acc_dir.glob("*.md")))
    else:
        for brand_dir in sorted(bikes_dir.iterdir()):
            if brand_dir.is_dir():
                notes.extend(sorted(brand_dir.glob("*.md")))
                acc_dir = brand_dir / "accessories"
                if acc_dir.exists():
                    notes.extend(sorted(acc_dir.glob("*.md")))

        acc_dir = vault_path / "notes" / "accessories"
        if acc_dir.exists():
            notes.extend(sorted(acc_dir.rglob("*.md")))

    # Exclude translations
    notes = [n for n in notes if not n.name.endswith(".fr.md")]

    console.print(f"[bold]Extracting missing fields from {len(notes)} notes...[/bold]")

    # Process notes sequentially (structured output is sync, not async)
    changes: list[dict[str, Any]] = []
    for i, note_path in enumerate(notes, 1):
        if i % 20 == 0:
            console.print(f"  Processing {i}/{len(notes)}...")
        result = _extract_one(note_path, model)
        if result:
            changes.append(result)

    console.print(f"[bold]{len(changes)} notes have extractable fields.[/bold]")

    if not changes:
        console.print("[dim]Nothing to update.[/dim]")
        return

    if dry_run:
        for change in changes:
            console.print(
                f"\n[bold]{change['title']}[/bold] ({change['file_path'].name})"
            )
            for k, v in change["extracted"].items():
                console.print(f"  [green]+{k}:[/green] {v}")
        return

    if auto:
        accepted = changes
    else:
        review_items = [
            ReviewItem(
                data=change,
                label=change["title"],
                diff="\n".join(f"+{k}: {v}" for k, v in change["extracted"].items()),
            )
            for change in changes
        ]
        accepted, _ = run_review_session(
            review_items, console=console, entity_label="note"
        )

    # Apply changes
    for change in accepted:
        _apply_extracted_fields(change["file_path"], change["extracted"])
        console.print(
            f"[green]✓ {change['file_path'].name}[/green] +{len(change['extracted'])} fields"
        )

    console.print(f"\n[bold]Updated {len(accepted)} notes[/bold]")

    # Pass 2: wikilinks (if requested)
    if wikilinks:
        console.print("\n[bold]Converting wikilinks...[/bold]")
        wl_count = 0
        for note_path in notes:
            if _convert_wikilinks(note_path):
                wl_count += 1
        console.print(f"[bold]Converted wikilinks in {wl_count} notes[/bold]")
