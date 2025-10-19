#!/usr/bin/env python3
"""Generate bike table from YAML frontmatter in vault/notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from Markdown file content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    yaml_content = match.group(1)
    try:
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        print(f"  [WARN] YAML parse error: {e}")
        return None


def validate_bike_frontmatter(frontmatter: dict) -> bool:
    """Validate that frontmatter has required bike fields."""
    required_fields = ["title", "type", "tags"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        msg = f"Missing required fields: {', '.join(missing)}"
        print(f"  [ERR] {msg}")
        return False
    if frontmatter.get("type") != "bike":
        typ = frontmatter.get("type")
        print(f"  [SKIP] Not a bike entry (type={typ})")
        return False
    return True


def collect_bikes() -> list[dict]:
    """Collect all bikes from vault/notes."""
    bikes = []
    vault_notes = Path("vault/notes")
    if not vault_notes.exists():
        print(f"Error: {vault_notes} not found")
        return bikes
    print(f"\nScanning {vault_notes}...\n")
    for md_file in sorted(vault_notes.glob("*/*.md")):
        rel_path = md_file.relative_to("vault/notes")
        brand_folder = md_file.parent.name
        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter = extract_frontmatter(content)
            if frontmatter is None:
                print(f"[ERR] {rel_path}: No YAML frontmatter found")
                continue
            if not validate_bike_frontmatter(frontmatter):
                continue
            bike = {
                "title": frontmatter.get("title", ""),
                "brand": frontmatter.get("brand", brand_folder),
                "model": frontmatter.get("model", ""),
                "price": frontmatter.get("price", ""),
                "motor": frontmatter.get("motor", ""),
                "battery": frontmatter.get("battery", ""),
                "range": frontmatter.get("range", ""),
                "image": frontmatter.get("image", ""),
                "url": frontmatter.get("url", ""),
                "file_path": f"vault/notes/{rel_path}".replace("\\", "/"),
                "tags": frontmatter.get("tags", []),
            }
            bikes.append(bike)
            print(f"[OK] {rel_path}: {bike['title']}")
        except Exception as e:
            err_type = type(e).__name__
            print(f"[ERR] {rel_path}: {err_type}: {e}")
    return bikes


def format_table_cell(value: str, max_width: int = 50) -> str:
    """Format a value for Markdown table cell."""
    if not value:
        return "--"
    if len(value) > max_width:
        return value[: max_width - 3] + "..."
    return value


def generate_bike_table(bikes: list[dict]) -> str:
    """Generate Markdown table from bikes list."""
    if not bikes:
        return "No bikes found.\n"
    lines = []
    lines.append("## Bike Models\n")
    lines.append("| Image | Bike | Brand | Price | Motor | Battery | Range |")
    lines.append("|-------|------|-------|-------|-------|---------|-------|")
    sorted_bikes = sorted(bikes, key=lambda b: (b["brand"].lower(), b["title"].lower()))
    for bike in sorted_bikes:
        if bike["image"]:
            image_col = f"![img]({bike['image']})"
        else:
            image_col = "--"
        bike_link = f"[{bike['title']}]({bike['file_path']})"
        brand = format_table_cell(bike["brand"], 20)
        price = format_table_cell(bike["price"], 15)
        motor = format_table_cell(bike["motor"], 20)
        battery = format_table_cell(bike["battery"], 15)
        range_val = format_table_cell(bike["range"], 15)
        lines.append(
            f"| {image_col} | {bike_link} | {brand} | {price} | "
            f"{motor} | {battery} | {range_val} |"
        )
    return "\n".join(lines) + "\n"


def update_readme(table_content: str) -> None:
    """Update README.md with the bike table."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        return
    readme_content = readme_path.read_text(encoding="utf-8")
    start_marker = "<!-- BIKES_TABLE_START -->"
    end_marker = "<!-- BIKES_TABLE_END -->"
    if start_marker in readme_content and end_marker in readme_content:
        pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
        new_section = f"{start_marker}\n\n{table_content}\n{end_marker}"
        updated_content = re.sub(pattern, new_section, readme_content, flags=re.DOTALL)
    else:
        new_section = f"\n{start_marker}\n\n{table_content}\n{end_marker}\n"
        updated_content = readme_content + new_section
    readme_path.write_text(updated_content, encoding="utf-8")
    print(f"\n[OK] Updated {readme_path}")


def main() -> None:
    """Main entry point."""
    print("=" * 70)
    print("CARGO BIKES TABLE GENERATOR")
    print("=" * 70)
    bikes = collect_bikes()
    print(f"\n{'-' * 70}")
    print(f"Total bikes found: {len(bikes)}\n")
    if not bikes:
        print("No valid bikes to generate table from.")
        return
    table_content = generate_bike_table(bikes)
    print("\nGenerated table preview (first 800 chars):")
    print(table_content[:800])
    if len(table_content) > 800:
        print("...\n")
    print(f"\n{'-' * 70}")
    update_readme(table_content)
    print(f"{'-' * 70}")
    print("[OK] Done!")


if __name__ == "__main__":
    main()
