#!/usr/bin/env python3
"""Generate brand index pages from bike files."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml


def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from Markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def collect_bikes_by_brand() -> dict[str, list[dict]]:
    """Collect all bikes organized by brand."""
    bikes_dir = Path("vault/notes/bikes")
    bikes_by_brand: dict[str, list[dict]] = defaultdict(list)

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
                    bikes_by_brand[brand_dir.name].append(
                        {
                            "title": frontmatter.get("title", ""),
                            "brand": frontmatter.get(
                                "brand", brand_dir.name.replace("-", " ").title()
                            ),
                            "model": frontmatter.get("model", ""),
                            "category": frontmatter.get("specs", {}).get(
                                "category", "longtail"
                            )
                            if isinstance(frontmatter.get("specs"), dict)
                            else "longtail",
                        }
                    )
            except Exception:
                pass

    return bikes_by_brand


def generate_brand_index(brand_key: str, bikes: list[dict]) -> str:
    """Generate brand index page content."""
    if not bikes:
        return ""

    brand_name = bikes[0]["brand"]
    models_list = "\n".join([f"- **[[{bike['title']}]]**" for bike in bikes])

    content = f'''---
title: "{brand_name}"
type: "brand-index"
brand: "{brand_name}"
tags: [brand, index, {brand_key}]
date: {date.today()}
url: ""
image: ""
summary: "{brand_name} is a cargo bike manufacturer offering diverse models for families and professionals."
category: "longtail"
regions: ["EU"]
founded_year: null
headquarters: null
---

## Overview

{brand_name} is a cargo bike manufacturer dedicated to providing practical cargo bike solutions for urban families and professionals.

## Models in Vault

{models_list}

*Note: This vault currently documents {len(bikes)} {brand_name} model(s). The brand may offer additional models not yet documented.*

## Regional Availability

The brand is available through regional dealers and online channels. Availability varies by region and model.

## Brand Philosophy & Positioning

{brand_name} focuses on delivering reliable, functional cargo bikes designed to make urban transport easier and more sustainable.
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
