# Manufacturer/Brand Frontmatter Schema

This document defines the recommended frontmatter structure for **manufacturer and brand notes** (e.g., notes for "Tern", "Bosch", or "Gaya"). These notes serve as central hubs for information about a company, linking to all the bikes and components they produce or design.

## YAML Schema

```yaml
---
# Core Identity
title: string # (Required) The official brand/manufacturer name
type: string # (Required) Either 'brand' or 'manufacturer'
date: string # (Required) ISO date when note was created/updated, e.g., "2025-10-24"
url: string # The main corporate or brand website URL
logo: string # Filename or URL for the company's logo, e.g., "bosch-logo.svg"
summary: string # A brief one-sentence description of company focus and positioning

# Company Information
founded_year: number # The year the company was founded
country: string # Country of origin or primary headquarters, e.g., "Germany"
headquarters:
  city: string # City of headquarters
  country: string # Country of headquarters
  address: string # Full address (optional)

# Market & Positioning
categories: list[string] # Primary bike/product categories, e.g., ["longtail", "box-cargo", "trike"]
market_segments: list[string] # Target segments, e.g., ["urban-families", "professionals", "enthusiasts"]
regions: list[string] # Geographic regions served, e.g., ["EU", "North America", "Asia"]
price_tier: string # One of: "entry-level", "accessible", "mid-premium", "premium", "ultra-premium"

# Product Portfolio
product_types: list[string] # Primary products, e.g., ["bikes", "motors", "batteries", "drivetrains"]
model_count: number # Approximate number of current models
primary_motors: list[string] # Primary motor brands/systems used, e.g., ["Bosch", "Shimano", "proprietary"]
parent_company: string # Parent company name if applicable, e.g., "Robert Bosch GmbH"

# Manufacturing & Production
manufacturing:
  locations: list[string] # Countries where manufacturing occurs
  approach: string # One of: "in-house", "contracted", "hybrid"
  assembly_location: string # Country where final assembly occurs
  ethical_standards: string # Certifications or commitments, e.g., "Fair Trade certified", "employs individuals with disabilities"

# Distribution & Sales
distribution_model: string # One of: "direct", "retail", "both"
regions_active: list[string] # Regions with active sales/distribution
direct_sales: boolean # Whether brand sells directly to consumers
dealership_network: boolean # Whether distributed through dealers/resellers

# Impact Metrics (optional)
impact:
  bikes_sold_approx: number # Approximate lifetime bikes sold
  km_driven_approx: number # Approximate kilometers driven by customer bikes
  co2_avoided_kg_approx: number # Approximate CO2 avoided
  families_served: number # Approximate number of families/customers

# Brand Values & Differentiation
accessibility: list[string] # Value propositions, e.g., ["affordability", "safety-focused", "tech-integrated", "eco-conscious"]
values:
  sustainability: boolean # Environmental commitment prioritized
  local_manufacturing: boolean # Bikes/components made locally
  community_focus: boolean # Community co-design or engagement
  safety_emphasis: boolean # Safety features highlighted
  tech_integration: boolean # Smart/connected features emphasized

# Metadata
tags: list[string] # Searchable tags, e.g., [brand, belgian, longtail, electric, family-focused]
---
```

## Field Descriptions

| Field                | Type    | Required        | Notes                                                                            |
| -------------------- | ------- | --------------- | -------------------------------------------------------------------------------- |
| `title`              | string  | Yes             | Official brand/manufacturer name                                                 |
| `type`               | string  | Yes             | Either `brand` (cargo bike company) or `manufacturer` (component/motor supplier) |
| `date`               | string  | Yes             | ISO format (YYYY-MM-DD)                                                          |
| `url`                | string  | No              | Primary website URL                                                              |
| `logo`               | string  | No              | Logo filename or URL                                                             |
| `summary`            | string  | Yes             | One-sentence positioning statement                                               |
| `founded_year`       | number  | No              | Year of founding                                                                 |
| `country`            | string  | Yes             | Primary country (for filtering/discovery)                                        |
| `headquarters`       | object  | No              | Nested object with `city`, `country`, `address`                                  |
| `categories`         | array   | Yes (for bikes) | Bike types: longtail, box-cargo, trike, compact, midtail, etc.                   |
| `market_segments`    | array   | No              | Target customer profiles                                                         |
| `regions`            | array   | Yes             | Geographic markets served                                                        |
| `price_tier`         | string  | No              | Standardized pricing category                                                    |
| `product_types`      | array   | Yes             | What the company makes                                                           |
| `model_count`        | number  | No              | Number of active models                                                          |
| `primary_motors`     | array   | No              | Motor brands used in their bikes                                                 |
| `parent_company`     | string  | No              | If part of a larger group                                                        |
| `manufacturing`      | object  | No              | Nested production info                                                           |
| `distribution_model` | string  | No              | How customers purchase                                                           |
| `direct_sales`       | boolean | No              | Direct-to-consumer capability                                                    |
| `dealership_network` | boolean | No              | Retail partnership availability                                                  |
| `impact`             | object  | No              | Social/environmental metrics                                                     |
| `accessibility`      | array   | No              | Unique value propositions                                                        |
| `values`             | object  | No              | Boolean flags for brand characteristics                                          |
| `tags`               | array   | Yes             | Searchable keywords                                                              |

