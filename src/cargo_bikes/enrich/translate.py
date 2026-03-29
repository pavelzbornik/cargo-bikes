"""Claude-powered translation for multilingual vault content."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from cargo_bikes.enrich.agent import call_agent, run_concurrent
from cargo_bikes.enrich.prompts import TRANSLATE_SYSTEM


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


async def _translate_one(
    file_path: Path,
    lang: str,
    model: str,
) -> dict[str, str] | None:
    """Translate a single note's body content.

    Returns dict with output_path and translated content, or None if already exists.
    """
    output_path = file_path.with_suffix(f".{lang}.md")
    if output_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    body = _strip_frontmatter(content)

    if not body.strip():
        return None

    prompt = f"""Translate this cargo bike content to French:

{body}
"""

    result = await call_agent(
        prompt=prompt,
        system=TRANSLATE_SYSTEM,
        model=model,
        max_turns=1,
    )

    if not result.strip():
        return None

    return {
        "output_path": str(output_path),
        "content": result.strip(),
        "source": str(file_path),
    }


def translate_notes(
    lang: str = "fr",
    vault_path: Path = Path("vault"),
    brand: str | None = None,
    note_type: str | None = None,
    dry_run: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    """Translate vault notes to the specified language.

    Args:
        lang: Target language code (e.g., "fr").
        vault_path: Path to vault root.
        brand: If set, only translate notes for this brand.
        note_type: Filter by note type (bike, brand, guide, component).
        dry_run: If True, show what would be translated.
        model: Claude model to use.
    """
    from rich.console import Console

    console = Console()

    # Collect notes to translate
    notes: list[Path] = []

    if brand:
        brand_dir = vault_path / "notes" / "bikes" / brand
        if brand_dir.exists():
            notes.extend(
                f for f in sorted(brand_dir.glob("*.md"))
                if not f.stem.endswith(f".{lang}")
            )
    elif note_type == "guide":
        guides_dir = vault_path / "notes" / "guides"
        if guides_dir.exists():
            notes.extend(
                f for f in sorted(guides_dir.glob("*.md"))
                if not f.stem.endswith(f".{lang}")
            )
    elif note_type == "component":
        components_dir = vault_path / "notes" / "components"
        if components_dir.exists():
            notes.extend(
                f for f in sorted(components_dir.rglob("*.md"))
                if not f.stem.endswith(f".{lang}")
            )
    else:
        notes_dir = vault_path / "notes"
        if notes_dir.exists():
            notes.extend(
                f for f in sorted(notes_dir.rglob("*.md"))
                if not f.stem.endswith(f".{lang}")
            )

    # Filter out notes that already have translations
    to_translate = [
        n for n in notes
        if not n.with_suffix(f".{lang}.md").exists()
    ]

    console.print(
        f"[bold]Found {len(to_translate)} notes to translate to {lang}[/bold] "
        f"(skipping {len(notes) - len(to_translate)} already translated)"
    )

    if not to_translate:
        return

    if dry_run:
        for note in to_translate:
            console.print(f"  [dim]Would translate: {note}[/dim]")
        return

    # Translate concurrently
    async def _translate_all() -> list[dict[str, str]]:
        async def do_translate(path: Path) -> dict[str, str] | None:
            return await _translate_one(path, lang, model)

        results = await run_concurrent(
            items=to_translate,
            worker_fn=do_translate,
            concurrency=3,
            on_progress=lambda: console.print(".", end=""),
        )
        return [r for r in results if r is not None]

    translations = asyncio.run(_translate_all())

    # Write translated files
    for t in translations:
        output_path = Path(t["output_path"])
        header = f"<!-- generated_by: cargo-bikes-cli | source: {t['source']} -->\n\n"
        output_path.write_text(header + t["content"] + "\n", encoding="utf-8")
        console.print(f"[green]✓ {output_path}[/green]")

    console.print(f"\n[bold]Translated {len(translations)} notes to {lang}[/bold]")
