"""
Tests for the database hydration script.

Tests verify that the hydration script correctly populates the database
from Markdown files and maintains idempotency.
"""

import sys
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database.hydrate import (
    extract_frontmatter,
    get_or_create_brand,
    hydrate_from_vault,
    parse_date,
    parse_tags,
    upsert_bike,
    upsert_brand,
)
from scripts.database.schema import Base, Bike, Brand


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
        yield vault_path


class TestExtractFrontmatter:
    """Tests for frontmatter extraction."""

    def test_extract_valid_frontmatter(self, temp_vault):
        """Test extraction of valid frontmatter."""
        md_file = temp_vault / "test.md"
        md_file.write_text("""---
title: Test
type: bike
brand: TestBrand
---

# Content
""")
        frontmatter = extract_frontmatter(md_file)
        assert frontmatter is not None
        assert frontmatter["title"] == "Test"
        assert frontmatter["type"] == "bike"
        assert frontmatter["brand"] == "TestBrand"

    def test_extract_invalid_frontmatter(self, temp_vault):
        """Test extraction of invalid frontmatter."""
        md_file = temp_vault / "test.md"
        md_file.write_text("""# No frontmatter
Content here
""")
        frontmatter = extract_frontmatter(md_file)
        assert frontmatter is None


class TestParsers:
    """Tests for parser utility functions."""

    def test_parse_date_from_string(self):
        """Test parsing date from string."""
        result = parse_date("2024-05-22")
        assert result == date(2024, 5, 22)

    def test_parse_date_from_date(self):
        """Test parsing date from date object."""
        d = date(2024, 5, 22)
        result = parse_date(d)
        assert result == d

    def test_parse_date_invalid(self):
        """Test parsing invalid date."""
        result = parse_date("invalid")
        assert result is None

    def test_parse_tags_from_list(self):
        """Test parsing tags from list."""
        result = parse_tags(["bike", "longtail", "trek"])
        assert result == "bike,longtail,trek"

    def test_parse_tags_from_string(self):
        """Test parsing tags from string."""
        result = parse_tags("bike,longtail")
        assert result == "bike,longtail"

    def test_parse_tags_none(self):
        """Test parsing None tags."""
        result = parse_tags(None)
        assert result is None


class TestUpsertBrand:
    """Tests for brand upsert operations."""

    def test_create_new_brand(self, db_session, temp_vault):
        """Test creating a new brand."""
        brand_file = temp_vault / "brand.md"
        brand_file.write_text("""---
title: TestBrand
type: brand
date: 2024-05-22
url: https://testbrand.com
tags: [brand, cargo-bikes]
---

# TestBrand
""")
        frontmatter = extract_frontmatter(brand_file)
        brand = upsert_brand(db_session, frontmatter, brand_file)

        assert brand is not None
        assert brand.title == "TestBrand"
        assert brand.type == "brand"
        assert brand.url == "https://testbrand.com"
        assert brand.tags == "brand,cargo-bikes"

    def test_update_existing_brand(self, db_session, temp_vault):
        """Test updating an existing brand."""
        # Create initial brand
        brand_file = temp_vault / "brand.md"
        brand_file.write_text("""---
title: TestBrand
type: brand
date: 2024-05-22
url: https://testbrand.com
---

# TestBrand
""")
        frontmatter = extract_frontmatter(brand_file)
        brand1 = upsert_brand(db_session, frontmatter, brand_file)
        db_session.commit()

        # Update with new data
        brand_file.write_text("""---
title: TestBrand
type: brand
date: 2024-05-23
url: https://newurl.com
country: Germany
---

# TestBrand Updated
""")
        frontmatter = extract_frontmatter(brand_file)
        brand2 = upsert_brand(db_session, frontmatter, brand_file)
        db_session.commit()

        # Check that it's the same brand (not a duplicate)
        assert brand1.id == brand2.id
        assert brand2.url == "https://newurl.com"
        assert brand2.country == "Germany"

        # Verify only one brand exists
        stmt = select(Brand)
        brands = db_session.execute(stmt).scalars().all()
        assert len(brands) == 1

    def test_ignore_non_brand_type(self, db_session, temp_vault):
        """Test that non-brand types are ignored."""
        guide_file = temp_vault / "guide.md"
        guide_file.write_text("""---
title: Guide
type: guide
---

# Guide
""")
        frontmatter = extract_frontmatter(guide_file)
        brand = upsert_brand(db_session, frontmatter, guide_file)

        assert brand is None


