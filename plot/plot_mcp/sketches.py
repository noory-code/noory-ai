"""JSON-backed sketch store.

Thin wrapper over ``.plot/sketches/{id}.json``. No caching, no indexing —
every call reads the filesystem. Sketch counts in a workspace are expected
to be small (< 100) and each file is a few KB, so disk is not a bottleneck.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from plot_mcp.models import SketchDoc, SketchSummary


def _sketches_dir(plot_root: Path) -> Path:
    d = plot_root / "sketches"
    d.mkdir(exist_ok=True)
    return d


def _sketch_path(plot_root: Path, sketch_id: str) -> Path:
    return _sketches_dir(plot_root) / f"{sketch_id}.json"


def list_sketches(plot_root: Path) -> list[SketchSummary]:
    """Return a summary of every sketch file. Sorted by ``updated`` desc."""
    out: list[SketchSummary] = []
    for path in sorted(_sketches_dir(plot_root).glob("*.json")):
        try:
            doc = read_sketch(plot_root, path.stem)
        except (ValueError, json.JSONDecodeError):
            continue  # skip malformed files rather than 500 the list
        out.append(
            SketchSummary(
                id=doc.id,
                name=doc.name,
                updated=doc.updated,
                node_count=len(doc.nodes),
                edge_count=len(doc.edges),
            )
        )
    out.sort(key=lambda s: s.updated, reverse=True)
    return out


def read_sketch(plot_root: Path, sketch_id: str) -> SketchDoc:
    path = _sketch_path(plot_root, sketch_id)
    if not path.exists():
        raise FileNotFoundError(f"sketch not found: {sketch_id}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return SketchDoc.model_validate(raw)


def write_sketch(plot_root: Path, doc: SketchDoc) -> None:
    """Write the sketch, refreshing ``updated`` to now."""
    doc_out = doc.model_copy(update={"updated": datetime.now(UTC).isoformat()})
    path = _sketch_path(plot_root, doc_out.id)
    # Atomic replace so concurrent readers don't see a partial write.
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(doc_out.model_dump(by_alias=True), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)


def create_sketch(plot_root: Path, sketch_id: str, name: str) -> SketchDoc:
    """Create a new sketch, seeded with a Core root + Actor root + Service root.

    Raises ``FileExistsError`` if ``sketch_id`` is taken.
    """
    from plot_mcp.models import SketchNode  # local import avoids cycles

    path = _sketch_path(plot_root, sketch_id)
    if path.exists():
        raise FileExistsError(f"sketch already exists: {sketch_id}")
    today = date.today().isoformat()
    # Three root nodes: Core at origin, Actor root left, Service root right.
    seeds = [
        SketchNode(
            id="core-root",
            kind="core",
            label=name or sketch_id,
            x=-80,
            y=-60,
            width=160,
            height=120,
            color="#fde68a",
            shape="diamond",
            icon="star",
        ),
        SketchNode(
            id="actor-root",
            kind="actor",
            label="Actors",
            is_root=True,
            x=-320,
            y=180,
            width=140,
            height=140,
            color="#fecaca",
            shape="circle",
            icon="users",
            parent_id="core-root",
        ),
        SketchNode(
            id="service-root",
            kind="service",
            label="Services",
            is_root=True,
            x=180,
            y=180,
            width=200,
            height=120,
            color="#bae6fd",
            shape="rounded",
            icon="zap",
            parent_id="core-root",
        ),
    ]
    doc = SketchDoc(
        id=sketch_id,
        name=name or sketch_id,
        created=today,
        updated=datetime.now(UTC).isoformat(),
        nodes=seeds,
    )
    write_sketch(plot_root, doc)
    return doc


def delete_sketch(plot_root: Path, sketch_id: str) -> None:
    path = _sketch_path(plot_root, sketch_id)
    if not path.exists():
        raise FileNotFoundError(f"sketch not found: {sketch_id}")
    path.unlink()
