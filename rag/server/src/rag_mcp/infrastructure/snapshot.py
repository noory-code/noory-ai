"""Tarball-based export/import of a `.noory/rag/` index.

A snapshot bundles ``vec.db``, ``graph/``, ``manifest.json`` and ``settings.json``
together with a ``snapshot.json`` header that records the embedding model,
dimension, and plugin version. ``import_snapshot`` verifies the header and
refuses to apply when the model/dim disagrees with the destination settings.
"""

from __future__ import annotations

import json
import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..domain.models import FileDiff

SNAPSHOT_FORMAT_VERSION = 1
HEADER_NAME = "snapshot.json"


@dataclass(frozen=True)
class SnapshotHeader:
    format_version: int
    created_at: str
    embedding_model: str
    embedding_dim: int
    plugin_version: str
    stats: dict[str, int]

    def to_json(self) -> dict[str, Any]:
        return {
            "format_version": self.format_version,
            "created_at": self.created_at,
            "embedding": {"model": self.embedding_model, "dim": self.embedding_dim},
            "plugin_version": self.plugin_version,
            "stats": dict(self.stats),
        }


class IncompatibleSnapshot(Exception):
    pass


def export_snapshot(
    state_dir: Path,
    out_path: Path,
    *,
    embedding_model: str,
    embedding_dim: int,
    plugin_version: str,
    stats: dict[str, int] | None = None,
) -> SnapshotHeader:
    if not state_dir.exists():
        raise FileNotFoundError(f"state dir not found: {state_dir}")

    header = SnapshotHeader(
        format_version=SNAPSHOT_FORMAT_VERSION,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        embedding_model=embedding_model,
        embedding_dim=embedding_dim,
        plugin_version=plugin_version,
        stats=dict(stats or {}),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out_path, "w:gz") as tar:
        header_bytes = json.dumps(header.to_json(), indent=2).encode("utf-8")
        info = tarfile.TarInfo(name=HEADER_NAME)
        info.size = len(header_bytes)
        info.mtime = int(datetime.now(timezone.utc).timestamp())
        import io

        tar.addfile(info, io.BytesIO(header_bytes))
        for member in ("vec.db", "graph", "manifest.json", "settings.json"):
            src = state_dir / member
            if src.exists():
                tar.add(src, arcname=member)
    return header


def read_header(in_path: Path) -> SnapshotHeader:
    with tarfile.open(in_path, "r:gz") as tar:
        member = tar.getmember(HEADER_NAME)
        f = tar.extractfile(member)
        if f is None:
            raise IncompatibleSnapshot("snapshot.json unreadable")
        data = json.loads(f.read().decode("utf-8"))
    return SnapshotHeader(
        format_version=int(data.get("format_version", 0)),
        created_at=str(data.get("created_at", "")),
        embedding_model=str(data.get("embedding", {}).get("model", "")),
        embedding_dim=int(data.get("embedding", {}).get("dim", 0)),
        plugin_version=str(data.get("plugin_version", "")),
        stats=dict(data.get("stats", {})),
    )


def import_snapshot(
    in_path: Path,
    state_dir: Path,
    *,
    expected_model: str,
    expected_dim: int,
    plugin_major: str,
    mode: str = "replace",
) -> SnapshotHeader:
    if mode not in {"replace", "merge"}:
        raise ValueError(f"unsupported import mode: {mode}")

    header = read_header(in_path)
    if header.format_version != SNAPSHOT_FORMAT_VERSION:
        raise IncompatibleSnapshot(
            f"unsupported snapshot format_version={header.format_version}"
        )
    if header.embedding_model != expected_model:
        raise IncompatibleSnapshot(
            f"embedding.model mismatch: snapshot={header.embedding_model!r}, "
            f"expected={expected_model!r}"
        )
    if header.embedding_dim != expected_dim:
        raise IncompatibleSnapshot(
            f"embedding.dim mismatch: snapshot={header.embedding_dim}, "
            f"expected={expected_dim}"
        )
    snapshot_major = (header.plugin_version or "0").split(".")[0]
    if snapshot_major != plugin_major:
        raise IncompatibleSnapshot(
            f"plugin major mismatch: snapshot={snapshot_major}, expected={plugin_major}"
        )
    if mode == "merge":
        raise IncompatibleSnapshot("merge mode not yet supported in v0.1")

    backup: Path | None = None
    if state_dir.exists():
        backup = state_dir.with_suffix(
            state_dir.suffix + ".bak-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        )
        shutil.move(str(state_dir), str(backup))

    state_dir.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(in_path, "r:gz") as tar:
            members = [m for m in tar.getmembers() if m.name != HEADER_NAME]
            tar.extractall(path=state_dir, members=members, filter="data")
    except Exception:
        if backup is not None and backup.exists():
            if state_dir.exists():
                shutil.rmtree(state_dir)
            shutil.move(str(backup), str(state_dir))
        raise
    return header


def diff_after_restore(prior: dict[str, str], restored: dict[str, str]) -> FileDiff:
    """Convenience helper to report what changed after an import."""
    added = sorted(p for p in restored if p not in prior)
    removed = sorted(p for p in prior if p not in restored)
    changed = sorted(
        p for p in restored if p in prior and prior[p] != restored[p]
    )
    return FileDiff(added=tuple(added), changed=tuple(changed), removed=tuple(removed))
