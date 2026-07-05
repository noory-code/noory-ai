"""Quality gate adapter CLI (TS-003) — invoke project-declared checks, record, minimal failure action.

Reads settings.json ``checks`` (free-form check names + ``required``; legacy ``commands`` /
``required_checks`` accepted) via ``read_quality_commands``, runs the declared checks via
subprocess (``shell=False`` — security + Windows differences), and records the result as a
first-class ``check`` record in ``hook_audit.jsonl`` (aggregated by audit_report — AC-4).
If any required check fails, it blocks and stops with the **minimal failure action**
(non-zero exit + stderr report). A full failure decision policy (retry, partial pass, bypass) is a
non-goal — minimal action only here.

  run    → run and record declared checks. 1+ required failures → exit 1 + report / otherwise exit 0.
           0 declared checks (checks unset) → no-op pass (exit 0) — quality gate disabled (fail-safe).

Workspace root = CLAUDE_PROJECT_DIR (cwd if unset) — resolve_workspace_root SSOT.
No shebang (CLAUDE.md) — ``uv run --no-project python quality_gate_cli.py run``.
Independent of the enforcement hook (hook_pre_tool_validate.py) — a separate CLI (minimal failure action, not deny).
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone

from _flow_state import (
    active_unit_id,
    append_audit,
    read_quality_commands,
    resolve_workspace_root,
)


def _to_argv(cmd: "str | list") -> "list[str]":
    """Command to an argv list. **A list is used as-is** (OS-independent — the project splits it itself),
    **a str is split with OS-aware ``shlex.split``** (POSIX uses posix=True, Windows uses posix=False to
    preserve backslash paths). M-1: fixes the defect where a fixed POSIX split broke Windows paths (`C:\\...`)."""
    if isinstance(cmd, list):
        return [str(x) for x in cmd]
    return shlex.split(cmd, posix=(os.name != "nt"))


def _run_check(name: str, cmd: "str | list", workspace_root: str) -> "tuple[bool, int]":
    """Run one check → (passed, returncode). ``shell=False`` (argv list — blocks shell injection + OS differences).

    A command may be a str (OS-aware split) or an argv list (as-is) — `_to_argv`.
    A failure to run at all (missing command, etc.) is recorded as passed=False, returncode=-1."""
    try:
        proc = subprocess.run(_to_argv(cmd), cwd=workspace_root, shell=False)
        return proc.returncode == 0, proc.returncode
    except (OSError, ValueError) as exc:
        print(f"[quality-gate] {name} failed to run: {exc}", file=sys.stderr)
        return False, -1


def cmd_run(workspace_root: str) -> int:
    cmds = read_quality_commands(workspace_root)
    declared = list(cmds["checks"].items())  # free-form names, declaration order preserved
    if not declared:
        print("[quality-gate] No declared checks (settings.checks unset) — pass (no-op).")
        return 0

    unit = active_unit_id(workspace_root)
    results: dict[str, bool] = {}
    for name, cmd in declared:
        passed, returncode = _run_check(name, cmd, workspace_root)
        results[name] = passed
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "check": name,
            "cmd": cmd,
            "returncode": returncode,
            "passed": passed,
        }
        if unit:
            entry["unit_id"] = unit
        append_audit(workspace_root, entry)  # hook_audit.jsonl — aggregated by audit_report (AC-4)

    summary = ", ".join(f"{n}={'pass' if p else 'FAIL'}" for n, p in results.items())
    print(f"[quality-gate] Check result: {summary}")

    # M-2: required but command undeclared = **config error** (distinct from check failure) / failure after running = check failure.
    required = cmds["required_checks"]
    misconfigured = [c for c in required if c not in results]   # command undeclared (not run)
    failed = [c for c in required if c in results and not results[c]]  # ran and failed
    if misconfigured:
        print(
            f"[quality-gate] ⚠ config error: required checks {', '.join(misconfigured)} have no command "
            "declared in settings.commands — fix the config (separate from a check failure).",
            file=sys.stderr,
        )
    if failed:
        print(
            f"[quality-gate] ❌ required check failed: {', '.join(failed)} — block and stop (minimal failure action).",
            file=sys.stderr,
        )
    if misconfigured or failed:
        return 1
    print("[quality-gate] ✅ Required checks passed.")
    return 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # prevent Windows cp949 mojibake
    parser = argparse.ArgumentParser(prog="quality_gate_cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="run and record declared checks; minimal failure action")
    args = parser.parse_args()

    workspace_root = resolve_workspace_root({})
    if args.cmd == "run":
        sys.exit(cmd_run(workspace_root))


if __name__ == "__main__":
    main()
