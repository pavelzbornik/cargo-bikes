"""
Autonomous research agent for cargo bike data enrichment.

Uses the Anthropic Claude API with structured outputs to:
1. Extract structured specs from raw product page text
2. Fill missing data fields from web-scraped content
3. Validate and merge data intelligently

The agent can operate in two modes:
- Offline: Validation, legacy migration, and spec table generation (no API key needed)
- Online: Web fetching + LLM-powered data extraction (requires ANTHROPIC_API_KEY)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from scripts.bike_note_updater.data_fetcher import DataFetcher
from scripts.bike_note_updater.models import (
    BatchUpdateSummary,
    BikeSpecs,
    UpdateResult,
)
from scripts.bike_note_updater.note_merger import merge_note
from scripts.bike_note_updater.note_writer import parse_note, write_note
from scripts.bike_note_updater.schema_validator import (
    validate_frontmatter,
)

logger = logging.getLogger("bike_note_updater.agent")

# System prompt for the LLM extraction agent
EXTRACTION_SYSTEM_PROMPT = """\
You are a cargo bike specification extraction specialist. Given raw text from a
manufacturer's product page, extract structured technical specifications.

Be precise with numeric values. Use the exact units specified:
- Power in watts (W)
- Torque in Newton-meters (Nm)
- Battery capacity in watt-hours (Wh)
- Weight in kilograms (kg)
- Dimensions in centimeters (cm)
- Wheel sizes in inches (in)
- Brake rotors in millimeters (mm)
- Prices as numbers without currency symbols

If a value is not mentioned in the text, use null.
If a value is a range (e.g., "50-120 km"), represent it as a string.
For motor type, use one of: "mid-drive", "rear-hub", "front-hub".
For drivetrain type, use one of: "chain", "belt".
For brake type, describe fully (e.g., "hydraulic disc", "mechanical disc").

Extract the data as accurately as possible from the provided text."""


def _get_anthropic_client() -> Any:
    """Get an Anthropic client, or None if not available."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info(
            "ANTHROPIC_API_KEY not set; LLM extraction disabled. "
            "Set the key to enable intelligent data extraction."
        )
        return None

    try:
        import anthropic

        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        logger.warning("anthropic package not installed; LLM extraction disabled")
        return None


def extract_specs_with_llm(
    raw_text: str,
    existing_title: str | None = None,
    source_url: str | None = None,
) -> BikeSpecs | None:
    """
    Use Claude to extract structured bike specs from raw product page text.

    Args:
        raw_text: Raw text content from the product page
        existing_title: The bike's title for context
        source_url: The source URL for context

    Returns:
        BikeSpecs model with extracted data, or None on failure
    """
    client = _get_anthropic_client()
    if not client:
        return None

    # Build the extraction prompt
    context_parts = []
    if existing_title:
        context_parts.append(f"Bike: {existing_title}")
    if source_url:
        context_parts.append(f"Source: {source_url}")
    context = "\n".join(context_parts)

    user_message = f"""{context}

Extract the technical specifications from the following product page text.
Return a JSON object matching the BikeSpecs schema.

--- Product Page Text ---
{raw_text[:8000]}
--- End Text ---"""

    try:
        response = client.messages.create(
            model=os.environ.get("BIKE_UPDATER_MODEL", "claude-sonnet-4-5"),
            max_tokens=4096,
            system=EXTRACTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": ["string", "null"],
                                "description": "Bike category: longtail, box, trike, compact, shorttail, midtail",
                            },
                            "model_year": {"type": ["integer", "null"]},
                            "frame_material": {"type": ["string", "null"]},
                            "weight_with_battery_kg": {"type": ["number", "null"]},
                            "load_capacity_total_kg": {"type": ["number", "null"]},
                            "load_capacity_passenger_count": {
                                "type": ["integer", "null"]
                            },
                            "motor_make": {"type": ["string", "null"]},
                            "motor_model": {"type": ["string", "null"]},
                            "motor_type": {"type": ["string", "null"]},
                            "motor_power_w": {"type": ["number", "null"]},
                            "motor_torque_nm": {"type": ["number", "null"]},
                            "battery_capacity_wh": {"type": ["number", "null"]},
                            "battery_configuration": {"type": ["string", "null"]},
                            "battery_removable": {"type": ["boolean", "null"]},
                            "drivetrain_type": {"type": ["string", "null"]},
                            "drivetrain_speeds": {"type": ["string", "null"]},
                            "brakes_type": {"type": ["string", "null"]},
                            "wheels_front_size_in": {"type": ["string", "null"]},
                            "wheels_rear_size_in": {"type": ["string", "null"]},
                            "wheels_tire": {"type": ["string", "null"]},
                            "suspension_front": {"type": ["string", "null"]},
                            "suspension_rear": {"type": ["string", "null"]},
                            "range_estimate_km": {"type": ["string", "null"]},
                            "price_amount": {"type": ["number", "null"]},
                            "price_currency": {"type": ["string", "null"]},
                        },
                        "required": [
                            "category",
                            "motor_make",
                            "motor_model",
                            "battery_capacity_wh",
                            "price_amount",
                            "price_currency",
                        ],
                        "additionalProperties": False,
                    },
                }
            },
        )

        # Parse the structured response
        result_text = response.content[0].text
        data = json.loads(result_text)

        return _flat_data_to_bike_specs(data)

    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        return None


