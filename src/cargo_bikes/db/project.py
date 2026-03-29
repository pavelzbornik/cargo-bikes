"""Projection script for updating Markdown files from the SQLite database.

Reads bike data from vault.db and updates corresponding Markdown files,
replacing YAML frontmatter and specs table within markers while
preserving all other manual content.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from cargo_bikes.db.schema import Bike, Brand

SPECS_TABLE_START_MARKER = "<!-- BIKE_SPECS_TABLE_START -->"
SPECS_TABLE_END_MARKER = "<!-- BIKE_SPECS_TABLE_END -->"


def find_bike_file(bike: Bike) -> Path | None:
    """Get the markdown file path for a bike record."""
    if not bike.file_path:
        return None
    file_path = Path(bike.file_path)
    if file_path.exists():
        return file_path
    return None


def parse_markdown_file(file_path: Path) -> dict[str, str]:
    """Parse a markdown file into constituent parts."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    result = {
        "frontmatter": "",
        "before_table": "",
        "table": "",
        "after_table": "",
    }

    if lines and lines[0].strip() == "---":
        try:
            end_idx = lines[1:].index("---") + 1
            result["frontmatter"] = "\n".join(lines[1:end_idx])
            body_start = end_idx + 2
        except ValueError:
            return result
    else:
        body_start = 0

    body = "\n".join(lines[body_start:])

    start_marker_match = re.search(
        re.escape(SPECS_TABLE_START_MARKER), body, re.MULTILINE
    )
    end_marker_match = re.search(re.escape(SPECS_TABLE_END_MARKER), body, re.MULTILINE)

    if start_marker_match and end_marker_match:
        start_pos = start_marker_match.start()
        end_pos = end_marker_match.end()
        result["before_table"] = body[:start_pos].rstrip()
        result["table"] = body[start_marker_match.end() : end_marker_match.start()]
        result["after_table"] = body[end_pos:].lstrip()
    else:
        result["before_table"] = body

    return result


# Fields managed by the DB projection — these get overwritten from DB values.
# Any frontmatter fields NOT in this set are preserved as-is.
_MANAGED_FIELDS = {
    "title", "type", "brand", "model", "tags", "url", "image", "resellers",
    "category", "model_year",
    "frame_material", "frame_size", "frame_length_cm", "frame_width_cm", "frame_height_cm",
    "weight_bike_kg", "weight_with_battery_kg", "weight_battery_kg",
    "load_capacity_total_kg", "load_capacity_rear_kg", "load_capacity_front_kg",
    "load_capacity_passenger_count", "load_capacity_passenger_config",
    "motor_make", "motor_model", "motor_type", "motor_power_w", "motor_torque_nm", "motor_boost_throttle",
    "battery_capacity_wh", "battery_configuration", "battery_removable", "battery_charging_time_h",
    "drivetrain_type", "drivetrain_speeds", "drivetrain_hub",
    "brakes_type", "brakes_front_rotor_mm", "brakes_rear_rotor_mm", "brakes_pistons",
    "wheels_front_size_in", "wheels_rear_size_in", "wheels_tire", "wheels_rims",
    "suspension_front", "suspension_rear",
    "lights_front_type", "lights_front_integrated", "lights_front_powered_by",
    "lights_rear_type", "lights_rear_integrated", "lights_rear_brake_light",
    "lights_turn_signals_integrated", "lights_turn_signals_type",
    "features",
    "security_gps", "security_alarm_db", "security_app_lock", "security_frame_lock",
    "range_estimate_km", "range_notes",
    "price_amount", "price_currency",
    "specs_notes",
    # Legacy nested keys to remove during migration
    "specs",
}


