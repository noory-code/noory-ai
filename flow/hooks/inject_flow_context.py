#!/usr/bin/env python3
"""SessionStart Hook: Inject active flow context.

Scans .flow/workspace/ for active Initiative/Epic/Story/Action state and
injects it as additionalContext so the AI knows where we left off. If the Stop
hook (session_relay) left a previous-session summary, it is appended too.

The 4-tier scan logic lives in the `_flow_state` shared module (shares an SSOT with session_relay).

Input (stdin): JSON with common fields (session_id, cwd, transcript_path, etc.)
Output (stdout): JSON with hookSpecificOutput.additionalContext
"""
from __future__ import annotations

import json
import os
import sys

from _flow_state import (
    FOUR_WAY_BRIEF,
    detect_plugin_staleness,
    detect_rule_drift_all,
    find_active_epics,
    find_active_initiatives,
    plugin_rules_dir,
    project_rules_dir,
    resolve_workspace_root,
    runtime_dir,
)

SESSION_SUMMARY_FILE = "_session_summary.md"


def read_session_summary(workspace_root: str) -> str:
    """Read the summary left by the previous session's Stop hook (if any)."""
    path = os.path.join(runtime_dir(workspace_root), SESSION_SUMMARY_FILE)
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def _format_epic(epic: dict, lines: list[str], heading: str) -> None:
    """Append one epic's tree (including a one-line purpose) to lines."""
    lines.append(f"\n{heading} {epic['name']}")
    if epic.get("purpose"):
        lines.append(f"> Ultimate purpose: {epic['purpose']}")
    for story in epic["stories"]:
        lines.append(f"- {story['name']} [{story['status']}]")
        for action in story["actions"]:
            delegate = f" → {action['delegate_to']}" if action["delegate_to"] else ""
            lines.append(f"  - {action['file']} [{action['status']}]{delegate}")


def format_context(initiatives: list[dict], epics: list[dict]) -> str:
    """Format initiative/epic data as concise context string."""
    if not initiatives and not epics:
        return "Flow state: no active Initiative/Epic. Batch work mode available."

    lines = ["## Active flow state (auto-injected by SessionStart Hook)"]

    for init in initiatives:
        lines.append(f"\n## {init['name']}")
        if init.get("purpose"):
            lines.append(f"> Ultimate purpose: {init['purpose']}")
        for epic in init["epics"]:
            _format_epic(epic, lines, "###")

    for epic in epics:
        _format_epic(epic, lines, "###")

    lines.append("")
    lines.append(
        "> Phase-Asset binding: load the flow-* skill matching the current Phase with Read."
    )
    lines.append(FOUR_WAY_BRIEF)  # SSOT: _flow_state.FOUR_WAY_BRIEF (shared with pre_tool)
    lines.append(
        "> Planning procedure: no level (Initiative/Epic/Story/Action) may execute without a plan "
        "— no arbitrary skipping per level (no-write-without-plan). Planning is enforced through artifacts "
        "(Action documents, playbook fields, ultimate purpose) and the hook blocks otherwise "
        "(no-action-without-doc / no-work-without-playbook / no-node-without-purpose). On entering work, pick "
        "the work-type playbook and record it in the _epic.md **playbook** field. (Plan Mode is one tool for "
        "holding a plan — the means is not mandated.)"
    )
    return "\n".join(lines)


def _drift_names(items: list[str]) -> str:
    """Summarize filenames (first 3 + remaining N) — avoids the additionalContext limit (no diff body)."""
    head = ", ".join(items[:3])
    extra = len(items) - 3
    return head + (f" and {extra} more" if extra > 0 else "")


