# AI Agent: Bike Note Updater

## Objective

Create and maintain a PydanticAI-based agent that automatically keeps bike notes up to date by:

1. Fetching current bike product information from manufacturer websites
2. Validating existing bike notes against the BIKE_SPECS_SCHEMA
3. Updating outdated specifications when the schema changes
4. Merging new product data with existing user-added content
5. Ensuring all notes comply with the schema structure

The agent should be **scheduled** to periodically update a queue of bikes and **manually triggerable** via CLI to update specific bikes or all bikes.

---

## Architecture Overview

### Agent Core Components

#### 1. **Data Fetcher**

- Retrieve product pages from manufacturer URLs stored in bike note frontmatter
- Extract key specifications (motor, battery, price, availability, weight, etc.)
- Handle pagination, redirects, and anti-bot protections gracefully
- Support both structured data (JSON-LD, microdata) and web scraping as fallbacks
- Cache fetched data to avoid repeated requests within a 24-hour window

#### 2. **Schema Validator**

- Load the BIKE_SPECS_SCHEMA from `docs/schema/BIKE_SPECS_SCHEMA.md`
- Validate existing bike notes against the schema
- Identify missing, outdated, or incorrectly formatted fields
- Generate validation reports with specific issues and suggestions

#### 3. **Merger**

- Merge fetched product data with existing note content
- Preserve all user-added content (reviews, customizations, community notes)
- Update only schema-defined fields (specs, price, resellers, availability)
- Detect conflicts and log them for manual review

#### 4. **Writer**

- Generate properly formatted YAML frontmatter compliant with BIKE_SPECS_SCHEMA
- Update bike note markdown files with merged data
- Maintain proper indentation and syntax
- Ensure all URLs are valid and images are accessible

---

## Implementation Specification

### Technology Stack

- **Framework:** PydanticAI (for LLM-powered reasoning and task planning)
- **Dependencies:**
  - `pydantic`: Data validation and schema modeling
  - `pydantic-ai`: Agent framework with LLM reasoning
  - `httpx`: Async HTTP client for web fetching
  - `beautifulsoup4`: HTML parsing and data extraction
  - `pyyaml`: YAML file handling
  - `python-dateutil`: Date parsing and manipulation
  - `pytest`: Testing framework
  - `click` or `typer`: CLI interface

### Project Structure

```bash
scripts/
├── __init__.py
├── bike_note_updater/
│   ├── __init__.py
│   ├── agent.py                    # Main PydanticAI agent
│   ├── data_fetcher.py             # Product page fetching logic
│   ├── schema_validator.py         # Validation against BIKE_SPECS_SCHEMA
│   ├── note_merger.py              # Merge fetched data with existing notes
│   ├── note_writer.py              # Write updated notes to disk
│   ├── models.py                   # PydanticAI models and schemas
│   ├── utils.py                    # Helper utilities (URL validation, parsing, etc.)
│   └── cli.py                      # CLI entry point
├── generate_bike_table.py           # (existing)
├── validate_urls.py                # (existing)
└── bike_note_updater_tests/        # or under tests/
    ├── test_agent.py
    ├── test_data_fetcher.py
    ├── test_schema_validator.py
    ├── test_note_merger.py
    └── test_note_writer.py
```

### Key Modules

#### `agent.py`

The main PydanticAI agent that orchestrates the update workflow:

```python
from pydantic_ai import Agent

agent = Agent(
    model="claude-3-5-sonnet",  # or configurable via env
    system_prompt="""
    You are a Bike Note Updater agent. Your task is to:
    1. Fetch current bike information from product pages
    2. Validate notes against the BIKE_SPECS_SCHEMA
    3. Merge new data with existing content
    4. Generate updated bike notes that comply with the schema

    Follow all rules in the schema strictly. Preserve user-added content.
    Report any conflicts or data issues clearly.
    """
)

@agent.tool
def fetch_bike_data(url: str) -> dict:
    """Fetch bike product data from URL"""
    pass

@agent.tool
def validate_frontmatter(frontmatter: dict) -> ValidationReport:
    """Validate frontmatter against BIKE_SPECS_SCHEMA"""
    pass

@agent.tool
def merge_notes(old_note: dict, new_data: dict) -> dict:
    """Merge fetched data with existing note"""
    pass

async def update_bike(note_path: str) -> UpdateResult:
    """Main update workflow for a single bike"""
    pass
```

