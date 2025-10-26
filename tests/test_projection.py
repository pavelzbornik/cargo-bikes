"""
Tests for the database projection script.

Tests verify that the projection script correctly updates Markdown files
from database records while preserving manual content outside managed sections.
"""

import sys
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database.project import (
    SPECS_TABLE_END_MARKER,
    SPECS_TABLE_START_MARKER,
    find_bike_file,
    generate_frontmatter,
    generate_specs_table,
    parse_markdown_file,
    project_bike_to_file,
    reconstruct_markdown_file,
)
from scripts.database.schema import Base, Bike, Brand, Reseller


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory for testing."""
    with TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        # Create bikes directory structure
        bikes_dir = vault_path / "bikes"
        bikes_dir.mkdir()
        yield vault_path


@pytest.fixture
def sample_bike(db_session):
    """Create a sample bike record for testing."""
    # Create brand
    brand = Brand(title="TestBrand", type="brand", date=date.today())
    db_session.add(brand)

    # Create bike with comprehensive specs
    bike = Bike(
        title="Test Bike Model X",
        type="bike",
        brand_name="TestBrand",
        model="Model X",
        tags="bike,longtail,testbrand,bosch",
        url="https://testbrand.com/model-x",
        image="https://testbrand.com/model-x.jpg",
        category="longtail",
        model_year=2024,
        # Motor
        motor_make="Bosch",
        motor_model="Performance CX",
        motor_type="mid-drive",
        motor_power_w=250.0,
        motor_torque_nm=85.0,
        motor_boost_throttle=False,
        # Battery
        battery_capacity_wh=500.0,
        battery_configuration="single",
        battery_removable=True,
        battery_charging_time_h="3-5",
        # Weight
        weight_bike_kg=28.0,
        weight_with_battery_kg=30.0,
        # Load capacity
        load_capacity_total_kg=200.0,
        load_capacity_rear_kg=80.0,
        load_capacity_passenger_count=2,
        # Drivetrain
        drivetrain_type="chain",
        drivetrain_speeds="10-speed",
        brakes_type="hydraulic disk",
        # Wheels
        wheels_front_size_in='24"',
        wheels_rear_size_in='20"',
        wheels_tire="Schwalbe Big Ben",
        # Range
        range_estimate_km="60-100",
        # Price
        price_amount="3999",
        price_currency="EUR",
    )
    bike.brand = brand
    db_session.add(bike)

    # Add resellers
    reseller1 = Reseller(
        bike=bike,
        name="Shop A",
        url="https://shopa.com/bike",
        price="3999",
        currency="EUR",
        region="EU",
        availability="in-stock",
    )
    reseller2 = Reseller(
        bike=bike,
        name="Shop B",
        url="https://shopb.com/bike",
        price="4200",
        currency="EUR",
        region="EU",
    )
    db_session.add(reseller1)
    db_session.add(reseller2)

    db_session.commit()
    return bike


class TestParseMarkdownFile:
    """Tests for markdown file parsing."""

    def test_parse_file_with_all_sections(self, temp_vault):
        """Test parsing a file with all sections."""
        md_file = temp_vault / "test.md"
        md_file.write_text(
            """---
title: Test
type: bike
---

## Introduction

This is some manual content before the table.

<!-- BIKE_SPECS_TABLE_START -->

| Spec | Value |
|------|-------|
| Old  | Data  |

<!-- BIKE_SPECS_TABLE_END -->

## Details

This is some manual content after the table.

### More Content

Multiple sections should be preserved.
"""
        )

        parts = parse_markdown_file(md_file)

        assert "title: Test" in parts["frontmatter"]
        assert "type: bike" in parts["frontmatter"]
        assert "## Introduction" in parts["before_table"]
        assert "manual content before the table" in parts["before_table"]
        assert "| Spec | Value |" in parts["table"]
        assert "## Details" in parts["after_table"]
        assert "### More Content" in parts["after_table"]
        assert "Multiple sections should be preserved" in parts["after_table"]

    def test_parse_file_without_markers(self, temp_vault):
        """Test parsing a file without specs table markers."""
        md_file = temp_vault / "test.md"
        md_file.write_text(
            """---
title: Test
type: bike
---

## Content

All content should be in before_table.
"""
        )

        parts = parse_markdown_file(md_file)

        assert "title: Test" in parts["frontmatter"]
        assert "## Content" in parts["before_table"]
        assert parts["table"] == ""
        assert parts["after_table"] == ""

    def test_parse_file_with_empty_table_block(self, temp_vault):
        """Test parsing a file with empty table block."""
        md_file = temp_vault / "test.md"
        md_file.write_text(
            """---
