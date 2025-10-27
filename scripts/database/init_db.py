"""
Database initialization script for the cargo-bikes vault.

This script creates a SQLite database file (vault.db) with all tables
defined in the schema. It can be run standalone or imported as a module.

Usage:
    python scripts/database/init_db.py [--db-path path/to/database.db]

Examples:
    # Create database at default location (vault.db in repo root)
    python scripts/database/init_db.py

    # Create database at custom location
    python scripts/database/init_db.py --db-path /tmp/test.db

    # Use as module
    from scripts.database.init_db import init_database
    engine = init_database("vault.db")
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.database.schema import create_tables, get_table_names


def init_database(db_path: str = "vault.db", echo: bool = False) -> Engine:
    """
    Initialize the SQLite database with all required tables.

    Args:
        db_path: Path to the database file (default: "vault.db")
        echo: Whether to echo SQL statements (default: False)

    Returns:
        SQLAlchemy Engine instance

    Raises:
        Exception: If database creation fails
    """
    # Convert to absolute path
    db_file = Path(db_path).resolve()

    # Create parent directory if it doesn't exist
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Create engine
    engine = create_engine(f"sqlite:///{db_file}", echo=echo)

    # Create all tables
    try:
        create_tables(engine)
        print(f"✓ Database created successfully: {db_file}")

        # Verify tables were created
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
    """
    Verify that all expected tables exist in the database.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        True if all tables exist, False otherwise
    """
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


def main() -> int:
    """Command-line interface for database initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize the cargo-bikes vault database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="vault.db",
        help="Path to the database file (default: vault.db)",
    )

    parser.add_argument(
        "--echo",
        action="store_true",
        help="Echo SQL statements to stdout",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify schema after creation",
    )

    args = parser.parse_args()

    try:
        # Initialize database
        engine = init_database(db_path=args.db_path, echo=args.echo)

        # Verify schema if requested
        if args.verify:
            if not verify_schema(engine):
                sys.exit(1)

        print("\n✓ Database initialization complete!")
        return 0

    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
