"""
Tests for the Markdown structural linter.

Tests validate that the linter correctly identifies valid and invalid
markdown files based on frontmatter and bike-specific requirements.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.linters.validate_structure import (
    ValidationError,
    extract_frontmatter,
    validate_bike_note,
    validate_file,
    validate_vault,
)


class TestExtractFrontmatter:
    """Tests for frontmatter extraction."""

    def test_valid_frontmatter(self):
        """Test extraction of valid YAML frontmatter."""
        content = """---
title: Test Bike
type: bike
brand: TestBrand
---

# Content here
"""
        frontmatter, error = extract_frontmatter(content)
        assert error is None
        assert frontmatter is not None
        assert frontmatter["title"] == "Test Bike"
        assert frontmatter["type"] == "bike"
        assert frontmatter["brand"] == "TestBrand"

    def test_empty_frontmatter(self):
        """Test extraction of empty but valid frontmatter."""
        content = """---
---

# Content here
"""
        frontmatter, error = extract_frontmatter(content)
        assert error is None
        assert frontmatter == {}

    def test_missing_start_delimiter(self):
        """Test file without frontmatter start delimiter."""
        content = """title: Test
type: bike
---

# Content
"""
        frontmatter, error = extract_frontmatter(content)
        assert frontmatter is None
        assert "Missing frontmatter start delimiter" in error

    def test_missing_end_delimiter(self):
        """Test file without frontmatter end delimiter."""
        content = """---
title: Test
type: bike

# Content
"""
        frontmatter, error = extract_frontmatter(content)
        assert frontmatter is None
        assert "Missing frontmatter end delimiter" in error

    def test_invalid_yaml(self):
        """Test file with malformed YAML."""
        content = """---
