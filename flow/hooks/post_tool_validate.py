#!/usr/bin/env python3
"""PostToolUse Hook: audit logging after a tool runs.

Appends every tool call to `.flow/.runtime/hook_audit.jsonl` (gitignored).
Source data for flow-activity tracking / retrospective & evolution metrics.

Record (TS-001 capture extension): {ts, tool, success, unit_id?, skill?}
- unit_id = single attribution to the in-progress (🔄) work item (active_unit_id — omitted if none)
- skill = the skill name when the Skill tool is called (omitted otherwise)
Aggregation (audit_report) groups each item's share by unit_id and counts used skills by skill.

Input (stdin): JSON with tool_name, tool_input, tool_response, cwd
Output (stdout): JSON {} (always allow — a post hook, so it never blocks)

Note: the "hook .py syntax check" that was in the early project-local hook has been removed.
Plugins run from a cache, so a source-hook edit cannot be detected within the same session,
and the target project usually has no hook of its own, so it has no general value (YAGNI).
"""
import json
import sys
from datetime import datetime, timezone

from _flow_state import resolve_workspace_root, append_audit, active_unit_id


def build_entry(input_data: dict, workspace_root: str) -> dict:
    """Build an audit record (testable — separated from main).

    Keeps the existing fields (ts/tool/success) + tags unit_id (the in-progress item) + skill (Skill tool).
    """
    tool_name = input_data.get("tool_name", "")
    tool_response = input_data.get("tool_response", {}) or {}
    tool_input = input_data.get("tool_input", {}) or {}
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "success": not tool_response.get("isError", False),
    }
    unit = active_unit_id(workspace_root)
    if unit:
        entry["unit_id"] = unit
    if tool_name == "Skill":
        skill = tool_input.get("skill")
        if skill:
            entry["skill"] = skill
    return entry


def main():
    # Prevent Hangul mojibake under Windows Python's default encoding (cp949 etc.) → force UTF-8
    # on both stdin/stdout. Without stdin, Hangul in the input payload is misread as cp949. No-op on macOS/Linux.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Guarantee the decision output first (PostToolUse must always emit {}). Measurement capture is
    # an add-on, so no exception (e.g. the active_unit_id scan) may break the hook output (same as the pre hook).
    print(json.dumps({}))

    try:
        workspace_root = resolve_workspace_root(input_data)
        append_audit(workspace_root, build_entry(input_data, workspace_root))
    except Exception:
        pass


if __name__ == "__main__":
    main()
