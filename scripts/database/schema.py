"""
SQLAlchemy models for the cargo-bikes vault database.

This module defines the database schema that mirrors the structures in:
- docs/schema/BIKE_SPECS_SCHEMA.md
- docs/schema/MANUFACTURER_SCHEMA.md

All tables and relationships are designed to enable structured, queryable storage
of vault content including bikes, brands, manufacturers, components, and resellers.
"""

from datetime import date
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# ==============================================================================
# BRAND/MANUFACTURER MODELS
# ==============================================================================


class Brand(Base):
    """
    Represents a cargo bike brand or component manufacturer.

    Maps to MANUFACTURER_SCHEMA.md. This table stores both bike brands
    (type='brand') and component manufacturers (type='manufacturer').
    """

    __tablename__ = "brands"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core Identity
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'brand' or 'manufacturer'
    date: Mapped[date] = mapped_column(Date, nullable=False)
    url: Mapped[str | None] = mapped_column(String(500))
    logo: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)

    # Company Information
    founded_year: Mapped[int | None] = mapped_column(Integer)
    country: Mapped[str | None] = mapped_column(String(100))
    headquarters_city: Mapped[str | None] = mapped_column(String(100))
    headquarters_country: Mapped[str | None] = mapped_column(String(100))
    headquarters_address: Mapped[str | None] = mapped_column(String(500))

    # Market & Positioning
    # Note: categories, market_segments, regions stored as comma-separated strings
    # Alternative: create junction tables for proper normalization
    categories: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated, e.g., "longtail,box-cargo"
    market_segments: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated, e.g., "urban-families,professionals"
    regions: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated, e.g., "EU,North America"
    price_tier: Mapped[str | None] = mapped_column(
        String(50)
    )  # entry-level, accessible, mid-premium, premium, ultra-premium

    # Product Portfolio
    product_types: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated, e.g., "bikes,motors,batteries"
    model_count: Mapped[int | None] = mapped_column(Integer)
    primary_motors: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated motor brands
    parent_company: Mapped[str | None] = mapped_column(String(255))

    # Manufacturing & Production
    manufacturing_locations: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated countries
    manufacturing_approach: Mapped[str | None] = mapped_column(
        String(50)
    )  # in-house, contracted, hybrid
    assembly_location: Mapped[str | None] = mapped_column(String(100))
    ethical_standards: Mapped[str | None] = mapped_column(Text)

    # Distribution & Sales
    distribution_model: Mapped[str | None] = mapped_column(
        String(50)
    )  # direct, retail, both, b2b
    regions_active: Mapped[str | None] = mapped_column(Text)  # Comma-separated
    direct_sales: Mapped[bool | None] = mapped_column(Boolean)
    dealership_network: Mapped[bool | None] = mapped_column(Boolean)

    # Impact Metrics
    impact_bikes_sold_approx: Mapped[int | None] = mapped_column(Integer)
    impact_km_driven_approx: Mapped[int | None] = mapped_column(Integer)
    impact_co2_avoided_kg_approx: Mapped[int | None] = mapped_column(Integer)
    impact_families_served: Mapped[int | None] = mapped_column(Integer)

    # Accessibility & Values
    accessibility: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated value propositions
    value_sustainability: Mapped[bool | None] = mapped_column(Boolean)
    value_local_manufacturing: Mapped[bool | None] = mapped_column(Boolean)
    value_community_focus: Mapped[bool | None] = mapped_column(Boolean)
    value_safety_emphasis: Mapped[bool | None] = mapped_column(Boolean)
    value_tech_integration: Mapped[bool | None] = mapped_column(Boolean)

    # Metadata
    tags: Mapped[str | None] = mapped_column(Text)  # Comma-separated tags

    # Relationships
    bikes: Mapped[list["Bike"]] = relationship("Bike", back_populates="brand")


# ==============================================================================
# BIKE MODELS
# ==============================================================================