title: Test
---

Content before

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->

Content after
"""
        )

        parts = parse_markdown_file(md_file)

        assert "Content before" in parts["before_table"]
        assert parts["table"].strip() == ""
        assert "Content after" in parts["after_table"]


class TestGenerateFrontmatter:
    """Tests for frontmatter generation."""

    def test_generate_frontmatter_basic(self, sample_bike):
        """Test generating basic frontmatter."""
        frontmatter = generate_frontmatter(sample_bike)
        data = yaml.safe_load(frontmatter)

        assert data["title"] == "Test Bike Model X"
        assert data["type"] == "bike"
        assert data["brand"] == "TestBrand"
        assert data["model"] == "Model X"
        assert data["url"] == "https://testbrand.com/model-x"
        assert data["image"] == "https://testbrand.com/model-x.jpg"

    def test_generate_frontmatter_tags(self, sample_bike):
        """Test that tags are converted to list."""
        frontmatter = generate_frontmatter(sample_bike)
        data = yaml.safe_load(frontmatter)

        assert "tags" in data
        assert isinstance(data["tags"], list)
        assert "bike" in data["tags"]
        assert "longtail" in data["tags"]
        assert "testbrand" in data["tags"]
        assert "bosch" in data["tags"]

    def test_generate_frontmatter_specs(self, sample_bike):
        """Test that specs are correctly nested."""
        frontmatter = generate_frontmatter(sample_bike)
        data = yaml.safe_load(frontmatter)

        assert "specs" in data
        specs = data["specs"]

        # Check category and year
        assert specs["category"] == "longtail"
        assert specs["model_year"] == 2024

        # Check motor
        assert "motor" in specs
        assert specs["motor"]["make"] == "Bosch"
        assert specs["motor"]["model"] == "Performance CX"
        assert specs["motor"]["type"] == "mid-drive"
        assert specs["motor"]["power_w"] == 250
        assert specs["motor"]["torque_nm"] == 85
        assert specs["motor"]["boost_throttle"] is False

        # Check battery
        assert "battery" in specs
        assert specs["battery"]["capacity_wh"] == 500
        assert specs["battery"]["configuration"] == "single"
        assert specs["battery"]["removable"] is True
        assert specs["battery"]["charging_time_h"] == "3-5"

        # Check weight
        assert "weight" in specs
        assert specs["weight"]["bike_kg"] == 28.0
        assert specs["weight"]["with_battery_kg"] == 30.0

        # Check load capacity
        assert "load_capacity" in specs
        assert specs["load_capacity"]["total_kg"] == 200.0
        assert specs["load_capacity"]["rear_kg"] == 80.0
        assert specs["load_capacity"]["passenger_count_excluding_rider"] == 2

    def test_generate_frontmatter_resellers(self, sample_bike):
        """Test that resellers are included."""
        frontmatter = generate_frontmatter(sample_bike)
        data = yaml.safe_load(frontmatter)

        assert "resellers" in data
        assert len(data["resellers"]) == 2

        reseller1 = data["resellers"][0]
        assert reseller1["name"] == "Shop A"
        assert reseller1["url"] == "https://shopa.com/bike"
        assert reseller1["price"] == "3999"
        assert reseller1["currency"] == "EUR"
        assert reseller1["region"] == "EU"
        assert reseller1["availability"] == "in-stock"

    def test_generate_frontmatter_minimal_bike(self, db_session):
        """Test generating frontmatter for a bike with minimal data."""
        bike = Bike(title="Minimal Bike", type="bike")
        db_session.add(bike)
        db_session.commit()

        frontmatter = generate_frontmatter(bike)
        data = yaml.safe_load(frontmatter)

        assert data["title"] == "Minimal Bike"
        assert data["type"] == "bike"
        # Should not have specs if no specs data
        assert "specs" not in data or data["specs"] == {}


class TestGenerateSpecsTable:
    """Tests for specs table generation."""

    def test_generate_specs_table(self, sample_bike):
        """Test generating a specs table."""
        table = generate_specs_table(sample_bike)

        assert "| Specification | Value |" in table
        assert "|---------------|-------|" in table
        assert "| **Category** | longtail |" in table
        assert "| **Model Year** | 2024 |" in table
        assert "| **Motor** | Bosch Performance CX |" in table
        assert "| **Motor Power** | 250W |" in table
        assert "| **Motor Torque** | 85Nm |" in table
        assert "| **Battery Capacity** | 500Wh |" in table
        assert "| **Range** | 60-100 km |" in table
        assert "| **Weight (with battery)** | 30.0kg |" in table
        assert "| **Total Load Capacity** | 200.0kg |" in table
        assert "| **Drivetrain** | chain |" in table
        assert "| **Brakes** | hydraulic disk |" in table
        assert "| **Price** | 3999 EUR |" in table

    def test_generate_specs_table_wheel_sizes(self, sample_bike):
        """Test wheel size formatting in specs table."""
        table = generate_specs_table(sample_bike)
        assert '| **Wheel Size** | Front: 24", Rear: 20" |' in table

        # Test with same wheel sizes
        sample_bike.wheels_front_size_in = '20"'
        table = generate_specs_table(sample_bike)
        assert '| **Wheel Size** | 20" |' in table

    def test_generate_specs_table_minimal(self, db_session):
        """Test generating table for bike with minimal specs."""
        bike = Bike(title="Minimal", type="bike")
        db_session.add(bike)
        db_session.commit()

        table = generate_specs_table(bike)
        # Should return empty string if no specs
        assert table == ""


class TestReconstructMarkdownFile:
    """Tests for markdown file reconstruction."""

    def test_reconstruct_with_all_parts(self):
        """Test reconstructing a file with all parts."""
        parts = {
            "frontmatter": "title: Test\ntype: bike",
            "before_table": "## Introduction\n\nManual content before.",
            "table": "| Spec | Value |\n|------|-------|\n| Test | Data |",
            "after_table": "## Details\n\nManual content after.",
        }

        new_frontmatter = "title: Updated\ntype: bike\nbrand: NewBrand"
        new_table = "| New | Table |\n|-----|-------|\n| A   | B     |"

        result = reconstruct_markdown_file(parts, new_frontmatter, new_table)

        # Check frontmatter
        assert result.startswith("---\n")
        assert "title: Updated" in result
        assert "brand: NewBrand" in result

        # Check manual content is preserved
        assert "## Introduction" in result
        assert "Manual content before." in result
        assert "## Details" in result
        assert "Manual content after." in result

        # Check new table is present with markers
        assert SPECS_TABLE_START_MARKER in result
        assert SPECS_TABLE_END_MARKER in result
        assert "| New | Table |" in result

        # Check old table is not present
        assert "| Test | Data |" not in result

    def test_reconstruct_without_after_content(self):
        """Test reconstruction when there's no content after table."""
        parts = {
            "frontmatter": "title: Test",
            "before_table": "Content before",
            "table": "",
            "after_table": "",
        }

        new_frontmatter = "title: Updated"
        new_table = "| A | B |"

        result = reconstruct_markdown_file(parts, new_frontmatter, new_table)

        assert "---\n" in result
        assert "title: Updated" in result
        assert "Content before" in result
        assert SPECS_TABLE_START_MARKER in result
        assert SPECS_TABLE_END_MARKER in result
        assert "| A | B |" in result

    def test_reconstruct_preserves_exact_content(self):
        """Test that reconstruction preserves exact manual content."""
        # Complex manual content with various markdown elements
        manual_before = """## Overview

The bike is **awesome** with:
- Feature 1
- Feature 2

### Technical Details

Some code:
```python
print("test")
```

> A quote block
"""

        manual_after = """## User Reviews

1. First review
2. Second review

### Maintenance

- Step 1
- Step 2

[Link to manual](https://example.com)
"""

        parts = {
            "frontmatter": "title: Test",
            "before_table": manual_before,
            "table": "old table",
            "after_table": manual_after,
        }

        result = reconstruct_markdown_file(parts, "title: Updated", "new table")

        # Verify exact manual content preservation
        assert "The bike is **awesome** with:" in result
        assert "- Feature 1" in result
        assert "- Feature 2" in result
        assert '```python\nprint("test")\n```' in result
        assert "> A quote block" in result
        assert "## User Reviews" in result
        assert "1. First review" in result
        assert "[Link to manual](https://example.com)" in result


