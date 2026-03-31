---
title: Shimano EP6 Cargo
type: component
category: motors
parent: "[[Shimano]]"
domain: "[[Motors MOC]]"
tags:
  - motor
  - shimano
  - mid-drive
  - cargo
  - ebike
  - steps
generated_by: cargo-bikes-cli
motor_type: Mid-drive
nominal_power: 250W
peak_torque: 85 Nm
weight_kg: 2.9
voltage: 36V
max_cadence_rpm: 120
system: Shimano STEPS
max_system_weight_kg: 150
walk_assist: true
di2_compatible: true
---

## Shimano EP6 Cargo

The Shimano EP6 Cargo (model code EP600) is a mid-drive motor unit from [[Shimano]]'s STEPS e-bike system, purpose-engineered for cargo bikes and utility cycles carrying heavy loads. It is a variant of the standard EP6 motor with firmware and mechanical tuning optimised for the higher total system weights typical of longtail and box-cargo configurations.

## Overview

The EP6 Cargo delivers 85 Nm of peak torque at a nominal 250 W continuous output, keeping it within EU and UK pedelec regulations. Its compact mid-drive format places mass low and centrally in the frame, which is particularly advantageous for cargo bikes where rider and payload shift the overall centre of gravity rearward or upward.

Shimano rates the EP6 Cargo for a maximum total system weight (bike + rider + cargo) of approximately 150 kg, distinguishing it from recreational EP6 variants tuned for lighter sport applications.

## Specifications

| Specification             | Value                               |
| ------------------------- | ----------------------------------- |
| Motor type                | Mid-drive (bottom bracket)          |
| Nominal power             | 250 W                               |
| Peak torque               | 85 Nm                               |
| Voltage                   | 36 V                                |
| Maximum supported cadence | 120 RPM                             |
| Motor unit weight         | ~2.9 kg                             |
| Max total system weight   | ~150 kg                             |
| Walk assist               | Yes                                 |
| Di2 compatibility         | Yes                                 |
| Connectivity              | Bluetooth / ANT+ (via display unit) |
| STEPS system              | Yes                                 |

> [!note] Spec verification
> Weight and maximum system weight figures are drawn from training data (knowledge cutoff early 2025). Verify against the current [[Shimano]] STEPS EP6 Cargo product page before publishing.

## STEPS System Integration

The EP6 Cargo operates within the broader Shimano STEPS ecosystem, allowing integration with:

- **Display units** — SC-E6100, SC-E7000, SC-E8000 series
- **Batteries** — BT-E8035 and BT-E8036 (504 Wh / 630 Wh) as well as frame-integrated options
- **Di2 electronic shifting** — enables automatic gear changes co-ordinated with motor assist

Assist modes are typically configurable via the E-TUBE PROJECT app, with Eco, Trail/Normal, Boost, and customisable modes available depending on OEM implementation.

## Bikes Using This Component

- [[Peugeot e-Longtail]]

## Comparisons to Alternatives

| Motor                     | Peak Torque | Notes                                           |
| ------------------------- | ----------- | ----------------------------------------------- |
| Shimano EP6 Cargo         | 85 Nm       | Cargo-optimised, mid-range STEPS                |
| Shimano EP8 / EP801       | 85 Nm       | Higher-end, lighter, more sport-oriented        |
| Bosch Cargo Line          | 85 Nm       | Direct competitor; broader cargo OEM adoption   |
| Bosch Performance Line CX | 85 Nm       | Sport focus; less cargo-specific tuning         |
| Bafang M620 (Ultra)       | 160 Nm      | High torque, common in aftermarket cargo builds |

The EP6 Cargo sits in [[Shimano]]'s mid-tier STEPS offering. The EP8/EP801 shares the same torque figure but targets lighter recreational and mountain applications. Bosch's Cargo Line is the most direct market rival, with similar torque and a comparably large OEM cargo-bike install base.

## Market Position

The EP6 Cargo is positioned as a reliable, cost-effective OEM choice for mid-range electric cargo bikes. Its integration with the mature STEPS ecosystem — including batteries, displays, and Di2 — lowers development complexity for bike manufacturers. It is a common choice for family longtails and urban utility bikes in the EUR 3,000–5,000 segment.

## References

- [[Shimano]] — parent manufacturer
- [[Peugeot e-Longtail]] — uses this motor
- [[Motors MOC]] — domain overview

---

**Notes on sourcing:**

- Core specs (85 Nm torque, 250 W, 36 V, 120 RPM cadence, Di2 compatibility, walk assist) are well-established from Shimano STEPS documentation available before my knowledge cutoff.
- The `~2.9 kg` weight and `~150 kg` max system weight are based on training data — the `[!note]` callout in the spec table flags these for manual verification against Shimano's live product page before the note is published.
