"""Tests for bike_note_updater Pydantic models."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bike_note_updater.models import (
    Battery,
    BikeFrontmatter,
    BikeSpecs,
    Frame,
    LoadCapacity,
    MergeConflict,
    Motor,
    Price,
    ResellerEntry,
    UpdateResult,
    ValidationIssue,
    ValidationReport,
    Weight,
)


class TestBikeSpecs:
    """Tests for the BikeSpecs model."""

    def test_empty_specs(self) -> None:
        specs = BikeSpecs()
        assert specs.category is None
        assert specs.motor is None
        assert specs.battery is None

    def test_full_specs(self) -> None:
        specs = BikeSpecs(
            category="longtail",
            model_year=2024,
            frame=Frame(material="aluminum", size="one size"),
            weight=Weight(with_battery_kg=31.0),
            load_capacity=LoadCapacity(
                total_kg=200.0, passenger_count_excluding_rider=2
            ),
            motor=Motor(
                make="Bosch",
                model="Performance Line CX",
                type="mid-drive",
                power_w=250,
                torque_nm=85,
            ),
            battery=Battery(
                capacity_wh=500, configuration="single", removable=True
            ),
            price=Price(amount=5999, currency="USD"),
        )
        assert specs.category == "longtail"
        assert specs.motor is not None
        assert specs.motor.make == "Bosch"
        assert specs.price is not None
        assert specs.price.amount == 5999

    def test_specs_serialization(self) -> None:
        specs = BikeSpecs(
            category="box",
            motor=Motor(make="Shimano", power_w=250),
            battery=Battery(capacity_wh=630),
        )
        data = specs.model_dump(exclude_none=True)
        assert data["category"] == "box"
        assert data["motor"]["make"] == "Shimano"
        assert "frame" not in data  # None fields excluded


class TestBikeFrontmatter:
    """Tests for the BikeFrontmatter model."""

    def test_minimal_frontmatter(self) -> None:
        fm = BikeFrontmatter(title="Test Bike")
        assert fm.title == "Test Bike"
        assert fm.type == "bike"
        assert fm.specs is None

    def test_full_frontmatter(self) -> None:
        fm = BikeFrontmatter(
            title="Trek Fetch+ 2",
            type="bike",
            brand="Trek",
            model="Fetch+ 2",
            tags=["bike", "longtail", "electric"],
            date="2024-10-16",
            url="https://www.trekbikes.com/fetch",
            specs=BikeSpecs(category="longtail"),
            resellers=[
                ResellerEntry(
                    name="Trek Store",
                    url="https://trek.com",
                    price=5999,
                    currency="USD",
                    availability="in-stock",
                )
            ],
        )
        assert fm.brand == "Trek"
        assert len(fm.resellers) == 1
        assert fm.resellers[0].name == "Trek Store"

    def test_legacy_fields(self) -> None:
        """Test that legacy fields are accepted for backward compatibility."""
        fm = BikeFrontmatter(
            title="Old Bike",
            price="€5500",
            motor="85Nm",
            battery="400Wh",
        )
        assert fm.price == "€5500"
        assert fm.motor == "85Nm"


class TestResellerEntry:
    """Tests for the ResellerEntry model."""

    def test_minimal_reseller(self) -> None:
        r = ResellerEntry(name="BikeShop")
        assert r.name == "BikeShop"
        assert r.url is None

    def test_full_reseller(self) -> None:
        r = ResellerEntry(
            name="Cyclable",
            url="https://cyclable.com/bike",
            price=2999,
            currency="EUR",
            region="EU",
            availability="in-stock",
            note="Free shipping",
        )
        assert r.price == 2999
        assert r.region == "EU"


class TestValidationModels:
    """Tests for validation-related models."""

    def test_validation_issue(self) -> None:
        issue = ValidationIssue(
            field="specs",
            issue_type="missing",
            message="No specs section found",
            suggestion="Add a specs section",
        )
        assert issue.field == "specs"
        assert issue.suggestion is not None

    def test_validation_report(self) -> None:
        report = ValidationReport(
            file_path="vault/notes/bikes/trek/fetch-2.md",
            is_valid=True,
            specs_completeness=0.75,
        )
        assert report.is_valid
        assert report.specs_completeness == 0.75

    def test_merge_conflict(self) -> None:
        conflict = MergeConflict(
            field="specs.price.amount",
            old_value=5999,
            new_value=6499,
            severity="minor",
            reason="Price changed by 8.3%",
        )
        assert conflict.severity == "minor"

    def test_update_result(self) -> None:
        result = UpdateResult(
            success=True,
            bike_name="Trek Fetch+ 2",
            note_path="vault/notes/bikes/trek/fetch-2.md",
            changes_made=["specs.price.amount", "specs.battery.capacity_wh"],
        )
        assert result.success
        assert len(result.changes_made) == 2
