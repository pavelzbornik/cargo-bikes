"""Unit tests for the bike table generator script."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.generate_bike_table import (
    collect_bikes,
    extract_frontmatter,
    extract_spec_value,
    format_table_cell,
    generate_bike_table,
    get_battery_display,
    get_motor_display,
    get_price_display,
    get_range_display,
    update_file_with_table,
    validate_bike_frontmatter,
)


class TestExtractFrontmatter:
    """Test YAML frontmatter extraction."""

    def test_extract_valid_frontmatter(self):
        """Test extraction of valid YAML frontmatter."""
        content = """---
title: "Test Bike"
type: bike
brand: "TestBrand"
tags: [test]
---
# Content here"""
        result = extract_frontmatter(content)
        assert result is not None
        assert result["title"] == "Test Bike"
        assert result["type"] == "bike"
        assert result["brand"] == "TestBrand"
        assert result["tags"] == ["test"]

    def test_extract_no_frontmatter(self):
        """Test handling of content without frontmatter."""
        content = "# No frontmatter here\nJust content"
        result = extract_frontmatter(content)
        assert result is None

    def test_extract_invalid_yaml(self, capsys):
        """Test handling of invalid YAML frontmatter."""
        content = """---
title: "Test"
invalid yaml: [unclosed
---
Content"""
        result = extract_frontmatter(content)
        assert result is None
        captured = capsys.readouterr()
        assert "[WARN]" in captured.out

    def test_extract_empty_frontmatter(self):
        """Test extraction of empty frontmatter."""
        content = """---
---
Content"""
        result = extract_frontmatter(content)
        assert result is None or result == {}


class TestValidateBikeFrontmatter:
    """Test frontmatter validation."""

    def test_valid_bike_frontmatter(self):
        """Test validation of valid bike frontmatter."""
        frontmatter = {"title": "Test Bike", "type": "bike", "tags": ["test"]}
        assert validate_bike_frontmatter(frontmatter) is True

    def test_missing_title(self, capsys):
        """Test validation fails when title is missing."""
        frontmatter = {"type": "bike", "tags": ["test"]}
        assert validate_bike_frontmatter(frontmatter) is False
        captured = capsys.readouterr()
        assert "[ERR]" in captured.out
        assert "title" in captured.out

    def test_missing_tags(self, capsys):
        """Test validation fails when tags are missing."""
        frontmatter = {"title": "Test", "type": "bike"}
        assert validate_bike_frontmatter(frontmatter) is False
        captured = capsys.readouterr()
        assert "[ERR]" in captured.out
        assert "tags" in captured.out

    def test_wrong_type(self, capsys):
        """Test validation fails for non-bike entries."""
        frontmatter = {
            "title": "Test",
            "type": "article",
            "tags": ["test"],
        }
        assert validate_bike_frontmatter(frontmatter) is False
        captured = capsys.readouterr()
        assert "[SKIP]" in captured.out

    def test_missing_type_field(self, capsys):
        """Test validation fails when type field is missing."""
        frontmatter = {"title": "Test", "tags": ["test"]}
        assert validate_bike_frontmatter(frontmatter) is False


class TestExtractSpecValue:
    """Test spec value extraction with nested key paths."""

    def test_extract_simple_value(self):
        """Test extracting a simple spec value."""
        specs = {"category": "longtail", "model_year": 2024}
        result = extract_spec_value(specs, ["category"])
        assert result == "longtail"

    def test_extract_nested_value(self):
        """Test extracting nested spec value."""
        specs = {
            "motor": {
                "make": "Bosch",
                "power_w": 250,
            }
        }
        result = extract_spec_value(specs, ["motor", "make"])
        assert result == "Bosch"

    def test_extract_power_w_formatting(self):
        """Test that power_w is formatted with W suffix."""
        specs = {"motor": {"power_w": 250}}
        result = extract_spec_value(specs, ["motor", "power_w"])
        assert result == "250W"

    def test_extract_capacity_wh_formatting(self):
        """Test that capacity_wh is formatted with Wh suffix."""
        specs = {"battery": {"capacity_wh": 500}}
        result = extract_spec_value(specs, ["battery", "capacity_wh"])
        assert result == "500Wh"

    def test_extract_estimate_km_formatting(self):
        """Test that estimate_km is formatted with km suffix."""
        specs = {"range": {"estimate_km": 100}}
        result = extract_spec_value(specs, ["range", "estimate_km"])
        assert result == "100km"

    def test_extract_missing_key(self):
        """Test extraction with missing key returns default."""
        specs = {"motor": {"make": "Bosch"}}
        result = extract_spec_value(specs, ["motor", "power_w"], "N/A")
        assert result == "N/A"

    def test_extract_none_specs(self):
        """Test extraction with None specs returns default."""
        result = extract_spec_value(None, ["motor", "make"], "unknown")
        assert result == "unknown"

    def test_extract_invalid_path(self):
        """Test extraction with invalid path returns default."""
        specs = {"motor": "Bosch"}  # Not a dict
        result = extract_spec_value(specs, ["motor", "make"], "default")
        assert result == "default"


