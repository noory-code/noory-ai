"""JSON-backed file-hash manifest implementing :class:`ManifestPort`."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..domain.models import FileDiff


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def diff_maps(current: dict[str, str], previous: dict[str, str]) -> FileDiff:
    added = sorted(p for p in current if p not in previous)
    changed = sorted(
        p for p, h in current.items() if p in previous and previous[p] != h
    )
    removed = sorted(p for p in previous if p not in current)
    return FileDiff(added=tuple(added), changed=tuple(changed), removed=tuple(removed))


class JsonManifest:
    """Manifest adapter persisting hashes to a single JSON file.

    A corrupt manifest degrades gracefully to "no known hashes" (so a full
    reindex follows), but the degradation is surfaced: ``corrupt_detected``
    is set by the offending ``load`` and callers (the tool layer) attach a
    warning to their response instead of pretending the manifest was empty.
    """

    def __init__(self, file: Path):
        self.file = file
        self.corrupt_detected = False

    def load(self) -> dict[str, str]:
        self.corrupt_detected = False
        if not self.file.exists():
            return {}
        try:
            data = json.loads(self.file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.corrupt_detected = True
            return {}
        if not isinstance(data, dict):
            self.corrupt_detected = True
            return {}
        hashes = data.get("hashes", {})
        if not isinstance(hashes, dict):
            self.corrupt_detected = True
            return {}
        return {str(k): str(v) for k, v in hashes.items()}

    def save(self, hashes: dict[str, str]) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(
            json.dumps({"hashes": dict(sorted(hashes.items()))}, indent=2) + "\n",
            encoding="utf-8",
        )

    def diff(self, current: dict[str, str]) -> FileDiff:
        return diff_maps(current, self.load())
