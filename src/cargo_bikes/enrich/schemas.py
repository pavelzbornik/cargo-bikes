"""Pydantic models for structured data extraction from vault notes.

Used with Claude's structured output (messages.parse) to extract
missing frontmatter fields from note body content.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BikeExtraction(BaseModel):
    """Fields to extract from a bike note body. All optional — only fill what's found."""

    category: str | None = Field(
        None, description="longtail, compact, box, trike, or midtail"
    )
    model_year: int | None = Field(None, description="Model year")
    motor_make: str | None = Field(
        None,
        description="Motor manufacturer: Bosch, Shimano, Bafang, Gaya, Specialized, Valeo",
    )
    motor_model: str | None = Field(None, description="Motor model name")
    motor_type: str | None = Field(None, description="mid-drive or hub")
    motor_power_w: int | None = Field(None, description="Motor power in watts")
    motor_torque_nm: int | None = Field(None, description="Motor torque in Nm")
    battery_capacity_wh: int | None = Field(None, description="Battery capacity in Wh")
    battery_removable: bool | None = Field(None, description="Is battery removable")
    battery_charging_time_h: str | None = Field(
        None, description="Charging time in hours"
    )
    weight_with_battery_kg: float | None = Field(
        None, description="Weight with battery in kg"
    )
    weight_bike_kg: float | None = Field(
        None, description="Weight without battery in kg"
    )
    load_capacity_total_kg: float | None = Field(
        None, description="Max total load capacity in kg"
    )
    load_capacity_passenger_count: int | None = Field(
        None, description="Number of passengers excluding rider"
    )
    price_amount: str | None = Field(
        None, description="Price as number string, no currency symbol"
    )
    price_currency: str | None = Field(None, description="EUR, USD, or GBP")
    range_estimate_km: str | None = Field(
        None, description="Range in km, can be '50-120'"
    )
    frame_material: str | None = Field(
        None, description="aluminum, steel, carbon, etc."
    )
    frame_length_cm: float | None = Field(None, description="Frame length in cm")
    brakes_type: str | None = Field(
        None, description="hydraulic disc, mechanical disc, etc."
    )
    drivetrain_type: str | None = Field(None, description="chain or belt")
    drivetrain_speeds: str | None = Field(
        None, description="Number of speeds as string"
    )
    drivetrain_hub: str | None = Field(None, description="Hub model if internal geared")
    wheels_front_size_in: str | None = Field(
        None, description="Front wheel size in inches"
    )
    wheels_rear_size_in: str | None = Field(
        None, description="Rear wheel size in inches"
    )
    wheels_tire: str | None = Field(None, description="Tire model name")
    suspension_front: str | None = Field(
        None, description="Front suspension type or 'none'"
    )
    suspension_rear: str | None = Field(
        None, description="Rear suspension type or 'none'"
    )


class BrandExtraction(BaseModel):
    """Fields to extract from a brand note body."""

    country: str | None = Field(None, description="Country where brand is based")
    headquarters_city: str | None = Field(None, description="City of headquarters")
    headquarters_country: str | None = Field(
        None, description="Country of headquarters"
    )
    founded_year: int | None = Field(None, description="Year founded")
    price_tier: str | None = Field(
        None, description="accessible, mid, premium, or ultra-premium"
    )
    categories: list[str] | str | None = Field(
        None, description="Bike types offered as list: ['longtail', 'compact']"
    )
    manufacturing_approach: str | None = Field(
        None, description="in-house, contracted, or hybrid"
    )
    assembly_location: str | None = Field(None, description="Where bikes are assembled")
    distribution_model: str | None = Field(None, description="direct, retail, or both")
