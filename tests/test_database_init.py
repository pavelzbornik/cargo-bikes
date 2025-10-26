"""
Unit tests for database initialization and schema validation.

Tests verify that:
1. The database can be created successfully
2. All expected tables are created
3. Table columns match the schema definitions
4. Relationships between tables are properly configured
"""

import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.database.init_db import init_database, verify_schema
from scripts.database.schema import (
    Base,
    get_table_names,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path that will be cleaned up after tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as tmp:
        tmp_path = Path(tmp.name)

    # At this point the file has been deleted by the context manager
    yield str(tmp_path)

    # Cleanup: remove the temp database file after test if it was created
    if tmp_path.exists():
        tmp_path.unlink()


@pytest.fixture
def in_memory_engine():
    """Create an in-memory SQLite database for testing."""
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


class TestDatabaseInitialization:
    """Test suite for database initialization functionality."""

    def test_init_database_creates_file(self, temp_db_path):
        """Test that init_database creates a database file at the specified path."""
        # Database file should not exist yet
        assert not Path(temp_db_path).exists()

        # Initialize database
        engine = init_database(temp_db_path, echo=False)

        # Verify file was created
        assert Path(temp_db_path).exists()
        assert isinstance(engine, Engine)

    def test_init_database_creates_all_tables(self, temp_db_path):
        """Test that all expected tables are created."""
        engine = init_database(temp_db_path, echo=False)

        # Get actual tables from database
        inspector = inspect(engine)
        created_tables = set(inspector.get_table_names())

        # Get expected tables from schema
        expected_tables = set(get_table_names())

        # Verify all expected tables exist
        assert created_tables == expected_tables
        assert len(created_tables) == 4  # bikes, brands, resellers, components

    def test_in_memory_database_creation(self, in_memory_engine):
        """Test that schema works with in-memory database."""
        inspector = inspect(in_memory_engine)
        tables = inspector.get_table_names()

        assert "bikes" in tables
        assert "brands" in tables
        assert "resellers" in tables
        assert "components" in tables

    def test_verify_schema_success(self, in_memory_engine):
        """Test that verify_schema returns True for valid schema."""
        result = verify_schema(in_memory_engine)
        assert result is True

    def test_get_table_names(self):
        """Test that get_table_names returns all expected table names."""
        table_names = get_table_names()

        assert isinstance(table_names, list)
        assert "bikes" in table_names
        assert "brands" in table_names
        assert "resellers" in table_names
        assert "components" in table_names


class TestBrandTableSchema:
    """Test suite for Brand table schema validation."""

    def test_brand_table_exists(self, in_memory_engine):
        """Test that brands table exists."""
        inspector = inspect(in_memory_engine)
        assert "brands" in inspector.get_table_names()

    def test_brand_required_columns(self, in_memory_engine):
        """Test that brands table has all required columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("brands")}

        required_columns = {
            "id",
            "title",
            "type",
            "date",
        }

        assert required_columns.issubset(columns)

    def test_brand_optional_columns(self, in_memory_engine):
        """Test that brands table has all optional columns from MANUFACTURER_SCHEMA."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("brands")}

        optional_columns = {
            "url",
            "logo",
            "summary",
            "founded_year",
            "country",
            "headquarters_city",
            "headquarters_country",
            "categories",
            "market_segments",
            "regions",
            "price_tier",
            "product_types",
            "model_count",
            "primary_motors",
            "parent_company",
            "manufacturing_locations",
            "manufacturing_approach",
            "distribution_model",
            "direct_sales",
            "dealership_network",
            "tags",
        }

        assert optional_columns.issubset(columns)

    def test_brand_value_columns(self, in_memory_engine):
        """Test that brands table has value boolean columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("brands")}

        value_columns = {
            "value_sustainability",
            "value_local_manufacturing",
            "value_community_focus",
            "value_safety_emphasis",
            "value_tech_integration",
        }

        assert value_columns.issubset(columns)


class TestBikeTableSchema:
    """Test suite for Bike table schema validation."""

    def test_bike_table_exists(self, in_memory_engine):
        """Test that bikes table exists."""
        inspector = inspect(in_memory_engine)
        assert "bikes" in inspector.get_table_names()

    def test_bike_required_columns(self, in_memory_engine):
        """Test that bikes table has all required columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        required_columns = {
            "id",
            "title",
            "type",
        }

        assert required_columns.issubset(columns)

    def test_bike_top_level_columns(self, in_memory_engine):
        """Test that bikes table has top-level frontmatter columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        top_level_columns = {
            "brand_id",
            "brand_name",
            "model",
            "tags",
            "url",
            "image",
        }

        assert top_level_columns.issubset(columns)

    def test_bike_specs_basic_columns(self, in_memory_engine):
        """Test that bikes table has basic spec columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        basic_spec_columns = {
            "category",
            "model_year",
        }

        assert basic_spec_columns.issubset(columns)

    def test_bike_frame_columns(self, in_memory_engine):
        """Test that bikes table has frame specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        frame_columns = {
            "frame_material",
            "frame_size",
            "frame_length_cm",
            "frame_width_cm",
            "frame_height_cm",
        }

        assert frame_columns.issubset(columns)

    def test_bike_weight_columns(self, in_memory_engine):
        """Test that bikes table has weight specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        weight_columns = {
            "weight_bike_kg",
            "weight_with_battery_kg",
            "weight_battery_kg",
        }

        assert weight_columns.issubset(columns)

    def test_bike_load_capacity_columns(self, in_memory_engine):
        """Test that bikes table has load capacity columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        load_columns = {
            "load_capacity_total_kg",
            "load_capacity_rear_kg",
            "load_capacity_front_kg",
            "load_capacity_passenger_count",
            "load_capacity_passenger_config",
        }

        assert load_columns.issubset(columns)

    def test_bike_motor_columns(self, in_memory_engine):
        """Test that bikes table has motor specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        motor_columns = {
            "motor_make",
            "motor_model",
            "motor_type",
            "motor_power_w",
            "motor_torque_nm",
            "motor_boost_throttle",
        }

        assert motor_columns.issubset(columns)

    def test_bike_battery_columns(self, in_memory_engine):
        """Test that bikes table has battery specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        battery_columns = {
            "battery_capacity_wh",
            "battery_configuration",
            "battery_removable",
            "battery_charging_time_h",
        }

        assert battery_columns.issubset(columns)

    def test_bike_drivetrain_columns(self, in_memory_engine):
        """Test that bikes table has drivetrain specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        drivetrain_columns = {
            "drivetrain_type",
            "drivetrain_speeds",
            "drivetrain_hub",
        }

        assert drivetrain_columns.issubset(columns)

    def test_bike_brakes_columns(self, in_memory_engine):
        """Test that bikes table has brake specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        brake_columns = {
            "brakes_type",
            "brakes_front_rotor_mm",
            "brakes_rear_rotor_mm",
            "brakes_pistons",
        }

        assert brake_columns.issubset(columns)

    def test_bike_wheels_columns(self, in_memory_engine):
        """Test that bikes table has wheel specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        wheel_columns = {
            "wheels_front_size_in",
            "wheels_rear_size_in",
            "wheels_tire",
            "wheels_rims",
        }

        assert wheel_columns.issubset(columns)

    def test_bike_lights_columns(self, in_memory_engine):
        """Test that bikes table has lighting specification columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        light_columns = {
            "lights_front_type",
            "lights_front_integrated",
            "lights_rear_type",
            "lights_rear_integrated",
            "lights_rear_brake_light",
            "lights_turn_signals_integrated",
        }

        assert light_columns.issubset(columns)

    def test_bike_security_columns(self, in_memory_engine):
        """Test that bikes table has security feature columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        security_columns = {
            "security_gps",
            "security_alarm_db",
            "security_app_lock",
            "security_frame_lock",
        }

        assert security_columns.issubset(columns)

    def test_bike_range_columns(self, in_memory_engine):
        """Test that bikes table has range estimation columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        range_columns = {
            "range_estimate_km",
            "range_notes",
        }

        assert range_columns.issubset(columns)

    def test_bike_price_columns(self, in_memory_engine):
        """Test that bikes table has price columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("bikes")}

        price_columns = {
            "price_amount",
            "price_currency",
        }

        assert price_columns.issubset(columns)


