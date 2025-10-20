# Bike Frontmatter Schema

This document defines the recommended YAML frontmatter structure for all bike notes in the vault. Adhering to this schema ensures that metadata is consistent, machine-readable, and easy to use for automation, such as with `scripts/generate_bike_table.py`.

---

## YAML Schema

The schema is divided into two parts: top-level fields common to every bike note, and a nested `specs` mapping for detailed technical data.

### Top-level Fields

These fields should appear at the root level of the frontmatter.

```yaml
title: string # (Required) The full, human-readable name of the bike.
type: string # (Required) The type of this note, almost always 'bike'.
brand: string # The manufacturer's name, e.g., "Tern".
model: string # The specific model name, e.g., "GSD S10".
tags: list[string] # A list of relevant tags for searching and linking.
url: string # The official product URL from the manufacturer's website.
image: string # A link to a primary image of the bike.
resellers: # A list of places where the bike can be purchased.
  - name: string # The name of the reseller or store.
    url: string # A direct URL to the bike's listing on the reseller's site.
    price: number or string # The listed price. Use a string for ranges like "from 4999".
    currency: string # The currency code, e.g., "USD", "EUR".
    region: string # The geographical region, e.g., "EU", "North America".
    availability: string # Stock status, e.g., "in-stock", "pre-order", "out-of-stock".
    note: string # Any additional notes about this specific reseller listing.
```

### The `specs` Mapping

All detailed technical specifications are nested under the `specs` key.

```yaml
specs:
  category: string # The bike's primary classification, e.g., "longtail", "box", "trike".
  model_year: number # The release year of this specific model, e.g., 2024.
  frame:
    material: string # The primary frame material, e.g., "aluminum", "steel".
    size: string or number # Frame size options, e.g., "one size", "48cm".
    dimensions: # Overall physical dimensions of the bike.
      length_cm: number # Total length in centimeters.
      width_cm: number # Total width (usually handlebars) in centimeters.
      height_cm: number # Total height in centimeters.
  weight: # Bike weight specifications. Prefer 'with_battery_kg' if only one value is known.
    bike_kg: number # Weight of the bike without the battery in kilograms.
    with_battery_kg: number # Total weight with the battery installed, in kilograms.
    battery_kg: number # Weight of a single battery in kilograms.
  load_capacity:
    total_kg: number # Maximum total weight capacity, including rider, passengers, and cargo.
    rear_kg: number # Maximum weight capacity of the rear rack.
    front_kg: number # Maximum weight capacity of the front rack/area.
    passenger_count_excluding_rider: integer # Max number of passengers (e.g., children).
    passenger_config: string # Human-readable summary, e.g., "2 children on rear", "1 adult passenger".
  motor:
    make: string # The brand of the motor, e.g., "Bosch", "Shimano", "Bafang".
    model: string # The specific model of the motor, e.g., "Performance Line CX".
    type: string # Motor placement type, e.g., "mid-drive", "rear-hub", "front-hub".
    power_w: number or string # Motor power in watts, e.g., 250 or "250W continuous".
    torque_nm: number # Maximum motor torque in Newton-meters.
    boost_throttle: boolean # True if the bike has a throttle or walk-assist boost button.
    options: list[object] # Use if multiple motor configurations are offered. Each object can contain model, power_w, etc.
  battery:
    capacity_wh: number # The capacity of a single battery in watt-hours.
    configuration: string # Describes the battery setup, e.g., "single", "dual (500+400)", "integrated".
    removable: boolean # True if the battery can be easily removed for charging.
    charging_time_h: number or string # Time for a full charge in hours, e.g., 6 or "3-5".
  drivetrain:
    type: string # The type of drivetrain, e.g., "chain", "belt".
    speeds: string or integer # Number of gears, e.g., 10 or "10-speed".
    hub: string # The internal gear hub model if applicable, e.g., "Enviolo", "Shimano Nexus 5".
  brakes:
    type: string # Brake system type, e.g., "hydraulic disc", "mechanical disc".
    front_rotor_mm: number # Diameter of the front brake rotor in millimeters.
    rear_rotor_mm: number # Diameter of the rear brake rotor in millimeters.
    pistons: string or number # Number of pistons in the brake calipers, e.g., 4 or "4-piston".
  wheels:
    front_size_in: string # Diameter of the front wheel in inches, e.g., "20\"".
    rear_size_in: string # Diameter of the rear wheel in inches, e.g., "24\"".
    tire: string # The model and/or size of the tires, e.g., "Schwalbe Big Ben Plus 2.15\"".
    rims: string # Details about the wheel rims.
  suspension:
    front: string # Description of front suspension, e.g., "80mm fork", "none".
    rear: string # Description of rear suspension, e.g., "shock absorber", "none".
  lights: # Details about the integrated lighting system.
    front:
      type: string # Description of the front light, e.g., "LED 180 lm", "Supernova M99".
      integrated: boolean # True if hard-wired into the bike's electrical system.
      powered_by: string # Power source, e.g., "main battery", "dynamo".
      optional_kits: list[string] # List of any official lighting upgrade kits.
    rear:
      type: string # Description of the rear light.
      integrated: boolean # True if hard-wired into the bike's electrical system.
      brake_light: boolean # True if the light brightens upon braking.
      optional_kits: list[string]
    turn_signals:
      integrated: boolean # True if turn signals are part of the bike's system.
      type: string # Description, e.g., "handlebar end LEDs", "rear rack indicators".
      left_right_buttons: boolean # True if dedicated handlebar controls are present.
  features: list[string] # A list of notable features as short, hyphen-separated tags for searchability.
  security:
    gps: boolean # True if the bike includes a GPS tracker.
    alarm_db: number # The volume of the integrated alarm in decibels.
    app_lock: boolean # True if the bike can be electronically locked via a mobile app.
    frame_lock: boolean # True if a cafe lock (wheel lock) is included.
  range:
    estimate_km: string or number # The manufacturer's estimated range in kilometers, e.g., 120 or "60-150".
    notes: string # Any context for the range estimate, e.g., "eco mode, no load".
  price: # Manufacturer's Suggested Retail Price (MSRP).
    amount: number or string # The base price amount.
    currency: string # The currency code, e.g., "USD", "EUR".
  notes: string # General free-form notes about the bike's specifications.
```