title: Test
type: [bike
invalid: {broken yaml
---

# Content
"""
        frontmatter, error = extract_frontmatter(content)
        assert frontmatter is None
        assert "Invalid YAML syntax" in error

    def test_complex_frontmatter(self):
        """Test extraction of complex nested YAML."""
        content = """---
title: Complex Bike
type: bike
specs:
  motor:
    make: Bosch
    power_w: 250
  battery:
    capacity_wh: 500
tags: [bike, longtail]
---

# Content
"""
        frontmatter, error = extract_frontmatter(content)
        assert error is None
        assert frontmatter["specs"]["motor"]["make"] == "Bosch"
        assert frontmatter["specs"]["battery"]["capacity_wh"] == 500
        assert frontmatter["tags"] == ["bike", "longtail"]


class TestValidateBikeNote:
    """Tests for bike note validation."""

    def test_non_bike_note_passes(self):
        """Test that non-bike notes don't require the marker."""
        content = """---
title: Guide
type: guide
---

# Guide content
"""
        frontmatter = {"title": "Guide", "type": "guide"}
        error = validate_bike_note(content, frontmatter)
        assert error is None

    def test_bike_note_with_marker_passes(self):
        """Test that bike notes with the marker pass validation."""
        content = """---
title: Test Bike
type: bike
---

# Test Bike

## Specifications

<!-- BIKE_SPECS_TABLE_START -->
| Spec | Value |
| ---- | ----- |
<!-- BIKE_SPECS_TABLE_END -->
"""
        frontmatter = {"title": "Test Bike", "type": "bike"}
        error = validate_bike_note(content, frontmatter)
        assert error is None

    def test_bike_note_without_marker_fails(self):
        """Test that bike notes without the marker fail validation."""
        content = """---
title: Test Bike
type: bike
---

# Test Bike

No specs table here.
"""
        frontmatter = {"title": "Test Bike", "type": "bike"}
        error = validate_bike_note(content, frontmatter)
        assert error is not None
        assert "BIKE_SPECS_TABLE_START" in error


class TestValidateFile:
    """Tests for file validation."""

    def test_valid_bike_file(self, tmp_path):
        """Test validation of a valid bike markdown file."""
        bike_file = tmp_path / "bike.md"
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
---

# Test Bike

<!-- BIKE_SPECS_TABLE_START -->
| Spec | Value |
<!-- BIKE_SPECS_TABLE_END -->
""")
        error = validate_file(bike_file)
        assert error is None

    def test_valid_non_bike_file(self, tmp_path):
        """Test validation of a valid non-bike markdown file."""
        guide_file = tmp_path / "guide.md"
        guide_file.write_text("""---
title: Maintenance Guide
type: guide
---

# Maintenance Guide

Some guide content.
""")
        error = validate_file(guide_file)
        assert error is None

    def test_file_with_invalid_frontmatter(self, tmp_path):
        """Test validation of file with invalid frontmatter."""
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text("""---
title: [broken
---

# Content
""")
        error = validate_file(invalid_file)
        assert error is not None
        assert isinstance(error, ValidationError)
        assert "Invalid YAML syntax" in error.error_message

    def test_bike_file_missing_marker(self, tmp_path):
        """Test validation of bike file missing required marker."""
        bike_file = tmp_path / "bike.md"
        bike_file.write_text("""---
title: Test Bike
type: bike
---

# Test Bike

No marker here.
""")
        error = validate_file(bike_file)
        assert error is not None
        assert isinstance(error, ValidationError)
        assert "BIKE_SPECS_TABLE_START" in error.error_message

    def test_file_read_error(self, tmp_path):
        """Test handling of file read errors."""
        # Create a file that doesn't exist
        nonexistent_file = tmp_path / "nonexistent.md"
        error = validate_file(nonexistent_file)
        assert error is not None
        assert "Failed to read file" in error.error_message


class TestValidateVault:
    """Tests for vault validation."""

    def test_empty_vault(self, tmp_path):
        """Test validation of an empty vault."""
        errors = validate_vault(tmp_path)
        assert len(errors) == 0

    def test_vault_with_valid_files(self, tmp_path):
        """Test validation of vault with all valid files."""
        # Create valid bike file
        bikes_dir = tmp_path / "bikes"
        bikes_dir.mkdir()
        bike_file = bikes_dir / "bike1.md"
        bike_file.write_text("""---
title: Bike 1
type: bike
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")

        # Create valid guide file
        guides_dir = tmp_path / "guides"
        guides_dir.mkdir()
        guide_file = guides_dir / "guide1.md"
        guide_file.write_text("""---
title: Guide 1
type: guide
---

# Guide content
""")

        errors = validate_vault(tmp_path)
        assert len(errors) == 0

    def test_vault_with_mixed_files(self, tmp_path):
        """Test validation of vault with valid and invalid files."""
        # Create valid file
        valid_file = tmp_path / "valid.md"
        valid_file.write_text("""---
title: Valid
type: guide
---

# Content
""")

        # Create invalid file (no frontmatter)
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text("""# No frontmatter here
""")

        # Create bike file missing marker
        bike_file = tmp_path / "bike.md"
        bike_file.write_text("""---
title: Bike
type: bike
---

# No marker
""")

        errors = validate_vault(tmp_path)
        assert len(errors) == 2
        error_messages = [e.error_message for e in errors]
        assert any(
            "Missing frontmatter start delimiter" in msg for msg in error_messages
        )
        assert any("BIKE_SPECS_TABLE_START" in msg for msg in error_messages)

    def test_vault_with_nested_structure(self, tmp_path):
        """Test validation of vault with nested directory structure."""
        # Create nested structure
        brand_dir = tmp_path / "bikes" / "trek"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "fetch.md"
        bike_file.write_text("""---
title: Trek Fetch
type: bike
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")

        errors = validate_vault(tmp_path)
        assert len(errors) == 0


class TestValidationError:
    """Tests for ValidationError class."""

    def test_validation_error_str(self, tmp_path):
        """Test string representation of ValidationError."""
        file_path = tmp_path / "test.md"
        error = ValidationError(file_path, "Test error message")
        error_str = str(error)
        assert str(file_path) in error_str
        assert "Test error message" in error_str