def _flat_data_to_bike_specs(data: dict[str, Any]) -> BikeSpecs:
    """Convert flat extracted data to nested BikeSpecs model."""
    from scripts.bike_note_updater.models import (
        Battery,
        Brakes,
        Drivetrain,
        Frame,
        LoadCapacity,
        Motor,
        Price,
        Range,
        Suspension,
        Weight,
        Wheels,
    )

    specs = BikeSpecs(category=data.get("category"), model_year=data.get("model_year"))

    if data.get("frame_material"):
        specs.frame = Frame(material=data["frame_material"])

    if data.get("weight_with_battery_kg"):
        specs.weight = Weight(with_battery_kg=data["weight_with_battery_kg"])

    if data.get("load_capacity_total_kg") or data.get(
        "load_capacity_passenger_count"
    ):
        specs.load_capacity = LoadCapacity(
            total_kg=data.get("load_capacity_total_kg"),
            passenger_count_excluding_rider=data.get(
                "load_capacity_passenger_count"
            ),
        )

    if any(data.get(k) for k in ["motor_make", "motor_model", "motor_power_w"]):
        specs.motor = Motor(
            make=data.get("motor_make"),
            model=data.get("motor_model"),
            type=data.get("motor_type"),
            power_w=data.get("motor_power_w"),
            torque_nm=data.get("motor_torque_nm"),
        )

    if data.get("battery_capacity_wh"):
        specs.battery = Battery(
            capacity_wh=data["battery_capacity_wh"],
            configuration=data.get("battery_configuration"),
            removable=data.get("battery_removable"),
        )

    if data.get("drivetrain_type") or data.get("drivetrain_speeds"):
        specs.drivetrain = Drivetrain(
            type=data.get("drivetrain_type"),
            speeds=data.get("drivetrain_speeds"),
        )

    if data.get("brakes_type"):
        specs.brakes = Brakes(type=data["brakes_type"])

    if data.get("wheels_front_size_in") or data.get("wheels_rear_size_in"):
        specs.wheels = Wheels(
            front_size_in=data.get("wheels_front_size_in"),
            rear_size_in=data.get("wheels_rear_size_in"),
            tire=data.get("wheels_tire"),
        )

    if data.get("suspension_front") or data.get("suspension_rear"):
        specs.suspension = Suspension(
            front=data.get("suspension_front"),
            rear=data.get("suspension_rear"),
        )

    if data.get("range_estimate_km"):
        specs.range = Range(estimate_km=data["range_estimate_km"])

    if data.get("price_amount"):
        specs.price = Price(
            amount=data["price_amount"],
            currency=data.get("price_currency"),
        )

    return specs


def update_single_bike(
    note_path: Path,
    fetch_url: bool = True,
    use_llm: bool = True,
    dry_run: bool = False,
    migrate_legacy: bool = True,
) -> UpdateResult:
    """
    Update a single bike note with fetched and extracted data.

    Args:
        note_path: Path to the bike note markdown file
        fetch_url: Whether to fetch data from the product URL
        use_llm: Whether to use LLM for data extraction
        dry_run: Preview changes without writing
        migrate_legacy: Whether to migrate legacy frontmatter fields

    Returns:
        UpdateResult with changes, conflicts, and errors
    """
    result = UpdateResult(
        success=False,
        bike_name=note_path.stem,
        note_path=str(note_path),
    )

    # Parse existing note
    frontmatter, body = parse_note(note_path)
    if frontmatter is None:
        result.errors.append(f"Could not parse frontmatter from {note_path}")
        return result

    if frontmatter.get("type") != "bike":
        result.errors.append(f"Not a bike note: type={frontmatter.get('type')}")
        return result

    result.bike_name = frontmatter.get("title", note_path.stem)

    # Validate before
    result.validation_before = validate_frontmatter(frontmatter, str(note_path))

    # Fetch data from URL if requested
    fetched_data = None
    product_url = frontmatter.get("url")

    if fetch_url and product_url:
        logger.info(f"Fetching data from {product_url}")
        fetcher = DataFetcher()
        fetched_data = fetcher.extract_from_url(product_url)

        # If we only got raw text and LLM is enabled, use LLM extraction
        if (
            fetched_data
            and fetched_data.extraction_method == "raw_text_only"
            and use_llm
            and fetched_data.raw_text
        ):
            logger.info("Using LLM for spec extraction")
            llm_specs = extract_specs_with_llm(
                fetched_data.raw_text,
                existing_title=frontmatter.get("title"),
                source_url=product_url,
            )
            if llm_specs:
                fetched_data.specs = llm_specs
                fetched_data.extraction_method = "llm"

    # Merge data
    if fetched_data:
        merge_result = merge_note(
            frontmatter, fetched_data, migrate_legacy=migrate_legacy
        )
        merged_frontmatter = merge_result.merged_frontmatter
        result.conflicts = merge_result.conflicts
        result.changes_made = merge_result.fields_updated
    else:
        # Even without fetched data, migrate legacy fields
        if migrate_legacy:
            from scripts.bike_note_updater.note_merger import (
                merge_frontmatter_dicts,
            )

            merge_result = merge_frontmatter_dicts(
                frontmatter, {}, migrate_legacy=True
            )
            merged_frontmatter = merge_result.merged_frontmatter
            result.changes_made = merge_result.fields_updated
        else:
            merged_frontmatter = frontmatter

    # Validate after merge
    result.validation_after = validate_frontmatter(
        merged_frontmatter, str(note_path)
    )

    # Write updated note
    if not dry_run:
        write_result = write_note(
            note_path,
            merged_frontmatter,
            body=body,
            update_specs_table=True,
            dry_run=False,
        )
        if not write_result["success"]:
            result.errors.extend(write_result["errors"])
            return result

    result.success = True
    return result


