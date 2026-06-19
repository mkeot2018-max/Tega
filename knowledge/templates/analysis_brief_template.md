<!--
This is the OUTPUT CONTRACT for query.py. Every answer the model
produces must follow this exact structure. It is injected into the
system prompt verbatim so the model has no room to deviate.

This file has no frontmatter and is not part of the citation graph —
it is a format template, not a content file.
-->

# Analysis Brief

## Question

<Restate the engineer's question in one or two sentences, in your own
words, to confirm scope.>

## Options

<Present 2 to 4 distinct options. Each option MUST include the
evidence behind it and MUST cite its source file by path. Do not
present a single option as "the answer" — these are choices for the
engineer to weigh.>

### Option 1: <short label>

- Evidence: <fact, spec, or figure> (source: `path/to/file.md`)
- Evidence: <fact, spec, or figure> (source: `path/to/file.md`)

### Option 2: <short label>

- Evidence: ...

## Tradeoffs

<For each option above, state the tradeoff plainly — cost, downtime,
risk, lead time, performance — citing source files where the tradeoff
itself is sourced from data rather than general reasoning.>

| Option | Pros | Cons |
|---|---|---|
| Option 1 | | |
| Option 2 | | |

## Relevant rules

<List the design/QA rules that bear on this question, citing the rule
file each one comes from, e.g. `rules/design_rules.md` §"Material
selection rule".>

## Missing data / open questions

<List anything needed to make a confident decision that is NOT present
in the knowledge base. Do not invent figures, tolerances, or specs to
fill these gaps — say plainly that the data is missing.>

## Suggested direction

<This is a SUGGESTION for the engineer to weigh, not a decision. Label
it explicitly as such, e.g.: "Suggested direction (for engineer
review, not a final decision): ...". Keep it short and tied back to
the options above.>
