---
title: "{{title}}"
type: bike
brand: "{{brand}}"
model: "{{model}}"
tags: [bike, { { bike-type } }, { { brand-lowercase } }]
date: { { YYYY-MM-DD } }
url: "{{product_url}}"
image: "{{bike_image_url}}"
resellers:
  - name: "{{reseller_name}}"
    url: "{{reseller_url}}"
    price: { { price_amount } }
    currency: "{{currency_code}}"
    region: "{{region}}"
    availability: "in-stock"
    note: ""
specs:
  category: "{{longtail|box|trike|etc}}"
  model_year: { { year } }
  frame:
    material: "{{aluminum|steel|carbon}}"
    size: "{{one size|size range}}"
  weight:
    with_battery_kg: { { weight_with_battery } }
    bike_kg: null
  load_capacity:
    total_kg: { { total_capacity } }
    rear_kg: { { rear_capacity } }
    passenger_count_excluding_rider: { { number } }
    passenger_config: "{{description}}"
  motor:
    make: "{{motor_brand}}"
    model: "{{motor_model}}"
    type: "{{mid-drive|rear-hub|front-hub}}"
    power_w: { { watts } }
    torque_nm: { { torque } }
    boost_throttle: { { true|false } }
  battery:
    capacity_wh: { { wh } }
    configuration: "{{single|dual}}"
    removable: { { true|false } }
    charging_time_h: { { hours } }
  drivetrain:
    type: "{{chain|belt}}"
    speeds: { { number|range } }
    hub: "{{hub_model|null}}"
  brakes:
    type: "{{brake_type}}"
    front_rotor_mm: { { mm } }
    rear_rotor_mm: { { mm } }
  wheels:
    front_size_in: '{{size}}"'
    rear_size_in: '{{size}}"'
    tire: "{{tire_model}}"
  suspension:
    front: "{{description|none}}"
    rear: "{{description|none}}"
  lights:
    front:
      type: "{{description}}"
      integrated: { { true|false } }
      powered_by: "{{main battery|dynamo}}"
    rear:
      type: "{{description}}"
      integrated: { { true|false } }
      brake_light: { { true|false } }
  features: [{ { hyphen-separated-tags } }, { { include-motor-brand } }]
  security:
    gps: { { true|false } }
    frame_lock: { { true|false } }
    app_lock: { { true|false } }
  range:
    estimate_km: { { number|range } }
    notes: "{{assist level, load, conditions}}"
  price:
    amount: { { price_amount } }
    currency: "{{currency_code}}"
  notes: "{{optional general notes}}"
---

## {{title}}

![{{title}}]({{image}})

## Overview

Brief description of the bike's purpose, positioning in the cargo bike market, and key value proposition.

## Technical Specifications

### Dimensions & Weight

- **Frame material:** {{material}}
- **Frame size:** {{size}}
- **Dimensions:** {{length_cm}}L × {{width_cm}}W × {{height_cm}}H cm
- **Weight:** {{with_battery_kg}} kg (with battery), {{bike_kg}} kg (frame only)
- **Load capacity:** {{total_kg}} kg total ({{passenger_config}})

### Motor & Power

- **Motor:** {{make}} {{model}} ({{type}})
- **Power:** {{power_w}}W
- **Torque:** {{torque_nm}} Nm
- **Throttle/Walk assist:** {{yes|no}}

### Battery & Range

- **Capacity:** {{capacity_wh}} Wh ({{configuration}})
- **Removable:** {{yes|no}}
- **Charging time:** {{charging_time_h}} hours
- **Estimated range:** {{estimate_km}} km ({{range_notes}})

### Drivetrain & Gears

- **Type:** {{chain|belt}}
- **Speeds:** {{speeds}}
- **Hub:** {{hub_model|internal gears|none}}

### Brakes

- **Type:** {{brake_type}}
- **Rotors:** {{front_rotor_mm}}mm front / {{rear_rotor_mm}}mm rear

### Wheels & Tires

- **Sizes:** {{front_size_in}} front / {{rear_size_in}} rear
- **Tires:** {{tire_model}}
- **Suspension:** {{suspension_front}} front / {{suspension_rear}} rear

### Lighting & Safety

- **Front light:** {{front_type}} ({{front_powered_by}})
- **Rear light:** {{rear_type}} (brake-light: {{brake_light}})
- **GPS tracker:** {{yes|no}}
- **Alarm:** {{db_level}} dB (if equipped)
- **App lock:** {{yes|no}}

## E-bike Features

- **Assist levels:** {{number|description}}
- **Display:** {{type|integrated|smartphone app}}
- **Security features:** {{list features}}
- **Weather resistance:** {{rating|description}}
- **Connectivity:** {{bluetooth|app integration|cloud features}}

## Real-world Performance

### Range & Power

- Typical range in city/mixed terrain
- Performance in hills
- Winter range impact
- Motor responsiveness and acceleration

### Comfort & Handling

- Riding position and ergonomics
- Suspension/shock absorption (if equipped)
- Noise levels
- Ease of mounting/dismounting

### Cargo Stability

- Rear rack stability with loads
- Weight distribution with passengers
- Turning radius and maneuverability

## Cost & Accessories

### Base Price

- {{currency}} {{price}} (manufacturer's suggested retail price)

### Recommended Accessories for 2-Child Transport

| Accessory            | Price         | Notes                               |
| -------------------- | ------------- | ----------------------------------- | ------- |
| Child seat (rear)    | {{price}}     | {{model                             | brand}} |
| Child seat (rear)    | {{price}}     | {{model                             | brand}} |
| Harness/safety kit   | {{price}}     | {{description}}                     |
| Cargo net/straps     | {{price}}     | For additional security             |
| Rain cover           | {{price}}     | Protection for cargo and passengers |
| **Total investment** | **{{total}}** | Including bike and essentials       |

## Cargo Capacity & Use Cases

- **Typical loads tested:** {{description}}
- **Child seat compatibility:** {{number}} children, seat models
- **Commuting:** {{suitable|considerations}}
- **Configurations:** {{rear rack|front basket|both|side carriers}}

## Maintenance

- **Battery maintenance:** {{expectations|lifespan}}
- **Motor service:** {{intervals|typical costs}}
- **Brake maintenance:** {{pads|rotors|service intervals}}
- **Tire care:** {{pressure|replacement intervals}}

## Modifications & Customization

- **Upgrade options:** {{available motor configs|battery upgrades}}
- **Common user modifications:** {{examples}}
- **Third-party accessory compatibility:** {{list}}

## User Reviews & Experiences

### Community Feedback

#### Pros

- {{advantage1}}
- {{advantage2}}
- {{advantage3}}

#### Cons

- {{drawback1}}
- {{drawback2}}
- {{drawback3}}

#### User Quotes

> "User experience quote here"
> — User name/handle

## Photos & Media

- Link to official photo gallery
- Video reviews or demonstrations
- Community photos/content

## Professional Reviews

- Link to reviews from cycling publications
- Links to YouTube reviews or tests
- Expert recommendations

## References

- Official product page: {{url}}
- Technical specifications PDF: {{pdf_link}}
- Professional reviews:
- Community forums/discussions:
- Related comparisons:
