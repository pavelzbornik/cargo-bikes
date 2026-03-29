"""Add BIKE_SPECS_TABLE markers to bike markdown files."""

from __future__ import annotations

from pathlib import Path

from cargo_bikes.vault.frontmatter import find_frontmatter_end

BIKE_SPECS_TABLE_START_MARKER = "<!-- BIKE_SPECS_TABLE_START -->"
BIKE_SPECS_TABLE_END_MARKER = "<!-- BIKE_SPECS_TABLE_END -->"
TECH_SPECS_SECTION_HEADER = "## Technical Specifications"


def has_markers(content: str) -> bool:
    """Check if content has the required markers."""
    return (
        BIKE_SPECS_TABLE_START_MARKER in content
        and BIKE_SPECS_TABLE_END_MARKER in content
    )


def add_markers(content: str) -> str:
    """Add the bike specs table markers if missing.

    Inserts under "## Technical Specifications" section if it exists,
    otherwise creates the section after frontmatter.
    """
    if has_markers(content):
        return content

    fm_end = find_frontmatter_end(content)
    if fm_end == -1:
        print("Warning: Could not find frontmatter end")
        return content

    after_frontmatter = content[fm_end:]
    if TECH_SPECS_SECTION_HEADER in after_frontmatter:
        tech_specs_pos = after_frontmatter.find(TECH_SPECS_SECTION_HEADER)
        line_end = after_frontmatter.find("\n", tech_specs_pos) + 1
        insert_pos = fm_end + line_end
        marker_block = (
            f"\n{BIKE_SPECS_TABLE_START_MARKER}\n{BIKE_SPECS_TABLE_END_MARKER}\n"
        )
        return content[:insert_pos] + marker_block + content[insert_pos:]
    else:
        marker_block = f"\n{TECH_SPECS_SECTION_HEADER}\n\n{BIKE_SPECS_TABLE_START_MARKER}\n{BIKE_SPECS_TABLE_END_MARKER}\n"
        return content[:fm_end] + marker_block + content[fm_end:]


def process_bike_files(vault_path: Path, dry_run: bool = False) -> dict[str, int]:
    """Process all bike markdown files, adding markers where missing.

    Args:
        vault_path: Path to vault/notes directory.
        dry_run: If True, don't write changes.

    Returns:
        Dictionary with processing statistics.
    """
    stats: dict[str, int] = {
        "total_files": 0,
        "files_with_markers": 0,
        "files_processed": 0,
        "errors": 0,
    }

    bikes_path = vault_path / "bikes"

    if not bikes_path.exists():
        print(f"Error: Bikes path does not exist: {bikes_path}")
        return stats

    all_md_files = sorted(bikes_path.rglob("*.md"))
    md_files = [f for f in all_md_files if f.name != "index.md"]
    stats["total_files"] = len(md_files)

    print(f"Found {len(md_files)} bike markdown files (excluding index.md)\n")

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")

            if has_markers(content):
                stats["files_with_markers"] += 1
                continue

            updated_content = add_markers(content)

            if not dry_run:
                md_file.write_text(updated_content, encoding="utf-8")

            rel_path = md_file.relative_to(vault_path)
            print(f"✓ {rel_path}")

            stats["files_processed"] += 1

        except Exception as e:
            print(f"✗ Error processing {md_file}: {e}")
            stats["errors"] += 1

    return stats
