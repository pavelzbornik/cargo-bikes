"""Vault scanning utilities for collecting bikes and brands."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from cargo_bikes.vault.frontmatter import extract_frontmatter, validate_bike_frontmatter


def collect_bikes(vault_path: Path | None = None) -> list[dict[str, Any]]:
    """Collect all bikes from vault/notes/bikes.

    Supports both legacy format and new BIKE_SPECS_SCHEMA format.

    Args:
        vault_path: Path to vault root. Defaults to Path("vault").

    Returns:
        List of bike dictionaries with extracted metadata.
    """
    from cargo_bikes.generate.bike_table import (
        get_battery_display,
        get_motor_display,
        get_price_display,
        get_range_display,
    )

    if vault_path is None:
        vault_path = Path("vault")

    bikes_dir = vault_path / "notes" / "bikes"
    bikes: list[dict[str, Any]] = []

    if not bikes_dir.exists():
        print(f"Error: {bikes_dir} not found")
        return bikes

    print(f"\nScanning {bikes_dir}...\n")
    for md_file in sorted(bikes_dir.glob("*/*.md")):
        rel_path = md_file.relative_to(bikes_dir)
        brand_folder = md_file.parent.name

        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter = extract_frontmatter(content)

            if frontmatter is None:
                print(f"[ERR] {rel_path}: No YAML frontmatter found")
                continue

            if not validate_bike_frontmatter(frontmatter):
                continue

            title = frontmatter.get("title", "")
            brand = frontmatter.get("brand", brand_folder)
            model = frontmatter.get("model", "")
            image = frontmatter.get("image", "")
            url = frontmatter.get("url", "")
            motor = get_motor_display(frontmatter)
            battery = get_battery_display(frontmatter)
            range_val = get_range_display(frontmatter)
            price = get_price_display(frontmatter)

            file_path_str = str(
                (bikes_dir / rel_path).relative_to(vault_path.parent)
            ).replace("\\", "/")

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
                "frontmatter": frontmatter,
            }
            bikes.append(bike)
            print(f"[OK] {rel_path}: {title}")
        except Exception as e:
            err_type = type(e).__name__
            print(f"[ERR] {rel_path}: {err_type}: {e}")

    return bikes


def collect_bikes_by_brand(
    vault_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Collect all bikes organized by brand folder.

    Args:
        vault_path: Path to vault root. Defaults to Path("vault").

    Returns:
        Dict mapping brand folder names to lists of bike metadata.
    """
    if vault_path is None:
        vault_path = Path("vault")

    bikes_dir = vault_path / "notes" / "bikes"
    bikes_by_brand: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for brand_dir in sorted(bikes_dir.iterdir()):
        if not brand_dir.is_dir() or brand_dir.name.startswith("_"):
            continue

        for bike_file in sorted(brand_dir.glob("*.md")):
            if bike_file.name == "index.md":
                continue

            try:
                content = bike_file.read_text(encoding="utf-8")
                frontmatter = extract_frontmatter(content)

                if frontmatter and frontmatter.get("type") == "bike":
                    specs = frontmatter.get("specs")
                    category = "longtail"
                    if isinstance(specs, dict):
                        category = str(specs.get("category", "longtail"))

                    bikes_by_brand[brand_dir.name].append(
                        {
                            "title": frontmatter.get("title", ""),
                            "filename": bike_file.stem,
                            "brand": frontmatter.get(
                                "brand",
                                brand_dir.name.replace("-", " ").title(),
                            ),
                            "model": frontmatter.get("model", ""),
                            "category": category,
                        }
                    )
            except Exception:
                pass

    return bikes_by_brand
