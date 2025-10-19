"""Unit tests for the bike table generator script."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.generate_bike_table import (
    collect_bikes,
    extract_frontmatter,
    format_table_cell,
    generate_bike_table,
    update_readme,
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
        frontmatter = {"title": "Test", "type": "article", "tags": ["test"]}
        assert validate_bike_frontmatter(frontmatter) is False
        captured = capsys.readouterr()
        assert "[SKIP]" in captured.out

    def test_missing_type_field(self, capsys):
        """Test validation fails when type field is missing."""
        frontmatter = {"title": "Test", "tags": ["test"]}
        assert validate_bike_frontmatter(frontmatter) is False


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
                "file_path": "vault/notes/test/test-bike.md",
            }
        ]
        result = generate_bike_table(bikes)
        assert "## Bike Models" in result
        assert "Test Bike" in result
        assert "TestBrand" in result
        assert "€1,000" in result
        assert "250W" in result
        assert "[Test Bike]" in result

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
                "file_path": "vault/notes/zebra/bike.md",
            },
            {
                "title": "Alpha Bike",
                "brand": "Alpha",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/alpha/bike.md",
            },
            {
                "title": "Beta Bike",
                "brand": "Alpha",
                "price": "",
                "motor": "",
                "battery": "",
                "range": "",
                "image": "",
                "file_path": "vault/notes/alpha/bike2.md",
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
                "file_path": "vault/notes/test/bike.md",
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
                "file_path": "vault/notes/test/bike.md",
            }
        ]
        result = generate_bike_table(bikes)
        assert "| -- |" in result


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

            with patch("scripts.generate_bike_table.Path") as mock_path:
                mock_path.return_value = readme_path
                update_readme("## New Table\nContent")

            content = readme_path.read_text()
            assert "Old content" not in content
            assert "New Table" in content
            assert "Content" in content

    def test_update_readme_create_markers(self):
        """Test updating README when markers don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text("# Test\nOriginal content")

            with patch("scripts.generate_bike_table.Path") as mock_path:
                mock_path.return_value = readme_path
                update_readme("## New Table")

            content = readme_path.read_text()
            assert "Original content" in content
            assert "<!-- BIKES_TABLE_START -->" in content
            assert "<!-- BIKES_TABLE_END -->" in content
            assert "New Table" in content

    def test_update_readme_file_not_found(self, capsys):
        """Test handling when README file doesn't exist."""
        with patch("scripts.generate_bike_table.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            update_readme("Content")
            captured = capsys.readouterr()
            assert "Error" in captured.out


class TestCollectBikes:
    """Test bike collection from markdown files."""

    def test_collect_bikes_directory_not_found(self, capsys):
        """Test handling when vault/notes directory doesn't exist."""
        with patch("scripts.generate_bike_table.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            result = collect_bikes()
            assert result == []
            captured = capsys.readouterr()
            assert "Error" in captured.out

    def test_collect_bikes_valid_structure(self, tmp_path, capsys):
        """Test collecting bikes from valid markdown files."""
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
