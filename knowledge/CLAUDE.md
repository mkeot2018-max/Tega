# Tega Industries Knowledge Base — Operating Spec

This repository is a local, offline knowledge base for Tega Industries
(screening panels: polyurethane/rubber panels with specific hole patterns,
thickness, and fixing profiles). It is queried by a small local LLM
(Gemma / Llama3-8B via Ollama) through `query.py`. This file is the spec
that both humans and the retrieval script follow.

## 1. Folder structure

```
knowledge/
├── CLAUDE.md                  this file
├── index.md                   human-readable map of the knowledge base
├── graph.json                 AUTO-GENERATED — do not hand-edit (see §4)
├── rules/
│   ├── design_rules.md        panel design constraints
│   └── standards.md           material/QA standards
├── customers/
│   ├── customer_001/
│   │   ├── profile.md
│   │   ├── projects.md
│   │   └── reports/
│   │       └── wear_report_2026_01.md
│   └── customer_002/
│       └── profile.md
├── products/
│   ├── trommel_panel.md
│   └── hydrocyclone.md
├── templates/
│   └── analysis_brief_template.md   output contract for the model
└── query.py                   retrieval + summarization + Ollama call
```

## 2. Frontmatter spec

Every markdown file in `knowledge/` (except `CLAUDE.md`, `index.md`,
`graph.json`) starts with YAML frontmatter:

```yaml
---
id: customer_001
type: customer | project | product | rule | report
name: Human readable name
related:
  - product_trommel_panel
  - report_wear_2026_01
tags: [copper, chile, trommel]
---
```

Field rules:

- `id` — globally unique string. Convention: `<type>_<slug>`, e.g.
  `customer_001`, `product_trommel_panel`, `report_wear_2026_01`,
  `rule_design_rules`. No two files may share an `id`.
- `type` — one of `customer`, `project`, `product`, `rule`, `report`.
  (`profile` and `projects` files use `type: customer` /
  `type: project` respectively — see existing files for examples.)
- `name` — human-readable title, used in retrieval output.
- `related` — list of other files' `id` values, in either direction
  (the link does not need to be reciprocated, but reciprocating it
  makes graph traversal more reliable — see existing files).
- `tags` — flat list of lowercase keywords used for keyword matching
  during retrieval (material, location, ore type, product line, etc).

## 3. Core rule: ANALYSIS, NEVER DECISIONS

**The system surfaces options and analysis for a human engineer to
decide. It never makes the decision itself.**

This applies to every prompt, template, and script in this repo:

- The model must present 2–4 options with evidence, not a single
  recommendation presented as fact.
- The model must cite the source file for every factual claim.
- The model must say so in **Missing data / open questions** rather
  than inventing figures, tolerances, or specs that aren't in the
  knowledge base.
- Any "suggested direction" must be clearly labelled as a suggestion
  for the engineer to weigh, not a conclusion.

## 4. graph.json (auto-generated)

`graph.json` is built by `query.py --build-graph` (also run
automatically before every query) by parsing the `related` frontmatter
field out of every markdown file. It is a flat adjacency map:

```json
{
  "customer_001": {
    "file": "customers/customer_001/profile.md",
    "type": "customer",
    "name": "...",
    "tags": ["copper", "chile", "trommel"],
    "related": ["project_customer_001_trommel", "..."]
  },
  ...
}
```

Never hand-edit `graph.json`. If it goes stale or out of sync, delete
it and rerun `query.py`.

## 5. Output format — analysis_brief_template.md

Every answer the model produces must follow
`templates/analysis_brief_template.md`:

- **Question** — restated
- **Options** — 2–4, each with evidence and the source file cited
- **Tradeoffs** — per option
- **Relevant rules** — citing the rule file
- **Missing data / open questions**
- **Suggested direction** — explicitly labelled as a suggestion, not
  a decision

`query.py` injects this template into the system prompt so the model
has no room to deviate from the format.

## 6. Writing for small-model consumption

The target model is small (8B-class, run locally, ~8K context by
default). Every content file in this repo must be written accordingly:

- Short sections (a few lines each), clear headers.
- Tables for any specs (dimensions, tolerances, hours, percentages) —
  tables are far more token-efficient and parseable than prose.
- No filler, no marketing language, no repeated boilerplate.
- State units explicitly (mm, %, hours, MPa, etc).
- Keep each file short enough to be summarized in one batch — if a
  file grows large, split it rather than letting it sprawl.
