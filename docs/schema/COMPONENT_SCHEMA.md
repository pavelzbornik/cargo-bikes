# Component Frontmatter Schema

This document defines the recommended frontmatter for **component notes** (e.g., a note for the "Bosch Performance Line CX" motor). Creating individual notes for components allows you to detail their specs once and link to them from multiple bike notes, avoiding data duplication.

## YAML Schema

```yaml
---
title: string # (Required) The full, official name of the component.
type: string # (Required) The type of note, should be 'component'.
component_type: string # (Required) The category of component, e.g., "motor", "battery", "brake", "drivetrain", "light".
manufacturer: string # The name of the manufacturer, e.g., "Bosch eBike Systems".
model_name: string # The specific model name or number, e.g., "Performance Line CX".
release_year: number # The model year the component was released.
url: string # The official product page URL for the component.
tags: list[string] # Relevant tags for the component, e.g., [component, motor, mid-drive].
specs:# A mapping of technical data relevant to this component type.
  # Fields here should mirror the structure from the main Bike Schema.
  # See notes below for examples.
---
```

## Notes on Usage

- **The `specs` Block is Key:** The power of this schema comes from reusing the structure defined in the main **Bike Frontmatter Schema**.
  - For a **motor** component, the `specs` block would contain fields from `motor` section of the bike schema: `type`, `power_w`, `torque_nm`, etc.
  - For a **battery**, it would contain `capacity_wh`, `removable`, `charging_time_h`, etc.
  - For a **brake set**, it would contain `type`, `pistons`, etc.
- This approach maintains a single source of truth for your data structures, making automation much simpler.

### Example: `Bosch Performance Line CX.md`

```yaml
---
title: "Bosch Performance Line CX"
type: component
component_type: "motor"
manufacturer: "Bosch eBike Systems"
model_name: "Performance Line CX (Smart System)"
release_year: 2022
url: "https://www.bosch-ebike.com/us/products/performance-line-cx"
tags: [component, motor, mid-drive, bosch]
specs:
  type: "mid-drive"
  power_w: 250
  torque_nm: 85
  notes: "4th generation motor, compatible with the Bosch Smart System."
---

# Bosch Performance Line CX

This is the flagship motor from [Bosch eBike Systems](../../components/manufacturers/bosch.md), designed for eMTB and high-performance cargo bike applications.

## Bikes using this motor
- [Trek Fetch+ 2](../../bikes/trek/fetch-2.md)
- [Riese & Müller Load 75](../../bikes/riese-muller/load-75.md)
```
