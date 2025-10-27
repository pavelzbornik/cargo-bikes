"""Tests for add_bike_table_markers script."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.add_bike_table_markers import (
    add_markers,
    find_frontmatter_end,
    has_markers,
    process_bike_files,
)


class TestFindFrontmatterEnd:
    """Tests for find_frontmatter_end function."""

    def test_find_frontmatter_end_valid(self) -> None:
        """Test finding frontmatter end with valid content."""
        content = """---
title: Test
type: bike
---

# Content"""
        result = find_frontmatter_end(content)
        assert result > 0
        # Check that the position points to the start of content after frontmatter
        assert content[result:].startswith("\n# Content")

    def test_find_frontmatter_end_no_frontmatter(self) -> None:
        """Test with content that has no frontmatter."""
        content = "# No frontmatter\nSome content"
        result = find_frontmatter_end(content)
        assert result == -1

    def test_find_frontmatter_end_incomplete_frontmatter(self) -> None:
        """Test with incomplete frontmatter (no closing ---)."""
        content = """---
title: Test
type: bike
No closing marker"""
        result = find_frontmatter_end(content)
        assert result == -1

    def test_find_frontmatter_end_multiline_values(self) -> None:
        """Test with multiline YAML values."""
        content = """---
title: Test
summary: |
  This is a
  multiline value
type: bike
---

# Content"""
        result = find_frontmatter_end(content)
        assert result > 0
        assert content[result:].startswith("\n# Content")


class TestHasMarkers:
    """Tests for has_markers function."""

    def test_has_both_markers(self) -> None:
        """Test content with both markers."""
        content = """---
title: Test
---

<!-- BIKE_SPECS_TABLE_START -->
Some content
<!-- BIKE_SPECS_TABLE_END -->"""
        assert has_markers(content) is True

    def test_missing_start_marker(self) -> None:
        """Test content missing start marker."""
        content = """---
title: Test
---

Some content
<!-- BIKE_SPECS_TABLE_END -->"""
        assert has_markers(content) is False

    def test_missing_end_marker(self) -> None:
        """Test content missing end marker."""
        content = """---
title: Test
---

<!-- BIKE_SPECS_TABLE_START -->
Some content"""
        assert has_markers(content) is False

    def test_no_markers(self) -> None:
        """Test content with no markers."""
        content = """---
title: Test
---

Some content"""
        assert has_markers(content) is False


class TestAddMarkers:
    """Tests for add_markers function."""

    def test_add_markers_basic(self) -> None:
        """Test adding markers to content without them."""
        content = """---
title: Test Bike
type: bike
---

# Introduction

Some content here."""
        result = add_markers(content)

        assert has_markers(result) is True
        assert "<!-- BIKE_SPECS_TABLE_START -->" in result
        assert "<!-- BIKE_SPECS_TABLE_END -->" in result
        # Original content should be preserved
        assert "# Introduction" in result
        assert "Some content here." in result

    def test_add_markers_already_present(self) -> None:
        """Test that markers are not duplicated."""
        content = """---
title: Test Bike
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->"""
        result = add_markers(content)
        assert result == content

    def test_add_markers_with_tech_specs_section(self) -> None:
        """Test adding markers when Technical Specifications section exists."""
        content = """---
title: Test Bike
---

# Introduction

## Technical Specifications

Some specs here."""
        result = add_markers(content)

        assert has_markers(result) is True
        # Markers should be right after the Technical Specifications header
        assert (
            "## Technical Specifications\n\n<!-- BIKE_SPECS_TABLE_START -->" in result
        )

    def test_add_markers_no_frontmatter(self) -> None:
        """Test with content that has no frontmatter."""
        content = "# No frontmatter\nSome content"
        result = add_markers(content)
        # Should return unchanged content
        assert result == content

    def test_add_markers_creates_section(self) -> None:
        """Test that markers create a Technical Specifications section if missing."""
        content = """---
title: Test Bike
---

# Introduction

Some content"""
        result = add_markers(content)

        assert "## Technical Specifications" in result
        assert has_markers(result) is True


class TestProcessBikeFiles:
    """Tests for process_bike_files function."""

    def test_process_empty_vault(self) -> None:
        """Test processing an empty vault."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes"
            bikes_path.mkdir()

            stats = process_bike_files(vault_path)

            assert stats["total_files"] == 0
            assert stats["files_processed"] == 0
            assert stats["errors"] == 0

    def test_process_files_without_markers(self) -> None:
        """Test processing files that need markers added."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "test-brand"
            bikes_path.mkdir(parents=True)

            bike_file = bikes_path / "bike1.md"
            bike_file.write_text("""---
title: Test Bike
type: bike
---

# Content""")

            stats = process_bike_files(vault_path, dry_run=False)

            assert stats["total_files"] == 1
            assert stats["files_processed"] == 1
            assert stats["errors"] == 0

            # Verify markers were added
            updated_content = bike_file.read_text()
            assert has_markers(updated_content) is True

    def test_process_files_already_have_markers(self) -> None:
        """Test processing files that already have markers."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "test-brand"
            bikes_path.mkdir(parents=True)

            bike_file = bikes_path / "bike1.md"
            bike_file.write_text("""---
title: Test Bike
type: bike
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->

