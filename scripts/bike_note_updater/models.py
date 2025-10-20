"""Pydantic models for bike specifications and validation.

These models represent the BIKE_SPECS_SCHEMA and provide type-safe
data structures for the bike note updater agent.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FrameDimensions(BaseModel):
    """Physical dimensions of the bike frame."""

    length_cm: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None


class Frame(BaseModel):
    """Frame specifications."""

    material: str | None = None
    size: str | int | None = None
    dimensions: FrameDimensions | None = None


class Weight(BaseModel):
    """Weight specifications."""

    bike_kg: float | None = None
    with_battery_kg: float | None = None
    battery_kg: float | None = None


class LoadCapacity(BaseModel):
    """Load capacity specifications."""

    total_kg: float | None = None
    rear_kg: float | None = None
    front_kg: float | None = None
    passenger_count_excluding_rider: int | None = None
    passenger_config: str | None = None


class MotorOption(BaseModel):
    """Single motor configuration option."""

    model: str | None = None
    power_w: int | str | None = None
    torque_nm: float | None = None


class Motor(BaseModel):
    """Motor specifications."""

    make: str | None = None
    model: str | None = None
    type: str | None = None
    power_w: int | str | None = None
    torque_nm: float | None = None
    boost_throttle: bool | None = None
    options: list[MotorOption] | None = None


class Battery(BaseModel):
    """Battery specifications."""

    capacity_wh: int | None = None
    configuration: str | None = None
    removable: bool | None = None
    charging_time_h: float | str | None = None


class Drivetrain(BaseModel):
    """Drivetrain specifications."""

    type: str | None = None
    speeds: str | int | None = None
    hub: str | None = None


class Brakes(BaseModel):
    """Brake system specifications."""

    type: str | None = None
    front_rotor_mm: int | None = None
    rear_rotor_mm: int | None = None
    pistons: str | int | None = None


class Wheels(BaseModel):
    """Wheel specifications."""

    front_size_in: str | None = None
    rear_size_in: str | None = None
    tire: str | None = None
    rims: str | None = None


class Suspension(BaseModel):
    """Suspension specifications."""

    front: str | None = None
    rear: str | None = None


class Light(BaseModel):
    """Individual light specifications."""

    type: str | None = None
    integrated: bool | None = None
    powered_by: str | None = None
    optional_kits: list[str] | None = None
    brake_light: bool | None = None


class TurnSignals(BaseModel):
    """Turn signal specifications."""

    integrated: bool | None = None
    optional_kit: str | None = None


class Lights(BaseModel):
    """Lighting system specifications."""

    front: Light | None = None
    rear: Light | None = None
    turn_signals: TurnSignals | None = None


class Security(BaseModel):
    """Security features."""

    integrated_lock: str | None = None
    alarm: bool | None = None
    gps_tracker: bool | None = None


class Range(BaseModel):
    """Range estimates."""

    estimate_km: int | str | None = None
    eco_mode_km: int | None = None
    turbo_mode_km: int | None = None


class Price(BaseModel):
    """Price information."""

    amount: float | str | None = None
    currency: str | None = None
    region: str | None = None


class BikeSpecs(BaseModel):
    """Complete bike technical specifications.

    This represents the nested 'specs' object in the BIKE_SPECS_SCHEMA.
    """

    category: str | None = None
    model_year: int | None = None
    frame: Frame | None = None
    weight: Weight | None = None
    load_capacity: LoadCapacity | None = None
    motor: Motor | None = None
    battery: Battery | None = None
    drivetrain: Drivetrain | None = None
    brakes: Brakes | None = None
    wheels: Wheels | None = None
    suspension: Suspension | None = None
    lights: Lights | None = None
    security: Security | None = None
    features: list[str] | None = None
    range: Range | None = None
    price: Price | None = None
    notes: str | None = None


class Reseller(BaseModel):
    """Reseller information."""

    name: str
    url: str
    price: float | str | None = None
    currency: str | None = None
    region: str | None = None
    availability: str | None = None
    note: str | None = None


class BikeFrontmatter(BaseModel):
    """Top-level frontmatter for a bike note.

    This represents the complete YAML frontmatter structure for bike notes.
    """

    title: str
    type: str = Field(default="bike")
    brand: str | None = None
    model: str | None = None
    tags: list[str]
    date: str  # ISO 8601 format: YYYY-MM-DD
    url: str | None = None
    image: str | None = None
    resellers: list[Reseller] | None = None
    specs: BikeSpecs | None = None

    # Legacy fields (for backward compatibility)
    price: str | None = None
    motor: str | None = None
    battery: str | None = None
    range: str | None = None


class ValidationIssue(BaseModel):
    """A single validation issue."""

    field: str
    issue_type: str  # missing, invalid_type, invalid_format, deprecated
    message: str
    suggestion: str | None = None


class ValidationReport(BaseModel):
    """Report from schema validation."""

    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Conflict(BaseModel):
    """A detected conflict between old and new data."""

    field: str
    old_value: Any
    new_value: Any
    conflict_type: str  # minor, major, unresolvable
    description: str


class MergeResult(BaseModel):
    """Result of merging fetched data with existing note."""

    merged_frontmatter: dict
    conflicts: list[Conflict] = Field(default_factory=list)
    preserved_sections: list[str] = Field(default_factory=list)
    changes_made: dict = Field(default_factory=dict)


class UpdateResult(BaseModel):
    """Result of updating a single bike note."""

    success: bool
    bike_name: str
    note_path: str
    changes_made: dict = Field(default_factory=dict)
    conflicts: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    timestamp: str


class WriteResult(BaseModel):
    """Result of writing a note to disk."""

    success: bool
    path: str
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
