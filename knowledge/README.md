# Tega Knowledge Base

Local, offline knowledge base for Tega Industries screening panel
products, queried by a small local LLM via Ollama.

## Setup

1. Pull this repo to your local machine.
2. Install [Ollama](https://ollama.com) and pull a model, e.g.:
   ```
   ollama pull gemma2:9b
   ```
3. Start the Ollama server (if not already running as a service):
   ```
   ollama serve
   ```

## Usage

```
cd knowledge
python query.py "Why is the feed end of the Los Andes trommel wearing faster than the rest of the drum?"
```

The script will:

1. Rebuild `graph.json` from every file's frontmatter.
2. Print which files it selected as relevant to your question.
3. Summarize those files in small batches, then synthesize one final
   answer, printed to the terminal.

The answer always follows the format in
`templates/analysis_brief_template.md`: options with cited evidence,
tradeoffs, relevant rules, missing data, and a clearly-labelled
suggested direction. **It is an analysis aid, not a decision-maker —
final calls are made by the engineer.**

## Configuration

Edit the constants at the top of `query.py`:

| Constant | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |
| `MODEL_NAME` | `gemma2:9b` | Model to query (must be pulled in Ollama) |
| `NUM_CTX` | `8192` | Context window passed to Ollama on every call |
| `BATCH_SIZE` | `3` | Files summarized per batch call |

## Adding content

See `CLAUDE.md` for the full frontmatter spec and folder layout. In
short: every new markdown file needs a frontmatter block with a unique
`id`, a `type`, a `name`, a `related` list of other files' ids, and
`tags`. Run `python query.py "anything"` afterward to regenerate
`graph.json` — it's a cache, not something you maintain by hand.
