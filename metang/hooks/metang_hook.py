#!/usr/bin/env python3
"""metang — inject answer & question discipline on every user turn.

Wired as a Claude Code ``UserPromptSubmit`` command hook. Reads the hook
JSON from stdin (content unused), then emits the discipline reminder via
``hookSpecificOutput.additionalContext`` so the model sees it before it
answers.

Optional config: ``.metang.json`` in the project root (``$CLAUDE_PROJECT_DIR``)
overriding ``~/.metang.json``. Recognised keys:

- ``enabled`` (bool, default ``true``) — set ``false`` to mute the reminder
  without uninstalling the plugin.
- ``explainRules`` (str) — replaces the default "Explaining" bullets.
- ``askRules`` (str) — replaces the default "Asking" bullets.

With no config file present, the built-in defaults below are used.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCOPE = (
    "Scope: this governs the ANSWER the user reads, not your private reasoning. "
    "Think as freely, long, and raw as you need — apply the discipline only to "
    "what you output."
)

DEFAULT_EXPLAIN = """- Don't dump raw names/identifiers (file, repo, function, command). Abstract: say what happened and what it means as one graspable whole.
- Don't dodge with empty placeholders either (A, B, "the object", "the system"). Point at real things, but at a level that carries meaning.
- Pitch the abstraction to what the listener will DO with it. Surface exact names only when they must act on them (copy-paste, run).
- And keep it short. Over-unpacking is its own failure — rambling, verbose."""

DEFAULT_ASK = """- When a decision arises, first judge "must I actually ask this?" — asking is not the default.
- Self-check: "If I know the ultimate goal, can I decide this myself?" Most questions dissolve.
- Never ask about task order or how to proceed — decide it.
- Kill useless questions: ones the ultimate goal already answers, ones with an obvious default, or pure reassurance-seeking. Don't send them — act, then state what you did.
- Ask ONLY in two cases: (1) the criterion for the choice is missing, or (2) the criterion is known but the data to decide is missing.
- When you do ask, state exactly what must be decided.
- Exception: anything hard to reverse or outward-facing still gets confirmed, regardless of the above."""


def load_config() -> dict[str, object]:
    """Merge ~/.metang.json then project .metang.json (project wins)."""
    cfg: dict[str, object] = {}
    candidates = [Path.home() / ".metang.json"]
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        candidates.append(Path(project_dir) / ".metang.json")
    for path in candidates:
        try:
            if path.is_file():
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    cfg.update(loaded)
        except (OSError, ValueError):
            pass  # malformed config never breaks the hook
    return cfg


def build_rule(cfg: dict[str, object]) -> str:
    explain = cfg.get("explainRules") or DEFAULT_EXPLAIN
    ask = cfg.get("askRules") or DEFAULT_ASK
    return (
        "[metang — answer & question discipline]\n\n"
        f"{SCOPE}\n\n"
        f"Explaining:\n{explain}\n\n"
        f"Asking:\n{ask}"
    )


def dump_defaults() -> str:
    """The built-in config a user can seed and then edit. This script is the
    single source of the default rule text."""
    return json.dumps(
        {"enabled": True, "explainRules": DEFAULT_EXPLAIN, "askRules": DEFAULT_ASK},
        ensure_ascii=False,
        indent=2,
    )


def main() -> None:
    if "--dump-defaults" in sys.argv:
        sys.stdout.write(dump_defaults())
        sys.exit(0)
    # Drain stdin so the hook pipe closes cleanly; the prompt content is unused.
    try:
        sys.stdin.read()
    except Exception:
        pass
    cfg = load_config()
    if cfg.get("enabled", True) is False:
        sys.exit(0)  # muted: emit nothing, inject nothing
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": build_rule(cfg),
                }
            },
            ensure_ascii=False,
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
