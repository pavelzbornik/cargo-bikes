"""Tests for bike_note_updater schema validator."""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bike_note_updater.schema_validator import (
    extract_frontmatter,
    validate_file,
    validate_frontmatter,
)


class TestValidateFrontmatter:
    """Tests for frontmatter validation logic."""

    def test_valid_complete_frontmatter(self) -> None:
        fm = {
            "title": "Trek Fetch+ 2",
            "type": "bike",
            "brand": "Trek",
            "model": "Fetch+ 2",
            "tags": ["bike", "longtail", "electric"],
            "url": "https://www.trekbikes.com/fetch",
            "date": "2024-10-16",
            "specs": {
                "category": "longtail",
                "model_year": 2024,
                "motor": {"make": "Bosch", "model": "CX", "power_w": 250},
                "battery": {"capacity_wh": 500},
                "price": {"amount": 5999, "currency": "USD"},
            },
        }
        report = validate_frontmatter(fm)
        assert report.is_valid
        assert report.specs_completeness > 0

    def test_missing_required_fields(self) -> None:
        fm = {"brand": "Trek"}  # Missing title and type
        report = validate_frontmatter(fm)
        assert not report.is_valid
        assert "title" in report.missing_required
        assert "type" in report.missing_required

    def test_wrong_type(self) -> None:
        fm = {"title": "Some Page", "type": "brand"}
        report = validate_frontmatter(fm)
        # type check should flag non-bike type
        issues = [i for i in report.issues if i.field == "type"]
        assert len(issues) > 0

    def test_legacy_fields_detected(self) -> None:
        fm = {
            "title": "Old Bike",
            "type": "bike",
            "price": "€5500",
            "motor": "85Nm",
            "battery": "400Wh",
        }
        report = validate_frontmatter(fm)
        assert report.has_legacy_fields
        deprecated_issues = [i for i in report.issues if i.issue_type == "deprecated"]
        assert len(deprecated_issues) == 3

    def test_missing_specs_section(self) -> None:
        fm = {"title": "Bike Without Specs", "type": "bike"}
        report = validate_frontmatter(fm)
        assert report.specs_completeness == 0.0
        missing_specs = [
            i for i in report.issues if i.field == "specs" and i.issue_type == "missing"
        ]
        assert len(missing_specs) == 1

    def test_specs_completeness_scoring(self) -> None:
        # Minimal specs
        fm_minimal = {
            "title": "Minimal",
            "type": "bike",
            "specs": {"category": "longtail"},
        }
        report_min = validate_frontmatter(fm_minimal)

        # More complete specs
        fm_complete = {
            "title": "Complete",
            "type": "bike",
            "specs": {
                "category": "longtail",
                "model_year": 2024,
                "motor": {
                    "make": "Bosch",
                    "model": "CX",
                    "type": "mid-drive",
                    "power_w": 250,
                    "torque_nm": 85,
                },
                "battery": {"capacity_wh": 500, "configuration": "single"},
                "drivetrain": {"type": "chain", "speeds": "10-speed"},
                "brakes": {"type": "hydraulic disc"},
                "wheels": {"front_size_in": '20"', "rear_size_in": '20"'},
                "price": {"amount": 5999, "currency": "USD"},
                "weight": {"with_battery_kg": 31},
                "load_capacity": {"total_kg": 200},
            },
        }
        report_full = validate_frontmatter(fm_complete)

        assert report_full.specs_completeness > report_min.specs_completeness

    def test_invalid_tag_format(self) -> None:
        fm = {
            "title": "Bad Tags",
            "type": "bike",
            "tags": ["Bike", "Long Tail", "electric_bike"],
        }
        report = validate_frontmatter(fm)
        tag_issues = [i for i in report.issues if i.field == "tags"]
        assert len(tag_issues) >= 2  # "Bike" and "Long Tail" are invalid

    def test_valid_tag_format(self) -> None:
        fm = {
            "title": "Good Tags",
            "type": "bike",
            "tags": ["bike", "long-tail", "electric"],
        }
        report = validate_frontmatter(fm)
        tag_issues = [i for i in report.issues if i.field == "tags"]
        assert len(tag_issues) == 0

    def test_invalid_date_format(self) -> None:
        fm = {"title": "Bad Date", "type": "bike", "date": "16/10/2024"}
        report = validate_frontmatter(fm)
        date_issues = [i for i in report.issues if i.field == "date"]
        assert len(date_issues) == 1

    def test_valid_date_format(self) -> None:
        fm = {"title": "Good Date", "type": "bike", "date": "2024-10-16"}
        report = validate_frontmatter(fm)
        date_issues = [i for i in report.issues if i.field == "date"]
        assert len(date_issues) == 0

    def test_invalid_url_format(self) -> None:
        fm = {
            "title": "Bad URL",
            "type": "bike",
            "url": "not-a-url",
        }
        report = validate_frontmatter(fm)
        url_issues = [i for i in report.issues if i.field == "url"]
        assert len(url_issues) == 1

    def test_recommended_fields_tracking(self) -> None:
        fm = {"title": "Minimal Bike", "type": "bike"}
        report = validate_frontmatter(fm)
        assert "brand" in report.missing_recommended
        assert "model" in report.missing_recommended
        assert "url" in report.missing_recommended


class TestExtractFrontmatter:
    """Tests for frontmatter extraction from markdown files."""

    def test_extract_valid_frontmatter(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\ntitle: Test Bike\ntype: bike\n---\n\n# Content\n")
            f.flush()
            result = extract_frontmatter(Path(f.name))
        assert result is not None
        assert result["title"] == "Test Bike"

    def test_extract_no_frontmatter(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Just a heading\n\nSome content.\n")
            f.flush()
            result = extract_frontmatter(Path(f.name))
        assert result is None

    def test_extract_empty_frontmatter(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\n---\n\n# Empty frontmatter\n")
            f.flush()
            result = extract_frontmatter(Path(f.name))
        assert result == {}


class TestValidateFile:
    """Tests for file-level validation."""

    def test_validate_bike_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                "---\ntitle: Test Bike\ntype: bike\nbrand: Test\n"
                "specs:\n  category: longtail\n---\n\n# Content\n"
            )
            f.flush()
            report = validate_file(Path(f.name))
        assert report is not None
        assert report.is_valid

    def test_validate_non_bike_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\ntitle: Brand Page\ntype: brand\n---\n\n# Content\n")
            f.flush()
            report = validate_file(Path(f.name))
        assert report is None  # Not a bike note
