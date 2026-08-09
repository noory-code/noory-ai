#!/usr/bin/env python3
"""Land one completed Stage run from its worktree into the project checkout."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = SCRIPTS_DIR.parent / "hooks"
for import_dir in (SCRIPTS_DIR, HOOKS_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from drive_parallel import (  # noqa: E402
    WorktreeSpec,
    cleanup_worktree,
    registered_worktrees,
    run_git,
)
from lifecycle_paths import v4_lifecycle_paths  # noqa: E402
from stage_records import resolve_retrospective_ref  # noqa: E402
from stage_work import (  # noqa: E402
    WORK_FINAL_STATUSES,
    WorkItem,
    item_completion_blockers,
    item_is_completed,
    item_matches_path,
    load_work_items,
)


TEAMMATE_BRANCH_PREFIX = "stage/teammate/"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Commit, merge, and clean up one completed Stage run."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Clean Git checkout that will receive the run (default: cwd).",
    )
    parser.add_argument(
        "--worktree",
        required=True,
        help="Registered Git worktree containing the completed run.",
    )
    parser.add_argument("target", help="Completed W-* work item ID named by the run branch.")
    return parser.parse_args(argv)


def error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def git_output(root: Path, args: list[str], purpose: str) -> tuple[str, str]:
    status, output = run_git(root, args)
    if status != 0:
        detail = output.strip() or f"git exited with status {status}"
        return "", f"{purpose}: {detail}"
    return output, ""


def validate_git_root(project_root: Path) -> str:
    output, failure = git_output(
        project_root,
        ["rev-parse", "--show-toplevel"],
        "project root is not a Git worktree",
    )
    if failure:
        return failure
    if Path(output.strip()).resolve() != project_root:
        return f"project root must be the Git worktree root: {output.strip()}"
    return ""


def validate_clean_project(project_root: Path) -> str:
    output, failure = git_output(
        project_root,
        ["status", "--porcelain", "--untracked-files=normal"],
        "cannot inspect project checkout status",
    )
    if failure:
        return failure
    if output:
        return "project checkout is dirty; commit or stash its changes before landing a run"
    return ""


def branch_names_target(branch: str, target: str) -> bool:
    return (
        branch.startswith(f"stage/driver/{target}-")
        or branch == f"stage/worktree/{target}"
        or branch.startswith(f"{TEAMMATE_BRANCH_PREFIX}{target}-")
    )


def resolve_run_branch(project_root: Path, worktree: Path, target: str) -> tuple[str, str]:
    registrations, failure = registered_worktrees(project_root)
    if failure:
        return "", failure
    branch = registrations.get(worktree)
    if branch is None:
        if worktree.exists() or worktree.is_symlink():
            return "", f"run path is not a registered Git worktree: {worktree}"
        branches, failure = git_output(
            project_root,
            ["for-each-ref", "--format=%(refname:short)", "refs/heads"],
            "cannot inspect retained run branches",
        )
        if failure:
            return "", failure
        candidates = [
            candidate
            for candidate in branches.splitlines()
            if branch_names_target(candidate.strip(), target)
        ]
        if len(candidates) != 1:
            return "", (
                f"run path is absent and {target} resolves to {len(candidates)} retained "
                "run branches"
            )
        branch = candidates[0]
        try:
            worktree.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return "", f"cannot create run worktree parent {worktree.parent}: {exc}"
        status, output = run_git(
            project_root,
            ["worktree", "add", str(worktree), branch],
        )
        if status != 0:
            return "", f"cannot restore retained run worktree: {output.strip()}"
    if not branch_names_target(branch, target):
        return "", f"run branch `{branch or '(detached HEAD)'}` does not name {target}"
    return branch, ""


def work_item_chain(
    items: list[WorkItem],
    target: str,
) -> tuple[WorkItem | None, list[WorkItem], str]:
    matching = [item for item in items if item.item_id == target]
    if len(matching) != 1:
        return None, [], f"current work item {target} resolved {len(matching)} times"
    selected = matching[0]
    by_id = {item.item_id: item for item in items}
    closed = [selected]
    seen = {target}
    parent_id = selected.parent
    while parent_id:
        if parent_id in seen:
            return None, [], f"work hierarchy cycle reaches {parent_id}"
        seen.add(parent_id)
        parent = by_id.get(parent_id)
        if parent is None:
            return None, [], f"ancestor work item does not exist: {parent_id}"
        if parent.status not in WORK_FINAL_STATUSES:
            break
        closed.append(parent)
        parent_id = parent.parent
    return selected, closed, ""


def validate_closed_item(
    project_root: Path,
    stage_root: Path,
    item: WorkItem,
) -> tuple[Path | None, str]:
    if item.status not in {"completed", "rejected"}:
        return None, f"{item.item_id}: status `{item.status}` is not final"
    if item_is_completed(item):
        blockers = item_completion_blockers(item)
        if blockers:
            return None, "; ".join(blockers)
    if item.retrospective != "completed":
        return None, f"{item.item_id}: retrospective `{item.retrospective}` is not completed"
    if not item.retrospective_ref:
        return None, f"{item.item_id}: retrospective_ref is empty"
    retrospective = resolve_retrospective_ref(
        project_root,
        stage_root,
        item.retrospective_ref,
    )
    if not retrospective.is_file():
        return None, f"{item.item_id}: retrospective file does not exist: {retrospective}"
    try:
        retrospective.resolve().relative_to(project_root)
    except ValueError:
        return None, f"{item.item_id}: retrospective file is outside the run worktree"
    return retrospective, ""


def changed_paths_against(project_root: Path, basis: str) -> tuple[list[str], str]:
    committed, failure = git_output(
        project_root,
        ["diff", "--name-only", "-z", f"{basis}...HEAD"],
        "cannot inspect committed run changes",
    )
    if failure:
        return [], failure
    tracked, failure = git_output(
        project_root,
        ["diff", "--name-only", "-z", "HEAD"],
        "cannot inspect uncommitted run changes",
    )
    if failure:
        return [], failure
    untracked, failure = git_output(
        project_root,
        ["ls-files", "--others", "--exclude-standard", "-z"],
        "cannot inspect untracked run paths",
    )
    if failure:
        return [], failure
    return sorted(
        set(filter(None, (committed + tracked + untracked).split("\0")))
    ), ""


def staged_paths(project_root: Path) -> tuple[list[str], str]:
    output, failure = git_output(
        project_root,
        ["diff", "--cached", "--name-only", "-z"],
        "cannot inspect staged run paths",
    )
    if failure:
        return [], failure
    return sorted(filter(None, output.split("\0"))), ""


def allowed_lifecycle_paths(
    project_root: Path,
    closed_items: list[WorkItem],
    retrospectives: list[Path],
) -> set[str]:
    lifecycle = v4_lifecycle_paths()
    exact = {
        f".stage/{lifecycle.active_index}",
        f".stage/{lifecycle.review_index}",
    }
    for item in closed_items:
        exact.add(item.path.resolve().relative_to(project_root).as_posix())
    for retrospective in retrospectives:
        exact.add(retrospective.resolve().relative_to(project_root).as_posix())
    return exact


def outside_allowance(
    project_root: Path,
    target: WorkItem,
    exact_paths: set[str],
    paths: list[str],
) -> list[str]:
    lifecycle = v4_lifecycle_paths()
    current_cards = f".stage/{lifecycle.current_cards}/"
    current_retrospectives = f".stage/{lifecycle.current_retrospectives}/"

    def allowed(path: str) -> bool:
        if path in exact_paths:
            return True
        if path == ".stage/official" or path.startswith(".stage/official/"):
            return False
        if path.startswith(current_cards) or path.startswith(current_retrospectives):
            return False
        return item_matches_path(target, path, project_root)

    return [
        path
        for path in paths
        if not allowed(path)
    ]


def commit_message(subject: str, target: str, branch: str) -> str:
    return f"{subject}\n\nWork-Item: {target}\nSource-Branch: {branch}"


def copy_run_log(project_root: Path, worktree: Path, target: str) -> str:
    relative = Path(".stage/.runtime/driver/logs") / f"{target}.md"
    source = worktree / relative
    destination = project_root / relative
    if not source.is_file():
        if destination.is_file():
            return ""
        return f"run log does not exist in either checkout: {source}"
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    except OSError as exc:
        return f"cannot copy run log to project checkout: {exc}"
    return ""


def abort_merge(project_root: Path) -> str:
    status, output = run_git(project_root, ["merge", "--abort"])
    if status == 0:
        return ""
    return output.strip() or f"git exited with status {status}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    worktree = Path(args.worktree).expanduser().resolve()
    target_id = args.target.strip()
    if project_root == worktree:
        return error("project checkout and run worktree must be different paths")

    for failure in (validate_git_root(project_root), validate_clean_project(project_root)):
        if failure:
            return error(failure)

    branch, failure = resolve_run_branch(project_root, worktree, target_id)
    if failure:
        return error(failure)

    items = load_work_items(worktree / ".stage")
    target, closed_items, failure = work_item_chain(items, target_id)
    if failure or target is None:
        return error(failure)

    retrospectives: list[Path] = []
    for item in closed_items:
        retrospective, failure = validate_closed_item(worktree, worktree / ".stage", item)
        if failure or retrospective is None:
            return error(failure)
        retrospectives.append(retrospective)

    exact_paths = allowed_lifecycle_paths(worktree, closed_items, retrospectives)
    staged, failure = staged_paths(worktree)
    if failure:
        return error(failure)
    outside = outside_allowance(worktree, target, exact_paths, staged)
    if outside:
        return error(
            "path(s) already staged outside the landing allowance: " + ", ".join(outside)
        )

    main_head, failure = git_output(
        project_root,
        ["rev-parse", "HEAD"],
        "cannot resolve project HEAD",
    )
    if failure:
        return error(failure)
    main_head = main_head.strip()
    changed, failure = changed_paths_against(worktree, main_head)
    if failure:
        return error(failure)
    outside = outside_allowance(worktree, target, exact_paths, changed)
    if outside:
        return error("path(s) outside the landing allowance: " + ", ".join(outside))

    if changed:
        status, output = run_git(worktree, ["add", "-A", "--", *changed])
        if status != 0:
            return error(f"cannot stage landing paths: {output.strip()}")

    landing_message = commit_message(
        f"stage: prepare {target_id} for landing",
        target_id,
        branch,
    )
    status, output = run_git(worktree, ["commit", "--allow-empty", "-m", landing_message])
    if status != 0:
        return error(f"cannot commit run worktree: {output.strip()}")

    failure = copy_run_log(project_root, worktree, target_id)
    if failure:
        return error(failure)

    status, output = run_git(
        project_root,
        ["merge", "--no-ff", "--no-commit", branch],
    )
    if status != 0:
        abort_failure = abort_merge(project_root)
        suffix = f"; merge abort also failed: {abort_failure}" if abort_failure else ""
        return error(f"merge conflict or merge failure: {output.strip()}{suffix}")

    current_head, failure = git_output(
        project_root,
        ["rev-parse", "HEAD"],
        "cannot verify pre-commit merge HEAD",
    )
    if failure or current_head.strip() != main_head:
        abort_failure = abort_merge(project_root)
        suffix = f"; merge abort also failed: {abort_failure}" if abort_failure else ""
        detail = failure or "merge created a commit before final validation"
        return error(detail + suffix)

    merge_message = commit_message(f"stage: land {target_id}", target_id, branch)
    status, output = run_git(project_root, ["commit", "-m", merge_message])
    if status != 0:
        abort_failure = abort_merge(project_root)
        suffix = f"; merge abort also failed: {abort_failure}" if abort_failure else ""
        return error(f"cannot create landing merge commit: {output.strip()}{suffix}")

    cleanup = cleanup_worktree(
        project_root,
        WorktreeSpec(target=target_id, path=worktree, branch=branch),
    )
    if cleanup.errors:
        return error("landing succeeded but cleanup failed: " + "; ".join(cleanup.errors))
    if not cleanup.removed:
        return error("landing succeeded but cleanup did not remove the worktree and branch")

    print(f"Landed {target_id} from {branch} and removed its worktree and branch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
