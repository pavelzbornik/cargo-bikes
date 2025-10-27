---
description: "Python coding conventions and guidelines for cargo-bikes utilities"
applyTo: "**/*.py"
---

# Python Coding Conventions

## Python General Guidelines

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`, `Optional[str]`).
- Break down complex functions into smaller, more manageable functions.
- Always prioritize readability and clarity.
- Handle edge cases and write clear exception handling.
- Use consistent naming conventions and follow language-specific best practices.

## Project-Specific Guidelines

### Cargo Bikes Utilities Structure

This project contains utilities for managing cargo bike documentation in a Markdown-based vault:

- **scripts/**: Automated utilities for processing bike documentation
  - `generate_bike_table.py`: Extract YAML frontmatter and generate bike tables
  - `validate_urls.py`: Validate and clean URLs in bike frontmatter
  - `add_bike_table_markers.py`: Add/update table markers in README
  - `generate_brand_indexes.py`: Generate brand index pages
  - `database/`: Database initialization and data hydration utilities
  - `linters/`: Custom Markdown structure validation

- **tests/**: pytest test suite for validating scripts and data processing
- **vault/**: Markdown documentation organized by bike brand and content type

### Working with YAML Frontmatter

All bike documentation uses YAML frontmatter for structured metadata:

- **Extract frontmatter carefully**: Use `yaml.safe_load()` with proper error handling
- **Validate required fields**: Check for mandatory fields (`title`, `type`, `brand`, `model`, `tags`, etc.)
- **Handle nested specs**: Bike specs use nested dictionary structures (motor, battery, drivetrain, etc.)
- **Use schema validation**: Reference `docs/schema/BIKE_SPECS_SCHEMA.md` for required fields

Example:

```python
import re
import yaml

def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from Markdown file content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"[WARN] YAML parse error: {e}")
        return None
```

### File and Path Operations

- **Use pathlib.Path**: Always use `Path` from pathlib for file operations
- **Preserve file encoding**: Set UTF-8 encoding explicitly when needed
- **Handle glob patterns**: Use `.glob()` and `.rglob()` for file discovery
- **Respect vault structure**: Bikes are in `vault/notes/bikes/{brand-name}/`

Example:

```python
from pathlib import Path

vault_path = Path("vault/notes/bikes")
for bike_file in vault_path.rglob("*.md"):
    # Process each bike file
    pass
```

### Data Processing and Validation

- **Validate before modifying**: Always validate bike frontmatter before writing
- **Use sets for tags**: Handle tags consistently (lowercase, hyphenated format)
- **Extract nested values safely**: Check if dictionaries exist before accessing nested keys
- **Format output consistently**: Generate Markdown tables with proper alignment and escaping

Example:

```python
def extract_spec_value(specs: dict | None, keys: list[str], default: str = "") -> str:
    """Extract nested spec value with safe fallback."""
    if not specs or not isinstance(specs, dict):
        return default
    value = specs
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    return str(value) if value else default
```

### Working with URLs

- **Validate URL structure**: Check for proper scheme and netloc before making requests
- **Implement retry logic**: Use exponential backoff for HTTP requests
- **Handle timeouts**: Set reasonable timeouts (typically 5-10 seconds)
- **Update metadata**: Track when URLs were last validated

Example:

```python
from urllib.parse import urlparse
import requests

def is_valid_url(url: str) -> bool:
    """Check if URL is structurally valid."""
    if not url or not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
```

### Database Operations

- **Use SQLAlchemy ORM**: Define models in `scripts/database/schema.py`
- **Handle sessions properly**: Use context managers for session lifecycle
- **Validate data before insertion**: Check schema compliance before writing to database
- **Maintain referential integrity**: Use foreign keys appropriately

### Testing Requirements

- **Test data extraction**: Verify YAML parsing and frontmatter extraction
- **Test validation logic**: Test bike schema validation against sample data
- **Test file operations**: Mock file I/O for isolated unit tests
- **Test data transformation**: Validate table generation and data projection
- **Achieve 80%+ coverage**: Run `pytest --cov=scripts` regularly

## Type Checking with mypy

### mypy Requirements

**Type checking is strictly enforced via mypy with these settings:**

- `disallow_untyped_defs = true`: All functions require complete type annotations
- `disallow_incomplete_defs = true`: Type annotations must be complete (no partial typing)
- `check_untyped_defs = true`: Code without types is still validated
- `warn_return_any = true`: Warns when functions return type `Any`
- `strict_equality = true`: Enforces strict equality checks

**Run mypy locally:**

```bash
uv run mypy scripts/  # Must show: Success: no issues found
```

### Type Annotation Standards

**Required for all functions:**

- Parameter types on every argument
- Return type annotation (including `None` if applicable)
- Use Python 3.10+ syntax: `dict[str, Any]`, `list[str]`, `str | None`

**Example of correct typing:**

```python
from typing import Any
from collections.abc import Callable

def calculate_total(
    items: list[float],
    multiplier: int = 1,
    callback: Callable[[float], None] | None = None
) -> float:
    """Calculate total of items with optional callback.

    Args:
        items: List of numeric values
        multiplier: Multiplier for total (default 1)
        callback: Optional function to call with each item

    Returns:
        Total of items multiplied by multiplier
    """
    total: float = sum(items) * multiplier
    if callback is not None:
        for item in items:
            callback(item)
    return total
```

### Common mypy Errors and Fixes

#### Error: "Function is missing a type annotation"

```python
# ❌ Missing return type
def get_name(user_id: int):
    return "John"

# ✅ With return type
def get_name(user_id: int) -> str:
    return "John"
```

#### Error: "Argument of type X cannot be assigned to parameter of type Y"

```python
# ❌ Type mismatch
def process(value: str) -> None:
    pass

