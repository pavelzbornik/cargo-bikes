# Copilot Coding Agent Onboarding Instructions for cargo-bikes

## Repository Summary

This repository is a public Markdown vault for structured knowledge about cargo bikes, with a focus on long-tail cargo bikes. It is intended as a Markdown-based knowledge base for models, design notes, specifications, maintenance tips, and community contributions. The repo includes Python utilities for generating and validating bike documentation.

## High-Level Information

- **Project type:** Markdown documentation vault with Python utilities
- **Languages:** Markdown (with YAML frontmatter), Python 3.10+
- **Frameworks/runtimes:** Python for automation scripts
- **Repo size:** Small; documentation, templates, and Python utilities
- **Main directories:**
  - `vault/notes/bikes/` (main content; bike documentation organized by brand)
  - `vault/templates/` (Markdown templates for new notes)
  - `scripts/` (Python utilities for table generation and validation)
  - `tests/` (pytest test suite for Python scripts)
  - `docs/` (documentation for Python utilities)
  - `vault/README.md` and `CONTRIBUTING.md` (conventions and rules)
  - `pyproject.toml` (Python dependencies and tool configuration)

## Build, Validation, and Contribution Instructions

### Python Environment Setup

- Python 3.10+ is required for running scripts and tests.
- Dependencies are managed via `pyproject.toml` and installed using [uv](https://github.com/astral-sh/uv).
- To set up:
  1. Install uv: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
  2. Create and sync the virtual environment: `uv sync`
  3. Activate the venv: `.venv\Scripts\Activate.ps1` (Windows PowerShell) or `source .venv/bin/activate` (Linux/Mac)

### Python Scripts

#### Bike Table Generator

- **Script:** `scripts/generate_bike_table.py`
- **Purpose:** Automatically generates a comprehensive bike table in `README.md` by scanning all `vault/notes/bikes/*/*.md` files for YAML frontmatter.
- **Usage:** `python scripts/generate_bike_table.py`
- **Details:** See `docs/GENERATE_BIKE_TABLE.md` for complete documentation.
- **Key features:**
  - Extracts YAML frontmatter from all bike notes
  - Validates required fields (`title`, `type: bike`, `tags`)
  - Generates a sorted Markdown table with specs and images
  - Updates README.md between `<!-- BIKES_TABLE_START -->` and `<!-- BIKES_TABLE_END -->` markers

#### Testing

- **Framework:** pytest
- **Location:** `tests/`
- **Run tests:** `pytest` or `uv run pytest`
- **Coverage:** `pytest --cov=scripts`
- **Tests validate:**
  - YAML frontmatter extraction
  - Bike frontmatter validation
  - Table generation logic
  - README.md update functionality

### Bike Specifications Schema

- **Location:** `docs/schema/BIKE_SPECS_SCHEMA.md`
- **Purpose:** Defines the standardized YAML frontmatter structure for all bike notes to ensure consistent, machine-readable metadata.
- **Applies to:** All bike notes in `vault/notes/bikes/`
- **Key sections:**
  - **Top-level fields:** `title`, `type`, `brand`, `model`, `tags`, `date`, `url`, `image`, `resellers`
  - **`specs` object:** Nested structure containing technical details:
    - Motor, battery, drivetrain, brakes, wheels, suspension, lights, security, features
    - Load capacity, weight, dimensions, frame details, range estimates, pricing
  - **Required vs optional:** See schema doc for full details
- **Example:** See BIKE_SPECS_SCHEMA.md for a complete Trek Fetch+ 2 example
- **When creating bike notes:** Always reference this schema for proper field structure and data types

### Markdown Linting and Formatting

- All `*.md` files are automatically checked and formatted on commit using [pre-commit](https://pre-commit.com/) with these tools:
  - `markdownlint` (via `markdownlint-cli`): enforces Markdown style and structure rules.
  - `prettier`: enforces consistent formatting.
- The configuration is in `.pre-commit-config.yaml` (repo root).
- To set up locally:
  1. Activate the Python venv created and maintained by uv.
  2. Sync Python dependencies using uv: `uv sync`.
  3. Install Node.js (required for markdownlint and prettier): [nodejs.org](https://nodejs.org/)
  4. Run `pre-commit install` in the repo root. Alternatively, run `uv pre-commit install` to ensure the venv is activated.
- Hooks run automatically on `git commit`. To check all files manually: `pre-commit run --all-files`

### Manual Validation

- Ensure all new or modified Markdown files start with a valid YAML frontmatter block as described in `vault/README.md`, `CONTRIBUTING.md`, and the **BIKE_SPECS_SCHEMA** (`docs/schema/BIKE_SPECS_SCHEMA.md`).
- For bike pages, place files in `vault/notes/bikes/brand-name/` (lowercase, hyphenated) and include all required frontmatter keys:
  - **Top-level:** `title`, `type: bike`, `brand`, `model`, `date` (ISO: YYYY-MM-DD), `tags`, `url`, `image`
  - **Nested structure:** `specs` object with technical details (see schema)
  - **Recommended:** `resellers` array with pricing and availability
- Use **lowercase, hyphenated** tags in the format: `[bike, bike-type, brand-name, motor-brand]`
  - Examples: `[bike, longtail, trek, bosch]` or `[bike, box, cargo-bikes, shimano]`
- **Tag requirements:**
  - Always include: `bike`
  - Always include: bike category/type (e.g., `longtail`, `box`, `trike`, `midtail`)
  - Always include: brand name (lowercase, hyphenated)
  - Optionally include: motor brand, drivetrain type, or other relevant features
- Validate that Markdown renders and frontmatter YAML syntax is correct.
- One logical change per PR (add/modify a single bike note or template).
- Include sources for factual claims where possible (links in a References section).
- Prefer concise headings, short paragraphs, and lists for specs/steps.
- After adding or modifying bike notes, run `python scripts/generate_bike_table.py` to update the bike table in README.md.

## Project Layout

- **Root files:**
  - `README.md`: Project overview, quick start, and frontmatter example.
  - `CONTRIBUTING.md`: Contribution rules, frontmatter conventions, PR checklist, and style guide.
  - `LICENSE`: Repository license.
  - `pyproject.toml`: Python dependencies and tool configuration (pytest, ruff, pre-commit, etc.).
  - `.pre-commit-config.yaml`: Pre-commit hooks configuration for linting and formatting.
- **vault/**
  - `README.md`: Vault structure and frontmatter conventions.
  - `notes/`: Individual notes organized by type:
    - `bikes/`: Bike documentation organized by brand (subdirectories).
    - Other content folders (future): Components, accessories, guides, etc.
  - `templates/`: Contains `bike-template.md` and `note-template.md` for new entries.
    - `bike-template.md`: Template for bike pages with required frontmatter and section headings.
    - `note-template.md`: Template for general notes with required frontmatter.
- **scripts/**
  - `generate_bike_table.py`: Python script to generate the bike table in README.md from frontmatter.
  - `__init__.py`: Makes scripts a Python package.
- **tests/**
  - `test_generate_bike_table.py`: pytest test suite for the table generator.
  - `conftest.py`: pytest configuration and fixtures.
- **docs/**
  - `GENERATE_BIKE_TABLE.md`: Comprehensive documentation for the bike table generator script.

## Key Facts and Guidance

- **Python utilities automate bike table generation from YAML frontmatter.**
- **Python 3.10+ environment managed via uv and pyproject.toml.**
- **Markdown linting and formatting enforced via pre-commit hooks.**
- **Tests validate Python script functionality (pytest).**
- **All bike documentation follows structured frontmatter conventions.**
- **After modifying bike notes, regenerate the table with `python scripts/generate_bike_table.py`.**
- **Always trust these instructions. Only search the codebase if information here is incomplete or found to be in error.**
