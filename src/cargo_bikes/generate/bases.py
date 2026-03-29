"""Generate Obsidian Bases (.base) files from database state.

Bases files use YAML format with Obsidian's filter expression syntax.
See: https://help.obsidian.md/bases/syntax

Uses string templates instead of yaml.dump to guarantee the exact
indentation format that Obsidian expects.
"""

from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine, distinct, select
from sqlalchemy.orm import Session

from cargo_bikes.db.schema import Bike


def _table_view(
    name: str,
    fields: list[str],
    filters: list[str] | None = None,
) -> str:
    """Generate a single table view YAML block."""
    lines = [
        f"  - type: table",
        f'    name: "{name}"',
    ]
    if filters:
        lines.append("    filters:")
        lines.append("      and:")
        for f in filters:
            lines.append(f"        - '{f}'")
    lines.append("    order:")
    for field in fields:
        lines.append(f"      - {field}")
    return "\n".join(lines)


def _cards_view(
    name: str,
    fields: list[str],
    filters: list[str] | None = None,
) -> str:
    """Generate a single cards view YAML block."""
    lines = [
        f"  - type: cards",
        f'    name: "{name}"',
    ]
    if filters:
        lines.append("    filters:")
        lines.append("      and:")
        for f in filters:
            lines.append(f"        - '{f}'")
    lines.append("    order:")
    for field in fields:
        lines.append(f"      - {field}")
    return "\n".join(lines)


BIKE_FIELDS = ["title", "brand", "price_amount", "motor_make", "battery_capacity_wh", "range_estimate_km"]
MOTOR_FIELDS = ["title", "brand", "motor_model", "motor_torque_nm", "motor_power_w", "battery_capacity_wh", "price_amount"]


def generate_bikes_by_price(session: Session) -> str:
    """Generate bikes-by-price.base content."""
    views = "\n".join([
        _table_view("Under 3,000 EUR", BIKE_FIELDS, ['price_amount < 3000']),
        _table_view("3,000-4,000 EUR", BIKE_FIELDS, ['price_amount >= 3000', 'price_amount < 4000']),
        _table_view("4,000+ EUR", BIKE_FIELDS, ['price_amount >= 4000']),
    ])
    return f"filters:\n  and:\n    - 'type == \"bike\"'\nviews:\n{views}"


def generate_bikes_by_category(session: Session) -> str:
    """Generate bikes-by-category.base content."""
    categories = sorted(
        r[0]
        for r in session.execute(
            select(distinct(Bike.category)).where(Bike.category.isnot(None))
        ).all()
    )

    cat_fields = ["title", "brand", "price_amount", "motor_torque_nm", "load_capacity_total_kg", "weight_bike_kg"]
    views = "\n".join([
        _table_view(
            cat.replace("-", " ").title(),
            cat_fields,
            [f'category == "{cat}"'],
        )
        for cat in categories
    ])
    return f"filters:\n  and:\n    - 'type == \"bike\"'\nviews:\n{views}"


def generate_brands_base(session: Session) -> str:
    """Generate brands.base content."""
    table = _table_view("All Brands", ["title", "country", "headquarters_city", "model_count", "price_tier", "categories", "regions"])
    cards = _cards_view("Brand Cards", ["title", "logo", "summary", "categories", "price_tier", "country"])
    return f"filters:\n  or:\n    - 'type == \"brand\"'\n    - 'type == \"brand-index\"'\nviews:\n{table}\n{cards}"


def generate_motors_base(session: Session) -> str:
    """Generate motors.base content with views per motor manufacturer."""
    motor_makes = sorted(
        r[0]
        for r in session.execute(
            select(distinct(Bike.motor_make)).where(Bike.motor_make.isnot(None))
        ).all()
    )

    views = "\n".join([
        _table_view(f"{make} Motors", MOTOR_FIELDS, [f'motor_make == "{make}"'])
        for make in motor_makes
    ])
    return f"filters:\n  and:\n    - 'type == \"bike\"'\nviews:\n{views}"


def generate_components_base(session: Session) -> str:
    """Generate components.base content."""
    table_all = _table_view("All Components", ["title", "category", "parent", "type"])
    table_motors = _table_view("Motors", ["title", "parent", "torque_nm", "power_w", "motor_type"], ['category == "motors"'])
    return f"filters:\n  or:\n    - 'type == \"component\"'\n    - 'type == \"component-manufacturer\"'\nviews:\n{table_all}\n{table_motors}"


def generate_accessories_base(session: Session) -> str:
    """Generate accessories.base content."""
    table_all = _table_view("All Accessories", ["title", "category", "manufacturer", "price_amount"])
    table_seats = _table_view("Child Seats", ["title", "manufacturer", "price_amount"], ['category == "child-seats"'])
    table_weather = _table_view("Weather Protection", ["title", "manufacturer", "price_amount"], ['category == "weather-protection"'])
    table_racks = _table_view("Racks & Panniers", ["title", "manufacturer", "price_amount"], ['category == "racks" || category == "panniers"'])
    return f"filters:\n  and:\n    - 'type == \"accessory\"'\nviews:\n{table_all}\n{table_seats}\n{table_weather}\n{table_racks}"


def generate_all_bases(
    vault_path: Path = Path("vault"),
    db_path: Path = Path("vault.db"),
) -> None:
    """Generate all .base files from current database state."""
    engine = create_engine(f"sqlite:///{db_path.resolve()}", echo=False)

    base_files: dict[str, callable] = {
        "bikes-by-price.base": generate_bikes_by_price,
        "bikes-by-category.base": generate_bikes_by_category,
        "brands.base": generate_brands_base,
        "motors.base": generate_motors_base,
        "components.base": generate_components_base,
        "accessories.base": generate_accessories_base,
    }

    with Session(engine) as session:
        for filename, generator in base_files.items():
            content = generator(session)
            output_path = vault_path / filename
            output_path.write_text(content + "\n", encoding="utf-8")
            print(f"✓ Generated {output_path}")

    print(f"\n✓ Generated {len(base_files)} .base files")
