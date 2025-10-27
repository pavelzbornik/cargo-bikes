#!/usr/bin/env python3
"""Generate bike table from YAML frontmatter in vault/notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def extract_frontmatter(content: str) -> dict[str, object] | None:
    """Extract YAML frontmatter from Markdown file content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    yaml_content = match.group(1)
    try:
        fm_data = yaml.safe_load(yaml_content)
        return fm_data if isinstance(fm_data, dict) else None
    except yaml.YAMLError as e:
        print(f"  [WARN] YAML parse error: {e}")
        return None


def validate_bike_frontmatter(frontmatter: dict[str, object]) -> bool:
    """Validate that frontmatter has required bike fields.

    Supports both legacy format (top-level fields) and new schema format (specs).
    """
    required_fields = ["title", "type", "tags"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        msg = f"Missing required fields: {', '.join(missing)}"
        print(f"  [ERR] {msg}")
        return False
    if frontmatter.get("type") != "bike":
        typ = frontmatter.get("type")
        print(f"  [SKIP] Not a bike entry (type={typ})")
        return False
    return True


def extract_spec_value(
    specs: dict[str, object] | None, keys: list[str], default: str = ""
) -> str:
    """Extract a nested value from specs object with fallback to default.

    Args:
        specs: The specs dictionary (or None)
        keys: List of keys to traverse (e.g., ["motor", "power_w"])
        default: Default value if key path not found

    Returns:
        The value as a string, or default if not found
    """
    if not specs or not isinstance(specs, dict):
        return default
    value: object = specs
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    if value is None:
        return default
    # Format numeric values with appropriate units
    if len(keys) >= 1 and keys[-1] == "power_w" and isinstance(value, (int, float)):
        return f"{value}W"
    if len(keys) >= 1 and keys[-1] == "capacity_wh" and isinstance(value, (int, float)):
        return f"{value}Wh"
    if len(keys) >= 1 and keys[-1] == "estimate_km" and isinstance(value, (int, float)):
        return f"{value}km"
    return str(value) if value else default


def get_motor_display(frontmatter: dict[str, object]) -> str:
    """Extract motor information for display.

    Supports both legacy 'motor' field and new 'specs.motor.power_w' structure.
    """
    # Try new schema first
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        motor_spec = specs.get("motor", {})
        if isinstance(motor_spec, dict):
            power_w = motor_spec.get("power_w")
            if power_w is not None:
                make = motor_spec.get("make", "")
                if make:
                    return f"{make} {power_w}W"
                return f"{power_w}W"
    # Fall back to legacy format
    legacy_motor = frontmatter.get("motor", "")
    return str(legacy_motor) if legacy_motor else ""


def get_battery_display(frontmatter: dict[str, object]) -> str:
    """Extract battery information for display.

    Supports both legacy 'battery' field and new 'specs.battery.capacity_wh' structure.
    """
    # Try new schema first
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        battery_spec = specs.get("battery", {})
        if isinstance(battery_spec, dict):
            capacity_wh = battery_spec.get("capacity_wh")
            if capacity_wh is not None:
                return f"{capacity_wh}Wh"
    # Fall back to legacy format
    legacy_battery = frontmatter.get("battery", "")
    return str(legacy_battery) if legacy_battery else ""


def get_range_display(frontmatter: dict[str, object]) -> str:
    """Extract range information for display.

    Supports both legacy 'range' field and new 'specs.range.estimate_km' structure.
    """
    # Try new schema first
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        range_spec = specs.get("range", {})
        if isinstance(range_spec, dict):
            estimate_km = range_spec.get("estimate_km")
            if estimate_km is not None:
                return f"{estimate_km}km"
    # Fall back to legacy format
    legacy_range = frontmatter.get("range", "")
    return str(legacy_range) if legacy_range else ""


def get_price_display(frontmatter: dict[str, object]) -> str:
    """Extract price information for display.

    Supports both legacy 'price' field and new 'specs.price.amount' structure.
    """
    # Try new schema first
    specs = frontmatter.get("specs")
    if specs and isinstance(specs, dict):
        price_spec = specs.get("price", {})
        if isinstance(price_spec, dict):
            amount = price_spec.get("amount")
            currency = price_spec.get("currency", "")
            if amount is not None:
                if currency:
                    return f"{currency} {amount}"
                return str(amount)
    # Fall back to legacy format
    legacy_price = frontmatter.get("price", "")
    return str(legacy_price) if legacy_price else ""


def collect_bikes() -> list[dict[str, object]]:
    """Collect all bikes from vault/notes/bikes.

    Supports both legacy format and new BIKE_SPECS_SCHEMA format.
    """
    bikes: list[dict[str, object]] = []
    vault_notes = Path("vault/notes/bikes")
    if not vault_notes.exists():
        print(f"Error: {vault_notes} not found")
        return bikes
    print(f"\nScanning {vault_notes}...\n")
    for md_file in sorted(vault_notes.glob("*/*.md")):
        rel_path = md_file.relative_to("vault/notes/bikes")
        brand_folder = md_file.parent.name
        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter = extract_frontmatter(content)
            if frontmatter is None:
                print(f"[ERR] {rel_path}: No YAML frontmatter found")
                continue
            if not validate_bike_frontmatter(frontmatter):
                continue
            # Extract values with support for both legacy and new schema
            title = frontmatter.get("title", "")
            brand = frontmatter.get("brand", brand_folder)
            model = frontmatter.get("model", "")
            image = frontmatter.get("image", "")
            url = frontmatter.get("url", "")
            motor = get_motor_display(frontmatter)
            battery = get_battery_display(frontmatter)
            range_val = get_range_display(frontmatter)
            price = get_price_display(frontmatter)
            file_path_str = f"vault/notes/bikes/{rel_path}".replace("\\", "/")
            bike = {
                "title": title,
                "brand": brand,
                "model": model,
                "price": price,
                "motor": motor,
                "battery": battery,
                "range": range_val,
                "image": image,
                "url": url,
                "file_path": file_path_str,
                "tags": frontmatter.get("tags", []),
                "frontmatter": frontmatter,  # Store full FM for reference
            }
            bikes.append(bike)
            print(f"[OK] {rel_path}: {title}")
        except Exception as e:
            err_type = type(e).__name__
            print(f"[ERR] {rel_path}: {err_type}: {e}")
    return bikes


def format_table_cell(value: str, max_width: int = 50) -> str:
    """Format a value for Markdown table cell."""
    if not value:
        return "--"
    if len(value) > max_width:
        return value[: max_width - 3] + "..."
    return value


def extract_price_amount(price_str: str) -> float | None:
    """Extract numeric price amount from price string.

    For price ranges, uses the first (lower) price.
    Handles both European (3.000,00) and US (3,000.00) formats.

    Args:
        price_str: Price string like "€ 2500" or "USD 3200" or "2500-3000"

    Returns:
        Numeric price as float, or None if not extractable
    """
    if not price_str or price_str == "--":
        return None
    # Extract numbers and separators from the string
    import re

    # Find all full numbers including thousands and decimal separators
    # Matches: 1234, 1,234, 1.234, 1,234.56, 1.234,56, etc.
    matches = re.findall(r"\d+(?:[.,]\d+)*", price_str)
    if matches:
        try:
            first_num_str = matches[0]
            # Determine the number format by analyzing separators
            if "," in first_num_str and "." in first_num_str:
                # Both separators present
                comma_pos = first_num_str.rindex(",")
                dot_pos = first_num_str.rindex(".")
                if comma_pos > dot_pos:
                    # Comma is last (1.234,56 - European format)
                    first_num_str = first_num_str.replace(".", "").replace(",", ".")
                else:
                    # Dot is last (1,234.56 - US format)
                    first_num_str = first_num_str.replace(",", "")
            elif "," in first_num_str:
                # Only comma
                parts = first_num_str.split(",")
                if len(parts[-1]) == 2:
                    # Likely decimal (3,99)
                    first_num_str = first_num_str.replace(",", ".")
                else:
                    # Likely thousands (3,715 or 1,000,000)
                    first_num_str = first_num_str.replace(",", "")
            elif "." in first_num_str:
                # Only dot
                parts = first_num_str.split(".")
                if len(parts[-1]) == 2:
                    # Likely decimal (3.99)
                    pass
                else:
                    # Likely thousands (3.715 or 1.000.000)
                    first_num_str = first_num_str.replace(".", "")
            return float(first_num_str)
        except (ValueError, IndexError):
            return None
    return None


def categorize_bikes_by_price(
    bikes: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    """Categorize bikes into price ranges.

    Price ranges:
    - "Under 3000": < 3000
    - "3000-4000": 3000 to < 4000
    - "4000+": >= 4000

    Args:
        bikes: List of bike dictionaries

    Returns:
        Dictionary with price range keys and bike lists as values
    """
    categories: dict[str, list[dict[str, object]]] = {
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
    bikes: list[dict[str, object]], category_name: str, use_relative_links: bool = False
) -> str:
    """Generate Markdown table for a single price category.

    Args:
        bikes: List of bike dictionaries for this category
        category_name: Name of the price category
        use_relative_links: If True, use relative links

    Returns:
        Markdown table string
    """
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
        # Use relative path for index.md, full path for README.md
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
    bikes: list[dict[str, object]], use_relative_links: bool = False
) -> str:
    """Generate Markdown tables from bikes list, split by price range.

    Args:
        bikes: List of bike dictionaries
        use_relative_links: If True, use relative links
    """
    if not bikes:
        return "No bikes found.\n"
    lines = []
    lines.append("## Bike Models by Price Range\n")
    categorized = categorize_bikes_by_price(bikes)
    # Generate tables in order, skipping empty categories
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
    """Update a file with the bike table between markers.

    Args:
        file_path: Path to the file to update
        table_content: Generated table content
        use_relative_links: If True, adjust paths for relative links
    """
    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return
    # Adjust paths if needed for relative links
    # For index.md at vault/notes/, change "vault/notes/bikes/" to ""
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


def main() -> None:
    """Main entry point."""
    print("=" * 70)
    print("CARGO BIKES TABLE GENERATOR")
    print("=" * 70)
    bikes = collect_bikes()
    print(f"\n{'-' * 70}")
    print(f"Total bikes found: {len(bikes)}\n")
    if not bikes:
        print("No valid bikes to generate table from.")
        return
    table_content = generate_bike_table(bikes)
    print("\nGenerated table preview (first 800 chars):")
    print(table_content[:800])
    if len(table_content) > 800:
        print("...\n")
    print(f"\n{'-' * 70}")
    print("Updating files with bike table...\n")
    update_file_with_table(Path("README.md"), table_content)
    update_file_with_table(
        Path("vault/notes/bikes/index.md"),
        table_content,
        use_relative_links=True,
    )
    print(f"{'-' * 70}")
    print("[OK] Done!")


if __name__ == "__main__":
    main()
