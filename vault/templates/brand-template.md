---
title: "{{brand_name}}"
type: "brand"
brand: "{{brand_name}}"
tags: [brand, "{{country_code}}", "{{bike_types}}", "{{primary_features}}"]
date: "{{YYYY-MM-DD}}"
url: "{{official_website_url}}"
logo: "{{logo_filename_or_url}}"
summary: "{{one_sentence_brand_positioning}}"

# Brand Identity
founded_year: { { year } }
country: "{{country}}"
headquarters:
  city: "{{city}}"
  country: "{{country}}"
  address: "{{full_address_optional}}"

# Market Positioning
categories: ["{{primary_category}}", "{{secondary_category}}"]
market_segments: ["{{segment_1}}", "{{segment_2}}"]
regions: ["{{region_1}}", "{{region_2}}"]
price_tier: "{{entry-level|accessible|mid-premium|premium|ultra-premium}}"

# Product Portfolio
product_types: ["{{type_1}}", "{{type_2}}"]
model_count: { { number_of_models } }
primary_motors: ["{{motor_brand_1}}", "{{motor_brand_2}}"]
parent_company: "{{parent_company_name_if_applicable}}"
manufacturing:
  locations: ["{{country_1}}", "{{country_2}}"]
  approach: "{{in-house|contracted|hybrid}}"
  assembly_location: "{{country}}"
  ethical_standards: "{{certification_or_commitment}}"

# Distribution
distribution_model: "{{direct|retail|both}}"
regions_active: ["{{region_1}}", "{{region_2}}"]
direct_sales: { { true|false } }
dealership_network: { { true|false } }

# Key Metrics (if available)
impact:
  bikes_sold_approx: { { number } }
  km_driven_approx: { { number } }
  co2_avoided_kg_approx: { { number } }
  families_served: { { number } }

# Accessibility & Values
accessibility:
  - "{{value_1}}"
  - "{{value_2}}"
values:
  sustainability: { { true|false } }
  local_manufacturing: { { true|false } }
  community_focus: { { true|false } }
  safety_emphasis: { { true|false } }
  tech_integration: { { true|false } }
---

## Overview

**Who they are:** {{one_paragraph_about_brand_origin_and_founders}}

**What makes them different:** {{one_paragraph_about_unique_value_proposition_not_tech_specs}}

{{optional_additional_context_about_market_position_or_expansion}}

**Sources:** {{primary_source}}, {{secondary_source}}

## Target Market & Positioning

This brand appeals to: {{description_of_ideal_customer_profile}}

Key positioning differences from competitors: {{explain_differentiation_strategy}}

## Brand Story & Philosophy

{{Narrative_about_founding_motivation_or_core_mission}}

{{Philosophy_behind_design_decisions_or_manufacturing_approach}}

This approach reflects their belief that {{core_belief_or_value_statement}}.

## Design Language & Innovation

**What sets them apart:**

- {{unique_design_element_or_philosophy}}
- {{manufacturing_or_sourcing_innovation}}
- {{customer_service_or_community_approach}}

**Not covered in individual bike pages:**

- {{Brand-level_innovation_or_approach}}
- {{Broader_product_strategy}}
- {{Accessibility_or_inclusivity_stance}}

## Manufacturing & Sustainability

- **Where bikes are made:** {{manufacturing_locations}}
- **Sourcing approach:** {{component_sourcing_strategy}}
- **Environmental commitment:** {{sustainability_practices}}
- **Social responsibility:** {{workers_or_community_initiatives}}

## Product Strategy

**Market segments served:** {{description_of_model_tiers_or_categories}}

**How models differ:** {{explanation_of_segmentation_logic}} (Not: "see individual bike pages for specs")

**Development philosophy:** {{approach_to_innovation_or_customization}}

## Community & Customer Relationship

- **How customers interact with brand:** {{distribution_model_emphasis}}
- **Customer support approach:** {{customer_service_philosophy}}
- **Community engagement:** {{how_brand_builds_loyalty}}
- **Regional focus:** {{primary_vs_secondary_markets}}

## Business Model Insights

- **Direct vs. retail:** {{sales_channel_strategy}}
- **Build-to-order vs. stock:** {{fulfillment_model}}
- **Pricing strategy:** {{premium_accessible_or_value}}
- **Customization options:** {{how_customers_personalize_bikes}}

## Related Brands & Comparisons

**Similar brands to compare:** {{brands_with_similar_positioning}}

**Key differences from [Brand X]:** {{comparison_that_helps_users_understand_market}}

## Resources & Further Research

- **Official Website:** {{url}}
- **Key Pages:** {{product_pages_or_resources}}
- **Contact:** {{sales_or_press_contact}}

**Where to find more info:**

- Individual bike pages for technical specifications and detailed reviews
- [BIKE_SPECS_SCHEMA.md](../../schema/BIKE_SPECS_SCHEMA.md) for standardized specification fields

## Notes for Contributors

**What to include in this page:** Brand story, philosophy, market positioning, manufacturing practices, what makes them unique beyond specifications.

**What NOT to duplicate:** Technical specs (see individual bike pages), detailed component lists, performance comparisons, user reviews (see bike pages).

**Keep in mind:** This page should answer "Who is this brand and why do they matter?" not "What are the specs of each bike?" The individual bike pages handle that.
