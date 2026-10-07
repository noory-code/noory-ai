"""Read bounded source sections and verify recorded file evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess


class PacketError(ValueError):
    pass


def relative_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Empty path")
    portable = value.replace("\\", "/")
    if (portable.startswith("/") or PureWindowsPath(value).drive
            or ".." in portable.split("/") or any(mark in value for mark in "*?[")):
        raise ValueError("Path must stay inside the project and cannot use globs")
    path = root / PurePosixPath(portable)
    try:
        path.resolve().relative_to(root.resolve())
    except (ValueError, RuntimeError) as error:
        raise ValueError("Path resolves outside the project") from error
    return path


def section(text: str, heading: str) -> str | None:
    """Return H2 body with outer whitespace stripped; ignore fenced headings."""
    active = False
    body = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            if active:
                body.append(line)
            continue
        h2 = re.fullmatch(r"##[ \t]+(.+?)[ \t]*\r?\n?", line) if fence is None else None
        if h2:
            if active:
                break
            active = h2.group(1) == heading
        elif active:
            body.append(line)
    return "".join(body).strip() if active else None


def source_status(origin: dict, root: Path, project_key: str) -> str:
    if origin.get("kind") not in {"stage_card", "stage_decision"}:
        return "not_checkable"
    reference = origin.get("source_ref", "")
    if not isinstance(reference, str) or not reference.startswith("stage:"):
        return "rejected_ref"
    prefix = "stage:" + project_key + "/"
    if not isinstance(reference, str) or not reference.startswith(prefix):
        return "not_checkable"
    target, separator, heading = reference[len(prefix):].partition("#")
    try:
        path = relative_path(root, target)
    except ValueError:
        return "rejected_ref"
    if not separator or not heading:
        return "missing"
    try:
        body = section(path.read_text(encoding="utf-8"), heading)
    except (OSError, UnicodeError):
        return "missing"
    if body is None:
        return "missing"
    actual = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return "matches" if actual == origin.get("source_sha256") else "changed"


def evidence(progress: str, root: Path) -> list[str]:
    lines = []
    for line in record_lines(progress, "Evidence"):
        try:
            record = json.loads(line.partition(":")[2])
            if not isinstance(record, dict):
                raise ValueError("Evidence must be a JSON object")
            if record.get("kind") == "check":
                lines.append(json.dumps(record, ensure_ascii=False) + " — not rerun by this packet")
                continue
            if record.get("kind") != "file":
                raise ValueError("Unknown evidence kind")
            path = relative_path(root, record.get("path"))
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                status = "matches" if actual == record.get("sha256") else "changed"
            except OSError:
                status, actual = "missing", None
            try:
                result = subprocess.run(
                    ["git", "--literal-pathspecs", "status", "--porcelain", "--", record["path"]],
                    cwd=root, capture_output=True, text=True, shell=False, timeout=30,
                )
                dirty = bool(result.stdout.strip()) if result.returncode == 0 else "unknown"
            except (OSError, subprocess.TimeoutExpired):
                dirty = "unknown"
            lines.append(json.dumps({**record, "status": status, "current_sha256": actual,
                                     "uncommitted": dirty}, ensure_ascii=False))
        except (ValueError, TypeError) as error:
            lines.append(f"Rejected evidence: {error}")
    return lines or ["No recorded evidence; completion is not established."]


def record_lines(progress: str, label: str) -> list[str]:
    """Read plain, bulleted, or date-prefixed records without discarding malformed ones."""
    result = []
    prefix = r"^\s*(?:[-*]\s+)?(?:\d{4}-\d{2}-\d{2}(?:T[^\s]+)?[: ]+\s*)?"
    for line in progress.splitlines():
        match = re.match(prefix + re.escape(label) + r":\s*(.*)$", line)
        if match:
            result.append(label + ": " + match.group(1))
        elif label + ":" in line:
            result.append("Unparsed record: " + line.strip())
    return result
