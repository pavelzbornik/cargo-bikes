"""
Intelligent note merger for combining fetched data with existing bike notes.

Implements a merge strategy that:
- Updates spec fields with new data when existing value is None
- Detects conflicts when existing and new values differ significantly
- Preserves all user-authored content
- Migrates legacy top-level fields into the specs structure
"""

from __future__ import annotations

import logging
from typing import Any

from scripts.bike_note_updater.models import (
    FetchedBikeData,
    MergeConflict,
    MergeResult,
)

logger = logging.getLogger("bike_note_updater.note_merger")

# Conflict thresholds
PRICE_CONFLICT_THRESHOLD = 0.05  # 5% price difference = minor conflict
WEIGHT_CONFLICT_THRESHOLD = 0.10  # 10% weight difference = major conflict

# Sections that should never be overwritten by automated updates
PRESERVE_SECTIONS = {
    "user reviews & experiences",
    "reviews",
    "modifications & customization",
    "references",
    "photos / media",
    "cost",
    "accessories & pricing",
}


def _numeric_value(val: Any) -> float | None:
    """Try to extract a numeric value from various types."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        import re

        match = re.search(r"[\d.]+", val.replace(",", ""))
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
    return None


def _detect_numeric_conflict(
    field: str,
    old_val: Any,
    new_val: Any,
    threshold: float = 0.10,
) -> MergeConflict | None:
    """Detect if two numeric values differ beyond a threshold."""
    old_num = _numeric_value(old_val)
    new_num = _numeric_value(new_val)

    if old_num is None or new_num is None:
        return None

    if old_num == 0:
        return None

    diff_ratio = abs(new_num - old_num) / old_num

    if diff_ratio > threshold:
        severity = "major" if diff_ratio > 0.20 else "minor"
        return MergeConflict(
            field=field,
            old_value=old_val,
            new_value=new_val,
            severity=severity,
            resolution="auto" if severity == "minor" else "manual",
            reason=f"Value changed by {diff_ratio:.1%}",
        )

    return None


def _deep_merge_dict(
    existing: dict[str, Any],
    new_data: dict[str, Any],
    path: str = "",
    conflicts: list[MergeConflict] | None = None,
    fields_updated: list[str] | None = None,
    fields_preserved: list[str] | None = None,
) -> dict[str, Any]:
    """
    Recursively merge new_data into existing, tracking changes.

    Strategy:
    - If existing value is None/missing, use new value
    - If both have values and they differ, detect conflicts
    - New value wins for minor conflicts; existing wins for major
    """
    if conflicts is None:
        conflicts = []
    if fields_updated is None:
        fields_updated = []
    if fields_preserved is None:
        fields_preserved = []

    result = dict(existing)

    for key, new_val in new_data.items():
        full_path = f"{path}.{key}" if path else key
        old_val = existing.get(key)

        if new_val is None:
            continue

        if old_val is None:
            # Fill in missing data
            result[key] = new_val
            fields_updated.append(full_path)
            logger.debug(f"Populated {full_path}: {new_val}")

        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            # Recurse into nested dicts
            result[key] = _deep_merge_dict(
                old_val,
                new_val,
                full_path,
                conflicts,
                fields_updated,
                fields_preserved,
            )

        elif old_val != new_val:
            # Values differ - check for conflicts
            conflict = _detect_numeric_conflict(
                full_path,
                old_val,
                new_val,
                threshold=PRICE_CONFLICT_THRESHOLD
                if "price" in full_path
                else WEIGHT_CONFLICT_THRESHOLD,
            )

            if conflict:
                conflicts.append(conflict)
                if conflict.severity == "minor":
                    result[key] = new_val
                    fields_updated.append(full_path)
                else:
                    fields_preserved.append(full_path)
            else:
                # Non-numeric difference - preserve existing by default
                fields_preserved.append(full_path)

        else:
            # Values are the same
            fields_preserved.append(full_path)

    return result


def _migrate_legacy_fields(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """
    Migrate legacy top-level fields into the specs structure.

    Handles: price, motor, battery, range
    """
    import re

    result = dict(frontmatter)
    specs = dict(result.get("specs", {}) or {})

    # Migrate price
    legacy_price = result.pop("price", None)
    if legacy_price and not specs.get("price"):
        if isinstance(legacy_price, str):
            amount = _numeric_value(legacy_price)
            currency = None
            if "€" in legacy_price or "eur" in legacy_price.lower():
                currency = "EUR"
            elif "$" in legacy_price or "usd" in legacy_price.lower():
                currency = "USD"
            if amount:
                specs.setdefault("price", {})
                specs["price"]["amount"] = amount
                if currency:
                    specs["price"]["currency"] = currency

    # Migrate motor
    legacy_motor = result.pop("motor", None)
    if legacy_motor and not specs.get("motor"):
        if isinstance(legacy_motor, str):
            motor_info: dict[str, Any] = {}
            # Try to extract power
            power_match = re.search(r"(\d+)\s*[Ww]", legacy_motor)
            if power_match:
                motor_info["power_w"] = int(power_match.group(1))
            # Try to extract torque
            torque_match = re.search(r"(\d+)\s*[Nn]m", legacy_motor)
            if torque_match:
                motor_info["torque_nm"] = int(torque_match.group(1))
            if motor_info:
                specs.setdefault("motor", {})
                specs["motor"].update(motor_info)

    # Migrate battery
    legacy_battery = result.pop("battery", None)
    if legacy_battery and not specs.get("battery"):
        if isinstance(legacy_battery, str):
            wh_match = re.search(r"(\d+)\s*[Ww]h", legacy_battery)
            if wh_match:
                specs.setdefault("battery", {})
                specs["battery"]["capacity_wh"] = int(wh_match.group(1))

    # Migrate range
    legacy_range = result.pop("range", None)
    if legacy_range and not specs.get("range"):
        if isinstance(legacy_range, str) and legacy_range.lower() not in (
            "variable",
            "unknown",
            "n/a",
        ):
            specs.setdefault("range", {})
            specs["range"]["estimate_km"] = legacy_range

    if specs:
        result["specs"] = specs

    return result


def _fetched_data_to_dict(fetched: FetchedBikeData) -> dict[str, Any]:
    """Convert FetchedBikeData to a frontmatter-compatible dict."""
    result: dict[str, Any] = {}

    if fetched.title:
        result["title"] = fetched.title
    if fetched.brand:
        result["brand"] = fetched.brand
    if fetched.model:
        result["model"] = fetched.model
    if fetched.image_url:
        result["image"] = fetched.image_url

    if fetched.specs:
        specs_dict = fetched.specs.model_dump(exclude_none=True)
        if specs_dict:
            result["specs"] = specs_dict

    if fetched.resellers:
        result["resellers"] = [
            r.model_dump(exclude_none=True) for r in fetched.resellers
        ]

    return result


def merge_note(
    existing_frontmatter: dict[str, Any],
    fetched_data: FetchedBikeData,
    migrate_legacy: bool = True,
) -> MergeResult:
    """
    Merge fetched data with existing bike note frontmatter.

    Args:
        existing_frontmatter: Current parsed YAML frontmatter
        fetched_data: Data extracted from manufacturer page
        migrate_legacy: Whether to migrate legacy top-level fields

    Returns:
        MergeResult with merged data, conflicts, and change tracking
    """
    conflicts: list[MergeConflict] = []
    fields_updated: list[str] = []
    fields_preserved: list[str] = []

    # Start with existing frontmatter
    working = dict(existing_frontmatter)

    # Optionally migrate legacy fields first
    if migrate_legacy:
        working = _migrate_legacy_fields(working)

    # Convert fetched data to dict
    new_data = _fetched_data_to_dict(fetched_data)

    # Deep merge
    merged = _deep_merge_dict(
        working,
        new_data,
        path="",
        conflicts=conflicts,
        fields_updated=fields_updated,
        fields_preserved=fields_preserved,
    )

    return MergeResult(
        merged_frontmatter=merged,
        conflicts=conflicts,
        fields_updated=fields_updated,
        fields_preserved=fields_preserved,
    )


def merge_frontmatter_dicts(
    existing: dict[str, Any],
    new_data: dict[str, Any],
    migrate_legacy: bool = True,
) -> MergeResult:
    """
    Merge two frontmatter dictionaries directly.

    Useful when the new data comes from LLM extraction rather than
    the DataFetcher pipeline.

    Args:
        existing: Current parsed YAML frontmatter
        new_data: New data to merge in
        migrate_legacy: Whether to migrate legacy fields first

    Returns:
        MergeResult with merged data, conflicts, and change tracking
    """
    conflicts: list[MergeConflict] = []
    fields_updated: list[str] = []
    fields_preserved: list[str] = []

    working = dict(existing)
    if migrate_legacy:
        working = _migrate_legacy_fields(working)

    merged = _deep_merge_dict(
        working,
        new_data,
        path="",
        conflicts=conflicts,
        fields_updated=fields_updated,
        fields_preserved=fields_preserved,
    )

    return MergeResult(
        merged_frontmatter=merged,
        conflicts=conflicts,
        fields_updated=fields_updated,
        fields_preserved=fields_preserved,
    )
