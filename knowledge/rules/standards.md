---
id: rule_standards
type: rule
name: Material and QA Standards
related:
  - product_trommel_panel
  - product_hydrocyclone
  - rule_design_rules
tags: [standards, qa, testing, inspection, material]
---

# Material and QA Standards

## Polyurethane compound test standards

| Property | Test method | Acceptance |
|---|---|---|
| Hardness | ASTM D2240 (Shore A) | Within ±3 of spec |
| Abrasion resistance | DIN 53516 | Volume loss ≤ 60 mm³ |
| Tensile strength | ASTM D412 | ≥ 30 MPa |
| Tear strength | ASTM D624 | ≥ 50 kN/m |

## Rubber compound test standards

| Property | Test method | Acceptance |
|---|---|---|
| Hardness | ASTM D2240 (Shore A) | Within ±3 of spec |
| Abrasion resistance | DIN 53516 | Volume loss ≤ 120 mm³ |
| Tensile strength | ASTM D412 | ≥ 18 MPa |
| Elongation at break | ASTM D412 | ≥ 400% |

## Incoming QA checks (per batch)

1. Visual inspection — no voids, no cracking, no incomplete cure.
2. Dimensional check — aperture size and panel dimensions within
   tolerance (see `rules/design_rules.md` §"Aperture tolerance").
3. Hardness spot check — 1 panel per 50, or minimum 2 per batch.
4. Fixing component fit check — pins/sleeves seat correctly without
   force.

## Inspection intervals (in-service)

| Equipment | Standard interval | High-wear-zone interval |
|---|---|---|
| Trommel panels | Every 3 months | Every 1 month (feed end / impact zones) |
| Flat screening panels | Every 2 months | Every 1 month (feed end) |
| Hydrocyclone cylinder/cone liner | Every 6 months | — |
| Hydrocyclone apex/spigot liner | Every 6 months | Every 2 months |

## Reporting requirement

Every wear inspection must record: thickness by zone, aperture drift if
measurable, any cracking/pin failure/blinding observed, and a wear-rate
projection to minimum service thickness. See
`customers/customer_001/reports/wear_report_2026_01.md` for an example
of the expected report format.
