---
title: Specialized 2.2 Cargo
type: component
category: motors
parent: '[[Specialized]]'
domain: '[[Motors MOC]]'
tags:
- motor
- mid-drive
- specialized
- cargo
- ebike-component
generated_by: cargo-bikes-cli
motor_type: Mid-drive
nominal_power: 250W
peak_power: 530W
max_torque: 90 Nm
weight_kg: ~3.5
standard: EU EN15194 compliant
connectivity: ANT+, Bluetooth (Mission Control)
---
# Specialized 2.2 Cargo

## Overview

The Specialized 2.2 Cargo is a mid-drive electric motor developed by [Specialized](/components/motors/specialized.md) for use in their cargo-oriented Turbo platform bikes. It is a dedicated cargo variant within the 2.x motor family — Specialized's full-power motor line — tuned for higher sustained loads, low-cadence torque, and the stop-start riding patterns typical of cargo and utility cycling.

Unlike the lightweight [[Specialized SL 1.1]] motor (designed for road and light-trail use), the 2.2 Cargo prioritises raw torque output and thermal durability over weight savings.

## Specifications

| Attribute | Value |
|---|---|
| Motor type | Mid-drive |
| Nominal power (EU) | 250W |
| Peak power | 530W |
| Maximum torque | 90 Nm |
| Assist cut-off speed | 25 km/h (EU) |
| Connectivity | Bluetooth / ANT+ |
| App integration | Specialized Mission Control |
| Approx. motor weight | ~3.5 kg |

> [!note] Data sourced from training data (knowledge cutoff early 2025). Verify peak power and weight figures against current Specialized press materials or geometry/spec sheets for the most accurate values.

## Bikes Using This Motor

- [Specialized Turbo Porto](/bikes/specialized/turbo-porto.md)

## Motor Family Context

The 2.x series sits above the SL (Super Light) family in Specialized's motor lineup:

| Motor | Peak Power | Max Torque | Intended Use |
|---|---|---|---|
| [[Specialized SL 1.1]] | 240W | 35 Nm | Road, light trail |
| [[Specialized 2.1]] | 530W | 90 Nm | Trail, commuter |
| Specialized 2.2 Cargo | 530W | 90 Nm | Cargo, utility |

The 2.2 Cargo shares its core power figures with the 2.1 but is optimised in firmware and thermal management for the demands of cargo cycling — heavier total system weight, frequent low-speed loaded starts, and sustained hill climbing under load.

## Integration and Ecosystem

- Controlled via the **Specialized Mission Control** app (iOS/Android), allowing riders to customise assist levels, set maximum power modes, and view battery/motor diagnostics.
- Works with the Turbo platform's integrated battery system; battery sizing is bike-dependent (see [Specialized Turbo Porto](/bikes/specialized/turbo-porto.md) for battery specs).
- Compatible with Specialized's **Turbo Connect Unit (TCU)** display interface.

## Comparisons to Alternatives

| Motor | Max Torque | Weight | Notes |
|---|---|---|---|
| Specialized 2.2 Cargo | 90 Nm | ~3.5 kg | Proprietary, deep system integration |
| [Bosch Cargo Line](/components/motors/bosch-cargo-line.md) | 85 Nm | 3.9 kg | Industry standard, wide aftermarket support |
| [[Shimano EP8]] | 85 Nm | 2.6 kg | Lighter, broad compatibility |
| [[Fazua Ride 60]] | 60 Nm | 1.96 kg | Lightweight only, not cargo-class |

The 2.2 Cargo's main advantage is deep integration with Specialized's own software and battery ecosystem. Its main limitation is exclusivity to Specialized platforms — it is not available as an aftermarket or OEM component for other brands.

## Notes

- "2.2" likely denotes a second-generation revision of Specialized's full-power motor architecture; exact generation changelog is not publicly detailed by Specialized.
- Rider-facing motor branding on the [Specialized Turbo Porto](/bikes/specialized/turbo-porto.md) may simply read "Turbo" — the 2.2 Cargo designation appears in technical/spec documentation.

## References

- [Specialized](/components/motors/specialized.md)
- [Specialized Turbo Porto](/bikes/specialized/turbo-porto.md)
- [[Motors MOC]]
