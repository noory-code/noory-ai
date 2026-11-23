#!/usr/bin/env python3
"""Run today's close reviewer on a past commit and record what it judged (W-00000414).

DE-00000101 (3-가) measures the reviewer against past changes whose defect is on
record. This script gives the reviewer of the checkout it runs from (the review
command in `.stage/settings.json`, `run_review.py`, `claude_review_companion.py`)
the tree of a past commit, the same way `close_work.py` would at close:

- the tree is checked out alone in a throwaway repository that borrows this
  repository's objects, so `git log --all` there shows no later commit;
- `STAGE_WORK_ITEM_PATH` is the card as it stood in that commit;
- `STAGE_CHANGED_PATHS_FILE` lists the paths of the commits under review;
- `STAGE_WORK_LOG_PATH` holds the executor report from the commit body, when the
  commit carries one, and nothing else;
- `STAGE_REVIEW_VERDICT_FILE` is where `close_work.py` would put it.

The reviewer's scripts and prompt come from this checkout, never from the past
tree, so every case is judged by the same reviewer. The verdict is validated by
this checkout's `close_work.load_review_verdict`.

Each run writes one JSON file: the verdict, how long it took, the shell commands
the reviewer ran and the tokens it used (both read from the Claude Code transcript
of the run), and the paths the review changed in the tree.

Usage (from the project root):
    python3 .stage/research/review-judgment/measure_reviewer.py \\
        --cases .stage/research/review-judgment/cases.json \\
        --out .stage/research/review-judgment/runs --workdir <temp folder> \\
        [--only <case id> ...] [--repeat 1] [--jobs 3]
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
for import_dir in (
    PROJECT_ROOT / "stage" / "hooks",
    PROJECT_ROOT / "stage" / "scripts",
    PROJECT_ROOT / "stage" / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import (  # noqa: E402
    WORK_LOG_PREAMBLE,
    load_review_verdict,
    review_verdict_path,
    work_log_path,
)
from import_executor_report import parse_report, render_report  # noqa: E402

REVIEW_STRENGTH = "standard"
COMPANION = PROJECT_ROOT / "stage" / "scripts" / "claude_review_companion.py"
REVIEW_TIMEOUT_SECONDS = 3600


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {cwd}: {proc.stderr.strip()}")
    return proc.stdout


def review_command() -> str:
    """The close review command of this checkout, with its scripts named absolutely."""

    settings = json.loads(
        (PROJECT_ROOT / ".stage" / "settings.json").read_text(encoding="utf-8")
    )
    command = settings["review"]["strengths"][REVIEW_STRENGTH]
    scripts = (PROJECT_ROOT / "stage" / "scripts").as_posix()
    return str(command).replace("python3 stage/scripts/", f"python3 {scripts}/")


def isolated_tree(repo: Path, commit: str) -> None:
    """Check out `commit` in a new repository that knows no other commit by name."""

    repo.mkdir(parents=True)
    git(repo, "init", "--quiet")
    objects = Path(git(PROJECT_ROOT, "rev-parse", "--git-common-dir").strip())
    if not objects.is_absolute():
        objects = PROJECT_ROOT / objects
    alternates = repo / ".git" / "objects" / "info" / "alternates"
    alternates.write_text(f"{(objects / 'objects').resolve().as_posix()}\n", encoding="utf-8")
    git(repo, "checkout", "--quiet", "--detach", commit)


def changed_paths(commits: list[str]) -> list[str]:
    paths: set[str] = set()
    for commit in commits:
        listed = git(PROJECT_ROOT, "show", "--format=", "--name-only", "--no-renames", "-z", commit)
        paths.update(path for path in listed.split("\0") if path)
    return sorted(paths)


def executor_report(commit: str) -> str:
    """The commit's executor report as the importer writes it, or "" when it has none."""

    message = git(PROJECT_ROOT, "log", "-1", "--format=%B", commit)
    try:
        return render_report(parse_report(message))
    except ValueError:
        return ""


def tree_state(repo: Path) -> str:
    return git(repo, "status", "--porcelain", "--untracked-files=all")


