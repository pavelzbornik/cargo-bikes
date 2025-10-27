"""
Hydration script for populating the SQLite database from Markdown files.

This script reads YAML frontmatter from all valid Markdown files in vault/notes/
and populates the SQLite database with structured data. It first validates files
using the linter, then performs idempotent upserts to avoid duplicate records.

Usage:
    python scripts/database/hydrate.py [--db-path path/to/database.db]

Exit Codes:
    0: Success
    1: Linter validation failed
    2: Database hydration failed
"""

import argparse
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.database.schema import Base, Bike, Brand, Reseller


def run_linter(vault_path: Path) -> bool:
    """
    Run the structural linter to validate all markdown files.

    Args:
        vault_path: Path to the vault/notes directory

    Returns:
        True if linter passes, False if validation fails
    """
    print("Running structural linter...")
    linter_script = Path(__file__).parent.parent / "linters" / "validate_structure.py"

    try:
        result = subprocess.run(
            [sys.executable, str(linter_script), "--vault-path", str(vault_path)],
            capture_output=True,
            text=True,
        )

        # Print linter output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"✗ Failed to run linter: {e}", file=sys.stderr)
        return False


def extract_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """
    Extract YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary of frontmatter data, or None if extraction fails
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        if not lines or lines[0].strip() != "---":
            return None

        try:
            end_idx = lines[1:].index("---") + 1
        except ValueError:
            return None

        frontmatter_text = "\n".join(lines[1:end_idx])
        return yaml.safe_load(frontmatter_text) or {}

    except Exception as e:
        print(f"⚠ Warning: Failed to extract frontmatter from {file_path}: {e}")
        return None


def parse_date(date_value: Any) -> date | None:
    """
    Parse a date value from frontmatter.

    Args:
        date_value: Date value (can be date, datetime, or string)

    Returns:
        date object or None if parsing fails
    """
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
    """
    Parse tags from frontmatter and convert to comma-separated string.

    Args:
        tags_value: Tags value (can be list or string)

    Returns:
        Comma-separated string of tags or None
    """
    if isinstance(tags_value, list):
        return ",".join(str(tag).strip() for tag in tags_value)
    elif isinstance(tags_value, str):
        return tags_value
    return None


def upsert_brand(
    session: Session, frontmatter: dict[str, Any], file_path: Path
) -> Brand | None:
    """
    Insert or update a brand record.

    Args:
        session: SQLAlchemy session
        frontmatter: Frontmatter dictionary
        file_path: Path to the markdown file

    Returns:
        Brand object or None
    """
    # Determine if this is a brand or manufacturer
    note_type = frontmatter.get("type")
    if note_type not in ["brand", "manufacturer"]:
        return None

    title = frontmatter.get("title")
    if not title:
        return None

    # Check if brand already exists
    stmt = select(Brand).where(Brand.title == title)
    existing_brand = session.execute(stmt).scalar_one_or_none()

    if existing_brand:
        # Update existing brand
        brand = existing_brand
    else:
        # Create new brand
        brand = Brand(title=title, type=note_type)
        session.add(brand)

    # Update fields
    brand.date = parse_date(frontmatter.get("date")) or date.today()
    brand.url = frontmatter.get("url")
    brand.logo = frontmatter.get("logo")
    brand.summary = frontmatter.get("summary")
    brand.tags = parse_tags(frontmatter.get("tags"))

    # Company information
    brand.founded_year = frontmatter.get("founded_year")
    brand.country = frontmatter.get("country")

    # Handle headquarters (can be nested dict or string)
    headquarters = frontmatter.get("headquarters")
    if isinstance(headquarters, dict):
        brand.headquarters_city = headquarters.get("city")
        brand.headquarters_country = headquarters.get("country")
        brand.headquarters_address = headquarters.get("address")

    # Market & positioning
    brand.categories = parse_tags(frontmatter.get("categories"))
    brand.market_segments = parse_tags(frontmatter.get("market_segments"))
    brand.regions = parse_tags(frontmatter.get("regions"))
    brand.price_tier = frontmatter.get("price_tier")

    # Product portfolio
    brand.product_types = parse_tags(frontmatter.get("product_types"))
    brand.model_count = frontmatter.get("model_count")
    brand.primary_motors = parse_tags(frontmatter.get("primary_motors"))
    brand.parent_company = frontmatter.get("parent_company")

    # Manufacturing
    brand.manufacturing_locations = parse_tags(
        frontmatter.get("manufacturing_locations")
    )
    brand.manufacturing_approach = frontmatter.get("manufacturing_approach")
    brand.assembly_location = frontmatter.get("assembly_location")

    # Distribution
    brand.distribution_model = frontmatter.get("distribution_model")
    brand.regions_active = parse_tags(frontmatter.get("regions_active"))
    brand.direct_sales = frontmatter.get("direct_sales")
    brand.dealership_network = frontmatter.get("dealership_network")

    # Values
    brand.value_sustainability = frontmatter.get("value_sustainability")
    brand.value_local_manufacturing = frontmatter.get("value_local_manufacturing")
    brand.value_community_focus = frontmatter.get("value_community_focus")

    return brand


def get_or_create_brand(session: Session, brand_name: str) -> Brand | None:
    """
    Get existing brand or create a placeholder.

    Args:
        session: SQLAlchemy session
        brand_name: Name of the brand

    Returns:
        Brand object or None
    """
    if not brand_name:
        return None

    # Check if brand exists
    stmt = select(Brand).where(Brand.title == brand_name)
    brand = session.execute(stmt).scalar_one_or_none()

    if not brand:
        # Create placeholder brand
        brand = Brand(title=brand_name, type="brand", date=date.today())
        session.add(brand)

    return brand


def upsert_bike(
    session: Session, frontmatter: dict[str, Any], file_path: Path
) -> Bike | None:
    """
    Insert or update a bike record.

    Args:
        session: SQLAlchemy session
        frontmatter: Frontmatter dictionary
        file_path: Path to the markdown file

    Returns:
        Bike object or None
    """
    if frontmatter.get("type") != "bike":
        return None

    title = frontmatter.get("title")
    if not title:
        return None

    # Check if bike already exists (by title and brand)
    brand_name = frontmatter.get("brand")
    stmt = select(Bike).where(Bike.title == title, Bike.brand_name == brand_name)
    existing_bike = session.execute(stmt).scalar_one_or_none()

    if existing_bike:
        bike = existing_bike
    else:
        bike = Bike(title=title)
        session.add(bike)

    # Top-level fields
    bike.type = "bike"
    bike.brand_name = brand_name
    bike.model = frontmatter.get("model")
    bike.tags = parse_tags(frontmatter.get("tags"))
    bike.url = frontmatter.get("url")
    bike.image = frontmatter.get("image")

    # Store file path relative to workspace root
    try:
        # Try to get path relative to current working directory
        bike.file_path = str(file_path.relative_to(Path.cwd()))
    except ValueError:
        # If that fails, resolve both paths and try again
        try:
            bike.file_path = str(file_path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            # Fall back to absolute path
            bike.file_path = str(file_path.resolve())

    # Get or create brand relationship
    if brand_name:
        brand = get_or_create_brand(session, brand_name)
        bike.brand = brand

    # Extract specs
    specs = frontmatter.get("specs", {})

    # Basic classification
    bike.category = specs.get("category")
    bike.model_year = specs.get("model_year")

    # Frame
    frame = specs.get("frame", {})
    bike.frame_material = frame.get("material")
    bike.frame_size = frame.get("size")
    dimensions = frame.get("dimensions", {})
    bike.frame_length_cm = dimensions.get("length_cm")
    bike.frame_width_cm = dimensions.get("width_cm")
    bike.frame_height_cm = dimensions.get("height_cm")

    # Weight
    weight = specs.get("weight", {})
    bike.weight_bike_kg = weight.get("bike_kg")
    bike.weight_with_battery_kg = weight.get("with_battery_kg")
    bike.weight_battery_kg = weight.get("battery_kg")

    # Load capacity
    load_capacity = specs.get("load_capacity", {})
    bike.load_capacity_total_kg = load_capacity.get("total_kg")
    bike.load_capacity_rear_kg = load_capacity.get("rear_kg")
    bike.load_capacity_front_kg = load_capacity.get("front_kg")
    bike.load_capacity_passenger_count = load_capacity.get(
        "passenger_count_excluding_rider"
    )
    bike.load_capacity_passenger_config = load_capacity.get("passenger_config")

    # Motor
    motor = specs.get("motor", {})
    bike.motor_make = motor.get("make")
    bike.motor_model = motor.get("model")
    bike.motor_type = motor.get("type")

    # Handle power_w which can be numeric or string
    power_w = motor.get("power_w")
    if isinstance(power_w, (int, float)):
        bike.motor_power_w = float(power_w)
    elif isinstance(power_w, str):
        try:
            # Remove common suffixes like 'W' and handle ranges
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

    bike.motor_torque_nm = motor.get("torque_nm")
    bike.motor_boost_throttle = motor.get("boost_throttle")

    # Battery
    battery = specs.get("battery", {})
    # Handle capacity_wh which can be numeric or string range
    capacity_wh = battery.get("capacity_wh")
    if isinstance(capacity_wh, (int, float)):
        bike.battery_capacity_wh = float(capacity_wh)
    elif isinstance(capacity_wh, str):
        # For ranges like "630-800", store as string in configuration field
        # and extract first value for capacity_wh
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

    bike.battery_configuration = battery.get("configuration")
    bike.battery_removable = battery.get("removable")
    bike.battery_charging_time_h = (
        str(battery.get("charging_time_h")) if battery.get("charging_time_h") else None
    )

    # Drivetrain
    drivetrain = specs.get("drivetrain", {})
    bike.drivetrain_type = drivetrain.get("type")
    bike.drivetrain_speeds = (
        str(drivetrain.get("speeds")) if drivetrain.get("speeds") else None
    )
    bike.drivetrain_hub = drivetrain.get("hub")

    # Brakes
    brakes = specs.get("brakes", {})
    bike.brakes_type = brakes.get("type")
    bike.brakes_front_rotor_mm = brakes.get("front_rotor_mm")
    bike.brakes_rear_rotor_mm = brakes.get("rear_rotor_mm")
    bike.brakes_pistons = str(brakes.get("pistons")) if brakes.get("pistons") else None

    # Wheels
    wheels = specs.get("wheels", {})
    bike.wheels_front_size_in = wheels.get("front_size_in")
    bike.wheels_rear_size_in = wheels.get("rear_size_in")
    bike.wheels_tire = wheels.get("tire")
    bike.wheels_rims = wheels.get("rims")

    # Suspension
    suspension = specs.get("suspension", {})
    bike.suspension_front = suspension.get("front")
    bike.suspension_rear = suspension.get("rear")

    # Lights
    lights = specs.get("lights", {})
    front = lights.get("front", {})
    bike.lights_front_type = front.get("type")
    bike.lights_front_integrated = front.get("integrated")
    bike.lights_front_powered_by = front.get("powered_by")
    bike.lights_front_optional_kits = parse_tags(front.get("optional_kits"))

    rear = lights.get("rear", {})
    bike.lights_rear_type = rear.get("type")
    bike.lights_rear_integrated = rear.get("integrated")
    bike.lights_rear_brake_light = rear.get("brake_light")
    bike.lights_rear_optional_kits = parse_tags(rear.get("optional_kits"))

    turn_signals = lights.get("turn_signals", {})
    bike.lights_turn_signals_integrated = turn_signals.get("integrated")
    bike.lights_turn_signals_type = turn_signals.get("type")
    bike.lights_turn_signals_left_right_buttons = turn_signals.get("left_right_buttons")

    # Features
    bike.features = parse_tags(specs.get("features"))

    # Security
    security = specs.get("security", {})
    bike.security_gps = security.get("gps")
    bike.security_alarm_db = security.get("alarm_db")
    bike.security_app_lock = security.get("app_lock")
    bike.security_frame_lock = security.get("frame_lock")

    # Range
    range_data = specs.get("range", {})
    bike.range_estimate_km = (
        str(range_data.get("estimate_km")) if range_data.get("estimate_km") else None
    )
    bike.range_notes = range_data.get("notes")

    # Price
    price = specs.get("price", {})
    bike.price_amount = str(price.get("amount")) if price.get("amount") else None
    bike.price_currency = price.get("currency")

    # General notes
    bike.specs_notes = specs.get("notes")

    # Handle resellers
    resellers_data = frontmatter.get("resellers", [])
    if resellers_data:
        # Remove existing resellers
        for reseller in bike.resellers:
            session.delete(reseller)

        # Add new resellers
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
    """
    Hydrate the database from markdown files in the vault.

    Args:
        session: SQLAlchemy session
        vault_path: Path to the vault/notes directory

    Returns:
        Dictionary with counts of processed items
    """
    stats = {
        "files_processed": 0,
        "brands_created": 0,
        "brands_updated": 0,
        "bikes_created": 0,
        "bikes_updated": 0,
    }

    # Find all .md files
    md_files = list(vault_path.rglob("*.md"))
    total_files = len(md_files)

    print(f"\nProcessing {total_files} markdown files...")

    for md_file in md_files:
        frontmatter = extract_frontmatter(md_file)
        if not frontmatter:
            continue

        stats["files_processed"] += 1
        note_type = frontmatter.get("type")

        try:
            if note_type in ["brand", "manufacturer"]:
                # Track if brand existed with substantive data before
                title = frontmatter.get("title")
                stmt = select(Brand).where(Brand.title == title)
                existing_brand = session.execute(stmt).scalar_one_or_none()

                # A brand is considered "existed" if it had a URL or summary
                # (indicating it came from an explicit brand file, not a placeholder)
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
                # Track if bike existed before
                title = frontmatter.get("title")
                brand_name = frontmatter.get("brand")
                stmt = select(Bike).where(
                    Bike.title == title, Bike.brand_name == brand_name
                )
                existed = session.execute(stmt).scalar_one_or_none() is not None

                bike = upsert_bike(session, frontmatter, md_file)
                if bike:
                    if existed:
                        stats["bikes_updated"] += 1
                    else:
                        stats["bikes_created"] += 1

            # Commit after each file to maintain progress
            session.commit()

        except Exception as e:
            print(f"⚠ Warning: Failed to process {md_file}: {e}")
            session.rollback()
            continue

    return stats


def main():
    """Command-line interface for the hydration script."""
    parser = argparse.ArgumentParser(
        description="Hydrate the cargo-bikes database from Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="vault.db",
        help="Path to the database file (default: vault.db)",
    )

    parser.add_argument(
        "--vault-path",
        type=str,
        default="vault/notes",
        help="Path to the vault notes directory (default: vault/notes)",
    )

    parser.add_argument(
        "--skip-linter",
        action="store_true",
        help="Skip linter validation (not recommended)",
    )

    args = parser.parse_args()

    # Convert paths
    vault_path = Path(args.vault_path)
    db_path = Path(args.db_path)

    # Validate vault path
    if not vault_path.exists():
        print(f"✗ Vault path does not exist: {vault_path}", file=sys.stderr)
        return 2

    # Run linter first (unless skipped)
    if not args.skip_linter:
        if not run_linter(vault_path):
            print(
                "\n✗ Linter validation failed. Fix errors before hydrating.",
                file=sys.stderr,
            )
            return 1
        print()

    # Create database engine
    db_path = db_path.resolve()
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # Ensure tables exist
    Base.metadata.create_all(engine)

    # Hydrate database
    print(f"Hydrating database: {db_path}")
    print(f"From vault: {vault_path}")

    try:
        with Session(engine) as session:
            stats = hydrate_from_vault(session, vault_path)

        # Print summary
        print("\n✓ Hydration complete!")
        print("\nSummary:")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Brands created: {stats['brands_created']}")
        print(f"  Brands updated: {stats['brands_updated']}")
        print(f"  Bikes created: {stats['bikes_created']}")
        print(f"  Bikes updated: {stats['bikes_updated']}")
        print("\nTotal records:")
        print(f"  Brands: {stats['brands_created'] + stats['brands_updated']}")
        print(f"  Bikes: {stats['bikes_created'] + stats['bikes_updated']}")

        return 0

    except Exception as e:
        print(f"\n✗ Hydration failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
