# Demo Runbook — Tega Knowledge Base

Plain steps to run this demo for engineers/heads of department, plus
what to check before you're in front of the room.

Demo customer: **Minera Los Andes Cobre** (`customer_001`), a Chilean
copper mine. It's the only customer with the full chain:
`customer_001` → `project_customer_001_trommel` → `product_trommel_panel`
→ `report_wear_2026_01` (all four files cross-link by id — see
`graph.json` or `knowledge/CLAUDE.md` for the frontmatter spec).

## Before the demo (do this the night before, not 5 minutes before)

1. Start Ollama:
   ```
   ollama serve
   ```
2. Pull the model `query.py` is configured to use (check the
   `MODEL_NAME` constant near the top of `query.py` — default is
   `gemma2:9b`):
   ```
   ollama pull gemma2:9b
   ```
3. Run the deterministic retrieval test (no model call, just confirms
   the file-linking works):
   ```
   cd knowledge
   python test_demo.py
   ```
   You should see `ALL TESTS PASSED`. If anything fails, the
   frontmatter `related` links are broken — fix the content before
   the demo, the LLM step can't compensate for broken retrieval.
4. Run the three demo questions below once, end to end, so you've
   seen real model output and aren't surprised live.

## The three questions, in order

Ask these to `query.py` exactly in this order — they build up from
simple to the full cross-file chain, which is the payoff moment.

```
python query.py "Where is Greenfield Aggregates Ltd located and what is their daily throughput?"
```

```
python query.py "What is the drum motor power rating for the Los Andes Cobre trommel?"
```

```
python query.py "What trommel wear issues has Los Andes Cobre reported and which panel spec did we supply?"
```

### Question 1 — warm-up, single customer

**Files that should light up:** `customers/customer_002/profile.md`,
`products/hydrocyclone.md`, `rules/design_rules.md`,
`rules/standards.md`

**What a good answer looks like:** states Greenfield Aggregates Ltd is
in Yorkshire, UK, throughput ~1,200 t/day, citing
`customers/customer_002/profile.md`. Should NOT mention Los Andes,
trommels, or copper — if it does, retrieval pulled in the wrong
customer.

### Question 2 — missing data check

**Files that should light up:** `customers/customer_001/profile.md`,
`customers/customer_001/projects.md`,
`customers/customer_001/reports/wear_report_2026_01.md`,
`products/trommel_panel.md`, `rules/design_rules.md`,
`rules/standards.md`

**What a good answer looks like:** the model correctly finds nothing
about drum *motor power rating* anywhere in those files (there isn't
any — it's not in the knowledge base) and says so explicitly under
**Missing data / open questions**. This is the moment to point out to
the room: the model did NOT make up a horsepower figure. That's the
whole point of the system.

### Question 3 — the finale: full cross-file chain

**Files that should light up:** all of
`customers/customer_001/profile.md`,
`customers/customer_001/projects.md`,
`customers/customer_001/reports/wear_report_2026_01.md`,
`products/trommel_panel.md`, `rules/design_rules.md`,
`rules/standards.md`

**What a good answer looks like:**
- States the wear issue from the report: accelerated, uneven wear at
  the feed end (≈22.5% thickness loss in 10 months vs ≈7.5% at the
  discharge end), citing
  `customers/customer_001/reports/wear_report_2026_01.md`.
- States the panel spec supplied: 305×305mm, 40mm polyurethane, 25mm
  round aperture, pin-and-sleeve fixing, citing
  `customers/customer_001/projects.md` and/or
  `products/trommel_panel.md`.
- Presents 2+ **options** for the feed-end wear issue (e.g. a
  localized harder-compound/thicker panel zone vs a feed-chute
  modification to reduce impingement velocity) — this mirrors the open
  question already logged in the wear report.
- Cites `rules/design_rules.md` for the minimum service thickness rule
  and the "localized wear zones" guidance.
- Ends with a clearly labelled **suggested direction**, not a decision
  — make sure the room notices it says "for engineer review" rather
  than telling them what to do.

## If something looks wrong live

- **Wrong files selected / wrong customer's data shows up:** rerun
  `python test_demo.py` — if it fails now but passed in pre-checks,
  someone edited frontmatter since your last check. Don't debug live;
  fall back to the pre-recorded run from your before-the-demo pass.
- **Model invents a number not in the files:** call it out as exactly
  what the citation requirement is meant to catch, and point at the
  printed "Selected files" list above the answer to show what it had
  to work with.
- **Ollama not responding:** confirm `ollama serve` is running and
  `OLLAMA_HOST` in `query.py` matches (default
  `http://localhost:11434`).
