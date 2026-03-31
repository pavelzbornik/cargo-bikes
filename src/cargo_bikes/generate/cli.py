"""CLI commands for content generation."""

from pathlib import Path

import typer

app = typer.Typer(help="Content generation commands.")


@app.command("bike-table")
def bike_table(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
) -> None:
    """Generate bike comparison tables by price range."""
    from cargo_bikes.generate.bike_table import (
        generate_bike_table,
        update_file_with_table,
    )
    from cargo_bikes.vault.scanner import collect_bikes

    print("=" * 70)
    print("CARGO BIKES TABLE GENERATOR")
    print("=" * 70)

    bikes = collect_bikes(vault_path)

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
    print("Updating files with bike table...\n")
    update_file_with_table(Path("README.md"), table_content)
    update_file_with_table(
        vault_path / "notes" / "bikes" / "index.md",
        table_content,
        use_relative_links=True,
    )
    print(f"{'-' * 70}")
    print("[OK] Done!")


@app.command("brand-indexes")
def brand_indexes(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
) -> None:
    """Generate brand index pages from bike files."""
    from cargo_bikes.generate.brand_indexes import generate_brand_index
    from cargo_bikes.vault.scanner import collect_bikes_by_brand

    bikes_dir = vault_path / "notes" / "bikes"
    bikes_by_brand = collect_bikes_by_brand(vault_path)

    created = 0
    for brand_key in sorted(bikes_by_brand):
        bikes = bikes_by_brand[brand_key]
        if not bikes:
            continue

        index_content = generate_brand_index(brand_key, bikes)
        index_file = bikes_dir / brand_key / "index.md"
        index_file.write_text(index_content, encoding="utf-8")

        created += 1
        print(f"✓ {brand_key}: {len(bikes)} models")

    print(f"\n✓ Successfully generated {created} brand index pages!")


@app.command("bike-markers")
def bike_markers(
    vault_path: Path = typer.Option(
        Path("vault/notes"), help="Path to vault/notes directory"
    ),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
) -> None:
    """Add BIKE_SPECS_TABLE markers to bike markdown files."""
    from cargo_bikes.generate.bike_markers import process_bike_files

    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        raise typer.Exit(1)

    mode = "DRY RUN - No changes will be written" if dry_run else "Processing files"
    print(f"{mode}")
    print(f"Vault path: {vault_path}\n")

    stats = process_bike_files(vault_path, dry_run=dry_run)

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Already have markers: {stats['files_with_markers']}")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Errors: {stats['errors']}")
    print("=" * 60)

    if dry_run:
        print("\nDRY RUN: No changes were written.")


@app.command("fix-links")
def fix_links(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    dry_run: bool = typer.Option(False, help="Show what would be changed"),
) -> None:
    """Convert [[wikilinks]] to markdown links for MkDocs compatibility."""
    from cargo_bikes.generate.links import fix_all_links

    fix_all_links(vault_path=vault_path, dry_run=dry_run)


@app.command("bases")
def bases(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database"),
) -> None:
    """Generate Obsidian Bases (.base) files from database state."""
    from cargo_bikes.generate.bases import generate_all_bases

    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        raise typer.Exit(1)

    generate_all_bases(vault_path=vault_path, db_path=db_path)
