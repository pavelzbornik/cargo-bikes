# Vault structure and conventions

This folder contains the content of the public Obsidian vault for cargo bikes.

## Structure

- `notes/bikes/` — Individual notes for cargo bike models organized by manufacturer
- `templates/` — Markdown templates to create new notes with standardized frontmatter

## Organization

The vault separates bike-specific content from general reference material:

- **bikes/** — Detailed specs, reviews, and technical information for specific cargo bike models (organized by brand)
- **Other notes** (future) — Maintenance guides, component reviews, design principles, and other shared knowledge

## Frontmatter Conventions

Each note must include a **YAML frontmatter block** with the structure defined in `docs/schema/BIKE_SPECS_SCHEMA.md`.

### For Bike Notes

All bike notes follow the **BIKE_SPECS_SCHEMA** structure:

**Required top-level fields:**

- `title` — Full bike name
- `type` — Set to `bike`
- `brand` — Manufacturer name
- `model` — Model name
- `tags` — List of lowercase, hyphenated tags (always include: `bike`, bike type, brand)
- `date` — ISO format (YYYY-MM-DD)
- `url` — Official product page
- `image` — URL to product image
- `specs` — Nested object with technical specifications

**Recommended fields:**

- `resellers` — Array of vendor listings (price, currency, region, availability)

**Example frontmatter:**

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2025-10-20
tags: [bike, longtail, electric, trek, bosch]
url: "https://www.trekbikes.com/us/bikes/fetch-2/"
image: "https://example.com/trek-fetch-2.jpg"
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/bikes/fetch-2/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
specs:
  category: "longtail"
  model_year: 2024
  motor:
    make: "Bosch"
    model: "Performance Line CX"
    power_w: 250
  battery:
    capacity_wh: 500
    removable: true
  weight:
    with_battery_kg: 31
  load_capacity:
    total_kg: 200
    rear_kg: 80
---
```

### File Paths

Organize bike notes as: `vault/notes/bikes/brand-name/bike-model.md`

Examples:

- `vault/notes/bikes/tern/gsd-p10.md`
- `vault/notes/bikes/trek/fetch-plus-2.md`

Use **lowercase, hyphenated** names for both directories and filenames.

## Schema Reference

For complete field definitions, data types, examples, and validation rules, see:
**`docs/schema/BIKE_SPECS_SCHEMA.md`**

### Key Spec Fields

The `specs` object includes:

- **`category`** — Bike type: `longtail`, `box`, `trike`, etc.
- **`frame`** — Material, size, dimensions
- **`weight`** — With/without battery
- **`load_capacity`** — Total weight, rear capacity, passenger config
- **`motor`** — Make, model, type (mid-drive, rear-hub), power, torque, throttle
- **`battery`** — Capacity, configuration, removable, charging time
- **`drivetrain`** — Type (chain/belt), speeds, hub model
- **`brakes`** — Type, rotor sizes
- **`wheels`** — Sizes, tire model
- **`suspension`** — Front and rear details
- **`lights`** — Front/rear types, integration, power source
- **`features`** — Short, hyphenated tags (e.g., `bosch-smart-system`, `integrated-lights`)
- **`security`** — GPS, alarm, app lock, frame lock
- **`range`** — Estimated kilometers and context notes
- **`price`** — MSRP with currency

## Creating a New Bike Note

1. Copy `templates/bike-template.md`
2. Follow the frontmatter structure from `docs/schema/BIKE_SPECS_SCHEMA.md`
3. Place file in `vault/notes/bikes/brand-name/` (create directory if needed)
4. Use lowercase, hyphenated filenames
5. Fill in all known fields; omit optional fields if data is unavailable
6. For tag format, see **CONTRIBUTING.md**

## Validation

- Ensure YAML frontmatter syntax is valid (no missing colons, quotes, or brackets)
- Verify all URLs are properly formatted
- Check that tags are lowercase and hyphenated
- Test that markdown renders correctly
- Confirm date is ISO format (YYYY-MM-DD)

For detailed contribution rules, see **CONTRIBUTING.md**.
