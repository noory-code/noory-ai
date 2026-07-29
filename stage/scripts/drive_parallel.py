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
WORK_ID_RE = re.compile(r"W-\d{8}")


class WorktreeSpec(NamedTuple):
    target: str
    path: Path
    branch: str


class DriverResult(NamedTuple):
    spec: WorktreeSpec
    returncode: int
    stdout: str
    stderr: str


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

    for spec in specs:
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


def cleanup_worktree(project_root: Path, spec: WorktreeSpec) -> list[str]:
    errors: list[str] = []
    status, _ = run_git(
        project_root,
        ["worktree", "remove", "--force", str(spec.path)],
    )
    if status != 0 and spec.path.exists():
        try:
            shutil.rmtree(spec.path)
        except OSError as exc:
            errors.append(f"cannot remove worktree {spec.path}: {exc}")
        else:
            prune_status, prune_output = run_git(
                project_root,
                ["worktree", "prune", "--expire", "now"],
            )
            if prune_status != 0:
                errors.append(
                    "cannot prune failed worktree metadata: "
                    f"{prune_output.strip() or f'git exited with status {prune_status}'}"
                )

    status, _ = run_git(
        project_root,
        ["show-ref", "--verify", "--quiet", f"refs/heads/{spec.branch}"],
    )
    if status == 0:
        delete_status, delete_output = run_git(
            project_root,
            ["branch", "-D", spec.branch],
        )
        if delete_status != 0:
            errors.append(
                f"cannot remove branch {spec.branch}: "
                f"{delete_output.strip() or f'git exited with status {delete_status}'}"
            )
    elif status != 1:
        errors.append(f"cannot inspect cleanup branch {spec.branch}")
    return errors


def run_driver(spec: WorktreeSpec, driver_path: Path) -> DriverResult:
    command = [
        sys.executable,
        str(driver_path),
        "--project-root",
        str(spec.path),
        "--execute",
        spec.target,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=str(spec.path),
            capture_output=True,
            env=real_git_environment(),
            text=True,
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
                cleanup_errors.extend(cleanup_worktree(project_root, cleanup_spec))
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(specs)) as executor:
        futures = {
            spec.target: executor.submit(run_driver, spec, driver_path)
            for spec in specs
        }
        results = [futures[spec.target].result() for spec in specs]

    for result in results:
        print_result(result)
    return 0 if all(result.returncode == 0 for result in results) else 1


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    worktree_root = (
        Path(args.worktree_root).expanduser().resolve()
        if args.worktree_root
        else project_root.parent / f"{project_root.name}-stage-worktrees"
    )
    return run_parallel(
        project_root,
        args.targets,
        worktree_root=worktree_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
