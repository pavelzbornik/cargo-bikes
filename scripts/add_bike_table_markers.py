#!/usr/bin/env python3
"""
Temporary script to add <!-- BIKE_SPECS_TABLE_START --> and <!-- BIKE_SPECS_TABLE_END --> markers
to all bike markdown files in vault/notes/bikes/ that are missing them.

This script:
1. Finds all .md files in vault/notes/bikes/
2. Checks if they contain the required markers
3. Adds the markers after the frontmatter if missing
4. Reports progress and counts of files processed

Usage:
    python scripts/add_bike_table_markers.py [--vault-path path/to/vault/notes]
    python scripts/add_bike_table_markers.py --dry-run  # Preview changes without writing
"""

import argparse
import sys
from pathlib import Path


def find_frontmatter_end(content: str) -> int:
    """
    Find the end position of the YAML frontmatter block.

    Args:
        content: File content

    Returns:
        Index of the position right after the closing --- marker, or -1 if not found
    """
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return -1

    # Find the closing ---
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            # Return the position after this line (including newline)
            return len("\n".join(lines[: i + 1])) + 1

    return -1


def has_markers(content: str) -> bool:
    """
    Check if content has the required markers.

    Args:
        content: File content

    Returns:
        True if both markers are present
    """
    return (
        "<!-- BIKE_SPECS_TABLE_START -->" in content
        and "<!-- BIKE_SPECS_TABLE_END -->" in content
    )


def add_markers(content: str) -> str:
    """
    Add the bike specs table markers under "## Technical Specifications" section if missing.
    If the section doesn't exist, create it after frontmatter.

    Args:
        content: Original file content

    Returns:
        Updated content with markers added
    """
    if has_markers(content):
        return content

    fm_end = find_frontmatter_end(content)
    if fm_end == -1:
        print("Warning: Could not find frontmatter end")
        return content

    # Check if "## Technical Specifications" section already exists
    after_frontmatter = content[fm_end:]
    if "## Technical Specifications" in after_frontmatter:
        # Find the position of the first "## Technical Specifications"
        tech_specs_pos = after_frontmatter.find("## Technical Specifications")
        # Find the end of that line
        line_end = after_frontmatter.find("\n", tech_specs_pos) + 1

        # Insert markers right after the section header
        insert_pos = fm_end + line_end
        marker_block = (
            "\n<!-- BIKE_SPECS_TABLE_START -->\n<!-- BIKE_SPECS_TABLE_END -->\n"
        )
        return content[:insert_pos] + marker_block + content[insert_pos:]
    else:
        # Create new section after frontmatter
        marker_block = "\n## Technical Specifications\n\n<!-- BIKE_SPECS_TABLE_START -->\n<!-- BIKE_SPECS_TABLE_END -->\n"
        return content[:fm_end] + marker_block + content[fm_end:]


def process_bike_files(vault_path: Path, dry_run: bool = False) -> dict:
    """
    Process all bike markdown files.

    Args:
        vault_path: Path to vault/notes
        dry_run: If True, don't write changes

    Returns:
        Dictionary with processing statistics
    """
    stats = {
        "total_files": 0,
        "files_with_markers": 0,
        "files_processed": 0,
        "errors": 0,
    }

    bikes_path = vault_path / "bikes"

    if not bikes_path.exists():
        print(f"Error: Bikes path does not exist: {bikes_path}")
        return stats

    # Find all .md files in bikes directory, excluding index.md files
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

            # Add markers
            updated_content = add_markers(content)

            if not dry_run:
                md_file.write_text(updated_content, encoding="utf-8")

            # Get relative path for display
            rel_path = md_file.relative_to(vault_path)
            print(f"✓ {rel_path}")

            stats["files_processed"] += 1

        except Exception as e:
            print(f"✗ Error processing {md_file}: {e}")
            stats["errors"] += 1

    return stats


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Add bike specs table markers to markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--vault-path",
        type=str,
        default="vault/notes",
        help="Path to vault/notes directory (default: vault/notes)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing",
    )

    args = parser.parse_args()

    vault_path = Path(args.vault_path)

    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}", file=sys.stderr)
        return 1

    mode = (
        "DRY RUN - No changes will be written" if args.dry_run else "Processing files"
    )
    print(f"{mode}")
    print(f"Vault path: {vault_path}\n")

    stats = process_bike_files(vault_path, dry_run=args.dry_run)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Already have markers: {stats['files_with_markers']}")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Errors: {stats['errors']}")
    print("=" * 60)

    if args.dry_run:
        print(
            "\nDRY RUN: No changes were written. Run without --dry-run to apply changes."
        )

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
