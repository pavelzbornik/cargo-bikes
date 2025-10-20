"""Main agent orchestration for bike note updates.

This module provides the core update workflow that coordinates data fetching,
validation, merging, and writing. It can be extended with PydanticAI for
LLM-powered reasoning when API keys are available.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from .data_fetcher import DataFetcher
from .models import UpdateResult
from .note_merger import NoteMerger
from .note_writer import NoteWriter
from .schema_validator import SchemaValidator
from .utils import get_today_iso

logger = logging.getLogger("bike_note_updater")


class BikeNoteUpdater:
    """Main agent for updating bike notes.

    This class orchestrates the complete workflow:
    1. Load existing note
    2. Fetch current product data
    3. Validate against schema
    4. Merge data intelligently
    5. Write updated note
    """

    def __init__(
        self,
        fetch_timeout: int = 30,
        conflict_threshold: float = 0.1,
        validate: bool = True,
    ):
        """Initialize the updater agent.

        Args:
            fetch_timeout: HTTP request timeout in seconds
            conflict_threshold: Threshold for detecting conflicts (0.1 = 10%)
            validate: Whether to validate against schema
        """
        self.fetcher = DataFetcher(timeout=fetch_timeout)
        self.validator = SchemaValidator()
        self.merger = NoteMerger(conflict_threshold=conflict_threshold)
        self.writer = NoteWriter(validate=validate)

    async def update_bike(
        self,
        note_path: str | Path,
        fetch_url: bool = True,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Update a single bike note.

        Args:
            note_path: Path to the bike note file
            fetch_url: Whether to fetch data from product URL
            dry_run: If True, don't write changes to disk

        Returns:
            UpdateResult with operation status and details
        """
        note_path = Path(note_path)
        errors: list[str] = []
        warnings: list[str] = []
        conflicts: list[str] = []
        changes_made: dict = {}

        # Read existing note
        logger.info(f"Reading note: {note_path}")
        existing_frontmatter, body = self.writer.read_note(note_path)

        if existing_frontmatter is None:
            errors.append(f"Could not parse frontmatter from {note_path}")
            return UpdateResult(
                success=False,
                bike_name=str(note_path.stem),
                note_path=str(note_path),
                errors=errors,
                warnings=warnings,
                conflicts=conflicts,
                changes_made=changes_made,
                timestamp=datetime.now().isoformat(),
            )

        bike_name = existing_frontmatter.get("title", note_path.stem)

        # Validate existing note
        logger.info(f"Validating existing note for: {bike_name}")
        validation = self.validator.validate_frontmatter(existing_frontmatter)
        if validation.issues:
            warnings.append(
                f"Validation issues: {len(validation.issues)} issue(s) found"
            )
            for issue in validation.issues:
                warnings.append(f"  - {issue.field}: {issue.message}")

        # Fetch new data if requested
        new_data = {}
        if fetch_url:
            url = existing_frontmatter.get("url")
            if not url:
                warnings.append("No URL found in frontmatter, skipping fetch")
            else:
                logger.info(f"Fetching data from: {url}")
                try:
                    new_data = await self.fetcher.fetch_from_url(url)
                    logger.info(f"Successfully fetched data from {url}")
                except Exception as e:
                    errors.append(f"Failed to fetch from URL: {str(e)}")
                    logger.error(f"Fetch failed for {url}: {str(e)}")

        # If we got new data, merge it
        if new_data:
            logger.info("Merging fetched data with existing note")
            merge_result = self.merger.merge(existing_frontmatter, new_data)

            # Record conflicts
            for conflict in merge_result.conflicts:
                conflicts.append(
                    f"{conflict.field}: {conflict.old_value} -> {conflict.new_value} "
                    f"({conflict.conflict_type})"
                )

            changes_made = merge_result.changes_made
            merged_frontmatter = merge_result.merged_frontmatter

            # Validate merged result
            logger.info("Validating merged frontmatter")
            validation = self.validator.validate_frontmatter(merged_frontmatter)
            if not validation.is_valid:
                errors.append("Merged frontmatter failed validation")
                for issue in validation.issues:
                    errors.append(f"  - {issue.field}: {issue.message}")

                # Don't write invalid data
                return UpdateResult(
                    success=False,
                    bike_name=bike_name,
                    note_path=str(note_path),
                    errors=errors,
                    warnings=warnings,
                    conflicts=conflicts,
                    changes_made=changes_made,
                    timestamp=datetime.now().isoformat(),
                )

            # Write the updated note if not dry run
            if not dry_run:
                logger.info(f"Writing updated note to: {note_path}")
                write_result = self.writer.write_note(
                    note_path, merged_frontmatter, body
                )

                if not write_result.success:
                    errors.extend(write_result.errors)
                    return UpdateResult(
                        success=False,
                        bike_name=bike_name,
                        note_path=str(note_path),
                        errors=errors,
                        warnings=warnings,
                        conflicts=conflicts,
                        changes_made=changes_made,
                        timestamp=datetime.now().isoformat(),
                    )

                warnings.extend(write_result.warnings)
            else:
                logger.info("Dry run mode - not writing changes")
                warnings.append("Dry run mode - changes not written")

        logger.info(f"Successfully updated: {bike_name}")
        return UpdateResult(
            success=True,
            bike_name=bike_name,
            note_path=str(note_path),
            errors=errors,
            warnings=warnings,
            conflicts=conflicts,
            changes_made=changes_made,
            timestamp=datetime.now().isoformat(),
        )

    def validate_note(self, note_path: str | Path) -> UpdateResult:
        """Validate a bike note without updating.

        Args:
            note_path: Path to the bike note file

        Returns:
            UpdateResult with validation status
        """
        note_path = Path(note_path)
        errors: list[str] = []
        warnings: list[str] = []

        # Read note
        frontmatter, _ = self.writer.read_note(note_path)

        if frontmatter is None:
            errors.append(f"Could not parse frontmatter from {note_path}")
            return UpdateResult(
                success=False,
                bike_name=str(note_path.stem),
                note_path=str(note_path),
                errors=errors,
                warnings=warnings,
                conflicts=[],
                changes_made={},
                timestamp=datetime.now().isoformat(),
            )

        bike_name = frontmatter.get("title", note_path.stem)

        # Validate
        validation = self.validator.validate_frontmatter(frontmatter)

        if not validation.is_valid:
            for issue in validation.issues:
                errors.append(f"{issue.field}: {issue.message}")

        for warning in validation.warnings:
            warnings.append(warning)

        return UpdateResult(
            success=validation.is_valid,
            bike_name=bike_name,
            note_path=str(note_path),
            errors=errors,
            warnings=warnings,
            conflicts=[],
            changes_made={},
            timestamp=datetime.now().isoformat(),
        )

    def close(self) -> None:
        """Clean up resources."""
        self.fetcher.close()
