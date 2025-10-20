# Vault structure and conventions

This folder contains the content of the public Obsidian vault for cargo bikes.

## Structure

- `notes/bikes/` — individual notes for cargo bike models organized by manufacturer
- `templates/` — Markdown templates to create new notes with standardized frontmatter

## Organization

The vault separates bike-specific content from general reference material:

- **bikes/** — Detailed specs, reviews, and technical information for specific cargo bike models (organized by brand)
- **Other notes** (future) — Maintenance guides, component reviews, design principles, and other shared knowledge

## Frontmatter conventions

Each note should include a YAML frontmatter block with keys: `title`, `type`, `tags`, and optional `brand`, `model`, `date`. Use `type: bike` for specific bike pages.

### File paths

Bike notes should be organized as: `vault/notes/bikes/brand-name/bike-model.md`

Example: `vault/notes/bikes/tern/gsd-p10.md`
