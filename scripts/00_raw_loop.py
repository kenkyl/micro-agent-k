"""A minimal framework-free reference loop: Claude + one tool, no LangGraph.

Run: uv run --env-file .env python scripts/00_raw_loop.py "What time is it in Tokyo?"
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
MAX_STEPS = int(os.environ.get("MAX_STEPS", "10"))

TOOLS = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time in an IANA timezone, e.g. 'Asia/Tokyo'.",
        "input_schema": {
            "type": "object",
            "properties": {"timezone": {"type": "string", "description": "IANA timezone name"}},
            "required": ["timezone"],
        },
    }
]


def get_current_time(timezone: str) -> str:
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")


def run_tool(name: str, args: dict) -> dict:
    """Run one tool call. Errors go back to the model instead of crashing the loop."""
    try:
        if name != "get_current_time":
            raise ValueError(f"unknown tool: {name}")
        return {"content": get_current_time(**args)}
    except Exception as exc:
        return {"content": f"{type(exc).__name__}: {exc}", "is_error": True}


def main(question: str) -> None:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    messages = [{"role": "user", "content": question}]

    for step in range(1, MAX_STEPS + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=16000, tools=TOOLS, messages=messages
        )
        # Append the full content (thinking + text + tool_use blocks) so the next call sees it.
        messages.append({"role": "assistant", "content": response.content})
        print(f"[step {step}] stop_reason={response.stop_reason}")

        if response.stop_reason != "tool_use":
            break

        # Every tool_use needs a matching tool_result, all in one user message.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> {block.name}({block.input})")
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        **run_tool(block.name, block.input),
                    }
                )
        messages.append({"role": "user", "content": results})
    else:
        print(f"Stopped: hit MAX_STEPS={MAX_STEPS}")

    print("\n" + "".join(b.text for b in response.content if b.type == "text"))


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or "What time is it in Tokyo and in New York?")