#### `data_fetcher.py`

Fetches and extracts bike specification data:

```python
class DataFetcher:
    async def fetch_from_url(self, url: str) -> dict:
        """Fetch product page and extract structured data"""
        # Try JSON-LD or microdata first
        # Fall back to beautifulsoup scraping
        # Return: {title, specs, price, image, availability, ...}

    def extract_specs(self, html: str) -> dict:
        """Extract motor, battery, drivetrain, etc. from HTML"""
        pass

    def extract_price_reseller_info(self, html: str) -> list:
        """Extract reseller pricing and availability"""
        pass

    def validate_fetched_urls(self, urls: list) -> dict:
        """Check if product URLs still exist (200 status)"""
        pass
```

#### `schema_validator.py`

Validates bike notes against BIKE_SPECS_SCHEMA:

```python
class SchemaValidator:
    def __init__(self, schema_path: str = "docs/schema/BIKE_SPECS_SCHEMA.md"):
        self.schema = self.load_schema(schema_path)

    def validate_frontmatter(self, frontmatter: dict) -> ValidationReport:
        """
        Returns:
        - missing_required_fields: list
        - invalid_field_types: dict
        - deprecated_fields: list
        - suggestions: list
        """
        pass

    def validate_specs_structure(self, specs: dict) -> dict:
        """Validate nested specs against schema"""
        pass

    def check_tag_format(self, tags: list) -> bool:
        """Ensure tags are lowercase, hyphenated"""
        pass

    def check_date_format(self, date_str: str) -> bool:
        """Ensure date is ISO 8601 (YYYY-MM-DD)"""
        pass
```

#### `note_merger.py`

Intelligently merges fetched data with existing notes:

```python
class NoteMerger:
    def merge(self,
              existing_frontmatter: dict,
              new_data: dict,
              preserve_sections: list = None) -> MergeResult:
        """
        Merge strategy:
        1. Update all fields in 'specs', 'resellers', 'price'
        2. Keep existing 'date' (set to today only if note is new)
        3. Preserve existing content sections (markdown body)
        4. Flag conflicts for manual review

        Returns:
        - merged_frontmatter: dict
        - conflicts: list
        - preserved_sections: list
        """
        pass

    def detect_conflicts(self, old_value, new_value) -> Conflict:
        """Identify significant discrepancies"""
        pass
```

#### `note_writer.py`

Writes updated notes to disk with proper formatting:

```python
class NoteWriter:
    def write_note(self,
                   file_path: str,
                   frontmatter: dict,
                   body: str,
                   validate: bool = True) -> WriteResult:
        """
        1. Validate frontmatter against schema (if validate=True)
        2. Format YAML with proper indentation
        3. Write to file
        4. Verify markdown syntax

        Returns: {success, path, errors, warnings}
        """
        pass

    def format_frontmatter(self, frontmatter: dict) -> str:
        """Format frontmatter to valid YAML"""
        pass
```

#### `models.py`

PydanticAI models for type safety:

```python
from pydantic import BaseModel, Field

class BikeSpecs(BaseModel):
    """Represents the specs section of BIKE_SPECS_SCHEMA"""
    category: str
    model_year: int
    frame: dict
    weight: dict
    load_capacity: dict
    motor: dict
    battery: dict
    drivetrain: dict
    brakes: dict
    wheels: dict
    suspension: dict = None
    lights: dict = None
    features: list[str] = []
    security: dict = None
    range: dict = None
    price: dict
    notes: str = None

class BikeFrontmatter(BaseModel):
    """Top-level frontmatter for a bike note"""
    title: str
    type: str = "bike"
    brand: str
    model: str
    tags: list[str]
    date: str
    url: str
    image: str
    resellers: list[dict] = []
    specs: BikeSpecs

class ValidationReport(BaseModel):
    """Report from schema validation"""
    is_valid: bool
    missing_fields: list[str]
    invalid_fields: dict
    suggestions: list[str]

class UpdateResult(BaseModel):
    """Result of a single bike update"""
    success: bool
    bike_name: str
    note_path: str
    changes_made: dict
    conflicts: list[str]
    errors: list[str]
    timestamp: str
```

#### `cli.py`

Command-line interface for triggering updates:

