"""
Custom Markdown structural linter for cargo-bikes vault.

This script validates that all Markdown files in vault/notes/ contain valid
YAML frontmatter and that bike notes include the required BIKE_SPECS_TABLE_START
comment marker.

Usage:
    python scripts/linters/validate_structure.py

Exit Codes:
    0: All files valid
    1: One or more files invalid
"""

import argparse
import sys
from pathlib import Path

import yaml


class ValidationError:
    """Represents a validation error for a specific file."""

    def __init__(self, file_path: Path, error_message: str):
        self.file_path = file_path
        self.error_message = error_message

    def __str__(self):
        return f"{self.file_path}: {self.error_message}"


def extract_frontmatter(content: str) -> tuple[dict | None, str]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown file content

    Returns:
        Tuple of (frontmatter_dict, error_message)
        If successful, returns (dict, None)
        If failed, returns (None, error_message)
    """
    lines = content.split("\n")

    # Check if file starts with ---
    if not lines or lines[0].strip() != "---":
        return None, "Missing frontmatter start delimiter (---)"

    # Find the closing ---
    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        return None, "Missing frontmatter end delimiter (---)"

    # Extract and parse YAML
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = "\n".join(frontmatter_lines)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            frontmatter = {}
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML syntax: {e}"


def validate_bike_note(content: str, frontmatter: dict) -> str | None:
    """
    Validate that a bike note contains the required BIKE_SPECS_TABLE_START marker.

    Args:
        content: Full markdown content
        frontmatter: Parsed frontmatter dictionary

    Returns:
        Error message if invalid, None if valid
    """
    # Check if this is a bike note
    if frontmatter.get("type") != "bike":
        return None

    # Check for BIKE_SPECS_TABLE_START marker
    if "<!-- BIKE_SPECS_TABLE_START -->" not in content:
        return "Bike note missing required <!-- BIKE_SPECS_TABLE_START --> marker"

    return None


def validate_file(file_path: Path) -> ValidationError | None:
    """
    Validate a single markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        ValidationError if invalid, None if valid
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return ValidationError(file_path, f"Failed to read file: {e}")

    # Validate frontmatter
    frontmatter, error = extract_frontmatter(content)
    if error:
        return ValidationError(file_path, error)

    # Validate bike-specific requirements
    bike_error = validate_bike_note(content, frontmatter)
    if bike_error:
        return ValidationError(file_path, bike_error)

    return None


def validate_vault(vault_path: Path) -> list[ValidationError]:
    """
    Validate all markdown files in the vault.

    Args:
        vault_path: Path to the vault/notes directory

    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []

    # Find all .md files recursively
    md_files = vault_path.rglob("*.md")

    for md_file in md_files:
        error = validate_file(md_file)
        if error:
            errors.append(error)

    return errors


def main():
    """Command-line interface for the linter."""
    parser = argparse.ArgumentParser(
        description="Validate Markdown structure in cargo-bikes vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--vault-path",
        type=str,
        default="vault/notes",
        help="Path to the vault notes directory (default: vault/notes)",
    )

    args = parser.parse_args()

    # Convert to Path and ensure it exists
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"✗ Vault path does not exist: {vault_path}", file=sys.stderr)
        return 1

    # Validate all files
    print(f"Validating markdown files in {vault_path}...")
    errors = validate_vault(vault_path)

    if errors:
        print(f"\n✗ Found {len(errors)} validation error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    else:
        print("✓ All markdown files are valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
