# Bike Note Updater - Developer Guide

This guide is for developers who want to understand, modify, or extend the bike note updater agent.

## Architecture Overview

The bike note updater follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                          CLI Layer                          │
│                      (cli.py - Typer)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      Agent Layer                            │
│                  (agent.py - BikeNoteUpdater)               │
└──┬─────────┬──────────┬──────────┬───────────┬──────────────┘
   │         │          │          │           │
   │         │          │          │           │
┌──▼─────┐ ┌▼──────┐ ┌▼───────┐ ┌▼─────┐   ┌▼──────┐
│ Data   │ │Schema │ │  Note  │ │ Note │   │ Utils │
│Fetcher │ │Valid  │ │ Merger │ │Writer│   │       │
│        │ │ator   │ │        │ │      │   │       │
└────────┘ └───────┘ └────────┘ └──────┘   └───────┘
```

## Module Reference

### models.py

Defines Pydantic models for type-safe data structures:

- **BikeFrontmatter**: Top-level frontmatter structure
- **BikeSpecs**: Nested specs object with motor, battery, etc.
- **ValidationReport**: Validation results
- **MergeResult**: Merge operation results
- **UpdateResult**: Update operation results
- **Conflict**: Detected conflicts between old/new data

#### Key Models

```python
class BikeFrontmatter(BaseModel):
    title: str
    type: str = "bike"
    tags: list[str]
    date: str  # ISO 8601
    specs: BikeSpecs | None = None
    # ... other fields

class BikeSpecs(BaseModel):
    category: str | None = None
    motor: Motor | None = None
    battery: Battery | None = None
    # ... other specs
```

### utils.py

Utility functions for common operations:

- `validate_url()`: Check if URL is reachable
- `normalize_tag()`: Convert tags to lowercase-hyphenated format
- `validate_iso_date()`: Validate ISO 8601 date format
- `find_bike_notes()`: Find all bike notes in vault
- `parse_frontmatter()`: Extract YAML frontmatter from markdown
- `format_yaml_frontmatter()`: Format dict as YAML
- `calculate_percentage_change()`: Calculate change between values
- `is_significant_change()`: Check if change exceeds threshold

### schema_validator.py

Validates bike notes against BIKE_SPECS_SCHEMA:

```python
class SchemaValidator:
    def validate_frontmatter(self, frontmatter: dict) -> ValidationReport:
        """Main validation method"""
        
    def _validate_specs_structure(self, specs: dict) -> list[ValidationIssue]:
        """Validate nested specs"""
        
    def check_tag_format(self, tags: list[str]) -> bool:
        """Validate tag format"""
```

#### Validation Rules

1. **Required fields**: title, type, tags, date
2. **Type check**: type must be "bike"
3. **Date format**: Must be ISO 8601 (YYYY-MM-DD)
4. **Tags**: Must include "bike", should be lowercase-hyphenated
5. **Specs structure**: Motor/battery/weight should have required fields

### data_fetcher.py

Fetches product data from manufacturer websites:

```python
class DataFetcher:
    async def fetch_from_url(self, url: str) -> dict:
        """Fetch and extract bike data from URL"""
        
    def _extract_json_ld(self, html: str) -> dict | None:
        """Extract JSON-LD structured data"""
        
    def _extract_from_html(self, html: str) -> dict:
        """Fallback HTML parsing"""
```

#### Extraction Strategy

1. **Primary**: JSON-LD structured data (Schema.org Product)
2. **Secondary**: Microdata parsing
3. **Fallback**: BeautifulSoup HTML parsing

### note_merger.py

Intelligently merges fetched data with existing notes:

```python
class NoteMerger:
    def merge(
        self,
        existing_frontmatter: dict,
        new_data: dict,
        preserve_sections: list[str] | None = None
    ) -> MergeResult:
        """Main merge logic"""
        
    def _merge_specs(self, existing_specs: dict, new_specs: dict):
        """Merge specs objects"""
        
    def _detect_value_conflict(self, field: str, old_value, new_value):
        """Detect conflicts"""
```

#### Merge Strategy

- **Update**: specs, resellers, image, url
- **Preserve**: date, tags, markdown body
- **Conflict detection**: Changes > threshold (default 10%)

#### Conflict Types

- **Minor**: < 10% change, auto-merge with note
- **Major**: > 10% change or component model change
- **Unresolvable**: Require manual intervention (future)

### note_writer.py

Writes updated notes to disk:

```python
class NoteWriter:
    def write_note(
        self,
        file_path: Path,
        frontmatter: dict,
        body: str,
        validate: bool | None = None
    ) -> WriteResult:
        """Write note with validation"""
        
    def read_note(self, file_path: Path) -> tuple[dict | None, str]:
        """Read existing note"""
```

### agent.py

Main orchestration layer:

```python
class BikeNoteUpdater:
    async def update_bike(
        self,
        note_path: Path,
        fetch_url: bool = True,
        dry_run: bool = False
    ) -> UpdateResult:
        """Complete update workflow"""
        
    def validate_note(self, note_path: Path) -> UpdateResult:
        """Validation-only mode"""