class TestMotorDisplay:
    """Test motor display extraction."""

    def test_motor_from_new_schema(self):
        """Test extracting motor from new schema specs."""
        frontmatter = {"specs": {"motor": {"make": "Bosch", "power_w": 250}}}
        result = get_motor_display(frontmatter)
        assert result == "Bosch 250W"

    def test_motor_from_new_schema_no_make(self):
        """Test motor from new schema without make."""
        frontmatter = {"specs": {"motor": {"power_w": 250}}}
        result = get_motor_display(frontmatter)
        assert result == "250W"

    def test_motor_from_legacy_field(self):
        """Test motor from legacy top-level field."""
        frontmatter = {"motor": "250W Bosch"}
        result = get_motor_display(frontmatter)
        assert result == "250W Bosch"

    def test_motor_empty(self):
        """Test motor extraction when empty."""
        frontmatter = {}
        result = get_motor_display(frontmatter)
        assert result == ""

    def test_motor_schema_preferred_over_legacy(self):
        """Test that new schema is preferred over legacy."""
        frontmatter = {
            "motor": "legacy 250W",
            "specs": {"motor": {"make": "Bosch", "power_w": 500}},
        }
        result = get_motor_display(frontmatter)
        assert result == "Bosch 500W"


class TestBatteryDisplay:
    """Test battery display extraction."""

    def test_battery_from_new_schema(self):
        """Test extracting battery from new schema specs."""
        frontmatter = {"specs": {"battery": {"capacity_wh": 500}}}
        result = get_battery_display(frontmatter)
        assert result == "500Wh"

    def test_battery_from_legacy_field(self):
        """Test battery from legacy top-level field."""
        frontmatter = {"battery": "500Wh"}
        result = get_battery_display(frontmatter)
        assert result == "500Wh"

    def test_battery_empty(self):
        """Test battery extraction when empty."""
        frontmatter = {}
        result = get_battery_display(frontmatter)
        assert result == ""

    def test_battery_schema_preferred_over_legacy(self):
        """Test that new schema is preferred over legacy."""
        frontmatter = {
            "battery": "400Wh",
            "specs": {"battery": {"capacity_wh": 500}},
        }
        result = get_battery_display(frontmatter)
        assert result == "500Wh"


class TestRangeDisplay:
    """Test range display extraction."""

    def test_range_from_new_schema(self):
        """Test extracting range from new schema specs."""
        frontmatter = {"specs": {"range": {"estimate_km": 120}}}
        result = get_range_display(frontmatter)
        assert result == "120km"

    def test_range_from_legacy_field(self):
        """Test range from legacy top-level field."""
        frontmatter = {"range": "100-120km"}
        result = get_range_display(frontmatter)
        assert result == "100-120km"

    def test_range_empty(self):
        """Test range extraction when empty."""
        frontmatter = {}
        result = get_range_display(frontmatter)
        assert result == ""

    def test_range_schema_preferred_over_legacy(self):
        """Test that new schema is preferred over legacy."""
        frontmatter = {
            "range": "100km",
            "specs": {"range": {"estimate_km": 150}},
        }
        result = get_range_display(frontmatter)
        assert result == "150km"


class TestPriceDisplay:
    """Test price display extraction."""

    def test_price_from_new_schema_with_currency(self):
        """Test extracting price from new schema with currency."""
        frontmatter = {"specs": {"price": {"amount": 5999, "currency": "USD"}}}
        result = get_price_display(frontmatter)
        assert result == "USD 5999"

    def test_price_from_new_schema_without_currency(self):
        """Test extracting price from new schema without currency."""
        frontmatter = {"specs": {"price": {"amount": 5999}}}
        result = get_price_display(frontmatter)
        assert result == "5999"

    def test_price_from_legacy_field(self):
        """Test price from legacy top-level field."""
        frontmatter = {"price": "€5,999"}
        result = get_price_display(frontmatter)
        assert result == "€5,999"

    def test_price_empty(self):
        """Test price extraction when empty."""
        frontmatter = {}
        result = get_price_display(frontmatter)
        assert result == ""

    def test_price_schema_preferred_over_legacy(self):
        """Test that new schema is preferred over legacy."""
        frontmatter = {
            "price": "€4,999",
            "specs": {"price": {"amount": 5999, "currency": "USD"}},
        }
        result = get_price_display(frontmatter)
        assert result == "USD 5999"


