---
id: rule_design_rules
type: rule
name: Screening Panel Design Rules
related:
  - product_trommel_panel
  - product_hydrocyclone
  - rule_standards
tags: [design, rules, thickness, tolerance, material, fixing]
---

# Screening Panel Design Rules

## Minimum service thickness

| Panel type | New thickness | Minimum service thickness | Replace at |
|---|---|---|---|
| Trommel panel (PU) | 25–50 mm | 60% of new thickness | 15 mm absolute floor |
| Trommel panel (rubber) | 25–50 mm | 50% of new thickness | 12 mm absolute floor |
| Flat screening panel | 20–40 mm | 50% of new thickness | 10 mm absolute floor |

Below the absolute floor, fixing pins/sleeves are at risk of pull-through
and panels must be replaced regardless of remaining open area.

## Aperture tolerance

| Aperture size | Manufacturing tolerance |
|---|---|
| < 10 mm | ±0.3 mm |
| 10–30 mm | ±0.5 mm |
| 30–80 mm | ±1.0 mm |

Aperture drift beyond tolerance (from wear, not manufacturing) signals
the panel should be scheduled for replacement even if thickness is
otherwise within range, since separation accuracy degrades.

## Material selection rule

1. Default to **polyurethane** for dry, abrasive, high-silica material
   where abrasion (not impact) is the dominant wear mode.
2. Default to **rubber** where impact, large lump size, or cutting wear
   from sharp tramp material dominates.
3. For mixed/variable feed, prefer zoned panels (different material or
   thickness by drum/deck zone) over a single uniform spec.
4. Never select material based on cost alone without checking expected
   wear mode — a cheaper rubber panel in a high-abrasion duty will cost
   more in replacement frequency than a PU panel.

## Fixing profile rules

| Fixing type | Use when |
|---|---|
| Pin-and-sleeve, top-fix | Standard duty, panels need tool-free removal |
| Strap-fix | High-vibration applications, added retention needed |
| Bolt-through | Low panel-count decks, infrequent panel changes |

Pin-and-sleeve fixings must never be reused after panel replacement if
the sleeve shows any visible deformation — replace sleeves with each
panel change.

## Localized wear zones

Where wear data (see `rules/standards.md` §"Inspection intervals" and
any customer wear report) shows uneven wear concentrated in one zone of
a drum or deck (e.g. feed end), evaluate zone-specific changes
(thickness, material, or upstream feed modification) rather than
upgrading the entire panel set uniformly. This is a candidate decision
for engineering analysis, not a default action — see
`templates/analysis_brief_template.md`.
