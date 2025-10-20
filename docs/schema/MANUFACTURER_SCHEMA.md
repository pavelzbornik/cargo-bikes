# Manufacturer Frontmatter Schema

This document defines the recommended frontmatter structure for **manufacturer notes** (e.g., a note for "Tern" or "Bosch"). These notes serve as central hubs for information about a company, linking to all the bikes and components they produce.

## YAML Schema

```yaml
---
title: string # (Required) The official name of the manufacturer.
type: string # (Required) The type of note, should be 'manufacturer'.
founded_year: number # The year the company was founded.
country: string # The country of origin or headquarters, e.g., "Germany".
url: string # The main corporate or brand website URL.
logo: string # Filename or URL for the company's logo, e.g., "bosch-logo.svg".
summary: string # A brief one-sentence description of the company and its focus.
product_types: list[string] # A list of primary products, e.g., ["bikes", "motors", "drivetrains"].
parent_company: string # The name of the parent company, if any (e.g., "Robert Bosch GmbH").
tags: list[string] # Relevant tags, e.g., [manufacturer, german-engineering, component-maker].
---
```

### Notes on Usage

- **`title`:** Use the official brand name. For divisions, you can be more specific, like "Bosch eBike Systems".
- **Linking:** The main purpose of this note is to be linked from other notes. In a bike or component note, you would link to it like this: `manufacturer: "[[Bosch eBike Systems]]"`.

### Example: `Bosch eBike Systems.md`

```yaml
---
title: "Bosch eBike Systems"
type: manufacturer
founded_year: 2009
country: "Germany"
url: "https://www.bosch-ebike.com/"
logo: "bosch-logo.svg"
summary: "A leading manufacturer of drive systems, including motors, batteries, and displays for electric bikes."
product_types: ["motors", "batteries", "displays", "ebike-systems", "software"]
parent_company: "Robert Bosch GmbH"
tags: [manufacturer, component, motor, battery, german-engineering]
---

# Bosch eBike Systems

Bosch eBike Systems is a division of the Robert Bosch GmbH group that specializes in developing and manufacturing complete electrical systems for e-bikes. Their products are widely used by many top-tier bike manufacturers.

## Key Products
- [[Bosch Performance Line CX]]
- [[Bosch PowerTube 500]]
```