def generate_frontmatter(bike: Bike, existing: dict[str, Any] | None = None) -> str:
    """Generate YAML frontmatter from a bike DB record.

    If existing frontmatter is provided, merges DB fields into it,
    preserving any non-managed fields (date, review_*, components, etc.).
    Also removes the legacy nested 'specs' key.
    """
    # Start with existing frontmatter or empty dict
    if existing:
        data: dict[str, Any] = {}
        # Preserve non-managed fields in original order
        for key, value in existing.items():
            if key not in _MANAGED_FIELDS:
                data[key] = value
    else:
        data = {}

    # Always set identity fields first
    data["title"] = bike.title
    data["type"] = "bike"

    if bike.brand_name:
        data["brand"] = bike.brand_name
    if bike.model:
        data["model"] = bike.model
    if bike.tags:
        tag_list = [t.strip() for t in bike.tags.split(",")]
        data["tags"] = tag_list
    if bike.url:
        data["url"] = bike.url
    if bike.image:
        data["image"] = bike.image

    if bike.resellers:
        resellers = []
        for reseller in bike.resellers:
            reseller_data: dict[str, Any] = {"name": reseller.name}
            if reseller.url:
                reseller_data["url"] = reseller.url
            if reseller.price:
                reseller_data["price"] = reseller.price
            if reseller.currency:
                reseller_data["currency"] = reseller.currency
            if reseller.region:
                reseller_data["region"] = reseller.region
            if reseller.availability:
                reseller_data["availability"] = reseller.availability
            if reseller.note:
                reseller_data["note"] = reseller.note
            resellers.append(reseller_data)
        data["resellers"] = resellers

    # Flat spec fields — no nesting, directly queryable by Obsidian Bases
    # Classification
    if bike.category:
        data["category"] = bike.category
    if bike.model_year:
        data["model_year"] = bike.model_year

    # Frame
    if bike.frame_material:
        data["frame_material"] = bike.frame_material
    if bike.frame_size:
        data["frame_size"] = bike.frame_size
    if bike.frame_length_cm:
        data["frame_length_cm"] = bike.frame_length_cm
    if bike.frame_width_cm:
        data["frame_width_cm"] = bike.frame_width_cm
    if bike.frame_height_cm:
        data["frame_height_cm"] = bike.frame_height_cm

    # Weight
    if bike.weight_bike_kg:
        data["weight_bike_kg"] = bike.weight_bike_kg
    if bike.weight_with_battery_kg:
        data["weight_with_battery_kg"] = bike.weight_with_battery_kg
    if bike.weight_battery_kg:
        data["weight_battery_kg"] = bike.weight_battery_kg

    # Load capacity
    if bike.load_capacity_total_kg:
        data["load_capacity_total_kg"] = bike.load_capacity_total_kg
    if bike.load_capacity_rear_kg:
        data["load_capacity_rear_kg"] = bike.load_capacity_rear_kg
    if bike.load_capacity_front_kg:
        data["load_capacity_front_kg"] = bike.load_capacity_front_kg
    if bike.load_capacity_passenger_count:
        data["load_capacity_passenger_count"] = bike.load_capacity_passenger_count
    if bike.load_capacity_passenger_config:
        data["load_capacity_passenger_config"] = bike.load_capacity_passenger_config

    # Motor
    if bike.motor_make:
        data["motor_make"] = bike.motor_make
    if bike.motor_model:
        data["motor_model"] = bike.motor_model
    if bike.motor_type:
        data["motor_type"] = bike.motor_type
    if bike.motor_power_w:
        data["motor_power_w"] = int(bike.motor_power_w)
    if bike.motor_torque_nm:
        data["motor_torque_nm"] = int(bike.motor_torque_nm)
    if bike.motor_boost_throttle is not None:
        data["motor_boost_throttle"] = bike.motor_boost_throttle

    # Battery
    if bike.battery_capacity_wh:
        data["battery_capacity_wh"] = int(bike.battery_capacity_wh)
    if bike.battery_configuration:
        data["battery_configuration"] = bike.battery_configuration
    if bike.battery_removable is not None:
        data["battery_removable"] = bike.battery_removable
    if bike.battery_charging_time_h:
        data["battery_charging_time_h"] = bike.battery_charging_time_h

    # Drivetrain
    if bike.drivetrain_type:
        data["drivetrain_type"] = bike.drivetrain_type
    if bike.drivetrain_speeds:
        data["drivetrain_speeds"] = bike.drivetrain_speeds
    if bike.drivetrain_hub:
        data["drivetrain_hub"] = bike.drivetrain_hub

    # Brakes
    if bike.brakes_type:
        data["brakes_type"] = bike.brakes_type
    if bike.brakes_front_rotor_mm:
        data["brakes_front_rotor_mm"] = bike.brakes_front_rotor_mm
    if bike.brakes_rear_rotor_mm:
        data["brakes_rear_rotor_mm"] = bike.brakes_rear_rotor_mm
    if bike.brakes_pistons:
        data["brakes_pistons"] = bike.brakes_pistons

    # Wheels
    if bike.wheels_front_size_in:
        data["wheels_front_size_in"] = bike.wheels_front_size_in
    if bike.wheels_rear_size_in:
        data["wheels_rear_size_in"] = bike.wheels_rear_size_in
    if bike.wheels_tire:
        data["wheels_tire"] = bike.wheels_tire
    if bike.wheels_rims:
        data["wheels_rims"] = bike.wheels_rims

    # Suspension
    if bike.suspension_front:
        data["suspension_front"] = bike.suspension_front
    if bike.suspension_rear:
        data["suspension_rear"] = bike.suspension_rear

    # Lights
    if bike.lights_front_type:
        data["lights_front_type"] = bike.lights_front_type
    if bike.lights_front_integrated is not None:
        data["lights_front_integrated"] = bike.lights_front_integrated
    if bike.lights_front_powered_by:
        data["lights_front_powered_by"] = bike.lights_front_powered_by
    if bike.lights_rear_type:
        data["lights_rear_type"] = bike.lights_rear_type
    if bike.lights_rear_integrated is not None:
        data["lights_rear_integrated"] = bike.lights_rear_integrated
    if bike.lights_rear_brake_light is not None:
        data["lights_rear_brake_light"] = bike.lights_rear_brake_light
    if bike.lights_turn_signals_integrated is not None:
        data["lights_turn_signals_integrated"] = bike.lights_turn_signals_integrated
    if bike.lights_turn_signals_type:
        data["lights_turn_signals_type"] = bike.lights_turn_signals_type

    # Features
    if bike.features:
        data["features"] = [f.strip() for f in bike.features.split(",")]

    # Security
    if bike.security_gps is not None:
        data["security_gps"] = bike.security_gps
    if bike.security_alarm_db:
        data["security_alarm_db"] = bike.security_alarm_db
    if bike.security_app_lock is not None:
        data["security_app_lock"] = bike.security_app_lock
    if bike.security_frame_lock is not None:
        data["security_frame_lock"] = bike.security_frame_lock

    # Range
    if bike.range_estimate_km:
        data["range_estimate_km"] = bike.range_estimate_km
    if bike.range_notes:
        data["range_notes"] = bike.range_notes

    # Price
    if bike.price_amount:
        data["price_amount"] = bike.price_amount
    if bike.price_currency:
        data["price_currency"] = bike.price_currency

    # Notes
    if bike.specs_notes:
        data["specs_notes"] = bike.specs_notes

    yaml_str = yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    return yaml_str.rstrip() + "\n"


