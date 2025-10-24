"""Tests for Pydantic models."""

import pytest

from scripts.bike_note_updater.models import (
    BikeFrontmatter,
    BikeSpecs,
    Conflict,
    MergeResult,
    Motor,
    UpdateResult,
    ValidationIssue,
    ValidationReport,
    WriteResult,
)


class TestMotor:
    """Test Motor model."""

    def test_motor_creation(self):
        """Test creating a Motor instance."""
        motor = Motor(make="Bosch", model="Performance Line CX", power_w=250, torque_nm=85)
        assert motor.make == "Bosch"
        assert motor.model == "Performance Line CX"
        assert motor.power_w == 250
        assert motor.torque_nm == 85

    def test_motor_optional_fields(self):
        """Test Motor with optional fields."""
        motor = Motor(make="Bosch")
        assert motor.make == "Bosch"
        assert motor.model is None
        assert motor.power_w is None


class TestBikeSpecs:
    """Test BikeSpecs model."""

    def test_bike_specs_minimal(self):
        """Test creating BikeSpecs with minimal data."""
        specs = BikeSpecs(category="longtail", model_year=2024)
        assert specs.category == "longtail"
        assert specs.model_year == 2024
        assert specs.motor is None

    def test_bike_specs_with_motor(self):
        """Test BikeSpecs with nested motor."""
        motor = Motor(make="Bosch", power_w=250)
        specs = BikeSpecs(
            category="longtail",
            model_year=2024,
            motor=motor,
        )
        assert specs.motor.make == "Bosch"
        assert specs.motor.power_w == 250


class TestBikeFrontmatter:
    """Test BikeFrontmatter model."""

    def test_frontmatter_minimal(self):
        """Test creating frontmatter with minimal required fields."""
        frontmatter = BikeFrontmatter(
            title="Test Bike",
            type="bike",
            tags=["bike", "test"],
            date="2024-01-15",
        )
        assert frontmatter.title == "Test Bike"
        assert frontmatter.type == "bike"
        assert "bike" in frontmatter.tags
        assert frontmatter.date == "2024-01-15"

    def test_frontmatter_with_specs(self):
        """Test frontmatter with specs."""
        specs = BikeSpecs(category="longtail", model_year=2024)
        frontmatter = BikeFrontmatter(
            title="Test Bike",
            type="bike",
            tags=["bike", "longtail"],
            date="2024-01-15",
            specs=specs,
        )
        assert frontmatter.specs.category == "longtail"

    def test_frontmatter_validation_fails_without_required(self):
        """Test that frontmatter validation fails without required fields."""
        with pytest.raises(Exception):
            BikeFrontmatter(title="Test")  # Missing required fields


class TestValidationReport:
    """Test ValidationReport model."""

    def test_validation_report_valid(self):
        """Test creating a valid ValidationReport."""
        report = ValidationReport(is_valid=True, issues=[], warnings=[])
        assert report.is_valid
        assert len(report.issues) == 0

    def test_validation_report_with_issues(self):
        """Test ValidationReport with issues."""
        issue = ValidationIssue(
            field="title",
            issue_type="missing",
            message="Title is required",
            suggestion="Add a title",
        )
        report = ValidationReport(is_valid=False, issues=[issue])
        assert not report.is_valid
        assert len(report.issues) == 1
        assert report.issues[0].field == "title"


class TestConflict:
    """Test Conflict model."""

    def test_conflict_creation(self):
        """Test creating a Conflict instance."""
        conflict = Conflict(
            field="motor.power_w",
            old_value=250,
            new_value=350,
            conflict_type="major",
            description="Motor power changed significantly",
        )
        assert conflict.field == "motor.power_w"
        assert conflict.old_value == 250
        assert conflict.new_value == 350
        assert conflict.conflict_type == "major"


class TestMergeResult:
    """Test MergeResult model."""

    def test_merge_result_creation(self):
        """Test creating a MergeResult."""
        result = MergeResult(
            merged_frontmatter={"title": "Test"},
            conflicts=[],
            preserved_sections=["references"],
            changes_made={"motor": "updated"},
        )
        assert result.merged_frontmatter["title"] == "Test"
        assert len(result.conflicts) == 0
        assert "references" in result.preserved_sections


class TestUpdateResult:
    """Test UpdateResult model."""

    def test_update_result_success(self):
        """Test creating a successful UpdateResult."""
        result = UpdateResult(
            success=True,
            bike_name="Test Bike",
            note_path="/path/to/note.md",
            changes_made={"motor": "updated"},
            conflicts=[],
            errors=[],
            warnings=[],
            timestamp="2024-01-15T10:00:00",
        )
        assert result.success
        assert result.bike_name == "Test Bike"
        assert len(result.errors) == 0

    def test_update_result_with_errors(self):
        """Test UpdateResult with errors."""
        result = UpdateResult(
            success=False,
            bike_name="Test Bike",
            note_path="/path/to/note.md",
            errors=["Failed to fetch URL"],
            warnings=[],
            conflicts=[],
            changes_made={},
            timestamp="2024-01-15T10:00:00",
        )
        assert not result.success
        assert len(result.errors) == 1


class TestWriteResult:
    """Test WriteResult model."""

    def test_write_result_success(self):
        """Test creating a successful WriteResult."""
        result = WriteResult(
            success=True,
            path="/path/to/note.md",
            errors=[],
            warnings=[],
        )
        assert result.success
        assert result.path == "/path/to/note.md"
