---
mode: agent
description: "Migrate bike notes from legacy format to BIKE_SPECS_SCHEMA"
---

# Migrate Bike Notes to New Schema

## Objective

Migrate bike note frontmatter from legacy format to the new **BIKE_SPECS_SCHEMA** format, while preserving all content and user-added notes. Can process a single file or all files in a folder/brand.

! IMPORTANT: Preserve all markdown content below frontmatter
! IMPORTANT: Keep any user-added notes, reviews, and customizations
! IMPORTANT: If a note already has specs structure, update it carefully
! IMPORTANT: Only migrate required fields; omit optional fields if not available

## Process

### 1. Identify Migration Target

Choose one of:

- **Single file**: `vault/notes/bikes/brand-name/bike-name.md`
- **Entire brand folder**: `vault/notes/bikes/brand-name/`
- **Multiple brands**: List specific folders to process

## 2. Analyze Current Frontmatter

Read the current YAML frontmatter and identify:

- **Required fields** (present): `title`, `type`, `brand`, `model`, `date`, `tags`, `url`, `image`
- **Legacy fields** (to migrate): `price`, `motor`, `battery`, `range`
- **Optional legacy fields**: Any others at top level
- **Existing specs**: If `specs` object already exists, preserve and enhance it
- **Content preservation**: All markdown content must remain unchanged
- **Completeness assessment**: Which fields have sufficient data vs. which need URL enrichment

## 3. Extract and Parse Legacy Values

For each legacy field, intelligently parse the value:

### Motor Field Parsing

Parse `motor: "250W Bosch"` or `motor: "Shimano 500W"` into:

- `make`: Extract brand (Bosch, Shimano, Bafang, etc.)
- `power_w`: Extract wattage as number
- `type`: Default to "mid-drive" if not specified (can be mid-drive, rear-hub, front-hub)

**Examples:**

- `"250W Bosch"` → `make: "Bosch", power_w: 250`
- `"Shimano 250W"` → `make: "Shimano", power_w: 250`
- `"500W"` → `power_w: 500` (no make)
- `"Bosch Performance Line CX"` → `make: "Bosch", model: "Performance Line CX"` (if model detectable)

**If unparseable or insufficient:**

- Keep entire value in `specs.motor.model`
- Note field as incomplete in analysis
- **Plan to fetch missing data from manufacturer URL** (see section below)

### Battery Field Parsing

Parse `battery: "500Wh"` or `battery: "500Wh dual"` into:

- `capacity_wh`: Extract numeric capacity
- `configuration`: Detect "single", "dual", "integrated", or default to "single"

**Examples:**

- `"500Wh"` → `capacity_wh: 500, configuration: "single"`
- `"500Wh dual"` → `capacity_wh: 500, configuration: "dual"` (or total if two batteries listed)
- `"1000Wh (2x500)"` → `capacity_wh: 1000, configuration: "dual"`
- `"500Wh removable"` → `capacity_wh: 500, removable: true`

**If unparseable or insufficient:**

- Keep entire value in string format
- Note field as incomplete in analysis
- **Plan to fetch missing data from manufacturer URL** (see section below)

### Range Field Parsing

Parse `range: "100-120km"` or `range: "100km"` into:

- `estimate_km`: Keep as string (e.g., "100-120") or number if single value
- `notes`: Add context if available (e.g., "eco mode, no load")

**Examples:**

- `"100-120km"` → `estimate_km: "100-120"`
- `"120km"` → `estimate_km: 120`
- `"up to 150km"` → `estimate_km: "150"` (approximate)

**If unparseable or insufficient:**

- Keep as-is
- Note field as incomplete in analysis
- **Plan to fetch missing data from manufacturer URL** (see section below)

### Price Field Parsing

Parse `price: "€3,999"` or `price: "from 4999"` into:

- `amount`: Extract numeric amount or keep as string
- `currency`: Extract currency code (USD, EUR, GBP) or keep symbol mapping

**Examples:**

- `"€3,999"` → `amount: 3999, currency: "EUR"`
- `"$4,999"` → `amount: 4999, currency: "USD"`
- `"£2,999"` → `amount: 2999, currency: "GBP"`
- `"from 4999"` → `amount: "from 4999"` (as string)

**If unparseable or insufficient:**

- Keep as-is
- Note field as incomplete in analysis
- **Plan to fetch missing data from manufacturer URL** (see section below)

## 3a. Enrich Specs from Manufacturer URL (If Data Insufficient)

**When to fetch:** If any critical specs are missing or unclear from legacy data:

- Motor: Missing make or wattage
- Battery: Missing capacity or unclear
- Range: Not specified or unclear
- Price: Listed as "on request" or "contact us"

**How to fetch:**

