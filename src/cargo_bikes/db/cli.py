"""CLI commands for database management."""

from pathlib import Path

import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = typer.Typer(help="Database management commands.")


@app.command("hydrate")
def hydrate(
    vault_path: Path = typer.Option(
        Path("vault/notes"), help="Path to vault/notes directory"
    ),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database file"),
    skip_linter: bool = typer.Option(False, help="Skip linter validation"),
) -> None:
    """Hydrate the database from Markdown files."""
    from cargo_bikes.db.hydrate import hydrate_from_vault, run_linter
    from cargo_bikes.db.schema import Base

    if not vault_path.exists():
        print(f"✗ Vault path does not exist: {vault_path}")
        raise typer.Exit(2)

    if not skip_linter:
        if not run_linter(vault_path):
            print("\n✗ Linter validation failed. Fix errors before hydrating.")
            raise typer.Exit(1)
        print()

    db_path_resolved = db_path.resolve()
    engine = create_engine(f"sqlite:///{db_path_resolved}", echo=False)
    Base.metadata.create_all(engine)

    print(f"Hydrating database: {db_path_resolved}")
    print(f"From vault: {vault_path}")

    try:
        with Session(engine) as session:
            stats = hydrate_from_vault(session, vault_path)

        print("\n✓ Hydration complete!")
        print("\nSummary:")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Brands created: {stats['brands_created']}")
        print(f"  Brands updated: {stats['brands_updated']}")
        print(f"  Bikes created: {stats['bikes_created']}")
        print(f"  Bikes updated: {stats['bikes_updated']}")

    except Exception as e:
        print(f"\n✗ Hydration failed: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(2)


@app.command("project")
def project(
    vault_path: Path = typer.Option(
        Path("vault/notes"), help="Path to vault/notes directory"
    ),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database file"),
    dry_run: bool = typer.Option(False, help="Show what would be updated"),
    bike_id: int | None = typer.Option(None, help="Project only this bike ID"),
) -> None:
    """Project database records back to Markdown files."""
    from cargo_bikes.db.project import project_all_bikes

    if not vault_path.exists():
        print(f"✗ Vault path does not exist: {vault_path}")
        raise typer.Exit(2)

    if not db_path.exists():
        print(f"✗ Database does not exist: {db_path}")
        raise typer.Exit(2)

    db_path_resolved = db_path.resolve()
    engine = create_engine(f"sqlite:///{db_path_resolved}", echo=False)

    print(f"Projecting from database: {db_path_resolved}")
    print(f"To vault: {vault_path}")
    if dry_run:
        print("DRY RUN - No changes will be written")
    print()

    try:
        with Session(engine) as session:
            success_count, fail_count = project_all_bikes(
                session, dry_run=dry_run, bike_id=bike_id
            )

        print(f"\nSummary:")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {fail_count}")

        if fail_count > 0:
            raise typer.Exit(2)

    except typer.Exit:
        raise
    except Exception as e:
        print(f"\n✗ Projection failed: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(2)


@app.command("project-brands")
def project_brands(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database file"),
    dry_run: bool = typer.Option(False, help="Show what would be updated"),
) -> None:
    """Project brand records back to Markdown files (flatten nested fields)."""
    from cargo_bikes.db.project import project_all_brands

    if not db_path.exists():
        print(f"✗ Database does not exist: {db_path}")
        raise typer.Exit(2)

    db_path_resolved = db_path.resolve()
    engine = create_engine(f"sqlite:///{db_path_resolved}", echo=False)

    print(f"Projecting brands from: {db_path_resolved}")
    if dry_run:
        print("DRY RUN - No changes will be written")
    print()

    try:
        with Session(engine) as session:
            success_count, fail_count = project_all_brands(
                session, vault_path=vault_path, dry_run=dry_run
            )

        print(f"\nSummary:")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {fail_count}")

    except Exception as e:
        print(f"\n✗ Brand projection failed: {e}")
        import traceback

        traceback.print_exc()
        raise typer.Exit(2)
