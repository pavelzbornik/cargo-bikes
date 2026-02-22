"""
Data fetcher for extracting bike specifications from manufacturer websites.

Supports multiple extraction strategies:
1. JSON-LD structured data
2. Microdata/RDFa
3. HTML scraping with BeautifulSoup
4. LLM-assisted extraction (via PydanticAI) as fallback

Includes caching to avoid redundant fetches within a configurable TTL.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

from scripts.bike_note_updater.models import (
    Battery,
    BikeSpecs,
    Brakes,
    Drivetrain,
    FetchedBikeData,
    Frame,
    LoadCapacity,
    Motor,
    Price,
    Range,
    Suspension,
    Weight,
    Wheels,
)

logger = logging.getLogger("bike_note_updater.data_fetcher")

# Default settings
DEFAULT_TIMEOUT = 30
DEFAULT_CACHE_DIR = ".cache/bike_fetches"
DEFAULT_CACHE_TTL = 86400  # 24 hours

# Common user-agent for polite crawling
USER_AGENT = (
    "Mozilla/5.0 (compatible; CargoBikeResearchAgent/0.1; "
    "+https://github.com/pavelzbornik/cargo-bikes)"
)


class FetchCache:
    """Simple file-based cache for fetched HTML content."""

    def __init__(
        self, cache_dir: str = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_CACHE_TTL
    ):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, url: str) -> str | None:
        """Get cached content if it exists and is not expired."""
        if not self.cache_dir.exists():
            return None

        cache_file = self.cache_dir / f"{self._key(url)}.json"
        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if time.time() - data.get("timestamp", 0) > self.ttl:
                cache_file.unlink(missing_ok=True)
                return None
            return data.get("content")
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, url: str, content: str) -> None:
        """Cache content for a URL."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / f"{self._key(url)}.json"
        data = {"url": url, "timestamp": time.time(), "content": content}
        cache_file.write_text(json.dumps(data), encoding="utf-8")


