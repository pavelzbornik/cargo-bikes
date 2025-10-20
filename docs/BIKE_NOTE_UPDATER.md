# Bike Note Updater User Guide

The Bike Note Updater is an intelligent agent that automatically keeps bike notes up to date by fetching current product information from manufacturer websites, validating notes against the BIKE_SPECS_SCHEMA, and intelligently merging new data while preserving user-added content.

## Features

- **Automated Data Fetching**: Retrieve current specs from manufacturer product pages
- **Schema Validation**: Ensure all notes comply with BIKE_SPECS_SCHEMA
- **Intelligent Merging**: Update specifications while preserving user content
- **Conflict Detection**: Flag significant changes for manual review
- **Batch Processing**: Update multiple bikes at once
- **CLI Interface**: Simple command-line tools for all operations

## Installation

The bike note updater is part of the cargo-bikes project. Ensure you have the required dependencies installed:

```bash
# Using pip
pip install -e .

# Or using uv (recommended)
uv sync
```

## Command-Line Usage

### Update a Single Bike Note

Update a specific bike note by providing its file path:

```bash
python -m scripts.bike_note_updater.cli update-bike vault/notes/bikes/trek/fetch-2.md
```

Options:
- `--no-fetch-url`: Skip fetching data from the product URL
- `--dry-run`: Preview changes without writing to disk
- `--validate-only`: Only validate, don't fetch or update

Example with options:

```bash
# Preview changes without writing
python -m scripts.bike_note_updater.cli update-bike vault/notes/bikes/trek/fetch-2.md --dry-run

# Only validate the note
python -m scripts.bike_note_updater.cli update-bike vault/notes/bikes/trek/fetch-2.md --validate-only
```

### Update All Bike Notes

Update all bike notes in the vault:

```bash
python -m scripts.bike_note_updater.cli update-all-bikes
```

Options:
- `--vault-path PATH`: Path to vault root (default: "vault")
- `--brand BRAND`: Update only specific brand (e.g., "trek", "tern")
- `--validate-only`: Only validate, don't update
- `--dry-run`: Preview changes without writing

Examples:

```bash
# Update all Trek bikes
python -m scripts.bike_note_updater.cli update-all-bikes --brand trek

# Validate all bikes without updating
python -m scripts.bike_note_updater.cli update-all-bikes --validate-only

# Preview updates for all bikes
python -m scripts.bike_note_updater.cli update-all-bikes --dry-run
```

### Validate All Notes

Validate all notes against the BIKE_SPECS_SCHEMA without making changes:

```bash
python -m scripts.bike_note_updater.cli validate-all-notes
```

Options:
- `--vault-path PATH`: Path to vault root
- `--brand BRAND`: Validate only specific brand

### Check Product URLs

Check if all product URLs in notes are still valid and reachable:

```bash
python -m scripts.bike_note_updater.cli check-urls
```

Options:
- `--vault-path PATH`: Path to vault root
- `--brand BRAND`: Check only specific brand

Example:

```bash
# Check URLs for Trek bikes only
python -m scripts.bike_note_updater.cli check-urls --brand trek
```

## Understanding the Output

### Success Messages

When a note is successfully updated, you'll see:

```
✓ Success: Trek Fetch+ 2
Changes made:
  - specs.motor: updated
  - image: old-image.jpg -> new-image.jpg
```

### Conflict Warnings

Significant changes are flagged as conflicts for manual review:

```
⚠ Conflicts detected:
  - motor.power_w: 250 -> 350 (major)
  - specs.weight.with_battery_kg: 30 -> 35 (major)
```

### Validation Errors

If a note fails validation:

```
✗ Failed: Test Bike
  Error: Required field 'title' is missing or empty
  Error: Date '01/15/2024' is not in ISO 8601 format (YYYY-MM-DD)
```

## What Gets Updated

The updater intelligently merges new data while preserving your work:

### Always Updated
- Product specifications (motor, battery, weight, etc.)
- Product image URLs
- Product URLs
- Reseller pricing and availability

### Always Preserved
- User-written markdown sections (reviews, notes, modifications)
- Date field (only set on note creation)
- Tags
- Custom fields not in the schema

### Conflict Detection

Changes that exceed the conflict threshold (default: 10%) are flagged:

- **Minor conflicts**: Price changes < 5%, minor spec updates
- **Major conflicts**: Motor/battery model changes, weight changes > 10%
- **Unresolvable**: Require manual intervention

## Best Practices

1. **Run Validation First**: Always run validation before updating:
   ```bash
   python -m scripts.bike_note_updater.cli validate-all-notes
   ```

2. **Use Dry Run Mode**: Preview changes before committing:
   ```bash
   python -m scripts.bike_note_updater.cli update-all-bikes --dry-run
   ```

3. **Update Brand by Brand**: For large vaults, process one brand at a time:
   ```bash
   python -m scripts.bike_note_updater.cli update-all-bikes --brand trek
   ```

4. **Review Conflicts**: Always review flagged conflicts before accepting changes

5. **Check URLs Regularly**: Ensure product URLs are still valid:
   ```bash
   python -m scripts.bike_note_updater.cli check-urls
   ```

## Schema Compliance

All generated notes must comply with the BIKE_SPECS_SCHEMA defined in `docs/schema/BIKE_SPECS_SCHEMA.md`.

### Required Fields

- `title`: Bike name
- `type`: Must be "bike"
- `tags`: List including "bike" and relevant tags
- `date`: ISO 8601 format (YYYY-MM-DD)

### Recommended Fields in specs

- `category`: Bike category (longtail, box, etc.)
- `motor`: Motor specifications
- `battery`: Battery specifications
- `weight`: Bike weight

See the full schema documentation for complete field definitions.

## Troubleshooting

### "Failed to fetch from URL"

**Cause**: Product page is unreachable or requires authentication

**Solution**: 
- Check if the URL is still valid
- Try accessing the page in a browser
- Update the URL if the product page has moved

### "Validation failed: Type must be 'bike'"

**Cause**: The `type` field is not set to "bike"

**Solution**: Manually edit the frontmatter to set `type: bike`

### "Tag format warning"

**Cause**: Tags are not in lowercase, hyphenated format

**Solution**: The updater will warn but not fail. Consider normalizing tags manually:
- "BIKE" → "bike"
- "Cargo Bike" → "cargo-bike"

### "No URL found in frontmatter"

**Cause**: The note doesn't have a `url` field

**Solution**: Add a product URL to the frontmatter to enable fetching

## Advanced Usage

### Programmatic Usage

You can use the updater programmatically in your own scripts:

```python
import asyncio
from pathlib import Path
from scripts.bike_note_updater.agent import BikeNoteUpdater

async def update_my_bike():
    updater = BikeNoteUpdater()
    try:
        result = await updater.update_bike(
            note_path=Path("vault/notes/bikes/trek/fetch-2.md"),
            fetch_url=True,
            dry_run=False
        )
        print(f"Success: {result.success}")
        print(f"Changes: {result.changes_made}")
    finally:
        updater.close()

asyncio.run(update_my_bike())
```

### Custom Conflict Threshold

Adjust the conflict detection threshold:

```python
updater = BikeNoteUpdater(conflict_threshold=0.05)  # 5% threshold
```

## Support

For issues, questions, or contributions:

- GitHub Issues: [cargo-bikes/issues](https://github.com/pavelzbornik/cargo-bikes/issues)
- Documentation: See `scripts/bike_note_updater/README.md` for developer guide
- Schema Reference: `docs/schema/BIKE_SPECS_SCHEMA.md`