def format_plugin_staleness() -> str:
    """Return an upgrade-guidance block if the installed plugin is behind the latest (empty string if not).

    Compares the current local state (`detect_plugin_staleness` — zero network). Guides the per-environment
    application method, but the user does the apply/restart. main isolates it in an independent try/except
    (blast radius 0).
    """
    info = detect_plugin_staleness()
    if not info["stale"]:
        return ""
    env = info["env"]
    if env == "cli":
        how = ("`claude plugin marketplace update <marketplace>` then "
               "`claude plugin update <plugin>@<marketplace> --scope <install scope>` → restart session")
    elif env == "vscode":
        how = "`git pull` the marketplace repo then `Developer: Reload Window`"
    else:
        how = "Upgrade the plugin then restart the session"
    return "\n".join([
        "",
        "## ⚠ Plugin upgrade required (auto-detected at SessionStart)",
        f"> Installed flow v{info['installed']} < latest v{info['latest']} — it is behind.",
        f"> 👉 Upgrade: {how}",
        "> (The user does the upgrade/restart. **After restart**, sync rules with `/flow-upgrade`. "
        "For the exact latest version, re-check after a marketplace update[update/fetch] — the hook only "
        "compares the current local state.)",
    ])


def format_rule_drift(workspace_root: str) -> str:
    """Detect drift between the plugin rule canonical source and the project copy in **read-only** mode and
    return a notice block (propagation-rule model).

    `detect_rule_drift_all` (rule-details merged + orphan/protected). Propagation rules always override
    (no conflict concept). Zero file writes — applying is done by /flow-upgrade (a human). Empty string
    if no drift. main isolates it in an independent try/except (blast radius 0). When the plugin is stale,
    main omits this block (upgrade/restart the plugin first, then sync rules).
    """
    plugin_rules = plugin_rules_dir()
    project_rules = project_rules_dir(workspace_root)
    # Canonical/copy directory missing (not installed, not configured, cwd cache) → cannot compare → fail-safe silence
    if not os.path.isdir(plugin_rules) or not os.path.isdir(project_rules):
        return ""
    drift = detect_rule_drift_all(workspace_root)
    stale = drift["stale"]
    missing_new = drift["missing_new"]
    orphan = drift["orphan"]
    if not (stale or missing_new or orphan):
        return ""  # In sync → silence (zero noise). protected (self-authored rules) are preserved — not announced.

    ver = drift.get("plugin_version") or "?"
    lines = [
        "",
        "## ⚠ Flow rule sync required (auto-detected at SessionStart)",
        f"> The plugin rule canonical source (v{ver}) and the project `.claude/rules/` copy have diverged "
        "— sync them with `/flow-upgrade`. (A human applies — the hook only detects.)",
    ]
    if stale:
        lines.append(f"- Out of sync (canonical changed) ({len(stale)}): {_drift_names(stale)}")
    if missing_new:
        lines.append(f"- Not propagated (new rule) ({len(missing_new)}): {_drift_names(missing_new)}")
    if orphan:
        lines.append(
            f"- To delete (propagation rule gone from canonical) ({len(orphan)}): {_drift_names(orphan)}"
        )
    lines.append(
        "> 👉 **preflight before task**: A stale rule state can affect the gate/rule judgment basis of later "
        "work, so the agent must first confirm whether to run `/flow-upgrade` before starting the "
        "user-requested work."
    )
    lines.append(
        "> Proceed with the current work only if the user explicitly answers \"later\", \"skip\", or "
        "\"do the work first\". This confirmation is performed only once per session; if the user has already "
        "responded, do not re-confirm on later turns."
    )
    return "\n".join(lines)


def main():
    # Prevent Hangul mojibake under Windows Python default encodings (cp949, etc.) → force UTF-8 on both
    # stdin/stdout. Without stdin, Hangul in the input payload is misread as cp949. No-op on macOS/Linux.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    workspace_root = resolve_workspace_root(input_data)
    initiatives = find_active_initiatives(workspace_root)
    epics = find_active_epics(workspace_root)
    context = format_context(initiatives, epics)

    # 2-axis detection (read-only) — plugin staleness first → rule drift. Each isolated independently (blast radius 0).
    # If the plugin is stale, "upgrade + restart" comes first (rule sync after restart — the detect basis changes).
    try:
        plugin_block = format_plugin_staleness()
    except Exception:
        plugin_block = ""
    if plugin_block:
        context += "\n" + plugin_block
    else:
        try:
            drift_block = format_rule_drift(workspace_root)
        except Exception:
            drift_block = ""
        if drift_block:
            context += "\n" + drift_block

    # Integrate the previous session's Stop hook summary (continuity)
    summary = read_session_summary(workspace_root)
    if summary:
        context += "\n\n## Previous session summary (recorded by Stop Hook)\n" + summary

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
