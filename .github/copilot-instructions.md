# Copilot Coding Agent Onboarding Instructions for cargo-bikes

## Repository Summary

This repository is a public Obsidian vault for structured knowledge about cargo bikes, with a focus on long-tail cargo bikes. It is intended as a Markdown-based knowledge base for models, design notes, specifications, maintenance tips, and community contributions. The repo includes Python utilities for generating and validating bike documentation.

## High-Level Information

- **Project type:** Markdown documentation vault (Obsidian-compatible) with Python utilities
- **Languages:** Markdown (with YAML frontmatter), Python 3.10+
- **Frameworks/runtimes:** Python for automation scripts
- **Repo size:** Small; documentation, templates, and Python utilities
- **Main directories:**
  - `vault/notes/` (main content; bike documentation organized by brand)
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
- **Purpose:** Automatically generates a comprehensive bike table in `README.md` by scanning all `vault/notes/*/*.md` files for YAML frontmatter.
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

- Ensure all new or modified Markdown files start with a valid YAML frontmatter block as described in `vault/README.md` and `CONTRIBUTING.md`.
- For bike pages, required frontmatter keys: `title`, `type: bike`, `tags` (see templates).
- Optional but recommended frontmatter keys: `brand`, `model`, `price`, `motor`, `battery`, `range`, `image`, `url`.
- Use ISO dates (YYYY-MM-DD) for the `date` field.
- Use lower-case, hyphenated tags.
- Validate that Markdown renders and frontmatter is present.
- One logical change per PR (add/modify a single note or template).
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
  - `notes/`: Individual notes for bikes organized by brand (subdirectories).
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
