"""Classify a criterion without broadening its path or work-kind conditions."""
from __future__ import annotations

from pathlib import Path, PurePosixPath

from handoff_sources import relative_path


def normalized(value: str, root: Path) -> str:
    relative_path(root, value)
    path = PurePosixPath(value.replace("\\", "/")).as_posix()
    return path + "/" if (value.endswith(("/", "\\")) or path == ".") else path


def contains(outer: str, inner: str) -> bool:
    return (outer == "./" or outer == inner
            or (outer.endswith("/") and inner.startswith(outer)))


def intersection(left: str, right: str) -> str | None:
    if contains(left, right):
        return right
    if contains(right, left):
        return left
    return None


def classify(criterion: dict, scope: list[str], kind: str, root: Path) -> dict:
    unresolved = {"status": "unresolved", "targets": [], "excluded": []}
    try:
        scopes = []
        for value in scope:
            if value == "*":
                scopes.append("./")
                continue
            path = normalized(value, root)
            if path == "./":
                return unresolved
            scopes.append(path.rstrip("/") if relative_path(root, value).is_file()
                          else path.rstrip("/") + "/")
        scopes = sorted(set(scopes))
        if not scopes:
            return unresolved
        groups = []
        exceptions = []
        for field, destination in (("applies_when", groups), ("exceptions", exceptions)):
            values = criterion.get(field, [])
            if not isinstance(values, list):
                return unresolved
            for condition in values:
                if not isinstance(condition, dict) or condition.get("kind") not in {"path", "work_kind"}:
                    return unresolved
                alternatives = condition.get("any")
                if not isinstance(alternatives, list) or not alternatives or not all(
                    isinstance(value, str) and value.strip() for value in alternatives
                ):
                    return unresolved
                if condition["kind"] == "path":
                    alternatives = [normalized(v, root) for v in alternatives]
                destination.append((condition["kind"], alternatives))
        paths = [value for condition_kind, values in groups + exceptions
                 if condition_kind == "path" for value in values]
        for value in paths:
            path = relative_path(root, value)
            if value.endswith("/"):
                if path.is_file():
                    return unresolved
            elif path.is_dir() or any(other.startswith(value + "/") for other in scopes + paths):
                return unresolved
        notes = criterion.get("notes", [])
        if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
            return unresolved
    except (ValueError, TypeError, OSError):
        return unresolved
    targets = scopes[:]
    for condition_kind, alternatives in groups:
        if condition_kind == "work_kind":
            if kind not in alternatives:
                targets = []
        else:
            targets = sorted({common for target in targets for value in alternatives
                              if (common := intersection(target, value)) is not None})
    excluded = []
    for condition_kind, alternatives in exceptions:
        if condition_kind == "work_kind":
            if kind in alternatives:
                targets = []
        else:
            for value in alternatives:
                targets = [target for target in targets if not contains(value, target)]
                if any(contains(target, value) for target in targets):
                    excluded.append(value)
    if not targets:
        status = "not_applicable"
    elif not all(any(contains(target, value) for target in targets) for value in scopes) or excluded:
        status = "partial"
    elif notes:
        status = "needs_judgment"
    else:
        status = "applies"
    return {"status": status, "targets": targets, "excluded": sorted(set(excluded))}
