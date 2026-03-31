"""CLI commands for validation."""

import sys
from pathlib import Path

import typer

app = typer.Typer(help="Validation commands.")


@app.command("structure")
def structure(
    vault_path: Path = typer.Option(
        Path("vault/notes"), help="Path to vault/notes directory"
    ),
) -> None:
    """Validate Markdown structure in the vault."""
    from cargo_bikes.validate.structure import validate_vault

    if not vault_path.exists():
        print(f"✗ Vault path does not exist: {vault_path}")
        raise typer.Exit(1)

    print(f"Validating markdown files in {vault_path}...")
    errors = validate_vault(vault_path)

    if errors:
        print(f"\n✗ Found {len(errors)} validation error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        raise typer.Exit(1)
    else:
        print("✓ All markdown files are valid!")


@app.command("urls")
def urls(
    vault_path: Path = typer.Option(
        Path("vault/notes"), help="Path to vault/notes directory"
    ),
    dry_run: bool = typer.Option(False, help="Preview changes without modifying files"),
    skip_check: bool = typer.Option(
        False, help="Skip HTTP validation (structure only)"
    ),
) -> None:
    """Validate URL links in frontmatter."""
    from cargo_bikes.validate.urls import (
        save_changelog,
        validate_vault_urls,
    )

    print("=" * 70)
    print("URL VALIDATOR FOR CARGO BIKES VAULT")
    print("=" * 70)

    if dry_run:
        print("[DRY RUN MODE] - No files will be modified")
    if skip_check:
        print("[SKIP CHECK MODE] - URL structure only, no HTTP requests")
    print()

    changelog, total_files = validate_vault_urls(
        vault_path=vault_path, dry_run=dry_run, skip_check=skip_check
    )

    save_changelog(changelog, dry_run=dry_run)

    print(f"\n{'=' * 70}")
    print(f"Total files processed: {total_files}")
    print(f"Total entries in changelog: {len(changelog)}")
    print("=" * 70)
