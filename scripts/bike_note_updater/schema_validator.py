"""Schema validation for bike notes against BIKE_SPECS_SCHEMA.

This module validates bike frontmatter against the standardized schema
defined in docs/schema/BIKE_SPECS_SCHEMA.md.
"""

from __future__ import annotations

from pathlib import Path

from .models import BikeFrontmatter, ValidationIssue, ValidationReport
from .utils import normalize_tag, validate_iso_date


class SchemaValidator:
    """Validates bike notes against the BIKE_SPECS_SCHEMA."""

    def __init__(self, schema_path: str | Path | None = None):
        """Initialize the schema validator.

        Args:
            schema_path: Optional path to BIKE_SPECS_SCHEMA.md
        """
        self.schema_path = schema_path
        # Schema rules are encoded in the BikeFrontmatter Pydantic model
        # Additional validation logic is implemented in methods below

    def validate_frontmatter(self, frontmatter: dict) -> ValidationReport:
        """Validate bike frontmatter against schema.

        Args:
            frontmatter: The frontmatter dictionary to validate

        Returns:
            ValidationReport with validation results
        """
        issues: list[ValidationIssue] = []
        warnings: list[str] = []

        # Check required fields
        required_fields = ["title", "type", "tags", "date"]
        for field in required_fields:
            if field not in frontmatter or not frontmatter[field]:
                issues.append(
                    ValidationIssue(
                        field=field,
                        issue_type="missing",
                        message=f"Required field '{field}' is missing or empty",
                        suggestion=f"Add '{field}' to frontmatter",
                    )
                )

        # Validate type field
        if frontmatter.get("type") != "bike":
            issues.append(
                ValidationIssue(
                    field="type",
                    issue_type="invalid_type",
                    message=f"Type must be 'bike', got '{frontmatter.get('type')}'",
                    suggestion="Set type: bike",
                )
            )

        # Validate date format
        date_str = frontmatter.get("date")
        if date_str and not validate_iso_date(str(date_str)):
            issues.append(
                ValidationIssue(
                    field="date",
                    issue_type="invalid_format",
                    message=f"Date '{date_str}' is not in ISO 8601 format (YYYY-MM-DD)",
                    suggestion="Use format: 2024-01-15",
                )
            )

        # Validate tags format
        tags = frontmatter.get("tags", [])
        if not isinstance(tags, list):
            issues.append(
                ValidationIssue(
                    field="tags",
                    issue_type="invalid_type",
                    message="Tags must be a list",
                    suggestion="Format: tags: [bike, longtail, brand-name]",
                )
            )
        else:
            # Check if required tags are present
            if "bike" not in tags:
                issues.append(
                    ValidationIssue(
                        field="tags",
                        issue_type="missing",
                        message="Tags must include 'bike'",
                        suggestion="Add 'bike' to tags list",
                    )
                )

            # Check tag formatting
            for tag in tags:
                normalized = normalize_tag(str(tag))
                if tag != normalized:
                    warnings.append(
                        f"Tag '{tag}' should be normalized to '{normalized}'"
                    )

        # Check for legacy fields that should be migrated to specs
        legacy_fields = ["motor", "battery", "range", "price"]
        has_legacy = any(
            field in frontmatter and frontmatter[field] for field in legacy_fields
        )
        has_specs = "specs" in frontmatter and frontmatter["specs"]

        if has_legacy and not has_specs:
            warnings.append(
                "Legacy fields detected. Consider migrating to 'specs' structure."
            )

        # Validate specs structure if present
        if has_specs:
            specs_issues = self._validate_specs_structure(frontmatter["specs"])
            issues.extend(specs_issues)

        # Try to parse with Pydantic model for comprehensive validation
        try:
            BikeFrontmatter(**frontmatter)
        except Exception as e:
            issues.append(
                ValidationIssue(
                    field="frontmatter",
                    issue_type="invalid_type",
                    message=f"Pydantic validation failed: {str(e)}",
                    suggestion="Check field types and structure",
                )
            )

        is_valid = len(issues) == 0
        return ValidationReport(is_valid=is_valid, issues=issues, warnings=warnings)

    def _validate_specs_structure(self, specs: dict) -> list[ValidationIssue]:
        """Validate the nested specs structure.

        Args:
            specs: The specs dictionary

        Returns:
            List of validation issues
        """
        issues: list[ValidationIssue] = []

        # Check for recommended fields
        recommended_fields = ["category", "motor", "battery", "weight"]
        for field in recommended_fields:
            if field not in specs or not specs[field]:
                issues.append(
                    ValidationIssue(
                        field=f"specs.{field}",
                        issue_type="missing",
                        message=f"Recommended field 'specs.{field}' is missing",
                        suggestion=f"Add {field} information to specs",
                    )
                )

        # Validate motor structure if present
        motor = specs.get("motor")
        if motor and isinstance(motor, dict):
            if not motor.get("make") and not motor.get("model"):
                issues.append(
                    ValidationIssue(
                        field="specs.motor",
                        issue_type="invalid_type",
                        message="Motor should have at least 'make' or 'model'",
                        suggestion="Add motor make and/or model",
                    )
                )

        # Validate battery structure if present
        battery = specs.get("battery")
        if battery and isinstance(battery, dict):
            if not battery.get("capacity_wh"):
                issues.append(
                    ValidationIssue(
                        field="specs.battery",
                        issue_type="missing",
                        message="Battery should have 'capacity_wh'",
                        suggestion="Add battery capacity in watt-hours",
                    )
                )

        # Validate weight structure if present
        weight = specs.get("weight")
        if weight and isinstance(weight, dict):
            if not weight.get("with_battery_kg") and not weight.get("bike_kg"):
                issues.append(
                    ValidationIssue(
                        field="specs.weight",
                        issue_type="missing",
                        message="Weight should have at least 'with_battery_kg' or 'bike_kg'",
                        suggestion="Add bike weight in kilograms",
                    )
                )

        return issues

    def check_tag_format(self, tags: list[str]) -> bool:
        """Check if all tags follow the required format.

        Args:
            tags: List of tags to check

        Returns:
            True if all tags are properly formatted, False otherwise
        """
        for tag in tags:
            if tag != normalize_tag(str(tag)):
                return False
        return True

    def check_date_format(self, date_str: str) -> bool:
        """Check if date follows ISO 8601 format.

        Args:
            date_str: Date string to check

        Returns:
            True if valid ISO 8601 date, False otherwise
        """
        return validate_iso_date(date_str)