class DataFetcher:
    """Fetches and extracts bike specification data from product pages."""

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        cache_dir: str = DEFAULT_CACHE_DIR,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        use_cache: bool = True,
    ):
        self.timeout = timeout
        self.cache = FetchCache(cache_dir, cache_ttl) if use_cache else None

    def fetch_html(self, url: str) -> str | None:
        """
        Fetch HTML content from a URL with caching.

        Args:
            url: The URL to fetch

        Returns:
            HTML content string, or None on failure
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(url)
            if cached:
                logger.debug(f"Cache hit for {url}")
                return cached

        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": USER_AGENT},
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                html = response.text

                # Cache the result
                if self.cache:
                    self.cache.set(url, html)

                return html

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def extract_json_ld(self, html: str) -> list[dict[str, Any]]:
        """
        Extract JSON-LD structured data from HTML.

        Args:
            html: Raw HTML content

        Returns:
            List of JSON-LD objects found (typically Product schema)
        """
        soup = BeautifulSoup(html, "lxml")
        results = []

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    results.extend(data)
                elif isinstance(data, dict):
                    results.append(data)
            except (json.JSONDecodeError, TypeError):
                continue

        return results

    def extract_product_from_json_ld(
        self, json_ld_items: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Extract Product data from JSON-LD items."""
        for item in json_ld_items:
            item_type = item.get("@type", "")
            if isinstance(item_type, list):
                item_type = " ".join(item_type)
            if "Product" in str(item_type):
                return item

            # Check @graph
            graph = item.get("@graph", [])
            for node in graph:
                node_type = node.get("@type", "")
                if isinstance(node_type, list):
                    node_type = " ".join(node_type)
                if "Product" in str(node_type):
                    return node

        return None

    def _parse_number(self, value: Any) -> float | None:
        """Try to parse a numeric value from various formats."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove common suffixes and currency symbols
            cleaned = re.sub(r"[€$£,\s]", "", value)
            cleaned = re.sub(
                r"(wh|w|nm|kg|cm|mm|km|h|ah)$", "", cleaned, flags=re.IGNORECASE
            )
            try:
                return float(cleaned)
            except ValueError:
                # Try to extract first number
                match = re.search(r"[\d.]+", cleaned)
                if match:
                    try:
                        return float(match.group())
                    except ValueError:
                        pass
        return None

    def _extract_specs_from_html(self, soup: BeautifulSoup) -> dict[str, str]:
        """
        Extract specification key-value pairs from common HTML patterns.

        Looks for specification tables, definition lists, and labeled sections.
        """
        specs: dict[str, str] = {}

        # Strategy 1: Look for spec tables
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value

        # Strategy 2: Look for definition lists
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                key = dt.get_text(strip=True).lower()
                value = dd.get_text(strip=True)
                if key and value:
                    specs[key] = value

        # Strategy 3: Look for labeled spans/divs (common in product pages)
        for container in soup.find_all(
            ["div", "section"],
            class_=re.compile(
                r"spec|feature|detail|characteristic|tech",
                re.IGNORECASE,
            ),
        ):
            labels = container.find_all(
                ["span", "strong", "b", "dt", "th", "label"],
            )
            for label in labels:
                key = label.get_text(strip=True).lower().rstrip(":")
                # Get the next sibling text
                next_el = label.find_next_sibling()
                if next_el and isinstance(next_el, Tag):
                    value = next_el.get_text(strip=True)
                    if key and value:
                        specs[key] = value

        return specs

    def _map_specs_to_model(self, raw_specs: dict[str, str]) -> BikeSpecs:
        """
        Map extracted raw specification strings to the BikeSpecs model.

        Uses keyword matching to identify which field each spec corresponds to.
        """
        motor_keywords = {
            "motor",
            "moteur",
            "engine",
            "drive",
            "antrieb",
        }
        battery_keywords = {
            "battery",
            "batterie",
            "akku",
            "power pack",
            "powerpack",
        }
        weight_keywords = {"weight", "poids", "gewicht", "masse"}
        torque_keywords = {"torque", "couple", "drehmoment", "nm"}
        power_keywords = {"power", "puissance", "leistung", "watt"}
        brake_keywords = {"brake", "frein", "bremse"}
        wheel_keywords = {"wheel", "roue", "rad", "tire", "pneu", "reifen"}
        frame_keywords = {"frame", "cadre", "rahmen", "material", "matériau"}
        speed_keywords = {
            "speed",
            "gear",
            "vitesse",
            "gang",
            "transmission",
            "derailleur",
        }
        capacity_keywords = {
            "capacity",
            "capacité",
            "load",
            "charge",
            "payload",
            "zuladung",
        }
        range_keywords = {"range", "autonomie", "reichweite"}
        suspension_keywords = {"suspension", "fork", "fourche", "federgabel"}

        motor = Motor()
        batt = Battery()
        weight = Weight()
        brakes = Brakes()
        wheels = Wheels()
        frame = Frame()
        drivetrain = Drivetrain()
        load_cap = LoadCapacity()
        range_spec = Range()
        suspension = Suspension()
        price = Price()

        for key, value in raw_specs.items():
            key_lower = key.lower()

            if any(kw in key_lower for kw in motor_keywords):
                if any(kw in key_lower for kw in torque_keywords):
                    motor.torque_nm = self._parse_number(value)
                elif any(kw in key_lower for kw in power_keywords):
                    motor.power_w = self._parse_number(value)
                else:
                    # Try to infer brand/model from the value
                    if not motor.make:
                        motor.make = value.split()[0] if value else None
            elif any(kw in key_lower for kw in battery_keywords):
                wh = self._parse_number(value)
                if wh and wh > 10:
                    batt.capacity_wh = wh
            elif any(kw in key_lower for kw in weight_keywords):
                w = self._parse_number(value)
                if w:
                    weight.with_battery_kg = w
            elif any(kw in key_lower for kw in brake_keywords):
                brakes.type = value
            elif any(kw in key_lower for kw in wheel_keywords):
                if "front" in key_lower or "avant" in key_lower:
                    wheels.front_size_in = value
                elif "rear" in key_lower or "arrière" in key_lower:
                    wheels.rear_size_in = value
                elif "tire" in key_lower or "pneu" in key_lower:
                    wheels.tire = value
            elif any(kw in key_lower for kw in frame_keywords):
                frame.material = value
            elif any(kw in key_lower for kw in speed_keywords):
                drivetrain.speeds = value
            elif any(kw in key_lower for kw in capacity_keywords):
                cap = self._parse_number(value)
                if cap:
                    load_cap.total_kg = cap
            elif any(kw in key_lower for kw in range_keywords):
                range_spec.estimate_km = value
            elif any(kw in key_lower for kw in suspension_keywords):
                if "front" in key_lower or "avant" in key_lower:
                    suspension.front = value
                elif "rear" in key_lower or "arrière" in key_lower:
                    suspension.rear = value
                else:
                    suspension.front = value
            elif "price" in key_lower or "prix" in key_lower or "preis" in key_lower:
                amt = self._parse_number(value)
                if amt:
                    price.amount = amt
                if "€" in value or "eur" in value.lower():
                    price.currency = "EUR"
                elif "$" in value or "usd" in value.lower():
                    price.currency = "USD"
                elif "£" in value or "gbp" in value.lower():
                    price.currency = "GBP"

        # Only include non-empty sub-models
        specs = BikeSpecs()
        if motor.make or motor.model or motor.power_w or motor.torque_nm:
            specs.motor = motor
        if batt.capacity_wh:
            specs.battery = batt
        if weight.bike_kg or weight.with_battery_kg:
            specs.weight = weight
        if brakes.type:
            specs.brakes = brakes
        if wheels.front_size_in or wheels.rear_size_in or wheels.tire:
            specs.wheels = wheels
        if frame.material:
            specs.frame = frame
        if drivetrain.type or drivetrain.speeds:
            specs.drivetrain = drivetrain
        if load_cap.total_kg:
            specs.load_capacity = load_cap
        if range_spec.estimate_km:
            specs.range = range_spec
        if suspension.front or suspension.rear:
            specs.suspension = suspension
        if price.amount:
            specs.price = price

        return specs

    def extract_from_url(self, url: str) -> FetchedBikeData | None:
        """
        Fetch a product page and extract bike data using all strategies.

        Args:
            url: The product page URL

        Returns:
            FetchedBikeData with extracted specs, or None on failure
        """
        html = self.fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        # Extract basic page info
        title = None
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Get page text for context
        raw_text = soup.get_text(separator="\n", strip=True)
        # Truncate to reasonable length
        if len(raw_text) > 10000:
            raw_text = raw_text[:10000]

        # Strategy 1: JSON-LD
        json_ld_items = self.extract_json_ld(html)
        product_data = self.extract_product_from_json_ld(json_ld_items)

        if product_data:
            specs = self._parse_json_ld_product(product_data)
            image_url = self._extract_image(product_data, soup)
            return FetchedBikeData(
                source_url=url,
                title=product_data.get("name", title),
                specs=specs,
                image_url=image_url,
                raw_text=raw_text,
                extraction_method="json_ld",
            )

        # Strategy 2: HTML spec extraction
        raw_specs = self._extract_specs_from_html(soup)
        if raw_specs:
            specs = self._map_specs_to_model(raw_specs)
            image_url = self._extract_image_from_html(soup)
            return FetchedBikeData(
                source_url=url,
                title=title,
                specs=specs,
                image_url=image_url,
                raw_text=raw_text,
                extraction_method="scraping",
            )

        # Strategy 3: Return raw text for LLM-based extraction
        return FetchedBikeData(
            source_url=url,
            title=title,
            raw_text=raw_text,
            extraction_method="raw_text_only",
        )

    def _parse_json_ld_product(self, product: dict[str, Any]) -> BikeSpecs:
        """Parse a JSON-LD Product object into BikeSpecs."""
        specs = BikeSpecs()

        # Extract price from offers
        offers = product.get("offers", {})
        if isinstance(offers, list) and offers:
            offers = offers[0]
        if isinstance(offers, dict):
            price_val = offers.get("price")
            currency = offers.get("priceCurrency")
            if price_val is not None:
                specs.price = Price(
                    amount=self._parse_number(price_val),
                    currency=currency,
                )

        # Extract weight
        weight_val = product.get("weight")
        if weight_val:
            if isinstance(weight_val, dict):
                w = self._parse_number(weight_val.get("value"))
            else:
                w = self._parse_number(weight_val)
            if w:
                specs.weight = Weight(with_battery_kg=w)

        # Extract description-based specs
        description = product.get("description", "")
        if description:
            # Try to extract motor info from description
            motor_match = re.search(
                r"(Bosch|Shimano|Bafang|Yamaha|Brose)\s+([^,\n.]+)", description
            )
            if motor_match:
                specs.motor = Motor(make=motor_match.group(1))

        return specs

    def _extract_image(
        self, product: dict[str, Any], soup: BeautifulSoup
    ) -> str | None:
        """Extract product image URL from JSON-LD or HTML."""
        # From JSON-LD
        image = product.get("image")
        if image:
            if isinstance(image, list):
                return str(image[0]) if image else None
            if isinstance(image, dict):
                return image.get("url") or image.get("contentUrl")
            return str(image)

        return self._extract_image_from_html(soup)

    def _extract_image_from_html(self, soup: BeautifulSoup) -> str | None:
        """Extract main product image from HTML."""
        # Look for Open Graph image
        og_image = soup.find("meta", property="og:image")
        if og_image and isinstance(og_image, Tag):
            content = og_image.get("content")
            if content:
                return str(content)

        # Look for main product image
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = str(img.get("alt", "")).lower()
            if any(
                kw in alt
                for kw in ["product", "bike", "vélo", "cargo", "main"]
            ):
                return str(src)

        return None
