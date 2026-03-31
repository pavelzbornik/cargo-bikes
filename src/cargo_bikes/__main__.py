"""Cargo bikes CLI entry point.

Usage:
    cargo-bikes generate bike-table
    cargo-bikes generate brand-indexes
    cargo-bikes generate bike-markers
    cargo-bikes db hydrate
    cargo-bikes db project
    cargo-bikes validate structure
    cargo-bikes validate urls
"""

import sys

import typer

from cargo_bikes.db.cli import app as db_app
from cargo_bikes.enrich.cli import app as enrich_app
from cargo_bikes.generate.cli import app as generate_app
from cargo_bikes.validate.cli import app as validate_app

# Handle UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

app = typer.Typer(
    name="cargo-bikes",
    help="Cargo bikes vault management CLI.",
    no_args_is_help=True,
)

app.add_typer(generate_app, name="generate")
app.add_typer(db_app, name="db")
app.add_typer(validate_app, name="validate")
app.add_typer(enrich_app, name="enrich")


if __name__ == "__main__":
    app()