class Bike(Base):
    """
    Represents a cargo bike model with complete specifications.

    Maps to BIKE_SPECS_SCHEMA.md with all top-level fields and nested specs.
    """

    __tablename__ = "bikes"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Top-level Fields (Required)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="bike"
    )  # Always 'bike'

    # Top-level Fields (Optional)
    brand_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("brands.id"), index=True
    )
    brand_name: Mapped[str | None] = mapped_column(
        String(255)
    )  # Denormalized for queries
    model: Mapped[str | None] = mapped_column(String(255))
    tags: Mapped[str | None] = mapped_column(Text)  # Comma-separated
    url: Mapped[str | None] = mapped_column(String(500))
    image: Mapped[str | None] = mapped_column(String(500))
    file_path: Mapped[str | None] = mapped_column(
        String(500)
    )  # Relative path to markdown file (e.g., vault/notes/bikes/brand/model.md)

    # Specs: Basic Classification
    category: Mapped[str | None] = mapped_column(
        String(50), index=True
    )  # longtail, box, trike, etc.
    model_year: Mapped[int | None] = mapped_column(Integer, index=True)

    # Specs: Frame
    frame_material: Mapped[str | None] = mapped_column(String(100))
    frame_size: Mapped[str | None] = mapped_column(String(100))
    frame_length_cm: Mapped[float | None] = mapped_column(Float)
    frame_width_cm: Mapped[float | None] = mapped_column(Float)
    frame_height_cm: Mapped[float | None] = mapped_column(Float)

    # Specs: Weight
    weight_bike_kg: Mapped[float | None] = mapped_column(Float)
    weight_with_battery_kg: Mapped[float | None] = mapped_column(Float)
    weight_battery_kg: Mapped[float | None] = mapped_column(Float)

    # Specs: Load Capacity
    load_capacity_total_kg: Mapped[float | None] = mapped_column(Float)
    load_capacity_rear_kg: Mapped[float | None] = mapped_column(Float)
    load_capacity_front_kg: Mapped[float | None] = mapped_column(Float)
    load_capacity_passenger_count: Mapped[int | None] = mapped_column(Integer)
    load_capacity_passenger_config: Mapped[str | None] = mapped_column(String(255))

    # Specs: Motor
    motor_make: Mapped[str | None] = mapped_column(String(100), index=True)
    motor_model: Mapped[str | None] = mapped_column(String(100))
    motor_type: Mapped[str | None] = mapped_column(
        String(50)
    )  # mid-drive, rear-hub, front-hub
    motor_power_w: Mapped[float | None] = mapped_column(Float)
    motor_torque_nm: Mapped[float | None] = mapped_column(Float)
    motor_boost_throttle: Mapped[bool | None] = mapped_column(Boolean)
    motor_options: Mapped[str | None] = mapped_column(
        Text
    )  # JSON string for multiple configs

    # Specs: Battery
    battery_capacity_wh: Mapped[float | None] = mapped_column(Float)
    battery_configuration: Mapped[str | None] = mapped_column(
        String(100)
    )  # single, dual, integrated
    battery_removable: Mapped[bool | None] = mapped_column(Boolean)
    battery_charging_time_h: Mapped[str | None] = mapped_column(
        String(50)
    )  # Can be range like "3-5"

    # Specs: Drivetrain
    drivetrain_type: Mapped[str | None] = mapped_column(String(50))  # chain, belt
    drivetrain_speeds: Mapped[str | None] = mapped_column(
        String(50)
    )  # e.g., "10-speed" or "10"
    drivetrain_hub: Mapped[str | None] = mapped_column(
        String(100)
    )  # Internal hub model

    # Specs: Brakes
    brakes_type: Mapped[str | None] = mapped_column(String(100))
    brakes_front_rotor_mm: Mapped[int | None] = mapped_column(Integer)
    brakes_rear_rotor_mm: Mapped[int | None] = mapped_column(Integer)
    brakes_pistons: Mapped[str | None] = mapped_column(String(50))

    # Specs: Wheels
    wheels_front_size_in: Mapped[str | None] = mapped_column(String(50))
    wheels_rear_size_in: Mapped[str | None] = mapped_column(String(50))
    wheels_tire: Mapped[str | None] = mapped_column(String(255))
    wheels_rims: Mapped[str | None] = mapped_column(String(255))

    # Specs: Suspension
    suspension_front: Mapped[str | None] = mapped_column(String(255))
    suspension_rear: Mapped[str | None] = mapped_column(String(255))

    # Specs: Lights - Front
    lights_front_type: Mapped[str | None] = mapped_column(String(255))
    lights_front_integrated: Mapped[bool | None] = mapped_column(Boolean)
    lights_front_powered_by: Mapped[str | None] = mapped_column(String(100))
    lights_front_optional_kits: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated

    # Specs: Lights - Rear
    lights_rear_type: Mapped[str | None] = mapped_column(String(255))
    lights_rear_integrated: Mapped[bool | None] = mapped_column(Boolean)
    lights_rear_brake_light: Mapped[bool | None] = mapped_column(Boolean)
    lights_rear_optional_kits: Mapped[str | None] = mapped_column(
        Text
    )  # Comma-separated

    # Specs: Lights - Turn Signals
    lights_turn_signals_integrated: Mapped[bool | None] = mapped_column(Boolean)
    lights_turn_signals_type: Mapped[str | None] = mapped_column(String(255))
    lights_turn_signals_left_right_buttons: Mapped[bool | None] = mapped_column(Boolean)

    # Specs: Features
    features: Mapped[str | None] = mapped_column(Text)  # Comma-separated feature tags

    # Specs: Security
    security_gps: Mapped[bool | None] = mapped_column(Boolean)
    security_alarm_db: Mapped[int | None] = mapped_column(Integer)
    security_app_lock: Mapped[bool | None] = mapped_column(Boolean)
    security_frame_lock: Mapped[bool | None] = mapped_column(Boolean)

    # Specs: Range
    range_estimate_km: Mapped[str | None] = mapped_column(
        String(100)
    )  # Can be range like "60-150"
    range_notes: Mapped[str | None] = mapped_column(Text)

    # Specs: Price (MSRP)
    price_amount: Mapped[str | None] = mapped_column(
        String(50)
    )  # Can be number or string like "from 4999"
    price_currency: Mapped[str | None] = mapped_column(String(10))

    # Specs: General Notes
    specs_notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="bikes")
    resellers: Mapped[list["Reseller"]] = relationship(
        "Reseller", back_populates="bike", cascade="all, delete-orphan"
    )


