"""Command-line interface for the bike note updater.

This module provides CLI commands for updating, validating, and checking
bike notes in the vault.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .agent import BikeNoteUpdater
from .utils import find_bike_notes, validate_url

app = typer.Typer(
    name="bike-note-updater",
    help="Update and validate bike notes from manufacturer product pages",
)
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.command()
def update_bike(
    note_path: str = typer.Argument(..., help="Path to bike note file"),
    fetch_url: bool = typer.Option(True, help="Fetch from product URL"),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
    validate_only: bool = typer.Option(False, help="Only validate, don't update"),
):
    """Update a single bike note."""
    updater = BikeNoteUpdater()

    try:
        if validate_only:
            console.print(f"[cyan]Validating:[/cyan] {note_path}")
            result = updater.validate_note(note_path)
        else:
            console.print(f"[cyan]Updating:[/cyan] {note_path}")
            result = asyncio.run(
                updater.update_bike(note_path, fetch_url=fetch_url, dry_run=dry_run)
            )

        # Display result
        if result.success:
            console.print(f"[green]✓ Success:[/green] {result.bike_name}")
            if result.changes_made:
                console.print("[yellow]Changes made:[/yellow]")
                for field, change in result.changes_made.items():
                    console.print(f"  - {field}: {change}")
            if result.conflicts:
                console.print("[yellow]⚠ Conflicts detected:[/yellow]")
                for conflict in result.conflicts:
                    console.print(f"  - {conflict}")
        else:
            console.print(f"[red]✗ Failed:[/red] {result.bike_name}")
            for error in result.errors:
                console.print(f"  [red]Error:[/red] {error}")

        if result.warnings:
            console.print("[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"  - {warning}")

    finally:
        updater.close()


@app.command()
def update_all_bikes(
    vault_path: str = typer.Option(
        "vault", help="Path to vault root directory"
    ),
    brand: str | None = typer.Option(None, help="Update only specific brand"),
    validate_only: bool = typer.Option(False, help="Only validate, don't update"),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
):
    """Update all bike notes in the vault."""
    vault_path_obj = Path(vault_path)
    if not vault_path_obj.exists():
        console.print(f"[red]Error:[/red] Vault path not found: {vault_path}")
        raise typer.Exit(1)

    # Find all bike notes
    bike_notes = find_bike_notes(vault_path_obj, brand=brand)

    if not bike_notes:
        console.print("[yellow]No bike notes found[/yellow]")
        return

    console.print(f"[cyan]Found {len(bike_notes)} bike note(s)[/cyan]")

    updater = BikeNoteUpdater()
    results = []

    try:
        for note_path in bike_notes:
            console.print(f"\n[cyan]Processing:[/cyan] {note_path.name}")

            if validate_only:
                result = updater.validate_note(note_path)
            else:
                result = asyncio.run(
                    updater.update_bike(note_path, fetch_url=True, dry_run=dry_run)
                )

            results.append(result)

            # Show result
            if result.success:
                console.print(f"  [green]✓[/green] {result.bike_name}")
            else:
                console.print(f"  [red]✗[/red] {result.bike_name}")
                for error in result.errors[:2]:  # Show first 2 errors
                    console.print(f"    [red]{error}[/red]")

        # Summary
        console.print("\n[bold cyan]Summary[/bold cyan]")
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_conflicts = sum(len(r.conflicts) for r in results)

        summary_table = Table()
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total processed", str(len(results)))
        summary_table.add_row("Successful", str(successful))
        summary_table.add_row("Failed", str(failed))
        summary_table.add_row("Conflicts flagged", str(total_conflicts))

        console.print(summary_table)

    finally:
        updater.close()


@app.command()
def validate_all_notes(
    vault_path: str = typer.Option(
        "vault", help="Path to vault root directory"
    ),
    brand: str | None = typer.Option(None, help="Validate only specific brand"),
):
    """Validate all notes against schema."""
    update_all_bikes(vault_path=vault_path, brand=brand, validate_only=True)


@app.command()
def check_urls(
    vault_path: str = typer.Option(
        "vault", help="Path to vault root directory"
    ),
    brand: str | None = typer.Option(None, help="Check only specific brand"),
):
    """Check that all product URLs in notes are still valid."""
    from .utils import parse_frontmatter

    vault_path_obj = Path(vault_path)
    bike_notes = find_bike_notes(vault_path_obj, brand=brand)

    if not bike_notes:
        console.print("[yellow]No bike notes found[/yellow]")
        return

    console.print(f"[cyan]Checking URLs for {len(bike_notes)} bike(s)[/cyan]\n")

    valid_count = 0
    invalid_count = 0

    for note_path in bike_notes:
        content = note_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)

        if not frontmatter:
            continue

        url = frontmatter.get("url")
        if not url:
            console.print(f"[yellow]⚠[/yellow] {note_path.name}: No URL")
            continue

        console.print(f"Checking: {note_path.name}... ", end="")

        is_valid = validate_url(url)

        if is_valid:
            console.print("[green]✓[/green]")
            valid_count += 1
        else:
            console.print(f"[red]✗[/red] {url}")
            invalid_count += 1

    # Summary
    console.print(f"\n[cyan]Valid:[/cyan] {valid_count}")
    console.print(f"[red]Invalid:[/red] {invalid_count}")


if __name__ == "__main__":
    app()