def update_batch(
    vault_path: Path,
    brand: str | None = None,
    fetch_url: bool = True,
    use_llm: bool = True,
    dry_run: bool = False,
    migrate_legacy: bool = True,
    limit: int | None = None,
) -> BatchUpdateSummary:
    """
    Update multiple bike notes in the vault.

    Args:
        vault_path: Path to the vault/notes directory
        brand: Optional brand filter
        fetch_url: Whether to fetch data from product URLs
        use_llm: Whether to use LLM for data extraction
        dry_run: Preview changes without writing
        migrate_legacy: Whether to migrate legacy fields
        limit: Maximum number of notes to process

    Returns:
        BatchUpdateSummary with all results
    """
    summary = BatchUpdateSummary()

    bikes_dir = vault_path / "bikes" if (vault_path / "bikes").exists() else vault_path

    # Collect bike note files
    note_files = []
    if brand:
        brand_dir = bikes_dir / brand.lower().replace(" ", "-")
        if brand_dir.exists():
            note_files = sorted(
                f for f in brand_dir.glob("*.md") if f.name != "index.md"
            )
        else:
            logger.warning(f"Brand directory not found: {brand_dir}")
    else:
        note_files = sorted(
            f for f in bikes_dir.rglob("*.md") if f.name != "index.md"
        )

    if limit:
        note_files = note_files[:limit]

    total = len(note_files)
    logger.info(f"Processing {total} bike notes...")

    for i, note_file in enumerate(note_files, 1):
        logger.info(f"[{i}/{total}] Processing {note_file.name}")

        try:
            result = update_single_bike(
                note_file,
                fetch_url=fetch_url,
                use_llm=use_llm,
                dry_run=dry_run,
                migrate_legacy=migrate_legacy,
            )

            summary.results.append(result)
            summary.total_processed += 1

            if result.success:
                if result.changes_made:
                    summary.successful_updates += 1
                else:
                    summary.skipped += 1
            else:
                summary.errors += 1

            if result.conflicts:
                summary.conflicts_flagged += len(result.conflicts)

        except Exception as e:
            logger.error(f"Error processing {note_file}: {e}")
            summary.errors += 1
            summary.results.append(
                UpdateResult(
                    success=False,
                    bike_name=note_file.stem,
                    note_path=str(note_file),
                    errors=[str(e)],
                )
            )

    return summary


def print_update_summary(summary: BatchUpdateSummary) -> None:
    """Print a human-readable update summary."""
    print(f"\n{'=' * 60}")
    print("BIKE NOTE UPDATE SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total processed:     {summary.total_processed}")
    print(f"Successful updates:  {summary.successful_updates}")
    print(f"Conflicts flagged:   {summary.conflicts_flagged}")
    print(f"Errors:              {summary.errors}")
    print(f"Skipped (no change): {summary.skipped}")

    # List updates
    updated = [r for r in summary.results if r.success and r.changes_made]
    if updated:
        print("\nUpdated bikes:")
        for r in updated:
            changes = ", ".join(r.changes_made[:5])
            if len(r.changes_made) > 5:
                changes += f" (+{len(r.changes_made) - 5} more)"
            print(f"  - {r.bike_name}: {changes}")

    # List conflicts
    conflicted = [r for r in summary.results if r.conflicts]
    if conflicted:
        print("\nConflicts requiring review:")
        for r in conflicted:
            for c in r.conflicts:
                print(f"  - {r.bike_name}: {c.field} ({c.reason})")

    # List errors
    errored = [r for r in summary.results if r.errors]
    if errored:
        print("\nErrors:")
        for r in errored:
            for e in r.errors:
                print(f"  - {r.bike_name}: {e}")

    print(f"{'=' * 60}\n")