# ==============================================================================
# RESELLER MODELS
# ==============================================================================


class Reseller(Base):
    """
    Represents a reseller entry for a specific bike.

    Each bike can have multiple reseller entries, each with pricing and
    availability information for different regions or stores.
    """

    __tablename__ = "resellers"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key to Bike
    bike_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bikes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Reseller Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[str | None] = mapped_column(String(50))  # Can be number or "from X"
    currency: Mapped[str | None] = mapped_column(String(10))
    region: Mapped[str | None] = mapped_column(String(100))
    availability: Mapped[str | None] = mapped_column(
        String(50)
    )  # in-stock, pre-order, out-of-stock
    note: Mapped[str | None] = mapped_column(Text)

    # Relationships
    bike: Mapped["Bike"] = relationship("Bike", back_populates="resellers")


# ==============================================================================
# COMPONENT MODELS (Future Extension)
# ==============================================================================


class Component(Base):
    """
    Represents individual bike components (motors, batteries, etc.).

    This is a placeholder for future extension based on COMPONENT_SCHEMA.md
    when that schema is fully defined.
    """

    __tablename__ = "components"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Basic Fields (to be expanded based on component schema)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # motor, battery, display, etc.
    manufacturer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("brands.id")
    )
    manufacturer_name: Mapped[str | None] = mapped_column(String(255))
    model: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(String(500))
    image: Mapped[str | None] = mapped_column(String(500))
    specs: Mapped[str | None] = mapped_column(Text)  # JSON string for flexible specs
    tags: Mapped[str | None] = mapped_column(Text)


# ==============================================================================
# DATABASE UTILITIES
# ==============================================================================


def create_tables(engine):
    """
    Create all tables in the database.

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """
    Drop all tables from the database.

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)


def get_table_names():
    """
    Get a list of all table names defined in the schema.

    Returns:
        List of table name strings
    """
    return [table.name for table in Base.metadata.sorted_tables]
