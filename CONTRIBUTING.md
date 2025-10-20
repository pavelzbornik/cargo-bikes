# Contributing to the cargo-bikes vault

Thanks for wanting to contribute. Please follow these simple rules so the vault stays consistent and useful.

## Development Environment Setup

### Option 1: Using DevContainer (Recommended)

If you're using **VS Code**, the easiest way to get started is with the DevContainer:

1. Install [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
3. Open this repository in VS Code
4. Click the green remote indicator in the bottom-left and select **"Reopen in Container"**
5. VS Code will automatically set up the full development environment with Python 3.13, uv, pre-commit, Node.js, and Taskfile

The DevContainer includes all tools pre-configured:

- **Python 3.13** via uv for fast, reliable package management
- **Pre-commit hooks** for linting and formatting
- **Node.js 24** for markdown linting
- **Taskfile** for task automation
- **GitHub CLI** for repository operations
- Recommended VS Code extensions for Python, Markdown, and GitHub workflows

### Option 2: Local Setup

If you prefer local development without Docker:

1. **Install Python 3.10+** from [python.org](https://python.org)
2. **Install uv** from [github.com/astral-sh/uv](https://github.com/astral-sh/uv)
3. **Create and sync the virtual environment:**

   ```powershell
   # Windows PowerShell
   uv sync
   .venv\Scripts\Activate.ps1
   ```

   ```bash
   # Linux/Mac
   uv sync
   source .venv/bin/activate
   ```

4. **Install Node.js** from [nodejs.org](https://nodejs.org/) (required for markdown linting)
5. **Set up pre-commit hooks:**

   ```bash
   uv run pre-commit install
   ```

## Python Development Tasks

Use **Taskfile** to automate common development tasks:

```bash
task python:deps:install    # Install Python dependencies
task python:test            # Run pytest tests
task python:test:coverage   # Run tests with coverage report
task python:lint            # Lint Python files with ruff
task python:format          # Format Python files with ruff
task precommit:run          # Run all pre-commit hooks
task precommit:run:staged   # Run pre-commit on staged files only
```

**Or run tasks directly:**

```bash
uv run pytest tests/                           # Run tests
uv run pytest --cov=scripts tests/             # Run with coverage
uv run ruff check scripts/ tests/               # Lint
uv run ruff format scripts/ tests/              # Format
uv run pre-commit run --all-files               # Run all pre-commit hooks
```

## Frontmatter Rules

Every note must start with a YAML frontmatter block. For bike pages, follow the **BIKE_SPECS_SCHEMA** (`docs/schema/BIKE_SPECS_SCHEMA.md`).

### Required Fields (All Bikes)

- `title` — Full, human-readable bike name
- `type` — Must be `bike`
- `tags` — List of lowercase, hyphenated tags (e.g., `[bike, longtail, electric, tern, bosch]`)
- `date` — ISO format (YYYY-MM-DD)
- `brand` — Manufacturer name
- `model` — Model name
- `url` — Official product page URL
- `image` — Direct URL to product image
- `specs` — Nested structure with technical specifications (see schema)

### Recommended Fields

- `resellers` — Array of vendor listings with price, currency, region, availability
- See `docs/schema/BIKE_SPECS_SCHEMA.md` for complete field definitions and examples

### Tag Format

- Use **lowercase, hyphenated** tags: `long-tail`, `mid-drive`, `bosch-performance-line`, etc.
- Always include: `bike`, and bike type (`longtail`, `box`, `trike`, etc.)
- Always include: brand name in lowercase hyphenated format

### Date Format

- Use ISO 8601: `YYYY-MM-DD` (e.g., `2025-10-20`)

## File Organization

Bike notes go in: `vault/notes/bikes/brand-name/bike-model.md`

Examples:

- `vault/notes/bikes/tern/gsd-p10.md`
- `vault/notes/bikes/cargo-bikes/longtail-lite.md`

Use lowercase, hyphenated names for both brand and model folders.

## PR Checklist

1. **One logical change per PR** — Add or modify a single bike note or template, not multiple bikes.
2. **Follow the template** — Use `vault/templates/bike-template.md` as your starting point.
3. **Validate frontmatter** — Ensure YAML syntax is correct (no missing colons, brackets, quotes).
4. **Schema compliance** — Check that your note matches `docs/schema/BIKE_SPECS_SCHEMA.md` structure.
5. **Include sources** — Add links to official pages, reviews, or forums in the References section.
6. **Test markdown rendering** — Verify the note renders correctly in Obsidian or Markdown viewer.
7. **Update bike table** — After finalizing, run `python scripts/generate_bike_table.py` to update the main README.

## Writing Style

- Use **concise headings** and short paragraphs
- Prefer **lists** over prose for specs and features
- Use **tables** for accessory pricing and comparisons
- Keep language neutral and factual
- Provide context for specifications (e.g., "eco mode, no load" for range estimates)

## Schema Reference

For detailed field definitions, data types, and validation rules, see:
**`docs/schema/BIKE_SPECS_SCHEMA.md`**

Key concepts:

- **`specs.category`** — Bike type: `longtail`, `box`, `trike`, etc.
- **`specs.features`** — Short, hyphenated tags for searchability
- **`specs.motor`** — Motor details (make, model, type, power, torque, throttle)
- **`specs.battery`** — Battery specs (capacity, removable, charging time)
- **`specs.load_capacity`** — Weight limits and passenger config
- **`specs.range`** — Estimated range with context notes

## If You're Unsure

Open an issue first to discuss before starting work. Ask about:

- Bike classification or category
- Missing specification data
- Sourcing or permission questions
