---
title: Shimano EP801
type: component
category: motors
parent: '[[Shimano]]'
domain: '[[Motors MOC]]'
tags:
- motor
- shimano
- steps
- mid-drive
- cargo
- ep801
generated_by: cargo-bikes-cli
motor_type: Mid-drive (AC brushless DC)
torque_nm: 85
rated_power_w: 250
assist_ratio_max_pct: 400
weight_kg: 2.95
q_factor_mm: 177
chainline_mm: 50 / 56
cadence_range_rpm: 0–120
assist_modes:
- Eco
- Trail
- Boost
walk_assist: true
di2_compatible: true
---
# Shimano EP801

## Overview

The Shimano EP801 is a mid-drive motor unit within the [[Shimano]] STEPS platform, purpose-built for cargo and load-carrying e-bikes. It succeeds and extends the EP8 lineage with reinforced torque output and improved thermal management to handle the sustained, heavy-load demands of cargo cycling. The unit integrates directly with Shimano's Di2 electronic drivetrain ecosystem and is controlled via the SC-EM800 or compatible cycle computers.

## Key Specifications

| Specification | Value |
|---|---|
| Motor type | AC brushless DC, mid-drive |
| Rated output (EU) | 250 W |
| Peak torque | 85 Nm |
| Max assist ratio | 400% |
| Cadence range | 0–120 RPM |
| Motor weight | ~2.95 kg |
| Q-factor | 177 mm |
| Chainline | 50 mm / 56 mm |
| Walk assist | Yes |
| Di2 compatible | Yes |
| Assist modes | Eco, Trail, Boost |

> **Note:** Specifications above are drawn from Shimano STEPS EP801 product documentation known at training cutoff. Verify against current Shimano dealer documentation for the latest revisions.

## Assist Modes

- **Eco** — Maximum range, reduced assist output; suited to flat terrain and light loads.
- **Trail** — Balanced assist; the general-purpose mode for varied terrain with a loaded cargo bike.
- **Boost** — Full 85 Nm output; intended for hill starts, steep inclines, and maximum payload situations.

Walk assist mode activates a low-speed motor push (up to ~6 km/h) useful when manoeuvring a loaded cargo bike in tight spaces.

## Compatible Batteries

The EP801 is compatible with the Shimano STEPS battery range, including:

- BT-E8035 (504 Wh, frame-integrated)
- BT-E8043 (630 Wh, frame-integrated)
- Dual-battery configurations where frame geometry permits

## Bikes Using This Component

- [[Mundo EP801]]

## Comparison to Alternatives

| Motor | Torque | Rated Power | Notable Difference |
|---|---|---|---|
| Shimano EP801 | 85 Nm | 250 W | Cargo-optimised, Di2 integration |
| Shimano EP6 | 60 Nm | 250 W | Lighter, trail/trekking focus |
| Bosch CX Gen 4 | 85 Nm | 250 W | eMTB/cargo competitor, different ecosystem |
| Brose Drive S Mag | 90 Nm | 250 W | Quieter operation, less ecosystem breadth |

## Notes

- The EP801 shares the same 250 W EU-rated output as the EP8 but is distinguished by its cargo-specific thermal design and load-bearing casing.
- Di2 integration allows automatic gear shifting to be coordinated with motor assist changes, reducing drivetrain wear under load.
- Firmware updates are applied via E-TUBE PROJECT Voyager (iOS/Android) or the desktop E-TUBE PROJECT app.

## Related Notes

- [[Shimano]]
- [[Motors MOC]]
- [[Mundo EP801]]
