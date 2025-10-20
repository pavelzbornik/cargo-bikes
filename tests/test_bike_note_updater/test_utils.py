"""Tests for utility functions."""

import tempfile
from pathlib import Path

from scripts.bike_note_updater.utils import (
    calculate_percentage_change,
    extract_brand_from_path,
    find_bike_notes,
    format_yaml_frontmatter,
    get_today_iso,
    is_significant_change,
    normalize_tag,
    parse_frontmatter,
    validate_iso_date,
)


class TestNormalizeTag:
    """Test tag normalization."""

    def test_lowercase_conversion(self):
        """Test that tags are converted to lowercase."""
        assert normalize_tag("BIKE") == "bike"
        assert normalize_tag("Trek") == "trek"

    def test_space_to_hyphen(self):
        """Test that spaces are converted to hyphens."""
        assert normalize_tag("cargo bike") == "cargo-bike"
        assert normalize_tag("big ben") == "big-ben"

    def test_remove_special_chars(self):
        """Test that special characters are removed."""
        assert normalize_tag("bike!@#") == "bike"
        assert normalize_tag("cargo-bike?") == "cargo-bike"

    def test_multiple_hyphens(self):
        """Test that multiple hyphens are collapsed."""
        assert normalize_tag("cargo---bike") == "cargo-bike"
        assert normalize_tag("bike--brand") == "bike-brand"

    def test_already_normalized(self):
        """Test that already normalized tags remain unchanged."""
        assert normalize_tag("bike") == "bike"
        assert normalize_tag("cargo-bike") == "cargo-bike"


class TestValidateIsoDate:
    """Test ISO date validation."""

    def test_valid_iso_date(self):
        """Test valid ISO 8601 dates."""
        assert validate_iso_date("2024-01-15")
        assert validate_iso_date("2023-12-31")
        assert validate_iso_date("2025-06-01")

    def test_invalid_date_format(self):
        """Test invalid date formats."""
        assert not validate_iso_date("01-15-2024")
        assert not validate_iso_date("2024/01/15")
        assert not validate_iso_date("15-01-2024")

    def test_invalid_date_values(self):
        """Test invalid date values."""
        assert not validate_iso_date("2024-13-01")  # Invalid month
        assert not validate_iso_date("2024-01-32")  # Invalid day
        assert not validate_iso_date("not-a-date")


class TestGetTodayIso:
    """Test getting today's date in ISO format."""

    def test_get_today_iso(self):
        """Test that get_today_iso returns a valid ISO date."""
        today = get_today_iso()
        assert validate_iso_date(today)
        assert len(today) == 10  # YYYY-MM-DD format


class TestParseFrontmatter:
    """Test YAML frontmatter parsing."""

    def test_parse_valid_frontmatter(self):
        """Test parsing valid frontmatter."""
        content = """---
title: "Test Bike"
type: bike
tags: [bike, test]
---

# Content here"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter is not None
        assert frontmatter["title"] == "Test Bike"
        assert "# Content here" in body

    def test_parse_no_frontmatter(self):
        """Test content without frontmatter."""
        content = "# Just content\nNo frontmatter here"
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter is None
        assert "# Just content" in body

    def test_parse_invalid_yaml(self):
        """Test handling of invalid YAML."""
        content = """---
