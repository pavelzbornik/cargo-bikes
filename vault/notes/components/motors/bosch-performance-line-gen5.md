---
title: Bosch Performance Line Gen5
type: component
category: motors
parent: "[[Bosch]]"
domain: "[[Motors MOC]]"
tags:
  - motor
  - bosch
  - mid-drive
  - smart-system
  - gen5
  - cargo-bike
generated_by: cargo-bikes-cli
torque_nm: 85
power_w: 250
peak_power_w: 600
weight_kg: 2.9
max_speed_kmh: 25
max_speed_speed_variant_kmh: 45
cadence_range_rpm: up to 120
system: Smart System
connectivity: Bluetooth, ANT+
release_year: 2020
---

## Bosch Performance Line Gen5

A fifth-generation mid-drive motor from [[Bosch]], part of the Smart System platform. Released in 2020, it delivers 85 Nm of torque and is engineered for cargo, urban, and trail e-bike applications requiring reliable, low-noise assist.

## Specifications

| Spec                 | Value                                        |
| -------------------- | -------------------------------------------- |
| Nominal Power        | 250 W (EU pedelec)                           |
| Peak Power           | ~600 W (momentary)                           |
| Torque               | 85 Nm                                        |
| Weight               | 2.9 kg                                       |
| Max Assisted Speed   | 25 km/h (standard) / 45 km/h (Speed variant) |
| Cadence Range        | Up to 120 RPM                                |
| System Compatibility | Bosch Smart System only                      |
| Connectivity         | Bluetooth + ANT+                             |
| App                  | Bosch eBike Flow                             |

## Features

- **eMTB Mode** — continuously variable torque modulation without fixed assist levels; responds dynamically to rider input and terrain
- **Reduced Noise** — approximately 50% quieter than the Gen4 predecessor; no published dB figure from Bosch
- **Smart System Integration** — firmware updatable over-the-air via the eBike Flow app; compatible with Kiox 300, Nyon (BUI350), and Intuvia 100 displays
- **Free Ride Mode** — no assist cut-off when speed exceeds the assist threshold on descents
- **Extended Temperature Range** — improved cold-weather performance vs Gen4
- **No Separate Speed Sensor Required** — on supported frame integrations, speed data is derived internally

## Compatibility Notes

The Gen5 motor is exclusive to the **Bosch Smart System** platform and is not backwards compatible with the older Bosch Legacy system (different battery connectors and communication protocol). Batteries must be Smart System PowerTube or PowerPack units.

## Bikes Using This Component

- [[Bike43 Short]]

## Comparisons to Alternatives

| Motor                          | Torque | Weight | System           |
| ------------------------------ | ------ | ------ | ---------------- |
| Bosch Performance Line Gen5    | 85 Nm  | 2.9 kg | Smart System     |
| Bosch Performance Line CX Gen4 | 75 Nm  | 3.0 kg | Legacy           |
| Shimano EP8                    | 85 Nm  | 2.6 kg | Di2 / standalone |
| Brose Drive S Mag              | 90 Nm  | 2.9 kg | standalone       |

## Notes

> Specs sourced from Bosch eBike Systems training data (knowledge cutoff 2025). Verify torque, weight, and variant availability against the [official Bosch product page](https://www.bosch-ebike.com/en/products/drives) before publishing, as regional variants may differ.

## References

- [[Bosch]]
- [[Motors MOC]]
