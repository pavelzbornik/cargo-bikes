---
title: Naka E-Power Max (Ananda M100)
type: component-manufacturer
category: motors
parent: "[[Motors MOC]]"
domain: "[[Motors MOC]]"
generated_by: cargo-bikes-cli
tags:
  - motor
  - mid-drive
  - ananda
  - naka-e-power-max
  - cargo-bike
  - intersport
  - nakamura
motor_type: Mid-drive
oem_base: Ananda M100
rated_power_w: 250
peak_torque_nm: 100
voltage: 48V
sensor_type: Torque + Cadence
max_efficiency_pct: ">= 80"
noise_db: < 55
waterproof: IPX5
operating_temp: -20 to 55 C
shaft_standard: JIS / ISIS
weight_kg: 3.5
certifications:
  - CE
  - EN 15194
  - RoHS
  - REACH
---

## Naka E-Power Max (Ananda M100)

## Overview

The **Naka E-Power Max** is [[Nakamura]]'s branded denomination for a mid-drive motor system built on the **[[Ananda]] M100** platform. Ananda Drive Techniques (Shanghai) is one of China's largest e-bike motor manufacturers and a significant OEM supplier to European brands. The M100 is their flagship high-torque mid-drive unit, positioned as a direct competitor to [[Bosch]] Performance Line Cargo and [[Shimano]] EP8 in the longtail and cargo segment.

Nakamura — the Intersport house brand — sources this motor for its cargo-oriented models where the branding appears as "Naka E-Power Max," while the underlying hardware remains the standard Ananda M100. The motor operates with an integrated torque and cadence sensor combination, delivering natural, responsive pedal assist.

## Technical Specifications

| Parameter             | Value                          |
| --------------------- | ------------------------------ |
| Motor type            | Mid-drive                      |
| Rated power           | 250 W (EU-legal configuration) |
| Peak torque           | 100–110 Nm                     |
| Voltage               | 48 V DC                        |
| Sensor system         | Integrated torque + cadence    |
| Max efficiency        | >= 80%                         |
| Noise level           | < 55 dB                        |
| Waterproofing         | IPX5                           |
| Operating temperature | -20 to +55 C                   |
| Shaft standard        | JIS / ISIS                     |
| Motor weight          | ~3.5 kg                        |
| Communication         | UART / CAN                     |
| E-brake input         | Yes                            |
| Gear sensor support   | Yes                            |

> Specs sourced from Ananda Drive official product page and the Ananda eBike Systems Catalogue 2024. The 100 Nm figure is specific to the Nakamura implementation; the base M100 platform is available in 110/120/130 Nm variants depending on configuration.

## Product Range Context

The Ananda M100 is available across a spectrum of power and torque configurations:

| Variant       | Rated Power | Peak Torque | Weight |
| ------------- | ----------- | ----------- | ------ |
| M100 Standard | 250 W       | 110 Nm      | 3.5 kg |
| M100 Mid      | 350 W       | 120 Nm      | 3.9 kg |
| M100 High     | 500 W       | 130 Nm      | 3.9 kg |

The Naka E-Power Max corresponds to the 250 W / ~100–110 Nm configuration, compliant with EU EN 15194 regulations (250 W rated, 25 km/h assist cutoff).

## Cargo-Specific Features

The M100 platform, as deployed on cargo bikes, supports several features relevant to longtail and family cargo use:

- **6 km/h walk-assist / reverse mode** — useful for maneuvering heavy loaded bikes
- **Throttle option** — available depending on OEM configuration (market-dependent)
- **Turn light integration** — signal function support via motor controller
- **NAKA SMART mode** — Nakamura's implementation of adaptive real-time torque modulation responding to pedaling input

## Bikes Using This Motor

| Bike                            | Notes                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| [[Nakamura Crossover Longtail]] | Primary cargo application; dual battery setup (520 Wh + 250 Wh), total payload 170 kg |

## Market Position

The Ananda M100 occupies the **mid-tier to upper-mid-tier** segment of the cargo motor market. It offers torque figures competitive with Bosch Performance Line Cargo (85 Nm) and Shimano EP8 (85 Nm), at a lower system cost — a key reason Intersport/Nakamura adopted it for their longtail offering to keep pricing accessible.

### Comparison to Key Alternatives

| Motor                            | Peak Torque | Rated Power | Notable Advantage                   |
| -------------------------------- | ----------- | ----------- | ----------------------------------- |
| Ananda M100 (Naka E-Power Max)   | 100–110 Nm  | 250 W       | High torque, cost-effective         |
| [[Bosch]] Performance Line Cargo | 85 Nm       | 250 W       | Ecosystem maturity, dealer network  |
| [[Shimano]] EP8                  | 85 Nm       | 250 W       | Smooth power delivery, light weight |
| [[Bafang]] M620                  | 160 Nm      | 250 W       | Very high torque, widely available  |

## Manufacturer Background

**[[Ananda]]** (Ananda Drive Techniques, Shanghai) was founded in 2004 and is headquartered in Shanghai, China. They are one of the world's largest volume producers of e-bike drive systems, supplying OEM motors to brands across Europe and Asia. The M100 mid-drive line is their premium product tier, targeting performance and cargo applications.

- Website: [ananda-drive.com](https://www.ananda-drive.com)
- Certifications: CE, EN 15194, RoHS, REACH

## Sources

- [Ananda M100 — Official Product Page](https://www.ananda-drive.com/products/motor-m100/)
- [Ananda M100 250W 110Nm — Cargo Bike of Sweden](https://cargobikeofsweden.com/en/articles/2.9.481/ananda-m100-motor-250w-110nm)
- [Nakamura Crossover Longtail test — Transition Velo](https://www.transitionvelo.com/test/test-nakamura-crossover-longtail-un-velo-cargo-toute-option-abordable/)
- [Nakamura Crossover Longtail — Cleanrider catalogue](https://www.cleanrider.com/catalogue/velo-electrique/nakamura/nakamura-crossover-longtail/)
- [Naka E-Power app — Velco](https://velco.tech/en/naka-e-power-applicatione-bikes/)
