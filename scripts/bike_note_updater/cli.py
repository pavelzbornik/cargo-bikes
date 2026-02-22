"""
CLI entry point for the bike note updater agent.

Provides commands for:
- Updating single bike notes or entire vault
- Validating notes against schema
- Migrating legacy frontmatter fields
- Generating spec tables

Usage:
    python -m scripts.bike_note_updater.cli update-bike <path>
    python -m scripts.bike_note_updater.cli update-all [--brand <brand>]
    python -m scripts.bike_note_updater.cli validate [--brand <brand>]
    python -m scripts.bike_note_updater.cli migrate-legacy [--brand <brand>]
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer

app = typer.Typer(
    name="bike-note-updater",
    help="Autonomous research agent for cargo bike data enrichment.",
    add_completion=False,
)

# Default paths
DEFAULT_VAULT_PATH = "vault/notes"


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.command()
def update_bike(
    note_path: str = typer.Argument(..., help="Path to the bike note markdown file"),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip fetching from URL"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip LLM extraction"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without writing"
    ),
    no_migrate: bool = typer.Option(
        False, "--no-migrate", help="Skip legacy field migration"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Update a single bike note with fetched and extracted data."""
    _setup_logging(verbose)

    from scripts.bike_note_updater.agent import update_single_bike

    path = Path(note_path)
    if not path.exists():
        typer.echo(f"Error: File not found: {note_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Updating: {path}")
    if dry_run:
        typer.echo("(dry run - no files will be modified)")

    result = update_single_bike(
        path,
        fetch_url=not no_fetch,
        use_llm=not no_llm,
        dry_run=dry_run,
        migrate_legacy=not no_migrate,
    )

    if result.success:
        typer.echo(f"\nSuccess: {result.bike_name}")
        if result.changes_made:
            typer.echo(f"Changes: {len(result.changes_made)} fields updated")
            for change in result.changes_made:
                typer.echo(f"  + {change}")
        else:
            typer.echo("No changes needed.")
    else:
        typer.echo(f"\nFailed: {result.bike_name}", err=True)
        for error in result.errors:
            typer.echo(f"  Error: {error}", err=True)
        raise typer.Exit(1)

    if result.conflicts:
        typer.echo(f"\nConflicts ({len(result.conflicts)}):")
        for conflict in result.conflicts:
            typer.echo(
                f"  ! {conflict.field}: {conflict.old_value} -> "
                f"{conflict.new_value} ({conflict.reason})"
            )

    # Show completeness comparison
    if result.validation_before and result.validation_after:
        before = result.validation_before.specs_completeness
        after = result.validation_after.specs_completeness
        typer.echo(f"\nSpecs completeness: {before:.0%} -> {after:.0%}")


