"""Schema harmonization + wikilink conversion for vault notes."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from cargo_bikes.enrich.agent import call_agent
from cargo_bikes.enrich.prompts import HARMONIZE_SYSTEM
from cargo_bikes.enrich.review import ReviewItem, run_review_session
from cargo_bikes.vault.frontmatter import extract_frontmatter


async def _harmonize_one(
    file_path: Path,
    template_content: str,
    model: str,
) -> dict[str, Any] | None:
    """Harmonize a single note using Claude.

    Returns dict with file_path, original, and harmonized content, or None if no changes.
    """
    content = file_path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        return None

    prompt = f"""Here is a cargo bike vault note to harmonize:

--- NOTE FILE: {file_path.name} ---
{content}
--- END NOTE ---

--- TEMPLATE SCHEMA ---
{template_content}
--- END TEMPLATE ---

Harmonize this note: fill missing frontmatter fields, convert internal markdown
links to wikilinks, and add component wikilinks. Return the COMPLETE updated note.
"""

    result = await call_agent(
        prompt=prompt,
        system=HARMONIZE_SYSTEM,
        model=model,
        max_turns=1,
    )

    if not result or result.strip() == content.strip():
        return None

    return {
        "file_path": file_path,
        "original": content,
        "harmonized": result.strip(),
        "title": frontmatter.get("title", file_path.stem),
    }


def harmonize_notes(
    vault_path: Path,
    brand: str | None = None,
    dry_run: bool = False,
    auto: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    """Harmonize vault notes: fill schema gaps and convert to wikilinks.

    Args:
        vault_path: Path to vault root (e.g., Path("vault")).
        brand: If set, only harmonize notes for this brand.
        dry_run: If True, show changes without writing.
        auto: If True, skip interactive review.
        model: Claude model to use.
    """
    from rich.console import Console

    console = Console()

    # Load templates
    bike_template_path = vault_path / "templates" / "bike-template.md"
    brand_template_path = vault_path / "templates" / "brand-template.md"

    bike_template = bike_template_path.read_text(encoding="utf-8") if bike_template_path.exists() else ""
    brand_template = brand_template_path.read_text(encoding="utf-8") if brand_template_path.exists() else ""

    # Collect notes to process
    bikes_dir = vault_path / "notes" / "bikes"
    notes: list[Path] = []

    if brand:
        brand_dir = bikes_dir / brand
        if brand_dir.exists():
            notes.extend(sorted(brand_dir.glob("*.md")))
            # Also include brand-specific accessories
            acc_dir = brand_dir / "accessories"
            if acc_dir.exists():
                notes.extend(sorted(acc_dir.glob("*.md")))
    else:
        for brand_dir in sorted(bikes_dir.iterdir()):
            if brand_dir.is_dir():
                notes.extend(sorted(brand_dir.glob("*.md")))
                # Also include brand-specific accessories
                acc_dir = brand_dir / "accessories"
                if acc_dir.exists():
                    notes.extend(sorted(acc_dir.glob("*.md")))

        # Universal accessories
        acc_dir = vault_path / "notes" / "accessories"
        if acc_dir.exists():
            notes.extend(sorted(acc_dir.rglob("*.md")))

    # Exclude .fr.md translations
    notes = [n for n in notes if not n.name.endswith(".fr.md")]

    console.print(f"[bold]Harmonizing {len(notes)} notes...[/bold]")

    # Process notes concurrently
    async def _process_all() -> list[dict[str, Any]]:
        from cargo_bikes.enrich.agent import run_concurrent

        async def process_note(note_path: Path) -> dict[str, Any] | None:
            fm = extract_frontmatter(note_path.read_text(encoding="utf-8"))
            if not fm:
                return None
            note_type = fm.get("type", "")
            if note_type in ("brand", "brand-index"):
                template = brand_template
            elif note_type == "accessory":
                template = "Accessory note. Ensure flat frontmatter: title, type, category, manufacturer, price_amount, price_currency, compatible_bikes, tags."
            else:
                template = bike_template
            return await _harmonize_one(note_path, template, model)

        results = await run_concurrent(
            items=notes,
            worker_fn=process_note,
            concurrency=3,
            on_progress=lambda: console.print(".", end=""),
        )
        return [r for r in results if r is not None]

    changes = asyncio.run(_process_all())
    console.print(f"\n[bold]{len(changes)} notes have changes.[/bold]")

    if not changes:
        return

    if dry_run:
        for change in changes:
            console.print(f"\n[bold]{change['title']}[/bold] ({change['file_path']})")
            console.print("[dim]Changes would be applied (dry-run mode)[/dim]")
        return

    if auto:
        accepted = [c for c in changes]
        discarded: list[dict[str, Any]] = []
    else:
        review_items = [
            ReviewItem(
                data=change,
                label=change["title"],
                diff=change["harmonized"][:500] + "..." if len(change["harmonized"]) > 500 else change["harmonized"],
            )
            for change in changes
        ]
        accepted, discarded = run_review_session(
            review_items, console=console, entity_label="note"
        )

    # Write accepted changes
    for change in accepted:
        file_path: Path = change["file_path"]
        file_path.write_text(change["harmonized"] + "\n", encoding="utf-8")
        console.print(f"[green]✓ Updated {file_path}[/green]")

    console.print(
        f"\n[bold]Done:[/bold] {len(accepted)} updated, {len(discarded)} discarded"
    )
