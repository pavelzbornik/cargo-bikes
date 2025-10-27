#!/usr/bin/env python3
"""Validate URL links in YAML frontmatter and remove invalid ones."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml

if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class QuotedString(str):
    """String that should be quoted in YAML output."""

    pass


def quoted_representer(dumper: Any, data: Any) -> Any:
    """Custom representer to quote strings."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.add_representer(QuotedString, quoted_representer)


class URLValidator:
    """Validates and cleans URLs from frontmatter."""

    def __init__(self, timeout: int = 5, max_retries: int = 2):
        """Initialize validator with request settings.

        Args:
            timeout: HTTP request timeout in seconds.
            max_retries: Number of retries for failed requests.
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
            }
        )

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is structurally valid."""
        if not url or not isinstance(url, str):
            return False
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def check_url_reachable(self, url: str) -> bool:
        """Check if URL is reachable via HTTP request.

        Args:
            url: URL to check.

        Returns:
            True if URL returns 2xx or 3xx status code.
        """
        if not self.is_valid_url(url):
            return False

        for attempt in range(self.max_retries):
            try:
                response = self.session.head(
                    url, timeout=self.timeout, allow_redirects=True
                )
                if 200 <= response.status_code < 400:
                    return True
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return False
                continue
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException,
            ):
                return False
        return False


def extract_frontmatter(
    content: str,
) -> tuple[dict[str, object] | None, str, str | None]:
    """Extract YAML frontmatter from Markdown file content.

    Args:
        content: File content.

    Returns:
        Tuple of (frontmatter dict, remaining content, original yaml).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content, None
    yaml_content = match.group(1)
    body_content = match.group(2)
    try:
        frontmatter_data = yaml.safe_load(yaml_content)
        fm = frontmatter_data if isinstance(frontmatter_data, dict) else {}
        return fm, body_content, yaml_content
    except yaml.YAMLError as e:
        print(f"  [WARN] YAML parse error: {e}")
        return None, content, None


def reconstruct_frontmatter(
    frontmatter: dict[str, object],
    body: str,
    original_yaml: str | None = None,
) -> str:
    """Reconstruct Markdown file from frontmatter and body.

    Preserves original YAML formatting where possible.

    Args:
        frontmatter: YAML frontmatter dict.
        body: File body content.
        original_yaml: Original YAML to preserve formatting.

    Returns:
        Reconstructed file content.
    """
    if original_yaml is None:
        yaml_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    else:
        # Preserve original formatting
        yaml_str = _update_yaml_preserve_format(original_yaml, frontmatter)

    return f"---\n{yaml_str}\n---\n{body}"


def _update_yaml_preserve_format(
    original_yaml: str, updated_data: dict[str, object]
) -> str:
    """Update YAML while preserving original formatting style.

    Args:
        original_yaml: Original YAML string.
        updated_data: Updated data dictionary.

    Returns:
        Updated YAML string with preserved formatting.
    """
    lines = original_yaml.split("\n")
    result_lines = []

    for line in lines:
        if not line.strip() or ":" not in line:
            result_lines.append(line)
            continue

        # Parse key
        parts = line.split(":", 1)
        if len(parts) != 2:
            result_lines.append(line)
            continue

        key = parts[0].strip()
        original_value_part = parts[1].strip()

        if key not in updated_data:
            result_lines.append(line)
            continue

        new_value = updated_data[key]

        # Detect original quoting style
        has_double_quotes = original_value_part.startswith(
            '"'
        ) and original_value_part.endswith('"')
        has_single_quotes = original_value_part.startswith(
            "'"
        ) and original_value_part.endswith("'")

        if has_double_quotes:
            # Original had double quotes - preserve them
            result_lines.append(f'{key}: "{new_value}"')
        elif has_single_quotes:
            # Original had single quotes - preserve them
            result_lines.append(f"{key}: '{new_value}'")
        elif original_value_part.startswith("["):
            # Original had list format, don't modify
            result_lines.append(line)
        else:
            # No quotes in original
            result_lines.append(f"{key}: {new_value}")

    return "\n".join(result_lines)


def validate_and_clean_urls(
    frontmatter: dict[str, object], validator: URLValidator
) -> tuple[dict[str, object], list[str]]:
    """Validate URLs in frontmatter and set invalid ones to empty.

    Args:
        frontmatter: YAML frontmatter dict.
        validator: URLValidator instance.

    Returns:
        Tuple of (cleaned frontmatter, list of invalidated URLs).
    """
    removed_urls = []
    url_fields = ["url", "image"]

    for field in url_fields:
        if field in frontmatter:
            url = frontmatter[field]
            if url and isinstance(url, str):
                if not validator.check_url_reachable(url):
                    removed_urls.append(url)
                    frontmatter[field] = ""

    return frontmatter, removed_urls


def create_changelog_entry(
    file_path: str, removed_urls: list[str], status: str
) -> dict[str, object]:
    """Create a changelog entry for a validated file.

    Args:
        file_path: Path to the file.
        removed_urls: List of removed URLs.
        status: Status code (OK, REMOVED, SKIPPED, ERROR).

    Returns:
        Changelog entry dict.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "status": status,
        "removed_urls": removed_urls,
    }


