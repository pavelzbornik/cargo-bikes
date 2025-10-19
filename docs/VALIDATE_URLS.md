# URL Validator Script

## Overview

`scripts/validate_urls.py` is a Python utility that validates URL links in bike note frontmatter fields (`url` and `image`). It checks if URLs are reachable via HTTP requests, removes invalid URLs from the frontmatter, and logs all changes in a JSON changelog.

## Requirements

- Python 3.10+
- PyYAML (installed via `pyproject.toml`)
- requests (installed via `pyproject.toml`)

## Usage

### Basic Run

From the repo root:

```bash
python scripts/validate_urls.py
```

The script will:

- Scan all subdirectories in `vault/notes/` for `*.md` files
- Extract YAML frontmatter from each file
- Check for `url` and `image` fields
- Validate each URL via HTTP request (HEAD request with redirects allowed)
- Remove invalid URLs and update the frontmatter
- Save detailed changelog to `VALIDATE_URLS_CHANGELOG.json`

### Options

#### Dry-run Mode

Preview changes without modifying files:

```bash
python scripts/validate_urls.py --dry-run
```

In dry-run mode:

- Files are not modified
- Changelog is not saved
- Changes are only displayed in console output

#### Skip HTTP Check

Only validate URL structure without making HTTP requests:

```bash
python scripts/validate_urls.py --skip-check
```

Useful for:

- Quick validation of URL format only
- Testing without network access
- Avoiding timeouts or external dependencies

### Combined Options

```bash
python scripts/validate_urls.py --dry-run --skip-check
```

## Output

### Console Output

The script prints real-time progress for each file:

```text
[1/118] [OK] benno/boost-10d-evo-5.md: All URLs valid
[2/118] [REMOVED] douze-cycles/lt1.md: Removed 2 URL(s)
    - https://invalid-url.example.com/bike1
    - https://dead-link.example.com/image.jpg
    [SAVED]
[3/118] [OK] tern/gcn-s8.md: No URLs found
...
```

Status codes:

| Code        | Meaning                             |
| ----------- | ----------------------------------- |
| `[OK]`      | File processed successfully         |
| `[REMOVED]` | Invalid URLs were found and removed |
| `[SKIP]`    | File skipped (no frontmatter, etc.) |
| `[ERR]`     | Error processing file               |

### Changelog File

Creates `VALIDATE_URLS_CHANGELOG.json` with details:

```json
{
  "generated": "2025-10-19T19:52:38.123456+00:00",
  "total_entries": 118,
  "entries": [
    {
      "timestamp": "2025-10-19T19:52:38.654321+00:00",
      "file": "benno/boost-10d-evo-5.md",
      "status": "OK_VALID_URLS",
      "removed_urls": []
    },
    {
      "timestamp": "2025-10-19T19:52:39.234567+00:00",
      "file": "douze-cycles/lt1.md",
      "status": "URLS_REMOVED",
      "removed_urls": [
        "https://invalid-url.example.com/bike1",
        "https://dead-link.example.com/image.jpg"
      ]
    }
  ]
}
```

### Summary Statistics

After validation completes, displays:

```text
======================================================================
SUMMARY
======================================================================
Total files processed: 118
Total entries in changelog: 118

Status breakdown:
  ERROR_FileNotFoundError: 1
  OK_NO_URLS: 45
  OK_VALID_URLS: 62
  SKIPPED_NO_FM: 5
  URLS_REMOVED: 5

Total URLs removed: 12
======================================================================
```

## URL Validation Logic

### Structural Validation

URLs are first checked for correct structure:

- Must have a scheme (`http://` or `https://`)
- Must have a netloc (domain name)

### HTTP Reachability Check

If structural validation passes, the script:

1. Makes an HTTP HEAD request to the URL
2. Follows redirects (up to 30 by default, configured by requests)
3. Accepts status codes in ranges:
   - **2xx (200-299)**: OK
   - **3xx (300-399)**: Redirects (acceptable)
4. Rejects status codes:
   - **4xx (400-499)**: Not Found, Gone, etc.
   - **5xx (500-599)**: Server errors

### Retry Logic

Failed requests are retried up to 2 times (configurable):

- **Timeout**: Retries on timeout, fails after max retries
- **Connection Error**: Returns false immediately
- **HTTP Errors**: Returns false based on status code

### Request Headers

Requests include a User-Agent to avoid being blocked by strict servers:

```text
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

### Timeout

Default timeout is 5 seconds per request.

## Supported Frontmatter Fields

The script validates these URL fields:

- `url`: Product page or reference URL
- `image`: Image URL (for bike photos)

Both fields are optional in bike notes, but if present, they must be valid URLs.

### Example Frontmatter

**Before validation (with invalid URLs):**

```yaml
---
title: "Example Bike"
type: bike
tags: [bike, longtail]
url: "https://www.example.com/bike"
image: "https://broken-image.example.com/photo.jpg"
---
```

**After validation (if image URL is broken):**

```yaml
---
title: "Example Bike"
type: bike
tags: [bike, longtail]
url: "https://www.example.com/bike"
---
```

## Performance

- **Speed**: ~2-5 seconds to validate 118 bikes (depends on network)
- **Output**: Console + JSON changelog file
- **File I/O**: One read per `.md` file, one write per file with changes

## Error Handling

### No Frontmatter

Files without YAML frontmatter are skipped with `[SKIP]` status.

### YAML Parse Error

Files with invalid YAML are warned and skipped.

### Network Errors

Network timeouts and connection errors are caught. URLs that fail are removed.

### File I/O Errors

File read/write errors are caught and logged in changelog with `ERROR_*` status.

## Integration with Pre-commit

You can add this script to `.pre-commit-config.yaml` to run automatically on bike note changes:

```yaml
- repo: local
  hooks:
    - id: validate-urls
      name: Validate URLs in bike notes
      entry: python scripts/validate_urls.py
      language: python
      files: ^vault/notes/.*\.md$
      stages: [commit]
      additional_dependencies: ["pyyaml", "requests"]
```

## Common Tasks

### Validate all URLs

```bash
python scripts/validate_urls.py
```

### Preview changes without modifying

```bash
python scripts/validate_urls.py --dry-run
```

### Find which URLs were removed

```bash
python scripts/validate_urls.py
cat VALIDATE_URLS_CHANGELOG.json | grep -A 5 "URLS_REMOVED"
```

### Validate URL structure only

```bash
python scripts/validate_urls.py --skip-check
```

## License

Same as the cargo-bikes repository.