```python
import typer

app = typer.Typer()

@app.command()
def update_bike(
    note_path: str = typer.Argument(..., help="Path to bike note file"),
    fetch_url: bool = typer.Option(True, help="Fetch from product URL"),
    validate_only: bool = typer.Option(False, help="Only validate, don't update"),
):
    """Update a single bike note"""
    pass

@app.command()
def update_all_bikes(
    brand: str = typer.Option(None, help="Update only specific brand"),
    validate_only: bool = typer.Option(False, help="Only validate, don't update"),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
):
    """Update all bike notes"""
    pass

@app.command()
def validate_all_notes(
    brand: str = typer.Option(None, help="Validate only specific brand"),
):
    """Validate all notes against schema"""
    pass

@app.command()
def check_urls():
    """Check that all product URLs in notes are still valid"""
    pass

if __name__ == "__main__":
    app()
```

---

## Agent Workflow

### Single Bike Update Flow

1. **Load existing note** from file path
2. **Parse frontmatter** and body (markdown content)
3. **Extract product URL** from frontmatter
4. **Fetch current product data** via DataFetcher
   - Try structured data (JSON-LD, microdata)
   - Fall back to web scraping
   - Cache the result
5. **Validate existing frontmatter** against schema
6. **Merge new data with existing note** via NoteMerger
   - Update specs, price, resellers, availability
   - Preserve all markdown body sections
   - Flag conflicts
7. **Validate merged frontmatter** again
8. **Write updated note** to disk if valid
9. **Log results** with conflicts and changes

### Batch Update Flow

1. **Scan all bike notes** in `vault/notes/bikes/`
2. **Filter by criteria** (brand, date range, schema compliance, etc.)
3. **Queue for processing** (prioritize outdated or invalid notes)
4. **Process each bike** via single bike workflow
5. **Generate summary report** with statistics and conflicts
6. **Optional:** Create pull request with changes (future enhancement)

---

## Data Extraction Rules

### From Manufacturer Product Pages

Extract the following from product pages and map to BIKE_SPECS_SCHEMA:

| Schema Field                                    | Extraction Source                                |
| ----------------------------------------------- | ------------------------------------------------ |
| `motor.make`                                    | Product page specifications section, motor brand |
| `motor.model`                                   | Product page specifications, motor model name    |
| `motor.power_w`                                 | Specifications, motor power in watts             |
| `motor.torque_nm`                               | Specifications, motor torque (Newton-meters)     |
| `battery.capacity_wh`                           | Specifications, battery watt-hours               |
| `battery.removable`                             | Product description or spec sheet                |
| `battery.charging_time_h`                       | Specifications or manual                         |
| `weight.with_battery_kg`                        | Specifications section                           |
| `load_capacity.total_kg`                        | Specifications or product description            |
| `wheels.front_size_in`, `wheels.rear_size_in`   | Specifications                                   |
| `specs.price.amount`, `specs.price.currency`    | Product page price display                       |
| `resellers[].price`, `resellers[].availability` | Current retailer listings                        |

### Conflict Handling

If fetched data conflicts with existing values:

- **Minor conflicts** (e.g., price updated by <5%): Auto-merge with note in merged data
- **Major conflicts** (e.g., motor changed, weight differs by >10%): Flag for manual review
- **Unresolvable conflicts**: Report and skip update, require manual intervention

---

## Configuration & Environment

### Environment Variables

```bash
BIKE_UPDATER_MODEL=claude-3-5-sonnet          # LLM model for PydanticAI
BIKE_UPDATER_FETCH_TIMEOUT=30                 # HTTP request timeout in seconds
BIKE_UPDATER_CACHE_DIR=.cache/bike_fetches    # Cache directory
BIKE_UPDATER_CACHE_TTL=86400                  # Cache TTL in seconds (24h)
BIKE_UPDATER_PRESERVE_SECTIONS=references,user-reviews  # Sections to never overwrite
BIKE_UPDATER_DRY_RUN=false                    # Preview mode
BIKE_UPDATER_LOG_LEVEL=INFO                   # Logging level
BIKE_UPDATER_CONFLICT_THRESHOLD=0.1           # Conflict threshold for flagging (10% difference)
```

### Configuration File (Optional)

```yaml
# scripts/bike_note_updater/config.yaml
model: claude-3-5-sonnet
fetch_timeout: 30
cache_dir: .cache/bike_fetches
cache_ttl: 86400
preserve_sections:
  - references
  - user-reviews
  - modifications-and-customization
log_level: INFO
conflict_threshold: 0.1
batch_update_limit: 50
```

---