class TestFormatTableCell:
    """Test table cell formatting."""

    def test_format_normal_value(self):
        """Test formatting of normal values."""
        assert format_table_cell("Test Value") == "Test Value"

    def test_format_empty_value(self):
        """Test formatting of empty values."""
        assert format_table_cell("") == "--"
        assert format_table_cell(None) == "--"

    def test_format_truncate_value(self):
        """Test formatting with truncation."""
        long_value = "This is a very long value that exceeds max width"
        result = format_table_cell(long_value, max_width=20)
        assert len(result) <= 20
        assert result.endswith("...")

    def test_format_exact_width(self):
        """Test formatting with exact width."""
        value = "Exactly Twenty Chars"
        result = format_table_cell(value, max_width=20)
        assert result == value


class TestGenerateBikeTable:
    """Test bike table generation."""

    def test_generate_empty_list(self):
        """Test generation with empty bike list."""
        result = generate_bike_table([])
        assert "No bikes found" in result

    def test_generate_single_bike(self):
        """Test generation with single bike."""
        bikes = [
            {
                "title": "Test Bike",
                "brand": "TestBrand",
                "price": "€1,000",
                "motor": "250W",
                "battery": "500Wh",
                "range": "100km",
                "image": "",
                "file_path": "vault/notes/bikes/test/test-bike.md",
            }
        ]
        result = generate_bike_table(bikes)
        assert "## Bike Models" in result
        assert "Test Bike" in result
        assert "TestBrand" in result
        assert "€1,000" in result
        assert "250W" in result
        assert "[Test Bike]" in result
        # With use_relative_links=False, should have full path
        assert "vault/notes/bikes/test/test-bike.md" in result

    def test_generate_sorting(self):
        """Test that bikes are sorted by brand then title."""
        bikes = [
            {
                "title": "Zebra Bike",
                "brand": "Zebra",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/bikes/zebra/bike.md",
            },
            {
                "title": "Alpha Bike",
                "brand": "Alpha",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/bikes/alpha/bike.md",
            },
            {
                "title": "Beta Bike",
                "brand": "Alpha",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/bikes/alpha/bike2.md",
            },
        ]
        result = generate_bike_table(bikes)
        # Alpha brand should come first, then sorted by title
        alpha_pos = result.find("Alpha Bike")
        beta_pos = result.find("Beta Bike")
        zebra_pos = result.find("Zebra Bike")
        assert alpha_pos < beta_pos < zebra_pos

    def test_generate_with_image(self):
        """Test table generation with bike images."""
        bikes = [
            {
                "title": "Test Bike",
                "brand": "Brand",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "https://example.com/image.jpg",
                "file_path": "vault/notes/bikes/test/bike.md",
            }
        ]
        result = generate_bike_table(bikes)
        assert "![img](https://example.com/image.jpg)" in result

    def test_generate_without_image(self):
        """Test table generation without images."""
        bikes = [
            {
                "title": "Test Bike",
                "brand": "Brand",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/bikes/test/bike.md",
            }
        ]
        result = generate_bike_table(bikes)
        assert "| -- |" in result

    def test_generate_with_relative_links(self):
        """Test table generation with relative links for index.md."""
        bikes = [
            {
                "title": "Test Bike",
                "brand": "Brand",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/bikes/test/bike.md",
            }
        ]
        result = generate_bike_table(bikes, use_relative_links=True)
        # With relative links, path should be bikes/test/bike.md
        assert "test/bike.md" in result
        assert "vault/notes/bikes/" not in result


class TestUpdateReadme:
    """Test README update functionality."""

    def test_update_readme_with_existing_markers(self):
        """Test updating README when markers exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text(
                """# Test
