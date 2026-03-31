"""Consolidated frontmatter extraction and validation.

This module unifies the extract_frontmatter() logic that was previously
duplicated across generate_bike_table.py, generate_brand_indexes.py,
hydrate.py, and validate_structure.py.
"""

from __future__ import annotations

import re
from typing import Any

import yaml


def extract_frontmatter(content: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from Markdown content.

    Args:
        content: Raw markdown file content.

    Returns:
        Parsed frontmatter dict, or None if extraction/parsing fails.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        fm_data = yaml.safe_load(match.group(1))
        return fm_data if isinstance(fm_data, dict) else None
    except yaml.YAMLError:
        return None


def extract_frontmatter_with_error(
    content: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Extract YAML frontmatter with error reporting.

    Used by the validation/linting pipeline where error messages matter.

    Args:
        content: Raw markdown file content.

    Returns:
        Tuple of (frontmatter_dict, error_message).
        If successful, returns (dict, None).
        If failed, returns (None, error_message).
    """
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return None, "Missing frontmatter start delimiter (---)"

    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        return None, "Missing frontmatter end delimiter (---)"

    frontmatter_text = "\n".join(lines[1:end_idx])

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            frontmatter = {}
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML syntax: {e}"


def extract_frontmatter_from_file(
    file_path: "Path",
) -> dict[str, Any] | None:
    """Extract frontmatter from a file path.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Parsed frontmatter dict, or None if extraction fails.
    """
    from pathlib import Path

    file_path = Path(file_path)
    try:
        content = file_path.read_text(encoding="utf-8")
        return extract_frontmatter(content)
    except Exception:
        return None


def extract_frontmatter_and_body(
    content: str,
) -> tuple[dict[str, Any] | None, str, str | None]:
    """Extract frontmatter, body content, and raw YAML from markdown.

    Used by validate_urls for format-preserving rewrites.

    Args:
        content: File content.

    Returns:
        Tuple of (frontmatter dict, remaining body, original yaml string).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content, None
    yaml_content = match.group(1)
    body_content = match.group(2)
    try:
        fm_data = yaml.safe_load(yaml_content)
        fm = fm_data if isinstance(fm_data, dict) else {}
        return fm, body_content, yaml_content
    except yaml.YAMLError:
        return None, content, None


def validate_bike_frontmatter(frontmatter: dict[str, Any]) -> bool:
    """Validate that frontmatter has required bike fields.

    Args:
        frontmatter: Parsed frontmatter dict.

    Returns:
        True if valid bike frontmatter, False otherwise.
    """
    required_fields = ["title", "type", "tags"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        return False
    return frontmatter.get("type") == "bike"


def find_frontmatter_end(content: str) -> int:
    """Find the end position of the YAML frontmatter block.

    Args:
        content: File content.

    Returns:
        Index after the closing --- marker, or -1 if not found.
    """
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return -1

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return len("\n".join(lines[: i + 1])) + 1

    return -1
