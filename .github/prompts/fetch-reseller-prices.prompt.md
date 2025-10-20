---
mode: agent
description: "Fetch bike pricing and availability from reseller websites and update bike notes"
---

# Fetch & Update Reseller Pricing Information

## Objective

Fetch bike pricing, availability, and reseller information from specified reseller websites and update the `resellers` section in existing bike note frontmatter. This ensures price data remains current across multiple sales channels and regions.

! IMPORTANT: Do not stop until all bikes from the reseller website are processed.
! IMPORTANT: When updating reseller information, merge new data with existing resellers (preserve existing entries, add new ones).

## Process

### Phase 1: Fetch All Reseller Data & Create Master Table

**Objective:** Collect all bikes from the reseller website into a single structured table for audit and matching.

#### Step 1.1: Retrieve Complete Bike Listings

- Retrieve complete bike listings from the provided reseller website URL
- Handle pagination or multiple requests if needed to get all products
- **IMPORTANT: Do not stop until all bikes from the reseller are fetched**
- Extract: bike name/model, brand, price, currency, availability status, product URL, region

#### Step 1.2: Create Master Reseller Data Table

Create a new Markdown file (if it doesn't exist) at `docs/temp-reseller-fetches/[RESELLER_NAME]-[DATE].md` with the following structure:

**File naming:** `docs/temp-reseller-fetches/[RESELLER_NAME]-2025-10-20.md`

**Example:** `docs/temp-reseller-fetches/trek-store-2025-10-20.md`

**Table structure:**

```markdown
---
title: "[Reseller Name] Bike Inventory - [Date]"
reseller: "[Reseller Name]"
url: "[Reseller Website URL]"
fetch_date: "2025-10-20"
fetch_status: "in-progress"
total_bikes: [number]
bikes_matched: 0
bikes_unmatched: 0
---

## Reseller Bike Data

| #   | Brand       | Model    | Price | Currency | Region        | Availability | Product URL | Vault Match     | Match Status |
| --- | ----------- | -------- | ----- | -------- | ------------- | ------------ | ----------- | --------------- | ------------ |
| 1   | Trek        | Fetch+ 2 | 5999  | USD      | North America | in-stock     | https://... | trek-fetch-2.md | ✓ matched    |
| 2   | Tern        | GSD S10  | 3899  | USD      | North America | in-stock     | https://... | tern-gsd-s10.md | ✓ matched    |
| 3   | Urban Arrow | Family   | 4500  | EUR      | EU            | pre-order    | https://... | —               | ✗ not found  |
```

**Table column definitions:**

- \# — Sequential row number
- Brand — Bike manufacturer name
- Model — Bike model name
- Price — List price (number or "from XXXX")
- Currency — ISO 4217 code (USD, EUR, GBP, etc.)
- Region — Standardized region (North America, EU, UK, APAC, LATAM)
- Availability — one of: in-stock, pre-order, out-of-stock, discontinued
- Product URL — Direct link to bike on reseller site
- Vault Match — Filename of matched vault note or "—" if unmatched
- Match Status — ✓ matched, ✗ not found, or ? ambiguous

## Phase 2: Match Fetched Bikes to Vault Notes

**Objective:** Identify which fetched bikes correspond to existing vault bike notes.

### Step 2.1: Perform Matching

For each bike in the reseller data table:

1. Use the bike list in `vault\notes\index.md` as the base to search for matches
2. Match by **brand and model name**:
   - Exact match: Brand folder and model filename match reseller data
   - Handle minor variations: "Trek Fetch+ 2" → `trek/fetch-2.md` or `trek/fetch-plus-2.md`
   - Case-insensitive and normalized comparison
3. If no match found, mark as `✗ not found` and note for potential new bike entry
4. If ambiguous (multiple potential matches), mark as `? ambiguous` and require manual review

#### Step 2.2: Update Master Table

Update the master table with:

- `Vault Match` column: Filename of matched note or "—"
- `Match Status` column: `✓ matched`, `✗ not found`, or `? ambiguous`
- Update frontmatter: `bikes_matched` and `bikes_unmatched` counts

### Phase 3: Update Vault Bike Notes (Reseller Section Only)

**Objective:** Update the `resellers` section in matched bike frontmatter with new reseller data.

#### Step 3.1: For Each Matched Bike

1. Locate the vault bike note (from `Vault Match` column)
2. Open the file and identify the frontmatter `resellers` array
3. Check for existing reseller entry:
   - **If reseller already exists**: Update only these fields:
     - `price` (new value)
     - `availability` (new status)
     - `note` (if changed)
     - Keep `url` and other fields as-is
   - **If new reseller**: Add complete new entry to array
4. **PRESERVE ALL OTHER CONTENT**: Do not modify:
   - Title, type, brand, model, date, tags, url, image
   - `specs` object and all technical details
   - Content sections (paragraphs, lists, references)
   - Comments or modification notes

#### Step 3.2: Reseller Entry Structure

```yaml
resellers:
  - name: "<Reseller Name>"
    url: "<Direct Product URL>"
    price: <number or "from XXXX">
    currency: "<Currency Code>"
    region: "<Region>"
    availability: "<in-stock|pre-order|out-of-stock|discontinued>"
    note: ""
```

#### Step 3.3: Update Date Only When Modifying

- Update the top-level `date` field only if reseller information changed
- Set to current date in ISO 8601 format (YYYY-MM-DD)
- If no reseller changes occurred, preserve original date

#### Step 3.4: Continue Until Complete

- Process all matched bikes from the reseller data table
- For unmatched bikes (`✗ not found`), note them for potential new bike fetch (separate workflow)

### 5. Field-Specific Guidelines

These guidelines apply to all reseller data entries in both the master table and vault updates.

**Price field:**

- Use numeric values for exact prices (e.g., `4999`)
- Use strings for ranges (e.g., `"from 4999"`, `"3999-4999"`)
- If pricing is unavailable, use `null`

**Availability field:**

- `in-stock`: Product currently available for immediate purchase
- `pre-order`: Product available for pre-order with a future delivery date
- `out-of-stock`: Currently unavailable but not permanently discontinued
- `discontinued`: Product is no longer offered by the reseller

**Region field:**

- Use standardized region names:
  - North America (USA, Canada)
  - EU (European Union countries)
  - UK (United Kingdom)
  - APAC (Asia-Pacific)
  - LATAM (Latin America)
  - Other specific country/region names if needed

**Currency codes:**

- Use ISO 4217 codes: USD, EUR, GBP, CAD, AUD, JPY, CHF, etc.

**Note field:**

- Leave empty string if no special notes
- Include: shipping policies, warranty info, bundle deals, financing options, regional limitations
- Example: `"Free shipping in Germany"` or `"Financing available 0% APR 12 months"`

### 6. Quality Checks: Master Table

Before finalizing the master reseller data table:

- **All bikes fetched** — Confirm total count matches reseller's inventory
- **Price consistency** — Prices are formatted correctly (numbers or quoted strings)
- **URL validity** — All product URLs are functional and link directly to product pages
- **Currency codes** — Are valid ISO 4217 codes
- **Availability status** — Uses one of the four standard values
- **Region accuracy** — Region is appropriate for the reseller's service area
- **Matching accuracy** — All matches verified against actual vault notes

### 7. Quality Checks: Vault Updates

Before finalizing each vault bike note update:

- **YAML syntax** — No missing colons, quotes, or incorrect indentation
- **Reseller entry completeness** — All required fields (name, url, price, currency, region, availability, note)
- **Price consistency** — Formatted correctly (numbers or quoted strings)
- **URL validity** — Links directly to the bike's product page on reseller site
- **No duplicate resellers** — Each reseller appears only once in the array
- **Preservation test** — ALL other content unchanged:
  - Title, type, brand, model, tags, url, image, date (only if reseller changed)
  - Entire `specs` object
  - All content sections and paragraphs
  - No accidental deletions or modifications

### 8. Handling Multiple Regions (Same Reseller)

If a reseller offers the same bike in multiple regions with different prices:

- Create separate entries for each region in the vault note's `resellers` array
- Example:

```yaml
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/en_US/bikes/.../fetch-2/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: "Free shipping on orders over $100"
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/de/de_DE/bikes/.../fetch-2/"
    price: 5999
    currency: "EUR"
    region: "EU"
    availability: "in-stock"
    note: "German warehouse"
```

### 9. Handling Price Changes

When updating prices from reseller data:

- Simply update to the current price in the reseller entry
- If a significant price change occurred, note it in the `note` field:
  - Example: `"Price increased from €4999 to €5299"`
  - Or let the top-level `date` field (updated when reseller info changes) indicate when change was recorded

### 10. Language & Data Standards

- **All text** must be in English (translate if sourced from non-English resellers)
- **Preserve bike model names** — Never translate brand or model names
- **Standardize currency** — Use ISO 4217 codes consistently
- **URLs** — Use the direct product link from the reseller's domain

## Workflow Summary

```text
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: FETCH ALL BIKES FROM RESELLER                           │
├─────────────────────────────────────────────────────────────────┤
│ • Get all bike listings (handle pagination)                       │
│ • Extract: brand, model, price, currency, availability, URL      │
│ • Store in master table: docs/temp-reseller-fetches/[NAME].md     │
│ • Table structure with Vault Match and Match Status columns      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: MATCH FETCHED BIKES TO VAULT NOTES                      │
├─────────────────────────────────────────────────────────────────┤
│ • For each bike in master table                                   │
│ • Search vault for matching brand/model                           │
│ • Populate "Vault Match" and "Match Status" columns              │
│ • Identify unmatched bikes (✗ not found)                          │
│ • Update master table frontmatter with counts                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: UPDATE VAULT BIKE NOTES (RESELLER SECTION ONLY)        │
├─────────────────────────────────────────────────────────────────┤
│ • For each matched bike (✓ matched)                              │
│ • Open vault note file                                            │
│ • Update resellers array with new reseller data                  │
│ • UPDATE ONLY: resellers array + date (if changed)              │
│ • PRESERVE ALL: title, type, brand, model, specs, content       │
│ • Validate YAML syntax                                           │
│ • Commit changes                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Example Workflow

**Original frontmatter:**

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2024-09-15
tags: [bike, longtail, trek]
url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/p/41913/"
image: "trek-fetch-2.jpg"
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/p/41913/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: ""
specs: ...
```

**After fetching from BikeShop.com:**

```yaml
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: ""
  - name: "BikeShop.com"
    url: "https://bikeshop.com/trek-fetch-2"
    price: 5799
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: "Free shipping & assembly included"
```

## Workflow Examples

### Step 1: Master Table Created

After fetching all bikes from "BikeShop.com", create `docs/temp-reseller-fetches/bikeshop-2025-10-20.md`:

```markdown
---
title: "BikeShop.com Inventory - 2025-10-20"
reseller: "BikeShop.com"
fetch_date: "2025-10-20"
fetch_status: "in-progress"
total_bikes: 47
bikes_matched: 45
bikes_unmatched: 2
---

| \#  | Brand       | Model    | Price | Currency | Region        | Availability | Product URL                       | Vault Match     | Match Status |
| --- | ----------- | -------- | ----- | -------- | ------------- | ------------ | --------------------------------- | --------------- | ------------ |
| 1   | Trek        | Fetch+ 2 | 5799  | USD      | North America | in-stock     | https://bikeshop.com/trek-fetch-2 | trek-fetch-2.md | ✓ matched    |
| 2   | Tern        | GSD S10  | 3899  | USD      | North America | in-stock     | https://bikeshop.com/tern-gsd-s10 | tern-gsd-s10.md | ✓ matched    |
| ... | ...         | ...      | ...   | ...      | ...           | ...          | ...                               | ...             | ...          |
| 46  | Urban Arrow | Family   | 4500  | EUR      | EU            | pre-order    | https://bikeshop.com/ua-family    | —               | ✗ not found  |
| 47  | Generic     | Cargo XL | 2999  | USD      | North America | discontinued | https://bikeshop.com/generic-xl   | —               | ✗ not found  |
```

### Step 2: Matching Complete

All bikes matched or flagged. Table shows 45 matches, 2 unmatched.

### Step 3: Vault Updates

**Original vault note** (`vault/notes/bikes/trek/fetch-2.md`):

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2024-09-15
tags: [bike, longtail, trek, bosch]
url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/"
image: "trek-fetch-2.jpg"
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: ""
specs:
  motor:
    brand: "Bosch"
    type: "Performance CX"
    # ... rest of specs
---
# Trek Fetch+ 2

Long description and content here...
```

**After updating from BikeShop.com** (RESELLER SECTION ONLY):

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2025-10-20
tags: [bike, longtail, trek, bosch]
url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/"
image: "trek-fetch-2.jpg"
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: ""
  - name: "BikeShop.com"
    url: "https://bikeshop.com/trek-fetch-2"
    price: 5799
    currency: "USD"
    region: "North America"
    availability: "in-stock"
    note: "Free shipping & assembly included"
specs:
  motor:
    brand: "Bosch"
    type: "Performance CX"
    # ... rest of specs UNCHANGED
---
# Trek Fetch+ 2

Long description and content here... (UNCHANGED)
```

**What changed:**

- ✓ Date updated to 2025-10-20
- ✓ New BikeShop.com entry added to `resellers` array
- ✓ Existing Trek Official Store entry preserved
- ✗ NO changes to: title, type, brand, model, tags, url, image, specs, or content

## Output & Validation

### Phase 1 Output: Master Table

Create and save: `docs/temp-reseller-fetches/[RESELLER_NAME]-[DATE].md`

Include in frontmatter:

- `reseller`: Reseller name
- `fetch_date`: Date fetched (ISO 8601)
- `fetch_status`: "in-progress" or "complete"
- `total_bikes`: Total count from reseller
- `bikes_matched`: Count matched to vault
- `bikes_unmatched`: Count not found in vault

### Phase 2 Output: Matching Report

Include in the master table file:

- Complete table with all bikes, matches, and statuses
- List of unmatched bikes for potential future fetch-bikes workflow
- Any ambiguous matches requiring manual review

### Phase 3 Output: Final Report

After all vault updates, provide:

1. **Summary**:
   - Total vault notes updated
   - Total new reseller entries added
   - Total existing reseller entries updated
   - Any vault update failures or errors

2. **Changed files**:
   - List all modified bike note files
   - Relative paths from workspace root

3. **Unmatched bikes**:
   - Count of bikes from reseller not found in vault
   - List for potential new bike entry via fetch-bikes workflow

4. **Quality validation**:
   - YAML syntax check results for all modified files
   - URL validation results
   - Currency code validation
   - No unintended data loss (spot-check 3-5 updated files)

5. **Master table update**:
   - Set `fetch_status: "complete"` in master table frontmatter
   - Document any issues or manual interventions

## Critical Rules & Guardrails

### IMPORTANT: Reseller Section Only

- Only modify the `resellers` array and top-level `date` field
- NEVER modify: title, type, brand, model, tags, url, image, specs, or any content sections
- Verify no unintended changes by comparing against original before and after

### IMPORTANT: Complete All Phases

- Do not stop until all bikes from the reseller website are fetched (Phase 1)
- Do not update vault notes until matching is complete (Phase 2)
- Validate all updates before finalizing (Phase 3)

### IMPORTANT: Master Table Audit Trail

- Always create/maintain the master reseller table for audit and transparency
- This allows verification of what was fetched and which bikes were matched
- Keeps a record of unmatched bikes for potential future workflows

### IMPORTANT: Preserve Existing Data

- When updating an existing reseller entry, only change: price, availability, note
- Keep existing: url and all other reseller fields as-is
- Merge new resellers into existing array; never replace the entire array

### Focus Areas

- Accuracy and currency of reseller data — this is your primary objective
- Audit trail via master table — ensure transparency in fetch/match/update workflow
- Preservation of existing bike content — no accidental modifications
- One logical reseller update per session (e.g., one reseller's entire catalog per invocation)