## Usage Guidelines

### For Cargo Bike Brands

Example: `Gaya.md`

```yaml
---
title: "Gaya"
type: "brand"
date: "2025-10-24"
url: "https://gaya.bike"
logo: "https://gaya.bike/api/medias/api/images/file/Gaya_Logo-1000x663.webp"
summary: "French manufacturer of smart, accessible electric cargo bikes designed for urban families, featuring integrated GPS security and comprehensive safety features."

founded_year: null
country: "France"
headquarters:
  city: "Vendée"
  country: "France"

categories: ["longtail", "box-cargo", "compact"]
market_segments: ["urban-families", "accessibility-focused"]
regions: ["EU"]
price_tier: "accessible"

product_types: ["bikes"]
model_count: 6
primary_motors: ["proprietary-rear-hub"]
parent_company: null

manufacturing:
  locations: ["France"]
  approach: "in-house"
  assembly_location: "France"
  ethical_standards: "Assembled in France since 2023; local employment commitment"

distribution_model: "both"
regions_active: ["EU"]
direct_sales: true
dealership_network: true

impact:
  bikes_sold_approx: null
  km_driven_approx: 5000000
  co2_avoided_kg_approx: 1045000
  families_served: 10000

accessibility:
  - "affordable-entry-level"
  - "comprehensive-safety"
  - "integrated-gps-security"
  - "family-focused"

values:
  sustainability: true
  local_manufacturing: true
  community_focus: true
  safety_emphasis: true
  tech_integration: true

tags: [brand, french, longtail, electric, family, affordable, gps-security]
---
```

### For Component Manufacturers

Example: `Bosch eBike Systems.md`

```yaml
---
title: "Bosch eBike Systems"
type: "manufacturer"
date: "2025-10-24"
url: "https://www.bosch-ebike.com/"
logo: "bosch-ebike-logo.svg"
summary: "Leading manufacturer of complete e-bike drive systems including motors, batteries, displays, and software."

founded_year: 2009
country: "Germany"
headquarters:
  city: "Stuttgart"
  country: "Germany"

categories: null # Manufacturers don't have bike categories
market_segments: ["bike-manufacturers", "premium-segment"]
regions: ["EU", "North America", "Asia"]
price_tier: "premium"

product_types: ["motors", "batteries", "displays", "ebike-systems", "software"]
model_count: null
primary_motors: null
parent_company: "Robert Bosch GmbH"

manufacturing:
  locations: ["Germany"]
  approach: "in-house"
  assembly_location: "Germany"
  ethical_standards: "ISO 14001 certified"

distribution_model: "b2b"
regions_active: ["EU", "North America", "Asia"]
direct_sales: false
dealership_network: false

impact: null # Not typically tracked for component makers

accessibility:
  - "industry-leading-reliability"
  - "wide-compatibility"

values:
  sustainability: true
  local_manufacturing: true
  community_focus: false
  safety_emphasis: true
  tech_integration: true

tags: [manufacturer, component, motor, battery, german-engineering, premium]
---
```

## Notes on Usage

- **`title`:** Use the official brand/manufacturer name. For divisions, be specific (e.g., "Bosch eBike Systems" not just "Bosch").
- **`type`:** Distinguish between `brand` (companies that design/sell cargo bikes) and `manufacturer` (component/motor suppliers).
- **Linking:** Reference manufacturers in text using Markdown links, e.g., `[Gaya](../manufacturers/gaya.md)` or in bike frontmatter as plain text. Use Markdown links in content sections when cross-referencing.
- **Structured Data:** Boolean flags in `values` enable filtering and discovery across the vault.
- **Impact Metrics:** Optional but valuable for understanding brand scale and environmental contribution.
- **Regional Specificity:** Use consistent region names: "EU", "North America", "Asia-Pacific", "UK", etc.