1. Access the `url` field from frontmatter (manufacturer's official website)
2. Search the page for relevant specification keywords:
   - **Motor:** "Bosch", "Shimano", "Bafang", "250W", "500W", "750W", "motor", "drive"
   - **Battery:** "Wh", "kWh", "battery", "capacity", "removable", "integrated"
   - **Range:** "range", "autonomy", "distance", "km", "miles", "endurance"
   - **Price:** "€", "$", "£", "price", "cost", "starting at", "from"
3. Extract the most specific/reliable values found
4. Parse extracted data using the parsing rules above
5. Document all sourced data in `specs.notes`: _"Additional specs sourced from [source]: motor wattage, range estimate, price"_
6. Include in migration summary which fields were URL-enriched

**Example - URL Enrichment Workflow:**

```yaml
# Original frontmatter (incomplete):
title: "Example Cargo Bike"
motor: "Bosch" # Incomplete (no wattage)
battery: "not listed" # Missing
range: "" # Empty
price: "on request" # Unavailable
url: "https://example-bikes.com/model-x"

# After accessing URL and extracting specs:
# Extracted from https://example-bikes.com/model-x:
#   - "Bosch Performance Line 500W" → motor.make: Bosch, motor.power_w: 500
#   - "48V 17.5Ah (840Wh)" → battery.capacity_wh: 840
#   - "up to 120km in eco mode" → range.estimate_km: 120
#   - "€4,999" → price.amount: 4999, price.currency: EUR

# Migrated frontmatter with URL-enriched specs:
specs:
  motor:
    make: "Bosch"
    power_w: 500 # ← fetched from URL
  battery:
    capacity_wh: 840 # ← fetched from URL
  range:
    estimate_km: 120 # ← fetched from URL
  price:
    amount: 4999 # ← fetched from URL
    currency: "EUR"
  notes: "Motor wattage (500W), battery capacity (840Wh), and range (120km eco) sourced from manufacturer specifications page"
```

**Important:**

- Only fetch from official manufacturer URLs (not reseller or review sites)
- Prioritize official specs over unofficial claims
- If URL is unreachable or specs are unclear, omit the field and note in migration summary
- Always credit the source in `specs.notes`

## 4. Create New Frontmatter Structure

Build new frontmatter following `docs/schema/BIKE_SPECS_SCHEMA.md`:

```yaml
---
title: "{{title}}"
type: bike
brand: "{{brand}}"
model: "{{model}}"
date: { { date or YYYY-MM-DD } }
tags: [bike, { { category } }, { { brand-lowercase } }]
url: "{{url}}"
image: "{{image}}"
specs:
  category: "{{longtail|box|trike|etc}}"
  motor:
    make: "{{extracted_make}}"
    power_w: { { extracted_wattage } }
    type: "mid-drive"
  battery:
    capacity_wh: { { extracted_capacity } }
    configuration: "{{single|dual}}"
  range:
    estimate_km: { { extracted_range } }
  price:
    amount: { { extracted_amount } }
    currency: "{{currency_code}}"
  notes: "{{migrated_from_legacy}}"
---
```

**Rules:**

- **Required fields:** Keep all top-level required fields
- **Optional specs fields:** Only include if data is available
- **Omit:** Fields without data (don't use null for optional fields)
- **Preserve brand folder name:** Use existing brand from file path if frontmatter brand is missing
- **ISO date:** If `date` field missing, use today's date or current note date
- **Tags format:** Lowercase, hyphenated (e.g., `[bike, longtail, trek, bosch]`)
- **Category guessing:** Infer from tags or bike name if not explicit (longtail, box, trike, etc.)

## 5. Preserve Content

**Critical:** Preserve all markdown content unchanged:

- Keep all sections: Overview, Technical Specifications, E-bike Features, etc.
- Keep all user reviews, community content, customization notes
- Keep all References and links
- Only replace frontmatter YAML block

## 6. Handle Edge Cases

### Already Has Specs

If note already contains `specs` object:

- Review existing `specs` structure
- Merge new parsed data carefully (don't overwrite hand-crafted specs)
- If conflict: Prefer existing `specs` data (user may have added detailed info)
- Update `specs.notes` to indicate migration/merge occurred

### Missing Required Data

If legacy field is missing or empty:

- Omit the spec section entirely if no data available
- Note in migration summary what data was missing
- Do not use defaults like "unknown" or "N/A" in specs

### Ambiguous Values

If a legacy field cannot be clearly parsed:

- Keep the original string in an appropriate `specs` subfield
- Add a note in `specs.notes` about the ambiguity
- Include in migration summary
- Example: `specs.motor.model: "Bosch Performance Line CX"` (if make/power can't be separated)

### Mixed Tags

Current tags might not follow new format (e.g., `[test, 250w, bosch]`):

- Normalize to lowercase, hyphenated format: `[bike, longtail, bosch]`
- Ensure always includes: `bike` and category type
- Always include: brand name in lowercase

## 7. Quality Checks

Before finalizing each migration:

- **YAML syntax** — No missing colons, brackets, or indentation errors
- **Schema structure** — Matches `docs/schema/BIKE_SPECS_SCHEMA.md`
- **Required fields** — Title, type, brand, model, tags, date, url, image present
- **Specs optional fields** — Only included if data available
- **Content preserved** — All markdown content below frontmatter unchanged
- **Tags normalized** — Lowercase, hyphenated, includes bike category and brand
- **Date format** — ISO 8601 (YYYY-MM-DD)
- **No data loss** — Unparseable data noted in migration summary
- **URL enrichment documented** — If specs were sourced from URL, noted in `specs.notes`
- **Source attribution** — All fetched data credited to manufacturer website in notes

## 8. Migration Summary

After processing each file or batch, provide:

- **Status**: ✅ Migrated / ⚠️ Needs Review / ❌ Error
- **File**: Path to updated note
- **Extraction Results**:
  - Motor: Extracted values, parse issues, or "enriched from URL"
  - Battery: Extracted values, parse issues, or "enriched from URL"
  - Range: Extracted values, parse issues, or "enriched from URL"
  - Price: Extracted values, parse issues, or "enriched from URL"
- **URL Enrichment**: Which specs were fetched from manufacturer website (if any)
- **Notes**: Any ambiguities, missing data, special handling, or URL issues
- **Content**: Confirmed preserved / Changes made

## Example Migration

### Before (Legacy Format)

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
tags: [bike, longtail]
price: "$5,999"
motor: "250W Bosch"
battery: "500Wh"
range: "50-120km"
image: "https://example.com/trek.jpg"
url: "https://trekbikes.com/fetch-2/"
---

## Overview

Amazing longtail cargo bike for families.

## Technical Specifications

...

## User Reviews

> "Best bike ever!" — John
```

### After (New Schema)

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2025-10-20
tags: [bike, longtail, trek, bosch]
url: "https://trekbikes.com/fetch-2/"
image: "https://example.com/trek.jpg"
specs:
  category: "longtail"
  motor:
    make: "Bosch"
    power_w: 250
    type: "mid-drive"
  battery:
    capacity_wh: 500
    configuration: "single"
  range:
    estimate_km: "50-120"
  price:
    amount: 5999
    currency: "USD"
  notes: "Migrated from legacy format"
---

## Overview

Amazing longtail cargo bike for families.

## Technical Specifications

...

## User Reviews

> "Best bike ever!" — John
```

### Migration Summary

```text
✅ MIGRATED: vault/notes/bikes/trek/fetch-plus-2.md

Extraction Results:
- Motor: ✅ Bosch 250W parsed successfully
- Battery: ✅ 500Wh parsed successfully
- Range: ✅ 50-120km parsed successfully
- Price: ✅ USD 5999 parsed successfully
- URL Enrichment: None needed (all specs complete)

All content preserved ✓
```

### Example with URL Enrichment

**Before (Incomplete):**

```yaml
---
title: "Urban Arrow Family"
type: bike
brand: "Urban Arrow"
model: "Family"
motor: "Bosch"
battery: "not specified"
range: ""
price: "contact sales"
url: "https://www.urbanarrrow.com/family"
---
```

**After (Enriched from URL):**

```yaml
---
title: "Urban Arrow Family"
type: bike
brand: "Urban Arrow"
model: "Family"
date: 2025-10-20
tags: [bike, box, urban-arrow, bosch]
url: "https://www.urbanarrrow.com/family"
specs:
  category: "box"
  motor:
    make: "Bosch"
    power_w: 250 # sourced from manufacturer specs
  battery:
    capacity_wh: 500 # sourced from manufacturer specs
  range:
    estimate_km: "50-100" # sourced from manufacturer specs
  notes: "Motor wattage, battery capacity, and range sourced from Urban Arrow specifications page"
---
```

**Migration Summary:**

```text
✅ MIGRATED: vault/notes/bikes/urban-arrow/family.md

Extraction Results:
- Motor: ⚠️ Parsed "Bosch" as make, wattage missing (enriched from URL: 250W)
- Battery: ❌ Not specified (enriched from URL: 500Wh)
- Range: ❌ Empty (enriched from URL: 50-100km)
- Price: ⚠️ "contact sales" kept as-is (no URL data found)
- URL Enrichment: ✅ Fetched motor wattage, battery capacity, and range from https://www.urbanarrrow.com/family

All content preserved ✓
```

## Batch Migration

For migrating entire brand folder or multiple brands:

- List all `.md` files in target folder(s)
- For each file, follow migration process
- Provide summary table:

| File                 | Motor | Battery | Range | Price | Status       |
| -------------------- | ----- | ------- | ----- | ----- | ------------ |
| trek/fetch-plus-2.md | ✅    | ✅      | ✅    | ✅    | Migrated     |
| trek/fetch-plus.md   | ✅    | ⚠️      | ✅    | ❌    | Needs Review |
| ...                  |       |         |       |       |              |

- Highlight files needing manual review
- Summarize any migration issues or ambiguities

## Notes

- **One migration at a time** — Process one file or folder, then verify before proceeding
- **Test table generation** — After migrating bikes, run `python scripts/generate_bike_table.py` to verify
- **Preserve user work** — Be especially careful with custom sections and reviews
- **Follow CONTRIBUTING.md** — After migration, adhere to new contribution guidelines
- **Update README** — After batch migrations, regenerate the bike table
- **Create PR per batch** — Each migration batch should be one logical PR
