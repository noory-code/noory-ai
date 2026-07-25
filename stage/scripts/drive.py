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
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


def git_untracked_paths(project_root: Path) -> tuple[set[str], str]:
    """Return untracked, non-ignored file paths without changing the index."""

    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=str(project_root),
            capture_output=True,
        )
    except OSError as exc:
        return set(), str(exc)
    if result.returncode != 0:
        return set(), (
            result.stderr.decode(errors="replace").strip()
            or f"git ls-files failed with exit code {result.returncode}"
        )
    return {
        os.fsdecode(raw_path)
        for raw_path in result.stdout.split(b"\0")
        if raw_path
    }, ""


def git_diff(project_root: Path) -> str:
    """Return staged, unstaged, and untracked changes for progress detection."""

    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--binary", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    if result.returncode == 0:
        tracked_diff = result.stdout
    else:
        unborn_diffs: list[str] = []
        for extra_args in (["--cached"], []):
            try:
                unborn_result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--no-ext-diff",
                        "--binary",
                        *extra_args,
                    ],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                )
            except OSError:
                return ""
            if unborn_result.returncode != 0:
                return ""
            unborn_diffs.append(unborn_result.stdout)
        tracked_diff = (
            "\0UNBORN-STAGED\0"
            + unborn_diffs[0]
            + "\0UNBORN-UNSTAGED\0"
            + unborn_diffs[1]
        )

    untracked_paths, untracked_error = git_untracked_paths(project_root)
    if untracked_error:
        return tracked_diff
    untracked: list[str] = []
    for relative in sorted(untracked_paths):
        path = project_root / relative
        try:
            content = path.read_bytes()
        except OSError as exc:
            digest = f"unreadable:{type(exc).__name__}"
        else:
            digest = hashlib.sha256(content).hexdigest()
        untracked.append(f"{relative}\0{digest}")
    return tracked_diff + "\0UNTRACKED\0" + "\0".join(untracked)


