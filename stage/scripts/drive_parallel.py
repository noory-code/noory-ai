#!/usr/bin/env python3
"""Run supervised Stage driver steps in card-specific Git worktrees."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


DRIVER = Path(__file__).resolve().with_name("drive.py")
SCRIPTS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = Path(__file__).resolve().parents[1] / "hooks"
for import_dir in (SCRIPTS_DIR, HOOKS_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from drive import resolve_reap_command  # noqa: E402
from stage_paths import read_settings  # noqa: E402
from stage_record_paths import record_path  # noqa: E402
from stage_work import parse_frontmatter  # noqa: E402


WORK_ID_RE = re.compile(r"W-\d{8}")
DEFAULT_MAX_WORKERS = 2
DEFAULT_DRIVER_TIMEOUT = 3600
REAPER_TIMEOUT = 120


class WorktreeSpec(NamedTuple):
    target: str
    path: Path
    branch: str


class DriverResult(NamedTuple):
    spec: WorktreeSpec
    returncode: int
    stdout: str
    stderr: str


class CleanupResult(NamedTuple):
    removed: bool
    absent: bool
    errors: tuple[str, ...]


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def real_git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("GIT_INDEX_FILE", None)
    return environment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one supervised Stage driver step per card in parallel worktrees."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Git worktree containing the Stage project (default: cwd).",
    )
    parser.add_argument(
        "--worktree-root",
        help=(
            "Directory that will contain one worktree per card "
            "(default: <project-parent>/<project-name>-stage-worktrees)."
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=positive_integer,
        default=DEFAULT_MAX_WORKERS,
        help=f"Maximum concurrent drivers (default: {DEFAULT_MAX_WORKERS}).",
    )
    parser.add_argument(
        "--driver-timeout",
        type=positive_integer,
        default=DEFAULT_DRIVER_TIMEOUT,
        help=f"Seconds allowed for each driver (default: {DEFAULT_DRIVER_TIMEOUT}).",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove the named parallel worktrees and branches instead of running drivers.",
    )
    parser.add_argument("targets", nargs="+", help="Existing W-* work item IDs.")
    return parser.parse_args()


def run_git(project_root: Path, args: list[str]) -> tuple[int, str]:
    """Run Git without raising and return its status plus combined output."""

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            capture_output=True,
            env=real_git_environment(),
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return 124, f"git {' '.join(args[:2])} timed out"
    except OSError as exc:
        return 127, str(exc)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def worktree_specs(worktree_root: Path, targets: list[str]) -> list[WorktreeSpec]:
    return [
        WorktreeSpec(
            target=target,
            path=(worktree_root / target).resolve(),
            branch=f"stage/worktree/{target}",
        )
        for target in targets
    ]


def validate_specs(project_root: Path, specs: list[WorktreeSpec]) -> str:
    status, top_level = run_git(project_root, ["rev-parse", "--show-toplevel"])
    if status != 0:
        return f"project root is not a Git worktree: {top_level.strip()}"
    if Path(top_level.strip()).resolve() != project_root:
        return f"project root must be the Git worktree root: {top_level.strip()}"

    status, dirty = run_git(
        project_root,
        ["status", "--porcelain", "--untracked-files=normal"],
    )
    if status != 0:
        return f"cannot inspect project worktree status: {dirty.strip()}"
    if dirty:
        return (
            "project worktree is dirty; commit or stash its changes before "
            "parallel execution"
        )

    current_root = project_root / ".stage/work/current"
    for spec in specs:
        try:
            card_path = record_path(current_root, spec.target)
        except (OSError, ValueError) as exc:
            return f"cannot resolve current work item {spec.target}: {exc}"
        if not card_path.is_file():
            return f"current work item does not exist: {spec.target}"
        if spec.path.exists() or spec.path.is_symlink():
            return f"worktree path already exists for {spec.target}: {spec.path}"
        status, output = run_git(
            project_root,
            ["show-ref", "--verify", "--quiet", f"refs/heads/{spec.branch}"],
        )
        if status == 0:
            return f"branch already exists for {spec.target}: {spec.branch}"
        if status != 1:
            return f"cannot inspect branch {spec.branch}: {output.strip()}"
    return ""


def create_worktree(project_root: Path, spec: WorktreeSpec) -> str:
    status, output = run_git(
        project_root,
        ["worktree", "add", "-b", spec.branch, str(spec.path), "HEAD"],
    )
    if status != 0:
        return output.strip() or f"git worktree add exited with status {status}"
    return ""


def registered_worktrees(project_root: Path) -> tuple[dict[Path, str], str]:
    status, output = run_git(
        project_root,
        ["worktree", "list", "--porcelain", "-z"],
    )
    if status != 0:
        detail = output.strip() or f"git exited with status {status}"
        return {}, f"cannot inspect registered Git worktrees: {detail}"

    registrations: dict[Path, str] = {}
    for raw_record in output.split("\0\0"):
        fields = [field for field in raw_record.split("\0") if field]
        path_text = next(
            (field.removeprefix("worktree ") for field in fields if field.startswith("worktree ")),
            "",
        )
        branch_ref = next(
            (field.removeprefix("branch ") for field in fields if field.startswith("branch ")),
            "",
        )
        if path_text:
            registrations[Path(path_text).resolve()] = branch_ref.removeprefix(
                "refs/heads/"
            )
    return registrations, ""


def cleanup_worktree(project_root: Path, spec: WorktreeSpec) -> CleanupResult:
    errors: list[str] = []
    registrations, registration_error = registered_worktrees(project_root)
    if registration_error:
        return CleanupResult(False, False, (registration_error,))

    status, branch_output = run_git(
        project_root,
        ["show-ref", "--verify", "--quiet", f"refs/heads/{spec.branch}"],
    )
    branch_exists = status == 0
    if status not in {0, 1}:
        detail = branch_output.strip() or f"git exited with status {status}"
        return CleanupResult(
            False,
            False,
            (f"cannot inspect cleanup branch {spec.branch}: {detail}",),
        )

    registered_branch = registrations.get(spec.path)
    if registered_branch is None:
        if not spec.path.exists() and not spec.path.is_symlink() and not branch_exists:
            return CleanupResult(False, True, ())
        return CleanupResult(
            False,
            False,
            (f"refusing cleanup: {spec.path} is not a registered Git worktree",),
        )
    if registered_branch != spec.branch:
        actual = registered_branch or "(detached HEAD)"
        return CleanupResult(
            False,
            False,
            (
                f"refusing cleanup: {spec.path} is registered on unexpected branch "
                f"{actual}; expected {spec.branch}",
            ),
        )
    if not branch_exists:
        return CleanupResult(
            False,
            False,
            (f"refusing cleanup: registered branch does not exist: {spec.branch}",),
        )

    merged_status, merged_output = run_git(
        project_root,
        ["merge-base", "--is-ancestor", spec.branch, "HEAD"],
    )
    if merged_status == 1:
        return CleanupResult(
            False,
            False,
            (
                f"refusing cleanup: {spec.branch} contains commits not merged into HEAD; "
                "merge or otherwise preserve them before cleanup",
            ),
        )
    if merged_status != 0:
        detail = merged_output.strip() or f"git exited with status {merged_status}"
        return CleanupResult(
            False,
            False,
            (f"cannot compare {spec.branch} with HEAD: {detail}",),
        )

    status, _ = run_git(
        project_root,
        ["worktree", "remove", "--force", str(spec.path)],
    )
    if status != 0:
        if spec.path.exists() or spec.path.is_symlink():
            try:
                shutil.rmtree(spec.path)
            except OSError as exc:
                errors.append(f"cannot remove worktree {spec.path}: {exc}")
        if not errors:
            prune_status, prune_output = run_git(
                project_root,
                ["worktree", "prune", "--expire", "now"],
            )
            if prune_status != 0:
                errors.append(
                    "cannot prune failed worktree metadata: "
                    f"{prune_output.strip() or f'git exited with status {prune_status}'}"
                )

    if not errors:
        delete_status, delete_output = run_git(
            project_root,
            ["branch", "-d", spec.branch],
        )
        if delete_status != 0:
            errors.append(
                f"cannot remove branch {spec.branch}: "
                f"{delete_output.strip() or f'git exited with status {delete_status}'}"
            )
    return CleanupResult(not errors, False, tuple(errors))


def reap_after_timeout(spec: WorktreeSpec) -> str:
    stage_root = spec.path / ".stage"
    try:
        item_path = record_path(stage_root / "work/current", spec.target)
    except (OSError, ValueError) as exc:
        return f"venue reaper was not run: cannot resolve {spec.target}: {exc}"
    if not item_path.is_file():
        return f"venue reaper was not run: current work item does not exist: {spec.target}"

    venue = str(parse_frontmatter(item_path).get("venue", "")).strip().lower()
    if not venue:
        return f"venue reaper was not run: {spec.target} has no venue"

    settings_path, settings, settings_error = read_settings(stage_root)
    if settings_error is not None:
        return f"venue reaper was not run: cannot read {settings_path}: {settings_error}"
    reapers = settings.get("reapers") if isinstance(settings, dict) else None
    command, configured, config_error = resolve_reap_command(reapers, venue)
    if config_error:
        return f"reapers.{venue} is unusable ({config_error}); external jobs may remain"
    if command is None:
        if configured:
            return f"reapers.{venue} declares that no external job needs reaping"
        return f"reapers.{venue} is not configured; external jobs may remain"

    environment = real_git_environment()
    environment.update(
        {
            "CLAUDE_PROJECT_DIR": str(spec.path),
            "PROJECT_ROOT": str(spec.path),
            "STAGE_WORK_ITEM_PATH": str(item_path.resolve()),
            "STAGE_PROJECT_ROOT": str(spec.path),
            "STAGE_WORK_LOG_PATH": str(
                stage_root / ".runtime/driver/logs" / f"{spec.target}.md"
            ),
            "STAGE_TURN_ROLE": "executor",
        }
    )
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(spec.path),
            capture_output=True,
            env=environment,
            text=True,
            timeout=REAPER_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return (
            f"reapers.{venue} timed out after {REAPER_TIMEOUT} seconds; "
            "external jobs may remain"
        )
    except OSError as exc:
        return f"reapers.{venue} could not start ({exc}); external jobs may remain"
    if result.returncode != 0:
        detail = ((result.stdout or "") + (result.stderr or "")).strip()
        suffix = f": {detail}" if detail else ""
        return (
            f"reapers.{venue} failed with status {result.returncode}; "
            f"external jobs may remain{suffix}"
        )
    return f"reapers.{venue} completed; confirm no external jobs remain before cleanup"


def run_driver(
    spec: WorktreeSpec,
    driver_path: Path,
    *,
    timeout: int,
) -> DriverResult:
    command = [
        sys.executable,
        str(driver_path),
        "--project-root",
        str(spec.path),
        "--execute",
        spec.target,
    ]
    environment = real_git_environment()
    environment["CLAUDE_PROJECT_DIR"] = str(spec.path)
    environment["PROJECT_ROOT"] = str(spec.path)
    try:
        result = subprocess.run(
            command,
            cwd=str(spec.path),
            capture_output=True,
            env=environment,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        reaper_status = reap_after_timeout(spec)
        return DriverResult(
            spec,
            124,
            "",
            (
                f"driver timed out after {timeout} seconds. External executor or reviewer "
                "jobs may still be running and writing to this worktree. Do not run "
                f"--cleanup until all jobs have stopped. {reaper_status}"
            ),
        )
    except OSError as exc:
        return DriverResult(spec, 127, "", str(exc))
    return DriverResult(
        spec,
        result.returncode,
        result.stdout or "",
        result.stderr or "",
    )


def print_result(result: DriverResult) -> None:
    print(f"{result.spec.target}: driver exited with status {result.returncode}")
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    print(f"Worktree: {result.spec.path}")
    print(f"Merge branch: {result.spec.branch}")


def run_parallel(
    project_root: Path,
    targets: list[str],
    *,
    worktree_root: Path,
    driver_path: Path = DRIVER,
    max_workers: int = DEFAULT_MAX_WORKERS,
    driver_timeout: int = DEFAULT_DRIVER_TIMEOUT,
) -> int:
    project_root = project_root.resolve()
    worktree_root = worktree_root.resolve()
    driver_path = driver_path.resolve()

    if worktree_root == project_root or project_root in worktree_root.parents:
        print("ERROR: worktree root must be outside the project worktree", file=sys.stderr)
        return 2
    if len(set(targets)) != len(targets):
        print("ERROR: each target may appear only once", file=sys.stderr)
        return 2
    if max_workers < 1:
        print("ERROR: max workers must be a positive integer", file=sys.stderr)
        return 2
    if driver_timeout < 1:
        print("ERROR: driver timeout must be a positive integer", file=sys.stderr)
        return 2
    invalid = [target for target in targets if not WORK_ID_RE.fullmatch(target)]
    if invalid:
        print(f"ERROR: invalid work item ID: {invalid[0]}", file=sys.stderr)
        return 2
    if not driver_path.is_file():
        print(f"ERROR: driver does not exist: {driver_path}", file=sys.stderr)
        return 2

    specs = worktree_specs(worktree_root, targets)
    validation_error = validate_specs(project_root, specs)
    if validation_error:
        print(f"ERROR: {validation_error}", file=sys.stderr)
        return 1

    root_created = not worktree_root.exists()
    try:
        worktree_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: cannot create worktree root {worktree_root}: {exc}", file=sys.stderr)
        return 1

    created: list[WorktreeSpec] = []
    for spec in specs:
        creation_error = create_worktree(project_root, spec)
        if creation_error:
            cleanup_errors: list[str] = []
            for cleanup_spec in [spec, *reversed(created)]:
                cleanup_errors.extend(
                    cleanup_worktree(project_root, cleanup_spec).errors
                )
            if root_created:
                try:
                    worktree_root.rmdir()
                except OSError:
                    pass
            print(
                f"ERROR: cannot create worktree for {spec.target}: {creation_error}",
                file=sys.stderr,
            )
            for error in cleanup_errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        created.append(spec)

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(max_workers, len(specs))
    ) as executor:
        futures = {
            spec.target: executor.submit(
                run_driver,
                spec,
                driver_path,
                timeout=driver_timeout,
            )
            for spec in specs
        }
        results = [futures[spec.target].result() for spec in specs]

    for result in results:
        print_result(result)
    return 0 if all(result.returncode == 0 for result in results) else 1


def cleanup_targets(
    project_root: Path,
    targets: list[str],
    *,
    worktree_root: Path,
) -> int:
    project_root = project_root.resolve()
    worktree_root = worktree_root.resolve()

    if worktree_root == project_root or project_root in worktree_root.parents:
        print("ERROR: worktree root must be outside the project worktree", file=sys.stderr)
        return 2
    if len(set(targets)) != len(targets):
        print("ERROR: each target may appear only once", file=sys.stderr)
        return 2
    invalid = [target for target in targets if not WORK_ID_RE.fullmatch(target)]
    if invalid:
        print(f"ERROR: invalid work item ID: {invalid[0]}", file=sys.stderr)
        return 2

    status, top_level = run_git(project_root, ["rev-parse", "--show-toplevel"])
    if status != 0:
        print(
            f"ERROR: project root is not a Git worktree: {top_level.strip()}",
            file=sys.stderr,
        )
        return 1
    if Path(top_level.strip()).resolve() != project_root:
        print(
            f"ERROR: project root must be the Git worktree root: {top_level.strip()}",
            file=sys.stderr,
        )
        return 1

    failed = False
    for spec in worktree_specs(worktree_root, targets):
        cleanup = cleanup_worktree(project_root, spec)
        if cleanup.errors:
            failed = True
            for error in cleanup.errors:
                print(f"ERROR: {error}", file=sys.stderr)
        elif cleanup.absent:
            print(f"No retained worktree or branch for {spec.target}")
        else:
            print(f"Removed worktree and branch for {spec.target}")
    return 1 if failed else 0


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    worktree_root = (
        Path(args.worktree_root).expanduser().resolve()
        if args.worktree_root
        else project_root.parent / f"{project_root.name}-stage-worktrees"
    )
    if args.cleanup:
        return cleanup_targets(
            project_root,
            args.targets,
            worktree_root=worktree_root,
        )
    return run_parallel(
        project_root,
        args.targets,
        worktree_root=worktree_root,
        max_workers=args.max_workers,
        driver_timeout=args.driver_timeout,
    )


if __name__ == "__main__":
    raise SystemExit(main())