class TestFindBikeFile:
    """Tests for finding bike files."""

    def test_find_bike_file(self, temp_vault, db_session):
        """Test finding a bike file by title."""
        # Create brand directory and bike file
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        bike_file.write_text(
            """---
title: Test Bike
type: bike
brand: TestBrand
---

Content
"""
        )

        # Create bike record
        bike = Bike(title="Test Bike", type="bike", brand_name="TestBrand")
        db_session.add(bike)
        db_session.commit()

        # Find file
        found = find_bike_file(bike, temp_vault)
        assert found is not None
        assert found == bike_file

    def test_find_bike_file_not_found(self, temp_vault, db_session):
        """Test when bike file is not found."""
        bike = Bike(title="Nonexistent Bike", type="bike", brand_name="TestBrand")
        db_session.add(bike)
        db_session.commit()

        found = find_bike_file(bike, temp_vault)
        assert found is None

    def test_find_bike_file_skips_index(self, temp_vault, db_session):
        """Test that index files are skipped."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        # Create index file
        index_file = brand_dir / "index.md"
        index_file.write_text(
            """---
title: Test Bike
type: bike
---
"""
        )

        # Create actual bike file
        bike_file = brand_dir / "model.md"
        bike_file.write_text(
            """---
title: Test Bike
type: bike
---
"""
        )

        bike = Bike(title="Test Bike", type="bike", brand_name="TestBrand")
        db_session.add(bike)
        db_session.commit()

        found = find_bike_file(bike, temp_vault)
        assert found == bike_file


class TestProjectBikeToFile:
    """Tests for the complete projection process."""

    def test_project_bike_to_file_preserves_manual_content(
        self, temp_vault, db_session, sample_bike
    ):
        """
        CRITICAL TEST: Verify manual content is preserved during projection.
        This is the most important test per AC #7.
        """
        # Create brand directory and bike file with extensive manual content
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        original_content = """---
title: Test Bike Model X
type: bike
brand: TestBrand
specs:
  category: old
  motor:
    make: OldMotor
