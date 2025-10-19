# Bike Table Generator Script

## Overview

`scripts/generate_bike_table.py` is a Python utility that automatically generates
a comprehensive bike table for the cargo-bikes vault by:

1. **Reading YAML frontmatter** from all `.md` files in `vault/notes/`
2. **Validating frontmatter** against required fields
3. **Generating a Markdown table** with bike specifications and images
4. **Updating the README.md** with the table (or inserting it if it doesn't exist)

## Requirements

- Python 3.10+
- PyYAML (installed via `pyproject.toml`)

## Usage

### Basic Run

From the repo root:

```bash
python scripts/generate_bike_table.py
```

The script will:

- Scan all subdirectories in `vault/notes/` for `*.md` files
- Extract YAML frontmatter from each file
- Validate required fields: `title`, `type`, `tags`
- Filter only entries with `type: bike`
- Generate a sorted table (by brand, then bike title)
- Update or create the bike table in `README.md`

### Output

Console output shows:

- Total bikes found
- Processing status for each file (`[OK]`, `[ERR]`, `[SKIP]`)
- Preview of generated table
- Confirmation of README update

Example:

```bash
[OK] benno/boost-10d-evo-5.md: Benno Boost 10D EVO 5 500Wh
[OK] douze-cycles/lt1.md: Douze Cycles LT1
...
Total bikes found: 118
```

## YAML Frontmatter Format

The script reads the following frontmatter fields:

### Required Fields

- `title` (string): Bike name/model
- `type` (string): Must be `bike`
- `tags` (list): Metadata tags (e.g., `[bike, longtail, electric]`)

### Optional Fields (displayed in table)

- `brand` (string): Manufacturer name (defaults to folder name)
- `model` (string): Model designation
- `price` (string): Price (any format)
- `motor` (string): Motor power/specs (e.g., "250W", "85Nm")
- `battery` (string): Battery capacity (e.g., "500Wh")
- `range` (string): Estimated range (e.g., "100km")
- `image` (string): URL to bike image

### Example Frontmatter

```yaml
---
title: "Gitane G-Life Longtail"
type: bike
brand: "Gitane"
model: "G-Life Longtail"
tags: [bike, longtail, gitane]
date: 2025-10-19
price: "€4,199"
motor: "85Nm"
battery: "504Wh"
range: "100km"
image: "https://example.com/image.jpg"
---
```

## Table Generation

### Table Columns

| Column  | Source          | Format                             |
| ------- | --------------- | ---------------------------------- |
| Image   | `image` field   | Rendered as embedded image or `--` |
| Bike    | `title` field   | Markdown link to vault note        |
| Brand   | `brand` field   | Brand name (or folder name)        |
| Price   | `price` field   | Any format (€, $, etc.)            |
| Motor   | `motor` field   | Power/torque specs                 |
| Battery | `battery` field | Capacity (Wh)                      |
| Range   | `range` field   | Estimated km                       |

### Sorting

Bikes are sorted by:

1. Brand (alphabetical, case-insensitive)
2. Title (alphabetical, case-insensitive)

Example order:

- ADDBIKE → U-Cargo Family, U-Cargo Lite
- Benno Bikes → Benno Boost 10D..., Benno Boost E..., etc.
- Yuba → Boda Boda, FastRack, Kombi, etc.

## README Integration

### Markers

The script uses HTML comments to identify where the table should be placed:

```markdown
<!-- BIKES_TABLE_START -->

...generated table...

<!-- BIKES_TABLE_END -->
```

### Behavior

- **Existing markers**: Table between markers is replaced with new version
- **No markers**: Table is appended to end of README.md
- **First run**: Add markers manually or let script append

## Validation & Error Handling

### Validation Checks

- **Missing required fields**: File is skipped with `[ERR]` message
- **Invalid YAML**: File is skipped with `[WARN]` message
- **Wrong type**: File is skipped with `[SKIP]` message (e.g., `type: article`)

### Status Codes

| Code     | Meaning                                     |
| -------- | ------------------------------------------- |
| `[OK]`   | Bike successfully added to table            |
| `[ERR]`  | Error: missing fields, no frontmatter, etc. |
| `[SKIP]` | Skipped: wrong type or invalid field values |
| `[WARN]` | Warning: YAML parse issue (file skipped)    |

### Cell Formatting

Fields that exceed max width are truncated with ellipsis:

- Brand: max 20 chars
- Price: max 15 chars
- Motor: max 20 chars
- Battery: max 15 chars
- Range: max 15 chars

Example: `"Shimano STEPS EP6 Cargo"` → `"Shimano STEPS EP6..."`

Empty or missing values display as `--`

## Performance

- **Speed**: ~0.5s to scan 118 bikes
- **Output**: Console + README update
- **File I/O**: One read per `.md` file, one write to `README.md`

## Common Tasks

### Add a new bike

1. Create `vault/notes/brand/bike-name.md`
2. Add required frontmatter: `title`, `type: bike`, `tags`
3. Add optional fields: `brand`, `price`, `motor`, `battery`, `range`, `image`
4. Run: `python scripts/generate_bike_table.py`

### Update bike specs

1. Edit the frontmatter in the bike's `.md` file
2. Run: `python scripts/generate_bike_table.py`
3. README table auto-updates

### Troubleshoot missing bike

1. Check if `type: bike` is set (not `type: article`, etc.)
2. Check if all required fields exist: `title`, `type`, `tags`
3. Run with console output to see `[ERR]` or `[SKIP]` status
4. Fix frontmatter and re-run

## Integration with Pre-commit

The script is configured to run automatically on commit when `.md` files change:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: generate-bike-table
      name: Generate Bike Table
      entry: python scripts/generate_bike_table.py
      language: python
      files: ^vault/notes/.*\.md$
      stages: [commit]
      additional_dependencies: ["pyyaml"]
```

See `.pre-commit-config.yaml` for current configuration.

## License

Same as the cargo-bikes repository.