def validate_vault_urls(
    dry_run: bool = False, skip_check: bool = False
) -> tuple[list[dict[str, object]], int]:
    """Validate all URLs in vault/notes.

    Args:
        dry_run: If True, do not modify files.
        skip_check: If True, skip HTTP validation.

    Returns:
        Tuple of (changelog entries, total files processed).
    """
    validator = URLValidator()
    changelog: list[dict[str, object]] = []
    vault_notes = Path("vault/notes")

    if not vault_notes.exists():
        print(f"Error: {vault_notes} not found")
        return changelog, 0

    print(f"\nValidating URLs in {vault_notes}...\n")

    md_files = sorted(vault_notes.glob("*/*.md"))
    total_files = len(md_files)

    for idx, md_file in enumerate(md_files, 1):
        rel_path = md_file.relative_to("vault/notes")
        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter, body, original_yaml = extract_frontmatter(content)

            if frontmatter is None:
                status_msg = "[SKIP] No frontmatter"
                print(f"[{idx}/{total_files}] {status_msg} {rel_path}")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "SKIPPED_NO_FM")
                )
                continue

            has_urls = any(field in frontmatter for field in ["url", "image"])
            if not has_urls:
                msg = f"[OK] {rel_path}: No URLs found"
                print(f"[{idx}/{total_files}] {msg}")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "OK_NO_URLS")
                )
                continue

            if skip_check:
                skip_msg = "Validation skipped (--skip-check)"
                print(f"[{idx}/{total_files}] [SKIP] {rel_path}: {skip_msg}")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "SKIPPED_CHECK")
                )
                continue

            cleaned_frontmatter, removed_urls = validate_and_clean_urls(
                frontmatter, validator
            )

            if removed_urls:
                removed_count = len(removed_urls)
                removed_msg = f"Removed {removed_count} URL(s)"
                print(f"[{idx}/{total_files}] [REMOVED] {rel_path}: {removed_msg}")
                for url in removed_urls:
                    print(f"    - {url}")

                if not dry_run:
                    updated_content = reconstruct_frontmatter(
                        cleaned_frontmatter, body, original_yaml
                    )
                    md_file.write_text(updated_content, encoding="utf-8")
                    print("    [SAVED]")

                changelog.append(
                    create_changelog_entry(str(rel_path), removed_urls, "URLS_REMOVED")
                )
            else:
                msg = f"[OK] {rel_path}: All URLs valid"
                print(f"[{idx}/{total_files}] {msg}")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "OK_VALID_URLS")
                )

        except Exception as e:
            err_type = type(e).__name__
            msg = f"[ERR] {rel_path}: {err_type}: {e}"
            print(f"[{idx}/{total_files}] {msg}")
            changelog.append(
                create_changelog_entry(str(rel_path), [], f"ERROR_{err_type}")
            )

    return changelog, total_files


def save_changelog(changelog: list[dict[str, object]], dry_run: bool = False) -> None:
    """Save changelog to file.

    Args:
        changelog: List of changelog entries.
        dry_run: If True, do not save file.
    """
    changelog_path = Path("scripts/VALIDATE_URLS_CHANGELOG.json")
    changelog_content: dict[str, object] = {
        "generated": datetime.now().isoformat(),
        "total_entries": len(changelog),
        "entries": changelog,
    }

    if dry_run:
        print("\n[DRY RUN] Changelog would be saved to:")
        print(f"  {changelog_path}")
        print(f"  Total entries: {len(changelog)}")
        return

    changelog_path.write_text(
        json.dumps(changelog_content, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n[OK] Changelog saved to {changelog_path}")


def print_summary(
    changelog: list[dict[str, object]], total_files: int, dry_run: bool
) -> None:
    """Print summary statistics.

    Args:
        changelog: List of changelog entries.
        total_files: Total files processed.
        dry_run: If True, indicate dry-run mode.
    """
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total files processed: {total_files}")
    print(f"Total entries in changelog: {len(changelog)}")

    status_counts: dict[str, int] = {}
    for entry in changelog:
        status = entry["status"]
        if isinstance(status, str):
            status_counts[status] = status_counts.get(status, 0) + 1

    print("\nStatus breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    urls_removed = sum(
        len(val) if isinstance(val, (list, tuple)) else 0
        for entry in changelog
        for val in [entry.get("removed_urls")]
    )
    print(f"\nTotal URLs removed: {urls_removed}")

    if dry_run:
        print("\n[DRY RUN] No files were modified")

    print(f"{'=' * 70}")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate URL links in bike note frontmatter"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip HTTP validation (only check URL structure)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("URL VALIDATOR FOR CARGO BIKES VAULT")
    print("=" * 70)

    if args.dry_run:
        print("[DRY RUN MODE] - No files will be modified")

    if args.skip_check:
        msg = "[SKIP CHECK MODE] - URL structure only, no HTTP requests"
        print(msg)

    print()

    changelog, total_files = validate_vault_urls(
        dry_run=args.dry_run, skip_check=args.skip_check
    )

    save_changelog(changelog, dry_run=args.dry_run)
    print_summary(changelog, total_files, args.dry_run)


if __name__ == "__main__":
    main()
