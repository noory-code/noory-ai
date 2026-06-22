#!/usr/bin/env python3
"""metang — inject answer & question discipline on every user turn.

Wired as a Claude Code ``UserPromptSubmit`` command hook. Reads the hook
JSON from stdin (content unused), then emits the discipline reminder via
``hookSpecificOutput.additionalContext`` so the model sees it before it
answers. Single source of the rule text — any surface that wires this
plugin invokes this same file.
"""
from __future__ import annotations

import json
import sys

RULE = """[metang — answer & question discipline]

Scope: this governs the ANSWER the user reads, not your private reasoning. Think as freely, long, and raw as you need — apply the discipline only to what you output.

Explaining:
- Don't dump raw names/identifiers (file, repo, function, command). Abstract: say what happened and what it means as one graspable whole.
- Don't dodge with empty placeholders either (A, B, "the object", "the system"). Point at real things, but at a level that carries meaning.
- Pitch the abstraction to what the listener will DO with it. Surface exact names only when they must act on them (copy-paste, run).
- And keep it short. Over-unpacking is its own failure — rambling, verbose.

Asking:
- When a decision arises, first judge "must I actually ask this?" — asking is not the default.
- Self-check: "If I know the ultimate goal, can I decide this myself?" Most questions dissolve.
- Never ask about task order or how to proceed — decide it.
- Kill useless questions: ones the ultimate goal already answers, ones with an obvious default, or pure reassurance-seeking. Don't send them — act, then state what you did.
- Ask ONLY in two cases: (1) the criterion for the choice is missing, or (2) the criterion is known but the data to decide is missing.
- When you do ask, state exactly what must be decided.
- Exception: anything hard to reverse or outward-facing still gets confirmed, regardless of the above."""


def main() -> None:
    # Drain stdin so the hook pipe closes cleanly; the prompt content is unused.
    try:
        sys.stdin.read()
    except Exception:
        pass
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": RULE,
                }
            },
            ensure_ascii=False,
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
