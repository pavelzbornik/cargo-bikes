"""Tests for bike_note_updater note merger."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bike_note_updater.models import (
    Battery,
    BikeSpecs,
    FetchedBikeData,
    Motor,
    Price,
)
from scripts.bike_note_updater.note_merger import (
    _migrate_legacy_fields,
    merge_frontmatter_dicts,
    merge_note,
)


class TestMigrateLegacyFields:
    """Tests for legacy field migration."""

    def test_migrate_price(self) -> None:
        fm = {"title": "Bike", "type": "bike", "price": "€5500"}
        result = _migrate_legacy_fields(fm)
        assert "price" not in result  # Legacy field removed
        assert result["specs"]["price"]["amount"] == 5500.0
        assert result["specs"]["price"]["currency"] == "EUR"

    def test_migrate_motor_power(self) -> None:
        fm = {"title": "Bike", "type": "bike", "motor": "250W"}
        result = _migrate_legacy_fields(fm)
        assert "motor" not in result
        assert result["specs"]["motor"]["power_w"] == 250

    def test_migrate_motor_torque(self) -> None:
        fm = {"title": "Bike", "type": "bike", "motor": "85Nm"}
        result = _migrate_legacy_fields(fm)
        assert "motor" not in result
        assert result["specs"]["motor"]["torque_nm"] == 85

    def test_migrate_battery(self) -> None:
        fm = {"title": "Bike", "type": "bike", "battery": "500Wh"}
        result = _migrate_legacy_fields(fm)
        assert "battery" not in result
        assert result["specs"]["battery"]["capacity_wh"] == 500

    def test_no_overwrite_existing_specs(self) -> None:
        """Legacy migration should not overwrite existing specs."""
        fm = {
            "title": "Bike",
            "type": "bike",
            "price": "€5500",
            "specs": {"price": {"amount": 4999, "currency": "EUR"}},
        }
        result = _migrate_legacy_fields(fm)
        # Existing specs price should be preserved
        assert result["specs"]["price"]["amount"] == 4999

    def test_skip_variable_range(self) -> None:
        """Legacy range 'variable' should not be migrated."""
        fm = {"title": "Bike", "type": "bike", "range": "variable"}
        result = _migrate_legacy_fields(fm)
        assert "range" not in result.get("specs", {})


class TestMergeNote:
    """Tests for merging fetched data with existing notes."""

    def test_fill_missing_fields(self) -> None:
        existing = {
            "title": "Trek Fetch+ 2",
            "type": "bike",
            "brand": "Trek",
            "specs": {"category": "longtail"},
        }
        fetched = FetchedBikeData(
            source_url="https://trek.com/fetch",
            specs=BikeSpecs(
                motor=Motor(make="Bosch", model="CX", power_w=250),
                battery=Battery(capacity_wh=500),
            ),
            extraction_method="json_ld",
        )

        result = merge_note(existing, fetched, migrate_legacy=False)
        merged = result.merged_frontmatter

        assert merged["specs"]["motor"]["make"] == "Bosch"
        assert merged["specs"]["battery"]["capacity_wh"] == 500
        assert "specs.motor" in result.fields_updated or any(
            "motor" in f for f in result.fields_updated
        )

    def test_preserve_existing_values(self) -> None:
        existing = {
            "title": "Trek Fetch+ 2",
            "type": "bike",
            "specs": {
                "motor": {"make": "Bosch", "model": "CX", "power_w": 250},
            },
        }
        fetched = FetchedBikeData(
            source_url="https://trek.com/fetch",
            specs=BikeSpecs(
                motor=Motor(make="Shimano", power_w=300),
            ),
            extraction_method="scraping",
        )

        result = merge_note(existing, fetched, migrate_legacy=False)
        merged = result.merged_frontmatter

        # Existing motor make should be preserved (conflict detected)
        assert merged["specs"]["motor"]["make"] == "Bosch"

    def test_detect_price_conflict(self) -> None:
        existing = {
            "title": "Bike",
            "type": "bike",
            "specs": {"price": {"amount": 5000, "currency": "EUR"}},
        }
        fetched = FetchedBikeData(
            source_url="https://example.com",
            specs=BikeSpecs(
                price=Price(amount=5500, currency="EUR"),
            ),
            extraction_method="json_ld",
        )

        result = merge_note(existing, fetched, migrate_legacy=False)
        # 10% price change should trigger a conflict
        assert len(result.conflicts) > 0

    def test_merge_with_legacy_migration(self) -> None:
        existing = {
            "title": "Old Bike",
            "type": "bike",
            "price": "€3999",
            "motor": "250W",
        }
        fetched = FetchedBikeData(
            source_url="https://example.com",
            specs=BikeSpecs(
                battery=Battery(capacity_wh=630),
            ),
            extraction_method="scraping",
        )

        result = merge_note(existing, fetched, migrate_legacy=True)
        merged = result.merged_frontmatter

        # Legacy fields should be migrated
        assert "price" not in merged or merged.get("price") is None
        assert merged["specs"]["price"]["amount"] == 3999.0
        # New fetched data should be added
        assert merged["specs"]["battery"]["capacity_wh"] == 630


class TestMergeFrontmatterDicts:
    """Tests for direct dict merging."""

    def test_simple_merge(self) -> None:
        existing = {"title": "Bike", "type": "bike", "specs": {"category": "longtail"}}
        new_data = {"specs": {"motor": {"make": "Bosch"}}}

        result = merge_frontmatter_dicts(existing, new_data, migrate_legacy=False)
        assert result.merged_frontmatter["specs"]["motor"]["make"] == "Bosch"
        assert result.merged_frontmatter["specs"]["category"] == "longtail"

    def test_empty_new_data(self) -> None:
        existing = {"title": "Bike", "type": "bike"}
        result = merge_frontmatter_dicts(existing, {}, migrate_legacy=False)
        assert result.merged_frontmatter == existing