# Content""")

            stats = process_bike_files(vault_path, dry_run=False)

            assert stats["total_files"] == 1
            assert stats["files_with_markers"] == 1
            assert stats["files_processed"] == 0

    def test_process_excludes_index_files(self) -> None:
        """Test that index.md files are excluded."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "test-brand"
            bikes_path.mkdir(parents=True)

            # Create index.md
            index_file = bikes_path / "index.md"
            index_file.write_text("""---
title: Test Brand
type: brand-index
---

# Test Brand""")

            # Create regular bike file
            bike_file = bikes_path / "bike1.md"
            bike_file.write_text("""---
title: Test Bike
type: bike
---

# Content""")

            stats = process_bike_files(vault_path, dry_run=False)

            # Should only process bike1.md, not index.md
            assert stats["total_files"] == 1
            assert stats["files_processed"] == 1

    def test_process_dry_run(self) -> None:
        """Test dry run mode doesn't modify files."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "test-brand"
            bikes_path.mkdir(parents=True)

            bike_file = bikes_path / "bike1.md"
            original_content = """---
title: Test Bike
type: bike
---

# Content"""
            bike_file.write_text(original_content)

            stats = process_bike_files(vault_path, dry_run=True)

            assert stats["files_processed"] == 1

            # Verify file was not modified
            current_content = bike_file.read_text()
            assert current_content == original_content
            assert has_markers(current_content) is False

    def test_process_multiple_files(self) -> None:
        """Test processing multiple files."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes"

            # Create multiple brand directories with bike files
            for brand_num in range(1, 4):
                brand_dir = bikes_path / f"brand-{brand_num}"
                brand_dir.mkdir(parents=True)

                for bike_num in range(1, 3):
                    bike_file = brand_dir / f"bike{bike_num}.md"
                    bike_file.write_text(f"""---
title: Brand {brand_num} Bike {bike_num}
type: bike
---

# Content""")

            stats = process_bike_files(vault_path, dry_run=False)

            assert stats["total_files"] == 6  # 3 brands * 2 bikes
            assert stats["files_processed"] == 6
            assert stats["errors"] == 0

    def test_process_vault_path_not_found(self) -> None:
        """Test handling of nonexistent vault path."""
        vault_path = Path("/nonexistent/path")
        stats = process_bike_files(vault_path)

        assert stats["total_files"] == 0
        assert stats["errors"] == 0

    def test_process_handles_read_errors(self) -> None:
        """Test handling of files that can't be read."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "test-brand"
            bikes_path.mkdir(parents=True)

            bike_file = bikes_path / "bike1.md"
            bike_file.write_text("""---
title: Test Bike
type: bike
---

# Content""")

            # Remove read permission (if on Unix-like system)
            import os

            if hasattr(os, "chmod"):
                original_stat = bike_file.stat()
                try:
                    os.chmod(bike_file, 0o000)

                    stats = process_bike_files(vault_path, dry_run=False)

                    # Should have an error
                    assert stats["errors"] > 0
                finally:
                    # Restore permissions for cleanup
                    os.chmod(bike_file, original_stat.st_mode)

    def test_process_nested_brand_directories(self) -> None:
        """Test processing with various directory structures."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes"

            # Create nested structure
            nested_dir = bikes_path / "brand" / "sub" / "structure"
            nested_dir.mkdir(parents=True)

            bike_file = nested_dir / "bike.md"
            bike_file.write_text("""---
title: Test Bike
type: bike
---

# Content""")

            stats = process_bike_files(vault_path, dry_run=False)

            assert stats["total_files"] == 1
            assert stats["files_processed"] == 1


class TestMainFunction:
    """Tests for main CLI function."""

    def test_main_with_invalid_vault_path(self, monkeypatch) -> None:
        """Test main function with invalid vault path."""
        import sys

        from scripts.add_bike_table_markers import main

        # Mock sys.argv to pass invalid path
        monkeypatch.setattr(sys, "argv", ["script", "--vault-path", "/nonexistent"])

        # Should return 1 (error)
        result = main()
        assert result == 1

    def test_main_success(self, monkeypatch, capsys) -> None:
        """Test main function with valid vault."""
        import sys

        from scripts.add_bike_table_markers import main

        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "brand"
            bikes_path.mkdir(parents=True)

            bike_file = bikes_path / "bike.md"
            bike_file.write_text("""---
title: Test
type: bike
---

# Content""")

            monkeypatch.setattr(
                sys, "argv", ["script", "--vault-path", str(vault_path)]
            )
            result = main()

            # Should return 0 (success)
            assert result == 0

            captured = capsys.readouterr()
            assert "Processing" in captured.out or "Summary" in captured.out

    def test_main_dry_run(self, monkeypatch, capsys) -> None:
        """Test main function with dry-run mode."""
        import sys

        from scripts.add_bike_table_markers import main

        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_path = vault_path / "bikes" / "brand"
            bikes_path.mkdir(parents=True)

            bike_file = bikes_path / "bike.md"
            original_content = """---
title: Test
type: bike
---

# Content"""
            bike_file.write_text(original_content)

            monkeypatch.setattr(
                sys, "argv", ["script", "--vault-path", str(vault_path), "--dry-run"]
            )
            result = main()

            assert result == 0

            captured = capsys.readouterr()
            assert "DRY RUN" in captured.out

            # File should not be modified
            current_content = bike_file.read_text()
            assert current_content == original_content
