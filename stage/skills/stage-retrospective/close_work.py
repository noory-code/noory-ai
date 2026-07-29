#!/usr/bin/env python3
"""Close a Stage work item by RUNNING its verification checks.

`verification: passed` becomes a byproduct of executing the checks and observing
their output, not a hand-typed claim (the honesty gap behind commit 79c86ee9).

Honest scope: this runs the checks you give it and captures their evidence. It
does NOT judge whether those checks are sufficient for the item's kind — supply
the kind-appropriate checks (see operations/verification.md). A check that runs
nothing (e.g. `true`, or unittest over an empty dir) will pass; that is the
caller's responsibility.

Closing also requires what the completion gate and audit require: a completed
retrospective (with an existing retrospective_ref) and a FINAL promotion
decision — otherwise the item would audit-fail (WORK008) and block later commits.

Usage:
    close_work.py --project-root . W-00000008 \
        --check "python3 -m unittest discover -s stage/hooks/tests -q" \
        --check "python3 stage/scripts/audit_stage.py" \
        [--promotion not_applicable] [--timeout 900]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

# The review resolver lives in the hook package (one owning definition, shared
# with the audit). close_work is stdlib-only and stage_paths is too, so a path
# insert is safe and side-effect-free.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from lifecycle_paths import relative_record_link, v4_lifecycle_paths  # noqa: E402
from stage_record_paths import record_path  # noqa: E402
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    load_review_config,
    resolve_independent_review_command,
    resolve_review_command,
    schema_migration_banner,
)
from stage_work import (  # noqa: E402
    GATE_FIELD_DEFAULTS,
    decision_status,
    item_from_fields,
    load_all_work_items,
    non_terminal_children,
    parse_frontmatter,
    split_scope,
)
from worktree_guard import ORDER_CONTRACT, dirty_paths_in_scope  # noqa: E402

OPEN_TO_CLOSE = {"active", "review"}
PROMOTION_FINAL = {"approved", "promoted", "deferred", "not_applicable", "rejected"}
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
MAX_LINES = 40
MAX_BYTES = 4000
WORK_LOG_RELATIVE_DIR = Path(".stage/.runtime/driver/logs")
REVIEW_VERDICT_RELATIVE_DIR = Path(".stage/.runtime/driver/verdicts")
WORK_LOG_PREAMBLE = """\
# Stage 작업 로그 — {item_id}

## 책임 경계

이 로그는 실행 시도별 작업자의 작업 내용·이유·변경 경로 주장과 리뷰어의 성공 기준별 판정을
소유한다. 작업 카드는 지속되는 수명 주기 상태와 `## Progress`, `## Verification`,
`## Retrospective`, `## Promotion decision`을 소유한다. 같은 사실을 두 파일에 복제하지 않고
서로의 소유 사실은 경로로 참조한다.
"""
EXECUTOR_REPORT_MARKER = "### Executor report"
REVIEW_DISPOSITIONS_LABEL = "Review dispositions (JSON):"


def field(text: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def set_field(text: str, name: str, value: str) -> str:
    updated, count = re.subn(
        rf"^({re.escape(name)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"missing lifecycle field `{name}`")
    return updated


def append_to_section(text: str, heading: str, body: str) -> str:
    # Body goes through a replacement FUNCTION, never an `rf"...\g<1>..."` template:
    # the check output is arbitrary and would otherwise be read as regex escapes
    # (`\1`, `\U…`) — a crash or silent corruption. Tail is a lookahead so the
    # section may be the last heading (\Z) without swallowing the next one.
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"

    def append(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}\n{body}\n"

    return re.sub(pattern, append, text, count=1, flags=re.DOTALL)


def work_log_path(stage_root: Path, item_id: str) -> Path:
    return record_path(stage_root.parent / WORK_LOG_RELATIVE_DIR, item_id)


def work_log_reference(item_id: str) -> str:
    return record_path(WORK_LOG_RELATIVE_DIR, item_id).as_posix()


def ensure_work_log(stage_root: Path, item_id: str) -> Path:
    path = work_log_path(stage_root, item_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(
                WORK_LOG_PREAMBLE.format(item_id=item_id),
                encoding="utf-8",
            )
    except OSError as exc:
        raise RuntimeError(f"cannot create work log for {item_id}: {exc}") from exc
    return path


def read_work_log(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"cannot read work log {path}: {exc}") from exc


def review_verdict_path(stage_root: Path, item_id: str) -> Path:
    return stage_root.parent / REVIEW_VERDICT_RELATIVE_DIR / f"{item_id}.json"


def clear_review_verdict(path: Path) -> None:
    """Remove the prior verdict so a missing new result cannot reuse stale approval."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
    except OSError as exc:
        raise RuntimeError(f"cannot prepare review verdict file {path}: {exc}") from exc


