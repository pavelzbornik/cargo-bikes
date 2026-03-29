"""Hydration script for populating the SQLite database from Markdown files.

Reads YAML frontmatter from all valid Markdown files in vault/notes/
and populates the SQLite database with structured data. Performs
idempotent upserts to avoid duplicate records.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cargo_bikes.db.schema import Base, Bike, Brand, Reseller
from cargo_bikes.validate.structure import validate_vault
from cargo_bikes.vault.frontmatter import extract_frontmatter_from_file


def run_linter(vault_path: Path) -> bool:
    """Run the structural linter to validate all markdown files.

    Args:
        vault_path: Path to the vault/notes directory.

    Returns:
        True if linter passes, False if validation fails.
    """
    print("Running structural linter...")
    errors = validate_vault(vault_path)
    if errors:
        print(f"\n✗ Found {len(errors)} validation error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return False
    print("✓ All markdown files are valid!")
    return True


def parse_date(date_value: Any) -> date | None:
    """Parse a date value from frontmatter."""
    if isinstance(date_value, date):
        return date_value
    if isinstance(date_value, datetime):
        return date_value.date()
    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            pass
    return None


def parse_tags(tags_value: Any) -> str | None:
    """Parse tags from frontmatter and convert to comma-separated string."""
    if isinstance(tags_value, list):
        return ",".join(str(tag).strip() for tag in tags_value)
    elif isinstance(tags_value, str):
        return tags_value
    return None


def upsert_brand(
    session: Session, frontmatter: dict[str, Any], file_path: Path
) -> Brand | None:
    """Insert or update a brand record."""
    note_type = frontmatter.get("type")
    if note_type not in ["brand", "manufacturer", "brand-index"]:
        return None

    title = frontmatter.get("title")
    if not title:
        return None

    stmt = select(Brand).where(Brand.title == title)
    existing_brand = session.execute(stmt).scalar_one_or_none()

    if existing_brand:
        brand = existing_brand
    else:
        brand = Brand(title=title, type=note_type)
        session.add(brand)

    brand.date = parse_date(frontmatter.get("date")) or date.today()
    brand.url = frontmatter.get("url")
    brand.logo = frontmatter.get("logo")
    brand.summary = frontmatter.get("summary")
    brand.tags = parse_tags(frontmatter.get("tags"))

    brand.founded_year = frontmatter.get("founded_year")
    brand.country = frontmatter.get("country")

    # Headquarters: flat first, nested fallback
    hq = frontmatter.get("headquarters") if isinstance(frontmatter.get("headquarters"), dict) else {}
    brand.headquarters_city = frontmatter.get("headquarters_city") or hq.get("city")
    brand.headquarters_country = frontmatter.get("headquarters_country") or hq.get("country")
    brand.headquarters_address = frontmatter.get("headquarters_address") or hq.get("address")

    brand.categories = parse_tags(frontmatter.get("categories"))
    brand.market_segments = parse_tags(frontmatter.get("market_segments"))
    brand.regions = parse_tags(frontmatter.get("regions"))
    brand.price_tier = frontmatter.get("price_tier")

    brand.product_types = parse_tags(frontmatter.get("product_types"))
    brand.model_count = frontmatter.get("model_count")
    brand.primary_motors = parse_tags(frontmatter.get("primary_motors"))
    brand.parent_company = frontmatter.get("parent_company")

    # Manufacturing: flat first, nested fallback
    mfg = frontmatter.get("manufacturing") if isinstance(frontmatter.get("manufacturing"), dict) else {}
    brand.manufacturing_locations = parse_tags(
        frontmatter.get("manufacturing_locations") or mfg.get("locations")
    )
    brand.manufacturing_approach = frontmatter.get("manufacturing_approach") or mfg.get("approach")
    brand.assembly_location = frontmatter.get("assembly_location") or mfg.get("assembly_location")
    brand.ethical_standards = frontmatter.get("ethical_standards") or mfg.get("ethical_standards")

    brand.distribution_model = frontmatter.get("distribution_model")
    brand.regions_active = parse_tags(frontmatter.get("regions_active"))
    brand.direct_sales = frontmatter.get("direct_sales")
    brand.dealership_network = frontmatter.get("dealership_network")

    # Impact: flat first, nested fallback
    impact = frontmatter.get("impact") if isinstance(frontmatter.get("impact"), dict) else {}
    brand.impact_bikes_sold_approx = frontmatter.get("impact_bikes_sold_approx") or impact.get("bikes_sold_approx")
    brand.impact_km_driven_approx = frontmatter.get("impact_km_driven_approx") or impact.get("km_driven_approx")
    brand.impact_co2_avoided_kg_approx = frontmatter.get("impact_co2_avoided_kg_approx") or impact.get("co2_avoided_kg_approx")
    brand.impact_families_served = frontmatter.get("impact_families_served") or impact.get("families_served")

    # Values: flat first, nested fallback
    vals = frontmatter.get("values") if isinstance(frontmatter.get("values"), dict) else {}
    brand.value_sustainability = frontmatter.get("value_sustainability") if frontmatter.get("value_sustainability") is not None else vals.get("sustainability")
    brand.value_local_manufacturing = frontmatter.get("value_local_manufacturing") if frontmatter.get("value_local_manufacturing") is not None else vals.get("local_manufacturing")
    brand.value_community_focus = frontmatter.get("value_community_focus") if frontmatter.get("value_community_focus") is not None else vals.get("community_focus")
    brand.value_safety_emphasis = frontmatter.get("value_safety_emphasis") if frontmatter.get("value_safety_emphasis") is not None else vals.get("safety_emphasis")
    brand.value_tech_integration = frontmatter.get("value_tech_integration") if frontmatter.get("value_tech_integration") is not None else vals.get("tech_integration")

    brand.accessibility = parse_tags(frontmatter.get("accessibility"))

    return brand


def get_or_create_brand(session: Session, brand_name: str) -> Brand | None:
    """Get existing brand or create a placeholder."""
    if not brand_name:
        return None

    stmt = select(Brand).where(Brand.title == brand_name)
    brand = session.execute(stmt).scalar_one_or_none()

    if not brand:
        brand = Brand(title=brand_name, type="brand", date=date.today())
        session.add(brand)

    return brand


def get_relative_file_path(file_path: Path) -> str:
    """Get file path relative to workspace root with fallback handling."""
    try:
        return str(file_path.relative_to(Path.cwd()))
    except ValueError:
        pass

    try:
        return str(file_path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(file_path.resolve())


def upsert_bike(
    session: Session, frontmatter: dict[str, Any], file_path: Path
) -> Bike | None:
    """Insert or update a bike record."""
    if frontmatter.get("type") != "bike":
        return None

    title = frontmatter.get("title")
    if not title:
        return None

    brand_name = frontmatter.get("brand")
    stmt = select(Bike).where(Bike.title == title, Bike.brand_name == brand_name)
    existing_bike = session.execute(stmt).scalar_one_or_none()

    if existing_bike:
        bike = existing_bike
    else:
        bike = Bike(title=title)
        session.add(bike)

    bike.type = "bike"
    bike.brand_name = brand_name
    bike.model = frontmatter.get("model")
    bike.tags = parse_tags(frontmatter.get("tags"))
    bike.url = frontmatter.get("url")
    bike.image = frontmatter.get("image")
    bike.file_path = get_relative_file_path(file_path)

    if brand_name:
        brand = get_or_create_brand(session, brand_name)
        bike.brand = brand

    # Read flat fields first, fall back to nested specs, then legacy top-level
    specs = frontmatter.get("specs") or {}

    def _get(flat_key: str, *nested_keys: str) -> Any:
        """Read flat top-level field, fall back to nested specs path."""
        val = frontmatter.get(flat_key)
        if val is not None:
            return val
        obj = specs
        for k in nested_keys:
            if isinstance(obj, dict):
                obj = obj.get(k)
            else:
                return None
        return obj

    # --- Parse legacy top-level fields (motor, battery, price, range) ---
    def _parse_legacy_motor() -> None:
        """Parse legacy 'motor: 85Nm Bosch Cargo Line' into DB fields."""
        if bike.motor_make or bike.motor_power_w:
            return  # Already set from flat/nested
        legacy = frontmatter.get("motor")
        if not legacy or not isinstance(legacy, str):
            return
        import re
        # Extract power: "250W" or "250w"
        power_match = re.search(r"(\d+)\s*[Ww]", legacy)
        if power_match:
            bike.motor_power_w = float(power_match.group(1))
        # Extract torque: "85Nm" or "85nm"
        torque_match = re.search(r"(\d+)\s*[Nn]m", legacy)
        if torque_match:
            bike.motor_torque_nm = float(torque_match.group(1))
        # Extract make: known brands
        for brand in ["Bosch", "Shimano", "Bafang", "Gaya", "Specialized", "Valéo", "Ananda", "Naka"]:
            if brand.lower() in legacy.lower():
                bike.motor_make = brand
                # Everything after the brand is the model
                idx = legacy.lower().find(brand.lower())
                model_part = legacy[idx + len(brand):].strip()
                if model_part:
                    bike.motor_model = model_part
                break

    def _parse_legacy_battery() -> None:
        """Parse legacy 'battery: 545Wh' into DB fields."""
        if bike.battery_capacity_wh:
            return
        legacy = frontmatter.get("battery")
        if not legacy or not isinstance(legacy, str):
            return
        import re
        wh_match = re.search(r"(\d+)\s*[Ww]h", legacy)
        if wh_match:
            bike.battery_capacity_wh = float(wh_match.group(1))

    def _parse_legacy_price() -> None:
        """Parse legacy 'price: €2,990' or 'price: 5999' into DB fields."""
        if bike.price_amount:
            return
        legacy = frontmatter.get("price")
        if not legacy:
            return
        legacy_str = str(legacy)
        if not legacy_str or legacy_str in ("''", '""', "N/A", "TBD"):
            return
        import re
        # Detect currency
        if "€" in legacy_str or "EUR" in legacy_str.upper():
            bike.price_currency = "EUR"
        elif "$" in legacy_str or "USD" in legacy_str.upper():
            bike.price_currency = "USD"
        # Extract number (handle 5999, €2,990, €6,340, etc.)
        nums = re.findall(r"[\d.,]+", legacy_str)
        if nums:
            num_str = nums[0].replace(",", "")
            try:
                bike.price_amount = str(int(float(num_str)))
            except ValueError:
                bike.price_amount = legacy_str

    def _parse_legacy_range() -> None:
        """Parse legacy 'range: 45-196km' into DB fields."""
        if bike.range_estimate_km:
            return
        legacy = frontmatter.get("range")
        if not legacy or not isinstance(legacy, str):
            return
        if legacy.lower() in ("", "n/a", "variable", "unknown"):
            return
        import re
        km_match = re.search(r"([\d][\d\-–]*)\s*km", legacy, re.IGNORECASE)
        if km_match:
            bike.range_estimate_km = km_match.group(1)

    bike.category = _get("category", "category")
    bike.model_year = _get("model_year", "model_year")

    bike.frame_material = _get("frame_material", "frame", "material")
    bike.frame_size = _get("frame_size", "frame", "size")
    bike.frame_length_cm = _get("frame_length_cm", "frame", "dimensions", "length_cm")
    bike.frame_width_cm = _get("frame_width_cm", "frame", "dimensions", "width_cm")
    bike.frame_height_cm = _get("frame_height_cm", "frame", "dimensions", "height_cm")

    bike.weight_bike_kg = _get("weight_bike_kg", "weight", "bike_kg")
    bike.weight_with_battery_kg = _get("weight_with_battery_kg", "weight", "with_battery_kg")
    bike.weight_battery_kg = _get("weight_battery_kg", "weight", "battery_kg")

    bike.load_capacity_total_kg = _get("load_capacity_total_kg", "load_capacity", "total_kg")
    bike.load_capacity_rear_kg = _get("load_capacity_rear_kg", "load_capacity", "rear_kg")
    bike.load_capacity_front_kg = _get("load_capacity_front_kg", "load_capacity", "front_kg")
    bike.load_capacity_passenger_count = _get(
        "load_capacity_passenger_count", "load_capacity", "passenger_count_excluding_rider"
    )
    bike.load_capacity_passenger_config = _get(
        "load_capacity_passenger_config", "load_capacity", "passenger_config"
    )

    bike.motor_make = _get("motor_make", "motor", "make")
    bike.motor_model = _get("motor_model", "motor", "model")
    bike.motor_type = _get("motor_type", "motor", "type")

    power_w = _get("motor_power_w", "motor", "power_w")
    if isinstance(power_w, (int, float)):
        bike.motor_power_w = float(power_w)
    elif isinstance(power_w, str):
        try:
            power_w_clean = power_w.replace("W", "").replace("w", "").strip()
            if "-" in power_w_clean:
                parts = power_w_clean.split("-")
                bike.motor_power_w = float(parts[0].strip())
            else:
                bike.motor_power_w = float(power_w_clean)
        except (ValueError, IndexError):
            bike.motor_power_w = None
    else:
        bike.motor_power_w = None

    bike.motor_torque_nm = _get("motor_torque_nm", "motor", "torque_nm")
    bike.motor_boost_throttle = _get("motor_boost_throttle", "motor", "boost_throttle")

    capacity_wh = _get("battery_capacity_wh", "battery", "capacity_wh")
    if isinstance(capacity_wh, (int, float)):
        bike.battery_capacity_wh = float(capacity_wh)
    elif isinstance(capacity_wh, str):
        try:
            if "-" in capacity_wh:
                parts = capacity_wh.split("-")
                bike.battery_capacity_wh = float(parts[0].strip())
            else:
                bike.battery_capacity_wh = float(capacity_wh)
        except (ValueError, IndexError):
            bike.battery_capacity_wh = None
    else:
        bike.battery_capacity_wh = None

    bike.battery_configuration = _get("battery_configuration", "battery", "configuration")
    bike.battery_removable = _get("battery_removable", "battery", "removable")
    charging = _get("battery_charging_time_h", "battery", "charging_time_h")
    bike.battery_charging_time_h = str(charging) if charging else None

    bike.drivetrain_type = _get("drivetrain_type", "drivetrain", "type")
    speeds = _get("drivetrain_speeds", "drivetrain", "speeds")
    bike.drivetrain_speeds = str(speeds) if speeds else None
    bike.drivetrain_hub = _get("drivetrain_hub", "drivetrain", "hub")

    bike.brakes_type = _get("brakes_type", "brakes", "type")
    bike.brakes_front_rotor_mm = _get("brakes_front_rotor_mm", "brakes", "front_rotor_mm")
    bike.brakes_rear_rotor_mm = _get("brakes_rear_rotor_mm", "brakes", "rear_rotor_mm")
    pistons = _get("brakes_pistons", "brakes", "pistons")
    bike.brakes_pistons = str(pistons) if pistons else None

    bike.wheels_front_size_in = _get("wheels_front_size_in", "wheels", "front_size_in")
    bike.wheels_rear_size_in = _get("wheels_rear_size_in", "wheels", "rear_size_in")
    bike.wheels_tire = _get("wheels_tire", "wheels", "tire")
    bike.wheels_rims = _get("wheels_rims", "wheels", "rims")

    bike.suspension_front = _get("suspension_front", "suspension", "front")
    bike.suspension_rear = _get("suspension_rear", "suspension", "rear")

    bike.lights_front_type = _get("lights_front_type", "lights", "front", "type")
    bike.lights_front_integrated = _get("lights_front_integrated", "lights", "front", "integrated")
    bike.lights_front_powered_by = _get("lights_front_powered_by", "lights", "front", "powered_by")
    bike.lights_front_optional_kits = parse_tags(
        _get(None, "lights", "front", "optional_kits") if specs else None
    )

    bike.lights_rear_type = _get("lights_rear_type", "lights", "rear", "type")
    bike.lights_rear_integrated = _get("lights_rear_integrated", "lights", "rear", "integrated")
    bike.lights_rear_brake_light = _get("lights_rear_brake_light", "lights", "rear", "brake_light")
    bike.lights_rear_optional_kits = parse_tags(
        _get(None, "lights", "rear", "optional_kits") if specs else None
    )

    bike.lights_turn_signals_integrated = _get("lights_turn_signals_integrated", "lights", "turn_signals", "integrated")
    bike.lights_turn_signals_type = _get("lights_turn_signals_type", "lights", "turn_signals", "type")
    bike.lights_turn_signals_left_right_buttons = _get(
        None, "lights", "turn_signals", "left_right_buttons"
    ) if specs else None

    bike.features = parse_tags(_get("features", "features"))

    bike.security_gps = _get("security_gps", "security", "gps")
    bike.security_alarm_db = _get("security_alarm_db", "security", "alarm_db")
    bike.security_app_lock = _get("security_app_lock", "security", "app_lock")
    bike.security_frame_lock = _get("security_frame_lock", "security", "frame_lock")

    range_km = _get("range_estimate_km", "range", "estimate_km")
    bike.range_estimate_km = str(range_km) if range_km else None
    bike.range_notes = _get("range_notes", "range", "notes")

    price_amt = _get("price_amount", "price", "amount")
    bike.price_amount = str(price_amt) if price_amt else None
    bike.price_currency = _get("price_currency", "price", "currency")

    bike.specs_notes = _get("specs_notes", "notes")

    # Parse legacy top-level fields as fallback
    _parse_legacy_motor()
    _parse_legacy_battery()
    _parse_legacy_price()
    _parse_legacy_range()

    resellers_data = frontmatter.get("resellers", [])
    if resellers_data:
        for reseller in bike.resellers:
            session.delete(reseller)

        for reseller_data in resellers_data:
            if isinstance(reseller_data, dict):
                reseller = Reseller(
                    bike=bike,
                    name=reseller_data.get("name", ""),
                    url=reseller_data.get("url"),
                    price=str(reseller_data.get("price"))
                    if reseller_data.get("price")
                    else None,
                    currency=reseller_data.get("currency"),
                    region=reseller_data.get("region"),
                    availability=reseller_data.get("availability"),
                    note=reseller_data.get("note"),
                )
                session.add(reseller)

    return bike


def hydrate_from_vault(session: Session, vault_path: Path) -> dict[str, int]:
    """Hydrate the database from markdown files in the vault."""
    stats = {
        "files_processed": 0,
        "brands_created": 0,
        "brands_updated": 0,
        "bikes_created": 0,
        "bikes_updated": 0,
    }

    md_files = list(vault_path.rglob("*.md"))
    total_files = len(md_files)

    print(f"\nProcessing {total_files} markdown files...")

    for md_file in md_files:
        frontmatter = extract_frontmatter_from_file(md_file)
        if not frontmatter:
            continue

        stats["files_processed"] += 1
        note_type = frontmatter.get("type")

        try:
            if note_type in ["brand", "manufacturer", "brand-index"]:
                title = frontmatter.get("title")
                stmt = select(Brand).where(Brand.title == title)
                existing_brand = session.execute(stmt).scalar_one_or_none()
                existed = existing_brand is not None and (
                    existing_brand.url is not None or existing_brand.summary is not None
                )

                brand = upsert_brand(session, frontmatter, md_file)
                if brand:
                    if existed:
                        stats["brands_updated"] += 1
                    else:
                        stats["brands_created"] += 1

            elif note_type == "bike":
                title = frontmatter.get("title")
                brand_name = frontmatter.get("brand")
                bike_stmt = select(Bike).where(
                    Bike.title == title, Bike.brand_name == brand_name
                )
                existed = (
                    session.execute(bike_stmt).scalar_one_or_none() is not None
                )

                bike = upsert_bike(session, frontmatter, md_file)
                if bike:
                    if existed:
                        stats["bikes_updated"] += 1
                    else:
                        stats["bikes_created"] += 1

            session.commit()

        except Exception as e:
            print(f"⚠ Warning: Failed to process {md_file}: {e}")
            session.rollback()
            continue

    return stats
