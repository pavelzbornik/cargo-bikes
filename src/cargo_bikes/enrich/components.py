"""Auto-generate component notes from bike spec data."""

from __future__ import annotations

import asyncio
import re
from collections import defaultdict
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cargo_bikes.db.schema import Bike
from cargo_bikes.enrich.agent import call_agent, call_api, run_concurrent
from cargo_bikes.enrich.prompts import COMPONENT_NOTE_SYSTEM
from cargo_bikes.enrich.review import ReviewItem, run_review_session


def _slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


CATEGORY_EXTRACTORS = {
    "motors": lambda b: (b.motor_make, b.motor_model),
    "drivetrains": lambda b: (
        b.drivetrain_hub.split()[0] if b.drivetrain_hub and " " in b.drivetrain_hub else b.drivetrain_hub,
        b.drivetrain_hub,
    ) if b.drivetrain_hub else (None, None),
    "brakes": lambda b: (
        b.brakes_type.split()[0] if b.brakes_type and " " in b.brakes_type else b.brakes_type,
        b.brakes_type,
    ) if b.brakes_type else (None, None),
    "tires": lambda b: (
        b.wheels_tire.split()[0] if b.wheels_tire and " " in b.wheels_tire else b.wheels_tire,
        b.wheels_tire,
    ) if b.wheels_tire else (None, None),
    "batteries": lambda b: (b.motor_make, f"{b.battery_capacity_wh}Wh") if b.battery_capacity_wh else (None, None),
    "suspension": lambda b: (
        b.suspension_front.split()[0] if b.suspension_front and " " in b.suspension_front else b.suspension_front,
        b.suspension_front,
    ) if b.suspension_front and b.suspension_front.lower() != "none" else (None, None),
    "lights": lambda b: (
        b.lights_front_type.split()[0] if b.lights_front_type and " " in b.lights_front_type else b.lights_front_type,
        b.lights_front_type,
    ) if b.lights_front_type else (None, None),
    "security": lambda b: ("GPS" if b.security_gps else None, "GPS Tracking" if b.security_gps else None),
}


def _gather_components(
    bikes: list[Bike], category: str
) -> dict[str, dict[str, list[str]]]:
    """Gather component data grouped by manufacturer → models.

    Returns:
        Dict of {manufacturer: {model: [bike_titles]}}.
    """
    extractor = CATEGORY_EXTRACTORS.get(category)
    if not extractor:
        return {}

    result: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for bike in bikes:
        make, model = extractor(bike)
        if make:
            result[make][model or "unknown"].append(bike.title)

    return dict(result)


async def _generate_component_note(
    manufacturer: str,
    model_name: str | None,
    category: str,
    bikes_using: list[str],
    model: str,
) -> dict[str, str]:
    """Generate a single component note using Claude."""
    is_manufacturer = model_name is None
    title = manufacturer if is_manufacturer else f"{manufacturer} {model_name}"
    note_type = "component-manufacturer" if is_manufacturer else "component"

    bikes_list = "\n".join(f"- [[{b}]]" for b in bikes_using[:10])

    prompt = f"""Create a {'manufacturer' if is_manufacturer else 'component model'} note:

Title: {title}
Category: {category}
Type: {note_type}
{'Parent: [[' + manufacturer + ']]' if not is_manufacturer else ''}
Domain: [[{category.title()} MOC]]

Bikes using this {'manufacturer' if is_manufacturer else 'component'}:
{bikes_list}
{'(and more...)' if len(bikes_using) > 10 else ''}

Generate a complete Obsidian markdown note.
"""

    # Manufacturer notes: web search for company details (more turns)
    # Model notes: no web search, but still need multiple turns for thinking
    if is_manufacturer:
        result = await call_agent(
            prompt=prompt,
            system=COMPONENT_NOTE_SYSTEM,
            model=model,
            max_turns=5,
            allowed_tools=["WebSearch", "WebFetch"],
        )
    else:
        result = await call_agent(
            prompt=prompt,
            system=COMPONENT_NOTE_SYSTEM,
            model=model,
            max_turns=6,
        )

    return {
        "title": title,
        "slug": _slugify(title),
        "category": category,
        "content": result.strip(),
        "is_manufacturer": is_manufacturer,
    }


