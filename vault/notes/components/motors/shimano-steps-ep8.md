---
title: Shimano STEPS EP8
type: component
category: motors
parent: "[[Shimano]]"
domain: "[[Motors MOC]]"
tags:
  - motor
  - mid-drive
  - shimano
  - steps
  - ebike
  - cargo
generated_by: cargo-bikes-cli
motor_type: Mid-drive (crank motor)
nominal_power: 250W
peak_power: 360W
max_torque: 85 Nm
assist_ratio: up to 400%
max_assisted_speed_eu: 25 km/h
max_assisted_speed_us: 20 mph
weight_kg: 2.6
connectivity:
  - Bluetooth
  - ANT+
  - Di2
introduced: 2020
---

# Shimano STEPS EP8

## Overview

The Shimano STEPS EP8 is a second-generation mid-drive crank motor and the flagship unit in Shimano's STEPS e-bike drivetrain ecosystem. Introduced in 2020 as the successor to the E8000, the EP8 was designed to be lighter, quieter, and more responsive than its predecessor, while retaining class-leading torque figures. It is widely used across e-MTB, trekking, and cargo platforms.

The EP8 integrates tightly with Shimano's Di2 electronic shifting system and is configurable via the **E-TUBE Project** app, allowing riders and dealers to tune assist modes, response curves, and maximum output.

## Variants

| Variant    | Notes                                                           |
| ---------- | --------------------------------------------------------------- |
| **EP8**    | Standard trail/trekking unit; 25 km/h assist limit (EU)         |
| **EP8-RS** | Speed-pedelec variant; 45 km/h assist limit                     |
| **EP8-C**  | Cargo/urban-optimised tuning; suited to heavy load applications |

The EP8-C variant is specifically tuned for the demands of cargo cycling — modulating power delivery under high payloads and at low cadences, making it a natural fit for longtail and front-loader cargo bikes.

## Key Specifications

> Specs sourced from Shimano product documentation (training data, 2020–2024). Verify current figures at [[Shimano]] or the official STEPS product page.

- **Motor type:** Mid-drive (bottom-bracket-mounted)
- **Nominal power:** 250 W (EU legal limit)
- **Peak power:** ~360 W
- **Maximum torque:** 85 Nm
- **Maximum assist ratio:** 400%
- **Weight:** 2.6 kg (motor unit only)
- **Max assisted speed:** 25 km/h (EU) / 20 mph (US) — EP8-RS variant: 45 km/h
- **Connectivity:** Bluetooth LE, ANT+, Shimano Di2 (E-TUBE)
- **Chainring interface:** Direct mount
- **Walk-assist:** Yes (6 km/h push-assist mode)
- **Assist modes:** 3 configurable via display (e.g. ECO / TRAIL / BOOST, tunable in app)

## Compatible Displays

- SC-E7000
- SC-EN500
- SC-E6100
- Di2 junction box integration (via E-TUBE)

## Bikes Using This Component

- [[Xtracycle eSwoop]]

## Comparisons to Alternatives

| Motor                         | Max Torque | Weight  | Notes                            |
| ----------------------------- | ---------- | ------- | -------------------------------- |
| Shimano EP8                   | 85 Nm      | 2.6 kg  | Strong Di2 integration; tunable  |
| [[Bosch Performance Line CX]] | 85 Nm      | 2.9 kg  | Dominant cargo motor; eMTB mode  |
| [[Brose Drive S Mag]]         | 90 Nm      | 2.9 kg  | Smooth, natural feel; quiet      |
| [[Fazua Ride 60]]             | 60 Nm      | 1.96 kg | Lighter but lower torque ceiling |

The EP8 is competitive on torque with the Bosch CX but is notably lighter. Its tighter integration with Shimano gearing (Di2 auto-shift via E-TUBE) is a meaningful advantage on multi-speed cargo builds like the [[Xtracycle eSwoop]].

## Notes

- The EP8 replaced the **E8000** in 2020 with a ~200 g weight reduction and reduced noise.
- Motor housing uses an **IPX6** water/dust rating.
- Firmware is updatable via E-TUBE Project (desktop and mobile).
- Not backward-compatible with first-generation STEPS displays without an adapter.

## Related Notes

- [[Shimano]]
- [[Motors MOC]]
- [[Xtracycle eSwoop]]
- [[Bosch Performance Line CX]]
