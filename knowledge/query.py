#!/usr/bin/env python3
"""
query.py — local retrieval + summarization front-end for the Tega
knowledge base, talking to a local Ollama model.

Pipeline:
  1. Parse YAML frontmatter out of every markdown file -> graph.json
     (always rebuilt before a query, since it is a cache, not a
     source of truth — see CLAUDE.md section 4).
  2. Match the question's keywords against frontmatter tags/name/id
     to find seed files, then follow `related` links (transitively)
     to pull in connected files.
  3. Summarize the selected files in small batches (so each Ollama
     call stays well within num_ctx), then synthesize one final
     answer from the batch summaries.
  4. Send everything to Ollama's /api/chat endpoint (required for
     Gemma-family models — /api/generate does not apply chat
     templating correctly for them).

Dependencies: Python 3.8+ standard library only. No pip installs
required — this is meant to run from a portable/bundled interpreter.
"""

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

# --------------------------------------------------------------------------
# Configuration — edit these to match your local setup.
# --------------------------------------------------------------------------

OLLAMA_HOST = "http://localhost:11434"   # Ollama server address
MODEL_NAME = "gemma2:9b"                 # any model pulled in `ollama list`
NUM_CTX = 8192                           # context window passed to Ollama
BATCH_SIZE = 3                           # files summarized per batch call
REQUEST_TIMEOUT_SECONDS = 120

KNOWLEDGE_ROOT = Path(__file__).resolve().parent
GRAPH_PATH = KNOWLEDGE_ROOT / "graph.json"
TEMPLATE_PATH = KNOWLEDGE_ROOT / "templates" / "analysis_brief_template.md"

# Files that are part of the repo but not part of the citation graph
# (no frontmatter, not selectable as a source).
NON_CONTENT_FILES = {"CLAUDE.md", "index.md", "README.md"}


# --------------------------------------------------------------------------
# Frontmatter parsing
#
# We deliberately avoid a PyYAML dependency since this is meant to run
# from a bundled/portable interpreter with stdlib only. The frontmatter
# in this repo is a small, fixed subset of YAML (scalars, inline lists,
# and block lists of plain strings), so a small hand-rolled parser is
# more portable than pulling in a YAML library.
# --------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Extract the YAML frontmatter block from a markdown file's text.

    Supports exactly the subset used in this repo:
      key: scalar value
      key: [inline, list, of, items]
      key:
        - block
        - list
        - of items
    Returns {} if no frontmatter block is found.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    fields: dict = {}
    lines = match.group(1).splitlines()
    current_key = None

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            continue

        # Block-list item, e.g. "  - product_trommel_panel"
        block_item = re.match(r"^\s*-\s*(.+)$", line)
        if block_item and current_key:
            fields.setdefault(current_key, [])
            fields[current_key].append(block_item.group(1).strip())
            continue

        # "key: value" or "key:" (start of a block list)
        key_value = re.match(r"^(\w+):\s*(.*)$", line)
        if not key_value:
            continue

        key, value = key_value.group(1), key_value.group(2).strip()
        current_key = key

        if value == "":
            # Block list follows on subsequent lines.
            fields[key] = []
        elif value.startswith("[") and value.endswith("]"):
            # Inline list, e.g. "[copper, chile, trommel]"
            items = value[1:-1].split(",")
            fields[key] = [item.strip() for item in items if item.strip()]
        else:
            fields[key] = value

    return fields


# --------------------------------------------------------------------------
# Graph building
# --------------------------------------------------------------------------

def scan_markdown_files() -> dict:
    """Walk the repo and parse frontmatter out of every content file.

    Returns a dict keyed by frontmatter `id`, matching the shape
    documented in CLAUDE.md section 4.
    """
    graph = {}

    for md_path in KNOWLEDGE_ROOT.rglob("*.md"):
        if md_path.name in NON_CONTENT_FILES:
            continue
        if TEMPLATE_PATH in (md_path,):
            continue  # the template itself has no frontmatter / is not a source

        text = md_path.read_text(encoding="utf-8")
        fields = parse_frontmatter(text)
        if "id" not in fields:
            continue  # not a frontmatter-bearing content file

        file_id = fields["id"]
        if file_id in graph:
            raise ValueError(
                f"Duplicate id '{file_id}' found in {md_path} "
                f"(already used by {graph[file_id]['file']})"
            )

        graph[file_id] = {
            "file": str(md_path.relative_to(KNOWLEDGE_ROOT)),
            "type": fields.get("type", ""),
            "name": fields.get("name", ""),
            "tags": fields.get("tags", []),
            "related": fields.get("related", []),
        }

    return graph


def build_graph() -> dict:
    """Rebuild graph.json from frontmatter and write it to disk."""
    graph = scan_markdown_files()
    GRAPH_PATH.write_text(json.dumps(graph, indent=2, sort_keys=True), encoding="utf-8")
    return graph


# --------------------------------------------------------------------------
# Retrieval: keyword match + transitive link traversal
# --------------------------------------------------------------------------

def tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def find_seed_ids(question: str, graph: dict) -> set:
    """Match question keywords against each file's id, name, and tags."""
    question_tokens = tokenize(question)
    seeds = set()

    for file_id, record in graph.items():
        haystack_tokens = tokenize(file_id) | tokenize(record["name"])
        for tag in record["tags"]:
            haystack_tokens |= tokenize(tag)

        if question_tokens & haystack_tokens:
            seeds.add(file_id)

    return seeds


