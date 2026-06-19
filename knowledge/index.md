# Tega Knowledge Base — Index

Human-readable map of this knowledge base. For the machine-readable
version, see `graph.json` (auto-generated — never hand-edit it, see
`CLAUDE.md` §4).

## Rules

| File | Covers |
|---|---|
| `rules/design_rules.md` | Minimum service thickness, aperture tolerance, material selection, fixing profiles, localized wear zones |
| `rules/standards.md` | PU/rubber test standards, incoming QA checks, inspection intervals, reporting requirements |

## Customers

| Customer | Files |
|---|---|
| Minera Los Andes Cobre (Chile) | `customers/customer_001/profile.md`, `customers/customer_001/projects.md`, `customers/customer_001/reports/wear_report_2026_01.md` |
| Greenfield Aggregates Ltd (UK) | `customers/customer_002/profile.md` |

## Products

| Product | File |
|---|---|
| Trommel Panel (modular PU/rubber) | `products/trommel_panel.md` |
| Hydrocyclone Liner | `products/hydrocyclone.md` |

## Templates

| File | Purpose |
|---|---|
| `templates/analysis_brief_template.md` | Output contract every model answer must follow |

## Retrieval

Queries are answered by `query.py`, which builds `graph.json` from
frontmatter `related` links, selects relevant files by keyword match
plus link traversal, summarizes in batches, and sends the result to a
local Ollama model. See `README.md` for usage.