---

## Introduction

This is a **manually written** introduction that must be preserved.

### Key Features

- Custom feature 1
- Custom feature 2
- Custom feature 3

The bike has been tested extensively:

```python
def test_bike():
    assert bike.speed > 25
```

<!-- BIKE_SPECS_TABLE_START -->

| Old | Table |
|-----|-------|
| A   | B     |

<!-- BIKE_SPECS_TABLE_END -->

## Detailed Review

### Performance

The performance was excellent in various conditions.

1. Urban riding: 5/5
2. Hill climbing: 4/5
3. Long distance: 5/5

### User Experience

> "This bike changed my life!" - Happy Customer

#### Ergonomics

The seat is comfortable for long rides.

#### Maintenance

See the [maintenance guide](https://example.com/guide) for details.

### Comparison

| Feature    | This Bike | Competitor |
|------------|-----------|------------|
| Weight     | 28kg      | 32kg       |
| Price      | €3999     | €4500      |

### Conclusion

A fantastic bike overall!

[Official Website](https://testbrand.com)
"""
        bike_file.write_text(original_content)

        # Project the bike
        success, message = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert success, f"Projection failed: {message}"

        # Read the updated file
        updated_content = bike_file.read_text()

        # CRITICAL ASSERTIONS: All manual content must be preserved exactly

        # Before table
        assert "## Introduction" in updated_content
        assert (
            "This is a **manually written** introduction that must be preserved."
            in updated_content
        )
        assert "### Key Features" in updated_content
        assert "- Custom feature 1" in updated_content
        assert "- Custom feature 2" in updated_content
        assert "- Custom feature 3" in updated_content
        assert "The bike has been tested extensively:" in updated_content
        assert "```python\ndef test_bike():\n    assert bike.speed > 25\n```" in updated_content

        # After table
        assert "## Detailed Review" in updated_content
        assert "### Performance" in updated_content
        assert (
            "The performance was excellent in various conditions." in updated_content
        )
        assert "1. Urban riding: 5/5" in updated_content
        assert "2. Hill climbing: 4/5" in updated_content
        assert "3. Long distance: 5/5" in updated_content
        assert "### User Experience" in updated_content
        assert '> "This bike changed my life!" - Happy Customer' in updated_content
        assert "#### Ergonomics" in updated_content
        assert "The seat is comfortable for long rides." in updated_content
        assert "#### Maintenance" in updated_content
        assert (
            "See the [maintenance guide](https://example.com/guide) for details."
            in updated_content
        )
        assert "### Comparison" in updated_content
        assert "| Feature    | This Bike | Competitor |" in updated_content
        assert "### Conclusion" in updated_content
        assert "A fantastic bike overall!" in updated_content
        assert "[Official Website](https://testbrand.com)" in updated_content

        # Verify frontmatter was updated
        assert "brand: TestBrand" in updated_content
        assert "model: Model X" in updated_content

        # Verify specs table was updated (old table should be gone)
        assert "| Old | Table |" not in updated_content
        # New table should have content from database
        assert "| **Category** | longtail |" in updated_content
        assert "| **Motor** | Bosch Performance CX |" in updated_content

    def test_project_bike_updates_frontmatter(self, temp_vault, db_session, sample_bike):
        """Test that frontmatter is completely replaced."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        bike_file.write_text(
            """---
title: Test Bike Model X
type: bike
brand: TestBrand
old_field: should_be_removed
specs:
  old_spec: old_value
---

Content

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
"""
        )

        success, message = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert success

        updated_content = bike_file.read_text()

        # Check new fields are present
        assert "model: Model X" in updated_content
        assert "url: https://testbrand.com/model-x" in updated_content

        # Check old field is gone
        assert "old_field: should_be_removed" not in updated_content
        assert "old_spec: old_value" not in updated_content

        # Check specs are updated
        data = yaml.safe_load(updated_content.split("---")[1])
        assert "specs" in data
        assert data["specs"]["category"] == "longtail"
        assert data["specs"]["motor"]["make"] == "Bosch"

    def test_project_bike_updates_specs_table(self, temp_vault, db_session, sample_bike):
        """Test that specs table is replaced."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        bike_file.write_text(
            """---
title: Test Bike Model X
type: bike
---

Before

<!-- BIKE_SPECS_TABLE_START -->

| Old | Spec |
|-----|------|
| X   | Y    |

<!-- BIKE_SPECS_TABLE_END -->

After
"""
        )

        success, message = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert success

        updated_content = bike_file.read_text()

        # Old table should be gone
        assert "| Old | Spec |" not in updated_content

        # New table should be present
        assert "| Specification | Value |" in updated_content
        assert "| **Motor** | Bosch Performance CX |" in updated_content

        # Manual content preserved
        assert "Before" in updated_content
        assert "After" in updated_content

    def test_project_bike_dry_run(self, temp_vault, db_session, sample_bike):
        """Test that dry run doesn't write changes."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        original_content = """---
title: Test Bike Model X
type: bike
---

Original content

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
"""
        bike_file.write_text(original_content)

        success, message = project_bike_to_file(sample_bike, temp_vault, dry_run=True)
        assert success

        # File should be unchanged
        current_content = bike_file.read_text()
        assert current_content == original_content

    def test_project_bike_file_not_found(self, temp_vault, db_session, sample_bike):
        """Test handling when bike file is not found."""
        success, message = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert not success
        assert "Could not find file" in message


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_multiple_code_blocks_preserved(self, temp_vault, db_session, sample_bike):
        """Test that multiple code blocks are preserved."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        bike_file.write_text(
            """---
title: Test Bike Model X
type: bike
---

## Setup

```bash
npm install
```

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->

## Configuration

```json
{
  "setting": "value"
}
```

## Testing

```python
assert True
```
"""
        )

        success, _ = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert success

        updated_content = bike_file.read_text()
        assert "```bash\nnpm install\n```" in updated_content
        assert '```json\n{\n  "setting": "value"\n}\n```' in updated_content
        assert "```python\nassert True\n```" in updated_content

    def test_nested_lists_preserved(self, temp_vault, db_session, sample_bike):
        """Test that nested lists are preserved."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        bike_file.write_text(
            """---
