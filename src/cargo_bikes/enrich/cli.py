"""CLI commands for AI-powered enrichment."""

from pathlib import Path

import typer

app = typer.Typer(help="AI-powered content enrichment commands.")


@app.command("harmonize")
def harmonize(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    brand: str | None = typer.Option(None, help="Only harmonize this brand"),
    dry_run: bool = typer.Option(False, help="Show changes without writing"),
    auto: bool = typer.Option(False, help="Skip interactive review"),
    wikilinks: bool = typer.Option(False, help="Also convert markdown links to wikilinks"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Extract missing frontmatter fields from note body content."""
    from cargo_bikes.enrich.harmonize import harmonize_notes

    harmonize_notes(
        vault_path=vault_path,
        brand=brand,
        dry_run=dry_run,
        auto=auto,
        wikilinks=wikilinks,
        model=model,
    )


# --- Content subcommands ---
content_app = typer.Typer(help="Generate web-ready content.")
app.add_typer(content_app, name="content")


@content_app.command("buying-guide")
def buying_guide(
    topic: str = typer.Argument(..., help="Guide topic"),
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Generate a buying guide on a topic."""
    from cargo_bikes.enrich.content import generate_buying_guide

    generate_buying_guide(
        topic=topic,
        vault_path=vault_path,
        db_path=db_path,
        model=model,
    )


@content_app.command("brand-profile")
def brand_profile(
    brand: str = typer.Argument(..., help="Brand folder name"),
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Generate a rich brand profile page."""
    from cargo_bikes.enrich.content import generate_brand_profile

    generate_brand_profile(
        brand_name=brand,
        vault_path=vault_path,
        db_path=db_path,
        model=model,
    )


@content_app.command("component-guide")
def component_guide(
    component_type: str = typer.Argument(..., help="Component type: motors, batteries, brakes"),
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Generate a component educational guide."""
    from cargo_bikes.enrich.content import generate_component_guide

    generate_component_guide(
        component_type=component_type,
        vault_path=vault_path,
        db_path=db_path,
        model=model,
    )


@app.command("components")
def components(
    category: str = typer.Option("all", help="Component category or 'all'"),
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    db_path: Path = typer.Option(Path("vault.db"), help="Path to database"),
    dry_run: bool = typer.Option(False, help="Show what would be generated"),
    auto: bool = typer.Option(False, help="Skip interactive review, accept all"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Auto-generate component notes from bike spec data."""
    from cargo_bikes.enrich.components import generate_components

    generate_components(
        category=category,
        vault_path=vault_path,
        db_path=db_path,
        dry_run=dry_run,
        auto=auto,
        model=model,
    )


@app.command("accessories")
def accessories(
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    brand: str | None = typer.Option(None, help="Only scan this brand"),
    category: str = typer.Option("all", help="Filter by category or 'all'"),
    auto: bool = typer.Option(False, help="Skip interactive review"),
    dry_run: bool = typer.Option(False, help="Show what would be generated"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Extract accessories from bike notes and generate individual notes."""
    from cargo_bikes.enrich.accessories import generate_accessories

    generate_accessories(
        vault_path=vault_path,
        brand=brand,
        category=category,
        auto=auto,
        dry_run=dry_run,
        model=model,
    )


@app.command("translate")
def translate(
    lang: str = typer.Option("fr", help="Target language code"),
    vault_path: Path = typer.Option(Path("vault"), help="Path to vault root"),
    brand: str | None = typer.Option(None, help="Only translate this brand"),
    note_type: str | None = typer.Option(
        None, help="Filter by type: bike, brand, guide, component"
    ),
    dry_run: bool = typer.Option(False, help="Show what would be translated"),
    model: str = typer.Option("claude-sonnet-4-6", help="Claude model to use"),
) -> None:
    """Translate vault notes to another language."""
    from cargo_bikes.enrich.translate import translate_notes

    translate_notes(
        lang=lang,
        vault_path=vault_path,
        brand=brand,
        note_type=note_type,
        dry_run=dry_run,
        model=model,
    )