def generate_specs_table(bike: Bike) -> str:
    """Generate a Markdown specifications table from a bike database record."""
    rows = []

    if bike.category:
        rows.append(f"| **Category** | {bike.category} |")
    if bike.model_year:
        rows.append(f"| **Model Year** | {bike.model_year} |")

    if bike.motor_make or bike.motor_model:
        motor_str = bike.motor_make or ""
        if bike.motor_model:
            motor_str += f" {bike.motor_model}" if motor_str else bike.motor_model
        rows.append(f"| **Motor** | {motor_str} |")
    if bike.motor_power_w:
        rows.append(f"| **Motor Power** | {int(bike.motor_power_w)}W |")
    if bike.motor_torque_nm:
        rows.append(f"| **Motor Torque** | {int(bike.motor_torque_nm)}Nm |")

    if bike.battery_capacity_wh:
        rows.append(f"| **Battery Capacity** | {int(bike.battery_capacity_wh)}Wh |")
    if bike.range_estimate_km:
        rows.append(f"| **Range** | {bike.range_estimate_km} km |")

    if bike.weight_with_battery_kg:
        rows.append(f"| **Weight (with battery)** | {bike.weight_with_battery_kg}kg |")
    if bike.load_capacity_total_kg:
        rows.append(f"| **Total Load Capacity** | {bike.load_capacity_total_kg}kg |")

    if bike.drivetrain_type:
        rows.append(f"| **Drivetrain** | {bike.drivetrain_type} |")
    if bike.brakes_type:
        rows.append(f"| **Brakes** | {bike.brakes_type} |")

    if bike.wheels_front_size_in or bike.wheels_rear_size_in:
        wheel_str = ""
        if bike.wheels_front_size_in == bike.wheels_rear_size_in:
            wheel_str = bike.wheels_front_size_in or ""
        else:
            if bike.wheels_front_size_in:
                wheel_str = f"Front: {bike.wheels_front_size_in}"
            if bike.wheels_rear_size_in:
                wheel_str += (
                    f", Rear: {bike.wheels_rear_size_in}"
                    if wheel_str
                    else f"Rear: {bike.wheels_rear_size_in}"
                )
        if wheel_str:
            rows.append(f"| **Wheel Size** | {wheel_str} |")

    if bike.price_amount and bike.price_currency:
        rows.append(f"| **Price** | {bike.price_amount} {bike.price_currency} |")

    if not rows:
        return ""

    table = "| Specification | Value |\n"
    table += "|---------------|-------|\n"
    table += "\n".join(rows)

    return table