process(123)  # Error: int is not str

# ✅ Correct type
process("123")
```

#### Error: "Incompatible return value type"

```python
# ❌ Returns None sometimes
def get_first(items: list[str]) -> str:
    if items:
        return items[0]
    # Missing return - implicitly returns None

# ✅ Correct return type
def get_first(items: list[str]) -> str | None:
    if items:
        return items[0]
    return None
```

#### Error: "Object is possibly None"

```python
# ❌ Potentially None value not checked
data: dict | None = get_data()
value = data["key"]  # Error: data could be None

# ✅ Check for None first
data: dict | None = get_data()
if data is None:
    return None
value = data["key"]  # Now safe
```

#### Error: "Cannot access attribute for unknown type"

```python
# ❌ Result from library with incomplete types
result = yaml.safe_load(content)  # Type is unknown (Any)
value = result["key"]  # Error: result could be None or wrong type

# ✅ Use # type: ignore comment or type explicitly
result: dict | None = yaml.safe_load(content)  # type: ignore[assignment]
if result is not None:
    value = result.get("key")
```

### Handling Third-Party Library Types

**For libraries with incomplete type stubs:**

1. First, try to find type stubs (packages like `types-*`, `*-stubs`)
2. If unavailable, add `# type: ignore` comments

**Example with yaml library:**

```python
import yaml
from typing import Any

# Load YAML - library has incomplete types
content = open("file.yml").read()
data = yaml.safe_load(content)  # type: ignore[assignment]

# Explicit typing for better clarity
data: dict[str, Any] | None = yaml.safe_load(content)  # type: ignore[assignment]

# Function that uses library
def load_frontmatter(file_path: str) -> dict[str, Any] | None:
    """Load and parse YAML frontmatter."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    return yaml.safe_load(content)  # type: ignore[return-value]
```

## Code Style and Formatting

- Follow **PEP 8** style guide (enforced by Ruff).
- Use **Ruff** for linting and formatting (not flake8/black/isort).
- Maintain proper indentation (4 spaces).
- Place docstrings immediately after `def` or `class` keyword.
- Use blank lines to separate logical sections.
- **Use type annotations on all functions** (enforced by mypy).

## Testing Best Practices

- Use **pytest** for all unit and integration tests
- Test data extraction logic thoroughly (YAML parsing, frontmatter validation)
- Mock file I/O for isolated unit tests
- Test edge cases and error conditions
- Achieve minimum 80% code coverage
- Run tests locally: `uv run pytest`
- Check coverage: `pytest --cov=scripts`

Example test structure:

```python
import pytest
from pathlib import Path

def test_extract_frontmatter_valid():
    """Test frontmatter extraction with valid YAML."""
    content = """---
title: Trek Fetch+
type: bike
brand: trek
tags: [bike, longtail, trek]
---
# Content here"""
    result = extract_frontmatter(content)
    assert result is not None
    assert result["title"] == "Trek Fetch+"
    assert result["type"] == "bike"

def test_extract_frontmatter_invalid():
    """Test frontmatter extraction with invalid YAML."""
    content = """---
title: Test
invalid: [unclosed
---
# Content"""
    result = extract_frontmatter(content)
    assert result is None

def test_validate_bike_frontmatter_missing_fields():
    """Test validation catches missing required fields."""
    frontmatter = {"title": "Test"}
    assert validate_bike_frontmatter(frontmatter) is False
```

## Type Hints and Complete Type Annotations

**All functions MUST have complete type annotations.** This is enforced by mypy with strict settings.

### Type Annotation Requirements

- **Function parameters**: Each parameter must have a type hint
- **Return values**: All functions must have return type annotations
- **Generic types**: Use modern syntax (Python 3.10+):
  - `dict[str, Any]` instead of `Dict[str, Any]`
  - `list[str]` instead of `List[str]`
  - `str | None` instead of `Optional[str]`
  - `set[str]` instead of `Set[str]`

### mypy Type Checking

The project uses mypy with strict settings to enforce type safety:

- Configured in `pyproject.toml` with `disallow_untyped_defs = true`
- Integrated into pre-commit hooks (runs on all Python files)
- Validated in CI pipeline on every PR

**Run mypy locally:**

```bash
uv run mypy scripts/  # Must show: Success: no issues found
```

### Type Annotations for Common Patterns

**Function with parameters and return type:**

```python
from typing import Any

def process_data(items: list[str], timeout: int = 30) -> dict[str, Any]:
    """Process items and return results.

    Args:
        items: List of items to process
        timeout: Timeout in seconds (default 30)

    Returns:
        Dictionary containing results
    """
    result: dict[str, Any] = {"status": "success", "count": len(items)}
    return result
```

**Optional and union types:**

```python
from typing import Any

def fetch_data(
    query: str,
    limit: int | None = None,
    format: str = "json"
) -> dict[str, Any] | None:
    """Fetch data with optional limit.

    Args:
        query: Search query
        limit: Optional result limit
        format: Output format (default: json)

    Returns:
        Results dictionary or None if not found
    """
    if not query:
        return None
    return {"query": query, "results": []}
```

**Callable types:**

```python
from collections.abc import Callable
from typing import Any

def execute_task(
    processor: Callable[[str], Any],
    data: str
) -> Any:
    """Execute a processing task.

    Args:
        processor: Callable that processes the data
        data: Input data to process

    Returns:
        Processing result
    """
    return processor(data)
```

**Generator/Iterator types:**

```python
from collections.abc import Generator
from pathlib import Path

def discover_bike_files(vault_path: Path) -> Generator[Path, None, None]:
    """Discover all bike markdown files in vault.

    Yields:
        Path objects for each bike markdown file
    """
    for bike_file in vault_path.rglob("*.md"):
        if bike_file.is_file():
            yield bike_file
```
