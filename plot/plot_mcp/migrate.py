"""v0.1 → v0.2 migration: single-file ``{id}.json`` → folder layout.

Algorithm
---------

For every ``.plot/sketches/{id}.json`` that looks like a v0.1 SketchDoc:

    1. Parse as ``SketchDoc``.
    2. Create ``.plot/sketches/{id}/`` and the four v0.2 canvas files:
       - ``project.json``
       - ``core.json``  (core + mission + identity, promoted from fields)
       - ``actors.json`` (actor subtree, parent chain cleaned)
       - ``services-overview.json`` (top-level services, no nesting)
       - ``services-detail/{service_id}.json`` per top-level service
    3. Rename the original to ``{id}.json.v01.bak``.

Running a second time does nothing (idempotent). Malformed v0.1 files are
left in place so the user can fix them by hand.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

from plot_mcp.folder_io import _canvas_file, _project_dir, _project_file, _write_json
from plot_mcp.models import (
    CanvasDoc,
    ProjectDoc,
    SketchEdge,
    SketchNode,
)

# ---------------------------------------------------------------------------
# v0.1 spec — private to the migration script
# ---------------------------------------------------------------------------
#
# v0.1 stored everything as one ``{id}.json`` under ``sketches/``. v0.4
# dropped that format but migration still needs to *read* it, so the
# Pydantic model lives here rather than polluting ``plot_mcp/models.py``.
# Identical shape + validators to the former ``SketchDoc``; kept strict so
# a corrupt file fails up-front instead of producing a half-migrated
# folder.


_V01_COMPOSITION_KINDS = {"rule", "content"}


class _V01SketchDoc(BaseModel):
    """Legacy v0.1 single-file sketch document. Migration-only.

    Loaded from ``.plot/sketches/{id}.json`` (the pre-v0.4 layout) and
    broken apart into the v0.4 folder-per-project + canvas files.
    """

    id: str = Field(..., min_length=1)
    name: str = ""
    created: str = ""  # ISO date (YYYY-MM-DD)
    updated: str = ""  # ISO datetime
    version: int = 1
    nodes: list[SketchNode] = Field(default_factory=list)
    edges: list[SketchEdge] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _kebab_id(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"sketch id must be alphanumeric with -/_ only, got {v!r}")
        return v

    @model_validator(mode="after")
    def _edges_reference_nodes(self) -> _V01SketchDoc:
        node_ids = {n.id for n in self.nodes}
        dangling = [e for e in self.edges if e.source not in node_ids or e.target not in node_ids]
        if dangling:
            missing = sorted({e.id for e in dangling})
            raise ValueError(f"edges reference unknown nodes: {missing}")
        if len({e.id for e in self.edges}) != len(self.edges):
            raise ValueError("edge ids must be unique")
        if len({n.id for n in self.nodes}) != len(self.nodes):
            raise ValueError("node ids must be unique")
        return self

    @model_validator(mode="after")
    def _parent_ids_are_valid(self) -> _V01SketchDoc:
        by_id = {n.id: n for n in self.nodes}
        for n in self.nodes:
            if n.parent_id is None:
                continue
            if n.parent_id == n.id:
                raise ValueError(f"node {n.id!r} cannot be its own parent")
            if n.parent_id not in by_id:
                raise ValueError(f"node {n.id!r}.parent_id points to unknown node {n.parent_id!r}")
        for start in self.nodes:
            seen: set[str] = set()
            current: str | None = start.id
            while current is not None:
                if current in seen:
                    raise ValueError(f"parent chain contains a cycle at node {current!r}")
                seen.add(current)
                parent = by_id[current]
                current = parent.parent_id
        return self

    @model_validator(mode="after")
    def _at_most_one_root_per_kind(self) -> _V01SketchDoc:
        cores = [n for n in self.nodes if n.kind == "core"]
        if len(cores) > 1:
            raise ValueError(
                f"at most one core node allowed per sketch; found {sorted(n.id for n in cores)}"
            )
        roots = [n for n in self.nodes if n.is_root]
        by_kind: dict[str, list[str]] = {}
        for r in roots:
            if r.kind not in ("actor", "service"):
                raise ValueError(
                    f"node {r.id!r} is_root=True but kind is {r.kind!r} "
                    "(only actor or service may be is_root)"
                )
            by_kind.setdefault(r.kind, []).append(r.id)
        for kind, ids in by_kind.items():
            if len(ids) > 1:
                raise ValueError(f"at most one {kind}-root allowed per sketch; found {sorted(ids)}")
        return self

    @model_validator(mode="after")
    def _composition_kinds_live_in_service(self) -> _V01SketchDoc:
        by_id = {n.id: n for n in self.nodes}
        for n in self.nodes:
            if n.kind not in _V01_COMPOSITION_KINDS:
                continue
            if n.parent_id is None:
                raise ValueError(
                    f"node {n.id!r} of kind {n.kind!r} requires a parent_id "
                    "(must live inside a service)"
                )
            parent = by_id.get(n.parent_id)
            if parent is not None and parent.kind != "service":
                raise ValueError(
                    f"node {n.id!r} of kind {n.kind!r} must be a child of a service, "
                    f"but parent {n.parent_id!r} has kind {parent.kind!r}"
                )
        return self


def _read_v01_sketch(path: Path) -> _V01SketchDoc:
    """Read one v0.1 ``{id}.json`` file. Raises on missing / malformed."""
    if not path.exists():
        raise FileNotFoundError(f"sketch not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _V01SketchDoc.model_validate(raw)


def migrate_v01_to_v02(plot_root: Path) -> list[str]:
    """Migrate every v0.1 ``{id}.json`` under ``sketches/`` to the v0.2 folder layout.

    Returns the list of project ids that were migrated (may be empty).
    Files that don't parse as v0.1 are skipped and stay in place.
    """
    sketches_dir = plot_root / "sketches"
    if not sketches_dir.is_dir():
        return []
    migrated: list[str] = []
    for path in sorted(sketches_dir.glob("*.json")):
        # Skip files that were already renamed to .v01.bak.
        if path.name.endswith(".v01.bak"):
            continue
        try:
            doc = _read_v01_sketch(path)
        except (ValueError, json.JSONDecodeError):
            continue
        folder = _project_dir(plot_root, doc.id)
        if folder.exists():
            # Already migrated — back up the leftover file and move on.
            _backup(path)
            continue
        _migrate_one(plot_root, doc)
        _backup(path)
        migrated.append(doc.id)
    return migrated


def _backup(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".v01.bak")
    path.replace(backup)


def _migrate_one(plot_root: Path, doc: _V01SketchDoc) -> None:
    folder = _project_dir(plot_root, doc.id)
    folder.mkdir(parents=True)
    (folder / "services-detail").mkdir()

    # --- project metadata -----------------------------------------------
    proj = ProjectDoc(
        id=doc.id,
        name=doc.name or doc.id,
        created=doc.created or date.today().isoformat(),
        updated=datetime.now(UTC).isoformat(),
        version=2,
    )
    _write_json(_project_file(plot_root, doc.id), proj.model_dump())

    # --- classify nodes -------------------------------------------------
    by_id = {n.id: n for n in doc.nodes}
    core_root = next((n for n in doc.nodes if n.kind == "core"), None)
    actor_root = next((n for n in doc.nodes if n.kind == "actor" and n.is_root), None)
    service_root = next((n for n in doc.nodes if n.kind == "service" and n.is_root), None)

    def _in_subtree(node: SketchNode, root_id: str) -> bool:
        cur: SketchNode | None = node
        while cur is not None:
            if cur.id == root_id:
                return True
            cur = by_id.get(cur.parent_id) if cur.parent_id else None
        return False

    actor_nodes: list[SketchNode] = []
    service_nodes: list[SketchNode] = []
    for n in doc.nodes:
        if n.kind == "core":
            continue  # core root already handled
        if actor_root and _in_subtree(n, actor_root.id):
            actor_nodes.append(n)
        elif service_root and _in_subtree(n, service_root.id):
            service_nodes.append(n)
        elif n.kind == "actor":
            actor_nodes.append(n)
        elif n.kind in ("service", "rule", "content"):
            service_nodes.append(n)
        # identity-kind nodes would go to core but v0.1 didn't have them.

    # --- write core canvas ----------------------------------------------
    core_canvas = _build_core_canvas(core_root)
    _write_json(
        _canvas_file(plot_root, doc.id, "core"),
        core_canvas.model_dump(by_alias=True),
    )

    # --- write actors canvas --------------------------------------------
    actors_canvas = _build_actors_canvas(actor_nodes, actor_root, doc.edges)
    _write_json(
        _canvas_file(plot_root, doc.id, "actors"),
        actors_canvas.model_dump(by_alias=True),
    )

    # --- split services into overview + details -------------------------
    overview, detail_canvases = _split_services(service_nodes, service_root, doc.edges)
    _write_json(
        _canvas_file(plot_root, doc.id, "services_overview"),
        overview.model_dump(by_alias=True),
    )
    for detail in detail_canvases:
        _write_json(
            _canvas_file(plot_root, doc.id, "service_detail", service_id=detail.canvas_id),
            detail.model_dump(by_alias=True),
        )


# ---------------------------------------------------------------------------
# per-canvas builders
# ---------------------------------------------------------------------------


def _build_core_canvas(core_root: SketchNode | None) -> CanvasDoc:
    """Promote Mission / Core Values / Identity text fields on the v0.1
    core-root into top-level nodes on the v0.4 Core canvas. The old
    ``core``-kind octagon anchor is dropped — its only job in v0.2 was
    to tie the single-canvas world together, and v0.4 canvases are
    already separate. Synthesises empty Mission + Identity when missing
    so the CanvasDoc validator (exactly 1 of each) stays happy.
    """
    nodes: list[SketchNode] = []

    mission_text = (core_root.mission if core_root else "").strip()
    nodes.append(
        SketchNode(
            id="mission",
            kind="mission",
            label="Mission",
            body=mission_text,
            x=-260,
            y=-60,
            width=200,
            height=90,
            color="#fef3c7",
            shape="rounded",
            icon="star",
        )
    )

    # Core values split on newlines so each becomes its own node. If the
    # old field was empty, seed one placeholder so the pillar is visible.
    cv_raw = (core_root.core_values if core_root else "").strip()
    if cv_raw:
        lines = [line.strip() for line in cv_raw.splitlines() if line.strip()]
    else:
        lines = ["Core value"]
    for i, line in enumerate(lines):
        nodes.append(
            SketchNode(
                id=f"core-value-{i + 1}",
                kind="core_value",
                label=line,
                x=0,
                y=-60 + i * 96,
                width=180,
                height=80,
                color="#fde68a",
                shape="rounded",
                icon="star",
            )
        )

    identity_text = (core_root.identity if core_root else "").strip()
    nodes.append(
        SketchNode(
            id="identity",
            kind="identity",
            label="Identity",
            body=identity_text,
            x=220,
            y=-60,
            width=200,
            height=90,
            color="#fed7aa",
            shape="rounded",
            icon="star",
        )
    )

    return CanvasDoc(canvas_id="core", canvas_kind="core", nodes=nodes)


def _build_actors_canvas(
    actor_nodes: list[SketchNode],
    actor_root: SketchNode | None,
    edges: list[SketchEdge],
) -> CanvasDoc:
    """Actor subtree. If actor-root was the only content, keep it as a
    top-level actor; sub-actors keep their parent_id relative to it.
    Edges reaching outside the subtree are dropped.
    """
    node_ids = {n.id for n in actor_nodes}
    cleaned: list[SketchNode] = []
    for n in actor_nodes:
        # If the parent is core-root (or anything outside the actors canvas),
        # drop parent_id so it becomes top-level here.
        parent_id = n.parent_id if n.parent_id in node_ids else None
        cleaned.append(
            n.model_copy(
                update={
                    "parent_id": parent_id,
                    "is_root": False,  # is_root meaningless across canvases
                    "mission": "",
                    "core_values": "",
                    "identity": "",
                }
            )
        )
    cleaned_ids = {n.id for n in cleaned}
    scoped_edges = [e for e in edges if e.source in cleaned_ids and e.target in cleaned_ids]
    return CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=cleaned,
        edges=scoped_edges,
    )


def _split_services(
    service_nodes: list[SketchNode],
    service_root: SketchNode | None,
    edges: list[SketchEdge],
) -> tuple[CanvasDoc, list[CanvasDoc]]:
    """Top-level services become Overview nodes (no nesting); each
    top-level service + its descendants becomes a Detail canvas.
    ``service-root`` itself is dropped — it was a layout anchor only.
    """
    by_id = {n.id: n for n in service_nodes}
    service_root_id = service_root.id if service_root else None

    # Top-level = direct children of service-root, OR a service that has no
    # parent at all in the input set.
    top_level: list[SketchNode] = []
    for n in service_nodes:
        if n.kind != "service":
            continue
        if n.id == service_root_id:
            continue  # drop the anchor
        parent = n.parent_id
        if parent is None or parent == service_root_id:
            top_level.append(n)

    # Overview: top-level services, parent_id cleared, no composition.
    overview_nodes = [
        n.model_copy(
            update={
                "parent_id": None,
                "is_root": False,
                "mission": "",
                "core_values": "",
                "identity": "",
            }
        )
        for n in top_level
    ]
    overview_ids = {n.id for n in overview_nodes}
    overview_edges = [e for e in edges if e.source in overview_ids and e.target in overview_ids]
    overview = CanvasDoc(
        canvas_id="services_overview",
        canvas_kind="services_overview",
        nodes=overview_nodes,
        edges=overview_edges,
    )

    # Detail per top-level service.
    details: list[CanvasDoc] = []
    for root_service in top_level:
        descendant_ids: set[str] = set()
        stack = [root_service.id]
        while stack:
            cur = stack.pop()
            descendant_ids.add(cur)
            for child in service_nodes:
                if child.parent_id == cur and child.id not in descendant_ids:
                    stack.append(child.id)
        descendants = [
            n.model_copy(
                update={
                    "is_root": False,
                    "mission": "",
                    "core_values": "",
                    "identity": "",
                    # root_service itself has parent cleared; composition
                    # kinds keep their intra-subtree parent_id.
                    "parent_id": None if n.id == root_service.id else n.parent_id,
                }
            )
            for n in (by_id[i] for i in descendant_ids)
        ]
        ids = {n.id for n in descendants}
        scoped_edges = [e for e in edges if e.source in ids and e.target in ids]
        details.append(
            CanvasDoc(
                canvas_id=root_service.id,
                canvas_kind="service_detail",
                service_ref=root_service.id,
                nodes=descendants,
                edges=scoped_edges,
            )
        )

    return overview, details