def reconstruct_markdown_file(
    parts: dict[str, str], new_frontmatter: str, new_table: str
) -> str:
    """Reconstruct a markdown file with updated frontmatter and specs table."""
    sections = []

    sections.append("---")
    sections.append(new_frontmatter)
    sections.append("---")
    sections.append("")

    if parts["before_table"]:
        before_content = parts["before_table"].rstrip()
        if before_content:
            sections.append(before_content)
            sections.append("")

    sections.append(SPECS_TABLE_START_MARKER)
    if new_table:
        sections.append(new_table)
    sections.append(SPECS_TABLE_END_MARKER)

    if parts["after_table"]:
        after_content = parts["after_table"].lstrip()
        if after_content:
            sections.append("")
            sections.append(after_content)

    content = "\n".join(sections)
    return content.rstrip() + "\n"


def project_bike_to_file(bike: Bike, dry_run: bool = False) -> tuple[bool, str]:
    """Project a bike record to its markdown file."""
    file_path = find_bike_file(bike)
    if not file_path:
        return False, f"Could not find file for bike: {bike.title}"

    try:
        parts = parse_markdown_file(file_path)
    except Exception as e:
        return False, f"Failed to parse file {file_path}: {e}"

    # Parse existing frontmatter to preserve non-managed fields
    existing_fm = None
    if parts["frontmatter"]:
        try:
            existing_fm = yaml.safe_load(parts["frontmatter"])
            if not isinstance(existing_fm, dict):
                existing_fm = None
        except yaml.YAMLError:
            existing_fm = None

    try:
        new_frontmatter = generate_frontmatter(bike, existing=existing_fm)
        new_table = generate_specs_table(bike)
    except Exception as e:
        return False, f"Failed to generate content for {bike.title}: {e}"

    try:
        new_content = reconstruct_markdown_file(parts, new_frontmatter, new_table)
    except Exception as e:
        return False, f"Failed to reconstruct file for {bike.title}: {e}"

    if not dry_run:
        try:
            file_path.write_text(new_content, encoding="utf-8")
        except Exception as e:
            return False, f"Failed to write file {file_path}: {e}"

    return True, f"Updated: {file_path}"


