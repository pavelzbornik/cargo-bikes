---
mode: agent
description: "Quick reference for migrating single bike notes to new schema"
---

# Quick Schema Migration Reference

## TL;DR — Fast Migration Path

### For One File

1. Open `vault/notes/bikes/brand-name/bike-name.md`
2. Extract current frontmatter (fields between `---` markers)
3. Parse legacy fields into new schema structure
4. Replace frontmatter, keep all content below
5. Verify: YAML syntax correct, all content preserved
6. Done! Run `python scripts/generate_bike_table.py` to verify

### For Entire Folder

1. List all `.md` files in `vault/notes/bikes/brand-name/`
2. Migrate each file following single file process
3. Run `python scripts/generate_bike_table.py` once
4. Create one PR with all files in that brand folder

## Field Parsing Cheat Sheet

### Motor Parsing

| Legacy Format              | →   | New Schema                                 |
| -------------------------- | --- | ------------------------------------------ |
| `"250W Bosch"`             | →   | `make: Bosch`, `power_w: 250`              |
| `"Bosch 250W"`             | →   | `make: Bosch`, `power_w: 250`              |
| `"Shimano 500W"`           | →   | `make: Shimano`, `power_w: 500`            |
| `"250W"`                   | →   | `power_w: 250` (no make)                   |
| `"Bosch Performance Line"` | →   | `make: Bosch`, `model: "Performance Line"` |

**Default:** `type: "mid-drive"` (can be `rear-hub` or `front-hub` if known)

### Battery Parsing

| Legacy Format       | →   | New Schema                                    |
| ------------------- | --- | --------------------------------------------- |
| `"500Wh"`           | →   | `capacity_wh: 500`, `configuration: "single"` |
| `"500Wh dual"`      | →   | `capacity_wh: 500`, `configuration: "dual"`   |
| `"1000Wh (2x500)"`  | →   | `capacity_wh: 1000`, `configuration: "dual"`  |
| `"500Wh removable"` | →   | `capacity_wh: 500`, `removable: true`         |
| `"~400Wh"`          | →   | `capacity_wh: 400` (remove ~)                 |

### Range Parsing

| Legacy Format    | →   | New Schema                                   |
| ---------------- | --- | -------------------------------------------- |
| `"100-120km"`    | →   | `estimate_km: "100-120"`                     |
| `"120km"`        | →   | `estimate_km: 120`                           |
| `"up to 150km"`  | →   | `estimate_km: "150"`                         |
| `"80-100km eco"` | →   | `estimate_km: "80-100"`, `notes: "eco mode"` |

### Price Parsing

| Legacy Format | →   | New Schema                        |
| ------------- | --- | --------------------------------- |
| `"€3,999"`    | →   | `amount: 3999`, `currency: "EUR"` |
| `"$4,999"`    | →   | `amount: 4999`, `currency: "USD"` |
| `"£2,999"`    | →   | `amount: 2999`, `currency: "GBP"` |
| `"from 4999"` | →   | `amount: "from 4999"` (as string) |
| `"4999€"`     | →   | `amount: 4999`, `currency: "EUR"` |

## Tag Normalization

**Always include:**

- `bike` (required)
- Category: `longtail`, `box`, `trike`, `midtail`, etc.
- Brand: lowercase, hyphenated (e.g., `trek`, `cargo-bikes`)

**Optional:**

- Motor brand: `bosch`, `shimano`, `bafang`
- Features: `integrated-lights`, `dual-battery`

**Before:**

```yaml
tags: [test, 250w, bosch, longtail]
```

**After:**

```yaml
tags: [bike, longtail, trek, bosch]
```

## New Schema Template (Minimal)

```yaml
---
title: "{{Bike Name}}"
type: bike
brand: "{{Brand}}"
model: "{{Model}}"
date: 2025-10-20
tags: [bike, { { category } }, { { brand-lowercase } }]
url: "{{url}}"
image: "{{image}}"
specs:
  category: "{{longtail|box|trike}}"
  motor:
    make: "{{make}}"
    power_w: { { wattage } }
  battery:
    capacity_wh: { { wh } }
  range:
    estimate_km: { { km or "range" } }
  price:
    amount: { { amount } }
    currency: "{{code}}"
---
```

## Common Issues & Solutions

### Issue: Motor field has multiple makes

**Example:** `"Bosch/Shimano 250W"`

**Solution:** Use primary make, add note to specs

```yaml
motor:
  make: "Bosch"
  power_w: 250
  notes: "Compatible with Shimano components"
```

