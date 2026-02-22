"""
Note writer for generating and updating bike note markdown files.

Handles:
- YAML frontmatter generation with proper formatting
- Preserving existing markdown body content
- Updating only the frontmatter and designated fenced blocks
- Generating specification tables for the BIKE_SPECS_TABLE block
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("bike_note_updater.note_writer")


class _LiteralStr(str):
    """String subclass for literal YAML block scalars."""

    pass


def _literal_str_representer(
    dumper: yaml.Dumper, data: _LiteralStr
) -> yaml.ScalarNode:
    """Represent multi-line strings as literal block scalars."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


def _str_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    """Use quoted strings for values containing special characters."""
    if any(c in data for c in ":#{}[]&*!|>'\"%@`"):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    if data.startswith(("- ", "? ")) or data == "":
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _get_yaml_dumper() -> type[yaml.Dumper]:
    """Get a configured YAML dumper with custom representers."""

    class CustomDumper(yaml.Dumper):
        pass

    CustomDumper.add_representer(_LiteralStr, _literal_str_representer)
    CustomDumper.add_representer(str, _str_representer)

    return CustomDumper


def format_frontmatter(frontmatter: dict[str, Any]) -> str:
    """
    Format a frontmatter dictionary as a YAML string.

    Args:
        frontmatter: The frontmatter data to format

    Returns:
        Formatted YAML string (without --- delimiters)
    """
    # Prepare data: convert multi-line strings to literal blocks
    prepared = _prepare_for_yaml(frontmatter)

    dumper = _get_yaml_dumper()
    yaml_str = yaml.dump(
        prepared,
        Dumper=dumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )

    return yaml_str.rstrip("\n")


