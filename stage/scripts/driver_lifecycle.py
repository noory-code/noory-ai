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
from stage_record_paths import record_path, record_paths  # noqa: E402
from stage_work import WorkItem, parse_frontmatter  # noqa: E402

CLOSE_WORK = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ESCALATE_WORK = STAGE_ROOT / "scripts" / "escalate_work.py"
AUDIT = STAGE_ROOT / "scripts" / "audit_stage.py"

WORK_ID_RE = re.compile(r"^W-[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9_-]*)?$")
RETRO_ID_RE = re.compile(r"^R-([0-9]+)$")

RETRO_SECTIONS = (
    "Work",
    "Decision points",
    "Principles applied",
    "Context that helped",
    "Context that was missing",
    "Next changes",
    "Rule candidate",
    "Promotion decision",
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
        "Work": (
            f"{note}: 무인 드라이버가 {item.item_id}의 executor를 실행하고 결과를 커밋했다. "
            "acceptance·독립 판정의 실제 통과 여부와 최종 완료는 항목의 Verification"
            "(close_work가 기록)이 정본이다. 실행자의 작업 내용·이유·변경 경로 주장은 "
            f"`{work_log_reference(item.item_id)}`가 소유한다."
        ),
        "Decision points": f"{note}: 기계 실행, 별도 결정 없음.",
        "Principles applied": f"{note}: Honesty, Fail Fast, No partial completion.",
        "Context that helped": f"{note}: 항목 acceptance가 종료를 결정적으로 판정.",
        "Context that was missing": f"{note}: 반성적 회고는 사람이 브랜치 머지 시 보완.",
        "Next changes": f"{note}: 사람이 격리 브랜치를 검토·머지.",
        # A run cannot judge from inside whether its own behavior should bind
        # future cards, so it leaves the rule candidate to whoever merges it.
        "Rule candidate": f"{note}: 머지하는 사람이 채운다 — 이 실행이 남긴 규칙 후보가 있으면.",
        "Promotion decision": (
            f"{note}: 항목 Verification의 결과를 따른다(close_work가 acceptance·독립 판정 통과 시에만 completed로 스탬프)."
        ),
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
        retro_id = retrospective_id_for_work_item(
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
) -> tuple[bool, str]:
    """Reuse the reviewed close_work.py: acceptance + (autonomous) independent review + close."""

    raw_promotion = parse_frontmatter(
        current_card_path(project_root / ".stage", item_id)
    ).get("promotion", "")
    promotion = raw_promotion.strip() if isinstance(raw_promotion, str) else ""
    if promotion == "pending" and promotion_default is not None:
        promotion = promotion_default
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
    ]
    for check in extra_checks:
        command += ["--check", check]
    try:
        proc = subprocess.run(
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout + 60,
            env=project_environment(project_root),
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
    stage_root: Path,
    item_id: str,
    content_for: Callable[[str], str],
) -> str:
    """Atomically reserve a retrospective, preferring the work item's number."""

    if not WORK_ID_RE.fullmatch(item_id):
        raise ValueError(f"invalid work item ID for retrospective: {item_id}")

    paths = v4_lifecycle_paths()
    current_root = stage_root / paths.current_retrospectives
    archive_root = stage_root / paths.archive_retrospectives
    current_root.mkdir(parents=True, exist_ok=True)

    numbers: set[int] = set()
    owned_ids: list[str] = []
    for root in (current_root, archive_root):
        for path in record_paths(root, pattern="R-*.md"):
            fields = parse_frontmatter(path)
            identities = (path.stem, str(fields.get("id", "")))
            for identity in identities:
                match = RETRO_ID_RE.fullmatch(identity)
                if match:
                    numbers.add(int(match.group(1)))
            record_id = str(fields.get("id", ""))
            if (
                root == current_root
                and fields.get("work_item", "") == item_id
                and RETRO_ID_RE.fullmatch(record_id)
            ):
                owned_ids.append(record_id)

    owned_ids = sorted(set(owned_ids))
    if len(owned_ids) > 1:
        raise RuntimeError(
            f"work item {item_id} already owns multiple retrospectives: "
            f"{', '.join(owned_ids)}"
        )
    if owned_ids:
        return owned_ids[0]

    def reserve(retro_id: str) -> bool:
        path = record_path(current_root, retro_id)
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content_for(retro_id))
        except FileExistsError:
            return False
        return True

    preferred_id = f"R-{item_id[2:]}"
    preferred_path = record_path(current_root, preferred_id)
    preferred_match = RETRO_ID_RE.fullmatch(preferred_id)
    preferred_number = int(preferred_match.group(1)) if preferred_match else None
    if preferred_path.exists():
        if parse_frontmatter(preferred_path).get("work_item", "") == item_id:
            return preferred_id
    elif preferred_number not in numbers and reserve(preferred_id):
        return preferred_id

    candidate = (max(numbers) + 1) if numbers else 1
    for _ in range(1000):
        retro_id = f"R-{candidate:08d}"
        if reserve(retro_id):
            return retro_id
        candidate += 1
    raise RuntimeError("could not allocate a free retrospective id")
