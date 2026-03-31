"""Database initialization for the cargo-bikes vault."""

import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from cargo_bikes.db.schema import create_tables, get_table_names


def init_database(db_path: str = "vault.db", echo: bool = False) -> Engine:
    """Initialize the SQLite database with all required tables."""
    db_file = Path(db_path).resolve()
    db_file.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_file}", echo=echo)

    try:
        create_tables(engine)
        print(f"✓ Database created successfully: {db_file}")

        inspector = inspect(engine)
        created_tables = inspector.get_table_names()

        print(f"✓ Created {len(created_tables)} tables:")
        for table_name in created_tables:
            print(f"  - {table_name}")

        return engine

    except Exception as e:
        print(f"✗ Error creating database: {e}", file=sys.stderr)
        raise


def verify_schema(engine: Engine) -> bool:
    """Verify that all expected tables exist in the database."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(get_table_names())

    missing_tables = expected_tables - existing_tables
    extra_tables = existing_tables - expected_tables

    if missing_tables:
        print(f"✗ Missing tables: {', '.join(missing_tables)}", file=sys.stderr)
        return False

    if extra_tables:
        print(f"⚠ Extra tables found: {', '.join(extra_tables)}", file=sys.stderr)

    print(f"✓ Schema verification passed: all {len(expected_tables)} tables present")
    return True
