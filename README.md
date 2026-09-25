# micro-agent-k

A small agent for tinkering, built from the ground up.

micro-agent-k is a minimal Redis ops assistant: Claude runs in a tool-use loop, and that loop is
written as a [LangGraph](https://github.com/langchain-ai/langgraph) state machine. The code stays
small and modular, so you can add tools, memory or context management one piece at a time.

> **Status:** early scaffold. The agent loop isn't wired up yet. See the [roadmap](#roadmap).

## Architecture

```
input ─▶ [agent node: call Claude] ──stop_reason?──▶ end_turn / max_steps / refusal ─▶ output
               ▲                          │ tool_use
               └──── [tools node: run tools, append tool_results] ◀┘
```

The agent has five building blocks. Each one can be swapped or extended without touching the others:

| Block | Role | Extension seam |
|---|---|---|
| **State** | Message history (Anthropic-format dicts) and a step counter | Memory refs, scratchpad |
| **Model node** | Builds the request, calls Claude, appends the response | Context building, caching, streaming |
| **Tool node** | Dispatches `tool_use` blocks through a registry and returns `tool_result`s | More tools, MCP, approval gates |
| **Router** | Continues on `tool_use`, otherwise ends; enforces `MAX_STEPS` | Human-in-the-loop, sub-graphs |
| **Runtime shell** | Config, CLI, container | Checkpointer, API server, observability |

Only `llm.py` imports `anthropic`. Tools are plain functions with JSON schemas, and the graph only wires nodes together.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13.

```bash
git clone https://github.com/kenkyl/micro-agent-k.git
cd micro-agent-k
uv sync
cp .env.example .env   # add your ANTHROPIC_API_KEY
uv run micro-agent --version
```

## Configuration

Settings are read from environment variables or from `.env`:

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Claude API key |
| `MODEL` | `claude-sonnet-5` | Claude model ID |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis instance the tools inspect |
| `MAX_STEPS` | `10` | Maximum model calls per run |

## Development

```bash
uv run pre-commit install   # ruff lint + format on commit
uv run ruff check . && uv run ruff format --check .
uv run pytest -m "not live"
```

## Roadmap

- [x] Project scaffold, CI, pre-commit
- [x] Minimal framework-free reference loop (`scripts/00_raw_loop.py`)
- [ ] LangGraph agent: state, model node, tool node, router, CLI
- [ ] Read-only Redis tools (`redis_info`, `redis_scan`, `redis_get`)
- [ ] Docker image and Compose setup
- [ ] Test suite: fakeredis, fake LLM, live smoke test
- [ ] Later: streaming, Redis checkpointer, long-term memory, human-approved write tools,
      prompt caching, observability, evals, MCP

## License

[MIT](LICENSE)
