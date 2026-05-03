"""Legacy-sketch migration: v0.1 single-file → v0.4 folder layout + v0.5 core schema.

Algorithm
---------

For every ``.plot/sketches/{id}.json`` that looks like a v0.1 SketchDoc:

    1. Normalise legacy node kinds (see ``_normalise_legacy_node_kinds``) then
       parse as ``_V01SketchDoc``.
    2. Create ``.plot/sketches/{id}/`` and the four v0.4 canvas files:
       - ``project.json``
       - ``core.json``  (project anchor + mission + core-value + identity)
       - ``actors.json`` (actor subtree, parent chain cleaned)
       - ``services/canvas.json`` (top-level services, no nesting)
       - ``services/{service_id}/detail.json`` per top-level service
    3. Rename the original to ``{id}.json.v01.bak``.

Running a second time does nothing (idempotent). Malformed v0.1 files are
left in place so the user can fix them by hand.

v0.5 Core schema upgrade (inline on open)
-----------------------------------------

``upgrade_core_canvas_if_needed`` handles Core canvases that were written
under earlier schemas (``core`` octagon anchor, ``identity_facet`` child
nodes). It rewrites the raw dict before Pydantic validation and, when
changes were made, persists the result so subsequent loads are cheap.
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
        # Legacy ``core`` root is normalised to ``project`` in _read_v01_sketch.
        cores = [n for n in self.nodes if n.kind == "project"]
        if len(cores) > 1:
            raise ValueError(
                f"at most one project node allowed per sketch; "
                f"found {sorted(n.id for n in cores)}"
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


def _normalise_legacy_node_kinds(nodes: list[dict[str, object]]) -> bool:
    """Rewrite node kinds that were removed in v0.5 to their canonical form.

    Returns True iff any node was rewritten — callers that persist canvases
    can use this to decide whether to re-save the file.

    Transformations:
      - ``kind="core"`` → ``kind="project"`` + ``shape="circle"``. The anchor
        also loses the stale ``icon="star"`` (the seeded default) since v0.5
        surfaces node identity via the top-left kind tag, not a star icon.
      - Any node whose ``parent_id`` pointed at a legacy ``core``-kind node
        is un-parented (``parent_id=None``). In v0.2 the octagon served as
        a container and mission/identity were nested inside; v0.5 treats
        them as peers around the small Project anchor, so leaving the old
        parent link would visually trap the children inside the anchor.
      - ``kind="identity_facet"`` → ``kind="identity"`` + ``parent_id=None``.
      - Any Mission / CoreValue / Identity node carrying the seeded
        ``icon="star"`` has the icon cleared (star retired from the palette).
    """
    changed = False
    legacy_core_ids: set[str] = set()
    for n in nodes:
        if isinstance(n, dict) and n.get("kind") == "core":
            node_id = n.get("id")
            if isinstance(node_id, str):
                legacy_core_ids.add(node_id)

    for n in nodes:
        if not isinstance(n, dict):
            continue
        kind = n.get("kind")
        if kind == "core":
            n["kind"] = "project"
            if n.get("shape") in (None, "", "octagon"):
                n["shape"] = "circle"
            changed = True
        elif kind == "identity_facet":
            n["kind"] = "identity"
            n["parent_id"] = None
            changed = True

        if n.get("parent_id") in legacy_core_ids:
            n["parent_id"] = None
            changed = True

        # Read the post-rewrite kind so facets migrated to ``identity`` also
        # lose their seeded star. ``project`` gets cleaned alongside the
        # three pillar kinds — no Core-canvas kind keeps a star in v0.5.
        current_kind = n.get("kind")
        if (
            current_kind in ("project", "mission", "core_value", "identity")
            and n.get("icon") == "star"
        ):
            n["icon"] = None
            changed = True

    return changed


def _read_v01_sketch(path: Path) -> _V01SketchDoc:
    """Read one v0.1 ``{id}.json`` file. Raises on missing / malformed."""
    if not path.exists():
        raise FileNotFoundError(f"sketch not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    # v0.1 files may carry kinds that were retired in v0.5 (``core`` anchor,
    # ``identity_facet`` children). Rewrite them up-front so Pydantic's
    # post-v0.5 ``NodeKind`` Literal accepts the document.
    _normalise_legacy_node_kinds(raw.get("nodes", []))
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
    # v0.8: no longer seed a ``services-detail/`` folder — detail canvases
    # live alongside their service under ``services/{sid}/detail.json``
    # and are created lazily by ``sync_details_with_overview``.

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
    # ``kind == "core"`` was normalised to ``"project"`` in _read_v01_sketch.
    core_root = next((n for n in doc.nodes if n.kind == "project"), None)
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
        if n.kind == "project":
            continue  # project anchor handled by _build_foundation_canvas
        if actor_root and _in_subtree(n, actor_root.id):
            actor_nodes.append(n)
        elif service_root and _in_subtree(n, service_root.id):
            service_nodes.append(n)
        elif n.kind == "actor":
            actor_nodes.append(n)
        elif n.kind in ("service", "rule", "content"):
            service_nodes.append(n)
        # identity-kind nodes would go to core but v0.1 didn't have them.

    # --- write foundation canvas ---------------------------------------
    foundation_canvas = _build_foundation_canvas(core_root, proj.name)
    _write_json(
        _canvas_file(plot_root, doc.id, "foundation"),
        foundation_canvas.model_dump(by_alias=True),
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
        _canvas_file(plot_root, doc.id, "services"),
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


def _build_foundation_canvas(core_root: SketchNode | None, project_name: str) -> CanvasDoc:
    """Promote v0.1 root text fields (mission / core_values / identity) into
    v0.5 top-level nodes on the Core canvas, and plant the v0.5 Project
    anchor in the centre. Empty fields get placeholder nodes so the
    ``_core_canvas_rules`` validator (≥ 1 mission, ≥ 1 identity, exactly
    1 project) stays happy.
    """
    nodes: list[SketchNode] = [
        SketchNode(
            id="project",
            kind="project",
            label=project_name,
            x=-75,
            y=-75,
            width=150,
            height=150,
            color="#fef3c7",
            shape="circle",
        ),
    ]

    # v0.9.1 dropped typed fields — legacy ``mission`` text on core-root
    # has nowhere structured to land. The user can paste it into the new
    # node's ``details.md`` after migration if they care; we don't auto-
    # synthesise an MD file here to keep migration side-effect-free.
    nodes.append(
        SketchNode(
            id="mission",
            kind="mission",
            label="Mission",
            x=-360,
            y=-45,
            width=200,
            height=90,
            color="#fef3c7",
            shape="rounded",
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
                x=-90,
                y=-260 + i * 96,
                width=180,
                height=80,
                color="#fde68a",
                shape="rounded",
                )
        )

    # Same: legacy ``identity`` text is dropped. User can paste it into
    # the new node's ``details.md`` after migration.
    nodes.append(
        SketchNode(
            id="identity",
            kind="identity",
            label="Voice",
            x=160,
            y=-45,
            width=200,
            height=90,
            color="#fed7aa",
            shape="rounded",
        )
    )

    return CanvasDoc(canvas_id="foundation", canvas_kind="foundation", nodes=nodes)


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
    # v0.11 — actors canvas requires ≥ 2 actor classes. Pad with placeholders
    # if a legacy v0.1 sketch had fewer; the user can rename them. Also
    # backfill ``side`` on legacy actors that have it unset (default = "user"
    # since the typical legacy pattern was "one user-side actor").
    cleaned = _backfill_actor_sides(cleaned)
    cleaned = _ensure_minimum_actors(cleaned)
    return CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=cleaned,
        edges=scoped_edges,
    )


def _detail_actor_ref_seeds(service_id: str) -> list[SketchNode]:
    """v0.11 — auto-seed two stub actor_refs (operator + user) when a
    migrated service_detail otherwise has zero. Mirrors
    ``folder_io.sync_details_with_overview``'s seeding so behaviour is
    consistent whether the canvas was created via migration or via auto
    sync.
    """
    return [
        SketchNode(
            id=f"{service_id}-operator-ref",
            kind="actor_ref",
            label="→ Operator",
            ref_actor_id="operator",
            side="operator",
            color="#bae6fd",
            shape="ellipse",
            width=140,
            height=70,
        ),
        SketchNode(
            id=f"{service_id}-user-ref",
            kind="actor_ref",
            label="→ User",
            ref_actor_id="user",
            side="user",
            color="#fecaca",
            shape="ellipse",
            width=140,
            height=70,
        ),
    ]


def _backfill_actor_sides(nodes: list[SketchNode]) -> list[SketchNode]:
    """v0.11 migration helper: legacy actor nodes have ``side = None``.
    Default them to ``"user"`` so the model is self-consistent. Users can
    flip individual actors to ``"operator"`` via the Inspector after open.
    """
    out: list[SketchNode] = []
    for n in nodes:
        if n.kind == "actor" and n.side is None:
            out.append(n.model_copy(update={"side": "user"}))
        else:
            out.append(n)
    return out


def _ensure_minimum_actors(nodes: list[SketchNode]) -> list[SketchNode]:
    """v0.11 migration helper: pad an under-populated actors canvas with
    placeholder classes so the new ≥ 2 validator doesn't reject open.
    Idempotent — adds only what's missing.
    """
    actors = [n for n in nodes if n.kind == "actor"]
    has_operator = any(n.side == "operator" for n in actors)
    has_user = any(n.side == "user" for n in actors)
    pad: list[SketchNode] = []
    used_ids = {n.id for n in nodes}
    if not has_operator:
        oid = "operator" if "operator" not in used_ids else "operator-seed"
        pad.append(
            SketchNode(
                id=oid,
                kind="actor",
                label="Operator",
                side="operator",
                x=-160,
                y=-50,
                width=140,
                height=80,
                color="#bae6fd",
                shape="rounded",
            )
        )
    if not has_user and len(actors) + len(pad) < 2:
        uid = "user" if "user" not in used_ids else "user-seed"
        pad.append(
            SketchNode(
                id=uid,
                kind="actor",
                label="User",
                side="user",
                x=40,
                y=-50,
                width=140,
                height=80,
                color="#fecaca",
                shape="rounded",
            )
        )
    return nodes + pad


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

    # v0.12 — services canvas now requires services to be nested inside a
    # category. Wrap all v0.1-migrated top-level services under a single
    # default category so the migrated canvas validates. Users can split
    # into more thematic categories afterwards.
    overview_nodes: list[SketchNode] = []
    if top_level:
        overview_nodes.append(
            SketchNode(
                id="default-category",
                kind="category",
                label="Services",
                theme="Migrated services",
                x=-200,
                y=-50,
                width=200,
                height=100,
                color="#e2e8f0",
                shape="rounded",
            )
        )
    overview_nodes.extend(
        n.model_copy(
            update={
                "parent_id": "default-category",
                "is_root": False,
                "mission": "",
                "core_values": "",
                "identity": "",
            }
        )
        for n in top_level
    )
    overview_ids = {n.id for n in overview_nodes}
    overview_edges = [e for e in edges if e.source in overview_ids and e.target in overview_ids]
    overview = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
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
        # v0.11 — pad with operator + user actor_refs so the new
        # ≥ 2 actor_ref validator accepts migrated detail canvases.
        descendants = descendants + _detail_actor_ref_seeds(root_service.id)
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


# ---------------------------------------------------------------------------
# Foundation-canvas schema upgrade (called from folder_io.read_canvas)
# ---------------------------------------------------------------------------


def upgrade_foundation_canvas_if_needed(plot_root: Path, project_id: str) -> bool:
    """Heal a Foundation canvas written under any pre-v0.10 schema.

    Rewrites the raw ``foundation/canvas.json`` on disk so subsequent
    reads are cheap and Pydantic parsing never trips on retired kinds.
    Returns True iff the file was rewritten. Safe to call on every load
    (idempotent).

    Operations (applied in order):
      0. v0.10 layout: rename ``core/`` folder → ``foundation/`` if the
         old name exists and the new one doesn't.
      1. ``canvas_kind="core"`` → ``canvas_kind="foundation"``.
      2. ``kind="core"`` (legacy octagon) → ``kind="project"``,
         ``shape="circle"``.
      3. ``kind="identity_facet"`` → ``kind="identity"``,
         ``parent_id=None``.
      4. If no Project anchor exists, synthesise one at centre using the
         project's ``ProjectDoc.name`` as label.
    """
    project_dir = plot_root / project_id
    legacy_dir = project_dir / "core"
    new_dir = project_dir / "foundation"

    # 0. Rename ``core/`` → ``foundation/`` if needed.
    if legacy_dir.is_dir() and not new_dir.exists():
        legacy_dir.rename(new_dir)

    path = _canvas_file(plot_root, project_id, "foundation")
    if not path.exists():
        return False
    raw = json.loads(path.read_text(encoding="utf-8"))

    changed = False

    # 1. Bump canvas_kind if a stale ``core`` value made it onto disk.
    if raw.get("canvas_kind") == "core":
        raw["canvas_kind"] = "foundation"
        if raw.get("canvas_id") == "core":
            raw["canvas_id"] = "foundation"
        changed = True

    nodes = raw.get("nodes")
    if not isinstance(nodes, list):
        return changed

    # 2-3. Legacy node-kind rewrites.
    if _normalise_legacy_node_kinds(nodes):
        changed = True

    # 4. Project anchor synthesis.
    has_project = any(isinstance(n, dict) and n.get("kind") == "project" for n in nodes)
    if not has_project:
        project_name = _read_project_name(plot_root, project_id)
        taken_ids = {n.get("id") for n in nodes if isinstance(n, dict)}
        nodes.insert(0, _project_anchor_dict(project_name, taken_ids))
        raw["nodes"] = nodes
        changed = True

    if changed:
        _write_json(path, raw)
    return changed


# Backwards-compatible alias for any in-process caller still importing the
# pre-v0.10 name. New code uses ``upgrade_foundation_canvas_if_needed``.
upgrade_core_canvas_if_needed = upgrade_foundation_canvas_if_needed


def _read_project_name(plot_root: Path, project_id: str) -> str:
    """Best-effort read of ``project.json``'s ``name``; falls back to id."""
    proj_path = _project_file(plot_root, project_id)
    try:
        raw = json.loads(proj_path.read_text(encoding="utf-8"))
        name = raw.get("name")
        if isinstance(name, str) and name.strip():
            return name
    except (OSError, json.JSONDecodeError):
        pass
    return project_id


def _project_anchor_dict(project_name: str, taken_ids: set[str | None]) -> dict[str, object]:
    anchor_id = "project"
    suffix = 1
    while anchor_id in taken_ids:
        suffix += 1
        anchor_id = f"project-{suffix}"
    return SketchNode(
        id=anchor_id,
        kind="project",
        label=project_name,
        x=-75,
        y=-75,
        width=150,
        height=150,
        color="#fef3c7",
        shape="circle",
        icon="compass",
    ).model_dump()
