"""
Schema validator for bike note frontmatter.

Validates bike notes against the BIKE_SPECS_SCHEMA, identifying missing fields,
incorrect types, deprecated legacy fields, and providing completeness scores.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from scripts.bike_note_updater.models import (
    ValidationIssue,
    ValidationReport,
)

# Fields required for a valid bike note
REQUIRED_FIELDS = ["title", "type"]

# Fields strongly recommended for completeness
RECOMMENDED_TOP_LEVEL = ["brand", "model", "tags", "url", "date"]

# Legacy fields that should be migrated into specs
LEGACY_FIELDS = {"price", "motor", "battery", "range"}

# All trackable spec fields for completeness scoring
SPEC_FIELDS = [
    "category",
    "model_year",
    "frame.material",
    "weight.with_battery_kg",
    "load_capacity.total_kg",
    "motor.make",
    "motor.model",
    "motor.type",
    "motor.power_w",
    "motor.torque_nm",
    "battery.capacity_wh",
    "battery.configuration",
    "battery.removable",
    "drivetrain.type",
    "drivetrain.speeds",
    "brakes.type",
    "wheels.front_size_in",
    "wheels.rear_size_in",
    "price.amount",
    "price.currency",
]


def extract_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """
    Extract YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary of frontmatter data, or None if extraction fails
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        if not lines or lines[0].strip() != "---":
            return None

        try:
            end_idx = lines[1:].index("---") + 1
        except ValueError:
            return None

        frontmatter_text = "\n".join(lines[1:end_idx])
        return yaml.safe_load(frontmatter_text) or {}

    except Exception:
        return None


def _get_nested(data: dict[str, Any], dotted_path: str) -> Any:
    """Get a value from nested dict using dot notation."""
    parts = dotted_path.split(".")
    current = data
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
        if current is None:
            return None
    return current


def _check_tag_format(tags: list[Any]) -> list[ValidationIssue]:
    """Validate that tags follow the lowercase-hyphenated convention."""
    issues = []
    tag_pattern = re.compile(r"^[a-z0-9][a-z0-9-]*$")
    for tag in tags:
        tag_str = str(tag)
        if not tag_pattern.match(tag_str):
            issues.append(
                ValidationIssue(
                    field="tags",
                    issue_type="invalid_format",
                    message=f"Tag '{tag_str}' should be lowercase and hyphenated",
                    suggestion=tag_str.lower().replace(" ", "-").replace("_", "-"),
                )
            )
    return issues


def _check_date_format(date_val: Any) -> list[ValidationIssue]:
    """Validate date is ISO 8601 (YYYY-MM-DD)."""
    issues = []
    date_str = str(date_val)
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not date_pattern.match(date_str):
        issues.append(
            ValidationIssue(
                field="date",
                issue_type="invalid_format",
                message=f"Date '{date_str}' is not ISO 8601 format (YYYY-MM-DD)",
                suggestion="Use format like 2024-10-16",
            )
        )
    return issues


def _check_url_format(url: str, field_name: str) -> list[ValidationIssue]:
    """Basic URL format validation."""
    issues = []
    if url and not url.startswith(("http://", "https://")):
        issues.append(
            ValidationIssue(
                field=field_name,
                issue_type="invalid_format",
                message=f"URL should start with http:// or https://: {url}",
            )
        )
    return issues


