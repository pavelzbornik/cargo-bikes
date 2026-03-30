---
title: Bosch
type: component-manufacturer
category: motors
parent: '[[Motors MOC]]'
domain: '[[Motors MOC]]'
tags:
- motor-manufacturer
- mid-drive
- bosch
- smart-system
- cargo-line
- ebike-systems
generated_by: cargo-bikes-cli
headquarters: Reutlingen, Germany
founded: 1886
ebike_division: Bosch eBike Systems
system_generations:
- Smart System (current)
- Legacy System (prior to ~2022)
motor_lineup:
- Cargo Line
- Cargo Line Speed
- Performance Line CX Gen 5
- Performance Line PX
- Performance Line Speed
- Performance Line SX
- Performance Line
max_torque_nm: 100
max_assist_ratio_pct: 400
max_battery_wh: 800
dual_battery_max_wh: 1600
---
# Bosch

Bosch eBike Systems is a division of Robert Bosch GmbH and the dominant mid-drive motor supplier in the premium cargo and utility e-bike segment. Based in Reutlingen, Germany, Bosch has been producing e-bike drive systems since 2011. Their current platform — the **Smart System** — connects all drive components over a shared data bus, enabling OTA firmware updates, app-unlockable performance tiers, and deep integration with displays, ABS, and electronic shifting.

## Motor Lineup

Bosch's cargo-relevant motors span two families: the purpose-built **Cargo Line** for heavy-duty utility use, and the **Performance Line** range for higher-performance applications. All current motors are Smart System only.

### Cargo Line

The primary motor for cargo bikes. Engineered for a permissible total system weight of up to **250 kg**, making it the standard choice for longtails, box bikes, and family cargo bikes.

| Spec | Value (shipped) | After App Unlock (MY2026+) |
|---|---|---|
| Max torque | 85 Nm | 100 Nm |
| Peak power | 600 W | 750 W |
| Max assist ratio | 340% | 400% |
| Assist cutoff | 25 km/h | 25 km/h |
| Weight | ~2.8 kg | — |

Key features:
- Dedicated Cargo mode with smooth low-speed power delivery under heavy load
- Motor and gearbox decouple above ~20 mph to reduce drag at speed
- Hill Start Assist holds the bike stationary on inclines during start-up
- Smart Walk Assist with Hill Hold (prevents rollback when engaging walk mode)
- DualBattery support (two PowerTube 800s = 1,600 Wh)
- ABS Cargo compatible

### Cargo Line Speed

S-Pedelec variant of the Cargo Line tuned for 45 km/h assist cutoff. Shares the same motor platform and torque/power figures as the standard Cargo Line after the MY2026 update. Used on speed pedelec cargo bikes requiring Class 3 / S-Pedelec compliance.

### Performance Line CX Gen 5 (2025)

Bosch's flagship high-performance motor, widely specified on longtails and high-end cargo bikes alongside pure eMTB applications.

| Spec | Value (shipped) | After App Unlock (from July 2025) |
|---|---|---|
| Max torque | 85 Nm | 100 Nm |
| Peak power | 600 W | 750 W |
| Max assist ratio | 340% | 400% |
| Weight | 2.7 kg | — |
| Casing | Magnesium | — |

Gen 5 improvements over Gen 4:
- 6-axis inertial sensor suite (gradient, inclination, vibration detection)
- Significantly quieter operation — drivetrain decouples under zero load
- Enhanced Extended Boost for steep short climbs
- 100 g lighter than Gen 4
- OTA performance unlock went live July 2025

### Performance Line PX (MY2026)

New touring-focused motor announced at Eurobike 2025. Slots between the standard Performance Line and CX Gen 5 in the lineup.

| Spec | Value |
|---|---|
| Max torque | 90 Nm |
| Peak power | 700 W |
| Max assist ratio | 400% |
| Weight | ~2.9 kg |

