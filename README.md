# cargo-bikes — Public Obsidian Vault for Cargo Bikes

This repository is a public Obsidian-style vault that stores structured information about cargo bikes, with a focus on long-tail (longtail) cargo bikes. Use this vault as a knowledge base for models, design notes, specifications, maintenance tips, and community contributions.

## Contents

- `/.obsidian/` — notes about recommended Obsidian setup for this vault.
- `/vault/notes/` — the main notes; each bike, article or topic is a separate Markdown file.
- `/vault/templates/` — templates for adding new bike entries, specs, and general notes.
- `CONTRIBUTING.md` — contribution rules, metadata/frontmatter conventions and PR checklist.

## Why this repo

Long-tail cargo bikes are a popular and practical platform for carrying kids, cargo, and commuting at scale. This vault is intended to collect manufacturer specs, rider notes, mod lists, maintenance tips, fit guidelines, and comparative analyses in a discoverable, linked-note format.

## Quick start

1. Clone the repo and open it as a vault in Obsidian or any Markdown editor.
2. Add new notes under `vault/notes/` using the templates in `vault/templates/`.
3. Follow the frontmatter conventions in `vault/README.md` and `CONTRIBUTING.md`.

**Frontmatter example:**

```yaml
---
title: "Yuba Mundo (example)"
type: bike
brand: "Yuba"
model: "Mundo"
tags: ["long-tail", "family", "electric-compat"]
date: 2025-10-16
---
```

## Linting and formatting Markdown (pre-commit)

To ensure all Markdown files are linted and formatted before commit, this repo uses [pre-commit](https://pre-commit.com/) with `markdownlint` and `prettier` hooks.

**Setup:**

1. Install pre-commit (requires Python):

   ```sh
   pip install pre-commit
   ```

1. Install Node.js (required for markdownlint and prettier):

[https://nodejs.org/](https://nodejs.org/)

1. Install the hooks:

```sh
pre-commit install
```

**Usage:**

- Hooks will run automatically on `git commit`.
- To manually check all files:

```sh
pre-commit run --all-files
```

**Configuration:**

- See `.pre-commit-config.yaml` for details.

## Notes and contributions

Please read `CONTRIBUTING.md` before opening issues or pull requests.

## License

This repository is public under the license in `LICENSE`.

## Contact

If you have questions or want to collaborate, open an issue or submit a PR.
