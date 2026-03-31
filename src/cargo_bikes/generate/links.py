"""Convert wikilinks to markdown links using a title-to-filepath map.

Obsidian-bridge resolves wikilinks by filename, not by frontmatter title.
This module builds a title map and converts [[Title]] to [Title](/path.md)
so links work on both Obsidian and MkDocs.
"""

from __future__ import annotations

import re
from pathlib import Path

from cargo_bikes.vault.frontmatter import extract_frontmatter


def build_title_map(notes_dir: Path) -> dict[str, str]:
    """Build a map of note title -> relative path from docs root.

    Also maps filename stems as fallback (e.g., "ejoy-e" -> path).
    """
    title_map: dict[str, str] = {}

    for md_file in sorted(notes_dir.rglob("*.md")):
        if md_file.name.endswith(".fr.md"):
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        fm = extract_frontmatter(content)
        if not fm:
            continue

        rel_path = str(md_file.relative_to(notes_dir)).replace("\\", "/")

        # Map by title
        title = fm.get("title", "")
        if title:
            title_map[title] = rel_path

        # Map by filename stem as fallback
        stem = md_file.stem
        if stem and stem != "index":
            title_map[stem] = rel_path

    return title_map


def convert_wikilinks_in_file(
    file_path: Path,
    notes_dir: Path,
    title_map: dict[str, str],
    dry_run: bool = False,
) -> int:
    """Convert [[wikilinks]] to [text](/path.md) in a single file.

    Returns the number of links converted.
    """
    content = file_path.read_text(encoding="utf-8")

    # Split into frontmatter and body — only convert in body
    fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    if fm_match:
        header = content[: fm_match.end()]
        body = content[fm_match.end() :]
    else:
        header = ""
        body = content

    converted = 0

    def replace_wikilink(m: re.Match) -> str:
        nonlocal converted
        inner = m.group(1)

        # Parse [[Target|Display]] or [[Target]]
        if "|" in inner:
            target, display = inner.split("|", 1)
        else:
            target = inner
            display = inner

        target = target.strip()
        display = display.strip()

        # Look up in title map
        if target in title_map:
            path = "/" + title_map[target]
            converted += 1
            return f"[{display}]({path})"

        # Try case-insensitive match
        target_lower = target.lower()
        for title, path in title_map.items():
            if title.lower() == target_lower:
                converted += 1
                return f"[{display}](/{path})"

        # Not found — leave as-is
        return m.group(0)

    new_body = re.sub(r"\[\[([^\]]+)\]\]", replace_wikilink, body)

    if converted > 0 and not dry_run:
        file_path.write_text(header + new_body, encoding="utf-8")

    return converted


def fix_all_links(
    vault_path: Path = Path("vault"),
    dry_run: bool = False,
) -> None:
    """Convert all wikilinks to markdown links across the vault."""
    notes_dir = vault_path / "notes"

    print("Building title map...")
    title_map = build_title_map(notes_dir)
    print(f"  {len(title_map)} entries")

    print("Scanning for wikilinks...")
    total_files = 0
    total_links = 0
    unresolved = 0

    for md_file in sorted(notes_dir.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")

        # Count wikilinks in body only
        fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        body = content[fm_match.end() :] if fm_match else content
        wikilinks = re.findall(r"\[\[([^\]]+)\]\]", body)

        if not wikilinks:
            continue

        converted = convert_wikilinks_in_file(
            md_file, notes_dir, title_map, dry_run=dry_run
        )
        remaining = len(wikilinks) - converted
        unresolved += remaining
        total_links += converted
        total_files += 1

        rel = str(md_file.relative_to(notes_dir)).replace("\\", "/")
        if dry_run:
            print(f"  {rel}: {converted}/{len(wikilinks)} links")
        elif converted > 0:
            status = f" ({remaining} unresolved)" if remaining else ""
            print(f"  {rel}: {converted} converted{status}")

    print(f"\nConverted {total_links} links in {total_files} files")
    if unresolved:
        print(f"  {unresolved} unresolved (no matching title in vault)")
