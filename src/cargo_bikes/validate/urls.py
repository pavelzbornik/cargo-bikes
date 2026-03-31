"""Validate URL links in YAML frontmatter and remove invalid ones."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml

from cargo_bikes.vault.frontmatter import extract_frontmatter_and_body

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
        """Check if URL is reachable via HTTP request."""
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


def reconstruct_frontmatter(
    frontmatter: dict[str, Any],
    body: str,
    original_yaml: str | None = None,
) -> str:
    """Reconstruct Markdown file from frontmatter and body."""
    if original_yaml is None:
        yaml_str = yaml.dump(
            frontmatter,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    else:
        yaml_str = _update_yaml_preserve_format(original_yaml, frontmatter)

    return f"---\n{yaml_str}\n---\n{body}"


def _update_yaml_preserve_format(
    original_yaml: str, updated_data: dict[str, Any]
) -> str:
    """Update YAML while preserving original formatting style."""
    lines = original_yaml.split("\n")
    result_lines = []

    for line in lines:
        if not line.strip() or ":" not in line:
            result_lines.append(line)
            continue

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

        has_double_quotes = original_value_part.startswith(
            '"'
        ) and original_value_part.endswith('"')
        has_single_quotes = original_value_part.startswith(
            "'"
        ) and original_value_part.endswith("'")

        if has_double_quotes:
            result_lines.append(f'{key}: "{new_value}"')
        elif has_single_quotes:
            result_lines.append(f"{key}: '{new_value}'")
        elif original_value_part.startswith("["):
            result_lines.append(line)
        else:
            result_lines.append(f"{key}: {new_value}")

    return "\n".join(result_lines)


def validate_and_clean_urls(
    frontmatter: dict[str, Any], validator: URLValidator
) -> tuple[dict[str, Any], list[str]]:
    """Validate URLs in frontmatter and set invalid ones to empty."""
    removed_urls: list[str] = []
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
) -> dict[str, Any]:
    """Create a changelog entry for a validated file."""
    return {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "status": status,
        "removed_urls": removed_urls,
    }


def validate_vault_urls(
    vault_path: Path | None = None,
    dry_run: bool = False,
    skip_check: bool = False,
) -> tuple[list[dict[str, Any]], int]:
    """Validate all URLs in vault/notes."""
    validator = URLValidator()
    changelog: list[dict[str, Any]] = []

    if vault_path is None:
        vault_path = Path("vault/notes")

    if not vault_path.exists():
        print(f"Error: {vault_path} not found")
        return changelog, 0

    print(f"\nValidating URLs in {vault_path}...\n")

    md_files = sorted(vault_path.glob("*/*.md"))
    total_files = len(md_files)

    for idx, md_file in enumerate(md_files, 1):
        rel_path = md_file.relative_to(vault_path)
        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter, body, original_yaml = extract_frontmatter_and_body(content)

            if frontmatter is None:
                print(f"[{idx}/{total_files}] [SKIP] No frontmatter {rel_path}")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "SKIPPED_NO_FM")
                )
                continue

            has_urls = any(field in frontmatter for field in ["url", "image"])
            if not has_urls:
                print(f"[{idx}/{total_files}] [OK] {rel_path}: No URLs found")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "OK_NO_URLS")
                )
                continue

            if skip_check:
                print(f"[{idx}/{total_files}] [SKIP] {rel_path}: Validation skipped")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "SKIPPED_CHECK")
                )
                continue

            cleaned_frontmatter, removed_urls = validate_and_clean_urls(
                frontmatter, validator
            )

            if removed_urls:
                print(
                    f"[{idx}/{total_files}] [REMOVED] {rel_path}: "
                    f"Removed {len(removed_urls)} URL(s)"
                )
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
                print(f"[{idx}/{total_files}] [OK] {rel_path}: All URLs valid")
                changelog.append(
                    create_changelog_entry(str(rel_path), [], "OK_VALID_URLS")
                )

        except Exception as e:
            err_type = type(e).__name__
            print(f"[{idx}/{total_files}] [ERR] {rel_path}: {err_type}: {e}")
            changelog.append(
                create_changelog_entry(str(rel_path), [], f"ERROR_{err_type}")
            )

    return changelog, total_files


def save_changelog(changelog: list[dict[str, Any]], dry_run: bool = False) -> None:
    """Save changelog to file."""
    changelog_path = Path("scripts/VALIDATE_URLS_CHANGELOG.json")
    changelog_content: dict[str, Any] = {
        "generated": datetime.now().isoformat(),
        "total_entries": len(changelog),
        "entries": changelog,
    }

    if dry_run:
        print(f"\n[DRY RUN] Changelog would be saved to: {changelog_path}")
        return

    changelog_path.parent.mkdir(parents=True, exist_ok=True)
    changelog_path.write_text(
        json.dumps(changelog_content, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n[OK] Changelog saved to {changelog_path}")
