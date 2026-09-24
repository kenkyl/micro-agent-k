"""Command-line entrypoint. The agent graph is wired in here once it exists."""

import sys

from micro_agent import __version__


def main() -> None:
    if "--version" in sys.argv[1:]:
        print(f"micro-agent {__version__}")
        return
    print("micro-agent: the agent loop isn't wired up yet.")


if __name__ == "__main__":
    main()
