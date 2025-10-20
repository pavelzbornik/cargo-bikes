"""Data fetching from manufacturer product pages.

This module handles fetching and extracting bike specifications from
manufacturer websites. It uses structured data (JSON-LD, microdata) when
available and falls back to HTML parsing.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from bs4 import BeautifulSoup


class DataFetcher:
    """Fetches and extracts bike product data from URLs."""

    def __init__(self, timeout: int = 30, cache_dir: str | None = None):
        """Initialize the data fetcher.

        Args:
            timeout: HTTP request timeout in seconds
            cache_dir: Optional cache directory for responses
        """
        self.timeout = timeout
        self.cache_dir = cache_dir
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)

    async def fetch_from_url(self, url: str) -> dict[str, Any]:
        """Fetch product page and extract bike data.

        Args:
            url: Product page URL

        Returns:
            Dictionary with extracted bike data

        Raises:
            httpx.HTTPError: If request fails
            ValueError: If extraction fails
        """
        # Fetch the page
        response = self.client.get(url)
        response.raise_for_status()

        html = response.text

        # Try to extract structured data first
        structured_data = self._extract_json_ld(html)
        if structured_data:
            return self._parse_structured_data(structured_data)

        # Fall back to HTML parsing
        return self._extract_from_html(html)

    def _extract_json_ld(self, html: str) -> dict[str, Any] | None:
        """Extract JSON-LD structured data from HTML.

        Args:
            html: The HTML content

        Returns:
            JSON-LD data or None if not found
        """
        soup = BeautifulSoup(html, "lxml")
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            try:
                data = json.loads(script.string)
                # Look for Product schema
                if isinstance(data, dict) and data.get("@type") == "Product":
                    return data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            return item
            except (json.JSONDecodeError, AttributeError):
                continue

        return None

    def _parse_structured_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse JSON-LD product data into bike specs format.

        Args:
            data: JSON-LD product data

        Returns:
            Dictionary with bike specifications
        """
        result: dict[str, Any] = {}

        # Extract basic info
        result["title"] = data.get("name", "")
        result["image"] = self._extract_image_url(data)

        # Extract price
        offers = data.get("offers", {})
        if isinstance(offers, dict):
            result["price"] = {
                "amount": offers.get("price"),
                "currency": offers.get("priceCurrency", "USD"),
            }

        # Extract specs from description or additional properties
        description = data.get("description", "")
        result["specs"] = self._extract_specs_from_description(description)

        # Check for product properties
        if "additionalProperty" in data:
            props = data["additionalProperty"]
            if isinstance(props, list):
                for prop in props:
                    if isinstance(prop, dict):
                        self._map_property_to_spec(prop, result)

        return result

    def _extract_image_url(self, data: dict[str, Any]) -> str | None:
        """Extract image URL from structured data.

        Args:
            data: The structured data

        Returns:
            Image URL or None
        """
        image = data.get("image")
        if isinstance(image, str):
            return image
        elif isinstance(image, dict):
            return image.get("url") or image.get("contentUrl")
        elif isinstance(image, list) and len(image) > 0:
            if isinstance(image[0], str):
                return image[0]
            elif isinstance(image[0], dict):
                return image[0].get("url") or image[0].get("contentUrl")
        return None

    def _extract_specs_from_description(self, description: str) -> dict[str, Any]:
        """Extract specifications from product description text.

        This is a simplified implementation. A production version would use
        more sophisticated pattern matching or LLM-based extraction.

        Args:
            description: Product description text

        Returns:
            Dictionary with extracted specs
        """
        specs: dict[str, Any] = {}

        # This is a placeholder - actual implementation would parse the description
        # to extract motor, battery, weight, etc.

        return specs

    def _map_property_to_spec(
        self, prop: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Map a structured data property to a spec field.

        Args:
            prop: Property dictionary
            result: Result dictionary to update
        """
        name = prop.get("name", "").lower()
        value = prop.get("value")

        # Initialize specs if not present
        if "specs" not in result:
            result["specs"] = {}

        # Map common properties
        if "motor" in name:
            if "motor" not in result["specs"]:
                result["specs"]["motor"] = {}
            if "power" in name:
                result["specs"]["motor"]["power_w"] = value
            elif "torque" in name:
                result["specs"]["motor"]["torque_nm"] = value
        elif "battery" in name:
            if "battery" not in result["specs"]:
                result["specs"]["battery"] = {}
            if "capacity" in name:
                result["specs"]["battery"]["capacity_wh"] = value
        elif "weight" in name:
            if "weight" not in result["specs"]:
                result["specs"]["weight"] = {}
            result["specs"]["weight"]["with_battery_kg"] = value

    def _extract_from_html(self, html: str) -> dict[str, Any]:
        """Extract bike data from HTML using BeautifulSoup.

        This is a fallback method when structured data is not available.

        Args:
            html: The HTML content

        Returns:
            Dictionary with extracted bike data
        """
        soup = BeautifulSoup(html, "lxml")
        result: dict[str, Any] = {}

        # Try to extract title from h1 or page title
        h1 = soup.find("h1")
        if h1:
            result["title"] = h1.get_text(strip=True)
        else:
            title = soup.find("title")
            if title:
                result["title"] = title.get_text(strip=True)

        # Try to extract main product image
        # Look for og:image meta tag
        og_image = soup.find("meta", property="og:image")
        if og_image:
            result["image"] = og_image.get("content")

        # Initialize specs
        result["specs"] = {}

        # This is a placeholder - actual implementation would use
        # site-specific selectors or pattern matching to extract specs

        return result

    def validate_fetched_urls(self, urls: list[str]) -> dict[str, bool]:
        """Check if URLs are valid and reachable.

        Args:
            urls: List of URLs to validate

        Returns:
            Dictionary mapping URLs to their validity status
        """
        results = {}
        for url in urls:
            try:
                response = self.client.head(url, timeout=10)
                results[url] = response.status_code == 200
            except Exception:
                results[url] = False
        return results

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