def generate_components(
    category: str = "all",
    vault_path: Path = Path("vault"),
    db_path: Path = Path("vault.db"),
    dry_run: bool = False,
    auto: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    """Auto-generate component notes from bike spec data.

    Args:
        category: Component category or "all".
        vault_path: Path to vault root.
        db_path: Path to database.
        dry_run: If True, show what would be generated.
        model: Claude model to use.
    """
    from rich.console import Console

    console = Console()

    engine = create_engine(f"sqlite:///{db_path.resolve()}", echo=False)

    with Session(engine) as session:
        bikes = list(session.execute(select(Bike)).scalars().all())

    categories = list(CATEGORY_EXTRACTORS.keys()) if category == "all" else [category]

    all_notes: list[dict[str, str]] = []

    for cat in categories:
        console.print(f"\n[bold]Processing {cat}...[/bold]")
        components = _gather_components(bikes, cat)

        if not components:
            console.print(f"  [dim]No {cat} data found[/dim]")
            continue

        console.print(f"  Found {len(components)} manufacturers")

        if dry_run:
            for mfr, models in components.items():
                console.print(f"  [dim]Would create: {mfr} (manufacturer)[/dim]")
                for m in models:
                    if m != "unknown":
                        console.print(f"    [dim]Would create: {mfr} {m}[/dim]")
            continue

        # Generate notes — skip already-existing ones with content
        def _note_exists(slug: str) -> bool:
            path = vault_path / "notes" / "components" / cat / f"{slug}.md"
            return path.exists() and path.stat().st_size > 10

        async def _generate_all() -> list[dict[str, str]]:
            tasks = []
            for mfr, models in components.items():
                # Manufacturer note
                slug = _slugify(mfr)
                if not _note_exists(slug):
                    all_bikes = [b for model_bikes in models.values() for b in model_bikes]
                    tasks.append((mfr, None, cat, all_bikes))

                # Model notes
                for m, bike_titles in models.items():
                    if m != "unknown":
                        model_slug = _slugify(f"{mfr} {m}")
                        if not _note_exists(model_slug):
                            tasks.append((mfr, m, cat, bike_titles))

            if not tasks:
                console.print("  [dim]All notes already exist[/dim]")
                return []

            console.print(f"  Generating {len(tasks)} notes (skipping existing)...")

            async def gen(args: tuple) -> dict[str, str]:
                mfr, m, c, bt = args
                return await _generate_component_note(mfr, m, c, bt, model)

            return await run_concurrent(
                items=tasks,
                worker_fn=gen,
                concurrency=3,
                on_progress=lambda: console.print(".", end=""),
            )

        notes = asyncio.run(_generate_all())
        all_notes.extend(notes)

    if dry_run or not all_notes:
        return

    # Review
    if auto:
        accepted = all_notes
        discarded: list[dict[str, str]] = []
    else:
        review_items = [
            ReviewItem(
                data=note,
                label=f"{note['category']}/{note['title']}",
                diff=note["content"][:300] + "...",
            )
            for note in all_notes
        ]
        accepted, discarded = run_review_session(
            review_items, console=console, entity_label="component"
        )

    # Write accepted notes
    for note in accepted:
        cat_dir = vault_path / "notes" / "components" / note["category"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        output_path = cat_dir / f"{note['slug']}.md"
        output_path.write_text(note["content"] + "\n", encoding="utf-8")
        console.print(f"[green]✓ {output_path}[/green]")

    console.print(
        f"\n[bold]Generated {len(accepted)} component notes, "
        f"discarded {len(discarded)}[/bold]"
    )