def transcript_facts(repo: Path) -> dict[str, object]:
    """Shell commands and token counts from the Claude Code transcript of a run."""

    slug = re.sub(r"[^A-Za-z0-9]", "-", str(repo.resolve()))
    folder = Path.home() / ".claude" / "projects" / slug
    commands: list[str] = []
    tokens = {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0}
    seen_messages: set[str] = set()
    for transcript in sorted(folder.glob("*.jsonl")) if folder.is_dir() else []:
        for line in transcript.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = event.get("message")
            if event.get("type") != "assistant" or not isinstance(message, dict):
                continue
            for block in message.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_input = block.get("input") or {}
                    if block.get("name") in ("Bash", "PowerShell"):
                        commands.append(str(tool_input.get("command", "")))
            message_id = str(message.get("id", ""))
            usage = message.get("usage")
            if message_id in seen_messages or not isinstance(usage, dict):
                continue
            seen_messages.add(message_id)
            tokens["input"] += int(usage.get("input_tokens") or 0)
            tokens["cache_creation"] += int(usage.get("cache_creation_input_tokens") or 0)
            tokens["cache_read"] += int(usage.get("cache_read_input_tokens") or 0)
            tokens["output"] += int(usage.get("output_tokens") or 0)
    return {"transcript_found": folder.is_dir(), "shell_commands": commands, "tokens": tokens}


def run_case(case: dict[str, object], run_number: int, workdir: Path, out: Path) -> Path:
    case_id = str(case["id"])
    commit = str(case["commit"])
    card_id = str(case["card"])
    run_id = f"{case_id}-run{run_number}"
    repo = workdir / run_id / "repo"
    if repo.parent.exists():
        shutil.rmtree(repo.parent)
    isolated_tree(repo, commit)

    stage_root = repo / ".stage"
    report = executor_report(str(case.get("report_commit") or commit))
    log_path = work_log_path(stage_root, card_id)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    preamble = WORK_LOG_PREAMBLE.format(item_id=card_id)
    log_path.write_text(preamble + (f"\n{report}" if report else ""), encoding="utf-8")
    verdict_file = review_verdict_path(stage_root, card_id)
    verdict_file.parent.mkdir(parents=True, exist_ok=True)
    paths = changed_paths([str(item) for item in case.get("path_commits") or [commit]])
    paths_file = workdir / run_id / "review-input" / "changed-paths.json"
    paths_file.parent.mkdir(parents=True)
    paths_file.write_text(json.dumps(paths, ensure_ascii=False) + "\n", encoding="utf-8")

    environment = os.environ.copy()
    environment.update(
        {
            "STAGE_CODEX_COMPANION": str(COMPANION),
            "STAGE_WORK_ITEM_PATH": str((repo / str(case["card_path"])).resolve()),
            "STAGE_CHANGED_PATHS_FILE": str(paths_file.resolve()),
            "STAGE_REVIEW_VERDICT_FILE": str(verdict_file.resolve()),
            "STAGE_WORK_LOG_PATH": str(log_path.resolve()),
        }
    )
    before = tree_state(repo)
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            review_command(),
            shell=True,
            cwd=str(repo),
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=REVIEW_TIMEOUT_SECONDS + 120,
        )
        exit_code, output = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out, exit_code = True, 124
        output = str(exc.stdout or "") + str(exc.stderr or "")
    seconds = round(time.monotonic() - started)
    after = tree_state(repo)

    verdict, error = load_review_verdict(verdict_file)
    result = {
        "case": case_id,
        "card": card_id,
        "version": case["version"],
        "commit": commit,
        "report_commit": case.get("report_commit") or commit,
        "run": run_number,
        "reviewer_checkout": git(PROJECT_ROOT, "rev-parse", "HEAD").strip(),
        "executor_report_in_log": bool(report),
        "changed_paths": len(paths),
        "seconds": seconds,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "verdict_error": error,
        "verdict": verdict,
        "tree_changed_by_review": before != after,
        "tree_state_after": after if before != after else "",
        "reviewer_output": output,
        **transcript_facts(repo),
    }
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{run_id}.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--only", nargs="*", default=[], help="Case ids to run; default all.")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--first-run", type=int, default=1)
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    selected = [case for case in cases if not args.only or case["id"] in args.only]
    work = [
        (case, number)
        for case in selected
        for number in range(args.first_run, args.first_run + args.repeat)
    ]
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {
            pool.submit(run_case, case, number, args.workdir.resolve(), args.out.resolve()): (
                case["id"],
                number,
            )
            for case, number in work
        }
        for future in concurrent.futures.as_completed(futures):
            case_id, number = futures[future]
            try:
                print(f"{case_id} run {number}: {future.result()}", flush=True)
            except Exception as exc:  # noqa: BLE001 - report every case, then fail
                failures += 1
                print(f"{case_id} run {number}: FAILED {exc}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
