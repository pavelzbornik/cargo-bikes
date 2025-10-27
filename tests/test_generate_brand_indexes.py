"""Tests for generate_brand_indexes script."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_brand_indexes import (
    collect_bikes_by_brand,
    extract_frontmatter,
    generate_brand_index,
)


class TestExtractFrontmatter:
    """Tests for extract_frontmatter function."""

    def test_extract_valid_frontmatter(self) -> None:
        """Test extracting valid YAML frontmatter."""
        content = """---
title: Test Bike
type: bike
brand: TestBrand
model: Model X
---

# Content here"""
        result = extract_frontmatter(content)
        assert result is not None
        assert result["title"] == "Test Bike"
        assert result["type"] == "bike"
        assert result["brand"] == "TestBrand"
        assert result["model"] == "Model X"

    def test_extract_frontmatter_with_specs(self) -> None:
        """Test extracting frontmatter with nested specs."""
        content = """---
title: Test Bike
type: bike
specs:
  category: longtail
  motor:
    make: Bosch
    power_w: 250
---

# Content"""
        result = extract_frontmatter(content)
        assert result is not None
        assert result["specs"]["category"] == "longtail"
        assert result["specs"]["motor"]["make"] == "Bosch"
        assert result["specs"]["motor"]["power_w"] == 250

    def test_extract_no_frontmatter(self) -> None:
        """Test with content that has no frontmatter."""
        content = "# No frontmatter\nSome content"
        result = extract_frontmatter(content)
        assert result is None

    def test_extract_invalid_yaml(self) -> None:
        """Test with invalid YAML."""
        content = """---
title: Test
invalid: [unclosed
---

# Content"""
        result = extract_frontmatter(content)
        assert result is None

    def test_extract_empty_frontmatter(self) -> None:
        """Test with empty frontmatter."""
        content = """---
---

# Content"""
        result = extract_frontmatter(content)
        # Empty YAML returns None from safe_load
        assert result is None or result == {}

    def test_extract_frontmatter_with_multiline_strings(self) -> None:
        """Test frontmatter with multiline strings."""
        content = """---
title: Test Bike
description: |
  This is a
  multiline description
type: bike
---

# Content"""
        result = extract_frontmatter(content)
        assert result is not None
        assert "multiline" in result["description"]


class TestGenerateBrandIndex:
    """Tests for generate_brand_index function."""

    def test_generate_brand_index_single_bike(self) -> None:
        """Test generating index with single bike."""
        bikes = [
            {
                "title": "Trek Fetch+",
                "filename": "trek-fetch-plus",
                "brand": "Trek",
                "model": "Fetch+",
                "category": "longtail",
            }
        ]
        result = generate_brand_index("trek", bikes)

        assert "Trek" in result
        assert "---" in result
        assert 'type: "brand-index"' in result
        assert "[Trek Fetch+]" in result
        assert "trek-fetch-plus.md" in result
        assert "brand-index" in result

    def test_generate_brand_index_multiple_bikes(self) -> None:
        """Test generating index with multiple bikes."""
        bikes = [
            {
                "title": "Trek Fetch+",
                "filename": "trek-fetch-plus",
                "brand": "Trek",
                "model": "Fetch+",
                "category": "longtail",
            },
            {
                "title": "Trek Fetch+ 2",
                "filename": "trek-fetch-plus-2",
                "brand": "Trek",
                "model": "Fetch+ 2",
                "category": "longtail",
            },
        ]
        result = generate_brand_index("trek", bikes)

        assert "2 model(s)" in result or "2 Trek model(s)" in result
        assert "[Trek Fetch+]" in result
        assert "[Trek Fetch+ 2]" in result
        assert "trek-fetch-plus.md" in result
        assert "trek-fetch-plus-2.md" in result

    def test_generate_brand_index_empty_bikes(self) -> None:
        """Test generating index with empty bikes list."""
        result = generate_brand_index("trek", [])
        assert result == ""

    def test_generate_brand_index_preserves_filenames(self) -> None:
        """Test that generated index uses correct filenames."""
        bikes = [
            {
                "title": "Custom Bike Name",
                "filename": "custom-slug",
                "brand": "TestBrand",
                "model": "Model",
                "category": "box",
            }
        ]
        result = generate_brand_index("testbrand", bikes)

        # Check that the filename slug is used, not the title
        assert "custom-slug.md" in result
        assert "[Custom Bike Name]" in result

    def test_generate_brand_index_frontmatter_format(self) -> None:
        """Test that frontmatter is properly formatted."""
        bikes = [
            {
                "title": "Trek Fetch+",
                "filename": "trek-fetch-plus",
                "brand": "Trek",
                "model": "Fetch+",
                "category": "longtail",
            }
        ]
        result = generate_brand_index("trek", bikes)

        # Check frontmatter structure
        assert result.startswith("---\n")
        assert 'title: "Trek"' in result
        assert 'type: "brand-index"' in result
        assert 'brand: "Trek"' in result
        assert "tags: [brand, index, trek]" in result
        assert "---\n" in result

    def test_generate_brand_index_includes_summary(self) -> None:
        """Test that index includes summary sections."""
        bikes = [
            {
                "title": "Trek Fetch+",
                "filename": "trek-fetch-plus",
                "brand": "Trek",
                "model": "Fetch+",
                "category": "longtail",
            }
        ]
        result = generate_brand_index("trek", bikes)

        assert "## Overview" in result
        assert "## Models in Vault" in result
        assert "## Regional Availability" in result
        assert "## Brand Philosophy & Positioning" in result

    def test_generate_brand_index_categories_preserved(self) -> None:
        """Test that bike categories are collected in output."""
        bikes = [
            {
                "title": "Trek Fetch+",
                "filename": "trek-fetch-plus",
                "brand": "Trek",
                "model": "Fetch+",
                "category": "longtail",
            },
            {
                "title": "Another Trek",
                "filename": "another-trek",
                "brand": "Trek",
                "model": "Model",
                "category": "box",
            },
        ]
        result = generate_brand_index("trek", bikes)

        assert "2 model(s)" in result or "2 Trek model(s)" in result


