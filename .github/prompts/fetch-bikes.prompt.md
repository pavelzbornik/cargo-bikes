---
mode: agent
description: "Fetch bikes from a website and create/update Obsidian vault notes"
---

# Fetch & Document E-Bikes

## Objective

Fetch all e-bikes and their relative accessories from a provided website and create or update Obsidian notes in the cargo-bikes vault following the bike template format.

## Process

### 1. Fetch All Bikes

- Retrieve complete bike listings from the provided website URL
- Handle pagination or multiple requests if needed to get all products
- Extract: bike name, model, brand, price, specifications, images, product URL

### 2. Organize & File Placement

- Create directory structure: `vault/notes/<Bike Brand>/` (if it doesn't exist)
- File naming: `vault/notes/<Bike Brand>/<bike_name>.md`
  - Use lowercase, hyphenated names (e.g., `le-cargo.md`, `le-compact.md`)
  - Brand folder should also be lowercase, hyphenated (e.g., `gaya/`)

### 3. Add Frontmatter

Every note **must** include this YAML frontmatter at the top:

```yaml
---
title: "<Bike Name>"
type: bike
tags: [bike, <bike-type>, <bike-brand>]
date: <ISO-DATE>
brand: "<Bike Brand>"
model: "<Bike Model Name>"
url: "<Product URL>"
image: "<Bike Image URL>"
price: "<Bike Price>"
motor: "<Bike motor_watts>W"
battery: "<Bike battery_wh>Wh"
range: "<Bike range_km>km"
---
```

**Frontmatter rules:**

- `title`: Full bike name (e.g., "Gaya Le Cargo")
- `tags`: Always include `bike`, plus bike type and brand in **lowercase, hyphenated** format
  - Example: `tags: [bike, long-tail, gaya]`
- `date`: ISO format (YYYY-MM-DD) — use today's date when fetching
- `brand` & `model`: Use exact names from source (do not translate)
- `url`: Direct link to product page
- `image`: URL to bike image (use official product image if available)

### 4. Fill Template Sections

Using the bike template (`vault/templates/bike-template.md`), populate:

- **Overview**: Brief description of the bike's purpose and positioning
- **Technical Specifications**: Price, weight, motor, battery, brakes, drivetrain, tires, load capacity, etc.
- **E-bike Features**: Assist levels, display, charging time, security, weather resistance, connectivity
- **Real-world Performance**: Range, hills, noise, comfort, handling
- **Cost**: Breakdown of bike cost with necessary accessories for typical use (e.g., carrying 2 kids) like monkeybars, 2x child seats etc
- **User Reviews & Experiences**: Pros, cons, user quotes (optional if not available)
- **Cargo Capacity & Use Cases**: Load capacity, configurations
- **Maintenance**: Battery care, service intervals
- **Modifications & Customization**: Upgrades, accessories
- **Accessories & Pricing**: Table with available accessories and prices
- **References**: Links to official pages, reviews, forums

**If a section lacks data, omit it from the note.**

### 5. Language & Naming Standards

- **Content**: Ensure all text is in English. Translate if sourced from other languages.
- **Preserve names**: Never translate bike names, brands, model names, or product-specific terms.
- **Lowercase tags**: Convert brand/type to lowercase with hyphens (e.g., `long-tail`, `cargo-bike`, `electric-assist`)

### 6. Update Existing Notes

If a note already exists for a bike:

- Merge new fetched data with existing content
- Preserve any additional user reviews, customization notes, or community content already in the note
- Update Technical Specifications and References with latest information
- Do not overwrite User Reviews & Experiences unless explicitly outdated

### 7. Quality Checks

Before finalizing:

- Validate YAML frontmatter syntax (no missing colons, quotes, or brackets)
- Ensure markdown renders correctly (test headers, lists, links, tables)
- Verify all URLs are functional
- Check that bike type and brand tags are lowercase and hyphenated
- Confirm date is in ISO format (YYYY-MM-DD)

## Example Output Structure

vault/notes/gaya/
├── le-cargo.md
├── le-compact.md
├── lincroyable-le-court.md
└── lincroyable-le-long.md

## Notes

- One note per bike model
- Preserve the vault's clean, organized structure
- Follow CONTRIBUTING.md and vault/README.md conventions
