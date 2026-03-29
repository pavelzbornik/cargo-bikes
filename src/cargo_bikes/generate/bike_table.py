"""Generate bike comparison tables from YAML frontmatter.

Extracted from scripts/generate_bike_table.py. Shared utilities
(extract_frontmatter, collect_bikes) moved to vault/ modules.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def extract_spec_value(
    specs: dict[str, Any] | None, keys: list[str], default: str = ""
) -> str:
    """Extract a nested value from specs object with fallback.

    Args:
        specs: The specs dictionary (or None).
        keys: List of keys to traverse (e.g., ["motor", "power_w"]).
        default: Default value if key path not found.

    Returns:
        The value as a string, or default if not found.
    """
    if not specs or not isinstance(specs, dict):
        return default
    value: Any = specs
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    if value is None:
        return default
    if len(keys) >= 1 and keys[-1] == "power_w" and isinstance(value, (int, float)):
        return f"{value}W"
    if (
        len(keys) >= 1
        and keys[-1] == "capacity_wh"
        and isinstance(value, (int, float))
    ):
        return f"{value}Wh"
    if (
        len(keys) >= 1
        and keys[-1] == "estimate_km"
        and isinstance(value, (int, float))
    ):
        return f"{value}km"
    return str(value) if value else default


def get_motor_display(frontmatter: dict[str, Any]) -> str:
    """Extract motor information for display."""
    # Flat format first
    power_w = frontmatter.get("motor_power_w")
    make = frontmatter.get("motor_make", "")
    if power_w is not None:
        if make:
            return f"{make} {power_w}W"
        return f"{power_w}W"
    # Nested specs fallback
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        motor_spec = specs.get("motor", {})
        if isinstance(motor_spec, dict):
            pw = motor_spec.get("power_w")
            if pw is not None:
                mk = motor_spec.get("make", "")
                return f"{mk} {pw}W" if mk else f"{pw}W"
    legacy_motor = frontmatter.get("motor", "")
    return str(legacy_motor) if legacy_motor else ""


def get_battery_display(frontmatter: dict[str, Any]) -> str:
    """Extract battery information for display."""
    # Flat format first
    capacity_wh = frontmatter.get("battery_capacity_wh")
    if capacity_wh is not None:
        return f"{capacity_wh}Wh"
    # Nested specs fallback
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        battery_spec = specs.get("battery", {})
        if isinstance(battery_spec, dict):
            cw = battery_spec.get("capacity_wh")
            if cw is not None:
                return f"{cw}Wh"
    legacy_battery = frontmatter.get("battery", "")
    return str(legacy_battery) if legacy_battery else ""


def get_range_display(frontmatter: dict[str, Any]) -> str:
    """Extract range information for display."""
    # Flat format first
    estimate_km = frontmatter.get("range_estimate_km")
    if estimate_km is not None:
        return f"{estimate_km}km"
    # Nested specs fallback
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        range_spec = specs.get("range", {})
        if isinstance(range_spec, dict):
            ek = range_spec.get("estimate_km")
            if ek is not None:
                return f"{ek}km"
    legacy_range = frontmatter.get("range", "")
    return str(legacy_range) if legacy_range else ""


def get_price_display(frontmatter: dict[str, Any]) -> str:
    """Extract price information for display."""
    # Flat format first
    amount = frontmatter.get("price_amount")
    currency = frontmatter.get("price_currency", "")
    if amount is not None:
        return f"{currency} {amount}" if currency else str(amount)
    # Nested specs fallback
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        price_spec = specs.get("price", {})
        if isinstance(price_spec, dict):
            a = price_spec.get("amount")
            c = price_spec.get("currency", "")
            if a is not None:
                return f"{c} {a}" if c else str(a)
    legacy_price = frontmatter.get("price", "")
    return str(legacy_price) if legacy_price else ""


def format_table_cell(value: str, max_width: int = 50) -> str:
    """Format a value for Markdown table cell."""
    if not value:
        return "--"
    if len(value) > max_width:
        return value[: max_width - 3] + "..."
    return value


def extract_price_amount(price_str: str) -> float | None:
    """Extract numeric price amount from price string.

    Handles both European (3.000,00) and US (3,000.00) formats.
    For price ranges, uses the first (lower) price.
    """
    if not price_str or price_str == "--":
        return None

    matches = re.findall(r"\d+(?:[.,]\d+)*", price_str)
    if matches:
        try:
            first_num_str = matches[0]
            if "," in first_num_str and "." in first_num_str:
                comma_pos = first_num_str.rindex(",")
                dot_pos = first_num_str.rindex(".")
                if comma_pos > dot_pos:
                    first_num_str = first_num_str.replace(".", "").replace(",", ".")
                else:
                    first_num_str = first_num_str.replace(",", "")
            elif "," in first_num_str:
                parts = first_num_str.split(",")
                if len(parts[-1]) == 2:
                    first_num_str = first_num_str.replace(",", ".")
                else:
                    first_num_str = first_num_str.replace(",", "")
            elif "." in first_num_str:
                parts = first_num_str.split(".")
                if len(parts[-1]) == 2:
                    pass
                else:
                    first_num_str = first_num_str.replace(".", "")
            return float(first_num_str)
        except (ValueError, IndexError):
            return None
    return None


def categorize_bikes_by_price(
    bikes: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Categorize bikes into price ranges."""
    categories: dict[str, list[dict[str, Any]]] = {
        "Under 3000": [],
        "3000-4000": [],
        "4000+": [],
        "No Price": [],
    }
    for bike in bikes:
        bike_price = bike.get("price")
        price_str = str(bike_price) if bike_price else ""
        price_amount = extract_price_amount(price_str)
        if price_amount is None:
            categories["No Price"].append(bike)
        elif price_amount < 3000:
            categories["Under 3000"].append(bike)
        elif price_amount < 4000:
            categories["3000-4000"].append(bike)
        else:
            categories["4000+"].append(bike)
    return categories