title: Test Bike Model X
type: bike
---

## Features

- Main feature 1
  - Sub feature 1.1
  - Sub feature 1.2
    - Deep feature 1.2.1
- Main feature 2

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->

## More

1. First
   1. Sub first
   2. Sub second
2. Second
"""
        )

        success, _ = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert success

        updated_content = bike_file.read_text()
        assert "- Main feature 1" in updated_content
        assert "  - Sub feature 1.1" in updated_content
        assert "    - Deep feature 1.2.1" in updated_content
        assert "1. First" in updated_content
        assert "   1. Sub first" in updated_content

    def test_tables_outside_markers_preserved(self, temp_vault, db_session, sample_bike):
        """Test that markdown tables outside markers are preserved."""
        brand_dir = temp_vault / "bikes" / "testbrand"
        brand_dir.mkdir(parents=True)

        bike_file = brand_dir / "model-x.md"
        bike_file.write_text(
            """---
title: Test Bike Model X
type: bike
---

## Comparison

| Feature | Value |
|---------|-------|
| A       | 1     |
| B       | 2     |

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->

## Pricing

| Retailer | Price |
|----------|-------|
| Shop A   | $100  |
| Shop B   | $110  |
"""
        )

        success, _ = project_bike_to_file(sample_bike, temp_vault, dry_run=False)
        assert success

        updated_content = bike_file.read_text()
        # Tables outside markers should be preserved
        assert "| Feature | Value |" in updated_content
        assert "| A       | 1     |" in updated_content
        assert "| Retailer | Price |" in updated_content
        assert "| Shop A   | $100  |" in updated_content