def load_review_verdict(path: Path) -> tuple[dict[str, object] | None, str]:
    """Load and validate the reviewer-owned JSON verdict."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "review verdict file is missing"
    except json.JSONDecodeError:
        return None, "review verdict file is invalid JSON"
    except OSError as exc:
        return None, f"cannot read review verdict file: {exc}"

    if not isinstance(raw, dict) or set(raw) != {"criteria", "approved"}:
        return None, (
            "review verdict must contain exactly `criteria` and `approved`"
        )
    criteria = raw["criteria"]
    approved = raw["approved"]
    if not isinstance(criteria, list) or not criteria:
        return None, "review verdict criteria must be a non-empty array"
    if type(approved) is not bool:
        return None, "review verdict approved must be a boolean"

    normalized: list[dict[str, str]] = []
    seen_criteria: set[str] = set()
    for entry in criteria:
        if not isinstance(entry, dict) or set(entry) != {
            "criterion",
            "verdict",
            "reason",
        }:
            return None, (
                "each review criterion must contain exactly `criterion`, "
                "`verdict`, and `reason`"
            )
        criterion = entry["criterion"]
        verdict = entry["verdict"]
        reason = entry["reason"]
        if not all(
            isinstance(value, str)
            for value in (criterion, verdict, reason)
        ):
            return None, "review criterion values must be strings"
        if (
            not criterion.strip()
            or not reason.strip()
            or "\n" in criterion
            or "\r" in criterion
            or "\n" in reason
            or "\r" in reason
        ):
            return None, (
                "review criterion and reason must be non-empty one-line strings"
            )
        if criterion in seen_criteria:
            return None, "review verdict criteria must be unique"
        if verdict not in {"PASS", "FAIL"}:
            return None, "review criterion verdict must be `PASS` or `FAIL`"
        seen_criteria.add(criterion)
        normalized.append(
            {
                "criterion": criterion,
                "verdict": verdict,
                "reason": reason,
            }
        )

    all_passed = all(entry["verdict"] == "PASS" for entry in normalized)
    if approved != all_passed:
        return None, (
            "review verdict approved must be true exactly when every criterion passes"
        )
    return {"criteria": normalized, "approved": approved}, ""


def review_verdict_error(path: Path) -> str:
    verdict, error = load_review_verdict(path)
    if error:
        return error
    if verdict is None or verdict["approved"] is not True:
        return "review verdict did not approve the work item"
    return ""


def review_verdict_failures(path: Path) -> list[str]:
    verdict, error = load_review_verdict(path)
    if error or verdict is None:
        return []
    criteria = verdict["criteria"]
    assert isinstance(criteria, list)
    return [
        entry["criterion"]
        for entry in criteria
        if isinstance(entry, dict) and entry.get("verdict") == "FAIL"
    ]


def section_marker_starts(text: str, marker: str) -> list[int]:
    """Return starts of marker heading lines, excluding marker mentions in prose."""

    return [
        match.start()
        for match in re.finditer(
            rf"(?m)^{re.escape(marker)}[ \t]*\r?$",
            text,
        )
    ]


def executor_report_error(
    previous_log: str,
    current_log: str,
    observed_paths: list[str],
    review_findings: list[str] | None = None,
    *,
    ignored_paths: list[str] | None = None,
) -> str:
    if current_log == previous_log:
        return "executor did not append a work log report"
    if not current_log.startswith(previous_log):
        return "executor rewrote existing work log content instead of appending"
    addition = current_log[len(previous_log) :]
    if len(section_marker_starts(addition, EXECUTOR_REPORT_MARKER)) != 1:
        return "executor must append exactly one `### Executor report` per attempt"
    for label in ("What changed", "Why", "Review request"):
        match = re.search(rf"(?m)^{re.escape(label)}:[ \t]*(.+)$", addition)
        if not match or not match.group(1).strip():
            return f"executor work log report is missing non-empty `{label}:`"
    paths_match = re.search(
        r"(?m)^Changed paths \(JSON\):[ \t]*\n([^\r\n]+)$",
        addition,
    )
    if not paths_match:
        return "executor work log report is missing one-line `Changed paths (JSON):`"
    try:
        claimed = json.loads(paths_match.group(1))
    except json.JSONDecodeError as exc:
        return f"executor changed-path claim is invalid JSON: {exc.msg}"
    if (
        not isinstance(claimed, list)
        or any(not isinstance(path, str) or not path for path in claimed)
        or len(set(claimed)) != len(claimed)
    ):
        return "executor changed-path claim must be a JSON array of unique non-empty strings"
    unsafe = [
        path
        for path in claimed
        if Path(path).is_absolute()
        or path == "."
        or ".." in Path(path).parts
        or "\\" in path
    ]
    if unsafe:
        return f"executor changed-path claim contains unsafe repository paths: {unsafe}"
    ignored = set(ignored_paths or [])
    claimed_paths = sorted(path for path in claimed if path not in ignored)
    expected_paths = sorted(path for path in observed_paths if path not in ignored)
    dispositions, disposition_error = executor_review_dispositions(
        previous_log,
        current_log,
        review_findings or [],
    )
    if disposition_error:
        return disposition_error
    reasoned_empty_claim = (
        not claimed_paths
        and bool(dispositions)
        and all(
            entry["disposition"] in {"decline", "defer"}
            for entry in dispositions
        )
    )
    if claimed_paths != expected_paths and not reasoned_empty_claim:
        return (
            "executor claimed changed paths do not match driver observation: "
            f"claimed={claimed_paths}, observed={expected_paths}"
        )
    return ""


def executor_review_dispositions(
    previous_log: str,
    current_log: str,
    review_findings: list[str],
) -> tuple[list[dict[str, str]], str]:
    """Validate one exact, reasoned disposition for each pending review failure."""

    if not review_findings:
        return [], ""
    if not current_log.startswith(previous_log):
        return [], "executor rewrote existing work log content instead of appending"
    addition = current_log[len(previous_log) :]
    match = re.search(
        rf"(?m)^{re.escape(REVIEW_DISPOSITIONS_LABEL)}[ \t]*\n([^\r\n]+)$",
        addition,
    )
    if not match:
        return [], (
            "executor work log report is missing one-line "
            f"`{REVIEW_DISPOSITIONS_LABEL}` for pending review failures"
        )
    try:
        raw_dispositions = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return [], f"executor review dispositions are invalid JSON: {exc.msg}"
    if not isinstance(raw_dispositions, list):
        return [], "executor review dispositions must be a JSON array"

    dispositions: list[dict[str, str]] = []
    for entry in raw_dispositions:
        if not isinstance(entry, dict) or set(entry) != {
            "finding",
            "disposition",
            "reason",
        }:
            return [], (
                "each executor review disposition must contain exactly "
                "`finding`, `disposition`, and `reason`"
            )
        finding = entry["finding"]
        disposition = entry["disposition"]
        reason = entry["reason"]
        if not all(isinstance(value, str) for value in (finding, disposition, reason)):
            return [], "executor review disposition values must be strings"
        if disposition not in {"accept", "decline", "defer"}:
            return [], (
                "executor review disposition must be `accept`, `decline`, or `defer`"
            )
        if not reason.strip() or "\n" in reason or "\r" in reason:
            return [], "executor review disposition requires a non-empty one-line reason"
        dispositions.append(
            {
                "finding": finding,
                "disposition": disposition,
                "reason": reason,
            }
        )

    claimed_findings = [entry["finding"] for entry in dispositions]
    if claimed_findings != review_findings:
        return [], (
            "executor review dispositions do not match the pending failures: "
            f"claimed={claimed_findings}, pending={review_findings}"
        )
    return dispositions, ""


def clip(output: str) -> str:
    cleaned = _CTRL_RE.sub("", output).replace("```", "``​`")  # don't break the evidence fence
    lines = cleaned.splitlines()
    clipped = lines[-MAX_LINES:]
    text = "\n".join(clipped)
    if len(text.encode("utf-8")) > MAX_BYTES:
        text = text.encode("utf-8")[-MAX_BYTES:].decode("utf-8", "ignore")
    prefix = "" if len(lines) <= MAX_LINES else f"... ({len(lines) - MAX_LINES} earlier lines omitted)\n"
    return prefix + text


def drop_row(text: str, item_id: str, item_link: str | None = None) -> str:
    link = item_link or record_path(Path("items"), item_id).as_posix()
    kept = [
        line
        for line in text.splitlines()
        if not re.search(rf"\({re.escape(link)}\)", line)
    ]
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def ensure_review_row(
    review_path: Path,
    item_id: str,
    verification: str,
    retrospective: str,
    promotion: str,
    item_link: str | None = None,
) -> None:
    # Index membership is eventually-consistent: this read-modify-write can lose a
    # row if two windows update the index at once. The id allocation is the atomic
    # part; a dropped index row is self-detected by the audit (INDEX003) and
    # repaired by a re-run (which reconciles rather than duplicates).
    link = item_link or record_path(Path("items"), item_id).as_posix()
    row = (
        f"| {item_id} | {verification} | {retrospective} | {promotion} | "
        f"[{link}]({link}) |"
    )
    text = review_path.read_text(encoding="utf-8") if review_path.exists() else ""
    if re.search(rf"\({re.escape(link)}\)", text):
        return
    review_path.write_text(f"{text.rstrip(chr(10))}\n{row}\n", encoding="utf-8")


def run_check(
    command: str,
    timeout: int,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> tuple[bool, str, str]:
    # Returns (ok, evidence_block, raw_output). The RAW output is returned
    # separately so a verdict scan (e.g. `^BLOCK:`) runs on the full text, never
    # on the clipped evidence block — a verdict line could otherwise be clipped
    # away and lost. cwd is the project root so a check's relative paths resolve
    # the same way whatever directory close_work was launched from.
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
            env=env,
        )
    except subprocess.TimeoutExpired:
        msg = f"$ {command}\n[TIMED OUT after {timeout}s]"
        return False, msg, msg
    output = (proc.stdout or "") + (proc.stderr or "")
    header = f"$ {command}\n[exit {proc.returncode}]"
    return proc.returncode == 0, f"{header}\n{clip(output)}", output


def committed_paths_in_head(project_root: Path, timeout: int) -> list[str]:
    command = [
        "git",
        "show",
        "--format=",
        "--name-only",
        "--no-renames",
        "-z",
        "HEAD",
    ]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            cwd=str(project_root),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"cannot list paths in HEAD commit: {exc}") from exc
    if proc.returncode != 0:
        detail = os.fsdecode(proc.stderr).strip() or f"git exited {proc.returncode}"
        raise RuntimeError(f"cannot list paths in HEAD commit: {detail}")
    return sorted({os.fsdecode(raw_path) for raw_path in proc.stdout.split(b"\0") if raw_path})


def close_review_environment(
    project_root: Path,
    item_path: Path,
    item_id: str,
    changed_paths_file: Path,
    timeout: int,
) -> dict[str, str]:
    paths = committed_paths_in_head(project_root, timeout)
    work_log = ensure_work_log(project_root / ".stage", item_id)
    verdict_file = review_verdict_path(project_root / ".stage", item_id)
    clear_review_verdict(verdict_file)
    try:
        changed_paths_file.write_text(
            json.dumps(paths, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(f"cannot write close-owned review path list: {exc}") from exc
    environment = os.environ.copy()
    environment["STAGE_WORK_ITEM_PATH"] = str(item_path.resolve())
    environment["STAGE_CHANGED_PATHS_FILE"] = str(changed_paths_file.resolve())
    environment["STAGE_REVIEW_VERDICT_FILE"] = str(verdict_file.resolve())
    environment["STAGE_WORK_LOG_PATH"] = str(work_log.resolve())
    return environment


def main() -> int:
    parser = argparse.ArgumentParser(description="Close a Stage work item by running its checks.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("item", help="Work item id, e.g. W-00000008.")
    parser.add_argument("--check", action="append", default=[], help="A verification command (repeatable). Runs in the platform shell.")
    parser.add_argument("--promotion", default=None, help=f"Set the promotion decision; must be one of {sorted(PROMOTION_FINAL)}.")
    parser.add_argument("--timeout", type=int, default=900, help="Per-check timeout in seconds.")
    parser.add_argument("--review-stage", default="implementation", help="settings.json review stage whose command runs at close.")
    args = parser.parse_args()

    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    schema_blocker = schema_migration_banner(stage_root)
    if schema_blocker:
        print(schema_blocker, file=sys.stderr)
        return 2
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        current_root = paths.current_cards
        active_relative = paths.active_index
        review_relative = paths.review_index
        current_retro_root = paths.current_retrospectives
        archive_retro_root = paths.archive_retrospectives
    else:
        current_root = Path("present", "work", "items").as_posix()
        active_relative = Path("present", "work", "active.md").as_posix()
        review_relative = Path("present", "work", "review.md").as_posix()
        current_retro_root = Path("present", "work", "retrospectives").as_posix()
        archive_retro_root = Path(
            "past", "work", "archive", "retrospectives"
        ).as_posix()
    item_path = record_path(stage_root / current_root, args.item)
    active_path = stage_root / active_relative
    review_path = stage_root / review_relative
    if not item_path.exists():
        if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
            print(f"{args.item}: no current item file at {item_path}", file=sys.stderr)
        else:
            print(f"{args.item}: no present item file at {item_path}", file=sys.stderr)
        return 2
    item_relative = item_path.relative_to(stage_root).as_posix()
    active_item_link = relative_record_link(active_relative, item_relative)
    review_item_link = relative_record_link(review_relative, item_relative)

    text = item_path.read_text(encoding="utf-8")
    work_item = item_from_fields(
        item_path,
        parse_frontmatter(item_path),
        GATE_FIELD_DEFAULTS,
        items_root=stage_root / current_root,
    )
    status = field(text, "status")

    # Reconcile a re-run: an already-completed item must sit in review.md, not active.md.
    if status == "completed":
        item_path.write_text(text, encoding="utf-8")
        active_path.write_text(
            drop_row(
                active_path.read_text(encoding="utf-8"),
                args.item,
                active_item_link,
            ),
            encoding="utf-8",
        ) if active_path.exists() else None
        ensure_review_row(
            review_path,
            args.item,
            field(text, "verification"),
            field(text, "retrospective"),
            field(text, "promotion"),
            review_item_link,
        )
        print(f"{args.item}: already completed; index reconciled")
        return 0
    if status not in OPEN_TO_CLOSE:
        print(f"{args.item}: status `{status}` is not active/review; refusing to close", file=sys.stderr)
        return 1

    blocking_children = non_terminal_children(
        args.item, load_all_work_items(stage_root)
    )
    if blocking_children:
        detail = ", ".join(
            f"{child.item_id} (`{child.status}`)" for child in blocking_children
        )
        print(
            f"{args.item}: non-terminal children block completion: {detail}",
            file=sys.stderr,
        )
        return 1

    try:
        dirty_paths = dirty_paths_in_scope(stage_root.parent, field(text, "scope"))
    except RuntimeError as exc:
        print(f"{args.item}: cannot verify worktree state; refusing to close: {exc}", file=sys.stderr)
        return 1
    if dirty_paths:
        print(
            f"{args.item}: uncommitted path(s) inside scope: {', '.join(dirty_paths)}; "
            f"required order: {ORDER_CONTRACT}",
            file=sys.stderr,
        )
        return 1

    if field(text, "retrospective") != "completed":
        print(f"{args.item}: retrospective is not completed — write it first (Completion principle)", file=sys.stderr)
        return 1
    ref = field(text, "retrospective_ref")
    if not ref or not record_path(stage_root / current_retro_root, ref).exists():
        print(f"{args.item}: retrospective_ref `{ref or 'empty'}` has no file", file=sys.stderr)
        return 1
    archive_retro = record_path(stage_root / archive_retro_root, ref)
    if archive_retro.exists():
        archived_work_item = field(archive_retro.read_text(encoding="utf-8"), "work_item")
        if archived_work_item and archived_work_item != args.item:
            print(
                f"{args.item}: retrospective id collision: {ref}.md already belongs to "
                f"{archived_work_item}; refusing to close",
                file=sys.stderr,
            )
            return 1

    # Finished work must not rest on undecided decisions (DE-00000005); the
    # audit reports the same state as DECISION002.
    for decision_ref in split_scope(field(text, "decision_refs")):
        if decision_status(stage_root, decision_ref) == "open":
            print(
                f"{args.item}: linked decision {decision_ref} is still open — close it "
                "(decided/promoted) before completing the work",
                file=sys.stderr,
            )
            return 1

    promotion = args.promotion if args.promotion is not None else field(text, "promotion")
    if promotion not in PROMOTION_FINAL:
        print(f"{args.item}: promotion `{promotion}` is not final {sorted(PROMOTION_FINAL)} — pass --promotion", file=sys.stderr)
        return 1

    checks = [*work_item.acceptance, *args.check]
    if not checks:
        print(
            f"{args.item}: no --check or acceptance given; closing must run the "
            "verification checks (no silent pass)",
            file=sys.stderr,
        )
        return 1

    if "## Verification\n" not in text:
        print(f"{args.item}: no '## Verification' section to record evidence into; refusing", file=sys.stderr)
        return 1

    project_root = stage_root.parent
    verification_blocks: list[str] = []
    for command in checks:
        ok, block, _raw = run_check(command, args.timeout, project_root)
        verification_blocks.append(block)
        if not ok:
            print(f"{args.item}: check failed, nothing changed:\n{block}", file=sys.stderr)
            return 1
        if re.search(r"Ran 0 tests", block):
            print(f"{args.item}: WARNING a check reported 'Ran 0 tests' — it may verify nothing", file=sys.stderr)

    # Autonomous work always requires an opposite-venue reviewer. Non-autonomous
    # review remains field-driven: only an item that DECLARES `review: pending`
    # runs the legacy per-stage command. Both paths fail on nonzero exit OR a
    # `BLOCK:` verdict line, scanned on RAW output so a verdict is never clipped.
    review_passed = False
    review_heading = ""
    if work_item.autonomous:
        review_command, review_error = resolve_independent_review_command(
            load_review_config(stage_root), work_item.venue
        )
        if review_error:
            print(
                f"{args.item}: independent review config unusable; autonomous item "
                f"cannot close (fix .stage/settings.json):\n{review_error}",
                file=sys.stderr,
            )
            return 1
        if not review_command:
            print(
                f"{args.item}: autonomous item cannot close without an opposite-venue "
                "reviewer command in review.reviewers",
                file=sys.stderr,
            )
            return 1
        try:
            with tempfile.TemporaryDirectory(prefix="stage-close-review-") as review_tmp:
                review_environment = close_review_environment(
                    project_root,
                    item_path,
                    work_item.item_id,
                    Path(review_tmp) / "changed-paths.json",
                    args.timeout,
                )
                ok, block, _raw = run_check(
                    review_command,
                    args.timeout,
                    project_root,
                    env=review_environment,
                )
        except RuntimeError as exc:
            print(
                f"{args.item}: cannot prepare independent review material: {exc}",
                file=sys.stderr,
            )
            return 1
        verdict_error = review_verdict_error(
            Path(review_environment["STAGE_REVIEW_VERDICT_FILE"])
        )
        if not ok or verdict_error:
            detail = f"\n{verdict_error}" if verdict_error else ""
            print(
                f"{args.item}: independent review did not pass; work item unchanged:"
                f"\n{block}{detail}",
                file=sys.stderr,
            )
            return 1
        review_passed = True
        review_heading = "Independent review at close"
    elif (field(text, "review") or "not_required") == "pending":
        review_command, review_error = resolve_review_command(load_review_config(stage_root), args.review_stage)
        if review_error:
            print(f"{args.item}: review config unusable (fix .stage/settings.json):\n{review_error}", file=sys.stderr)
            return 1
        if not review_command:
            print(f"{args.item}: review is pending but stage `{args.review_stage}` configures no review command in settings.json", file=sys.stderr)
            return 1
        try:
            with tempfile.TemporaryDirectory(prefix="stage-close-review-") as review_tmp:
                review_environment = close_review_environment(
                    project_root,
                    item_path,
                    work_item.item_id,
                    Path(review_tmp) / "changed-paths.json",
                    args.timeout,
                )
                ok, block, _raw = run_check(
                    review_command,
                    args.timeout,
                    project_root,
                    env=review_environment,
                )
        except RuntimeError as exc:
            print(
                f"{args.item}: cannot prepare review material: {exc}",
                file=sys.stderr,
            )
            return 1
        verdict_error = review_verdict_error(
            Path(review_environment["STAGE_REVIEW_VERDICT_FILE"])
        )
        if not ok or verdict_error:
            detail = f"\n{verdict_error}" if verdict_error else ""
            print(
                f"{args.item}: review did not pass; work item unchanged:\n"
                f"{block}{detail}",
                file=sys.stderr,
            )
            return 1
        review_passed = True
        review_heading = "Review at close"

    close_date = date.today().isoformat()
    evidence = (
        f"### Executed at close — {close_date}\n\n```\n"
        + "\n\n".join(verification_blocks)
        + "\n```"
    )
    if review_passed:
        evidence += (
            f"\n\n### {review_heading} — {close_date}\n\n```\n"
            f"Review report: {work_log_reference(work_item.item_id)}\n```"
        )
    try:
        updated = append_to_section(text, "Verification", evidence)
        updated = set_field(updated, "verification", "passed")
        updated = set_field(updated, "promotion", promotion)
        if review_passed:
            updated = set_field(updated, "review", "passed")
        updated = set_field(updated, "status", "completed")
    except ValueError as exc:
        print(
            f"{args.item}: cannot close; {exc}; work item unchanged",
            file=sys.stderr,
        )
        return 1
    item_path.write_text(updated, encoding="utf-8")

    # Index last, derived from the new status, so a re-run always converges.
    if active_path.exists():
        active_path.write_text(
            drop_row(
                active_path.read_text(encoding="utf-8"),
                args.item,
                active_item_link,
            ),
            encoding="utf-8",
        )
    ensure_review_row(
        review_path,
        args.item,
        "passed",
        "completed",
        promotion,
        review_item_link,
    )
    print(f"{args.item}: closed (verification passed on {len(checks)} check(s), status completed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