def git_index_path(project_root: Path) -> tuple[Path | None, str]:
    """Resolve the repository index, or return None when the root is not a Git worktree."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", "index"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return None, str(exc)
    if result.returncode != 0:
        return None, ""
    raw_path = Path(result.stdout.strip())
    return (
        raw_path if raw_path.is_absolute() else project_root / raw_path,
        "",
    )


def restore_git_index(
    index_path: Path, snapshot_path: Path, existed: bool
) -> str:
    """Restore the exact pre-executor index state without touching the worktree."""

    replacement = index_path.with_name(f"{index_path.name}.stage-driver-restore")
    try:
        if existed:
            shutil.copyfile(snapshot_path, replacement)
            replacement.replace(index_path)
        else:
            index_path.unlink(missing_ok=True)
    except OSError as exc:
        return str(exc)
    finally:
        replacement.unlink(missing_ok=True)
    return ""


def prepare_reviewer_index(
    project_root: Path,
    review_index_path: Path,
    new_untracked_paths: set[str],
) -> tuple[dict[str, str] | None, str]:
    """Expose executor-created files to Git diff through a disposable index."""

    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(review_index_path.resolve())
    if new_untracked_paths:
        try:
            result = subprocess.run(
                [
                    "git",
                    "add",
                    "--intent-to-add",
                    "--",
                    *sorted(new_untracked_paths),
                ],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                env=env,
            )
        except OSError as exc:
            return None, str(exc)
        if result.returncode != 0:
            return None, result.stderr.strip() or "git add --intent-to-add failed"
    return env, ""


def fingerprint(project_root: Path, acceptance_output: list[str]) -> str:
    payload = git_diff(project_root) + "\0" + "\n".join(acceptance_output)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def executor_environment(item: WorkItem, project_root: Path) -> dict[str, str]:
    """Return the inherited environment plus the selected work item context."""

    env = os.environ.copy()
    env.update(
        {
            "STAGE_WORK_ITEM": item.item_id,
            "STAGE_WORK_ITEM_PATH": str(item.path.resolve()),
            "STAGE_PROJECT_ROOT": str(project_root.resolve()),
        }
    )
    return env


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


def run_git(project_root: Path, args: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Run one git command; return (ok, combined output). Never raises."""

    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"git {' '.join(args[:2])} timed out after {timeout}s"
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

    if not current_branch(project_root).startswith("stage/driver/"):
        return False, "refusing item commit: HEAD is not on a stage/driver run branch"
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
    # Neutral wording: this is written BEFORE close_work verifies. It must not
    # claim success — the item's Verification (stamped by close_work) is the
    # source of truth for whether acceptance and the independent review passed.
    sections = {
        "Work": (
            f"{note}: 무인 드라이버가 {item.item_id}의 executor를 실행하고 결과를 커밋했다. "
            "acceptance·독립 판정의 실제 통과 여부와 최종 완료는 항목의 Verification"
            f"(close_work가 기록)이 정본이다.\n\nexecutor 출력:\n\n```\n{evidence[:1500]}\n```"
        ),
        "Decision points": f"{note}: 기계 실행, 별도 결정 없음.",
        "Principles applied": f"{note}: Honesty, Fail Fast, No partial completion.",
        "Context that helped": f"{note}: 항목 acceptance가 종료를 결정적으로 판정.",
        "Context that was missing": f"{note}: 반성적 회고는 사람이 브랜치 머지 시 보완.",
        "Next changes": f"{note}: 사람이 격리 브랜치를 검토·머지.",
        "Promotion decision": (
            f"{note}: 항목 Verification의 결과를 따른다(close_work가 acceptance·독립 판정 통과 시에만 completed로 스탬프)."
        ),
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
        proc = subprocess.run(
            command, cwd=str(project_root), capture_output=True, text=True, timeout=timeout + 60
        )
    except subprocess.TimeoutExpired:
        return False, f"close_work timed out after {timeout + 60}s"
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def escalate_via_escalate_work(
    project_root: Path, item_id: str, reason: str, timeout: int = 120
) -> tuple[bool, str]:
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
        proc = subprocess.run(
            command, cwd=str(project_root), capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, f"escalate_work timed out after {timeout}s"
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def is_in_subtree(item: WorkItem, target_id: str, by_id: dict[str, WorkItem]) -> bool:
    """Whether `item` is a descendant of `target_id` (following the parent chain).

    Bounded by the number of items so a malformed cycle cannot spin forever.
    """

    seen: set[str] = set()
    parent = item.parent
    for _ in range(len(by_id) + 1):
        if not parent or parent in seen:
            return False
        if parent == target_id:
            return True
        seen.add(parent)
        ancestor = by_id.get(parent)
        if ancestor is None:
            return False
        parent = ancestor.parent
    return False


def select_next_unattended_leaf(target_id: str, items: list[WorkItem]) -> WorkItem | None:
    """A ready leaf anywhere in the target's subtree: AUTONOMOUS (so close_work runs the
    mandatory independent review), `active` (not terminal, not blocked — escalated items
    are not retried), a leaf (no non-terminal children), and a descendant of the target."""

    by_id = {item.item_id: item for item in items}
    candidates = (
        item
        for item in items
        if item.status == "active"
        and item.autonomous
        and item.acceptance
        and not non_terminal_children(item.item_id, items)
        and is_in_subtree(item, target_id, by_id)
    )
    return next(
        iter(sorted(candidates, key=lambda item: (item.item_id, item.path.as_posix()))),
        None,
    )


def audit_check(project_root: Path) -> str:
    return f"{sys.executable} {AUDIT} --project-root {project_root}"


def close_ready_ancestors(
    project_root: Path, stage_root: Path, target_id: str, parent_id: str, timeout: int
) -> tuple[list[str], str]:
    """Close each ancestor up to and including the target whose children are all terminal.

    Returns (closed_ids, error). A non-empty error means a parent that SHOULD have
    closed did not (retrospective or close failed) — the caller must fail closed;
    stopping because a parent still has non-terminal children is normal, not an error.

    A parent has no acceptance; its verification is the audit (whole-.stage
    consistency) plus close_work's own aggregation gate (children terminal) — its
    children were each independently reviewed (DE-00000027). No silent pass.
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
            break  # normal: this parent waits for its other children
        if not (parent.retrospective == "completed" and parent.retrospective_ref):
            retro_id, err = write_driver_retrospective(
                stage_root, parent, "parent aggregation: all children terminal"
            )
            if err:
                return closed, f"{current}: {err}"
            mark_retrospective(stage_root, current, retro_id)
        checks = [audit_check(project_root), *parent.acceptance]
        ok, out = close_via_close_work(project_root, current, checks, timeout)
        if not ok:
            return closed, f"{current}: parent close failed: {out.strip()[:200]}"
        closed.append(current)
        current = "" if current == target_id else parent.parent
    return closed, ""


def current_branch(project_root: Path) -> str:
    ok, out = run_git(project_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip() if ok else ""


def worktree_clean(project_root: Path) -> bool:
    ok, out = run_git(project_root, ["status", "--porcelain"])
    return ok and out.strip() == ""


def discard_worktree(project_root: Path) -> None:
    """Drop a failed attempt's uncommitted changes so the next iteration starts clean."""

    run_git(project_root, ["checkout", "--", "."])
    run_git(project_root, ["clean", "-fdq"])


def commit_lifecycle(project_root: Path, message: str) -> tuple[bool, str]:
    """Commit the Stage lifecycle records (.stage/) to the run branch — never the base branch."""

    if not current_branch(project_root).startswith("stage/driver/"):
        return False, "refusing lifecycle commit: HEAD is not on a stage/driver run branch"
    ok, out = run_git(project_root, ["add", "--", ".stage"])
    if not ok:
        return False, f"git add .stage failed: {out.strip()}"
    ok, out = run_git(project_root, ["commit", "-m", message])
    if not ok and "nothing to commit" in out:
        return True, "nothing to commit"
    return (True, "") if ok else (False, f"git commit failed: {out.strip()}")


def remaining_timeout(now: float, wall_clock: int, per_command: int) -> int:
    return max(1, min(per_command, int(wall_clock - (time.time() - now))))


def escalate_and_commit(project_root: Path, item_id: str, reason: str, timeout: int) -> bool:
    """Escalate an item to blocked and commit the resulting lifecycle to the run branch.

    Returns False when escalation itself failed — the run must stop, because the item
    would otherwise stay `active` and be retried without bound.
    """

    ok, out = escalate_via_escalate_work(project_root, item_id, reason, timeout)
    if not ok:
        print_escalation(
            f"escalation of {item_id} FAILED ({out.strip()[:200]}); stopping run to avoid a stuck loop"
        )
        return False
    lifecycle_ok, lifecycle_out = commit_lifecycle(
        project_root, f"driver: {item_id} escalated (lifecycle)"
    )
    if not lifecycle_ok:
        print_escalation(
            f"cannot commit escalation lifecycle for {item_id}: {lifecycle_out.strip()[:200]}"
        )
        return False
    return True


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
    # A dirty index/worktree would leak unrelated changes into item commits.
    if not worktree_clean(project_root):
        print_escalation("working tree/index is not clean; commit or stash before an unattended run")
        return 1

    base_branch = current_branch(project_root)
    branch, branch_error = create_run_branch(project_root, args.target, now)
    if branch_error:
        print_escalation(branch_error)
        return 1
    print(f"Unattended run on isolated branch: {branch} (base: {base_branch or 'unknown'})")

    wall = limits["max_wall_clock_seconds"]
    cap = limits["max_attempts_per_item"]
    state_path = stage_root / ".runtime" / "driver" / f"{args.target}.json"
    processed: list[str] = []
    iteration = 0
    while True:
        if time.time() - now >= wall:
            print(f"STOP: wall-clock limit {wall}s reached; {len(processed)} closed; handoff on {branch}")
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

        # Safety: never leave the isolated branch (an executor could switch it).
        if current_branch(project_root) != branch:
            print_escalation(f"HEAD left the run branch {branch}; aborting to protect the base branch")
            return 1

        cmd_timeout = remaining_timeout(now, wall, args.timeout)

        executor_command, executor_error = resolve_executor_command(
            load_executors_config(stage_root), item.venue
        )
        if executor_error or not executor_command:
            if not escalate_and_commit(
                project_root, item.item_id, executor_error or "executor command missing", cmd_timeout
            ):
                return 1
            continue

        state, state_error = load_run_state(state_path, args.target, now)
        if state_error or state is None:
            print_escalation(state_error or "driver run state unavailable")
            return 1
        item_state = state["items"].get(item.item_id, {"attempt_count": 0, "last_fingerprint": ""})
        attempt = item_state["attempt_count"] + 1
        if attempt > cap:
            if not escalate_and_commit(
                project_root, item.item_id, f"per-item attempt cap ({cap}) reached", cmd_timeout
            ):
                return 1
            continue

        executor_ok, executor_evidence, _raw = run_check(
            executor_command,
            cmd_timeout,
            project_root,
            env=executor_environment(item, project_root),
        )
        current_fingerprint = fingerprint(project_root, [executor_evidence])
        no_progress = (
            bool(item_state["last_fingerprint"]) and current_fingerprint == item_state["last_fingerprint"]
        )
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        state["items"][item.item_id] = {"attempt_count": attempt, "last_fingerprint": current_fingerprint}
        write_run_state(state_path, state)

        # A FAILED executor must never proceed to commit/close. Discard the failed
        # attempt's partial output, then retry or escalate.
        if not executor_ok:
            discard_worktree(project_root)
            if no_progress or attempt >= cap:
                if not escalate_and_commit(
                    project_root, item.item_id, "executor failed; no progress or attempt cap", cmd_timeout
                ):
                    return 1
            else:
                print(f"[{item.item_id}] executor failed; retry {attempt}/{cap}")
            continue

        if current_branch(project_root) != branch:
            print_escalation(f"HEAD left the run branch {branch}; aborting")
            return 1

        commit_ok, commit_message = commit_item(project_root, item)
        if not commit_ok:
            discard_worktree(project_root)
            if not escalate_and_commit(
                project_root, item.item_id, f"commit failed: {commit_message}", cmd_timeout
            ):
                return 1
            continue

        if not (item.retrospective == "completed" and item.retrospective_ref):
            retro_id, retro_error = write_driver_retrospective(stage_root, item, executor_evidence)
            if retro_error:
                if not escalate_and_commit(project_root, item.item_id, retro_error, cmd_timeout):
                    return 1
                continue
            mark_retrospective(stage_root, item.item_id, retro_id)

        close_ok, _close_out = close_via_close_work(project_root, item.item_id, [], cmd_timeout)
        if not close_ok:
            reason = "close failed (acceptance or independent review)"
            if no_progress or attempt >= cap:
                if not escalate_and_commit(
                    project_root, item.item_id, f"{reason}; no progress or attempt cap reached", cmd_timeout
                ):
                    return 1
            else:
                # Persist the retrospective/lifecycle so a retry does not recreate it.
                lc_ok, lc_msg = commit_lifecycle(
                    project_root, f"driver: {item.item_id} pre-close lifecycle (retry)"
                )
                if not lc_ok:
                    print_escalation(
                        f"cannot commit pre-close lifecycle for {item.item_id}: "
                        f"{lc_msg.strip()[:200]}"
                    )
                    return 1
                print(f"[{item.item_id}] {reason}; retry {attempt}/{cap}")
            continue

        # Commit the lifecycle records (card completed, retrospective, indexes) to the run
        # branch, so a merge carries the Stage bookkeeping — not only the executor output.
        lc_ok, lc_msg = commit_lifecycle(project_root, f"driver: {item.item_id} closed (lifecycle)")
        if not lc_ok:
            print_escalation(f"cannot commit lifecycle for {item.item_id}: {lc_msg}")
            return 1
        processed.append(item.item_id)
        print(f"[{item.item_id}] completed on {branch}")

        _closed, anc_error = close_ready_ancestors(
            project_root, stage_root, args.target, item.parent, cmd_timeout
        )
        lc_ok, lc_msg = commit_lifecycle(
            project_root, f"driver: {item.item_id} ancestor aggregation (lifecycle)"
        )
        if not lc_ok:
            print_escalation(
                f"cannot commit ancestor lifecycle for {item.item_id}: {lc_msg.strip()[:200]}"
            )
            return 1
        if anc_error:
            print_escalation(f"parent aggregation-close failed: {anc_error}; handoff on {branch}")
            return 1

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
    executor_untracked_paths: set[str] = set()

    index_path, index_error = git_index_path(project_root)
    if index_error:
        print_escalation(f"cannot resolve Git index before execution: {index_error}")
        return 1
    untracked_before: set[str] = set()
    if index_path is not None:
        untracked_before, untracked_error = git_untracked_paths(project_root)
        if untracked_error:
            print_escalation(
                f"cannot inspect untracked files before execution: {untracked_error}"
            )
            return 1

    with tempfile.TemporaryDirectory(prefix="stage-drive-index-") as temporary:
        temporary_root = Path(temporary)
        original_index = temporary_root / "original-index"
        review_index = temporary_root / "review-index"
        index_existed = bool(index_path is not None and index_path.is_file())
        if index_existed and index_path is not None:
            try:
                shutil.copyfile(index_path, original_index)
            except OSError as exc:
                print_escalation(f"cannot snapshot Git index before execution: {exc}")
                return 1

        executor_ok, executor_evidence, _executor_raw = run_check(
            executor_command,
            args.timeout,
            project_root,
            env=executor_environment(item, project_root),
        )

        if index_path is not None:
            snapshot_error = ""
            try:
                if index_path.is_file():
                    shutil.copyfile(index_path, review_index)
                elif index_existed:
                    shutil.copyfile(original_index, review_index)
            except OSError as exc:
                snapshot_error = str(exc)
            finally:
                restore_error = restore_git_index(
                    index_path, original_index, index_existed
                )
            if snapshot_error or restore_error:
                index_failures: list[str] = []
                if snapshot_error:
                    index_failures.append(
                        f"cannot snapshot executor Git index: {snapshot_error}"
                    )
                if restore_error:
                    index_failures.append(
                        f"cannot restore Git index after execution: {restore_error}"
                    )
                print_escalation("; ".join(index_failures))
                return 1

        print(f"Executor result:\n{executor_evidence}")
        if not executor_ok:
            step_ok = False
            failure = "executor command failed"
        elif index_path is not None:
            untracked_after, untracked_error = git_untracked_paths(project_root)
            if untracked_error:
                step_ok = False
                failure = (
                    "cannot inspect executor-created files before review: "
                    f"{untracked_error}"
                )
            else:
                executor_untracked_paths = untracked_after - untracked_before

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
            reviewer_env: dict[str, str] | None = None
            if index_path is not None:
                if not review_index.is_file():
                    step_ok = False
                    failure = "cannot prepare disposable Git index for review"
                else:
                    reviewer_env, reviewer_index_error = prepare_reviewer_index(
                        project_root,
                        review_index,
                        executor_untracked_paths,
                    )
                    if reviewer_index_error:
                        step_ok = False
                        failure = (
                            "cannot prepare executor-created files for review: "
                            f"{reviewer_index_error}"
                        )

            if step_ok:
                reviewed, review_evidence, review_raw = run_check(
                    reviewer_command,
                    args.timeout,
                    project_root,
                    env=reviewer_env,
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
