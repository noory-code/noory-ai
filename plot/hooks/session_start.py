#!/usr/bin/env python3
"""SessionStart hook for Plot — surface VISION + recent DECISIONS.

Prints the project essence (VISION.md first sentence) and the last 5
DECISIONS.md entries to additionalContext so every Plot session begins
with the user's anchor in the assistant's working set.

Cross-platform (macOS, Linux, Windows) — pure Python stdlib only.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def find_plot_root() -> Path | None:
    """Locate plot/ relative to this hook script.

    The hook is registered with command
    ``python3 ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py``
    so ``CLAUDE_PLUGIN_ROOT`` (== ``plot/``) is the parent of the hooks
    directory containing this file.
    """
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidate = Path(plugin_root)
        if (candidate / "docs" / "VISION.md").exists():
            return candidate
    # Fallback: walk up from this file
    here = Path(__file__).resolve()
    for parent in [here.parent.parent, here.parent.parent.parent]:
        if (parent / "docs" / "VISION.md").exists():
            return parent
    return None


def read_vision_essence(plot_root: Path) -> str:
    """Extract the bolded one-sentence essence from VISION.md."""
    vision_path = plot_root / "docs" / "VISION.md"
    if not vision_path.exists():
        return "(VISION.md not found)"
    text = vision_path.read_text(encoding="utf-8")
    # The essence is the first **bolded** paragraph after "## The essence"
    match = re.search(
        r"## The essence.*?\*\*(.*?)\*\*",
        text,
        re.DOTALL,
    )
    if match:
        return match.group(1).strip()
    return "(essence sentence not found in VISION.md)"


def read_recent_decisions(plot_root: Path, n: int = 5) -> list[str]:
    """Return the headings of the last N DECISIONS entries."""
    decisions_path = plot_root / "docs" / "DECISIONS.md"
    if not decisions_path.exists():
        return ["(DECISIONS.md not found)"]
    text = decisions_path.read_text(encoding="utf-8")
    headings = re.findall(r"^### (D-\d{4}-\d{2}-\d{2}-[A-Z]+ — .+)$", text, re.MULTILINE)
    if not headings:
        return ["(no decisions found)"]
    return headings[-n:]


def read_next_session_queue(plot_root: Path) -> list[tuple[str, str]]:
    """Return [(trigger_keyword, short_title)] for every active queue item.

    NEXT_SESSION.md format:
    ## Active queue
    ### `<TRIGGER>` — <short title>
    ...
    ## Completed
    """
    next_path = plot_root / "docs" / "NEXT_SESSION.md"
    if not next_path.exists():
        return []
    text = next_path.read_text(encoding="utf-8")
    # Slice between "## Active queue" and "## Completed"
    active_match = re.search(
        r"^## Active queue\s*\n(.*?)(?=^## Completed|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not active_match:
        return []
    active_section = active_match.group(1)
    items = re.findall(
        r"^###\s+`([^`]+)`\s+—\s+(.+)$",
        active_section,
        re.MULTILINE,
    )
    return items


def main() -> int:
    plot_root = find_plot_root()
    if plot_root is None:
        # Silently no-op outside a Plot context
        print(json.dumps({"continue": True}))
        return 0

    essence = read_vision_essence(plot_root)
    recent = read_recent_decisions(plot_root, n=5)
    queue = read_next_session_queue(plot_root)

    additional_context_lines = [
        "# Plot session anchor",
        "",
        "**Plot's essence (read this first, every session):**",
        "",
        f"> {essence}",
        "",
        "Source of truth: `plot/docs/VISION.md`. Three phases: Discovery (Foundation) → Retention (anchor) → Execution (Actors / Services / Service-Detail) with AICollaboration cross-cutting.",
        "",
        "**Recent decisions (last 5):**",
        "",
    ]
    for d in recent:
        additional_context_lines.append(f"- `{d}`")
    additional_context_lines.extend(
        [
            "",
            "Source: `plot/docs/DECISIONS.md`. Always read the full entry before re-proposing related work.",
        ]
    )

    if queue:
        additional_context_lines.extend(
            [
                "",
                "**Queued tasks for next session — trigger by user keyword (read `plot/docs/NEXT_SESSION.md` for full scope):**",
                "",
            ]
        )
        for trigger, title in queue:
            additional_context_lines.append(
                f"- User says **`{trigger}`** ⇒ execute: {title}"
            )
        additional_context_lines.append("")
        additional_context_lines.append(
            "If the user's first message contains one of the trigger keywords above, "
            "open `plot/docs/NEXT_SESSION.md` and execute the matching item before any "
            "other work."
        )

    additional_context_lines.extend(
        [
            "",
            "**Pre-action gates active:**",
            "- Gate -1: read VISION.md essence (auto-loaded above).",
            "- Gate 0: user confirmation pins SPEC.md immediately.",
            "- Gate 1: SPEC-covered changes only; otherwise stop + ask.",
            "- Gate 2: do not grow SketchCanvas / SketchInspector / App / SketchStencil.",
            "- Gate 3: browser-verify UI changes via the `plot-verifier` sub-agent.",
            "- Gate 4: bump version + CHANGELOG + commit + push together.",
            "",
            "**Skills available for this project:**",
            "- `plot-frontend-bug-diagnosis` — Playwright probe-first for UI bugs.",
            "- `plot-feature-tdd` — essence-anchored test-first feature pipeline.",
        ]
    )
    additional_context = "\n".join(additional_context_lines)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        }
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
