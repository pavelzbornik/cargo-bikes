# MkDocs Plugins Quick Start

## What Was Added

Your cargo-bikes documentation now has 8 powerful plugins from the [MkDocs Catalog](https://github.com/mkdocs/catalog) plus Material's built-in tagging support.

## Plugin Usage Guide

### 1. Git Revision Date & Git Authors

**Auto-enabled** - Shows on every page:

- Last update date (bottom of page)
- Authors who contributed to the page

No configuration needed. They work automatically.

### 2. GLightbox (Image Zoom)

**How to use**: Just add images normally to your markdown. They'll automatically have zoom functionality.

```markdown
![Bike Name](path/to/image.jpg)
```

Visitors can click images to zoom in/out.

### 3. Table Reader (CSV Integration)

**How to use**: Reference CSV files directly in markdown:

```markdown
--8<-- "path/to/bikes.csv"
```

Perfect for bike specifications tables. Example:

```csv
brand,model,price,battery,range
Trek,FX3,800,400Wh,25km
Cube,Longtail,1200,625Wh,35km
```

### 4. Redirects (URL Management)

**How to use**: Create `redirects.yml` in docs root:

```yaml
redirects:
  old/page.md: new/page.md
  outdated/bike.md: bikes/brand/model.md
```

When URLs change, old links still work.

### 5. Section Index (Clickable Categories)

**How to use**: Navigation sections are now clickable if you add an index page.

Example navigation structure:

```text
Trek/
  index.md      (overview page)
  fx-3/
    model.md
  domane/
    model.md
```

Clicking "Trek" shows `index.md` instead of just expanding the menu.

### 6. Tags (Content Organization) - Material Built-in

**How to use**: Add tags to your frontmatter:

```yaml
---
title: Trek FX3
tags:
  - hybrid
  - electric
  - urban
  - commuting
---
```

Tags automatically appear and visitors can browse by tags. Recommended tags:

- **Type**: longtail, midtail, cargo-box, bucket, convertible
- **Motor**: bafang, bosch, yamaha, brose, shimano
- **Price**: budget, mid-range, premium
- **Use**: commuting, family, delivery

### 7. llmstxt (LLM-Friendly Documentation)

**How to use**: This plugin automatically generates `/llms.txt` for LLM consumption.

**Features**:

- Generates at: `https://pavelzbornik.github.io/cargo-bikes/llms.txt`
- Hierarchical index of all documentation
- Machine-readable format for AI tools
- Auto-configured for cargo-bikes vault

**Optional**: Generate expanded version with full page content:

```yaml
- llmstxt:
    full_output: llms-full.txt
```

No manual action needed - works automatically!

## Build & Test

```bash
# Test locally
uv run mkdocs serve

# Build for production
uv run mkdocs build
```

## Documentation Structure

```text
cargo-bikes/
├── vault/notes/        ← Source for building pages (unchanged)
├── docs/               ← MkDocs documentation
│   ├── MKDOCS_PLUGINS_APPLIED.md
│   ├── PLUGINS_QUICK_START.md
│   ├── GENERATE_BIKE_TABLE.md
│   └── VALIDATE_URLS.md
├── scripts/            ← Python utilities
├── tests/              ← Test suite
└── mkdocs.yml          ← MkDocs configuration
```

## Plugin List

Active plugins:

1. **search** - Built-in search functionality
2. **obsidian-bridge** - Obsidian vault compatibility
3. **git-revision-date** - Last updated timestamps
4. **git-authors** - Author attribution
5. **glightbox** - Image zoom/lightbox
6. **table-reader** - CSV table integration
7. **redirects** - URL redirect management
8. **section-index** - Clickable section headers
9. **llmstxt** - LLM-friendly documentation export

Plus Material's built-in tag support!

## Next Steps

1. Add tags to bike specification files in `vault/notes/bikes/`
2. Create brand index pages for section-index plugin
3. Set up CSV tables for bike specifications
4. Configure redirects if you restructure URLs
5. Test image zoom with glightbox

## More Information

See `MKDOCS_PLUGINS_APPLIED.md` for detailed documentation on each plugin.
