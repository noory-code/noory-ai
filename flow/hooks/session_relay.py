#!/usr/bin/env python3
"""Stop Hook: Session relay — save a summary for the next session.

Leaves a `.flow/.runtime/_session_summary.md` so the next SessionStart hook
(inject_flow_context) can pick up where this one left off. In-progress Action
discovery uses the 4-tier (Initiative/Epic/Story/Action) logic of the
`_flow_state` shared module.

Input (stdin): JSON with common fields + stop_hook_active
Output (stdout): JSON (continue)
"""
import json
import os
import sys
from datetime import datetime, timezone

from _flow_state import (
    resolve_workspace_root,
    runtime_dir,
    summarize_inprogress,
)

SESSION_SUMMARY_FILE = "_session_summary.md"


def main():
    # Prevent Hangul mojibake under Windows Python's default encoding (cp949, etc.) → force
    # UTF-8 on both stdin/stdout. Without stdin, Hangul in the input payload is misread as
    # cp949. No-op on macOS/Linux.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Prevent infinite loop
    if input_data.get("stop_hook_active", False):
        print(json.dumps({"continue": True}))
        return

    workspace_root = resolve_workspace_root(input_data)
    session_id = input_data.get("session_id", "unknown")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    state = summarize_inprogress(workspace_root)

    rt_dir = runtime_dir(workspace_root)
    os.makedirs(rt_dir, exist_ok=True)
    summary_path = os.path.join(rt_dir, SESSION_SUMMARY_FILE)
    rel_summary = os.path.join(".flow", ".runtime", SESSION_SUMMARY_FILE)

    summary = (
        f"# Session Summary\n"
        f"- **End time**: {now}\n"
        f"- **Session ID**: {session_id}\n"
        f"- **Flow state**: {state}\n"
    )

    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        msg = f"Session summary saved: {rel_summary}"
    except OSError as e:
        msg = f"Session summary save failed ({e})"

    output = {
        "continue": True,
        "systemMessage": msg,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
