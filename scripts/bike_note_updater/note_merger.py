"""Intelligent merging of fetched data with existing notes.

This module handles merging new product data with existing bike notes while
preserving user-added content and detecting conflicts.
"""

from __future__ import annotations

from typing import Any

from .models import Conflict, MergeResult
from .utils import is_significant_change


class NoteMerger:
    """Merges fetched product data with existing bike notes."""

    def __init__(self, conflict_threshold: float = 0.1):
        """Initialize the note merger.

        Args:
            conflict_threshold: Threshold for detecting significant changes (default 0.1 = 10%)
        """
        self.conflict_threshold = conflict_threshold

    def merge(
        self,
        existing_frontmatter: dict,
        new_data: dict,
        preserve_sections: list[str] | None = None,
    ) -> MergeResult:
        """Merge new data with existing frontmatter.

        Args:
            existing_frontmatter: Current frontmatter from the note
            new_data: Newly fetched product data
            preserve_sections: List of markdown sections to preserve

        Returns:
            MergeResult with merged data and conflicts
        """
        merged = existing_frontmatter.copy()
        conflicts: list[Conflict] = []
        changes_made: dict[str, Any] = {}

        if preserve_sections is None:
            preserve_sections = [
                "references",
                "user-reviews",
                "modifications-and-customization",
            ]

        # Update specs if present in new data
        if "specs" in new_data:
            merged_specs, spec_conflicts, spec_changes = self._merge_specs(
                existing_frontmatter.get("specs", {}),
                new_data["specs"],
            )
            merged["specs"] = merged_specs
            conflicts.extend(spec_conflicts)
            if spec_changes:
                changes_made["specs"] = spec_changes

        # Update resellers if present
        if "resellers" in new_data:
            merged["resellers"] = new_data["resellers"]
            if new_data["resellers"] != existing_frontmatter.get("resellers"):
                changes_made["resellers"] = "updated"

        # Update image if present
        if new_data.get("image"):
            old_image = existing_frontmatter.get("image")
            if new_data["image"] != old_image:
                merged["image"] = new_data["image"]
                changes_made["image"] = f"{old_image} -> {new_data['image']}"

        # Update URL if present
        if new_data.get("url"):
            old_url = existing_frontmatter.get("url")
            if new_data["url"] != old_url:
                merged["url"] = new_data["url"]
                changes_made["url"] = f"{old_url} -> {new_data['url']}"

        # Update title if present and significantly different
        if new_data.get("title"):
            old_title = existing_frontmatter.get("title")
            if new_data["title"] != old_title:
                # Flag as conflict if titles are significantly different
                conflicts.append(
                    Conflict(
                        field="title",
                        old_value=old_title,
                        new_value=new_data["title"],
                        conflict_type="minor",
                        description="Product title has changed",
                    )
                )
                # Still update it
                merged["title"] = new_data["title"]
                changes_made["title"] = f"{old_title} -> {new_data['title']}"

        return MergeResult(
            merged_frontmatter=merged,
            conflicts=conflicts,
            preserved_sections=preserve_sections,
            changes_made=changes_made,
        )

    def _merge_specs(
        self,
        existing_specs: dict,
        new_specs: dict,
    ) -> tuple[dict, list[Conflict], dict]:
        """Merge specifications dictionaries.

        Args:
            existing_specs: Current specs
            new_specs: New specs from fetched data

        Returns:
            Tuple of (merged_specs, conflicts, changes)
        """
        merged = existing_specs.copy()
        conflicts: list[Conflict] = []
        changes: dict[str, Any] = {}

        # Merge each spec category
        for key, new_value in new_specs.items():
            if new_value is None:
                continue

            old_value = existing_specs.get(key)

            # Handle nested dicts (motor, battery, etc.)
            if isinstance(new_value, dict) and isinstance(old_value, dict):
                merged_nested, nested_conflicts = self._merge_nested_spec(
                    key, old_value, new_value
                )
                merged[key] = merged_nested
                conflicts.extend(nested_conflicts)
                if merged_nested != old_value:
                    changes[key] = "updated"

            # Handle lists
            elif isinstance(new_value, list):
                if new_value != old_value:
                    merged[key] = new_value
                    changes[key] = "updated"

            # Handle simple values
            else:
                conflict = self._detect_value_conflict(key, old_value, new_value)
                if conflict:
                    conflicts.append(conflict)

                # Update the value
                if new_value != old_value:
                    merged[key] = new_value
                    changes[key] = f"{old_value} -> {new_value}"

        return merged, conflicts, changes

    def _merge_nested_spec(
        self,
        parent_key: str,
        old_dict: dict,
        new_dict: dict,
    ) -> tuple[dict, list[Conflict]]:
        """Merge nested specification dictionaries.

        Args:
            parent_key: Parent key name (e.g., "motor", "battery")
            old_dict: Existing nested dict
            new_dict: New nested dict

        Returns:
            Tuple of (merged dict, conflicts)
        """
        merged = old_dict.copy()
        conflicts: list[Conflict] = []

        for key, new_value in new_dict.items():
            if new_value is None:
                continue

            old_value = old_dict.get(key)
            field_path = f"{parent_key}.{key}"

            # Recursively merge nested dicts
            if isinstance(new_value, dict) and isinstance(old_value, dict):
                merged_nested, nested_conflicts = self._merge_nested_spec(
                    field_path, old_value, new_value
                )
                merged[key] = merged_nested
                conflicts.extend(nested_conflicts)
            else:
                # Check for conflicts
                conflict = self._detect_value_conflict(field_path, old_value, new_value)
                if conflict:
                    conflicts.append(conflict)

                # Update value
                merged[key] = new_value

        return merged, conflicts

    def _detect_value_conflict(
        self,
        field: str,
        old_value: Any,
        new_value: Any,
    ) -> Conflict | None:
        """Detect if there's a conflict between old and new values.

        Args:
            field: Field name
            old_value: Existing value
            new_value: New value

        Returns:
            Conflict object if conflict detected, None otherwise
        """
        if old_value is None or old_value == new_value:
            return None

        # Check for significant numeric changes
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            if is_significant_change(old_value, new_value, self.conflict_threshold):
                return Conflict(
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                    conflict_type="major",
                    description=f"Significant change detected: {old_value} -> {new_value}",
                )

        # Check for string changes that might be significant
        if isinstance(old_value, str) and isinstance(new_value, str):
            # Motor/battery model changes are significant
            if any(
                keyword in field.lower()
                for keyword in ["motor.model", "battery.model", "motor.make"]
            ):
                return Conflict(
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                    conflict_type="major",
                    description=f"Component model changed: {old_value} -> {new_value}",
                )

        return None

    def detect_conflicts(self, old_value: Any, new_value: Any) -> Conflict | None:
        """Detect conflicts between old and new values.

        Args:
            old_value: The old value
            new_value: The new value

        Returns:
            Conflict object if conflict detected, None otherwise
        """
        return self._detect_value_conflict("value", old_value, new_value)