def _prepare_for_yaml(data: Any) -> Any:
    """Recursively prepare data for YAML serialization."""
    if isinstance(data, dict):
        return {k: _prepare_for_yaml(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [_prepare_for_yaml(item) for item in data]
    elif isinstance(data, str) and "\n" in data:
        return _LiteralStr(data)
    return data


def _generate_specs_table(frontmatter: dict[str, Any]) -> str:
    """
    Generate a markdown specification table from frontmatter specs.

    Args:
        frontmatter: Complete frontmatter dict

    Returns:
        Markdown table string
    """
    specs = frontmatter.get("specs", {})
    if not specs:
        return ""

    rows: list[tuple[str, str]] = []

    # Category & Year
    if specs.get("category"):
        rows.append(("Category", str(specs["category"]).title()))
    if specs.get("model_year"):
        rows.append(("Model Year", str(specs["model_year"])))

    # Frame
    frame = specs.get("frame", {})
    if frame.get("material"):
        rows.append(("Frame Material", str(frame["material"]).title()))
    if frame.get("size"):
        rows.append(("Frame Size", str(frame["size"])))

    # Weight
    weight = specs.get("weight", {})
    if weight.get("with_battery_kg"):
        rows.append(("Weight (with battery)", f"{weight['with_battery_kg']} kg"))
    elif weight.get("bike_kg"):
        rows.append(("Weight (bike only)", f"{weight['bike_kg']} kg"))

    # Load Capacity
    load = specs.get("load_capacity", {})
    if load.get("total_kg"):
        rows.append(("Max Load", f"{load['total_kg']} kg"))
    if load.get("passenger_count_excluding_rider"):
        rows.append(("Passengers", str(load["passenger_count_excluding_rider"])))

    # Motor
    motor = specs.get("motor", {})
    motor_parts = []
    if motor.get("make"):
        motor_parts.append(str(motor["make"]))
    if motor.get("model"):
        motor_parts.append(str(motor["model"]))
    if motor_parts:
        rows.append(("Motor", " ".join(motor_parts)))
    if motor.get("power_w"):
        rows.append(("Motor Power", f"{motor['power_w']}W"))
    if motor.get("torque_nm"):
        rows.append(("Motor Torque", f"{motor['torque_nm']} Nm"))
    if motor.get("type"):
        rows.append(("Motor Type", str(motor["type"])))

    # Battery
    battery = specs.get("battery", {})
    if battery.get("capacity_wh"):
        rows.append(("Battery", f"{battery['capacity_wh']} Wh"))
    if battery.get("configuration"):
        rows.append(("Battery Config", str(battery["configuration"])))
    if battery.get("removable") is not None:
        rows.append(("Removable Battery", "Yes" if battery["removable"] else "No"))

    # Drivetrain
    drivetrain = specs.get("drivetrain", {})
    if drivetrain.get("type"):
        rows.append(("Drivetrain", str(drivetrain["type"]).title()))
    if drivetrain.get("speeds"):
        rows.append(("Speeds", str(drivetrain["speeds"])))
    if drivetrain.get("hub"):
        rows.append(("Hub", str(drivetrain["hub"])))

    # Brakes
    brakes = specs.get("brakes", {})
    if brakes.get("type"):
        rows.append(("Brakes", str(brakes["type"])))

    # Wheels
    wheels = specs.get("wheels", {})
    if wheels.get("front_size_in"):
        rows.append(("Front Wheel", str(wheels["front_size_in"])))
    if wheels.get("rear_size_in"):
        rows.append(("Rear Wheel", str(wheels["rear_size_in"])))
    if wheels.get("tire"):
        rows.append(("Tires", str(wheels["tire"])))

    # Suspension
    suspension = specs.get("suspension", {})
    if suspension.get("front"):
        rows.append(("Front Suspension", str(suspension["front"])))
    if suspension.get("rear"):
        rows.append(("Rear Suspension", str(suspension["rear"])))

    # Range
    range_data = specs.get("range", {})
    if range_data.get("estimate_km"):
        rows.append(("Range", f"{range_data['estimate_km']} km"))

    # Price
    price = specs.get("price", {})
    if price.get("amount"):
        currency = price.get("currency", "")
        symbol = {"EUR": "\u20ac", "USD": "$", "GBP": "\u00a3"}.get(currency, currency)
        rows.append(("Price (MSRP)", f"{symbol}{price['amount']}"))

    if not rows:
        return ""

    # Build markdown table
    lines = ["| Specification | Value |", "| --- | --- |"]
    for label, value in rows:
        lines.append(f"| **{label}** | {value} |")

    return "\n".join(lines)


def parse_note(file_path: Path) -> tuple[dict[str, Any] | None, str]:
    """
    Parse a bike note file into frontmatter and body.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (frontmatter_dict, body_string)
    """
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return None, content

    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        return None, content

    frontmatter_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        return None, content

    return frontmatter, body


def _update_specs_table_block(body: str, table_content: str) -> str:
    """
    Replace content between BIKE_SPECS_TABLE markers.

    Args:
        body: The markdown body content
        table_content: New table content to insert

    Returns:
        Updated body with new table content
    """
    start_marker = "<!-- BIKE_SPECS_TABLE_START -->"
    end_marker = "<!-- BIKE_SPECS_TABLE_END -->"

    start_idx = body.find(start_marker)
    end_idx = body.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        return body

    # Replace content between markers
    before = body[: start_idx + len(start_marker)]
    after = body[end_idx:]

    if table_content:
        return f"{before}\n{table_content}\n{after}"
    else:
        return f"{before}\n{after}"


def write_note(
    file_path: Path,
    frontmatter: dict[str, Any],
    body: str | None = None,
    update_specs_table: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Write an updated bike note to disk.

    Args:
        file_path: Path to write the file
        frontmatter: Updated frontmatter dictionary
        body: Markdown body (if None, preserves existing body)
        update_specs_table: Whether to regenerate the specs table
        dry_run: If True, return changes without writing

    Returns:
        Dict with {success, path, changes, errors}
    """
    result: dict[str, Any] = {
        "success": False,
        "path": str(file_path),
        "changes": [],
        "errors": [],
    }

    try:
        # Get existing body if not provided
        if body is None:
            if file_path.exists():
                _, body = parse_note(file_path)
            else:
                body = ""

        # Update specs table if requested
        if update_specs_table and body:
            table = _generate_specs_table(frontmatter)
            new_body = _update_specs_table_block(body, table)
            if new_body != body:
                result["changes"].append("Updated specs table")
                body = new_body

        # Format frontmatter
        yaml_str = format_frontmatter(frontmatter)

        # Assemble complete file
        content = f"---\n{yaml_str}\n---\n{body}"

        # Ensure file ends with newline
        if not content.endswith("\n"):
            content += "\n"

        if dry_run:
            result["success"] = True
            result["content_preview"] = content[:500]
            return result

        # Write to disk
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        result["success"] = True
        result["changes"].append("Wrote updated note")
        logger.info(f"Updated {file_path}")

    except Exception as e:
        result["errors"].append(str(e))
        logger.error(f"Failed to write {file_path}: {e}")

    return result
