"""Write updated bike notes to disk with proper formatting.

This module handles writing bike notes with properly formatted YAML
frontmatter and markdown content.
"""

from __future__ import annotations

from pathlib import Path

from .models import WriteResult
from .schema_validator import SchemaValidator
from .utils import format_yaml_frontmatter


class NoteWriter:
    """Writes updated bike notes to disk."""

    def __init__(self, validate: bool = True):
        """Initialize the note writer.

        Args:
            validate: Whether to validate before writing
        """
        self.validate = validate
        self.validator = SchemaValidator() if validate else None

    def write_note(
        self,
        file_path: str | Path,
        frontmatter: dict,
        body: str,
        validate: bool | None = None,
    ) -> WriteResult:
        """Write a bike note to disk.

        Args:
            file_path: Path to the note file
            frontmatter: Frontmatter dictionary
            body: Markdown body content
            validate: Override validation setting

        Returns:
            WriteResult with operation status
        """
        file_path = Path(file_path)
        errors: list[str] = []
        warnings: list[str] = []

        # Validate if requested
        should_validate = validate if validate is not None else self.validate
        if should_validate:
            # Create validator if we don't have one
            if self.validator is None:
                validator = SchemaValidator()
            else:
                validator = self.validator

            validation = validator.validate_frontmatter(frontmatter)
            if not validation.is_valid:
                errors.extend([issue.message for issue in validation.issues])
                return WriteResult(
                    success=False,
                    path=str(file_path),
                    errors=errors,
                    warnings=warnings,
                )
            warnings.extend(validation.warnings)

        # Format frontmatter
        try:
            yaml_str = self.format_frontmatter(frontmatter)
        except Exception as e:
            errors.append(f"Failed to format frontmatter: {str(e)}")
            return WriteResult(
                success=False,
                path=str(file_path),
                errors=errors,
                warnings=warnings,
            )

        # Combine frontmatter and body
        content = f"---\n{yaml_str}---\n\n{body}"

        # Write to file
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        except Exception as e:
            errors.append(f"Failed to write file: {str(e)}")
            return WriteResult(
                success=False,
                path=str(file_path),
                errors=errors,
                warnings=warnings,
            )

        return WriteResult(
            success=True,
            path=str(file_path),
            errors=[],
            warnings=warnings,
        )

    def format_frontmatter(self, frontmatter: dict) -> str:
        """Format frontmatter dictionary as YAML.

        Args:
            frontmatter: The frontmatter dictionary

        Returns:
            Formatted YAML string
        """
        return format_yaml_frontmatter(frontmatter)

    def read_note(self, file_path: str | Path) -> tuple[dict | None, str]:
        """Read a bike note from disk.

        Args:
            file_path: Path to the note file

        Returns:
            Tuple of (frontmatter, body)
        """
        from .utils import parse_frontmatter

        file_path = Path(file_path)
        if not file_path.exists():
            return None, ""

        content = file_path.read_text(encoding="utf-8")
        return parse_frontmatter(content)