def project_all_bikes(
    session: Session, dry_run: bool = False, bike_id: int | None = None
) -> tuple[int, int]:
    """Project all (or one) bike records to markdown files.

    Returns:
        Tuple of (success_count, fail_count).
    """
    if bike_id:
        stmt = select(Bike).where(Bike.id == bike_id)
        bike_or_none = session.execute(stmt).scalar_one_or_none()
        if not bike_or_none:
            print(f"✗ Bike with ID {bike_id} not found")
            return 0, 1
        bikes: list[Bike] = [bike_or_none]
    else:
        stmt = select(Bike).order_by(Bike.brand_name, Bike.title)
        bikes = list(session.execute(stmt).scalars().all())

    if not bikes:
        print("No bikes found in database")
        return 0, 0

    print(f"Processing {len(bikes)} bike(s)...\n")

    success_count = 0
    fail_count = 0

    for bike in bikes:
        success, message = project_bike_to_file(bike, dry_run)
        if success:
            print(f"✓ {message}")
            success_count += 1
        else:
            print(f"✗ {message}")
            fail_count += 1

    return success_count, fail_count


# ============================================================================
# Brand projection
# ============================================================================

# Fields managed by brand projection — nested keys get removed
_BRAND_MANAGED_FIELDS = {
    "title", "type", "url", "logo", "summary", "tags",
    "founded_year", "country",
    "headquarters", "headquarters_city", "headquarters_country", "headquarters_address",
    "categories", "market_segments", "regions", "price_tier",
    "product_types", "model_count", "primary_motors", "parent_company",
    "manufacturing", "manufacturing_locations", "manufacturing_approach",
    "assembly_location", "ethical_standards",
    "distribution_model", "regions_active", "direct_sales", "dealership_network",
    "impact", "impact_bikes_sold_approx", "impact_km_driven_approx",
    "impact_co2_avoided_kg_approx", "impact_families_served",
    "values", "value_sustainability", "value_local_manufacturing",
    "value_community_focus", "value_safety_emphasis", "value_tech_integration",
    "accessibility",
}


def generate_brand_frontmatter(brand: Brand, existing: dict[str, Any] | None = None) -> str:
    """Generate flat YAML frontmatter from a Brand DB record."""
    if existing:
        data: dict[str, Any] = {}
        for key, value in existing.items():
            if key not in _BRAND_MANAGED_FIELDS:
                data[key] = value
    else:
        data = {}

    data["title"] = brand.title
    data["type"] = brand.type or "brand"

    if brand.url:
        data["url"] = brand.url
    if brand.logo:
        data["logo"] = brand.logo
    if brand.summary:
        data["summary"] = brand.summary
    if brand.tags:
        data["tags"] = [t.strip() for t in brand.tags.split(",")]

    if brand.founded_year:
        data["founded_year"] = brand.founded_year
    if brand.country:
        data["country"] = brand.country

    # Headquarters — flat
    if brand.headquarters_city:
        data["headquarters_city"] = brand.headquarters_city
    if brand.headquarters_country:
        data["headquarters_country"] = brand.headquarters_country
    if brand.headquarters_address:
        data["headquarters_address"] = brand.headquarters_address

    if brand.categories:
        data["categories"] = [c.strip() for c in brand.categories.split(",")]
    if brand.market_segments:
        data["market_segments"] = [s.strip() for s in brand.market_segments.split(",")]
    if brand.regions:
        data["regions"] = [r.strip() for r in brand.regions.split(",")]
    if brand.price_tier:
        data["price_tier"] = brand.price_tier

    if brand.product_types:
        data["product_types"] = [p.strip() for p in brand.product_types.split(",")]
    if brand.model_count:
        data["model_count"] = brand.model_count
    if brand.primary_motors:
        data["primary_motors"] = [m.strip() for m in brand.primary_motors.split(",")]
    if brand.parent_company:
        data["parent_company"] = brand.parent_company

    # Manufacturing — flat
    if brand.manufacturing_locations:
        data["manufacturing_locations"] = [l.strip() for l in brand.manufacturing_locations.split(",")]
    if brand.manufacturing_approach:
        data["manufacturing_approach"] = brand.manufacturing_approach
    if brand.assembly_location:
        data["assembly_location"] = brand.assembly_location
    if brand.ethical_standards:
        data["ethical_standards"] = brand.ethical_standards

    if brand.distribution_model:
        data["distribution_model"] = brand.distribution_model
    if brand.regions_active:
        data["regions_active"] = [r.strip() for r in brand.regions_active.split(",")]
    if brand.direct_sales is not None:
        data["direct_sales"] = brand.direct_sales
    if brand.dealership_network is not None:
        data["dealership_network"] = brand.dealership_network

    # Impact — flat
    if brand.impact_bikes_sold_approx:
        data["impact_bikes_sold_approx"] = brand.impact_bikes_sold_approx
    if brand.impact_km_driven_approx:
        data["impact_km_driven_approx"] = brand.impact_km_driven_approx
    if brand.impact_co2_avoided_kg_approx:
        data["impact_co2_avoided_kg_approx"] = brand.impact_co2_avoided_kg_approx
    if brand.impact_families_served:
        data["impact_families_served"] = brand.impact_families_served

    # Values — flat
    if brand.value_sustainability is not None:
        data["value_sustainability"] = brand.value_sustainability
    if brand.value_local_manufacturing is not None:
        data["value_local_manufacturing"] = brand.value_local_manufacturing
    if brand.value_community_focus is not None:
        data["value_community_focus"] = brand.value_community_focus
    if brand.value_safety_emphasis is not None:
        data["value_safety_emphasis"] = brand.value_safety_emphasis
    if brand.value_tech_integration is not None:
        data["value_tech_integration"] = brand.value_tech_integration

    if brand.accessibility:
        data["accessibility"] = [a.strip() for a in brand.accessibility.split(",")]

    yaml_str = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False,
    )
    return yaml_str.rstrip() + "\n"