class TestResellerTableSchema:
    """Test suite for Reseller table schema validation."""

    def test_reseller_table_exists(self, in_memory_engine):
        """Test that resellers table exists."""
        inspector = inspect(in_memory_engine)
        assert "resellers" in inspector.get_table_names()

    def test_reseller_required_columns(self, in_memory_engine):
        """Test that resellers table has all required columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("resellers")}

        required_columns = {
            "id",
            "bike_id",
            "name",
        }

        assert required_columns.issubset(columns)

    def test_reseller_optional_columns(self, in_memory_engine):
        """Test that resellers table has all optional columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("resellers")}

        optional_columns = {
            "url",
            "price",
            "currency",
            "region",
            "availability",
            "note",
        }

        assert optional_columns.issubset(columns)

    def test_reseller_foreign_key(self, in_memory_engine):
        """Test that resellers table has foreign key to bikes."""
        inspector = inspect(in_memory_engine)
        foreign_keys = inspector.get_foreign_keys("resellers")

        assert len(foreign_keys) > 0
        fk = foreign_keys[0]
        assert fk["referred_table"] == "bikes"
        assert "bike_id" in fk["constrained_columns"]


class TestComponentTableSchema:
    """Test suite for Component table schema validation."""

    def test_component_table_exists(self, in_memory_engine):
        """Test that components table exists."""
        inspector = inspect(in_memory_engine)
        assert "components" in inspector.get_table_names()

    def test_component_required_columns(self, in_memory_engine):
        """Test that components table has all required columns."""
        inspector = inspect(in_memory_engine)
        columns = {col["name"] for col in inspector.get_columns("components")}

        required_columns = {
            "id",
            "title",
            "type",
        }

        assert required_columns.issubset(columns)