@app.command()
def update_all(
    vault_path: str = typer.Option(
        DEFAULT_VAULT_PATH, "--vault-path", help="Path to vault/notes directory"
    ),
    brand: str | None = typer.Option(
        None, "--brand", "-b", help="Update only a specific brand"
    ),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip fetching from URLs"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip LLM extraction"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without writing"
    ),
    no_migrate: bool = typer.Option(
        False, "--no-migrate", help="Skip legacy field migration"
    ),
    limit: int | None = typer.Option(
        None, "--limit", "-n", help="Max number of notes to process"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Update all bike notes in the vault."""
    _setup_logging(verbose)

    from scripts.bike_note_updater.agent import print_update_summary, update_batch

    path = Path(vault_path)
    if not path.exists():
        typer.echo(f"Error: Vault path not found: {vault_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Updating bike notes in: {path}")
    if brand:
        typer.echo(f"Brand filter: {brand}")
    if dry_run:
        typer.echo("(dry run - no files will be modified)")

    summary = update_batch(
        path,
        brand=brand,
        fetch_url=not no_fetch,
        use_llm=not no_llm,
        dry_run=dry_run,
        migrate_legacy=not no_migrate,
        limit=limit,
    )

    print_update_summary(summary)

    if summary.errors > 0:
        raise typer.Exit(1)


@app.command()
def validate(
    vault_path: str = typer.Option(
        DEFAULT_VAULT_PATH, "--vault-path", help="Path to vault/notes directory"
    ),
    brand: str | None = typer.Option(
        None, "--brand", "-b", help="Validate only a specific brand"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Validate all bike notes against the BIKE_SPECS_SCHEMA."""
    _setup_logging(verbose)

    from scripts.bike_note_updater.schema_validator import (
        print_validation_summary,
        validate_vault,
    )

    path = Path(vault_path)
    if not path.exists():
        typer.echo(f"Error: Vault path not found: {vault_path}", err=True)
        raise typer.Exit(1)

    # If brand filter, adjust path
    if brand:
        brand_dir = path / "bikes" / brand.lower().replace(" ", "-")
        if not brand_dir.exists():
            typer.echo(f"Error: Brand directory not found: {brand_dir}", err=True)
            raise typer.Exit(1)
        reports = validate_vault(brand_dir)
    else:
        reports = validate_vault(path)

    print_validation_summary(reports)

    # Show details for notes with issues
    if verbose:
        for report in reports:
            if report.issues:
                typer.echo(f"\n{report.file_path}:")
                for issue in report.issues:
                    typer.echo(f"  [{issue.issue_type}] {issue.field}: {issue.message}")
                    if issue.suggestion:
                        typer.echo(f"    -> {issue.suggestion}")

    # Exit with error if there are invalid notes
    invalid = sum(1 for r in reports if not r.is_valid)
    if invalid > 0:
        typer.echo(f"\n{invalid} invalid notes found.", err=True)
        raise typer.Exit(1)

    typer.echo("All notes are valid.")


@app.command()
def migrate_legacy(
    vault_path: str = typer.Option(
        DEFAULT_VAULT_PATH, "--vault-path", help="Path to vault/notes directory"
    ),
    brand: str | None = typer.Option(
        None, "--brand", "-b", help="Migrate only a specific brand"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview changes without writing"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Migrate legacy top-level fields (price, motor, battery) into specs structure."""
    _setup_logging(verbose)

    from scripts.bike_note_updater.agent import print_update_summary, update_batch

    path = Path(vault_path)
    if not path.exists():
        typer.echo(f"Error: Vault path not found: {vault_path}", err=True)
        raise typer.Exit(1)

    typer.echo("Migrating legacy frontmatter fields to specs structure...")
    if dry_run:
        typer.echo("(dry run - no files will be modified)")

    summary = update_batch(
        path,
        brand=brand,
        fetch_url=False,
        use_llm=False,
        dry_run=dry_run,
        migrate_legacy=True,
    )

    print_update_summary(summary)


@app.command()
def audit(
    vault_path: str = typer.Option(
        DEFAULT_VAULT_PATH, "--vault-path", help="Path to vault/notes directory"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Generate a completeness audit of all bike notes."""
    _setup_logging(verbose)

    from scripts.bike_note_updater.schema_validator import validate_vault

    path = Path(vault_path)
    if not path.exists():
        typer.echo(f"Error: Vault path not found: {vault_path}", err=True)
        raise typer.Exit(1)

    reports = validate_vault(path)

    # Sort by completeness
    reports.sort(key=lambda r: r.specs_completeness)

    typer.echo(f"\n{'=' * 70}")
    typer.echo("BIKE NOTE COMPLETENESS AUDIT")
    typer.echo(f"{'=' * 70}")
    typer.echo(f"{'File':<50} {'Complete':>8} {'Legacy':>7} {'Issues':>7}")
    typer.echo(f"{'-' * 50} {'-' * 8} {'-' * 7} {'-' * 7}")

    for report in reports:
        # Shorten path for display
        short_path = report.file_path
        if len(short_path) > 49:
            short_path = "..." + short_path[-46:]

        legacy = "Yes" if report.has_legacy_fields else ""
        typer.echo(
            f"{short_path:<50} {report.specs_completeness:>7.0%} "
            f"{legacy:>7} {len(report.issues):>7}"
        )

    total = len(reports)
    avg_completeness = (
        sum(r.specs_completeness for r in reports) / total if total > 0 else 0
    )
    with_legacy = sum(1 for r in reports if r.has_legacy_fields)

    typer.echo(f"\n{'=' * 70}")
    typer.echo(f"Total notes:          {total}")
    typer.echo(f"Avg completeness:     {avg_completeness:.1%}")
    typer.echo(f"With legacy fields:   {with_legacy}")
    typer.echo(f"{'=' * 70}\n")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    sys.exit(main() or 0)