def generate_bike_table_for_category(
    bikes: list[dict[str, Any]],
    category_name: str,
    use_relative_links: bool = False,
) -> str:
    """Generate Markdown table for a single price category."""
    if not bikes:
        return ""
    lines = []
    lines.append(f"### {category_name}\n")
    lines.append("| Image | Bike | Brand | Price | Motor | Battery | Range |")
    lines.append("|-------|------|-------|-------|-------|---------|-------|")
    sorted_bikes = sorted(
        bikes,
        key=lambda b: (
            str(b.get("brand", "")).lower(),
            str(b.get("title", "")).lower(),
        ),
    )
    for bike in sorted_bikes:
        bike_price = bike.get("price")
        bike_price_str = str(bike_price) if bike_price else ""
        if bike.get("image"):
            image_col = f"![img]({bike['image']})"
        else:
            image_col = "--"
        if use_relative_links:
            file_path_obj = bike.get("file_path", "")
            file_path = str(file_path_obj).replace("vault/notes/bikes/", "")
        else:
            file_path_obj = bike.get("file_path", "")
            file_path = str(file_path_obj)
        title_obj = bike.get("title", "")
        bike_link = f"[{title_obj}]({file_path})"
        brand_obj = bike.get("brand", "")
        brand = format_table_cell(str(brand_obj), 20)
        price = format_table_cell(bike_price_str, 15)
        motor_obj = bike.get("motor", "")
        motor = format_table_cell(str(motor_obj), 20)
        battery_obj = bike.get("battery", "")
        battery = format_table_cell(str(battery_obj), 15)
        range_obj = bike.get("range", "")
        range_val = format_table_cell(str(range_obj), 15)
        lines.append(
            f"| {image_col} | {bike_link} | {brand} | {price} | "
            f"{motor} | {battery} | {range_val} |"
        )
    return "\n".join(lines) + "\n"


def generate_bike_table(
    bikes: list[dict[str, Any]], use_relative_links: bool = False
) -> str:
    """Generate Markdown tables from bikes list, split by price range."""
    if not bikes:
        return "No bikes found.\n"
    lines = []
    lines.append("## Bike Models by Price Range\n")
    categorized = categorize_bikes_by_price(bikes)
    for category in ["Under 3000", "3000-4000", "4000+", "No Price"]:
        if categorized[category]:
            table = generate_bike_table_for_category(
                categorized[category], category, use_relative_links
            )
            lines.append(table)
    return "\n".join(lines)


def update_file_with_table(
    file_path: Path, table_content: str, use_relative_links: bool = False
) -> None:
    """Update a file with the bike table between markers."""
    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return
    if use_relative_links:
        table_content = table_content.replace("vault/notes/bikes/", "")
    file_content = file_path.read_text(encoding="utf-8")
    start_marker = "<!-- BIKES_TABLE_START -->"
    end_marker = "<!-- BIKES_TABLE_END -->"
    if start_marker in file_content and end_marker in file_content:
        pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
        new_section = f"{start_marker}\n\n{table_content}\n{end_marker}"
        updated_content = re.sub(pattern, new_section, file_content, flags=re.DOTALL)
    else:
        new_section = f"\n{start_marker}\n\n{table_content}\n{end_marker}\n"
        updated_content = file_content + new_section
    file_path.write_text(updated_content, encoding="utf-8")
    print(f"[OK] Updated {file_path}")