class TestTableRelationships:
    """Test suite for table relationships and foreign keys."""

    def test_bike_brand_relationship(self, in_memory_engine):
        """Test that bikes table has foreign key to brands."""
        inspector = inspect(in_memory_engine)
        foreign_keys = inspector.get_foreign_keys("bikes")

        # Find the brand_id foreign key
        brand_fk = [
            fk for fk in foreign_keys if "brand_id" in fk["constrained_columns"]
        ]

        assert len(brand_fk) > 0
        assert brand_fk[0]["referred_table"] == "brands"

    def test_component_manufacturer_relationship(self, in_memory_engine):
        """Test that components table has foreign key to brands."""
        inspector = inspect(in_memory_engine)
        foreign_keys = inspector.get_foreign_keys("components")

        # Find the manufacturer_id foreign key
        mfg_fk = [
            fk for fk in foreign_keys if "manufacturer_id" in fk["constrained_columns"]
        ]

        assert len(mfg_fk) > 0
        assert mfg_fk[0]["referred_table"] == "brands"


class TestSchemaIntegrity:
    """Test suite for overall schema integrity."""

    def test_all_models_have_primary_keys(self, in_memory_engine):
        """Test that all tables have primary keys defined."""
        inspector = inspect(in_memory_engine)

        for table_name in get_table_names():
            pk = inspector.get_pk_constraint(table_name)
            assert pk is not None
            assert len(pk["constrained_columns"]) > 0
            assert "id" in pk["constrained_columns"]

    def test_table_count_matches_models(self, in_memory_engine):
        """Test that number of created tables matches defined models."""
        inspector = inspect(in_memory_engine)
        actual_tables = set(inspector.get_table_names())
        expected_tables = set(get_table_names())

        assert len(actual_tables) == len(expected_tables)
        assert actual_tables == expected_tables
