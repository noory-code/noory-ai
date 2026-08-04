#!/usr/bin/env python3
"""Close or reopen Stage observations, questions, and proposals as one transaction."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))
HOOK_ROOT = Path(__file__).resolve().parents[1] / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import init_stage  # noqa: E402
from stage_paths import read_settings, schema_migration_banner  # noqa: E402


OUTCOMES = ("accepted", "rejected", "partial")
START_MARKER_RE = re.compile(
    r"<!-- stage-close-record:start v1 (?P<payload>[A-Za-z0-9_-]+) -->"
)
END_MARKER = "<!-- stage-close-record:end -->"
STATUS_HEADING_RE = re.compile(r"^##[ \t]+Status[ \t]*$", re.MULTILINE)
NEXT_SECTION_RE = re.compile(r"^##[ \t]+", re.MULTILINE)
TABLE_ENTRY_RE = re.compile(r"^[ \t]*\|", re.MULTILINE)
LIST_ENTRY_RE = re.compile(r"^(?P<indent>[ \t]*)[-+*][ \t]+", re.MULTILINE)


class CloseRecordError(RuntimeError):
    """The requested record transition cannot be completed safely."""


@dataclass(frozen=True)
class RecordFamily:
    prefix: str
    kind: str
    live_root: Path
    live_index: Path
    archive_root: Path
    archive_index: Path


FAMILIES = {
    "O": RecordFamily(
        "O",
        "observation",
        Path("state/observations"),
        Path("state/current.md"),
        Path("official/state/archive"),
        Path("official/state/archive/index.md"),
    ),
    "Q": RecordFamily(
        "Q",
        "question",
        Path("state/questions"),
        Path("state/questions.md"),
        Path("official/state/archive"),
        Path("official/state/archive/index.md"),
    ),
    "P": RecordFamily(
        "P",
        "proposal",
        Path("proposals"),
        Path("proposals/index.md"),
        Path("official/proposals/archive"),
        Path("official/proposals/archive/index.md"),
    ),
}


def _record_family(record_id: str) -> RecordFamily:
    match = re.fullmatch(r"(?P<prefix>O|Q|P)-\d{3,}", record_id)
    if match is None:
        raise CloseRecordError(
            "record ID must be an observation, question, or proposal ID (O-, Q-, or P-)"
        )
    return FAMILIES[match.group("prefix")]


def _newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _table_record_id(line: str) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return cells[0] if cells else ""


def _index_entry_span(text: str, record_id: str) -> tuple[int, int]:
    matches: list[tuple[int, int]] = []
    lines = text.splitlines(keepends=True)
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)

    for index, line in enumerate(lines):
        if TABLE_ENTRY_RE.match(line) and _table_record_id(line) == record_id:
            matches.append((offsets[index], offsets[index] + len(line)))
            continue
        list_match = LIST_ENTRY_RE.match(line)
        if list_match is None or f"[{record_id}]" not in line:
            continue
        indent_width = len(list_match.group("indent").expandtabs(4))
        end_index = index + 1
        while end_index < len(lines):
            following = lines[end_index]
            if not following.strip():
                break
            following_indent = following[: len(following) - len(following.lstrip())]
            if len(following_indent.expandtabs(4)) <= indent_width:
                break
            end_index += 1
        end = offsets[end_index] if end_index < len(lines) else len(text)
        matches.append((offsets[index], end))

    if not matches:
        raise CloseRecordError(f"{record_id} has no entry in its live index")
    if len(matches) != 1:
        raise CloseRecordError(f"{record_id} has more than one entry in its live index")
    return matches[0]


def _remove_index_entry(text: str, record_id: str) -> tuple[str, str]:
    start, end = _index_entry_span(text, record_id)
    return text[:start] + text[end:], text[start:end]


def _append_index_entry(text: str, entry: str) -> str:
    newline = _newline(text)
    if re.fullmatch(r"[ \t]*[-+*][ \t]*(?:\r?\n)?", text.splitlines(keepends=True)[-1]):
        lines = text.splitlines(keepends=True)
        lines[-1] = entry
        return "".join(lines)
    body = text.rstrip("\r\n")
    entry_body = entry.rstrip("\r\n")
    return f"{body}{newline}{entry_body}{newline}"


def _drop_archive_row(text: str, record_id: str) -> str:
    lines = text.splitlines(keepends=True)
    matches = [
        index
        for index, line in enumerate(lines)
        if TABLE_ENTRY_RE.match(line) and _table_record_id(line) == record_id
    ]
    if len(matches) != 1:
        raise CloseRecordError(
            f"{record_id} must have exactly one entry in its archive index"
        )
    del lines[matches[0]]
    return "".join(lines)


def _escape_table_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|")


def _append_archive_row(
    text: str,
    family: RecordFamily,
    record_id: str,
    reason: str,
    outcome: str | None,
) -> str:
    if re.search(rf"^[ \t]*\|[ \t]*{re.escape(record_id)}[ \t]*\|", text, re.MULTILINE):
        raise CloseRecordError(f"{record_id} already has an archive index entry")
    second = outcome if family.prefix == "P" else family.kind
    row = (
        f"| {record_id} | {second} | {_escape_table_cell(reason)} | "
        f"[{record_id}]({record_id}.md) |"
    )
    newline = _newline(text)
    return f"{text.rstrip(chr(13) + chr(10))}{newline}{row}{newline}"


def _encode_metadata(entry: str, leading: str, trailing: str) -> str:
    raw = json.dumps(
        {
            "index_entry": entry,
            "leading": leading,
            "trailing": trailing,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_metadata(payload: str) -> dict[str, str]:
    try:
        padding = "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload + padding).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CloseRecordError("the close marker contains invalid rollback metadata") from exc
    if not isinstance(data, dict) or any(
        not isinstance(data.get(key), str) for key in ("index_entry", "leading", "trailing")
    ):
        raise CloseRecordError("the close marker is missing rollback metadata")
    return {key: data[key] for key in ("index_entry", "leading", "trailing")}


def _project_language(stage_root: Path) -> str:
    _path, data, error = read_settings(stage_root)
    if error is None and isinstance(data, dict) and isinstance(data.get("language"), str):
        return data["language"]
    return "en"


def _close_labels(language: str, reason: str, outcome: str | None) -> list[str]:
    if language == "ko":
        lines = [f"닫은 근거: {reason}"]
        if outcome is not None:
            lines.insert(0, f"결과: {outcome}")
        return lines
    lines = [f"Closed reason: {reason}"]
    if outcome is not None:
        lines.insert(0, f"Outcome: {outcome}")
    return lines


def _add_close_marker(
    text: str,
    entry: str,
    language: str,
    reason: str,
    outcome: str | None,
) -> str:
    if START_MARKER_RE.search(text):
        raise CloseRecordError("record already contains a close marker")
    status = STATUS_HEADING_RE.search(text)
    if status is None:
        raise CloseRecordError("record is missing the required `## Status` section")
    following = NEXT_SECTION_RE.search(text, status.end())
    insertion_at = following.start() if following is not None else len(text)
    prefix = text[:insertion_at]
    suffix = text[insertion_at:]
    newline = _newline(text)
    if prefix.endswith(newline * 2):
        leading = ""
    elif prefix.endswith(newline):
        leading = newline
    else:
        leading = newline * 2
    trailing = newline * 2 if suffix.startswith("## ") else newline
    payload = _encode_metadata(entry, leading, trailing)
    human = newline.join(_close_labels(language, reason, outcome))
    block = (
        f"{leading}<!-- stage-close-record:start v1 {payload} -->{newline}"
        f"{human}{newline}{END_MARKER}{trailing}"
    )
    return prefix + block + suffix


def _remove_close_marker(text: str) -> tuple[str, str]:
    start = START_MARKER_RE.search(text)
    if start is None:
        raise CloseRecordError("archived record has no close marker")
    end_start = text.find(END_MARKER, start.end())
    if end_start < 0:
        raise CloseRecordError("archived record has an incomplete close marker")
    if START_MARKER_RE.search(text, start.end()) is not None:
        raise CloseRecordError("archived record has more than one close marker")
    metadata = _decode_metadata(start.group("payload"))
    removal_start = start.start() - len(metadata["leading"])
    removal_end = end_start + len(END_MARKER) + len(metadata["trailing"])
    if removal_start < 0 or text[removal_start : start.start()] != metadata["leading"]:
        raise CloseRecordError("archived record close marker has invalid leading metadata")
    marker_end = end_start + len(END_MARKER)
    if text[marker_end:removal_end] != metadata["trailing"]:
        raise CloseRecordError("archived record close marker has invalid trailing metadata")
    return text[:removal_start] + text[removal_end:], metadata["index_entry"]


def _archive_index_template(stage_root: Path, relative: Path) -> str:
    source = init_stage.template_source(relative, _project_language(stage_root))
    if not source.is_file():
        raise CloseRecordError(f"archive index template is missing: {source}")
    return source.read_text(encoding="utf-8")


def _replace_staged_file(staged: Path, target: Path) -> None:
    """Commit one already-written transaction file."""

    os.replace(staged, target)


def _restore_file(path: Path, content: bytes | None, staging_root: Path) -> None:
    if content is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    restore = staging_root / f"restore-{len(list(staging_root.iterdir()))}"
    restore.write_bytes(content)
    os.replace(restore, path)


def _apply_transaction(stage_root: Path, changes: dict[Path, bytes | None]) -> None:
    snapshots = {path: path.read_bytes() if path.exists() else None for path in changes}
    runtime_root = stage_root / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    created_dirs: list[Path] = []
    try:
        with tempfile.TemporaryDirectory(prefix="close-record-", dir=runtime_root) as tmp:
            staging_root = Path(tmp)
            staged: dict[Path, Path] = {}
            for index, (target, content) in enumerate(changes.items()):
                if content is None:
                    continue
                staged_path = staging_root / f"write-{index}"
                staged_path.write_bytes(content)
                staged[target] = staged_path
            try:
                for target, content in changes.items():
                    missing: list[Path] = []
                    parent = target.parent
                    while not parent.exists() and parent != stage_root.parent:
                        missing.append(parent)
                        parent = parent.parent
                    target.parent.mkdir(parents=True, exist_ok=True)
                    created_dirs.extend(reversed(missing))
                    if content is None:
                        target.unlink()
                    else:
                        _replace_staged_file(staged[target], target)
            except Exception as exc:
                rollback_errors: list[str] = []
                for target, original in reversed(list(snapshots.items())):
                    try:
                        _restore_file(target, original, staging_root)
                    except OSError as rollback_exc:
                        rollback_errors.append(f"{target}: {rollback_exc}")
                for directory in reversed(created_dirs):
                    try:
                        directory.rmdir()
                    except OSError:
                        pass
                detail = (
                    f"; rollback also failed: {'; '.join(rollback_errors)}"
                    if rollback_errors
                    else ""
                )
                raise CloseRecordError(f"transaction failed: {exc}{detail}") from exc
    except OSError as exc:
        raise CloseRecordError(f"cannot prepare record transaction: {exc}") from exc


def close_record(
    stage_root: Path,
    record_id: str,
    reason: str,
    outcome: str | None,
) -> str:
    family = _record_family(record_id)
    if not reason.strip():
        raise CloseRecordError("--reason must not be empty")
    if "\n" in reason or "\r" in reason:
        raise CloseRecordError("--reason must be one line")
    if family.prefix == "P" and outcome not in OUTCOMES:
        raise CloseRecordError("proposal closing requires --outcome accepted, rejected, or partial")
    if family.prefix != "P" and outcome is not None:
        raise CloseRecordError("--outcome is valid only for proposals")

    source = stage_root / family.live_root / f"{record_id}.md"
    destination = stage_root / family.archive_root / f"{record_id}.md"
    if destination.exists() and not source.exists():
        return f"{record_id}: already closed (skipped)"
    if not source.is_file():
        raise CloseRecordError(f"live record not found: {source}")
    if destination.exists():
        raise CloseRecordError(f"archive record already exists: {destination}")

    live_index = stage_root / family.live_index
    archive_index = stage_root / family.archive_index
    if not live_index.is_file():
        raise CloseRecordError(f"live index not found: {live_index}")
    source_text = source.read_text(encoding="utf-8")
    live_index_text = live_index.read_text(encoding="utf-8")
    updated_live_index, entry = _remove_index_entry(live_index_text, record_id)
    archived_text = _add_close_marker(
        source_text,
        entry,
        _project_language(stage_root),
        reason.strip(),
        outcome,
    )
    archive_index_text = (
        archive_index.read_text(encoding="utf-8")
        if archive_index.is_file()
        else _archive_index_template(stage_root, family.archive_index)
    )
    updated_archive_index = _append_archive_row(
        archive_index_text,
        family,
        record_id,
        reason.strip(),
        outcome,
    )
    _apply_transaction(
        stage_root,
        {
            destination: archived_text.encode("utf-8"),
            archive_index: updated_archive_index.encode("utf-8"),
            live_index: updated_live_index.encode("utf-8"),
            source: None,
        },
    )
    return f"{record_id}: closed into {family.archive_root.as_posix()}"


def reopen_record(stage_root: Path, record_id: str) -> str:
    family = _record_family(record_id)
    source = stage_root / family.archive_root / f"{record_id}.md"
    destination = stage_root / family.live_root / f"{record_id}.md"
    if destination.exists() and not source.exists():
        return f"{record_id}: already live (skipped)"
    if not source.is_file():
        raise CloseRecordError(f"archive record not found: {source}")
    if destination.exists():
        raise CloseRecordError(f"live record already exists: {destination}")

    live_index = stage_root / family.live_index
    archive_index = stage_root / family.archive_index
    if not live_index.is_file() or not archive_index.is_file():
        raise CloseRecordError("both live and archive indexes must exist before reopening")
    restored_text, entry = _remove_close_marker(source.read_text(encoding="utf-8"))
    updated_live_index = _append_index_entry(live_index.read_text(encoding="utf-8"), entry)
    updated_archive_index = _drop_archive_row(
        archive_index.read_text(encoding="utf-8"), record_id
    )
    _apply_transaction(
        stage_root,
        {
            destination: restored_text.encode("utf-8"),
            live_index: updated_live_index.encode("utf-8"),
            archive_index: updated_archive_index.encode("utf-8"),
            source: None,
        },
    )
    return f"{record_id}: reopened into {family.live_root.as_posix()}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Close or reopen a Stage observation, question, or proposal atomically."
    )
    parser.add_argument("--project-root", default=".", help="Project root (default: cwd).")
    commands = parser.add_subparsers(dest="command", required=True)
    close = commands.add_parser("close", help="Move a live record into its archive.")
    close.add_argument("record_id", help="O-, Q-, or P-prefixed record ID.")
    close.add_argument("--reason", required=True, help="One-line reason for closing the record.")
    close.add_argument("--outcome", choices=OUTCOMES, help="Required proposal outcome.")
    reopen = commands.add_parser("reopen", help="Return an archived record to its live drawer.")
    reopen.add_argument("record_id", help="O-, Q-, or P-prefixed record ID.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    if not stage_root.is_dir():
        print(f"Stage root not found: {stage_root}", file=sys.stderr)
        return 2
    blocker = schema_migration_banner(stage_root)
    if blocker:
        print(blocker, file=sys.stderr)
        return 2
    try:
        if args.command == "close":
            result = close_record(stage_root, args.record_id, args.reason, args.outcome)
        else:
            result = reopen_record(stage_root, args.record_id)
    except (CloseRecordError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
