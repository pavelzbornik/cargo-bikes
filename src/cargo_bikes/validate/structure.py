"""Custom Markdown structural linter for cargo-bikes vault.

Validates that all Markdown files contain valid YAML frontmatter
and that bike notes include the required BIKE_SPECS_TABLE_START marker.
"""

from __future__ import annotations

from pathlib import Path

from cargo_bikes.vault.frontmatter import extract_frontmatter_with_error


class ValidationError:
    """Represents a validation error for a specific file."""

    def __init__(self, file_path: Path, error_message: str) -> None:
        self.file_path = file_path
        self.error_message = error_message

    def __str__(self) -> str:
        return f"{self.file_path}: {self.error_message}"


def validate_bike_note(content: str, frontmatter: dict[str, object]) -> str | None:
    """Validate that a bike note contains the required marker."""
    if frontmatter.get("type") != "bike":
        return None
    if "<!-- BIKE_SPECS_TABLE_START -->" not in content:
        return "Bike note missing required <!-- BIKE_SPECS_TABLE_START --> marker"
    return None


def validate_file(file_path: Path) -> ValidationError | None:
    """Validate a single markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return ValidationError(file_path, f"Failed to read file: {e}")

    frontmatter, error = extract_frontmatter_with_error(content)
    if error:
        return ValidationError(file_path, error)
    if frontmatter is None:
        return ValidationError(file_path, "Failed to parse frontmatter")

    bike_error = validate_bike_note(content, frontmatter)
    if bike_error:
        return ValidationError(file_path, bike_error)

    return None


def validate_vault(vault_path: Path) -> list[ValidationError]:
    """Validate all markdown files in the vault.

    Args:
        vault_path: Path to the vault/notes directory.

    Returns:
        List of validation errors (empty if all valid).
    """
    errors = []
    md_files = vault_path.rglob("*.md")
    for md_file in md_files:
        error = validate_file(md_file)
        if error:
            errors.append(error)
    return errors