### Issue: Battery has removable + charging info

**Example:** `"500Wh removable, 6h charge"`

**Solution:** Parse all properties

```yaml
battery:
  capacity_wh: 500
  removable: true
  charging_time_h: 6
```

### Issue: Range varies by mode

**Example:** `"eco 120km, normal 80km, boost 50km"`

**Solution:** Use range notes for context

```yaml
range:
  estimate_km: "50-120"
  notes: "Varies by assist level: boost 50km, normal 80km, eco 120km"
```

### Issue: Price is a range

**Example:** `"from €3,500 to €5,000"`

**Solution:** Keep as string for ranges

```yaml
price:
  amount: "from 3500 to 5000"
  currency: "EUR"
```

### Issue: No price available

**Solution:** Omit price section entirely

```yaml
specs:
  motor: ...
  battery: ...
  # price omitted (not available)
```

## Validation Checklist

Before saving migration:

- [ ] YAML syntax valid (no missing colons, brackets)
- [ ] Required fields present: `title`, `type`, `brand`, `model`, `tags`, `date`, `url`, `image`
- [ ] All markdown content below frontmatter unchanged
- [ ] Tags include: `bike`, category, brand (all lowercase/hyphenated)
- [ ] Date is ISO format (YYYY-MM-DD)
- [ ] Specs structure matches schema (only optional fields if data available)
- [ ] Motor: `make` and `power_w` extracted correctly
- [ ] Battery: `capacity_wh` extracted correctly
- [ ] Range: `estimate_km` formatted correctly
- [ ] Price: `amount` and `currency` separated correctly
- [ ] No `null` values (omit optional fields instead)

## After Migration

1. **Verify locally:**

   ```bash
   python scripts/generate_bike_table.py
   ```

   Look for your bike in output and verify data looks correct

2. **Check markdown rendering:**
   - Open file in Obsidian or VS Code
   - Verify YAML frontmatter valid (no red squiggles)
   - Verify content renders correctly

3. **Git commit:**

   ```bash
   git add vault/notes/bikes/brand-name/
   git commit -m "Migrate brand-name bikes to BIKE_SPECS_SCHEMA"
   ```

4. **Create PR with batch:**
   - Group migrations by brand
   - One PR per brand folder
   - Include migration summary

## Examples by Complexity

### Simple (All Fields Present)

**Before:**

```yaml
title: "Gaya Le Cargo"
type: bike
brand: "Gaya"
model: "Le Cargo"
tags: [bike, longtail]
price: "€2,900"
motor: "250W Bosch"
battery: "460Wh"
range: "70km"
image: "url.jpg"
url: "https://gaya.bike/"
```

**After:**

```yaml
title: "Gaya Le Cargo"
type: bike
brand: "Gaya"
model: "Le Cargo"
date: 2025-10-20
tags: [bike, longtail, gaya, bosch]
url: "https://gaya.bike/"
image: "url.jpg"
specs:
  category: "longtail"
  motor:
    make: "Bosch"
    power_w: 250
  battery:
    capacity_wh: 460
  range:
    estimate_km: 70
  price:
    amount: 2900
    currency: "EUR"
```

### Complex (Missing Some Fields)

**Before:**

```yaml
title: "Cargo Bike X"
type: bike
brand: "Unknown"
motor: "Bafang"
battery: "500Wh removable"
tags: [bike]
image: "x.jpg"
```

**After:**

```yaml
title: "Cargo Bike X"
type: bike
brand: "Unknown"
model: ""
date: 2025-10-20
tags: [bike, unknown]
image: "x.jpg"
specs:
  motor:
    make: "Bafang"
  battery:
    capacity_wh: 500
    removable: true
  notes: "Limited data available, migrated from legacy format"
```

### Partial (Only Some Data)

**Before:**

```yaml
title: "DIY Longtail"
type: bike
brand: "DIY"
tags: [bike, diy]
motor: "various"
```

**After:**

```yaml
title: "DIY Longtail"
type: bike
brand: "DIY"
model: ""
date: 2025-10-20
tags: [bike, longtail, diy]
specs:
  category: "longtail"
  motor:
    model: "various"
  notes: "Motor varies, not standardized"
```

## Related Files

- Full guide: `.github/prompts/migrate-schema.prompt.md`
- Schema definition: `docs/schema/BIKE_SPECS_SCHEMA.md`
- Template: `vault/templates/bike-template.md`
- Contribution guide: `CONTRIBUTING.md`
- Migration info: `docs/SCHEMA_MIGRATION_GUIDE.md`