```

#### Update Workflow

1. Read existing note
2. Validate existing frontmatter
3. Fetch new data from URL (if requested)
4. Merge new data with existing
5. Validate merged result
6. Write to disk (if not dry-run)
7. Return results with conflicts/errors

### cli.py

Command-line interface using Typer:

- `update-bike`: Update single note
- `update-all-bikes`: Batch update
- `validate-all-notes`: Validation only
- `check-urls`: URL validity check

## Testing

### Test Structure

```
tests/test_bike_note_updater/
├── test_models.py          # Pydantic model tests
├── test_utils.py           # Utility function tests
├── test_schema_validator.py # Validation logic tests
├── test_note_merger.py     # Merge logic tests
├── test_note_writer.py     # File I/O tests
└── conftest.py             # Shared fixtures (if needed)
```

### Running Tests

```bash
# Run all tests
PYTHONPATH=. pytest tests/test_bike_note_updater/

# Run with coverage
PYTHONPATH=. pytest tests/test_bike_note_updater/ --cov=scripts/bike_note_updater

# Run specific test file
PYTHONPATH=. pytest tests/test_bike_note_updater/test_models.py -v
```

### Test Coverage

Current coverage (core modules):
- models.py: 100%
- schema_validator.py: 100%
- note_merger.py: 94%
- note_writer.py: 87%
- utils.py: 91%

## Extending the Updater

### Adding New Validation Rules

Edit `schema_validator.py`:

```python
def _validate_specs_structure(self, specs: dict) -> list[ValidationIssue]:
    issues = []
    
    # Add your new validation
    if specs.get("new_field"):
        if not self._validate_new_field(specs["new_field"]):
            issues.append(ValidationIssue(
                field="specs.new_field",
                issue_type="invalid_format",
                message="New field validation failed",
                suggestion="Fix the new field"
            ))
    
    return issues
```

### Adding New Data Extractors

Edit `data_fetcher.py`:

```python
def _extract_from_html(self, html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    
    # Add site-specific extraction
    if "manufacturer-site.com" in html:
        return self._extract_from_manufacturer_site(soup)
    
    # Fallback to generic extraction
    return self._generic_extraction(soup)
```

### Adding New CLI Commands

Edit `cli.py`:

```python
@app.command()
def my_new_command(
    option1: str = typer.Option(..., help="Help text"),
):
    """Command description."""
    # Implementation
    console.print("[cyan]Running my new command[/cyan]")
```

## Configuration

Configuration is handled via:

1. **Constructor parameters** (recommended):
   ```python
   updater = BikeNoteUpdater(
       fetch_timeout=30,
       conflict_threshold=0.1,
       validate=True
   )
   ```

2. **Environment variables** (future):
   - BIKE_UPDATER_FETCH_TIMEOUT
   - BIKE_UPDATER_CONFLICT_THRESHOLD

## Logging

The agent uses Python's standard logging module:

```python
import logging

logger = logging.getLogger("bike_note_updater")
logger.setLevel(logging.INFO)
```

Log levels:
- **INFO**: Normal operation, successful updates
- **WARNING**: Conflicts, validation warnings
- **ERROR**: Failed fetches, write errors

## Performance Considerations

### Batch Updates

For large vaults:

1. Process one brand at a time
2. Implement rate limiting for fetches (future)
3. Use caching to avoid repeated fetches
4. Consider parallel processing (future)

### Caching

Future enhancement - cache fetched data:

```python
# Cache structure (future)
.cache/bike_fetches/
├── trek_fetch-2_2024-01-15.json
└── tern_gsd-s10_2024-01-15.json
```

## Error Handling

### Graceful Degradation

1. **Fetch failure**: Skip bike, continue processing
2. **Validation failure**: Report errors, don't write
3. **Merge conflict**: Flag for review, allow update
4. **Write failure**: Report error, don't corrupt data

### Error Types

```python
try:
    result = await updater.update_bike(note_path)
except httpx.HTTPError:
    # Network/fetch errors
    pass
except yaml.YAMLError:
    # YAML parsing errors
    pass
except Exception as e:
    # Unexpected errors
    logger.exception("Unexpected error")
```

## Future Enhancements

### PydanticAI Integration

The specification calls for PydanticAI for LLM-powered reasoning:

```python
from pydantic_ai import Agent

agent = Agent(
    model="claude-3-5-sonnet",
    system_prompt="You are a bike data extraction expert..."
)

@agent.tool
def extract_specs(html: str) -> dict:
    """LLM-powered spec extraction"""
    pass
```

### GitHub Actions Integration

Scheduled updates via GitHub Actions:

```yaml
# .github/workflows/update-bike-notes.yml
name: Update Bike Notes

on:
  schedule:
    - cron: "0 2 * * 0"  # Weekly
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Update notes
        run: python -m scripts.bike_note_updater.cli update-all-bikes
```

### Caching System

Implement disk-based caching:

```python
class DataFetcher:
    def __init__(self, cache_dir=".cache/bike_fetches", cache_ttl=86400):
        self.cache_dir = Path(cache_dir)
        self.cache_ttl = cache_ttl
```

## Contributing

1. Write tests for new features
2. Ensure test coverage > 85%
3. Follow existing code style (ruff)
4. Update documentation
5. Run linting before committing:
   ```bash
   ruff check scripts/bike_note_updater/
   ```

## License

See LICENSE file in repository root.