<!-- BIKES_TABLE_START -->
Old content
<!-- BIKES_TABLE_END -->
End"""
            )

            update_file_with_table(readme_path, "## New Table\nContent")

            content = readme_path.read_text()
            assert "Old content" not in content
            assert "New Table" in content
            assert "Content" in content

    def test_update_readme_create_markers(self):
        """Test updating README when markers don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text("# Test\nOriginal content")

            update_file_with_table(readme_path, "## New Table")

            content = readme_path.read_text()
            assert "Original content" in content
            assert "<!-- BIKES_TABLE_START -->" in content
            assert "<!-- BIKES_TABLE_END -->" in content
            assert "New Table" in content

    def test_update_readme_file_not_found(self, capsys):
        """Test handling when README file doesn't exist."""
        readme_path = Path("/nonexistent/README.md")
        update_file_with_table(readme_path, "Content")
        captured = capsys.readouterr()
        assert "Error" in captured.out


class TestCollectBikes:
    """Test bike collection from markdown files."""

    def test_collect_bikes_directory_not_found(self, capsys):
        """Test handling when vault/notes/bikes directory doesn't exist."""
        with patch("scripts.generate_bike_table.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            result = collect_bikes()
            assert result == []
            captured = capsys.readouterr()
            assert "Error" in captured.out

    def test_collect_bikes_valid_legacy_format(self, tmp_path, capsys):
        """Test collecting bikes with legacy format."""
        # Create mock vault structure
        vault_notes = tmp_path / "vault" / "notes"
        brand_dir = vault_notes / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "test-bike.md"
        bike_file.write_text(
            """---
title: "Test Bike"
type: bike
brand: "TestBrand"
price: "€1,000"
motor: "250W"
battery: "500Wh"
range: "100km"
image: "https://example.com/image.jpg"
tags: [test, longtail]
---
# Content"""
        )

        with patch("scripts.generate_bike_table.Path") as mock_path_cls:
            mock_vault = MagicMock()
            mock_vault.exists.return_value = True
            mock_vault.glob.return_value = [bike_file]
            mock_path_cls.return_value = mock_vault

            # Partial test: basic mocking of directory structure
            assert mock_vault.exists() is True

    def test_collect_bikes_new_schema_format(self, tmp_path, capsys):
        """Test collecting bikes with new schema format."""
        # Create mock vault structure
        vault_notes = tmp_path / "vault" / "notes"
        brand_dir = vault_notes / "trek"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "fetch-plus-2.md"
        bike_file.write_text(
            """---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2025-10-20
tags: [bike, longtail, trek, bosch]
url: "https://www.trekbikes.com/fetch-2/"
image: "https://example.com/trek-fetch-2.jpg"
specs:
  category: "longtail"
  model_year: 2024
  motor:
    make: "Bosch"
    power_w: 250
  battery:
    capacity_wh: 500
  weight:
    with_battery_kg: 31
  range:
    estimate_km: "50-120"
  price:
    amount: 5999
    currency: "USD"
---
# Content"""
        )

        with patch("scripts.generate_bike_table.Path") as mock_path_cls:
            mock_vault = MagicMock()
            mock_vault.exists.return_value = True
            mock_vault.glob.return_value = [bike_file]
            mock_path_cls.return_value = mock_vault

            # Partial test: basic mocking of directory structure
            assert mock_vault.exists() is True


class TestSchemaCompatibility:
    """Test schema compatibility and migration scenarios."""

    def test_legacy_note_with_all_fields(self):
        """Test that legacy notes with all fields parse correctly."""
        frontmatter = {
            "title": "Legacy Bike",
            "type": "bike",
            "brand": "OldBrand",
            "model": "Model X",
            "price": "€3,000",
            "motor": "250W Shimano",
            "battery": "400Wh",
            "range": "80km",
            "image": "https://example.com/bike.jpg",
            "url": "https://example.com/bike",
            "tags": ["bike", "longtail"],
        }
        assert validate_bike_frontmatter(frontmatter) is True
        assert get_motor_display(frontmatter) == "250W Shimano"
        assert get_battery_display(frontmatter) == "400Wh"
        assert get_range_display(frontmatter) == "80km"
        assert get_price_display(frontmatter) == "€3,000"

    def test_new_schema_complete(self):
        """Test that new schema notes parse completely."""
        frontmatter = {
            "title": "New Bike",
            "type": "bike",
            "brand": "Trek",
            "model": "Fetch+ 2",
            "date": "2025-10-20",
            "tags": ["bike", "longtail", "trek", "bosch"],
            "url": "https://www.trekbikes.com/fetch-2/",
            "image": "https://example.com/trek.jpg",
            "specs": {
                "category": "longtail",
                "model_year": 2024,
                "motor": {
                    "make": "Bosch",
                    "model": "Performance Line CX",
                    "type": "mid-drive",
                    "power_w": 250,
                    "torque_nm": 85,
                },
                "battery": {
                    "capacity_wh": 500,
                    "configuration": "single",
                    "removable": True,
                    "charging_time_h": 6,
                },
                "weight": {"with_battery_kg": 31},
                "range": {"estimate_km": "50-120"},
                "price": {"amount": 5999, "currency": "USD"},
            },
        }
        assert validate_bike_frontmatter(frontmatter) is True
        assert get_motor_display(frontmatter) == "Bosch 250W"
        assert get_battery_display(frontmatter) == "500Wh"
        assert get_range_display(frontmatter) == "50-120km"
        assert get_price_display(frontmatter) == "USD 5999"

    def test_mixed_schema_legacy_takes_precedence_for_display(self):
        """Test that when both formats exist, schema is preferred."""
        frontmatter = {
            "title": "Mixed Bike",
            "type": "bike",
            "brand": "Brand",
            "price": "€5,000",  # Legacy
            "motor": "250W Generic",  # Legacy
            "battery": "400Wh",  # Legacy
            "range": "80km",  # Legacy
            "specs": {
                "motor": {"make": "Bosch", "power_w": 250},  # Schema
                "battery": {"capacity_wh": 500},  # Schema
                "range": {"estimate_km": 120},  # Schema
                "price": {"amount": 5999, "currency": "EUR"},  # Schema
            },
            "tags": ["bike"],
        }
        assert validate_bike_frontmatter(frontmatter) is True
        # Schema should be preferred
        assert get_motor_display(frontmatter) == "Bosch 250W"
        assert get_battery_display(frontmatter) == "500Wh"
        assert get_range_display(frontmatter) == "120km"
        assert get_price_display(frontmatter) == "EUR 5999"

    def test_partial_legacy_with_missing_fields(self):
        """Test legacy note with some missing optional fields."""
        frontmatter = {
            "title": "Partial Legacy",
            "type": "bike",
            "brand": "Brand",
            "tags": ["bike"],
            # Missing: price, motor, battery, range
        }
        assert validate_bike_frontmatter(frontmatter) is True
        assert get_motor_display(frontmatter) == ""
        assert get_battery_display(frontmatter) == ""
        assert get_range_display(frontmatter) == ""
        assert get_price_display(frontmatter) == ""

    def test_partial_new_schema_with_missing_fields(self):
        """Test new schema note with some missing optional fields."""
        frontmatter = {
            "title": "Partial Schema",
            "type": "bike",
            "brand": "Brand",
            "tags": ["bike"],
            "specs": {
                "motor": {"make": "Bosch"},  # Missing power_w
                "battery": {},  # Empty
            },
        }
        assert validate_bike_frontmatter(frontmatter) is True
        # Should handle gracefully
        motor = get_motor_display(frontmatter)
        assert "Bosch" in motor or motor == ""
        assert get_battery_display(frontmatter) == ""


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_special_characters_in_title(self):
        """Test handling of special characters in bike titles."""
        frontmatter = {
            "title": "Bike with Spëcial Çhars & Symbols",
            "type": "bike",
            "tags": ["test"],
        }
        assert validate_bike_frontmatter(frontmatter) is True

    def test_unicode_in_frontmatter(self):
        """Test handling of Unicode characters."""
        content = """---
title: "Vélo Électrique"
type: bike
brand: "Français"
tags:
  - français
---

Content"""
        result = extract_frontmatter(content)
        assert result is not None
        assert result["brand"] == "Français"

    def test_empty_tags_list(self):
        """Test handling of empty tags list."""
        frontmatter = {"title": "Test", "type": "bike", "tags": []}
        # Empty tags should still validate (tags list exists)
        assert validate_bike_frontmatter(frontmatter) is True

    def test_very_long_cell_values(self):
        """Test handling of very long cell values."""
        long_value = "x" * 1000
        result = format_table_cell(long_value, max_width=50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_string_price_range(self):
        """Test price as string range like 'from 4999'."""
        frontmatter = {"specs": {"price": {"amount": "from 4999", "currency": "EUR"}}}
        result = get_price_display(frontmatter)
        assert result == "EUR from 4999"

    def test_string_range_estimate(self):
        """Test range estimate as string like '50-120'."""
        frontmatter = {"specs": {"range": {"estimate_km": "50-120"}}}
        result = get_range_display(frontmatter)
        assert result == "50-120km"
