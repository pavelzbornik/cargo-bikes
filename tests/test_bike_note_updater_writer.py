"""Tests for bike_note_updater note writer."""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bike_note_updater.note_writer import (
    _generate_specs_table,
    _update_specs_table_block,
    format_frontmatter,
    parse_note,
    write_note,
)


class TestFormatFrontmatter:
    """Tests for YAML frontmatter formatting."""

    def test_simple_frontmatter(self) -> None:
        fm = {"title": "Test Bike", "type": "bike", "brand": "Trek"}
        yaml_str = format_frontmatter(fm)
        assert "title:" in yaml_str
        assert "type:" in yaml_str
        assert "brand:" in yaml_str

    def test_nested_specs(self) -> None:
        fm = {
            "title": "Test Bike",
            "type": "bike",
            "specs": {
                "category": "longtail",
                "motor": {"make": "Bosch", "model": "CX"},
            },
        }
        yaml_str = format_frontmatter(fm)
        assert "specs:" in yaml_str
        assert "motor:" in yaml_str
        assert "make:" in yaml_str

    def test_none_values_excluded(self) -> None:
        fm = {"title": "Test", "type": "bike", "brand": None, "model": "X"}
        yaml_str = format_frontmatter(fm)
        assert "brand" not in yaml_str
        assert "model:" in yaml_str

    def test_list_formatting(self) -> None:
        fm = {"title": "Test", "tags": ["bike", "electric", "longtail"]}
        yaml_str = format_frontmatter(fm)
        assert "tags:" in yaml_str
        assert "- bike" in yaml_str

    def test_special_characters_quoted(self) -> None:
        fm = {"title": "Trek Fetch+ 2", "url": "https://trek.com/fetch#details"}
        yaml_str = format_frontmatter(fm)
        # URLs with # should be quoted
        assert "https://trek.com/fetch#details" in yaml_str


class TestParseNote:
    """Tests for note parsing."""

    def test_parse_valid_note(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\ntitle: Test\ntype: bike\n---\n\n# Body content\n")
            f.flush()
            fm, body = parse_note(Path(f.name))
        assert fm is not None
        assert fm["title"] == "Test"
        assert "# Body content" in body

    def test_parse_no_frontmatter(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Just content\n\nNo frontmatter here.\n")
            f.flush()
            fm, body = parse_note(Path(f.name))
        assert fm is None
        assert "Just content" in body

    def test_parse_preserves_body(self) -> None:
        body_content = "\n## Section 1\n\nParagraph.\n\n## Section 2\n\nMore text.\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(f"---\ntitle: Test\n---\n{body_content}")
            f.flush()
            _fm, body = parse_note(Path(f.name))
        assert "Section 1" in body
        assert "Section 2" in body


class TestGenerateSpecsTable:
    """Tests for spec table generation."""

    def test_full_specs_table(self) -> None:
        fm = {
            "specs": {
                "category": "longtail",
                "motor": {"make": "Bosch", "model": "CX", "power_w": 250},
                "battery": {"capacity_wh": 500},
                "price": {"amount": 5999, "currency": "USD"},
                "weight": {"with_battery_kg": 31},
            }
        }
        table = _generate_specs_table(fm)
        assert "| Specification | Value |" in table
        assert "Bosch" in table
        assert "500 Wh" in table
        assert "$5999" in table
        assert "31 kg" in table

    def test_empty_specs_table(self) -> None:
        fm = {"specs": {}}
        table = _generate_specs_table(fm)
        assert table == ""

    def test_no_specs_key(self) -> None:
        fm = {"title": "Bike"}
        table = _generate_specs_table(fm)
        assert table == ""

    def test_partial_specs(self) -> None:
        fm = {"specs": {"motor": {"make": "Shimano"}}}
        table = _generate_specs_table(fm)
        assert "Shimano" in table
        assert "| --- | --- |" in table


class TestUpdateSpecsTableBlock:
    """Tests for spec table block replacement."""

    def test_replace_empty_block(self) -> None:
        body = "# Title\n\n<!-- BIKE_SPECS_TABLE_START -->\n<!-- BIKE_SPECS_TABLE_END -->\n\n## Next"
        table = "| Spec | Value |\n| --- | --- |\n| **Motor** | Bosch |"
        result = _update_specs_table_block(body, table)
        assert "| **Motor** | Bosch |" in result
        assert "## Next" in result

    def test_replace_existing_content(self) -> None:
        body = (
            "# Title\n\n<!-- BIKE_SPECS_TABLE_START -->\n"
            "old table content\n"
            "<!-- BIKE_SPECS_TABLE_END -->\n\n## Next"
        )
        table = "| New | Content |"
        result = _update_specs_table_block(body, table)
        assert "| New | Content |" in result
        assert "old table content" not in result

    def test_no_markers_unchanged(self) -> None:
        body = "# Title\n\nNo markers here.\n"
        result = _update_specs_table_block(body, "some table")
        assert result == body


class TestWriteNote:
    """Tests for note writing."""

    def test_write_note_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-bike.md"
            fm = {"title": "Test Bike", "type": "bike"}
            result = write_note(path, fm, body="\n## Content\n")
            assert result["success"]
            assert path.exists()
            content = path.read_text()
            assert content.startswith("---\n")
            assert "title:" in content
            assert "## Content" in content

    def test_write_note_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-bike.md"
            fm = {"title": "Test Bike", "type": "bike"}
            result = write_note(path, fm, body="\n## Content\n", dry_run=True)
            assert result["success"]
            assert not path.exists()  # File not created in dry run

    def test_write_preserves_existing_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test-bike.md"
            # Write initial content
            path.write_text(
                "---\ntitle: Old Title\ntype: bike\n---\n\n"
                "## Existing Content\n\nPreserve this.\n"
            )
            # Update with new frontmatter but no body
            fm = {"title": "New Title", "type": "bike"}
            result = write_note(path, fm)
            assert result["success"]
            content = path.read_text()
            assert "New Title" in content
            assert "Preserve this." in content