def _find_brand_file(brand: Brand, vault_path: Path) -> Path | None:
    """Find the index.md file for a brand."""
    # Try common slug patterns
    title_slug = brand.title.lower().replace(" ", "-").replace("'", "")
    bikes_dir = vault_path / "notes" / "bikes"

    for candidate in [
        bikes_dir / title_slug / "index.md",
    ]:
        if candidate.exists():
            return candidate

    # Scan all brand dirs for matching title
    for brand_dir in bikes_dir.iterdir():
        if not brand_dir.is_dir():
            continue
        index_file = brand_dir / "index.md"
        if index_file.exists():
            try:
                content = index_file.read_text(encoding="utf-8")
                import re as _re
                title_match = _re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, _re.MULTILINE)
                if title_match and title_match.group(1).strip() == brand.title:
                    return index_file
            except Exception:
                continue

    return None


def project_brand_to_file(
    brand: Brand, vault_path: Path, dry_run: bool = False
) -> tuple[bool, str]:
    """Project a brand record to its markdown file."""
    file_path = _find_brand_file(brand, vault_path)
    if not file_path:
        return False, f"No index.md found for brand: {brand.title}"

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Failed to read {file_path}: {e}"

    # Parse existing frontmatter
    import re as _re
    fm_match = _re.match(r"^---\s*\n(.*?)\n---\s*\n", content, _re.DOTALL)
    existing_fm = None
    body = content
    if fm_match:
        try:
            existing_fm = yaml.safe_load(fm_match.group(1))
            if not isinstance(existing_fm, dict):
                existing_fm = None
        except yaml.YAMLError:
            existing_fm = None
        body = content[fm_match.end():]

    new_frontmatter = generate_brand_frontmatter(brand, existing=existing_fm)
    new_content = f"---\n{new_frontmatter}---\n{body}"

    if not dry_run:
        file_path.write_text(new_content, encoding="utf-8")

    return True, f"Updated: {file_path}"


def project_all_brands(
    session: Session, vault_path: Path, dry_run: bool = False
) -> tuple[int, int]:
    """Project all brand records to their markdown files."""
    brands = list(session.execute(select(Brand).order_by(Brand.title)).scalars().all())

    if not brands:
        print("No brands found in database")
        return 0, 0

    print(f"Processing {len(brands)} brand(s)...\n")

    success_count = 0
    fail_count = 0

    for brand in brands:
        success, message = project_brand_to_file(brand, vault_path, dry_run)
        if success:
            print(f"✓ {message}")
            success_count += 1
        else:
            print(f"✗ {message}")
            fail_count += 1

    return success_count, fail_count
