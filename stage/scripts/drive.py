#!/usr/bin/env python3
"""Plan or execute one supervised Stage driver step.

The driver selects one existing READY leaf child of the requested parent. Dry
run is the default and has no side effects. ``--execute`` runs exactly one
executor -> acceptance -> independent-review sequence and records runtime
attempt state, but never commits, closes, escalates, promotes, creates work, or
advances a parent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


# Dry-run CLI use must not create import caches alongside the shipped plugin.
if __name__ == "__main__":
    sys.dont_write_bytecode = True

STAGE_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = STAGE_ROOT / "hooks"
SCRIPTS_DIR = STAGE_ROOT / "scripts"
RETROSPECTIVE_DIR = STAGE_ROOT / "skills" / "stage-retrospective"
for import_dir in (HOOKS_DIR, SCRIPTS_DIR, RETROSPECTIVE_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from lifecycle_paths import v4_lifecycle_paths  # noqa: E402
from close_work import run_check  # noqa: E402
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    load_executors_config,
    load_limits_config,
    load_review_config,
    resolve_executor_command,
    resolve_independent_review_command,
    schema_migration_banner,
)
from stage_work import (  # noqa: E402
    WORK_FINAL_STATUSES,
    WorkItem,
    load_all_work_items,
    non_terminal_children,
)


WORK_ID_RE = re.compile(r"^W-[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9_-]*)?$")
BLOCK_RE = re.compile(r"(?m)^BLOCK:")
RECOMMEND_PASS = (
    "verification+judge passed → ready to commit + close_work"
)
RECOMMEND_RETRY = "failed, retry (attempt {attempt}/{cap})"
RECOMMEND_ESCALATE = (
    "attempt cap reached / no progress / global limit exceeded → escalate_work"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or execute one supervised Stage driver step."
    )
    parser.add_argument(
        "--project-root", default=".", help="Project root (default: cwd)."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run exactly one executor/acceptance/reviewer step.",
    )
    parser.add_argument(
        "--unattended",
        action="store_true",
        help="Run the whole ready subtree unattended on an isolated branch (requires a limits config).",
    )
    parser.add_argument(
        "--timeout", type=int, default=900, help="Per-command timeout in seconds."
    )
    parser.add_argument("target", help="Existing parent work item id (W-*).")
    return parser.parse_args()


def select_next_ready_leaf(
    target_id: str, items: list[WorkItem]
) -> WorkItem | None:
    """Choose an existing direct READY leaf child in deterministic ID order."""

    candidates = (
        item
        for item in items
        if item.parent == target_id
        and item.status not in WORK_FINAL_STATUSES
        and item.acceptance
        and not non_terminal_children(item.item_id, items)
    )
    return next(
        iter(sorted(candidates, key=lambda item: (item.item_id, item.path.as_posix()))),
        None,
    )


def new_run_state(target_id: str, now: float) -> dict[str, Any]:
    return {
        "target": target_id,
        "started_at_unix": now,
        "iteration_count": 0,
        "items": {},
    }


def load_run_state(
    path: Path, target_id: str, now: float
) -> tuple[dict[str, Any] | None, str]:
    """Load runtime state or initialize it in memory without writing."""

    if not path.exists():
        return new_run_state(target_id, now), ""
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"cannot read driver run state: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"driver run state is not valid JSON: {exc}"
    if not isinstance(state, dict):
        return None, "driver run state must be a JSON object"
    if state.get("target") != target_id:
        return None, "driver run state target does not match the requested parent"
    started_at = state.get("started_at_unix")
    if not isinstance(started_at, (int, float)) or isinstance(started_at, bool):
        return None, "driver run state started_at_unix must be a number"
    iteration_count = state.get("iteration_count")
    if type(iteration_count) is not int or iteration_count < 0:
        return None, "driver run state iteration_count must be a non-negative integer"
    item_states = state.get("items")
    if not isinstance(item_states, dict):
        return None, "driver run state items must be an object"
    for item_id, item_state in item_states.items():
        if not isinstance(item_id, str) or not isinstance(item_state, dict):
            return None, "driver run state item entries must be objects"
        attempt_count = item_state.get("attempt_count")
        fingerprint = item_state.get("last_fingerprint")
        if type(attempt_count) is not int or attempt_count < 0:
            return None, (
                f"driver run state {item_id}.attempt_count must be a "
                "non-negative integer"
            )
        if not isinstance(fingerprint, str):
            return None, (
                f"driver run state {item_id}.last_fingerprint must be a string"
            )
    return state, ""


def write_run_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically replace one target's untracked runtime state."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    try:
        temporary.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def git_diff(project_root: Path) -> str:
    """Return the current tracked diff; unavailable Git state is an empty diff."""

    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--binary"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    return result.stdout if result.returncode == 0 else ""


def fingerprint(project_root: Path, acceptance_output: list[str]) -> str:
    payload = git_diff(project_root) + "\0" + "\n".join(acceptance_output)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cap_text(limits: dict[str, int] | None, key: str) -> str:
    return str(limits[key]) if limits is not None else "unlimited"


def print_escalation(reason: str) -> None:
    print(f"Outcome: blocked — {reason}")
    print(f"Recommended next action: {RECOMMEND_ESCALATE}")


def print_plan(
    *,
    execute: bool,
    target_id: str,
    item: WorkItem,
    executor_command: str,
    reviewer_command: str,
    attempt: int,
    iteration: int,
    elapsed: float,
    limits: dict[str, int] | None,
) -> None:
    print(f"Mode: {'execute' if execute else 'dry-run'}")
    print(f"Target parent: {target_id}")
    print(f"Selected item: {item.item_id}")
    print(f"Executor: {executor_command}")
    for command in item.acceptance:
        print(f"Acceptance: {command}")
    print(f"Independent reviewer: {reviewer_command}")
    print(
        "Attempt: "
        f"{attempt}/{cap_text(limits, 'max_attempts_per_item')}"
    )
    print(f"Iteration: {iteration}/{cap_text(limits, 'max_iterations')}")
    wall_cap = (
        f"{limits['max_wall_clock_seconds']}s"
        if limits is not None
        else "unlimited"
    )
    print(f"Wall clock: {int(elapsed)}s/{wall_cap}")


def limit_blocker(
    limits: dict[str, int] | None,
    *,
    attempt: int,
    iteration: int,
    elapsed: float,
) -> str:
    if limits is None:
        return ""
    if attempt > limits["max_attempts_per_item"]:
        return "per-item attempt cap reached before execution"
    if iteration > limits["max_iterations"]:
        return "global iteration limit exceeded before execution"
    if elapsed >= limits["max_wall_clock_seconds"]:
        return "global wall-clock limit exceeded before execution"
    return ""


CLOSE_WORK = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ESCALATE_WORK = STAGE_ROOT / "scripts" / "escalate_work.py"
RETRO_ID_RE = re.compile(r"^R-(\d+)(?:-.*)?\.md$")
RETRO_SECTIONS = (
    "Work",
    "Decision points",
    "Principles applied",
    "Context that helped",
    "Context that was missing",
    "Next changes",
    "Promotion decision",
)


def run_git(project_root: Path, args: list[str]) -> tuple[bool, str]:
    """Run one git command; return (ok, combined output). Never raises."""

    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def create_run_branch(project_root: Path, target_id: str, now: float) -> tuple[str, str]:
    """Create and check out an isolated run branch; NEVER commit to the base branch.

    Returns (branch_name, error). An existing branch (idempotent re-run) is
    checked out rather than recreated.
    """

    branch = f"stage/driver/{target_id}-{int(now)}"
    exists, _ = run_git(project_root, ["rev-parse", "--verify", "--quiet", branch])
    verb = ["checkout", branch] if exists else ["checkout", "-b", branch]
    ok, out = run_git(project_root, verb)
    if not ok:
        return "", f"cannot create/checkout run branch {branch}: {out.strip()}"
    return branch, ""


def commit_item(project_root: Path, item: WorkItem) -> tuple[bool, str]:
    """Stage the item's declared scope and commit to the current (run) branch.

    An executor that wrote nothing yields an empty commit — treated as a clean
    no-op so the caller can still close a doc-only or already-satisfied item.
    """

    scope_paths = [path for path in item.scope if path]
    if scope_paths:
        ok, out = run_git(project_root, ["add", "--", *scope_paths])
        if not ok:
            return False, f"git add failed: {out.strip()}"
    ok, out = run_git(
        project_root,
        ["commit", "-m", f"driver: {item.item_id} executor output"],
    )
    if not ok and "nothing to commit" in out:
        return True, "nothing to commit"
    return (True, "") if ok else (False, f"git commit failed: {out.strip()}")


def next_retro_id(stage_root: Path) -> str:
    highest = 0
    for relative in ("work/retrospectives", "official/work/archive/retrospectives"):
        root = stage_root / relative
        for path in root.glob("R-*.md") if root.exists() else ():
            match = RETRO_ID_RE.fullmatch(path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"R-{highest + 1:08d}"


def set_frontmatter_field(text: str, name: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(name)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def write_driver_retrospective(
    stage_root: Path, item: WorkItem, evidence: str
) -> tuple[str, str]:
    """Write a machine-generated retrospective, flagged driver-generated.

    Returns (retro_id, error). The reflective retrospective is deliberately
    thin — a human reviews it when merging the run branch (DE-24, mode A).
    """

    retro_id = next_retro_id(stage_root)
    note = "driver-generated (사람 머지 검토 대상)"
    sections = {
        "Work": (
            f"{note}: 무인 드라이버가 executor 실행 후 acceptance·독립 판정을 통과시켜 "
            f"{item.item_id}을 완료했다.\n\n검증 증거:\n\n```\n{evidence[:1500]}\n```"
        ),
        "Decision points": f"{note}: 기계 실행, 별도 결정 없음.",
        "Principles applied": f"{note}: Honesty, Fail Fast, No partial completion.",
        "Context that helped": f"{note}: 항목 acceptance가 종료를 결정적으로 판정.",
        "Context that was missing": f"{note}: 반성적 회고는 사람이 브랜치 머지 시 보완.",
        "Next changes": f"{note}: 사람이 격리 브랜치를 검토·머지.",
        "Promotion decision": f"approved ({note}).",
    }
    body = f"---\nid: {retro_id}\nwork_item: {item.item_id}\n---\n\n# {retro_id} {item.item_id} 무인 드라이버 회고\n"
    for heading in RETRO_SECTIONS:
        body += f"\n## {heading}\n\n{sections[heading]}\n"
    path = stage_root / "work" / "retrospectives" / f"{retro_id}.md"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write(body)
    except OSError as exc:
        return "", f"cannot write retrospective {retro_id}: {exc}"
    return retro_id, ""


AUDIT = STAGE_ROOT / "scripts" / "audit_stage.py"


def current_card_path(stage_root: Path, item_id: str) -> Path:
    return stage_root / v4_lifecycle_paths().current_cards / f"{item_id}.md"


def mark_retrospective(stage_root: Path, item_id: str, retro_id: str) -> None:
    path = current_card_path(stage_root, item_id)
    text = path.read_text(encoding="utf-8")
    text = set_frontmatter_field(text, "retrospective", "completed")
    text = set_frontmatter_field(text, "retrospective_ref", retro_id)
    path.write_text(text, encoding="utf-8")


def close_via_close_work(
    project_root: Path, item_id: str, extra_checks: list[str], timeout: int
) -> tuple[bool, str]:
    """Reuse the reviewed close_work.py: acceptance + (autonomous) independent review + close."""

    command = [
        sys.executable,
        str(CLOSE_WORK),
        "--project-root",
        str(project_root),
        item_id,
        "--promotion",
        "approved",
        "--timeout",
        str(timeout),
    ]
    for check in extra_checks:
        command += ["--check", check]
    try:
        proc = subprocess.run(command, cwd=str(project_root), capture_output=True, text=True)
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def escalate_via_escalate_work(project_root: Path, item_id: str, reason: str) -> tuple[bool, str]:
    """Reuse the reviewed escalate_work.py: item -> blocked + a pending decision."""

    command = [
        sys.executable,
        str(ESCALATE_WORK),
        "--project-root",
        str(project_root),
        item_id,
        "--reason",
        reason,
    ]
    try:
        proc = subprocess.run(command, cwd=str(project_root), capture_output=True, text=True)
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def select_next_unattended_leaf(target_id: str, items: list[WorkItem]) -> WorkItem | None:
    """A ready leaf for unattended run: AUTONOMOUS (so close_work runs the mandatory
    independent review), non-terminal, itself a leaf, direct child of the target."""

    candidates = (
        item
        for item in items
        if item.parent == target_id
        and item.status == "active"  # not terminal, and not blocked (escalated items are not retried)
        and item.autonomous
        and item.acceptance
        and not non_terminal_children(item.item_id, items)
    )
    return next(
        iter(sorted(candidates, key=lambda item: (item.item_id, item.path.as_posix()))),
        None,
    )


def audit_check(project_root: Path) -> str:
    return f"{sys.executable} {AUDIT} --project-root {project_root}"


def close_ready_ancestors(
    project_root: Path, stage_root: Path, target_id: str, parent_id: str, timeout: int
) -> list[str]:
    """Close each ancestor up to and including the target whose children are all terminal.

    A parent has no acceptance; its verification is the audit (whole-.stage
    consistency) plus close_work's own aggregation gate (children terminal). No
    silent pass — both must hold.
    """

    closed: list[str] = []
    current = parent_id
    while current:
        items = load_all_work_items(stage_root)
        match = [item for item in items if item.item_id == current]
        if not match:
            break
        parent = match[0]
        if parent.status in WORK_FINAL_STATUSES:
            current = "" if current == target_id else parent.parent
            continue
        if non_terminal_children(current, items):
            break
        if not (parent.retrospective == "completed" and parent.retrospective_ref):
            retro_id, err = write_driver_retrospective(
                stage_root, parent, "parent aggregation: all children terminal"
            )
            if err:
                break
            mark_retrospective(stage_root, current, retro_id)
        checks = list(parent.acceptance) or [audit_check(project_root)]
        ok, _out = close_via_close_work(project_root, current, checks, timeout)
        if not ok:
            break
        closed.append(current)
        current = "" if current == target_id else parent.parent
    return closed


def run_unattended(args: argparse.Namespace, project_root: Path, stage_root: Path, now: float) -> int:
    limits, limits_error = load_limits_config(stage_root)
    if limits_error:
        print_escalation(f"limits config unusable: {limits_error}")
        return 1
    if limits is None:
        print_escalation(
            "unattended mode requires a `limits` config (absent is not unlimited here); refusing to run"
        )
        return 1

    ok, base_branch = run_git(project_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    base_branch = base_branch.strip() if ok else ""
    branch, branch_error = create_run_branch(project_root, args.target, now)
    if branch_error:
        print_escalation(branch_error)
        return 1
    print(f"Unattended run on isolated branch: {branch} (base: {base_branch or 'unknown'})")

    state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
    processed: list[str] = []
    iteration = 0
    while True:
        elapsed = max(0.0, time.time() - now)
        if elapsed >= limits["max_wall_clock_seconds"]:
            print(
                f"STOP: wall-clock limit {limits['max_wall_clock_seconds']}s reached; "
                f"{len(processed)} closed; handoff on {branch}"
            )
            return 1
        if iteration >= limits["max_iterations"]:
            print(
                f"STOP: iteration limit {limits['max_iterations']} reached; "
                f"{len(processed)} closed; handoff on {branch}"
            )
            return 1

        items = load_all_work_items(stage_root)
        item = select_next_unattended_leaf(args.target, items)
        if item is None:
            break
        iteration += 1

        executor_command, executor_error = resolve_executor_command(
            load_executors_config(stage_root), item.venue
        )
        if executor_error or not executor_command:
            escalate_via_escalate_work(
                project_root, item.item_id, executor_error or "executor command missing"
            )
            continue

        state, state_error = load_run_state(state_path, args.target, now)
        if state_error or state is None:
            print_escalation(state_error or "driver run state unavailable")
            return 1
        item_state = state["items"].get(item.item_id, {"attempt_count": 0, "last_fingerprint": ""})
        attempt = item_state["attempt_count"] + 1
        if attempt > limits["max_attempts_per_item"]:
            escalate_via_escalate_work(
                project_root,
                item.item_id,
                f"per-item attempt cap ({limits['max_attempts_per_item']}) reached",
            )
            continue

        executor_ok, executor_evidence, _raw = run_check(executor_command, args.timeout, project_root)
        current_fingerprint = fingerprint(project_root, [executor_evidence])
        commit_ok, commit_message = commit_item(project_root, item)

        no_progress = (
            bool(item_state["last_fingerprint"]) and current_fingerprint == item_state["last_fingerprint"]
        )
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        state["items"][item.item_id] = {"attempt_count": attempt, "last_fingerprint": current_fingerprint}
        write_run_state(state_path, state)

        if not commit_ok:
            escalate_via_escalate_work(project_root, item.item_id, f"commit failed: {commit_message}")
            continue

        if not (item.retrospective == "completed" and item.retrospective_ref):
            retro_id, retro_error = write_driver_retrospective(stage_root, item, executor_evidence)
            if retro_error:
                escalate_via_escalate_work(project_root, item.item_id, retro_error)
                continue
            mark_retrospective(stage_root, item.item_id, retro_id)

        close_ok, _close_out = close_via_close_work(project_root, item.item_id, [], args.timeout)
        if not close_ok:
            reason = "close failed (acceptance or independent review)"
            if no_progress or attempt >= limits["max_attempts_per_item"]:
                escalate_via_escalate_work(
                    project_root, item.item_id, f"{reason}; no progress or attempt cap reached"
                )
            else:
                print(f"[{item.item_id}] {reason}; retry {attempt}/{limits['max_attempts_per_item']}")
            continue

        processed.append(item.item_id)
        print(f"[{item.item_id}] completed on {branch}")
        close_ready_ancestors(project_root, stage_root, args.target, item.parent, args.timeout)

    print(
        f"Unattended run finished: {len(processed)} item(s) closed on isolated branch {branch}. "
        "Human review + merge required; the base branch was not modified."
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.timeout <= 0:
        print_escalation("--timeout must be a positive integer")
        return 2
    if not WORK_ID_RE.fullmatch(args.target):
        print_escalation("target must be a safe W-* work item id")
        return 2

    project_root = Path(args.project_root).expanduser().resolve()
    stage_root = project_root / ".stage"
    schema_blocker = schema_migration_banner(stage_root)
    if schema_blocker:
        print_escalation(schema_blocker)
        return 2
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        print_escalation("drive requires a schema-v4 Stage project")
        return 2

    items = load_all_work_items(stage_root)
    targets = [item for item in items if item.item_id == args.target]
    if len(targets) != 1:
        print_escalation(
            f"target parent must resolve to exactly one existing work item; found {len(targets)}"
        )
        return 1

    if args.unattended:
        return run_unattended(args, project_root, stage_root, time.time())

    item = select_next_ready_leaf(args.target, items)
    if item is None:
        direct_children = [
            child
            for child in items
            if child.parent == args.target
            and child.status not in WORK_FINAL_STATUSES
        ]
        reason = (
            "no non-terminal direct child has non-empty acceptance and leaf readiness"
            if direct_children
            else "target has no non-terminal existing direct child"
        )
        print_escalation(reason)
        return 1

    limits, limits_error = load_limits_config(stage_root)
    if limits_error:
        print_escalation(f"limits config unusable: {limits_error}")
        return 1

    executor_command, executor_error = resolve_executor_command(
        load_executors_config(stage_root), item.venue
    )
    if executor_error or not executor_command:
        print_escalation(executor_error or "executor command is missing")
        return 1

    reviewer_command, reviewer_error = resolve_independent_review_command(
        load_review_config(stage_root), item.venue
    )
    if reviewer_error or not reviewer_command:
        print_escalation(
            reviewer_error or "independent reviewer command is missing"
        )
        return 1

    state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
    now = time.time()
    state, state_error = load_run_state(state_path, args.target, now)
    if state_error or state is None:
        print_escalation(state_error or "driver run state is unavailable")
        return 1

    item_state = state["items"].get(
        item.item_id, {"attempt_count": 0, "last_fingerprint": ""}
    )
    attempt = item_state["attempt_count"] + 1
    iteration = state["iteration_count"] + 1
    elapsed = max(0.0, now - state["started_at_unix"])
    print_plan(
        execute=args.execute,
        target_id=args.target,
        item=item,
        executor_command=executor_command,
        reviewer_command=reviewer_command,
        attempt=attempt,
        iteration=iteration,
        elapsed=elapsed,
        limits=limits,
    )

    blocker = limit_blocker(
        limits, attempt=attempt, iteration=iteration, elapsed=elapsed
    )
    if blocker:
        print_escalation(blocker)
        return 1
    if not args.execute:
        print("Outcome: plan only — no commands ran and no run state was written")
        return 0

    step_ok = True
    failure = ""
    reviewer_blocked = False
    acceptance_output: list[str] = []

    executor_ok, executor_evidence, _executor_raw = run_check(
        executor_command, args.timeout, project_root
    )
    print(f"Executor result:\n{executor_evidence}")
    if not executor_ok:
        step_ok = False
        failure = "executor command failed"

    if step_ok:
        for command in item.acceptance:
            accepted, evidence, raw = run_check(
                command, args.timeout, project_root
            )
            acceptance_output.append(raw)
            print(f"Acceptance result:\n{evidence}")
            if not accepted:
                step_ok = False
                failure = "acceptance check failed"
                break

    if step_ok:
        reviewed, review_evidence, review_raw = run_check(
            reviewer_command, args.timeout, project_root
        )
        print(f"Independent reviewer result:\n{review_evidence}")
        reviewer_blocked = bool(BLOCK_RE.search(review_raw))
        if reviewer_blocked or not reviewed:
            step_ok = False
            failure = (
                "independent reviewer BLOCK verdict"
                if reviewer_blocked
                else "independent reviewer command failed"
            )

    current_fingerprint = fingerprint(project_root, acceptance_output)
    previous_fingerprint = item_state["last_fingerprint"]
    no_progress = (
        bool(previous_fingerprint)
        and current_fingerprint == previous_fingerprint
    )
    state["iteration_count"] = iteration
    state["items"][item.item_id] = {
        "attempt_count": attempt,
        "last_fingerprint": current_fingerprint,
    }
    try:
        write_run_state(state_path, state)
    except OSError as exc:
        print_escalation(f"cannot persist driver run state after execution: {exc}")
        return 1

    elapsed_after = max(0.0, time.time() - state["started_at_unix"])
    escalation_reasons: list[str] = []
    if no_progress:
        escalation_reasons.append("NO-PROGRESS fingerprint matched the previous attempt")
    if reviewer_blocked:
        escalation_reasons.append(failure)
    if limits is not None:
        if not step_ok and attempt >= limits["max_attempts_per_item"]:
            escalation_reasons.append("per-item attempt cap reached")
        if not step_ok and iteration >= limits["max_iterations"]:
            escalation_reasons.append("global iteration limit reached")
        if elapsed_after >= limits["max_wall_clock_seconds"]:
            escalation_reasons.append("global wall-clock limit exceeded")

    if escalation_reasons:
        print_escalation("; ".join(escalation_reasons))
        return 1
    if step_ok:
        print("Outcome: executor, acceptance, and independent reviewer passed")
        print(f"Recommended next action: {RECOMMEND_PASS}")
        return 0

    print(f"Outcome: {failure}")
    print(
        "Recommended next action: "
        + RECOMMEND_RETRY.format(
            attempt=attempt,
            cap=cap_text(limits, "max_attempts_per_item"),
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
