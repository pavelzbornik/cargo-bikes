"""Generate brand index pages from bike files."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any


def generate_brand_index(brand_key: str, bikes: list[dict[str, Any]]) -> str:
    """Generate brand index page content.

    Args:
        brand_key: Brand folder name (e.g., "benno").
        bikes: List of bike metadata dicts for this brand.

    Returns:
        Markdown content for the brand index page.
    """
    if not bikes:
        return ""

    brand_name = bikes[0].get("brand", "")
    brand_name_str = str(brand_name) if brand_name else ""

    def bike_link(bike: dict[str, Any]) -> str:
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
