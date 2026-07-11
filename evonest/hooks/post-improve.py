#!/usr/bin/env python3
"""Cross-host PostToolUse hook: report remaining Evonest proposals.

Reads the shared Claude Code/Codex hook JSON from stdin, extracts the `project`
argument from ``tool_input``, and reports pending proposals.

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

    proposals_dir = Path(project) / ".noory" / "evonest" / "proposals"
    if not proposals_dir.is_dir():
        return

    pending = sum(1 for f in proposals_dir.iterdir() if f.suffix == ".md" and f.is_file())
    if pending > 0:
        msg = {
            "systemMessage": (
                f"evonest improve completed. There are still {pending} pending proposals. "
                "Invoke the Evonest improve workflow again to process the next one."
            )
        }
        print(json.dumps(msg))


if __name__ == "__main__":
    main()
