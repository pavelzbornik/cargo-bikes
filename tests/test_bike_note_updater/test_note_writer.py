"""Tests for note writing functionality."""

import tempfile
from pathlib import Path

import pytest

from scripts.bike_note_updater.note_writer import NoteWriter


class TestNoteWriter:
    """Test NoteWriter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.writer = NoteWriter(validate=True)

    def test_write_note_creates_file(self):
        """Test that write_note creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "bike",
                "tags": ["bike", "test"],
                "date": "2024-01-15",
            }
            body = "# Test Bike\n\nThis is a test bike."

            result = self.writer.write_note(file_path, frontmatter, body)

            assert result.success
            assert file_path.exists()

            # Verify content
            content = file_path.read_text(encoding="utf-8")
            assert "---" in content
            assert "title: Test Bike" in content
            assert "# Test Bike" in content

    def test_write_note_creates_parent_directories(self):
        """Test that write_note creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "bikes" / "trek" / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "bike",
                "tags": ["bike"],
                "date": "2024-01-15",
            }
            body = "Test content"

            result = self.writer.write_note(file_path, frontmatter, body)

            assert result.success
            assert file_path.exists()
            assert file_path.parent.exists()

    def test_write_note_validation_failure(self):
        """Test that invalid frontmatter fails validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "component",  # Wrong type
                "tags": ["bike"],
                "date": "2024-01-15",
            }
            body = "Test content"

            result = self.writer.write_note(file_path, frontmatter, body)

            assert not result.success
            assert len(result.errors) > 0
            assert not file_path.exists()  # File should not be created

    def test_write_note_skip_validation(self):
        """Test writing without validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "component",  # Would fail validation
            }
            body = "Test content"

            result = self.writer.write_note(file_path, frontmatter, body, validate=False)

            assert result.success
            assert file_path.exists()

    def test_write_note_with_warnings(self):
        """Test that validation warnings are included in result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "bike",
                "tags": ["bike", "LONGTAIL"],  # Tag format warning
                "date": "2024-01-15",
            }
            body = "Test content"

            result = self.writer.write_note(file_path, frontmatter, body)

            # Should succeed but have warnings
            assert result.success
            assert len(result.warnings) > 0

    def test_format_frontmatter(self):
        """Test formatting frontmatter to YAML."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike", "test"],
        }

        yaml_str = self.writer.format_frontmatter(frontmatter)

        assert "title: Test Bike" in yaml_str
        assert "type: bike" in yaml_str
        assert "tags:" in yaml_str

    def test_read_note(self):
        """Test reading a note from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            content = """---
title: "Test Bike"
type: bike
tags: [bike, test]
date: 2024-01-15
---

# Test Bike

This is the body content."""
            file_path.write_text(content, encoding="utf-8")

            frontmatter, body = self.writer.read_note(file_path)

            assert frontmatter is not None
            assert frontmatter["title"] == "Test Bike"
            assert frontmatter["type"] == "bike"
            assert "# Test Bike" in body

    def test_read_note_nonexistent(self):
        """Test reading a non-existent note."""
        file_path = Path("/nonexistent/path/note.md")
        frontmatter, body = self.writer.read_note(file_path)

        assert frontmatter is None
        assert body == ""

    def test_write_note_with_nested_specs(self):
        """Test writing a note with nested specs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "bike",
                "tags": ["bike", "longtail"],
                "date": "2024-01-15",
                "specs": {
                    "category": "longtail",
                    "motor": {
                        "make": "Bosch",
                        "power_w": 250,
                    },
                    "battery": {
                        "capacity_wh": 500,
                    },
                },
            }
            body = "# Test Bike"

            result = self.writer.write_note(file_path, frontmatter, body)

            assert result.success
            assert file_path.exists()

            # Verify nested structure in YAML
            content = file_path.read_text(encoding="utf-8")
            assert "specs:" in content
            assert "motor:" in content
            assert "make: Bosch" in content

    def test_write_note_preserves_body(self):
        """Test that the body content is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test Bike",
                "type": "bike",
                "tags": ["bike"],
                "date": "2024-01-15",
            }
            body = """# Overview

This is the bike overview.

## Features

- Feature 1
- Feature 2

## References

- [Link 1](https://example.com)"""

            result = self.writer.write_note(file_path, frontmatter, body)

            assert result.success

            content = file_path.read_text(encoding="utf-8")
            assert "# Overview" in content
            assert "## Features" in content
            assert "## References" in content
            assert "Feature 1" in content


class TestNoteWriterNoValidation:
    """Test NoteWriter without validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.writer = NoteWriter(validate=False)

    def test_write_invalid_frontmatter_no_validation(self):
        """Test writing invalid frontmatter without validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test",
                # Missing required fields
            }
            body = "Content"

            result = self.writer.write_note(file_path, frontmatter, body)

            # Should succeed because validation is disabled
            assert result.success
            assert file_path.exists()

    def test_override_validation_setting(self):
        """Test overriding validation setting per call."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-bike.md"
            frontmatter = {
                "title": "Test",
                "type": "wrong",  # Invalid - wrong type value
                "tags": ["bike"],
                "date": "2024-01-15",
            }
            body = "Content"

            # Override to enable validation
            result = self.writer.write_note(file_path, frontmatter, body, validate=True)

            # Should fail validation because type is wrong
            assert not result.success