## Scheduling

### Manual CLI Usage

```bash
# Update a single bike
python scripts/bike_note_updater/cli.py update-bike vault/notes/bikes/trek/fetch-2.md

# Update all bikes
python scripts/bike_note_updater/cli.py update-all-bikes

# Validate only (no changes)
python scripts/bike_note_updater/cli.py update-all-bikes --validate-only

# Update specific brand
python scripts/bike_note_updater/cli.py update-all-bikes --brand trek

# Dry run (preview changes)
python scripts/bike_note_updater/cli.py update-all-bikes --dry-run

# Check all product URLs
python scripts/bike_note_updater/cli.py check-urls

# Validate all notes against schema
python scripts/bike_note_updater/cli.py validate-all-notes
```

### GitHub Actions Workflow (Future Enhancement)

Create `.github/workflows/update-bike-notes.yml`:

```yaml
name: Update Bike Notes

on:
  schedule:
    - cron: "0 2 * * 0" # Weekly, Sunday at 2 AM UTC
  workflow_dispatch:
    inputs:
      brand:
        description: "Brand to update (leave empty for all)"
      validate_only:
        description: "Validate only, don't update"

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -e .
      - run: python scripts/bike_note_updater/cli.py update-all-bikes --validate-only
      - run: python scripts/bike_note_updater/cli.py update-all-bikes
      - uses: peter-evans/create-pull-request@v5
        if: github.event_name == 'schedule'
        with:
          commit-message: "chore: auto-update bike notes"
          title: "chore: auto-update bike notes from manufacturer pages"
          body: "Automated bike note updates based on current product information"
```

---

## Testing Strategy

### Unit Tests

- **test_data_fetcher.py**: Mock HTTP requests, test extraction logic, handle errors gracefully
- **test_schema_validator.py**: Test validation against all schema rules, edge cases
- **test_note_merger.py**: Test merge logic, conflict detection, preservation of sections
- **test_note_writer.py**: Test YAML formatting, file writing, markdown validation

### Integration Tests

- Test full workflow on sample bike notes
- Verify schema compliance of generated notes
- Test CLI commands end-to-end

### Fixtures

- Sample bike notes (existing and minimal)
- Sample fetched product data (mock HTTP responses)
- Sample frontmatter with various schema compliance levels

---

## Error Handling & Logging

### Graceful Failure Modes

- **URL unreachable**: Log error, skip bike, continue processing queue
- **Extraction failure**: Attempt multiple extraction strategies, report partial success
- **Invalid frontmatter generated**: Don't write file, report validation errors
- **Merge conflict**: Flag, log, preserve existing data, allow manual review

### Logging

```python
import logging

logger = logging.getLogger("bike_note_updater")
logger.info(f"Starting update for {bike_name}")
logger.warning(f"Conflict detected: {conflict_description}")
logger.error(f"Failed to update {note_path}: {error}")
```

### Result Reporting

After batch updates, generate a summary:

```text
=== Bike Note Update Summary ===
Total processed: 42
Successful updates: 38
Conflicts flagged: 3
Errors: 1
Skipped (unreachable URL): 0

Updated bikes:
  - Trek Fetch+ 2 (specs, price)
  - Tern GSD S10 (battery, resellers)
  ...

Conflicts requiring manual review:
  - Benno Boost 10D: Motor power changed from 250W to 350W
  - Gaya Le Cargo: Weight increased significantly
  ...
```

---

## Success Criteria

- ✅ Agent successfully fetches product data from 80%+ of product URLs
- ✅ Merged notes pass schema validation 100% of the time
- ✅ User-added content (markdown body sections) is preserved
- ✅ Conflicts are identified and logged clearly
- ✅ CLI provides both batch and single-bike update modes
- ✅ All tests pass with >85% code coverage
- ✅ Agent reasoning is transparent (logs explain decisions)

---

## Future Enhancements

1. **Multi-vendor data fusion**: Aggregate specs from multiple resellers for accuracy
2. **Price history tracking**: Record price changes over time
3. **Automated PR creation**: Generate pull requests with suggested changes
4. **Image validation**: Verify and update product images
5. **Component linking**: Link to component notes (motors, batteries, etc.)
6. **Review aggregation**: Fetch and summarize reviews from independent sources
7. **Availability alerts**: Notify when bikes go out of stock or receive new pricing
8. **A/B testing**: Test different extraction strategies and grade their accuracy
