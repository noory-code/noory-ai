#!/usr/bin/env python3
"""PostToolUse hook: auto-chain evonest improve when proposals remain.

Reads JSON from stdin (Claude Code hook protocol), extracts the `project`
argument from the tool_input, checks for pending proposals, and instructs
Claude to run the next improve if any exist.

Cross-platform replacement for post-improve.sh.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return

    project = (data.get("tool_input") or {}).get("project")
    if not project:
        return

    proposals_dir = Path(project) / ".evonest" / "proposals"
    if not proposals_dir.is_dir():
        return

    pending = sum(1 for f in proposals_dir.iterdir() if f.suffix == ".md" and f.is_file())
    if pending > 0:
        msg = {
            "systemMessage": (
                f"evonest improve completed. There are still {pending} pending proposals. "
                "Run /evonest:improve again to process the next one."
            )
        }
        print(json.dumps(msg))


if __name__ == "__main__":
    main()
