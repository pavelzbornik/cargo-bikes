---
mode: agent
description: "Fetch bikes from a website and create/update Obsidian vault notes"
---

# Fetch & Document E-Bikes

## Objective

Fetch all e-bikes and their relative accessories from a provided website and create or update Obsidian notes in the cargo-bikes vault following the bike template format.

! IMPORTANT: Do not stop untill all bikes are fetched and documented.
! IMPORTANT: When updating existing notes, preserve any user-added content.

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

Every note **must** include this YAML frontmatter at the top, following the **BIKE_SPECS_SCHEMA** (`docs/schema/BIKE_SPECS_SCHEMA.md`):

```yaml
---
title: "<Bike Name>"
type: bike
brand: "<Bike Brand>"
model: "<Bike Model Name>"
tags: [bike, <bike-type>, <brand-lowercase>]
date: <YYYY-MM-DD>
url: "<Product URL>"
image: "<Bike Image URL>"
resellers:
  - name: "<Reseller Name>"
    url: "<Reseller Product URL>"
    price: <price_amount>
    currency: "<Currency Code>"
    region: "<Region>"
    availability: "<in-stock|pre-order|out-of-stock>"
    note: ""
specs:
  category: "<longtail|box|trike|etc>"
  model_year: <year>
  frame:
    material: "<aluminum|steel|carbon>"
    size: "<size|one size>"
  weight:
    with_battery_kg: <number>
    bike_kg: <number or null>
  load_capacity:
    total_kg: <number>
    rear_kg: <number>
    passenger_count_excluding_rider: <number>
    passenger_config: "<description>"
  motor:
    make: "<Motor Brand>"
    model: "<Motor Model>"
    type: "<mid-drive|rear-hub|front-hub>"
    power_w: <wattage>
    torque_nm: <torque>
    boost_throttle: <true|false>
  battery:
    capacity_wh: <wh>
    configuration: "<single|dual|integrated>"
    removable: <true|false>
    charging_time_h: <hours>
  drivetrain:
    type: "<chain|belt>"
    speeds: <number or "range">
    hub: "<hub model|null>"
  brakes:
    type: "<brake type>"
    front_rotor_mm: <mm>
    rear_rotor_mm: <mm>
  wheels:
    front_size_in: '<size>"'
    rear_size_in: '<size>"'
    tire: "<tire model>"
  suspension:
    front: "<description|none>"
    rear: "<description|none>"
  lights:
    front:
      type: "<description>"
      integrated: <true|false>
      powered_by: "<main battery|dynamo>"
    rear:
      type: "<description>"
      integrated: <true|false>
      brake_light: <true|false>
  features: [tag1, tag2, tag3]
  security:
    gps: <true|false>
    frame_lock: <true|false>
    app_lock: <true|false>
  range:
    estimate_km: <number or "range">
    notes: "<assist level, load, conditions>"
  price:
    amount: <price_amount>
    currency: "<Currency Code>"
  notes: "<optional general notes>"
---
```

**Frontmatter rules:**

- `title`: Full bike name (e.g., "Gaya Le Cargo")
- `tags`: Always include `bike`, plus bike type and brand in **lowercase, hyphenated** format
  - Example: `tags: [bike, long-tail, gaya, bosch]`
- `date`: ISO format (YYYY-MM-DD) — use today's date when fetching
- `brand` & `model`: Use exact names from source (do not translate)
- `url`: Direct link to product page
- `image`: URL to bike image (use official product image if available)
- `specs`: Follow the nested structure defined in `docs/schema/BIKE_SPECS_SCHEMA.md`
- `resellers`: Include vendor information with pricing and availability
  - Only required if multiple vendors available; main manufacturer can be primary reseller
  - Use actual values from the source; use strings like "from 4999" for price ranges

### 4. Fill Template Sections

Using the bike template (`vault/templates/bike-template.md`), populate sections based on fetched data:

**Core Sections (Required):**

- **Overview**: Brief description of the bike's purpose, positioning, and value proposition
- **Technical Specifications**: All specs from the frontmatter `specs` object (motor, battery, drivetrain, brakes, wheels, weight, load capacity, etc.)
- **E-bike Features**: Assist levels, display type, charging time, security features, weather resistance, connectivity

**Standard Sections (Add if data available):**

- **Real-world Performance**: Range, hill performance, comfort, handling, cargo stability
- **Cost & Accessories**: Base price plus recommended accessories breakdown for 2-child transport
- **Cargo Capacity & Use Cases**: Load capacity, child seat compatibility, commuting suitability
- **Maintenance**: Battery care, motor service, brake maintenance
- **Modifications & Customization**: Upgrade options, common modifications, accessory compatibility

**Optional Sections (Include if data exists):**

- **User Reviews & Experiences**: Pros, cons, user quotes
- **Photos & Media**: Links to galleries, videos, community content
- **Professional Reviews**: Links to published reviews
- **References**: Official pages, PDFs, reviews, forums

**If a section lacks data, omit it from the note.**

### Content Guidelines for Each Section

**Technical Specifications:**

- Present all `specs` fields clearly (motor, battery, drivetrain, etc.)
- Use tables for comparisons or accessory pricing
- Include all weight, dimension, and load capacity data

**Cost & Accessories:**

- Create a table with accessories needed for typical 2-child setup
- Include: accessory name, price, where to buy
- Provide total investment calculation

**Real-world Performance:**

- Focus on practical usage: range in city/mixed terrain, hill performance
- Include noise levels, comfort, and handling observations
- Note winter range impact if applicable

**Cargo Capacity & Use Cases:**

- Specify child seat compatibility (number, models)
- Describe typical loads and configurations
- Address commuting, family, and errands use cases

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

Before finalizing each note:

- **YAML frontmatter syntax** — No missing colons, quotes, brackets, or incorrect indentation
- **Schema compliance** — Verify frontmatter structure matches `docs/schema/BIKE_SPECS_SCHEMA.md`
- **Required fields** — Ensure all required top-level fields are present: `title`, `type`, `brand`, `model`, `tags`, `date`, `url`, `image`, `specs`
- **Specs structure** — Check that `specs` is properly nested with appropriate subsections (motor, battery, drivetrain, etc.)
- **Tag format** — Verify tags are lowercase and hyphenated (e.g., `[bike, longtail, trek, bosch]`)
- **Date format** — Confirm date is ISO 8601 (YYYY-MM-DD)
- **URLs functional** — Test that product URL, image URL, and reseller URLs are valid
- **Markdown rendering** — Verify all headers, lists, tables, and links render correctly
- **No missing data** — Use `null` for fields that are applicable but unknown; omit optional fields if not applicable
- **Language** — Ensure content is in English (translate if sourced from other languages)
- **Preserve bike names** — Never translate bike names, brands, model names, or product-specific terms

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
