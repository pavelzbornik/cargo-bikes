#!/usr/bin/env python3
"""Generate brand index pages from bike files."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml


def extract_frontmatter(content: str) -> dict[str, object] | None:
    """Extract YAML frontmatter from Markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        fm_data = yaml.safe_load(match.group(1))
        return fm_data if isinstance(fm_data, dict) else None
    except yaml.YAMLError:
        return None


def collect_bikes_by_brand() -> dict[str, list[dict[str, object]]]:
    """Collect all bikes organized by brand."""
    bikes_dir = Path("vault/notes/bikes")
    bikes_by_brand: dict[str, list[dict[str, object]]] = defaultdict(list)

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
                                "brand", brand_dir.name.replace("-", " ").title()
                            ),
                            "model": frontmatter.get("model", ""),
                            "category": category,
                        }
                    )
            except Exception:
                pass

    return bikes_by_brand


def generate_brand_index(brand_key: str, bikes: list[dict[str, object]]) -> str:
    """Generate brand index page content."""
    if not bikes:
        return ""

    brand_name = bikes[0].get("brand", "")
    brand_name_str = str(brand_name) if brand_name else ""

    # Create proper markdown links with real filenames
    def bike_link(bike: dict[str, object]) -> str:
        title = bike.get("title", "")
        filename = bike.get("filename", "")
        return f"- [{title}]({filename}.md)"

    models_list = "\n".join([bike_link(bike) for bike in bikes])

    content = f'''---
title: "{brand_name_str}"
type: "brand-index"
brand: "{brand_name_str}"
tags: [brand, index, {brand_key}]
date: {date.today()}
url: ""
image: ""
summary: "{brand_name_str} is a cargo bike manufacturer offering diverse models for families and professionals."
category: "longtail"
regions: ["EU"]
founded_year: null
headquarters: null
---

## Overview

{brand_name_str} is a cargo bike manufacturer dedicated to providing practical cargo bike solutions for urban families and professionals.

## Models in Vault

{models_list}

*Note: This vault currently documents {len(bikes)} {brand_name} model(s). The brand may offer additional models not yet documented.*

## Regional Availability

The brand is available through regional dealers and online channels. Availability varies by region and model.

## Brand Philosophy & Positioning

{brand_name_str} focuses on delivering reliable, functional cargo bikes designed to make urban transport easier and more sustainable.
'''

    return content


def main() -> None:
    """Generate all brand index pages."""
    bikes_dir = Path("vault/notes/bikes")
    bikes_by_brand = collect_bikes_by_brand()

    created = 0
    for brand_key in sorted(bikes_by_brand):
        bikes = bikes_by_brand[brand_key]
        if not bikes:
            continue

        index_content = generate_brand_index(brand_key, bikes)
        index_file = bikes_dir / brand_key / "index.md"
        index_file.write_text(index_content, encoding="utf-8")

        created += 1
        print(f"✓ {brand_key}: {len(bikes)} models")

    print(f"\n✓ Successfully generated {created} brand index pages!")


if __name__ == "__main__":
    main()