def validate_frontmatter(
    frontmatter: dict[str, Any], file_path: str = "<unknown>"
) -> ValidationReport:
    """
    Validate bike frontmatter against the BIKE_SPECS_SCHEMA.

    Args:
        frontmatter: Parsed YAML frontmatter dictionary
        file_path: Path to the source file (for reporting)

    Returns:
        ValidationReport with all findings
    """
    issues: list[ValidationIssue] = []
    missing_required: list[str] = []
    missing_recommended: list[str] = []

    # Check type is 'bike'
    note_type = frontmatter.get("type")
    if note_type != "bike":
        issues.append(
            ValidationIssue(
                field="type",
                issue_type="invalid_type",
                message=f"Expected type 'bike', got '{note_type}'",
            )
        )

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in frontmatter or frontmatter[field] is None:
            missing_required.append(field)
            issues.append(
                ValidationIssue(
                    field=field,
                    issue_type="missing",
                    message=f"Required field '{field}' is missing",
                )
            )

    # Check recommended top-level fields
    for field in RECOMMENDED_TOP_LEVEL:
        if field not in frontmatter or frontmatter[field] is None:
            missing_recommended.append(field)

    # Check for legacy fields
    has_legacy = False
    for legacy_field in LEGACY_FIELDS:
        if legacy_field in frontmatter and frontmatter[legacy_field] is not None:
            has_legacy = True
            issues.append(
                ValidationIssue(
                    field=legacy_field,
                    issue_type="deprecated",
                    message=(
                        f"Legacy top-level field '{legacy_field}' should be "
                        f"migrated into 'specs.{legacy_field}'"
                    ),
                    suggestion=f"Move to specs.{legacy_field}",
                )
            )

    # Validate tags format
    tags = frontmatter.get("tags")
    if isinstance(tags, list):
        issues.extend(_check_tag_format(tags))

    # Validate date format
    date_val = frontmatter.get("date")
    if date_val is not None:
        issues.extend(_check_date_format(date_val))

    # Validate URLs
    url = frontmatter.get("url")
    if url:
        issues.extend(_check_url_format(str(url), "url"))

    # Validate resellers
    resellers = frontmatter.get("resellers", [])
    if isinstance(resellers, list):
        for i, reseller in enumerate(resellers):
            if isinstance(reseller, dict):
                r_url = reseller.get("url")
                if r_url:
                    issues.extend(
                        _check_url_format(str(r_url), f"resellers[{i}].url")
                    )

    # Calculate specs completeness
    specs = frontmatter.get("specs", {})
    if not isinstance(specs, dict):
        specs = {}

    populated_count = 0
    for spec_field in SPEC_FIELDS:
        value = _get_nested(specs, spec_field)
        if value is not None:
            populated_count += 1

    completeness = populated_count / len(SPEC_FIELDS) if SPEC_FIELDS else 0.0

    # Check if specs section exists at all
    if not specs:
        issues.append(
            ValidationIssue(
                field="specs",
                issue_type="missing",
                message="No 'specs' section found; structured data is missing",
                suggestion="Add a specs section with category, motor, battery, etc.",
            )
        )

    is_valid = len(missing_required) == 0

    return ValidationReport(
        file_path=file_path,
        is_valid=is_valid,
        issues=issues,
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        has_legacy_fields=has_legacy,
        specs_completeness=round(completeness, 3),
    )


def validate_file(file_path: Path) -> ValidationReport | None:
    """
    Validate a single bike note file.

    Args:
        file_path: Path to the markdown file

    Returns:
        ValidationReport, or None if file cannot be parsed
    """
    frontmatter = extract_frontmatter(file_path)
    if frontmatter is None:
        return None

    if frontmatter.get("type") != "bike":
        return None

    return validate_frontmatter(frontmatter, str(file_path))


def validate_vault(vault_path: Path) -> list[ValidationReport]:
    """
    Validate all bike notes in the vault.

    Args:
        vault_path: Path to the vault/notes directory

    Returns:
        List of ValidationReports for all bike notes
    """
    reports = []
    bikes_dir = vault_path / "bikes" if (vault_path / "bikes").exists() else vault_path

    for md_file in sorted(bikes_dir.rglob("*.md")):
        if md_file.name == "index.md":
            continue

        report = validate_file(md_file)
        if report is not None:
            reports.append(report)

    return reports


def print_validation_summary(reports: list[ValidationReport]) -> None:
    """Print a human-readable summary of validation results."""
    total = len(reports)
    valid = sum(1 for r in reports if r.is_valid)
    with_legacy = sum(1 for r in reports if r.has_legacy_fields)
    no_specs = sum(1 for r in reports if r.specs_completeness == 0.0)

    avg_completeness = (
        sum(r.specs_completeness for r in reports) / total if total > 0 else 0.0
    )

    print(f"\n{'=' * 60}")
    print("BIKE NOTE VALIDATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total bike notes:         {total}")
    print(f"Valid (required fields):   {valid}/{total}")
    print(f"With legacy fields:        {with_legacy}")
    print(f"Missing specs entirely:    {no_specs}")
    print(f"Avg specs completeness:    {avg_completeness:.1%}")

    # Show completeness distribution
    buckets = {"0%": 0, "1-25%": 0, "26-50%": 0, "51-75%": 0, "76-100%": 0}
    for r in reports:
        pct = r.specs_completeness
        if pct == 0:
            buckets["0%"] += 1
        elif pct <= 0.25:
            buckets["1-25%"] += 1
        elif pct <= 0.5:
            buckets["26-50%"] += 1
        elif pct <= 0.75:
            buckets["51-75%"] += 1
        else:
            buckets["76-100%"] += 1

    print("\nCompleteness distribution:")
    for bucket, count in buckets.items():
        bar = "#" * (count * 2)
        print(f"  {bucket:>8}: {count:>3} {bar}")

    # List worst notes
    sorted_reports = sorted(reports, key=lambda r: r.specs_completeness)
    print("\nLeast complete notes (bottom 10):")
    for r in sorted_reports[:10]:
        print(f"  {r.specs_completeness:>5.1%}  {r.file_path}")

    print(f"{'=' * 60}\n")
