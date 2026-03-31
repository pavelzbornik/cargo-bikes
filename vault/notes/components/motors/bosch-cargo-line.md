---
title: Bosch Cargo Line
type: component
category: motors
parent: "[[Bosch]]"
domain: "[[Motors MOC]]"
tags:
  - motor
  - bosch
  - mid-drive
  - cargo
  - smart-system
  - 85nm
generated_by: cargo-bikes-cli
peak_torque_nm: 85
nominal_power_w: 250
weight_kg: 3.6
speed_limit_kmh: 25
cadence_range_rpm: 10–120
drive_type: mid-drive
platform: Smart System
variants:
  - Cargo Line (25 km/h)
  - Cargo Line Speed (45 km/h)
---

# Bosch Cargo Line

The Bosch Cargo Line is a mid-drive motor purpose-built for cargo bikes and heavy-load e-bikes. Introduced at Eurobike 2021 and shipping on production bikes from the 2022 model year, it is the first dedicated cargo motor in [[Bosch]]'s lineup and runs exclusively on the Smart System (Gen 4) platform. It is designed for sustained torque delivery under heavy payloads, distinguishing it from the sport-focused Performance Line CX.

## Variants

| Variant          | Speed Limit | Regulatory Class |
| ---------------- | ----------- | ---------------- |
| Cargo Line       | 25 km/h     | Pedelec          |
| Cargo Line Speed | 45 km/h     | S-Pedelec        |

## Specifications

| Spec          | Cargo Line   | Cargo Line Speed |
| ------------- | ------------ | ---------------- |
| Nominal power | 250 W        | 250 W            |
| Peak torque   | 85 Nm        | 85 Nm            |
| Speed limit   | 25 km/h      | 45 km/h          |
| Weight        | ~3.6 kg      | ~3.9 kg          |
| Drive type    | Mid-drive    | Mid-drive        |
| Cadence range | 10–120 RPM   | 10–120 RPM       |
| Platform      | Smart System | Smart System     |

_Weights are approximate; exact gear reduction ratio is not published by Bosch._

## Assist Modes

- Eco
- Tour
- Sport
- Turbo

Walk assist is included as standard across all Smart System motors.

## Smart System Compatibility

### Batteries (PowerTube)

- PowerTube 400
- PowerTube 500
- PowerTube 600
- PowerTube 750
- Dual battery configurations via the DualBattery adapter

### Displays and Controls

- Kiox 300
- Kiox 500
- Purion 200
- Nyon (2nd gen)
- LED Remote

Smart System components communicate over a proprietary CAN bus and are not backward-compatible with older Bosch Classic/Gen 3 systems.

## Notable Features

- OTA firmware updates via the Bosch eBike Flow app
- Bluetooth connectivity (Smart System)
- eShift compatibility (electronic gear coordination)
- Automatic shifting integration with Enviolo and Shimano STEPS
- Smart System lock/anti-theft functionality via app
- Extended Range mode for conservative battery management
- Reinforced internals for sustained heavy-load use

## Bikes Using This Component

- [[Cube Longtail Hybrid 800]]
- [[Cube Longtail Hybrid Comfort 800]]
- [[Cube Longtail Hybrid Comfort Family 800]]
- [[Cube Longtail Hybrid Family 800]]
- [[Boda Boda]]
- [[Spicy Curry+]]
- [[Spicy Curry]]

## Comparison: Cargo Line vs. Performance Line CX

| Feature       | Cargo Line                  | Performance Line CX              |
| ------------- | --------------------------- | -------------------------------- |
| Primary use   | Cargo bikes, heavy loads    | MTB, sport, gravel               |
| Peak torque   | 85 Nm                       | 85 Nm                            |
| Weight        | ~3.6 kg                     | ~2.9 kg                          |
| eMTB mode     | No                          | Yes                              |
| Boost mode    | No                          | Yes                              |
| Motor tuning  | Low cadence, sustained load | High cadence, dynamic response   |
| Frame mounts  | Cargo-specific              | Standard MTB/road                |
| Speed variant | Cargo Line Speed (45 km/h)  | Performance Line Speed (45 km/h) |
| Platform      | Smart System                | Smart System                     |

The Cargo Line prioritises continuous torque at low cadences for laden cargo bikes; the Performance Line CX is tuned for high-cadence, burst-power trail riding. The Cargo Line also uses a wider Q-factor to suit cargo frame geometry and has reinforced gearing for sustained heavy-load stress.

## See Also

- [[Bosch]]
- [[Motors MOC]]