Features a two-stage gearbox (vs CX's three-stage) optimized for quiet, smooth operation. Includes an Auto mode for automatic assistance selection. Compatible with Shimano, TRP, and Magura ABS brakes.

### Performance Line Speed (MY2026)

S-Pedelec motor for 45 km/h bikes.

- 100 Nm torque, 750 W peak, 400% assist
- 30% reduction in pedaling resistance compared to predecessor
- New Limit mode caps assist at 25 km/h for shared or restricted spaces
- 100 g weight reduction

### Performance Line (MY2026)

Urban/trekking motor, entry point for Smart System performance range.

- 75 Nm torque, 600 W peak, 340% assist
- Weight reduced to 2.8 kg (400 g savings vs predecessor)
- Redesigned smaller housing

### Performance Line SX

Compact lightweight motor for XC and short-travel applications; occasionally specified on lightweight cargo designs.

- 60 Nm torque (up from 55 Nm via OTA update, MY2026)
- 400% assist
- ~2.0 kg — lightest in Smart System lineup
- eMTB+ mode added via OTA

## Battery Options

All Smart System batteries support DualBattery pairing (two batteries operated in parallel). Cells are 21700 format.

### PowerTube (frame-integrated)

| Model | Capacity | Weight | Notes |
|---|---|---|---|
| PowerTube 540 | 540 Wh | 3.0 kg | New MY2026; same dimensions as 600 |
| PowerTube 600 | 600 Wh | 3.0 kg | Current mid-range; interchangeable with 800 in compatible frames |
| PowerTube 800 | 800 Wh | 3.9 kg | Current flagship; 400 g lighter than prior 750 Wh model |
| PowerTube 500 | 500 Wh | — | Legacy; still present on in-stock/pre-owned bikes |

Two PowerTube 800s in DualBattery configuration deliver **1,600 Wh**.

### PowerPack (external/rack-mounted)

| Model | Capacity | Notes |
|---|---|---|
| PowerPack 800 | 800 Wh | Largest PowerPack; external frame or rack mount |
| PowerPack 300 Frame | ~300 Wh | Lightweight external mount option |

Battery Lock (digital anti-theft immobilization) introduced MY2026.

## Displays and Controllers

All Smart System units connect to the **eBike Flow** app (iOS/Android) for configuration, navigation, and OTA updates. Legacy system units use the older eBike Connect app.

| Unit | Screen | Notes |
|---|---|---|
| LED Remote | None (LEDs only) | Minimal bar controller; pairs with smartphone via Flow app |
| Purion 200 | Compact monochrome | Single-thumb handlebar control |
| Purion 400 | 1.6" with speaker | Stem or bar mount (31.8 / 35 mm); requires remote pairing; retrofit available |
| Kiox 300 | 2.0" color | Removable; eShift gear display; Flow app |
| Kiox 500 | 2.8" color | Larger removable display; eShift support |
| Nyon | Large color LCD + touch | Full navigation; multi-rider profiles; WiFi/BT OTA |
| SmartphoneGrip | User's phone | Pairs with Kiox 300 as display; suited to relaxed riding positions |

## Key Technologies

### Smart System vs Legacy

The **Smart System** (broadly rolled out from MY2023) is Bosch's current platform. All components share a single data bus, enabling OTA firmware updates and unlockable performance. ABS, eShift, and Auto modes are Smart System exclusive. **Legacy system** motors (CX Gen 4 and earlier, older Performance Line) use the eBike Connect app and do not support performance unlocks — these remain common on pre-owned and clearance-priced bikes.

### ABS

Bosch's ABS is integrated into the Smart System motor unit (no separate wheel sensors in the newer design). Four variants are available:

- **ABS Cargo** — calibrated for heavy loads and shifted weight distribution; the relevant variant for cargo bikes
- **ABS Touring** — general urban/touring use
- **ABS Trail** — off-road with toggleable Trail and All-Road modes (Kiox 300 required)
- **ABS Trail Pro** (MY2025) — enduro use; permits controlled rear wheel liftoff

Compatible brake brands as of MY2026: Magura, TRP, and Shimano.

### eMTB Mode

Continuously adaptive assist mode that varies output between Tour and Turbo levels based on terrain and rider input — no manual mode switching. Available on CX Gen 5, CX-R, and SX motors. The CX-R adds eMTB+.

### eShift (Electronic Gear Integration)

Motor cadence and torque data trigger automatic or semi-automatic gear changes. Compatible with Shimano XTR Di2, Deore XT Di2, and TRP derailleurs (MY2026 expansion). Current gear displayed on Kiox 300/500.

### Extended Boost

Short-duration power amplification for steep or technical sections. Enhanced in CX Gen 5.

### Walk Assist / Smart Walk Assist

Propels the bike at ~6 km/h walking pace. Smart System version adds Hill Hold to prevent rearward rollback on inclines when engaging the feature — particularly useful on heavy loaded cargo bikes.

## Market Position

Bosch is the reference-standard mid-drive motor in the premium European cargo bike segment. The Cargo Line motor's 250 kg GVW rating, dedicated Cargo mode, DualBattery support, Hill Start Assist, and ABS Cargo variant differentiate it from general-purpose drive systems. Key competitors are [Shimano](/components/motors/shimano.md) (EP8/EP801, strong in eMTB and increasingly in cargo), [[Yamaha]] (PW-Series, consumer/mid-market), and [[Brose]] (OEM supply to select brands).

## Bikes Using This Manufacturer

- [Benno Boost 10D EVO 5 500Wh](/bikes/benno/boost-10d-evo-5.md)
- [Benno Boost E EVO4 500Wh](/bikes/benno/boost-e-evo4.md)
- [Benno eJoy E](/bikes/benno/ejoy-e.md)
- [Bike43 Short](/bikes/bike43/short.md)
- [Cube Longtail Hybrid 800](/bikes/cube/longtail-hybrid-800.md)
- [Cube Longtail Hybrid Comfort 800](/bikes/cube/longtail-hybrid-comfort-800.md)
- [Cube Longtail Hybrid Comfort Family 800](/bikes/cube/longtail-hybrid-comfort-family-800.md)
- [Cube Longtail Hybrid Family 800](/bikes/cube/longtail-hybrid-family-800.md)
- [Boda Boda](/bikes/yuba/boda-boda.md)
- [Spicy Curry+](/bikes/yuba/spicy-curry-plus.md)
- [[Urban Arrow Family]] (Cargo Line)
- [[Riese & Muller Load]] (Cargo Line / DualBattery)
- [[Tern GSD]] (Smart System)
- And others across Gazelle, Yuba, and Babboe ranges

## Notable OEM Partners (Cargo Segment)

| Brand | Models |
|---|---|
| [Urban Arrow](/bikes/urban-arrow/index.md) | Family, Shorty, Tender — all Cargo Line |
| [Riese & Müller](/bikes/riese-muller/index.md) | Load, Carrie, Packster — Cargo Line, DualBattery |
| [Tern](/bikes/tern/index.md) | GSD, HSD Gen 2, Orox — Smart System partnership |
| [Cube](/bikes/cube/index.md) | Longtail Hybrid range — Cargo Line |
| [Yuba](/bikes/yuba/index.md) | Longtail range |
| [[Gazelle]] | Utility and cargo range |
| [[Babboe]] | Dutch box bikes with Bosch options |
| [[Benno]] | Boost and Carry-E range |

## Update History (Selected)

| Period | Update |
|---|---|
| MY2023 | Smart System broad rollout begins |
| Sept 2024 | PowerTube 600 and PowerTube 800 announced |
| Oct/Nov 2024 | Purion 400 retrofit availability |
| Early 2025 | Performance Line CX Gen 5 announced |
| Mid 2025 | Cargo Line MY2026 update: 100 Nm / 750 W unlockable |
| July 2025 | CX Gen 5 app unlock goes live |
| Eurobike June 2025 | CX-R, Performance Line PX, Kiox 400C, PowerTube 540, Shimano ABS, Battery Lock announced |
| Fall 2025 | First CX-R bikes at dealers; SX OTA torque increase (55 Nm to 60 Nm) |