class TestGetOrCreateBrand:
    """Tests for get_or_create_brand function."""

    def test_get_existing_brand(self, db_session):
        """Test getting an existing brand."""
        # Create a brand
        existing_brand = Brand(title="TestBrand", type="brand", date=date.today())
        db_session.add(existing_brand)
        db_session.commit()

        # Get the brand
        brand = get_or_create_brand(db_session, "TestBrand")
        assert brand is not None
        assert brand.id == existing_brand.id

    def test_create_placeholder_brand(self, db_session):
        """Test creating a placeholder brand."""
        brand = get_or_create_brand(db_session, "NewBrand")
        assert brand is not None
        assert brand.title == "NewBrand"
        assert brand.type == "brand"

    def test_none_brand_name(self, db_session):
        """Test with None brand name."""
        brand = get_or_create_brand(db_session, None)
        assert brand is None


class TestUpsertBike:
    """Tests for bike upsert operations."""

    def test_create_new_bike(self, db_session, temp_vault):
        """Test creating a new bike."""
        bike_file = temp_vault / "bike.md"
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
model: Model X
tags: [bike, longtail]
url: https://testbrand.com/bike
image: https://testbrand.com/bike.jpg
specs:
  category: longtail
  model_year: 2024
  motor:
    make: Bosch
    model: Performance CX
    power_w: 250
    torque_nm: 85
  battery:
    capacity_wh: 500
    removable: true
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")
        frontmatter = extract_frontmatter(bike_file)
        bike = upsert_bike(db_session, frontmatter, bike_file)
        db_session.commit()

        assert bike is not None
        assert bike.title == "Test Bike"
        assert bike.brand_name == "TestBrand"
        assert bike.model == "Model X"
        assert bike.category == "longtail"
        assert bike.model_year == 2024
        assert bike.motor_make == "Bosch"
        assert bike.motor_model == "Performance CX"
        assert bike.motor_power_w == 250
        assert bike.motor_torque_nm == 85
        assert bike.battery_capacity_wh == 500
        assert bike.battery_removable is True

    def test_update_existing_bike(self, db_session, temp_vault):
        """Test updating an existing bike."""
        # Create initial bike
        bike_file = temp_vault / "bike.md"
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
specs:
  motor:
    make: Bosch
    power_w: 250
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")
        frontmatter = extract_frontmatter(bike_file)
        bike1 = upsert_bike(db_session, frontmatter, bike_file)
        db_session.commit()

        # Update with new specs
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
specs:
  motor:
    make: Shimano
    power_w: 300
  battery:
    capacity_wh: 600
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")
        frontmatter = extract_frontmatter(bike_file)
        bike2 = upsert_bike(db_session, frontmatter, bike_file)
        db_session.commit()

        # Check that it's the same bike (not a duplicate)
        assert bike1.id == bike2.id
        assert bike2.motor_make == "Shimano"
        assert bike2.motor_power_w == 300
        assert bike2.battery_capacity_wh == 600

        # Verify only one bike exists
        stmt = select(Bike)
        bikes = db_session.execute(stmt).scalars().all()
        assert len(bikes) == 1

    def test_bike_with_resellers(self, db_session, temp_vault):
        """Test creating bike with resellers."""
        bike_file = temp_vault / "bike.md"
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
resellers:
  - name: BikeShop
    url: https://bikeshop.com/bike
    price: 3999
    currency: EUR
    region: EU
    availability: in-stock
  - name: Another Shop
    url: https://anothershop.com/bike
    price: 4200
    currency: EUR
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")
        frontmatter = extract_frontmatter(bike_file)
        bike = upsert_bike(db_session, frontmatter, bike_file)
        db_session.commit()

        assert bike is not None
        assert len(bike.resellers) == 2
        assert bike.resellers[0].name == "BikeShop"
        assert bike.resellers[0].price == "3999"
        assert bike.resellers[0].currency == "EUR"
        assert bike.resellers[1].name == "Another Shop"

    def test_update_bike_resellers(self, db_session, temp_vault):
        """Test updating bike resellers."""
        bike_file = temp_vault / "bike.md"

        # Create bike with initial resellers
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
resellers:
  - name: Shop1
    price: 3999
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")
        frontmatter = extract_frontmatter(bike_file)
        bike1 = upsert_bike(db_session, frontmatter, bike_file)
        db_session.commit()
        assert len(bike1.resellers) == 1

        # Update with new resellers
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
resellers:
  - name: Shop2
    price: 4200
  - name: Shop3
    price: 4500
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")
        frontmatter = extract_frontmatter(bike_file)
        bike2 = upsert_bike(db_session, frontmatter, bike_file)
        db_session.commit()

        # Refresh from database
        db_session.expire_all()
        stmt = select(Bike).where(Bike.id == bike2.id)
        bike_refreshed = db_session.execute(stmt).scalar_one()

        # Old resellers should be replaced
        assert len(bike_refreshed.resellers) == 2
        reseller_names = {r.name for r in bike_refreshed.resellers}
        assert "Shop2" in reseller_names
        assert "Shop3" in reseller_names
        assert "Shop1" not in reseller_names