---

### Notes on Usage

- **Use Numbers:** Use numeric values (e.g., `250`) instead of strings (e.g., `"250W"`) where possible to make filtering and sorting easier. The key name (e.g., `power_w`) already defines the unit.
- **Features Tags:** Keep items in the `features` list as short, hyphen-separated tags (e.g., `dual-battery-option`, `bosch-smart-system`) for better searchability.
- **Missing Data:** Use `null` for fields where data is applicable but currently unknown. Omit optional fields entirely if they do not apply to the bike (e.g., don't include a `suspension` section if the bike is fully rigid).
- **Backward Compatibility:** If you are updating an old note, you can preserve legacy top-level fields (e.g., a top-level `motor` key). Prefer adding the new `specs:` structure rather than immediately removing old keys to maintain compatibility.

---

### Example

Here is a complete example in a fenced YAML block to avoid markdown linting issues.

```yaml
---
title: "Trek Fetch+ 2"
type: bike
brand: "Trek"
model: "Fetch+ 2"
date: 2024-10-16
tags: [bike, longtail, electric, trek, bosch]
url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/p/41913/"
image: "trek-fetch-2.jpg"
resellers:
  - name: "Trek Official Store"
    url: "https://www.trekbikes.com/us/en_US/bikes/electric-bikes/electric-cargo-bikes/fetch-2/p/41913/"
    price: 5999
    currency: "USD"
    region: "North America"
    availability: "in-stock"
specs:
  category: "longtail"
  model_year: 2024
  frame:
    material: "aluminum"
    size: "one size"
  weight:
    bike_kg: null
    with_battery_kg: 31
  load_capacity:
    total_kg: 200
    rear_kg: 80
    passenger_count_excluding_rider: 2
    passenger_config: "2 children on rear rack"
  motor:
    make: "Bosch"
    model: "Performance Line CX"
    type: "mid-drive"
    power_w: 250
    torque_nm: 85
  battery:
    capacity_wh: 500
    configuration: "single"
    removable: true
  drivetrain:
    type: "chain"
    speeds: "10-speed"
  brakes:
    type: "hydraulic 4-piston disc"
  wheels:
    front_size_in: '20"'
    rear_size_in: '20"'
    tire: "Schwalbe Pick-Up"
  suspension:
    front: "none"
    rear: "none"
  lights:
    front:
      type: "180 lumen LED"
      integrated: true
      powered_by: "main battery"
    rear:
      type: "integrated rear brake light"
      integrated: true
      brake_light: true
  features: ["bosch-smart-system", "integrated-lights", "stable-kickstand"]
  security:
    frame_lock: true
  range:
    estimate_km: "50-120"
    notes: "Depends on assist level and conditions"
  price:
    amount: 5999
    currency: "USD"
---
```