def expand_via_related_links(seed_ids: set, graph: dict) -> set:
    """Follow `related` links transitively from the seed set.

    This is a breadth-first closure over the graph: a keyword hit on
    customer_001 should pull in its project, which pulls in the
    product and the wear report, etc.

    Traversal does NOT continue past `type: rule` nodes. Rule files
    (design_rules, standards) are referenced from almost every product
    and project, so they act as hub nodes — without this cutoff, a
    query about one customer would transitively pull in every other
    customer and product through the shared rule files. Rules are
    still always *included* (and cited) when reached; they just don't
    bridge the traversal onward.
    """
    selected = set(seed_ids)
    frontier = set(seed_ids)

    while frontier:
        next_frontier = set()
        for file_id in frontier:
            for related_id in graph.get(file_id, {}).get("related", []):
                if related_id not in graph or related_id in selected:
                    continue
                selected.add(related_id)
                if graph[related_id]["type"] != "rule":
                    next_frontier.add(related_id)
        frontier = next_frontier

    return selected


def select_files(question: str, graph: dict) -> list:
    seeds = find_seed_ids(question, graph)
    selected_ids = expand_via_related_links(seeds, graph)
    return sorted(selected_ids)


# --------------------------------------------------------------------------
# Ollama client
# --------------------------------------------------------------------------

def call_ollama(messages: list) -> str:
    """POST to Ollama's /api/chat endpoint (required for chat-tuned
    models like Gemma; /api/generate does not apply the chat template).
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"num_ctx": NUM_CTX},
    }
    request = urllib.request.Request(
        url=f"{OLLAMA_HOST}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"Could not reach Ollama at {OLLAMA_HOST}: {exc}\n"
            f"Is `ollama serve` running and is '{MODEL_NAME}' pulled?"
        )

    return body["message"]["content"]


# --------------------------------------------------------------------------
# Batch summarization + synthesis
# --------------------------------------------------------------------------

SUMMARY_SYSTEM_PROMPT = """You are summarizing internal Tega Industries technical
documents for later synthesis. For each document given to you:
- Extract only facts relevant to the user's question.
- Keep every specific number, spec, tolerance, or figure exactly as written.
- Prefix every fact with its source file path in parentheses.
- Do not add opinions, recommendations, or conclusions — extraction only.
Be terse. Use short bullet points."""


def summarize_batch(question: str, file_records: list) -> str:
    """Summarize one small batch of files into a fact list with citations."""
    documents = []
    for record in file_records:
        path = KNOWLEDGE_ROOT / record["file"]
        documents.append(f"--- SOURCE: {record['file']} ---\n{path.read_text(encoding='utf-8')}")

    user_message = (
        f"User question: {question}\n\n"
        f"Documents:\n\n" + "\n\n".join(documents)
    )

    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    return call_ollama(messages)


def batch_summarize_all(question: str, graph: dict, selected_ids: list) -> list:
    """Summarize selected files in small batches to stay within context."""
    records = [graph[file_id] for file_id in selected_ids]
    summaries = []

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]
        summaries.append(summarize_batch(question, batch))

    return summaries


def synthesize_answer(question: str, summaries: list) -> str:
    """Combine batch summaries into one final answer following the
    advisory output format defined in templates/analysis_brief_template.md.
    """
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    system_prompt = (
        "You are an engineering analysis assistant for Tega Industries "
        "screening panel products. You SURFACE OPTIONS AND ANALYSIS for a "
        "human engineer to decide — you NEVER make the decision yourself.\n\n"
        "Rules you must follow:\n"
        "1. Your output MUST follow this exact template structure:\n\n"
        f"{template_text}\n\n"
        "2. EVERY factual claim must cite its source file by path, e.g. "
        "(source: customers/customer_001/profile.md).\n"
        "3. Present multiple options, never a single forced answer.\n"
        "4. If information needed to answer is not present in the provided "
        "summaries, say so explicitly in 'Missing data / open questions' — "
        "never invent figures, tolerances, or specs.\n"
        "5. The 'Suggested direction' section must be clearly labelled as a "
        "suggestion for the engineer to weigh, not a final decision."
    )

    user_message = (
        f"Question: {question}\n\n"
        "Here are fact summaries extracted from the relevant knowledge base "
        "files (each fact is already cited with its source file):\n\n"
        + "\n\n".join(f"Batch {i + 1}:\n{summary}" for i, summary in enumerate(summaries))
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    return call_ollama(messages)


# --------------------------------------------------------------------------
# CLI entry point
# --------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {Path(sys.argv[0]).name} \"your question\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    graph = build_graph()
    selected_ids = select_files(question, graph)

    if not selected_ids:
        print("No relevant files found in the knowledge base for this question.")
        sys.exit(0)

    print("Selected files:")
    for file_id in selected_ids:
        record = graph[file_id]
        print(f"  - {record['file']}  (id: {file_id}, type: {record['type']})")
    print()

    summaries = batch_summarize_all(question, graph, selected_ids)
    answer = synthesize_answer(question, summaries)

    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    main()