class TestHydrateFromVault:
    """Tests for vault hydration."""

    def test_empty_vault(self, db_session, temp_vault):
        """Test hydrating from an empty vault."""
        stats = hydrate_from_vault(db_session, temp_vault)
        assert stats["files_processed"] == 0
        assert stats["brands_created"] == 0
        assert stats["bikes_created"] == 0

    def test_hydrate_brands_and_bikes(self, db_session, temp_vault):
        """Test hydrating brands and bikes."""
        # Create brand file
        brands_dir = temp_vault / "brands"
        brands_dir.mkdir()
        brand_file = brands_dir / "testbrand.md"
        brand_file.write_text("""---
title: TestBrand
type: brand
date: 2024-05-22
url: https://testbrand.com
---

# TestBrand
""")

        # Create bike file
        bikes_dir = temp_vault / "bikes" / "testbrand"
        bikes_dir.mkdir(parents=True)
        bike_file = bikes_dir / "bike1.md"
        bike_file.write_text("""---
title: Bike 1
type: bike
brand: TestBrand
specs:
  category: longtail
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")

        stats = hydrate_from_vault(db_session, temp_vault)

        assert stats["files_processed"] == 2
        assert stats["brands_created"] == 1
        assert stats["bikes_created"] == 1

        # Verify database contents
        stmt = select(Brand)
        brands = db_session.execute(stmt).scalars().all()
        assert len(brands) == 1
        assert brands[0].title == "TestBrand"

        stmt = select(Bike)
        bikes = db_session.execute(stmt).scalars().all()
        assert len(bikes) == 1
        assert bikes[0].title == "Bike 1"
        assert bikes[0].brand_name == "TestBrand"

    def test_idempotency(self, db_session, temp_vault):
        """Test that hydration is idempotent."""
        # Create test files
        bike_file = temp_vault / "bike.md"
        bike_file.write_text("""---
title: Test Bike
type: bike
brand: TestBrand
specs:
  motor:
    make: Bosch
---

<!-- BIKE_SPECS_TABLE_START -->
<!-- BIKE_SPECS_TABLE_END -->
""")

        # First hydration
        stats1 = hydrate_from_vault(db_session, temp_vault)
        assert stats1["bikes_created"] == 1
        # Note: Placeholder brand is created inline during bike processing, not counted separately

        # Get counts
        stmt = select(Bike)
        bikes_count1 = len(db_session.execute(stmt).scalars().all())
        stmt = select(Brand)
        brands_count1 = len(db_session.execute(stmt).scalars().all())

        # Should have 1 bike and 1 placeholder brand
        assert bikes_count1 == 1
        assert brands_count1 == 1

        # Second hydration (without changes)
        stats2 = hydrate_from_vault(db_session, temp_vault)
        assert stats2["bikes_created"] == 0
        assert stats2["bikes_updated"] == 1

        # Verify no duplicates
        stmt = select(Bike)
        bikes_count2 = len(db_session.execute(stmt).scalars().all())
        stmt = select(Brand)
        brands_count2 = len(db_session.execute(stmt).scalars().all())

        assert bikes_count1 == bikes_count2
        assert brands_count1 == brands_count2

    def test_ignore_invalid_files(self, db_session, temp_vault):
        """Test that invalid files are ignored gracefully."""
        # Create valid file
        valid_file = temp_vault / "valid.md"
        valid_file.write_text("""---
title: Valid
type: guide
---

# Valid
""")

        # Create file without frontmatter
        invalid_file = temp_vault / "invalid.md"
        invalid_file.write_text("""# No frontmatter
""")

        stats = hydrate_from_vault(db_session, temp_vault)

        # Only the valid file should be processed
        assert stats["files_processed"] == 1
