"""Capture Skill tool invocations to the active agent home's skill-usage log.

Reads the PreToolUse JSON payload from stdin. Best-effort: any failure
(malformed JSON, disk full, etc.) exits 0 silently so the underlying tool call
is never blocked. Pure stdlib — cross-platform (no jq/date/bash).

No shebang (CLAUDE.md) — invoked as ``python3 append-log.py`` (see hooks.json).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ARGS_MAX = 200  # keep log lines bounded


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") != "Skill":
        return 0

    # on/off: skill_usage.enabled in the project's .flow/settings.json.
    # Default on — records when the file/key is absent. Skips only when explicitly False.
    proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CODEX_PROJECT_DIR") or ""
    if proj:
        settings = Path(proj) / ".flow" / "settings.json"
        try:
            if settings.is_file():
                data = json.loads(settings.read_text(encoding="utf-8"))
                if (data.get("skill_usage") or {}).get("enabled") is False:
                    return 0
        except Exception:
            pass  # unreadable settings → default on

    tool_input = payload.get("tool_input") or {}
    skill = tool_input.get("skill") or ""
    if not skill:
        return 0

    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill": skill,
        "args": str(tool_input.get("args") or "")[:ARGS_MAX],
        "cwd": payload.get("cwd") or "",
        "session_id": payload.get("session_id") or "",
    }

    try:
        # Codex hook payloads carry turn-scoped fields (turn_id). Keep Claude's
        # log path stable and route Codex captures to ~/.codex. permission_mode
        # must NOT be used as the discriminator — it is a COMMON Claude Code hook
        # field, so keying on it would reroute every Claude capture into ~/.codex.
        log_dir = Path.home() / (".codex" if "turn_id" in payload else ".claude")
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "skill-usage.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
