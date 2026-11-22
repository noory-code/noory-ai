#!/usr/bin/env python3
"""Move a card to its end state by calling the commands that own that move.

The driver never edits a card's status itself. Closing runs close_work, giving
up runs escalate_work, and the machine retrospective only fills the slots and
the facts — what was learned is left for whoever merges the run, because a run
cannot judge from inside whether its own behavior should bind future work.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (
    STAGE_ROOT / "hooks",
    STAGE_ROOT / "scripts",
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import work_log_reference  # noqa: E402
from driver_environment import project_environment  # noqa: E402
from lifecycle_paths import v4_lifecycle_paths  # noqa: E402
from stage_record_paths import record_path  # noqa: E402
from stage_work import WorkItem, parse_frontmatter, parse_string_list  # noqa: E402

CLOSE_WORK = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ESCALATE_WORK = STAGE_ROOT / "scripts" / "escalate_work.py"
AUDIT = STAGE_ROOT / "scripts" / "audit_stage.py"

WORK_ID_RE = re.compile(r"^W-[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9_-]*)?$")

RETRO_SECTIONS = (
    "Decision points",
    "Context that was missing",
    "Rule candidate",
)


def write_driver_retrospective(
    stage_root: Path, item: WorkItem
) -> tuple[str, str]:
    """Write a machine-generated retrospective, flagged driver-generated.

    Returns (retro_id, error). The reflective retrospective is deliberately
    thin — a human reviews it when merging the run branch (DE-24, mode A).
    """

    note = "driver-generated (사람 머지 검토 대상)"
    # Neutral wording: this is written BEFORE close_work verifies. It must not
    # claim success — the item's Verification (stamped by close_work) is the
    # source of truth for whether acceptance and the independent review passed.
    sections = {
        "Decision points": (
            f"{note}: 무인 드라이버가 {item.item_id}의 executor를 실행하고 결과를 커밋했다. "
            "기계 실행이라 별도 결정은 없다. 실행자의 결정·이유·변경 경로 주장은 "
            f"`{work_log_reference(item.item_id)}`가 소유하고, acceptance·독립 판정의 "
            "통과 여부는 항목의 Verification(close_work가 기록)이 정본이다."
        ),
        "Context that was missing": f"{note}: 반성적 회고는 사람이 브랜치 머지 시 보완.",
        # A run cannot judge from inside whether its own behavior should bind
        # future cards, so it leaves the rule candidate to whoever merges it.
        "Rule candidate": f"{note}: 머지하는 사람이 채운다 — 이 실행이 남긴 규칙 후보가 있으면.",
    }

    def content_for(retro_id: str) -> str:
        body = (
            f"---\nid: {retro_id}\nwork_item: {item.item_id}\n---\n\n"
            f"# {retro_id} {item.item_id} 무인 드라이버 회고\n"
        )
        for heading in RETRO_SECTIONS:
            body += f"\n## {heading}\n\n{sections[heading]}\n"
        return body

    try:
        retro_id = reserve_retrospective(
            stage_root,
            item.item_id,
            content_for,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        return "", f"cannot write retrospective for {item.item_id}: {exc}"
    return retro_id, ""


def current_card_path(stage_root: Path, item_id: str) -> Path:
    return record_path(stage_root / v4_lifecycle_paths().current_cards, item_id)


def mark_retrospective(stage_root: Path, item_id: str, retro_id: str) -> None:
    path = current_card_path(stage_root, item_id)
    text = path.read_text(encoding="utf-8")
    text = set_frontmatter_field(text, "retrospective", "completed")
    text = set_frontmatter_field(text, "retrospective_ref", retro_id)
    path.write_text(text, encoding="utf-8")


def close_via_close_work(
    project_root: Path,
    item_id: str,
    extra_checks: list[str],
    timeout: int,
    promotion_default: str | None = None,
    review_timeout: int | None = None,
) -> tuple[bool, str]:
    """Reuse the reviewed close_work.py: acceptance + (autonomous) independent review + close.

    `timeout` bounds each check and `review_timeout` (default: `timeout`) bounds the
    review. The outer kill covers every check plus the review, so close_work is
    never cut off while its own budgets still run and the reviewer is never orphaned.
    """

    card_fields = parse_frontmatter(current_card_path(project_root / ".stage", item_id))
    raw_promotion = card_fields.get("promotion", "")
    promotion = raw_promotion.strip() if isinstance(raw_promotion, str) else ""
    if promotion == "pending" and promotion_default is not None:
        promotion = promotion_default
    review_budget = timeout if review_timeout is None else review_timeout
    command = [
        sys.executable,
        str(CLOSE_WORK),
        "--project-root",
        str(project_root),
        item_id,
        "--promotion",
        promotion,
        "--timeout",
        str(timeout),
        "--review-timeout",
        str(review_budget),
    ]
    for check in extra_checks:
        command += ["--check", check]
    check_count = len(parse_string_list(card_fields.get("acceptance"))) + len(extra_checks)
    outer_timeout = timeout * check_count + review_budget + 60
    try:
        proc = subprocess.run(
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=outer_timeout,
            env=project_environment(project_root),
        )
    except subprocess.TimeoutExpired:
        return False, f"close_work timed out after {outer_timeout}s"
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
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"escalate_work timed out after {timeout}s"
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "") + (proc.stderr or "")


def shell_command(args: list[str], os_name: str | None = None) -> str:
    """Join arguments the way the named platform's shell parses them.

    The result is handed to a shell, and the two shells disagree: POSIX shells
    strip single quotes, `cmd.exe` does not. Quoting for one breaks the other,
    so each gets its own joiner. Windows arguments containing shell
    metacharacters must be quoted even when they contain no whitespace.

    ``os_name`` defaults to the running platform. It is a parameter so a test can
    exercise the other branch without reaching into the process-wide ``os``
    module — there is no Windows runner here, so both branches have to be
    reachable from any host.
    """

    if (os_name or os.name) == "nt":
        rendered_args: list[str] = []
        for arg in args:
            rendered = subprocess.list2cmdline([arg])
            if any(character in arg for character in "&^|<>") and not (
                rendered.startswith('"') and rendered.endswith('"')
            ):
                trailing_backslashes = len(rendered) - len(rendered.rstrip("\\"))
                rendered += "\\" * trailing_backslashes
                rendered = f'"{rendered}"'
            rendered_args.append(rendered)
        return " ".join(rendered_args)
    return shlex.join(args)


def audit_check(project_root: Path, os_name: str | None = None) -> str:
    return shell_command(
        [sys.executable, str(AUDIT), "--project-root", str(project_root)], os_name
    )


def set_frontmatter_field(text: str, name: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(name)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def retrospective_id_for_work_item(
    item_id: str,
) -> str:
    """Derive the retrospective ID a work item tries first: `R-` plus its number."""

    if not WORK_ID_RE.fullmatch(item_id):
        raise ValueError(f"invalid work item ID for retrospective: {item_id}")
    return f"R-{item_id[2:]}"


def reserve_retrospective(
    stage_root: Path,
    item_id: str,
    content_for: Callable[[str], str],
) -> str:
    """Reserve the work item's retrospective without counting existing records.

    The first choice is `R-` plus the item's number. A project that numbered
    retrospectives one after another before that rule can hold that slot for
    another item. Then the slot's owner shows the way on: when `R-n` belongs to
    `W-m`, `W-m` already has its retrospective and will never need `R-m`, so
    `R-m` is tried next, and so on until a slot is free.

    Each work item owns at most one retrospective, so following owners is
    one-to-one: two items' chains never meet and never end on the same slot,
    even in copies of `.stage` that split from the same state. Counting the
    records and taking the last number plus one gave every copy the same answer
    (W-00000259), so allocation never counts.

    The walk stops with an error when the item's own slot is archived, when a
    slot's owner is not a work item, or when the chain comes back to a slot it
    already passed, which only inconsistent records can cause.
    """

    paths = v4_lifecycle_paths()
    current_root = stage_root / paths.current_retrospectives
    archive_root = stage_root / paths.archive_retrospectives
    current_root.mkdir(parents=True, exist_ok=True)

    card_path = current_card_path(stage_root, item_id)
    if card_path.is_file():
        bound_id = str(parse_frontmatter(card_path).get("retrospective_ref", "")).strip()
        bound_path = current_root / f"{bound_id}.md"
        if (
            bound_id
            and bound_path.is_file()
            and str(parse_frontmatter(bound_path).get("work_item", "")) == item_id
        ):
            return bound_id

    retro_id = retrospective_id_for_work_item(item_id)
    passed: list[str] = []
    while True:
        current_path = current_root / f"{retro_id}.md"
        archive_path = archive_root / f"{retro_id}.md"
        if current_path.exists():
            owner = str(parse_frontmatter(current_path).get("work_item", ""))
            if owner == item_id:
                return retro_id
            place = "current"
        elif archive_path.exists():
            owner = str(parse_frontmatter(archive_path).get("work_item", ""))
            if owner == item_id:
                raise RuntimeError(
                    f"retrospective {retro_id} is already archived for {item_id}; "
                    "cannot reserve it as current"
                )
            place = "archived"
        else:
            try:
                with current_path.open("x", encoding="utf-8") as handle:
                    handle.write(content_for(retro_id))
            except FileExistsError:
                continue  # created meanwhile; read its owner on the next pass
            return retro_id

        passed.append(retro_id)
        taken = f"retrospective {retro_id} is already {place} for "
        if not WORK_ID_RE.fullmatch(owner):
            raise RuntimeError(
                f"{taken}{owner or 'an unknown work item'}, not {item_id}; "
                "its owner is not a work item, so no other number can be chosen from it"
            )
        next_id = retrospective_id_for_work_item(owner)
        if next_id in passed:
            raise RuntimeError(
                f"{taken}{owner}, not {item_id}; following the owners of "
                f"{', '.join(passed)} returns to {next_id}, so the records disagree "
                "about who owns which retrospective"
            )
        retro_id = next_id
