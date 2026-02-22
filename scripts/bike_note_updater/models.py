"""
Pydantic models for bike note data validation.

These models mirror the BIKE_SPECS_SCHEMA defined in docs/schema/BIKE_SPECS_SCHEMA.md
and provide strict type validation for all bike specification data flowing through
the research agent pipeline.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ==============================================================================
# SPECS SUB-MODELS
# ==============================================================================


class FrameDimensions(BaseModel):
    """Physical dimensions of the bike frame."""

    length_cm: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None


class Frame(BaseModel):
    """Frame specifications."""

    material: str | None = None
    size: str | None = None
    dimensions: FrameDimensions | None = None


class Weight(BaseModel):
    """Bike weight specifications."""

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


class Motor(BaseModel):
    """Motor specifications."""

    make: str | None = None
    model: str | None = None
    type: str | None = None
    power_w: float | str | None = None
    torque_nm: float | None = None
    boost_throttle: bool | None = None
    options: list[dict[str, object]] | None = None


class Battery(BaseModel):
    """Battery specifications."""

    capacity_wh: float | str | None = None
    configuration: str | None = None
    removable: bool | None = None
    charging_time_h: float | str | None = None


class Drivetrain(BaseModel):
    """Drivetrain specifications."""

    type: str | None = None
    speeds: str | int | None = None
    hub: str | None = None


class Brakes(BaseModel):
    """Brake specifications."""

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


class LightUnit(BaseModel):
    """Single light unit specification."""

    type: str | None = None
    integrated: bool | None = None
    powered_by: str | None = None
    brake_light: bool | None = None
    optional_kits: list[str] | None = None


class TurnSignals(BaseModel):
    """Turn signal specifications."""

    integrated: bool | None = None
    type: str | None = None
    left_right_buttons: bool | None = None


class Lights(BaseModel):
    """Complete lighting specifications."""

    front: LightUnit | None = None
    rear: LightUnit | None = None
    turn_signals: TurnSignals | None = None


class Security(BaseModel):
    """Security feature specifications."""

    gps: bool | None = None
    alarm_db: int | None = None
    app_lock: bool | None = None
    frame_lock: bool | None = None


class Range(BaseModel):
    """Range specifications."""

    estimate_km: str | float | None = None
    notes: str | None = None


class Price(BaseModel):
    """MSRP price specification."""

    amount: float | str | None = None
    currency: str | None = None


class BikeSpecs(BaseModel):
    """Complete bike specifications nested under the 'specs' key."""

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
    features: list[str] | None = None
    security: Security | None = None
    range: Range | None = Field(default=None)
    price: Price | None = None
    notes: str | None = None


# ==============================================================================
# TOP-LEVEL MODELS
# ==============================================================================


class ResellerEntry(BaseModel):
    """A reseller listing for a bike."""

    name: str
    url: str | None = None
    price: float | str | None = None
    currency: str | None = None
    region: str | None = None
    availability: str | None = None
    note: str | None = None


class BikeFrontmatter(BaseModel):
    """Complete frontmatter for a bike note file."""

    title: str
    type: str = "bike"
    brand: str | None = None
    model: str | None = None
    tags: list[str] | None = None
    date: str | None = None
    url: str | None = None
    image: str | None = None
    resellers: list[ResellerEntry] | None = None
    specs: BikeSpecs | None = None

    # Legacy fields (for backward compatibility during migration)
    price: str | None = None
    motor: str | None = None
    battery: str | None = None


# ==============================================================================
# AGENT RESULT MODELS
# ==============================================================================


class ValidationIssue(BaseModel):
    """A single validation issue found in a bike note."""

    field: str
    issue_type: str  # "missing", "invalid_type", "invalid_format", "deprecated"
    message: str
    suggestion: str | None = None


class ValidationReport(BaseModel):
    """Complete validation report for a bike note."""

    file_path: str
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    missing_required: list[str] = Field(default_factory=list)
    missing_recommended: list[str] = Field(default_factory=list)
    has_legacy_fields: bool = False
    specs_completeness: float = 0.0  # 0.0 to 1.0


class FetchedBikeData(BaseModel):
    """Data extracted from a manufacturer's product page."""

    source_url: str
    title: str | None = None
    brand: str | None = None
    model: str | None = None
    specs: BikeSpecs | None = None
    resellers: list[ResellerEntry] | None = None
    image_url: str | None = None
    raw_text: str | None = None
    extraction_method: str = "unknown"  # "json_ld", "microdata", "scraping", "llm"


class MergeConflict(BaseModel):
    """A conflict detected during data merging."""

    field: str
    old_value: object | None = None
    new_value: object | None = None
    severity: str = "minor"  # "minor", "major", "critical"
    resolution: str = "auto"  # "auto", "manual", "skipped"
    reason: str | None = None


class MergeResult(BaseModel):
    """Result of merging fetched data with an existing note."""

    merged_frontmatter: dict[str, object]
    conflicts: list[MergeConflict] = Field(default_factory=list)
    fields_updated: list[str] = Field(default_factory=list)
    fields_preserved: list[str] = Field(default_factory=list)


class UpdateResult(BaseModel):
    """Result of updating a single bike note."""

    success: bool
    bike_name: str
    note_path: str
    changes_made: list[str] = Field(default_factory=list)
    conflicts: list[MergeConflict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    validation_before: ValidationReport | None = None
    validation_after: ValidationReport | None = None


class BatchUpdateSummary(BaseModel):
    """Summary of a batch update operation."""

    total_processed: int = 0
    successful_updates: int = 0
    conflicts_flagged: int = 0
    errors: int = 0
    skipped: int = 0
    results: list[UpdateResult] = Field(default_factory=list)
