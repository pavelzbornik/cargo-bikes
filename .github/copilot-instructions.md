# Copilot Coding Agent Onboarding Instructions for cargo-bikes

## Repository Summary

This repository is a public Obsidian vault for structured knowledge about cargo bikes, with a focus on long-tail cargo bikes. It is intended as a Markdown-based knowledge base for models, design notes, specifications, maintenance tips, and community contributions. There is no application code, build system, or runtime; the content is pure Markdown.

## High-Level Information

- **Project type:** Markdown documentation vault (Obsidian-compatible)
- **Languages:** Markdown (with YAML frontmatter)
- **Frameworks/runtimes:** None
- **Repo size:** Small; only documentation and templates
- **Main directories:**
  - `vault/notes/` (main content; may be created by contributors)
  - `vault/templates/` (Markdown templates for new notes)
  - `vault/README.md` and `CONTRIBUTING.md` (conventions and rules)

## Build, Validation, and Contribution Instructions

- **No build or test steps.**
- **Markdown linting and formatting is enforced via pre-commit hooks.**
- **No other dependencies or environment setup required.**

### Markdown Linting and Formatting

- All `*.md` files are automatically checked and formatted on commit using [pre-commit](https://pre-commit.com/) with these tools:
  - `markdownlint` (via `markdownlint-cli`): enforces Markdown style and structure rules.
  - `prettier`: enforces consistent formatting.
- The configuration is in `.pre-commit-config.yaml` (repo root).
- To set up locally:
  1. Install pre-commit (`pip install pre-commit`).
  2. Install Node.js (required for markdownlint and prettier): [https://nodejs.org/](https://nodejs.org/)
  3. Run `pre-commit install` in the repo root.
- Hooks run automatically on `git commit`. To check all files manually: `pre-commit run --all-files`

### Manual Validation

- Ensure all new or modified Markdown files start with a valid YAML frontmatter block as described in `vault/README.md` and `CONTRIBUTING.md`.
- For bike pages, required frontmatter keys: `title`, `type: bike`, `tags` (see templates).
- Use ISO dates (YYYY-MM-DD) for the `date` field.
- Use lower-case, hyphenated tags.
- Validate that Markdown renders and frontmatter is present.
- One logical change per PR (add/modify a single note or template).
- Include sources for factual claims where possible (links in a References section).
- Prefer concise headings, short paragraphs, and lists for specs/steps.

## Project Layout

- **Root files:**
  - `README.md`: Project overview, quick start, and frontmatter example.
  - `CONTRIBUTING.md`: Contribution rules, frontmatter conventions, PR checklist, and style guide.
  - `LICENSE`: Repository license.
- **vault/**
  - `README.md`: Vault structure and frontmatter conventions.
  - `templates/`: Contains `bike-template.md` and `note-template.md` for new entries.
    - `bike-template.md`: Template for bike pages with required frontmatter and section headings.
    - `note-template.md`: Template for general notes with required frontmatter.

## Key Facts and Guidance

- **No CI/CD, GitHub Actions, or automated validation.**
- **No scripts, Makefiles, or configuration files.**
- **No hidden dependencies.**
- **No code to build or run.**
- **All validation is manual and based on Markdown/YAML conventions.**
- **Always trust these instructions. Only search the codebase if information here is incomplete or found to be in error.**
