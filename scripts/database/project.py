"""
Projection script for updating Markdown files from the SQLite database.

This script reads bike data from the vault.db database and updates the corresponding
Markdown files in vault/notes/bikes/. It replaces the YAML frontmatter and the
specs table within markers while preserving all other manual content.

Usage:
    python scripts/database/project.py [--db-path path/to/database.db]

Exit Codes:
    0: Success
    1: Validation error
    2: Projection failed
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.database.schema import Bike

# Marker constants for the specs table block
SPECS_TABLE_START_MARKER = "<!-- BIKE_SPECS_TABLE_START -->"
SPECS_TABLE_END_MARKER = "<!-- BIKE_SPECS_TABLE_END -->"


def find_bike_file(bike: Bike, vault_path: Path) -> Path | None:
    """
    Find the markdown file for a bike record.

    Args:
        bike: Bike database record
        vault_path: Path to vault/notes directory

    Returns:
        Path to the bike's markdown file, or None if not found
    """
    if not bike.brand_name:
        return None

    # Convert brand name to lowercase hyphenated format
    brand_dir = bike.brand_name.lower().replace(" ", "-")
    bikes_dir = vault_path / "bikes" / brand_dir

    if not bikes_dir.exists():
        return None

    # Search for markdown files in the brand directory
    for md_file in bikes_dir.glob("*.md"):
        # Skip index files
        if md_file.stem == "index":
            continue

        # Read and check if title matches
        try:
            content = md_file.read_text(encoding="utf-8")
            if content.startswith("---"):
                lines = content.split("\n")
                end_idx = lines[1:].index("---") + 1
                frontmatter_text = "\n".join(lines[1:end_idx])
                frontmatter = yaml.safe_load(frontmatter_text)
                if frontmatter and frontmatter.get("title") == bike.title:
                    return md_file
        except (ValueError, yaml.YAMLError):
            continue

    return None


def parse_markdown_file(file_path: Path) -> dict[str, str]:
    """
    Parse a markdown file into its constituent parts.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary with keys: 'frontmatter', 'before_table', 'table', 'after_table'
    """
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    result = {
        "frontmatter": "",
        "before_table": "",
        "table": "",
        "after_table": "",
    }

    # Extract frontmatter
    if lines and lines[0].strip() == "---":
        try:
            end_idx = lines[1:].index("---") + 1
            result["frontmatter"] = "\n".join(lines[1:end_idx])
            body_start = end_idx + 2  # Skip the closing --- and blank line
        except ValueError:
            # Invalid frontmatter
            return result
    else:
        # No frontmatter
        body_start = 0

    # Get the body content
    body = "\n".join(lines[body_start:])

    # Find the specs table markers
    start_marker_match = re.search(
        re.escape(SPECS_TABLE_START_MARKER), body, re.MULTILINE
    )
    end_marker_match = re.search(re.escape(SPECS_TABLE_END_MARKER), body, re.MULTILINE)

    if start_marker_match and end_marker_match:
        # Extract content before, within, and after markers
        start_pos = start_marker_match.start()
        end_pos = end_marker_match.end()

        result["before_table"] = body[:start_pos].rstrip()
        result["table"] = body[start_marker_match.end() : end_marker_match.start()]
        result["after_table"] = body[end_pos:].lstrip()
    else:
        # No markers found - entire body is before_table
        result["before_table"] = body

    return result


def generate_frontmatter(bike: Bike) -> str:
    """
    Generate YAML frontmatter string from a bike database record.

    Args:
        bike: Bike database record

    Returns:
        YAML frontmatter string (without the --- delimiters)
    """
    data: dict[str, Any] = {
        "title": bike.title,
        "type": "bike",
    }

    # Add optional top-level fields
    if bike.brand_name:
        data["brand"] = bike.brand_name
    if bike.model:
        data["model"] = bike.model
    if bike.tags:
        data["tags"] = bike.tags.split(",")
    if bike.url:
        data["url"] = bike.url
    if bike.image:
        data["image"] = bike.image

    # Build resellers array
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

    # Build specs nested structure
    specs: dict[str, Any] = {}

    if bike.category:
        specs["category"] = bike.category
    if bike.model_year:
        specs["model_year"] = bike.model_year

    # Frame
    if any(
        [
            bike.frame_material,
            bike.frame_size,
            bike.frame_length_cm,
            bike.frame_width_cm,
            bike.frame_height_cm,
        ]
    ):
        frame: dict[str, Any] = {}
        if bike.frame_material:
            frame["material"] = bike.frame_material
        if bike.frame_size:
            frame["size"] = bike.frame_size
        if any([bike.frame_length_cm, bike.frame_width_cm, bike.frame_height_cm]):
            dimensions: dict[str, Any] = {}
            if bike.frame_length_cm:
                dimensions["length_cm"] = bike.frame_length_cm
            if bike.frame_width_cm:
                dimensions["width_cm"] = bike.frame_width_cm
            if bike.frame_height_cm:
                dimensions["height_cm"] = bike.frame_height_cm
            frame["dimensions"] = dimensions
        specs["frame"] = frame

    # Weight
    if any([bike.weight_bike_kg, bike.weight_with_battery_kg, bike.weight_battery_kg]):
        weight: dict[str, Any] = {}
        if bike.weight_bike_kg:
            weight["bike_kg"] = bike.weight_bike_kg
        if bike.weight_with_battery_kg:
            weight["with_battery_kg"] = bike.weight_with_battery_kg
        if bike.weight_battery_kg:
            weight["battery_kg"] = bike.weight_battery_kg
        specs["weight"] = weight

    # Load capacity
    if any(
        [
            bike.load_capacity_total_kg,
            bike.load_capacity_rear_kg,
            bike.load_capacity_front_kg,
            bike.load_capacity_passenger_count,
            bike.load_capacity_passenger_config,
        ]
    ):
        load_capacity: dict[str, Any] = {}
        if bike.load_capacity_total_kg:
            load_capacity["total_kg"] = bike.load_capacity_total_kg
        if bike.load_capacity_rear_kg:
            load_capacity["rear_kg"] = bike.load_capacity_rear_kg
        if bike.load_capacity_front_kg:
            load_capacity["front_kg"] = bike.load_capacity_front_kg
        if bike.load_capacity_passenger_count:
            load_capacity["passenger_count_excluding_rider"] = (
                bike.load_capacity_passenger_count
            )
        if bike.load_capacity_passenger_config:
            load_capacity["passenger_config"] = bike.load_capacity_passenger_config
        specs["load_capacity"] = load_capacity

    # Motor
    if any(
        [
            bike.motor_make,
            bike.motor_model,
            bike.motor_type,
            bike.motor_power_w,
            bike.motor_torque_nm,
            bike.motor_boost_throttle is not None,
        ]
    ):
        motor: dict[str, Any] = {}
        if bike.motor_make:
            motor["make"] = bike.motor_make
        if bike.motor_model:
            motor["model"] = bike.motor_model
        if bike.motor_type:
            motor["type"] = bike.motor_type
        if bike.motor_power_w:
            motor["power_w"] = int(bike.motor_power_w)
        if bike.motor_torque_nm:
            motor["torque_nm"] = int(bike.motor_torque_nm)
        if bike.motor_boost_throttle is not None:
            motor["boost_throttle"] = bike.motor_boost_throttle
        specs["motor"] = motor

    # Battery
    if any(
        [
            bike.battery_capacity_wh,
            bike.battery_configuration,
            bike.battery_removable is not None,
            bike.battery_charging_time_h,
        ]
    ):
        battery: dict[str, Any] = {}
        if bike.battery_capacity_wh:
            battery["capacity_wh"] = int(bike.battery_capacity_wh)
        if bike.battery_configuration:
            battery["configuration"] = bike.battery_configuration
        if bike.battery_removable is not None:
            battery["removable"] = bike.battery_removable
        if bike.battery_charging_time_h:
            battery["charging_time_h"] = bike.battery_charging_time_h
        specs["battery"] = battery

    # Drivetrain
    if any([bike.drivetrain_type, bike.drivetrain_speeds, bike.drivetrain_hub]):
        drivetrain: dict[str, Any] = {}
        if bike.drivetrain_type:
            drivetrain["type"] = bike.drivetrain_type
        if bike.drivetrain_speeds:
            drivetrain["speeds"] = bike.drivetrain_speeds
        if bike.drivetrain_hub:
            drivetrain["hub"] = bike.drivetrain_hub
        specs["drivetrain"] = drivetrain

    # Brakes
    if any(
        [
            bike.brakes_type,
            bike.brakes_front_rotor_mm,
            bike.brakes_rear_rotor_mm,
            bike.brakes_pistons,
        ]
    ):
        brakes: dict[str, Any] = {}
        if bike.brakes_type:
            brakes["type"] = bike.brakes_type
        if bike.brakes_front_rotor_mm:
            brakes["front_rotor_mm"] = bike.brakes_front_rotor_mm
        if bike.brakes_rear_rotor_mm:
            brakes["rear_rotor_mm"] = bike.brakes_rear_rotor_mm
        if bike.brakes_pistons:
            brakes["pistons"] = bike.brakes_pistons
        specs["brakes"] = brakes

    # Wheels
    if any([bike.wheels_front_size_in, bike.wheels_rear_size_in, bike.wheels_tire]):
        wheels: dict[str, Any] = {}
        if bike.wheels_front_size_in:
            wheels["front_size_in"] = bike.wheels_front_size_in
        if bike.wheels_rear_size_in:
            wheels["rear_size_in"] = bike.wheels_rear_size_in
        if bike.wheels_tire:
            wheels["tire"] = bike.wheels_tire
        if bike.wheels_rims:
            wheels["rims"] = bike.wheels_rims
        specs["wheels"] = wheels

    # Suspension
    if any([bike.suspension_front, bike.suspension_rear]):
        suspension: dict[str, Any] = {}
        if bike.suspension_front:
            suspension["front"] = bike.suspension_front
        if bike.suspension_rear:
            suspension["rear"] = bike.suspension_rear
        specs["suspension"] = suspension

    # Lights
    if any(
        [
            bike.lights_front_type,
            bike.lights_rear_type,
            bike.lights_turn_signals_integrated,
        ]
    ):
        lights: dict[str, Any] = {}

        # Front lights
        if any(
            [
                bike.lights_front_type,
                bike.lights_front_integrated is not None,
                bike.lights_front_powered_by,
            ]
        ):
            front: dict[str, Any] = {}
            if bike.lights_front_type:
                front["type"] = bike.lights_front_type
            if bike.lights_front_integrated is not None:
                front["integrated"] = bike.lights_front_integrated
            if bike.lights_front_powered_by:
                front["powered_by"] = bike.lights_front_powered_by
            lights["front"] = front

        # Rear lights
        if any(
            [
                bike.lights_rear_type,
                bike.lights_rear_integrated is not None,
                bike.lights_rear_brake_light is not None,
            ]
        ):
            rear: dict[str, Any] = {}
            if bike.lights_rear_type:
                rear["type"] = bike.lights_rear_type
            if bike.lights_rear_integrated is not None:
                rear["integrated"] = bike.lights_rear_integrated
            if bike.lights_rear_brake_light is not None:
                rear["brake_light"] = bike.lights_rear_brake_light
            lights["rear"] = rear

        # Turn signals
        if any(
            [
                bike.lights_turn_signals_integrated is not None,
                bike.lights_turn_signals_type,
            ]
        ):
            turn_signals: dict[str, Any] = {}
            if bike.lights_turn_signals_integrated is not None:
                turn_signals["integrated"] = bike.lights_turn_signals_integrated
            if bike.lights_turn_signals_type:
                turn_signals["type"] = bike.lights_turn_signals_type
            if bike.lights_turn_signals_left_right_buttons is not None:
                turn_signals["left_right_buttons"] = (
                    bike.lights_turn_signals_left_right_buttons
                )
            lights["turn_signals"] = turn_signals

        specs["lights"] = lights

    # Features
    if bike.features:
        specs["features"] = bike.features.split(",")

    # Security
    if any(
        [
            bike.security_gps is not None,
            bike.security_alarm_db,
            bike.security_app_lock is not None,
            bike.security_frame_lock is not None,
        ]
    ):
        security: dict[str, Any] = {}
        if bike.security_gps is not None:
            security["gps"] = bike.security_gps
        if bike.security_alarm_db:
            security["alarm_db"] = bike.security_alarm_db
        if bike.security_app_lock is not None:
            security["app_lock"] = bike.security_app_lock
        if bike.security_frame_lock is not None:
            security["frame_lock"] = bike.security_frame_lock
        specs["security"] = security

    # Range
    if any([bike.range_estimate_km, bike.range_notes]):
        range_data: dict[str, Any] = {}
        if bike.range_estimate_km:
            range_data["estimate_km"] = bike.range_estimate_km
        if bike.range_notes:
            range_data["notes"] = bike.range_notes
        specs["range"] = range_data

    # Price
    if any([bike.price_amount, bike.price_currency]):
        price: dict[str, Any] = {}
        if bike.price_amount:
            price["amount"] = bike.price_amount
        if bike.price_currency:
            price["currency"] = bike.price_currency
        specs["price"] = price

    # General notes
    if bike.specs_notes:
        specs["notes"] = bike.specs_notes

    if specs:
        data["specs"] = specs

    # Generate YAML string
    yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return yaml_str.rstrip()


def generate_specs_table(bike: Bike) -> str:
    """
    Generate a Markdown specifications table from a bike database record.

    Args:
        bike: Bike database record

    Returns:
        Markdown table string
    """
    rows = []

    # Basic info
    if bike.category:
        rows.append(f"| **Category** | {bike.category} |")
    if bike.model_year:
        rows.append(f"| **Model Year** | {bike.model_year} |")

    # Motor
    if bike.motor_make or bike.motor_model:
        motor_str = bike.motor_make or ""
        if bike.motor_model:
            motor_str += f" {bike.motor_model}" if motor_str else bike.motor_model
        rows.append(f"| **Motor** | {motor_str} |")
    if bike.motor_power_w:
        rows.append(f"| **Motor Power** | {int(bike.motor_power_w)}W |")
    if bike.motor_torque_nm:
        rows.append(f"| **Motor Torque** | {int(bike.motor_torque_nm)}Nm |")

    # Battery
    if bike.battery_capacity_wh:
        rows.append(f"| **Battery Capacity** | {int(bike.battery_capacity_wh)}Wh |")
    if bike.range_estimate_km:
        rows.append(f"| **Range** | {bike.range_estimate_km} km |")

    # Weight & Load
    if bike.weight_with_battery_kg:
        rows.append(f"| **Weight (with battery)** | {bike.weight_with_battery_kg}kg |")
    if bike.load_capacity_total_kg:
        rows.append(
            f"| **Total Load Capacity** | {bike.load_capacity_total_kg}kg |"
        )

    # Drivetrain
    if bike.drivetrain_type:
        rows.append(f"| **Drivetrain** | {bike.drivetrain_type} |")
    if bike.brakes_type:
        rows.append(f"| **Brakes** | {bike.brakes_type} |")

    # Wheels
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

    # Price
    if bike.price_amount and bike.price_currency:
        rows.append(f"| **Price** | {bike.price_amount} {bike.price_currency} |")

    if not rows:
        return ""

    # Build table
    table = "| Specification | Value |\n"
    table += "|---------------|-------|\n"
    table += "\n".join(rows)

    return table


def reconstruct_markdown_file(
    parts: dict[str, str], new_frontmatter: str, new_table: str
) -> str:
    """
    Reconstruct a markdown file with updated frontmatter and specs table.

    Args:
        parts: Dictionary with original file parts
        new_frontmatter: New YAML frontmatter string
        new_table: New specs table string

    Returns:
        Complete markdown file content
    """
    sections = []

    # Add frontmatter with delimiters
    sections.append("---")
    sections.append(new_frontmatter)
    sections.append("---")
    sections.append("")

    # Add content before table
    if parts["before_table"]:
        sections.append(parts["before_table"])
        if not parts["before_table"].endswith("\n"):
            sections.append("")

    # Add specs table with markers
    sections.append(SPECS_TABLE_START_MARKER)
    if new_table:
        sections.append("")
        sections.append(new_table)
        sections.append("")
    sections.append(SPECS_TABLE_END_MARKER)

    # Add content after table
    if parts["after_table"]:
        sections.append("")
        sections.append(parts["after_table"])

    return "\n".join(sections)


def project_bike_to_file(
    bike: Bike, vault_path: Path, dry_run: bool = False
) -> tuple[bool, str]:
    """
    Project a bike record to its markdown file.

    Args:
        bike: Bike database record
        vault_path: Path to vault/notes directory
        dry_run: If True, don't write changes

    Returns:
        Tuple of (success, message)
    """
    # Find the file
    file_path = find_bike_file(bike, vault_path)
    if not file_path:
        return False, f"Could not find file for bike: {bike.title}"

    # Parse existing file
    try:
        parts = parse_markdown_file(file_path)
    except Exception as e:
        return False, f"Failed to parse file {file_path}: {e}"

    # Generate new content
    try:
        new_frontmatter = generate_frontmatter(bike)
        new_table = generate_specs_table(bike)
    except Exception as e:
        return False, f"Failed to generate content for {bike.title}: {e}"

    # Reconstruct file
    try:
        new_content = reconstruct_markdown_file(parts, new_frontmatter, new_table)
    except Exception as e:
        return False, f"Failed to reconstruct file for {bike.title}: {e}"

    # Write file (unless dry run)
    if not dry_run:
        try:
            file_path.write_text(new_content, encoding="utf-8")
        except Exception as e:
            return False, f"Failed to write file {file_path}: {e}"

    return True, f"Updated: {file_path.relative_to(vault_path.parent.parent)}"


def main():
    """Command-line interface for the projection script."""
    parser = argparse.ArgumentParser(
        description="Project bike data from database to Markdown files",
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
        "--dry-run",
        action="store_true",
        help="Show what would be updated without writing changes",
    )

    parser.add_argument(
        "--bike-id",
        type=int,
        help="Project only the bike with this ID",
    )

    args = parser.parse_args()

    # Convert paths
    vault_path = Path(args.vault_path)
    db_path = Path(args.db_path)

    # Validate paths
    if not vault_path.exists():
        print(f"✗ Vault path does not exist: {vault_path}", file=sys.stderr)
        return 2

    if not db_path.exists():
        print(f"✗ Database does not exist: {db_path}", file=sys.stderr)
        return 2

    # Create database engine
    db_path = db_path.resolve()
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    print(f"Projecting from database: {db_path}")
    print(f"To vault: {vault_path}")
    if args.dry_run:
        print("DRY RUN - No changes will be written")
    print()

    try:
        with Session(engine) as session:
            # Query bikes
            if args.bike_id:
                stmt = select(Bike).where(Bike.id == args.bike_id)
                bikes = [session.execute(stmt).scalar_one_or_none()]
                if not bikes[0]:
                    print(f"✗ Bike with ID {args.bike_id} not found", file=sys.stderr)
                    return 1
            else:
                stmt = select(Bike).order_by(Bike.brand_name, Bike.title)
                bikes = list(session.execute(stmt).scalars().all())

            if not bikes:
                print("No bikes found in database")
                return 0

            print(f"Processing {len(bikes)} bike(s)...")
            print()

            success_count = 0
            fail_count = 0

            for bike in bikes:
                success, message = project_bike_to_file(bike, vault_path, args.dry_run)
                if success:
                    print(f"✓ {message}")
                    success_count += 1
                else:
                    print(f"✗ {message}", file=sys.stderr)
                    fail_count += 1

            # Print summary
            print()
            print("Summary:")
            print(f"  Successful: {success_count}")
            print(f"  Failed: {fail_count}")

            return 0 if fail_count == 0 else 2

    except Exception as e:
        print(f"\n✗ Projection failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
