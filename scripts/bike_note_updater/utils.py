"""Utility functions for the bike note updater.

This module provides helper functions for URL validation, file operations,
date handling, and other common tasks.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import httpx


def validate_url(url: str, timeout: int = 10) -> bool:
    """Check if a URL is valid and reachable.

    Args:
        url: The URL to validate
        timeout: Request timeout in seconds

    Returns:
        True if URL returns 200 status, False otherwise
    """
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        return response.status_code == 200
    except Exception:
        return False


def normalize_tag(tag: str) -> str:
    """Normalize a tag to lowercase, hyphenated format.

    Args:
        tag: The tag to normalize

    Returns:
        Normalized tag string
    """
    # Remove special characters and replace spaces with hyphens
    tag = re.sub(r"[^\w\s-]", "", tag.lower())
    tag = re.sub(r"\s+", "-", tag)
    tag = re.sub(r"-+", "-", tag)
    return tag.strip("-")


def validate_iso_date(date_str: str) -> bool:
    """Validate that a date string is in ISO 8601 format (YYYY-MM-DD).

    Args:
        date_str: The date string to validate

    Returns:
        True if valid ISO 8601 date, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_today_iso() -> str:
    """Get today's date in ISO 8601 format.

    Returns:
        Today's date as YYYY-MM-DD string
    """
    return datetime.now().strftime("%Y-%m-%d")


def find_bike_notes(vault_path: str | Path, brand: str | None = None) -> list[Path]:
    """Find all bike note files in the vault.

    Args:
        vault_path: Path to the vault root directory
        brand: Optional brand filter (lowercase, hyphenated)

    Returns:
        List of Path objects for bike notes
    """
    vault_path = Path(vault_path)
    bikes_dir = vault_path / "notes" / "bikes"

    if not bikes_dir.exists():
        return []

    if brand:
        brand_dir = bikes_dir / brand
        if brand_dir.exists():
            return list(brand_dir.glob("*.md"))
        return []

    # Find all .md files in all brand subdirectories
    return list(bikes_dir.glob("*/*.md"))


def extract_brand_from_path(note_path: Path) -> str | None:
    """Extract the brand name from a bike note file path.

    Args:
        note_path: Path to the bike note file

    Returns:
        Brand name (lowercase, hyphenated) or None
    """
    # Path structure: vault/notes/bikes/{brand}/{model}.md
    parts = note_path.parts
    try:
        bikes_idx = parts.index("bikes")
        if bikes_idx + 1 < len(parts):
            return parts[bikes_idx + 1]
    except (ValueError, IndexError):
        pass
    return None


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: The markdown file content

    Returns:
        Tuple of (frontmatter dict, body text)
    """
    import yaml

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content

    yaml_content = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter, body
    except yaml.YAMLError:
        return None, content


def format_yaml_frontmatter(frontmatter: dict) -> str:
    """Format frontmatter dict as YAML string.

    Args:
        frontmatter: The frontmatter dictionary

    Returns:
        Formatted YAML string with proper indentation
    """
    import yaml

    # Use safe_dump with proper settings for readability
    return yaml.safe_dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        indent=2,
    )


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values.

    Args:
        old_value: The original value
        new_value: The new value

    Returns:
        Percentage change (e.g., 0.1 for 10% increase)
    """
    if old_value == 0:
        return 1.0 if new_value != 0 else 0.0
    return abs((new_value - old_value) / old_value)


def is_significant_change(
    old_value: float, new_value: float, threshold: float = 0.1
) -> bool:
    """Check if the change between two values is significant.

    Args:
        old_value: The original value
        new_value: The new value
        threshold: Threshold percentage (default 0.1 = 10%)

    Returns:
        True if change exceeds threshold, False otherwise
    """
    return calculate_percentage_change(old_value, new_value) > threshold
