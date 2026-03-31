---
title: Bafang M400
type: component
category: motors
parent: "[[Bafang]]"
domain: "[[Motors MOC]]"
tags:
  - motor
  - mid-drive
  - bafang
  - 36v
  - 250w
generated_by: cargo-bikes-cli
motor_type: Mid-drive
rated_power: 250W
peak_power: ~500W
torque: 80 Nm
voltage: 36V
weight_kg: 3.3
bottom_bracket: 68 / 73 mm
chainline_mm: 52
sensor: Torque + cadence
assist_levels: 5 (configurable via programming cable)
waterproof_rating: IPX6
---

# Bafang M400

## Overview

The Bafang M400 is a mid-drive motor in [[Bafang]]'s M-series lineup, positioned as a mid-range unit between the entry-level M200 and the high-torque [[Bafang M600]]. It targets commuter and light cargo e-bike applications where a balance of performance, weight, and cost is required.

The M400 uses a combined torque and cadence sensor system, providing more natural pedal-assist feel compared to cadence-only motors.

> [!info] Data source
> Specs below are drawn from manufacturer documentation and training data (knowledge cutoff 2025). Verify against the latest Bafang datasheets for production variants.

## Specifications

| Parameter                    | Value                          |
| ---------------------------- | ------------------------------ |
| Motor type                   | Mid-drive                      |
| Rated power                  | 250 W (EN 15194 compliant)     |
| Peak power                   | ~500 W                         |
| Max torque                   | 80 Nm                          |
| Voltage                      | 36 V                           |
| Weight                       | ~3.3 kg                        |
| Bottom bracket compatibility | 68 mm / 73 mm threaded         |
| Chainline                    | 52 mm                          |
| Sensor system                | Torque sensor + cadence sensor |
| Assist levels                | 5 (configurable)               |
| Interface                    | UART                           |
| Waterproof rating            | IPX6                           |
| Compatible displays          | DPC-14, DPC-18, DP C07, SW102  |

## Bikes Using This Motor

- [[e-cargo Longtail L20]]

## Motor Position in Bafang M-Series

| Model    | Torque    | Voltage     | Notes                           |
| -------- | --------- | ----------- | ------------------------------- |
| M200     | 45 Nm     | 36 V        | Entry-level, cadence only       |
| **M400** | **80 Nm** | **36 V**    | **Mid-range, torque + cadence** |
| M600     | 120 Nm    | 36 V / 48 V | High-performance, cargo-focused |
| M820     | 160 Nm    | 48 V        | Ultra-high-torque, heavy cargo  |

## Compatibility Notes

- Uses a standard 68/73 mm threaded bottom bracket shell — common on steel and aluminium cargo framesets.
- UART communication protocol; not directly compatible with CAN-bus display ecosystems without an adapter.
- Chainring options: 38T–50T direct-mount spider (proprietary Bafang pattern).
- Programming via Bafang USB programming cable allows adjustment of current limits, assist levels, and speed cut-off.

## Alternatives

- [[Bafang M600]] — higher torque (120 Nm), better suited for heavy cargo loads above ~80 kg payload.
- [[Bosch Performance Line CX]] — comparable torque (85 Nm), more refined firmware, higher ecosystem cost.
- [[Shimano EP6]] — 85 Nm, strong integration with Shimano Di2 drivetrain components.

## Notes

- The M400 is a cost-effective choice for longtail cargo bikes carrying moderate loads.
- At 80 Nm it sits at the lower acceptable threshold for loaded cargo use; riders regularly carrying >60 kg cargo may prefer the [[Bafang M600]].
- Aftermarket tuning dongles (e.g., SpeedBox) are widely available but void warranty and may affect legal road compliance.

## References

- [[Bafang]] — manufacturer overview
- [[Motors MOC]] — full motor category index
