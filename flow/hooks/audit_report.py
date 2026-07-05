"""Per-work-item measurement aggregation CLI (TS-001 A-002).

Reads ``.flow/.runtime/hook_audit.jsonl`` captured by A-001 and, per work item
(unit_id), counts **exactly what is in the log** — no embellishment. Essence: not
trimming but simple + writing.

Aggregation (per unit):
- ``denied_rules`` : per-rule count of denies (diet — a deny rule that almost never fires = dead-weight candidate)
- ``asked_rules``  : per-rule count of ask-stops (decision-criteria-first etc. — fires often by design.
                     merging it with deny pollutes the 'fires often = alive' signal, so keep it separate)
- ``skills``       : per-skill usage count (diet — an unused skill = cleanup candidate)
- ``retries``      : number of success=false tool calls (the 'retry count' the retrospective evaluates)
- ``tools``        : per-tool call count — repeated successful edits of the same file = a thrashing signal
                     (retrospective 'inefficiency'; a separate signal, distinct from retries = failures)

Record discrimination: post = ``success`` key (executed) / pre-block = ``blocked_rule`` key (blocked).
A record without a ``unit_id`` goes to the ``unattributed`` bucket.

Usage: at work-item wrap-up/retrospective, quote that item's numbers with ``--unit <id>`` (evidence-based retrospective).
The whole (no filter) is the frequency of the **fired** rules/skills — a gauge of which barely fire. (Full
'dead rule' identification = the set difference against the whole rule population, which is TS-002 diet
scope — this CLI covers only what fired.)

Workspace root = CLAUDE_PROJECT_DIR (cwd if unset) — resolve_workspace_root SSOT.
No shebang (CLAUDE.md) — ``uv run --no-project python audit_report.py [--unit ID] [--json | --pr N]``.

Flag interplay: ``--pr`` combines with ``--unit`` (posts the unit-filtered markdown);
``--pr`` + a nonexistent unit **refuses** (exit 2, nothing posted — a typo'd id must not
land as a junk PR comment); ``--pr`` + ``--json`` is a parser error (PR comments are markdown).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter

from _flow_state import resolve_workspace_root, runtime_dir, AUDIT_FILE

UNATTRIBUTED = "unattributed"


def load_entries(path: str) -> list[dict]:
    """Read the audit jsonl. Missing file → []. Malformed line → skip (tolerates partial corruption)."""
    entries: list[dict] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # malformed → skip
    except OSError:
        return []
    return entries


def _blank() -> dict:
    return {
        "denied_rules": Counter(),
        "asked_rules": Counter(),
        "skills": Counter(),
        "retries": 0,
        "tools": Counter(),
        "checks": {},  # TS-003 verifier result: {check_name: {"pass": N, "fail": M}}
    }


def aggregate(entries: list[dict]) -> dict:
    """Aggregate per unit_id (pure function — counts exactly what is in the log).

    post record (``success`` key): tools/retries/skills.
    pre-block record (``blocked_rule`` key): denied_rules / asked_rules depending on decision.
    The capture SSOT (build_entry/build_block_entry) never emits both keys together — blocked wins.
    """
    units: dict[str, dict] = {}
    for e in entries:
        unit = e.get("unit_id") or UNATTRIBUTED
        u = units.setdefault(unit, _blank())
        if "check" in e:  # TS-003 quality-gate check result (verifier result)
            stats = u["checks"].setdefault(e["check"], {"pass": 0, "fail": 0})
            stats["pass" if e.get("passed") else "fail"] += 1
            continue
        if "blocked_rule" in e:  # blocked (not executed)
            bucket = "asked_rules" if e.get("decision") == "ask" else "denied_rules"
            u[bucket][e["blocked_rule"]] += 1
            continue
        if "success" in e:  # executed tool call
            tool = e.get("tool", "")
            if tool:
                u["tools"][tool] += 1
            if not e["success"]:
                u["retries"] += 1
            if tool == "Skill" and e.get("skill"):
                u["skills"][e["skill"]] += 1
    return units


def _counts_line(label: str, counter: Counter) -> str:
    if not counter:
        return f"  {label}: -"
    items = ", ".join(f"{k}={v}" for k, v in counter.most_common())
    return f"  {label}: {items}"


def _checks_line(checks: dict) -> str:
    """verifier-result line — {check: {pass, fail}} → 'test=3p/1f, lint=2p/0f' (TS-003 AC-4)."""
    if not checks:
        return "  verify(quality-gate): -"
    items = ", ".join(
        f"{name}={s['pass']}p/{s['fail']}f" for name, s in sorted(checks.items())
    )
    return f"  verify(quality-gate): {items}"


def format_report(units: dict) -> str:
    """Human-readable text — a plain dump (no embellishment)."""
    if not units:
        return "(no measurement data)"
    lines: list[str] = []
    for unit in sorted(units):
        u = units[unit]
        lines.append(f"[{unit}]")
        lines.append(_counts_line("deny rules", u["denied_rules"]))
        lines.append(_counts_line("ask rules", u["asked_rules"]))
        lines.append(_counts_line("skills", u["skills"]))
        lines.append(f"  retries(success=false): {u['retries']}")
        lines.append(_counts_line("tools", u["tools"]))
        lines.append(_checks_line(u["checks"]))
    return "\n".join(lines)


def format_markdown(units: dict) -> str:
    """Wrap the plain text report in a markdown code block for a PR comment (A-003).

    Reuses ``format_report`` verbatim inside a fenced block so the layout survives
    rendering — no separate markdown formatter to drift out of sync.
    """
    return f"### Flow measurement audit\n\n```\n{format_report(units)}\n```"


def post_pr_comment(pr: str, body: str) -> bool:
    """Post ``body`` as a comment on PR ``pr`` via ``gh``. Returns True on success.

    Fail-open: if ``gh`` is not installed or the call fails, return False instead of
    raising — publishing an audit report must never block the PR/flow.
    """
    try:
        subprocess.run(
            ["gh", "pr", "comment", pr, "--body-file", "-"],
            input=body,
            text=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _to_jsonable(units: dict) -> dict:
    return {
        unit: {
            "denied_rules": dict(u["denied_rules"]),
            "asked_rules": dict(u["asked_rules"]),
            "skills": dict(u["skills"]),
            "retries": u["retries"],
            "tools": dict(u["tools"]),
            "checks": u["checks"],
        }
        for unit, u in units.items()
    }


def filter_unit(units: dict, unit: str) -> dict:
    """Restrict the aggregation to one unit_id. Empty dict when absent — the caller picks
    the messaging (shared by render and the --pr path so the filter cannot drift)."""
    return {k: v for k, v in units.items() if k == unit}


def missing_unit_message(unit: str) -> str:
    """Message distinct from "(no measurement data)" — stops a mistyped unit id from being
    misread as "this item had zero activity" (prevents polluting the retrospective evidence)."""
    return f"(no records for unit '{unit}' — check the id, or it was not captured)"


def render(units: dict, unit: "str | None" = None, as_json: bool = False) -> str:
    """Aggregation → output string. If unit is given, only that work item."""
    if unit is not None:
        filtered = filter_unit(units, unit)
        if not filtered:
            return missing_unit_message(unit)
        units = filtered
    return json.dumps(_to_jsonable(units), ensure_ascii=False, indent=2) if as_json else format_report(units)


def main():
    parser = argparse.ArgumentParser(description="Per-work-item measurement aggregation (hook_audit.jsonl)")
    parser.add_argument("--unit", help="Aggregate only this unit_id (all if omitted; also filters --pr)")
    parser.add_argument("--json", action="store_true", help="JSON output (not combinable with --pr)")
    parser.add_argument(
        "--pr",
        help="Post the report as a markdown comment on this PR number (via gh). "
             "Honors --unit (unit-filtered body); rejects --json (PR comments are markdown)",
    )
    args = parser.parse_args()
    if args.pr and args.json:
        parser.error("--pr posts markdown — --json cannot be combined with --pr (use --unit to narrow)")

    workspace_root = resolve_workspace_root({})
    path = os.path.join(runtime_dir(workspace_root), AUDIT_FILE)
    units = aggregate(load_entries(path))
    if args.pr:
        if args.unit is not None:
            units = filter_unit(units, args.unit)
            if not units:
                # Refuse (fail fast, documented in the module docstring): a typo'd unit id
                # must not land as a junk PR comment. Same distinct message as render().
                print(missing_unit_message(args.unit))
                sys.exit(2)
        ok = post_pr_comment(args.pr, format_markdown(units))
        print(f"posted to PR #{args.pr}" if ok else "gh unavailable — skipped PR comment (fail-open)")
        return
    print(render(units, args.unit, args.json))


if __name__ == "__main__":
    main()
