"""Web-ready content generation: buying guides, brand profiles, component guides."""

from __future__ import annotations

import asyncio
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cargo_bikes.db.schema import Bike, Brand
from cargo_bikes.enrich.agent import call_agent
from cargo_bikes.enrich.prompts import (
    BRAND_PROFILE_SYSTEM,
    BUYING_GUIDE_SYSTEM,
    COMPONENT_GUIDE_SYSTEM,
)


def _slugify(text: str) -> str:
    """Convert text to a URL/filename-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


def generate_buying_guide(
    topic: str,
    vault_path: Path = Path("vault"),
    db_path: Path = Path("vault.db"),
    model: str = "claude-sonnet-4-6",
) -> Path:
    """Generate a buying guide on a given topic.

    Args:
        topic: Guide topic (e.g., "Best longtails under 4000 EUR").
        vault_path: Path to vault root.
        db_path: Path to database.
        model: Claude model to use.

    Returns:
        Path to the generated guide file.
    """
    from rich.console import Console

    console = Console()

    engine = create_engine(f"sqlite:///{db_path.resolve()}", echo=False)

    with Session(engine) as session:
        bikes = list(session.execute(select(Bike)).scalars().all())

    bike_data = []
    for bike in bikes:
        bike_data.append(
            f"- {bike.title} ({bike.brand_name}): "
            f"€{bike.price_amount or '?'}, "
            f"{bike.motor_make or '?'} {bike.motor_power_w or '?'}W, "
            f"{bike.battery_capacity_wh or '?'}Wh, "
            f"range {bike.range_estimate_km or '?'}km, "
            f"category: {bike.category or '?'}"
        )

    prompt = f"""Write a buying guide on: "{topic}"

Available bikes in the vault:
{chr(10).join(bike_data)}

Generate a complete Obsidian markdown note with proper frontmatter.
"""

    result = asyncio.run(
        call_agent(prompt=prompt, system=BUYING_GUIDE_SYSTEM, model=model)
    )

    slug = _slugify(topic)
    output_path = vault_path / "notes" / "guides" / f"{slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result + "\n", encoding="utf-8")

    console.print(f"[green]✓ Generated guide: {output_path}[/green]")
    return output_path


def generate_brand_profile(
    brand_name: str,
    vault_path: Path = Path("vault"),
    db_path: Path = Path("vault.db"),
    model: str = "claude-sonnet-4-6",
) -> Path:
    """Generate a rich brand profile page.

    Args:
        brand_name: Brand folder name (e.g., "benno").
        vault_path: Path to vault root.
        db_path: Path to database.
        model: Claude model to use.

    Returns:
        Path to the generated brand profile file.
    """
    from rich.console import Console

    console = Console()

    engine = create_engine(f"sqlite:///{db_path.resolve()}", echo=False)

    with Session(engine) as session:
        bikes = list(
            session.execute(
                select(Bike).where(Bike.brand_name.ilike(f"%{brand_name}%"))
            )
            .scalars()
            .all()
        )
        brand = session.execute(
            select(Brand).where(Brand.title.ilike(f"%{brand_name}%"))
        ).scalar_one_or_none()

    bike_data = []
    for bike in bikes:
        bike_data.append(
            f"- {bike.title}: {bike.category or '?'}, "
            f"€{bike.price_amount or '?'}, "
            f"{bike.motor_make or '?'} {bike.motor_power_w or '?'}W"
        )

    brand_info = ""
    if brand:
        brand_info = f"""
Brand DB record:
- Title: {brand.title}
- URL: {brand.url or 'unknown'}
- Country: {brand.country or 'unknown'}
- Summary: {brand.summary or 'none'}
- Categories: {brand.categories or 'unknown'}
- Price tier: {brand.price_tier or 'unknown'}
"""

    prompt = f"""Write a rich brand profile for: {brand_name}

{brand_info}

Models in vault ({len(bikes)} bikes):
{chr(10).join(bike_data)}

Generate a complete Obsidian markdown note with proper frontmatter.
Use web search to find brand history, founding details, and headquarters.
"""

    result = asyncio.run(
        call_agent(
            prompt=prompt,
            system=BRAND_PROFILE_SYSTEM,
            model=model,
            max_turns=10,
            allowed_tools=["WebSearch", "WebFetch"],
        )
    )

    # Find the brand folder
    brand_dir = vault_path / "notes" / "bikes" / brand_name
    if not brand_dir.exists():
        # Try to find a matching folder
        bikes_dir = vault_path / "notes" / "bikes"
        for d in bikes_dir.iterdir():
            if d.is_dir() and brand_name.lower() in d.name.lower():
                brand_dir = d
                break

    output_path = brand_dir / "index.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result + "\n", encoding="utf-8")

    console.print(f"[green]✓ Generated brand profile: {output_path}[/green]")
    return output_path


def generate_component_guide(
    component_type: str,
    vault_path: Path = Path("vault"),
    db_path: Path = Path("vault.db"),
    model: str = "claude-sonnet-4-6",
) -> Path:
    """Generate a component guide (e.g., motors, batteries, brakes).

    Args:
        component_type: Component category (motors, batteries, brakes, etc.).
        vault_path: Path to vault root.
        db_path: Path to database.
        model: Claude model to use.

    Returns:
        Path to the generated guide file.
    """
    from rich.console import Console

    console = Console()

    engine = create_engine(f"sqlite:///{db_path.resolve()}", echo=False)

    with Session(engine) as session:
        bikes = list(session.execute(select(Bike)).scalars().all())

    # Aggregate component data based on type
    component_data: list[str] = []
    if component_type == "motors":
        seen = set()
        for bike in bikes:
            key = f"{bike.motor_make}|{bike.motor_model}"
            if key not in seen and bike.motor_make:
                seen.add(key)
                component_data.append(
                    f"- {bike.motor_make} {bike.motor_model or ''}: "
                    f"{bike.motor_power_w or '?'}W, {bike.motor_torque_nm or '?'}Nm, "
                    f"type: {bike.motor_type or '?'} "
                    f"(used by: {bike.title})"
                )
    elif component_type == "batteries":
        seen = set()
        for bike in bikes:
            if bike.battery_capacity_wh:
                key = f"{bike.motor_make}|{bike.battery_capacity_wh}"
                if key not in seen:
                    seen.add(key)
                    component_data.append(
                        f"- {bike.battery_capacity_wh}Wh "
                        f"({bike.battery_configuration or 'single'}): "
                        f"removable={bike.battery_removable}, "
                        f"used by: {bike.title}"
                    )
    elif component_type == "brakes":
        seen = set()
        for bike in bikes:
            if bike.brakes_type and bike.brakes_type not in seen:
                seen.add(bike.brakes_type)
                component_data.append(
                    f"- {bike.brakes_type}: "
                    f"front {bike.brakes_front_rotor_mm or '?'}mm, "
                    f"rear {bike.brakes_rear_rotor_mm or '?'}mm "
                    f"(used by: {bike.title})"
                )

    prompt = f"""Write a component guide about: {component_type}

Component data from vault bikes:
{chr(10).join(component_data) if component_data else 'No data available'}

Generate a complete Obsidian markdown note with proper frontmatter.
"""

    result = asyncio.run(
        call_agent(prompt=prompt, system=COMPONENT_GUIDE_SYSTEM, model=model)
    )

    slug = _slugify(component_type)
    output_path = vault_path / "notes" / "components" / f"{slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result + "\n", encoding="utf-8")

    console.print(f"[green]✓ Generated component guide: {output_path}[/green]")
    return output_path