title: "Test
invalid: yaml: structure
---
Body"""
        frontmatter, _body = parse_frontmatter(content)
        assert frontmatter is None


class TestFormatYamlFrontmatter:
    """Test YAML frontmatter formatting."""

    def test_format_simple_dict(self):
        """Test formatting a simple dictionary."""
        data = {"title": "Test Bike", "type": "bike"}
        yaml_str = format_yaml_frontmatter(data)
        assert "title: Test Bike" in yaml_str
        assert "type: bike" in yaml_str

    def test_format_with_list(self):
        """Test formatting with lists."""
        data = {"tags": ["bike", "test", "longtail"]}
        yaml_str = format_yaml_frontmatter(data)
        assert "tags:" in yaml_str
        assert "- bike" in yaml_str

    def test_format_with_nested_dict(self):
        """Test formatting with nested dictionaries."""
        data = {
            "specs": {
                "motor": {"make": "Bosch", "power_w": 250},
            }
        }
        yaml_str = format_yaml_frontmatter(data)
        assert "specs:" in yaml_str
        assert "motor:" in yaml_str
        assert "make: Bosch" in yaml_str


class TestCalculatePercentageChange:
    """Test percentage change calculation."""

    def test_zero_to_nonzero(self):
        """Test change from zero to non-zero."""
        assert calculate_percentage_change(0, 100) == 1.0

    def test_nonzero_to_zero(self):
        """Test change from non-zero to zero."""
        assert calculate_percentage_change(100, 0) == 1.0

    def test_zero_to_zero(self):
        """Test no change from zero."""
        assert calculate_percentage_change(0, 0) == 0.0

    def test_positive_change(self):
        """Test positive percentage change."""
        change = calculate_percentage_change(100, 110)
        assert 0.09 < change < 0.11  # ~10% change

    def test_negative_change(self):
        """Test negative percentage change."""
        change = calculate_percentage_change(100, 90)
        assert 0.09 < change < 0.11  # ~10% change (absolute)


class TestIsSignificantChange:
    """Test significant change detection."""

    def test_not_significant_change(self):
        """Test changes below threshold."""
        assert not is_significant_change(100, 105, threshold=0.1)  # 5% change
        assert not is_significant_change(100, 95, threshold=0.1)

    def test_significant_change(self):
        """Test changes above threshold."""
        assert is_significant_change(100, 115, threshold=0.1)  # 15% change
        assert is_significant_change(100, 85, threshold=0.1)

    def test_exactly_threshold(self):
        """Test change exactly at threshold."""
        assert not is_significant_change(100, 110, threshold=0.1)  # Exactly 10%


class TestFindBikeNotes:
    """Test finding bike notes in vault."""

    def test_find_notes_in_temp_dir(self):
        """Test finding bike notes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            # Create test files
            (bikes_dir / "bike1.md").write_text("test")
            (bikes_dir / "bike2.md").write_text("test")

            notes = find_bike_notes(vault_path)
            assert len(notes) == 2

    def test_find_notes_by_brand(self):
        """Test finding notes filtered by brand."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create multiple brand directories
            trek_dir = vault_path / "notes" / "bikes" / "trek"
            tern_dir = vault_path / "notes" / "bikes" / "tern"
            trek_dir.mkdir(parents=True)
            tern_dir.mkdir(parents=True)

            (trek_dir / "bike1.md").write_text("test")
            (tern_dir / "bike2.md").write_text("test")

            # Find only trek bikes
            notes = find_bike_notes(vault_path, brand="trek")
            assert len(notes) == 1
            assert "trek" in str(notes[0])

    def test_find_notes_empty_vault(self):
        """Test finding notes in empty vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            notes = find_bike_notes(vault_path)
            assert len(notes) == 0


class TestExtractBrandFromPath:
    """Test extracting brand name from path."""

    def test_extract_brand_from_valid_path(self):
        """Test extracting brand from valid bike note path."""
        path = Path("/vault/notes/bikes/trek/fetch-2.md")
        brand = extract_brand_from_path(path)
        assert brand == "trek"

    def test_extract_brand_different_structure(self):
        """Test extracting brand from different path structures."""
        path = Path("vault/notes/bikes/tern/gsd-s10.md")
        brand = extract_brand_from_path(path)
        assert brand == "tern"

    def test_extract_brand_invalid_path(self):
        """Test extracting brand from invalid path."""
        path = Path("/some/other/path/file.md")
        brand = extract_brand_from_path(path)
        assert brand is None