class TestCollectBikesByBrand:
    """Tests for collect_bikes_by_brand function."""

    def test_collect_empty_vault(self) -> None:
        """Test collecting from empty vault."""
        with TemporaryDirectory() as tmpdir:
            # Create empty vault structure
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes"
            bikes_dir.mkdir(parents=True)

            # Change to temp directory to test
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()
                assert len(result) == 0
            finally:
                os.chdir(original_cwd)

    def test_collect_single_brand_single_bike(self) -> None:
        """Test collecting with one brand and one bike."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            bike_file = bikes_dir / "fetch-plus.md"
            bike_file.write_text("""---
title: Trek Fetch+
type: bike
brand: Trek
model: Fetch+
specs:
  category: longtail
---

# Content""")

            # Change to temp directory to test
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert "trek" in result
                assert len(result["trek"]) == 1
                assert result["trek"][0]["title"] == "Trek Fetch+"
                assert result["trek"][0]["filename"] == "fetch-plus"
            finally:
                os.chdir(original_cwd)

    def test_collect_multiple_brands(self) -> None:
        """Test collecting from multiple brands."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_root = vault_path / "vault" / "notes" / "bikes"

            for brand_name in ["trek", "specialized", "riese-muller"]:
                bikes_dir = bikes_root / brand_name
                bikes_dir.mkdir(parents=True)

                bike_file = bikes_dir / "model1.md"
                bike_file.write_text(f"""---
title: {brand_name.title()} Model 1
type: bike
brand: {brand_name.title()}
---

# Content""")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert len(result) == 3
                assert "trek" in result
                assert "specialized" in result
                assert "riese-muller" in result
            finally:
                os.chdir(original_cwd)

    def test_collect_excludes_index_files(self) -> None:
        """Test that index.md files are excluded."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            # Create index file
            index_file = bikes_dir / "index.md"
            index_file.write_text("""---
title: Trek
type: brand-index
---

# Trek""")

            # Create bike file
            bike_file = bikes_dir / "fetch-plus.md"
            bike_file.write_text("""---
title: Trek Fetch+
type: bike
brand: Trek
---

# Content""")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert len(result["trek"]) == 1
                assert result["trek"][0]["title"] == "Trek Fetch+"
            finally:
                os.chdir(original_cwd)

    def test_collect_excludes_non_bike_types(self) -> None:
        """Test that non-bike types are excluded."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            # Create guide file (not a bike)
            guide_file = bikes_dir / "guide.md"
            guide_file.write_text("""---
title: Maintenance Guide
type: guide
---

# Guide""")

            # Create bike file
            bike_file = bikes_dir / "fetch-plus.md"
            bike_file.write_text("""---
title: Trek Fetch+
type: bike
brand: Trek
---

# Content""")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert len(result["trek"]) == 1
                # Guide should be excluded, only bike file should be included
                assert result["trek"][0]["title"] == "Trek Fetch+"
            finally:
                os.chdir(original_cwd)

    def test_collect_handles_missing_specs(self) -> None:
        """Test collecting bikes with missing specs."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            bike_file = bikes_dir / "model.md"
            bike_file.write_text("""---
title: Trek Model
type: bike
brand: Trek
---

# Content""")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert len(result["trek"]) == 1
                # Should default to 'longtail' category
                assert result["trek"][0]["category"] == "longtail"
            finally:
                os.chdir(original_cwd)

    def test_collect_multiple_bikes_per_brand(self) -> None:
        """Test collecting multiple bikes from single brand."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            for i in range(1, 4):
                bike_file = bikes_dir / f"model{i}.md"
                bike_file.write_text(f"""---
title: Trek Model {i}
type: bike
brand: Trek
model: Model {i}
---

# Content""")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert len(result["trek"]) == 3
                titles = [bike["title"] for bike in result["trek"]]
                assert "Trek Model 1" in titles
                assert "Trek Model 2" in titles
                assert "Trek Model 3" in titles
            finally:
                os.chdir(original_cwd)

    def test_collect_with_complex_specs(self) -> None:
        """Test collecting bikes with complex nested specs."""
        with TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)
            bikes_dir = vault_path / "vault" / "notes" / "bikes" / "trek"
            bikes_dir.mkdir(parents=True)

            bike_file = bikes_dir / "fetch-plus.md"
            bike_file.write_text("""---
title: Trek Fetch+
type: bike
brand: Trek
specs:
  category: longtail
  motor:
    make: Bosch
    power_w: 250
  battery:
    capacity_wh: 500
---

# Content""")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = collect_bikes_by_brand()

                assert result["trek"][0]["category"] == "longtail"
            finally:
                os.chdir(original_cwd)
