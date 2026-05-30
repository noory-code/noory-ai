"""Folder-based project store for Plot v0.10 (wrapper-less, canvas-grouped).

Disk layout
-----------

    .plot/{project_id}/
        project.json                     — ProjectDoc
        foundation/
            canvas.json                  — CanvasDoc (canvas_kind = "foundation")
            {node-slug}/details.md       — node long-form (opt-in per node)
        actors/
            canvas.json
            {node-slug}/details.md
        services/
            canvas.json                  — top-view (canvas_kind = "services")
            {service_id}/
                details.md               — Service node long-form
                detail.json              — CanvasDoc (canvas_kind = "service_detail")

Every canvas lives in its own file (``canvas.json`` for singletons,
``detail.json`` for service detail) so a write to one canvas never
touches another. Thin wrapper: no caching, atomic replace only.

v0.10 renamed the ``core/`` folder to ``foundation/`` to match the
underlying concept (Foundation = the project's identity). Pre-v0.10
disk layouts are healed lazily on read — see
``migrate.upgrade_foundation_canvas_if_needed``.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from plot_mcp.edge_semantics import classify_edge
from plot_mcp.git_store import (
    ensure_clean_working_tree,
    ensure_repo,
    find_latest_publish_commit,
    publish_snapshot,
    revert_publish,
)
from plot_mcp.md_publish import (
    bump_major,
    bump_minor,
    can_publish,
    published_md_path,
    render_node_md,
)
from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    CanvasKind,
    CoreValueNode,
    IdentityNode,
    MissionNode,
    ProjectDoc,
    SketchEdge,
    SketchNode,
)
from plot_mcp.propagation import walk_ancestors

# v0.8 layout: every canvas — singleton or detail — lives in a folder
# named after the canvas (or the owning service, for details), and its
# structure is always called ``canvas.json`` (or ``detail.json`` for
# service_detail). No more per-canvas filename convention to memorise.


# ---------------------------------------------------------------------------
# path helpers
# ---------------------------------------------------------------------------


def _project_dir(plot_root: Path, project_id: str) -> Path:
    return plot_root / project_id


def _project_file(plot_root: Path, project_id: str) -> Path:
    return _project_dir(plot_root, project_id) / "project.json"


def _canvas_file(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None = None,
) -> Path:
    folder = _project_dir(plot_root, project_id)
    if canvas_kind == "service_detail":
        if not service_id:
            raise ValueError("service_detail requires service_id")
        return folder / "services" / service_id / "detail.json"
    return folder / canvas_kind / "canvas.json"


def _ensure_project(plot_root: Path, project_id: str) -> Path:
    folder = _project_dir(plot_root, project_id)
    if not folder.is_dir():
        raise FileNotFoundError(f"project not found: {project_id}")
    return folder


# ---------------------------------------------------------------------------
# atomic JSON helpers
# ---------------------------------------------------------------------------


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomic write — tmp file then rename, so readers never see half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# project-level IO
# ---------------------------------------------------------------------------


def read_project(plot_root: Path, project_id: str) -> ProjectDoc:
    _ensure_project(plot_root, project_id)
    raw = _read_json(_project_file(plot_root, project_id))
    return ProjectDoc.model_validate(raw)


def write_project(plot_root: Path, project: ProjectDoc) -> None:
    """Persist metadata, refreshing ``updated`` to now."""
    _ensure_project(plot_root, project.id)
    refreshed = project.model_copy(update={"updated": datetime.now(UTC).isoformat()})
    _write_json(
        _project_file(plot_root, project.id),
        refreshed.model_dump(),
    )


# ---------------------------------------------------------------------------
# canvas-level IO
# ---------------------------------------------------------------------------


def read_canvas(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None = None,
) -> CanvasDoc:
    _ensure_project(plot_root, project_id)
    if canvas_kind == "foundation":
        # Heal Foundation canvases written under pre-v0.10 schemas (legacy
        # ``core`` canvas folder + ``core``/``identity_facet`` node kinds +
        # missing Project anchor) before Pydantic sees the raw dict.
        # Imported here to keep migrate.py optional on the hot path for
        # non-foundation kinds.
        from plot_mcp.migrate import upgrade_foundation_canvas_if_needed

        upgrade_foundation_canvas_if_needed(plot_root, project_id)
    path = _canvas_file(plot_root, project_id, canvas_kind, service_id)
    raw = _read_json(path)
    # v0.13 Phase 0 — project anchor moved to ``ProjectDoc.anchors``. If an
    # old canvas still carries a ``project`` kind node, evict it: copy its
    # position/visual to ProjectDoc.anchors[canvas] and remove from nodes.
    if canvas_kind in ("foundation", "actors", "services"):
        raw = _evict_legacy_project_anchor(plot_root, project_id, canvas_kind, raw)
    # v0.24.11 (D-2026-05-19-D) — actor.is_root semantic deprecated; reset
    # any pre-v0.24.11 ``is_root=true`` on actor nodes to False on first
    # read. Service.is_root is preserved (still meaningful as the
    # ServiceDetail anchor marker). See [[project_plot_symbol_concept]].
    if canvas_kind == "actors":
        raw = _migrate_actor_isroot_to_false(raw)
    # v0.17 Phase 1 (D-2026-05-16-A) — JSON is the single SSOT for
    # Foundation typed-text fields. On first read of any pre-v0.17
    # project, absorb the typed H2 sections + post-``---`` body from
    # ``foundation/{kind}-{slug}.md`` into the JSON node, clear
    # ``details_path``, and quarantine the source MD file to
    # ``foundation/_legacy/``. Subsequent reads are no-ops (the
    # original path no longer exists).
    if canvas_kind == "foundation":
        raw = _absorb_md_typed_text_into_json(plot_root, project_id, raw)
    # v0.11.5 — services canvas no longer accepts Foundation refs (they
    # moved to service_detail). Drop any stale ones from older projects so
    # the canvas validates on open. Same idempotent pattern.
    if canvas_kind == "services":
        raw = _drop_disallowed_services_kinds(plot_root, project_id, raw)
    # v0.26.0 (D-2026-05-25-A) — convert pre-v0.26 ``parent_id`` field
    # to a directed edge from parent → child. Idempotent. Persists
    # back to disk on first read so the file format settles into the
    # new model without needing a write-side trigger.
    raw = _migrate_parent_id_to_directed_edges(plot_root, project_id, canvas_kind, service_id, raw)
    # v0.30.0 (D-2026-05-31-C) — assign the stored ``relation`` semantic
    # to any pre-v0.30 edge that lacks it, via classify_edge(canvas,
    # source-node kind). Idempotent; persists on first read.
    raw = _migrate_assign_edge_relation(plot_root, project_id, canvas_kind, service_id, raw)
    # v0.23.0 (D-2026-05-17-I) — migrate legacy flat published MD layout
    # (<canvas>/published/<kind>-<slug>-v<X>.md) to the kind/slug/version.md
    # hierarchy. Idempotent.
    canvas_dir = _canvas_file(plot_root, project_id, canvas_kind, service_id).parent
    _migrate_published_flat_to_kind_slug(canvas_dir)
    # v0.24.3 (D-2026-05-18-A) — migrate slug-folder layout to id-folder.
    # Reads node id↔label from the raw canvas so we can compute the
    # old slug folder name and rename it to the node id.
    _migrate_published_slug_to_id(canvas_dir, raw)
    return CanvasDoc.model_validate(raw)


# v0.23.0 (D-2026-05-17-I) — published MD layout migration.
# Pre-v0.23.0 layout was flat: ``<canvas>/published/<kind>-<slug>-vN.M.md``.
# v0.23.0+ layout groups by kind + slug: ``<canvas>/published/<kind>/<slug>/vN.M.md``.
# Same data, better navigation: all versions of a logical document live in
# one folder, and that folder is grouped under its kind.
_LEGACY_PUBLISHED_FILENAME_RE = re.compile(r"^(?P<kind>[a-z_]+)-(?P<slug>.+)-v(?P<v>\d+\.\d+)\.md$")


def _migrate_actor_isroot_to_false(raw: dict[str, Any]) -> dict[str, Any]:
    """v0.24.11 (D-2026-05-19-D) — reset legacy actor ``is_root=True``
    to False. Idempotent (no-op after first read).

    Background: pre-v0.24.11, ``actor.is_root`` was retained as a
    cross-canvas master marker (per SPEC.md). The user pinned 2026-05-19
    that every actor is a Symbol candidate (referenceable from the
    Service canvas via ``actor_ref``), so the boolean distinguishes
    nothing. Actor.is_root is now deprecated; service.is_root remains
    (ServiceDetail anchor marker).
    """
    nodes = raw.get("nodes")
    if not isinstance(nodes, list):
        return raw
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("kind") == "actor" and node.get("is_root") is True:
            node["is_root"] = False
    return raw


def _migrate_published_flat_to_kind_slug(canvas_dir: Path) -> None:
    """Move legacy flat published files into the new kind/slug/version layout.

    Idempotent: looks only at direct ``.md`` children of
    ``<canvas_dir>/published/``. Once moved, no files match the regex
    there so subsequent calls are no-ops. Existing destinations are
    skipped (the new layout takes precedence — we never overwrite).
    """
    published_dir = canvas_dir / "published"
    if not published_dir.is_dir():
        return
    for entry in published_dir.iterdir():
        if not entry.is_file() or entry.suffix != ".md":
            continue
        match = _LEGACY_PUBLISHED_FILENAME_RE.match(entry.name)
        if not match:
            continue
        kind = match.group("kind")
        slug = match.group("slug")
        version = match.group("v")
        dest = published_dir / kind / slug / f"v{version}.md"
        if dest.exists():
            # New layout already has this version; the legacy file is
            # redundant. Leave it in place rather than silently delete
            # — caller can clean up after auditing.
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        entry.rename(dest)


# v0.24.3 (D-2026-05-18-A) — published slug-folder → id-folder migration.
# Pre-v0.24.3 layout used ``slugify(label)`` as the folder name, which
# could be Korean / CJK. v0.24.3 switches to node id (ASCII per Plot's
# id policy) for clean, rename-stable folder names. Idempotent —
# once renamed, the slug folder no longer exists so subsequent reads
# are no-ops.


def _migrate_published_slug_to_id(canvas_dir: Path, raw_canvas: dict[str, Any]) -> None:
    """Rename ``<canvas>/published/<kind>/<slug>/`` folders to
    ``<canvas>/published/<kind>/<node_id>/`` for every node whose
    id and label appear in the raw canvas. Nodes whose id already
    equals their slug (e.g. id="mission" + label="Mission") are
    a no-op rename. Missing slug folders are silently skipped.
    Conflicts (id folder already exists) leave the slug folder in
    place so the user can audit; we never overwrite.
    """
    from plot_mcp.slug import slugify

    published_dir = canvas_dir / "published"
    if not published_dir.is_dir():
        return
    nodes = raw_canvas.get("nodes")
    if not isinstance(nodes, list):
        return
    for node in nodes:
        if not isinstance(node, dict):
            continue
        kind = node.get("kind")
        node_id = node.get("id")
        label = node.get("label")
        if not isinstance(kind, str) or not isinstance(node_id, str):
            continue
        if not isinstance(label, str):
            continue
        slug = slugify(label) or "untitled"
        if slug == node_id:
            continue  # already at the new layout (or coincidentally identical)
        kind_dir = published_dir / kind
        if not kind_dir.is_dir():
            continue
        slug_dir = kind_dir / slug
        id_dir = kind_dir / node_id
        if not slug_dir.is_dir():
            continue
        if id_dir.exists():
            continue  # destination occupied — leave slug folder for audit
        slug_dir.rename(id_dir)


# v0.26.0 (D-2026-05-25-A) — ``_wrap_legacy_services_in_default_category``
# removed. The v0.12 "service must be nested in a category" invariant
# was enforced via ``parent_id`` (now removed). With the new directed
# edge model, services may sit at any level; the wrapper that seeded
# a fake default-category is no longer needed.


def _migrate_parent_id_to_directed_edges(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.26.0 (D-2026-05-25-A) — convert pre-v0.26 ``parent_id`` field
    to a directed edge from parent → child. Idempotent.

    For each node carrying a non-null ``parent_id``:
      1. Remove the ``parent_id`` key from the node dict.
      2. Append a directed edge ``parent → child`` to ``edges`` (with
         a stable id ``e_migrated_{node_id}``), unless an equivalent
         directed edge already exists.

    Also fills ``directed: True`` on any pre-v0.26 edge that lacks
    the field — that matches the new default (``SketchEdge.directed =
    True``) and preserves any explicit hierarchical intent from
    earlier sessions.

    On any actual change, persists back to disk so the file settles
    into the new model. Subsequent reads are no-ops.
    """
    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    edges: list[dict[str, Any]] = list(raw.get("edges") or [])

    changed = False
    existing_directed = {
        (e.get("source"), e.get("target")) for e in edges if e.get("directed", True)
    }
    rebuilt_nodes: list[dict[str, Any]] = []
    for n in nodes:
        pid = n.get("parent_id")
        if pid is None and "parent_id" not in n:
            rebuilt_nodes.append(n)
            continue
        # Drop parent_id from the node copy.
        new_node = {k: v for k, v in n.items() if k != "parent_id"}
        rebuilt_nodes.append(new_node)
        changed = True
        if pid is None or pid == n.get("id"):
            continue
        key = (pid, n.get("id"))
        if key in existing_directed:
            continue
        edges.append(
            {
                "id": f"e_migrated_{n.get('id')}",
                "source": pid,
                "target": n.get("id"),
                "sourceHandle": None,
                "targetHandle": None,
                "label": "",
                "style": "solid",
                "directed": True,
                "action_verb": None,
                "value_form": [],
            }
        )
        existing_directed.add(key)

    rebuilt_edges: list[dict[str, Any]] = []
    for e in edges:
        if "directed" not in e:
            rebuilt_edges.append({**e, "directed": True})
            changed = True
        else:
            rebuilt_edges.append(e)

    if not changed:
        return raw

    raw = {**raw, "nodes": rebuilt_nodes, "edges": rebuilt_edges}
    _write_json(_canvas_file(plot_root, project_id, canvas_kind, service_id), raw)
    return raw


def _migrate_assign_edge_relation(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.30.0 (D-2026-05-31-C) — assign the stored ``relation`` semantic
    to any edge that lacks it. Idempotent.

    For each edge with no ``relation`` key, set it to
    ``classify_edge(canvas_kind, <source-node kind>)``. The source kind
    is looked up from the canvas's own nodes; the synthetic project
    anchor (not in ``nodes``) resolves to ``None`` → ``classify_edge``
    handles it (flow, or inheritance on the actors canvas). On any
    actual change, persists back to disk so subsequent reads are no-ops.
    """
    edges: list[dict[str, Any]] = list(raw.get("edges") or [])
    if all("relation" in e for e in edges):
        return raw

    kind_by_id: dict[str, str] = {
        n.get("id"): n.get("kind") for n in (raw.get("nodes") or []) if n.get("id")
    }
    rebuilt_edges: list[dict[str, Any]] = []
    changed = False
    for e in edges:
        if "relation" in e:
            rebuilt_edges.append(e)
            continue
        src = e.get("source")
        source_kind = kind_by_id.get(src) if isinstance(src, str) else None
        rebuilt_edges.append({**e, "relation": classify_edge(canvas_kind, source_kind)})
        changed = True

    if not changed:
        return raw

    raw = {**raw, "edges": rebuilt_edges}
    _write_json(_canvas_file(plot_root, project_id, canvas_kind, service_id), raw)
    return raw


def _drop_disallowed_services_kinds(
    plot_root: Path,
    project_id: str,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.11.5 migration helper: silently drop ``mission_ref`` / ``value_ref``
    / ``identity_ref`` (and any other now-disallowed kinds) from the services
    top view. They live in ``service_detail`` from v0.11.5 onwards.
    Idempotent.

    v0.12 update: read the live ``_ALLOWED_KINDS_BY_CANVAS`` so future
    additions to the services-canvas allow-list don't trigger spurious
    drops here.
    """
    from plot_mcp.models import _ALLOWED_KINDS_BY_CANVAS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    allowed = _ALLOWED_KINDS_BY_CANVAS["services"]
    kept = [n for n in nodes if n.get("kind") in allowed or n.get("kind") is None]
    if len(kept) == len(nodes):
        return raw
    raw = {**raw, "nodes": kept}
    _write_json(_canvas_file(plot_root, project_id, "services"), raw)
    return raw


def _foundation_md_path(
    plot_root: Path, project_id: str, kind: str, node_id: str, label: str
) -> Path:
    """v0.13 Phase 3+6: per-node Markdown file path for a Foundation node.

    Layout: ``foundation/{kind}-{slugified-label}.md`` directly under the
    canvas folder (no per-node subfolder). The node's ``id`` is the
    stable identity; the slug derives from ``label`` and is regenerated
    on rename. We pin uniqueness by also embedding the kind so two
    differently-kinded nodes with the same label don't collide.
    """
    from plot_mcp.slug import slugify

    base_slug = slugify(label) if label.strip() else node_id
    return _project_dir(plot_root, project_id) / "foundation" / f"{kind}-{base_slug}.md"


def _legacy_md_dir(plot_root: Path, project_id: str) -> Path:
    return _project_dir(plot_root, project_id) / "foundation" / "_legacy"


def _absorb_md_typed_text_into_json(
    plot_root: Path, project_id: str, raw: dict[str, Any]
) -> dict[str, Any]:
    """v0.17 Phase 1 one-shot read-side migrator (D-2026-05-16-A).

    For each Foundation node of a typed-text kind (mission / core_value /
    identity), absorb the H2 typed sections + post-``---`` free prose
    from ``foundation/{kind}-{slug}.md`` into the JSON node (typed fields
    + new ``body`` field, all as MD-formatted strings), clear
    ``details_path`` to ``None``, and quarantine the source MD file to
    ``foundation/_legacy/{kind}-{slug}.md``.

    Conflict policy (4 scenarios):
      - JSON empty,   MD populated → MD wins; absorb.
      - JSON populated, MD missing → no-op for fields (JSON already SSoT).
      - Both populated              → JSON wins (latest); MD still quarantined.
      - Both empty                  → no-op.

    Idempotent: once the original MD path is gone, subsequent reads see
    no source file and skip. The ``_legacy/`` quarantine is never read.
    """
    from plot_mcp.md_template import parse_md_template
    from plot_mcp.models import FOUNDATION_MD_FIELDS, FOUNDATION_TYPED_TEXT_FIELDS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    changed = False
    new_nodes: list[dict[str, Any]] = []
    for n in nodes:
        kind = n.get("kind")
        if not isinstance(kind, str) or not FOUNDATION_MD_FIELDS.get(kind):
            new_nodes.append(n)
            continue
        md_path = _foundation_md_path(plot_root, project_id, kind, n["id"], n.get("label", ""))
        # No source MD → no field absorption + no quarantine move. But
        # Foundation typed-text kinds carry no ``details_path`` in v0.17+
        # (invariant per D-2026-05-16-A: JSON is SSOT for these kinds;
        # the viewer's MD-editor surface is gone). Clear unconditionally
        # if set; idempotent when already cleared.
        if not md_path.exists():
            if n.get("details_path") is not None:
                cleaned = {**n, "details_path": None}
                changed = True
                new_nodes.append(cleaned)
                continue
            new_nodes.append(n)
            continue
        parsed = parse_md_template(md_path.read_text(encoding="utf-8"), kind)
        merged = {**n}
        # Typed H2 fields: JSON value wins when present, else absorb MD.
        for field in FOUNDATION_TYPED_TEXT_FIELDS.get(kind, []):
            json_val = str(merged.get(field) or "")
            md_val = parsed.typed_fields.get(field, "")
            if not json_val.strip() and md_val.strip():
                merged[field] = md_val
        # body ← MD's post-``---`` free prose (same conflict policy).
        json_body = str(merged.get("body") or "")
        if not json_body.strip() and parsed.free_prose.strip():
            merged["body"] = parsed.free_prose
        # Foundation typed-text kinds carry no details_path in v0.17+.
        merged["details_path"] = None
        # Quarantine the source MD file. ``Path.rename`` is atomic within
        # the same filesystem; if the destination already exists (e.g.
        # duplicate slug across nodes), append the node-id short suffix
        # and try once more; if still colliding, leave the source in
        # place and continue (no data loss, just deferred cleanup).
        legacy_dir = _legacy_md_dir(plot_root, project_id)
        legacy_dir.mkdir(parents=True, exist_ok=True)
        dest = legacy_dir / md_path.name
        if dest.exists():
            short_id = str(n.get("id", ""))[:8] or "x"
            dest = legacy_dir / f"{md_path.stem}-{short_id}.md"
        if dest.exists():
            # Two collisions — give up moving (rare; leave on disk).
            new_nodes.append(merged)
            changed = True
            continue
        md_path.rename(dest)
        new_nodes.append(merged)
        changed = True
    if changed:
        raw = {**raw, "nodes": new_nodes}
        _write_json(_canvas_file(plot_root, project_id, "foundation"), raw)
    return raw


def collect_foundation_md_warnings(
    plot_root: Path, project_id: str, canvas: CanvasDoc
) -> dict[str, list[str]]:
    """v0.17 Phase 1 (D-2026-05-16-A): JSON is the sole SSOT for
    Foundation typed-text fields. The pre-v0.17 MD-template parser
    warnings are no longer surfaced because there are no MD files left
    at the canonical path after ``_absorb_md_typed_text_into_json``
    runs. Kept as a stable callable so the API response shape stays
    backward-compatible; Phase 6 will drop the call site entirely.
    """
    return {}


def _evict_legacy_project_anchor(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.13 Phase 0 migration helper: project anchor is now in
    ``ProjectDoc.anchors``. If an old canvas .json still carries a
    ``project`` kind node, copy its position/visual into ProjectDoc.anchors
    and remove the node. Idempotent — does nothing once cleaned up.
    """
    from plot_mcp.models import AnchorPlacement

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    legacy_anchors = [n for n in nodes if n.get("kind") == "project"]
    if not legacy_anchors:
        # Defensive: an earlier eviction (without the edge cleanup that
        # landed in v0.13.0) may have left orphan edges referencing the
        # removed project node. Strip them now if any are still pointing
        # at a vanished id.
        #
        # v0.16.38 (D-2026-05-13-N) — the synthetic project anchor
        # ``PROJECT_ANCHOR_ID`` is a valid edge endpoint per
        # D-2026-05-04-B SPEC mandate even though it doesn't live in
        # ``nodes``. Whitelist it here so user-drawn anchor edges
        # aren't strip-and-rewritten on every read (which triggered
        # the watcher → broadcast → refetch loop reported by the
        # user on 2026-05-13 as *"새로고침을 하다보면 캔버스에 노드들이
        # 사라지는 이슈"*).
        from plot_mcp.models import PROJECT_ANCHOR_ID

        node_ids = {n.get("id") for n in nodes} | {PROJECT_ANCHOR_ID}
        edges: list[dict[str, Any]] = list(raw.get("edges") or [])
        kept_edges = [
            e for e in edges if e.get("source") in node_ids and e.get("target") in node_ids
        ]
        if len(kept_edges) != len(edges):
            raw = {**raw, "edges": kept_edges}
            _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
        return raw
    try:
        proj = read_project(plot_root, project_id)
    except FileNotFoundError:
        # No project doc → can't migrate; just drop the node so the canvas
        # validates. Position is unrecoverable but defaults are sensible.
        kept = [n for n in nodes if n.get("kind") != "project"]
        raw = {**raw, "nodes": kept}
        _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
        return raw
    legacy = legacy_anchors[0]
    anchor = AnchorPlacement(
        x=float(legacy.get("x", -75.0)),
        y=float(legacy.get("y", -75.0)),
        width=float(legacy.get("width", 150.0)),
        height=float(legacy.get("height", 150.0)),
        color=str(legacy.get("color", "#fef3c7")),
        shape=legacy.get("shape", "circle"),
    )
    new_anchors = {**proj.anchors, canvas_kind: anchor}
    proj = proj.model_copy(update={"anchors": new_anchors})
    write_project(plot_root, proj)
    evicted_ids = {n.get("id") for n in legacy_anchors}
    kept = [n for n in nodes if n.get("kind") != "project"]
    # v0.13 Phase 0: also drop any edges that referenced the evicted project
    # node — otherwise CanvasDoc validator fails with "edges reference
    # unknown nodes".
    all_edges: list[dict[str, Any]] = list(raw.get("edges") or [])
    kept_edges = [
        e
        for e in all_edges
        if e.get("source") not in evicted_ids and e.get("target") not in evicted_ids
    ]
    raw = {**raw, "nodes": kept, "edges": kept_edges}
    _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
    return raw


def write_canvas(plot_root: Path, project_id: str, canvas: CanvasDoc) -> None:
    _ensure_project(plot_root, project_id)
    service_id = canvas.service_ref if canvas.canvas_kind == "service_detail" else None
    path = _canvas_file(plot_root, project_id, canvas.canvas_kind, service_id)
    # v0.22.0 (D-2026-05-17-H) — preserve server-managed
    # ``_publish_baseline`` across PUTs. The client doesn't round-trip
    # this field (it's a server-managed dirty baseline), so a PUT from
    # the viewer would otherwise clobber it back to ``None`` and reset
    # every clean node to dirty. Read the existing on-disk canvas and
    # carry any non-None baseline forward for nodes whose incoming
    # baseline is ``None``.
    existing_baselines: dict[str, dict[str, Any]] = {}
    if path.is_file():
        try:
            existing_raw = _read_json(path)
            existing = CanvasDoc.model_validate(existing_raw)
            existing_baselines = {
                n.id: n.publish_baseline for n in existing.nodes if n.publish_baseline is not None
            }
        except (FileNotFoundError, ValueError, ValidationError):
            existing_baselines = {}
    if existing_baselines:
        preserved = [
            n.model_copy(update={"publish_baseline": existing_baselines[n.id]})
            if (n.publish_baseline is None and n.id in existing_baselines)
            else n
            for n in canvas.nodes
        ]
        canvas = canvas.model_copy(update={"nodes": preserved})
    raw = canvas.model_dump(by_alias=True)
    # v0.17 Phase 1 (D-2026-05-16-A) — JSON is the sole SSOT for
    # Foundation typed-text fields. The v0.13 ``_split_foundation_typed_
    # text_to_md`` write-side helper is gone; Pydantic now serialises
    # every field (typed + body) into the JSON output directly.
    _write_json(path, raw)
    try:
        meta = read_project(plot_root, project_id)
    except FileNotFoundError:
        return
    # v0.13 Phase 0: project label SSOT is ProjectDoc.name; no longer derived
    # from a per-canvas project node (the node is gone). Renames go through
    # ``rename_project`` directly. We just bump updated below.
    write_project(plot_root, meta)


def rename_project(plot_root: Path, project_id: str, new_name: str) -> ProjectDoc:
    """Update ``ProjectDoc.name``. v0.13 Phase 0: there is no per-canvas
    project node any more — label is derived from ProjectDoc.name at render
    time. Touching the foundation canvas via read still triggers the
    legacy-anchor eviction migrator for old projects.
    """
    proj = read_project(plot_root, project_id)
    renamed = proj.model_copy(update={"name": new_name})
    write_project(plot_root, renamed)
    # v0.13 Phase 0: project anchors no longer carry the label as a node
    # field — label SSOT is ProjectDoc.name, derived at render. Touch the
    # foundation canvas via read so the legacy-anchor eviction migrator
    # runs if the project predates v0.13.
    try:
        read_canvas(plot_root, project_id, "foundation")
    except FileNotFoundError:
        pass
    return read_project(plot_root, project_id)


def list_service_details(plot_root: Path, project_id: str) -> list[str]:
    """Return the service ids for which a Detail canvas exists.
    v0.8 layout: each service lives at ``services/{sid}/`` and its detail
    canvas is the sibling ``detail.json`` alongside ``index.md``. Folders
    without a ``detail.json`` (e.g. a service connected to a folder but
    whose detail was archived) are skipped."""
    _ensure_project(plot_root, project_id)
    services_folder = _project_dir(plot_root, project_id) / "services"
    if not services_folder.is_dir():
        return []
    return sorted(
        sid.name
        for sid in services_folder.iterdir()
        if sid.is_dir() and (sid / "detail.json").is_file()
    )


# ---------------------------------------------------------------------------
# create / delete
# ---------------------------------------------------------------------------


def _seed_foundation_canvas(project_name: str) -> CanvasDoc:  # noqa: ARG001
    """Minimum valid Foundation canvas — Mission / Core Value / Identity.

    v0.13 Phase 0: the Project anchor is no longer a node here. It lives in
    ``ProjectDoc.anchors["foundation"]`` and is rendered by the viewer at
    display time. ``project_name`` argument retained for signature stability
    but unused.
    """
    return CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            MissionNode(
                id="mission",
                label="Mission",
                x=-360,
                y=-45,
                width=200,
                height=90,
                color="#fef3c7",
                shape="rounded",
            ),
            CoreValueNode(
                id="core-value-1",
                label="Core value",
                x=-90,
                y=-260,
                width=180,
                height=80,
                color="#fde68a",
                shape="rounded",
            ),
            IdentityNode(
                id="identity",
                label="Voice",
                x=160,
                y=-45,
                width=200,
                height=90,
                color="#fed7aa",
                shape="rounded",
            ),
        ],
    )


def _seed_actors_canvas(project_name: str) -> CanvasDoc:  # noqa: ARG001
    """v0.11 — actors canvas seeds with two placeholder classes ("Operator"
    and "User") to satisfy the IDENTITY.md "≥ 2 actor classes" minimum.

    v0.13 Phase 0: project anchor moved to ``ProjectDoc.anchors``; not seeded
    here.
    """
    return CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(
                id="operator",
                label="Operator",
                side="operator",
                x=-260,
                y=-50,
                width=140,
                height=80,
                color="#bae6fd",
                shape="rounded",
            ),
            ActorNode(
                id="user",
                label="User",
                side="user",
                x=140,
                y=-50,
                width=140,
                height=80,
                color="#fecaca",
                shape="rounded",
            ),
        ],
    )


def _seed_services_canvas(project_name: str) -> CanvasDoc:  # noqa: ARG001
    """v0.13 Phase 0: services canvas starts empty (project anchor moved to
    ``ProjectDoc.anchors``). Categories + services are added by the user.
    """
    return CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[],
    )


def create_project(plot_root: Path, project_id: str, name: str) -> ProjectDoc:
    """Create a fresh project folder, seeded with Core / Actors / Services.

    v0.8 layout: one folder per project (``.plot/{project_id}/``) with a
    subfolder per canvas kind. Each canvas folder holds a ``canvas.json``.
    Service-detail canvases join the relevant service folder later via
    ``sync_details_with_overview``.

    Raises ``FileExistsError`` if ``project_id`` is taken.
    """
    folder = _project_dir(plot_root, project_id)
    if folder.exists():
        raise FileExistsError(f"project already exists: {project_id}")
    folder.mkdir(parents=True)
    # Initialise the project's per-folder git repo now so that
    # ``tag_snapshot`` works later without any extra wiring. The repo
    # stays empty until the user plants a tag.
    ensure_repo(folder)

    now = datetime.now(UTC).isoformat()
    proj = ProjectDoc(
        id=project_id,
        name=name or project_id,
        created=date.today().isoformat(),
        updated=now,
        version=3,
    )
    _write_json(_project_file(plot_root, project_id), proj.model_dump())

    _write_json(
        _canvas_file(plot_root, project_id, "foundation"),
        _seed_foundation_canvas(proj.name).model_dump(by_alias=True),
    )
    _write_json(
        _canvas_file(plot_root, project_id, "actors"),
        _seed_actors_canvas(proj.name).model_dump(by_alias=True),
    )
    _write_json(
        _canvas_file(plot_root, project_id, "services"),
        _seed_services_canvas(proj.name).model_dump(by_alias=True),
    )
    # v0.13 Phase 2 — write per-kind JSON Schema + MD template files into
    # ``.plot/{proj}/schema/`` so external tools (Obsidian YAML LSP, custom
    # validators) can verify Foundation node files.
    from plot_mcp.schema_export import export_all_schemas

    export_all_schemas(plot_root, project_id)
    return proj


def delete_project(plot_root: Path, project_id: str) -> None:
    folder = _project_dir(plot_root, project_id)
    if not folder.exists():
        raise FileNotFoundError(f"project not found: {project_id}")
    shutil.rmtree(folder)


# ---------------------------------------------------------------------------
# Overview ↔ Detail sync
# ---------------------------------------------------------------------------


def sync_details_with_overview(plot_root: Path, project_id: str) -> dict[str, list[str]]:
    """Ensure ``services/{sid}/detail.json`` exists for every service in the
    top-view ``services`` canvas.

    Services that disappear from the top view have their whole folder moved
    to ``services/_archive/{sid}/`` — a destructive delete would throw away
    user work (``index.md``, attachments) on a stray click. Called
    opportunistically after writes to the services canvas.

    Returns ``{"created": [...], "archived": [...]}`` for telemetry.
    """
    _ensure_project(plot_root, project_id)
    try:
        overview = read_canvas(plot_root, project_id, "services")
    except FileNotFoundError:
        return {"created": [], "archived": []}
    overview_service_ids = {n.id for n in overview.nodes if n.kind == "service"}
    services_folder = _project_dir(plot_root, project_id) / "services"
    services_folder.mkdir(exist_ok=True)
    # Existing service folders: every immediate subdir that isn't ``_archive``
    # and has its own ``detail.json``.
    existing_details: set[str] = set()
    if services_folder.is_dir():
        for child in services_folder.iterdir():
            if child.is_dir() and child.name != "_archive" and (child / "detail.json").is_file():
                existing_details.add(child.name)

    created: list[str] = []
    for service_id in sorted(overview_service_ids - existing_details):
        src = next(n for n in overview.nodes if n.id == service_id)
        detail = CanvasDoc(
            canvas_id=service_id,
            canvas_kind="service_detail",
            service_ref=service_id,
            # v0.11 — every service_detail needs ≥ 2 actor_refs (operator +
            # user) per IDENTITY.md. Auto-seed two stub refs that point at
            # the project's seeded actors. Users can re-pick via the
            # picker, or add more refs as the design develops.
            nodes=[
                # v0.26.0 (D-2026-05-25-A) — parent_id field removed;
                # service_detail root carries no structural parent
                # (is_root marks the canvas anchor).
                src.model_copy(update={"is_root": False}),
                ActorRefNode(
                    id=f"{service_id}-operator-ref",
                    label="→ Operator",
                    ref_actor_id="operator",
                    side="operator",
                    color="#bae6fd",
                    shape="rectangle",
                    width=140,
                    height=70,
                ),
                ActorRefNode(
                    id=f"{service_id}-user-ref",
                    label="→ User",
                    ref_actor_id="user",
                    side="user",
                    color="#fecaca",
                    shape="rectangle",
                    width=140,
                    height=70,
                ),
            ],
        )
        _write_json(
            _canvas_file(plot_root, project_id, "service_detail", service_id=service_id),
            detail.model_dump(by_alias=True),
        )
        created.append(service_id)

    archive_folder = services_folder / "_archive"
    archived: list[str] = []
    skipped_archive: list[str] = []
    for service_id in sorted(existing_details - overview_service_ids):
        src_path = services_folder / service_id
        # v0.27.14 (D-2026-05-28-I) — data-loss guard: if the disappearing
        # detail carries user-authored content (any node outside the
        # default seed set ``{service_id, {sid}-operator-ref,
        # {sid}-user-ref}``, OR any edges), do NOT silently archive.
        # The user's 2026-05-27 chrome-devtools session lost a root
        # service + its detail to a sync archive triggered by an
        # injected onNodesChange burst; this branch protects the
        # next instance of that pattern. Empty / default-seeded details
        # archive cleanly as before (existing test_sync coverage).
        if _detail_has_user_authored_content(src_path, service_id):
            skipped_archive.append(service_id)
            continue
        archive_folder.mkdir(exist_ok=True)
        dst_path = archive_folder / service_id
        # If the archive already has a folder with the same id (rare — same
        # service created, archived, and recreated), rename with a suffix.
        if dst_path.exists():
            n = 2
            while (archive_folder / f"{service_id}-{n}").exists():
                n += 1
            dst_path = archive_folder / f"{service_id}-{n}"
        src_path.replace(dst_path)
        archived.append(service_id)

    result: dict[str, list[str]] = {"created": created, "archived": archived}
    if skipped_archive:
        result["skipped_archive"] = skipped_archive
    else:
        result["skipped_archive"] = []
    return result


def _detail_has_user_authored_content(detail_dir: Path, service_id: str) -> bool:
    """v0.27.14 (D-2026-05-28-I) — return True iff the service's
    ``detail.json`` contains anything beyond the default seeded shape
    (root service node + 2 actor_refs, no edges).  Used by
    ``sync_details_with_overview`` to refuse to archive details the
    user has invested work in.
    """
    detail_path = detail_dir / "detail.json"
    if not detail_path.is_file():
        return False
    try:
        doc = json.loads(detail_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # Unreadable / malformed: treat as user content to be safe.
        return True
    seeded_ids = {
        service_id,
        f"{service_id}-operator-ref",
        f"{service_id}-user-ref",
    }
    nodes = doc.get("nodes") or []
    edges = doc.get("edges") or []
    if edges:
        return True
    for node in nodes:
        if not isinstance(node, dict):
            return True
        if node.get("id") not in seeded_ids:
            return True
    return False


# ---------------------------------------------------------------------------
# v0.18.0 Phase 3 (D-2026-05-16-E) — per-node publish
# ---------------------------------------------------------------------------


class PublishNotEligibleError(ValueError):
    """Raised by ``publish_node`` when the target node is not
    publish-eligible (project anchor, is_root, ``*_ref``).
    Mirrors the server-side guard for the viewer's button visibility
    rule in ``viewer/src/domain/publishEligibility.ts``."""


def _load_all_canvases(plot_root: Path, project_id: str) -> dict[str, CanvasDoc]:
    """Load every canvas in a project, keyed by a unique string.

    Key scheme:
      - ``"foundation"`` → foundation canvas
      - ``"actors"`` → actors canvas
      - ``"services"`` → services canvas
      - ``"service_detail:<service_id>"`` → per-service detail canvas

    Used by Phase 4 (D-2026-05-17-C) propagation walk; the walk only
    requires the keys to be unique within the returned dict.
    """
    canvases: dict[str, CanvasDoc] = {}
    fixed_kinds: tuple[CanvasKind, ...] = ("foundation", "actors", "services")
    for kind in fixed_kinds:
        try:
            canvases[kind] = read_canvas(plot_root, project_id, kind)
        except FileNotFoundError:
            continue
    for sid in list_service_details(plot_root, project_id):
        try:
            canvases[f"service_detail:{sid}"] = read_canvas(
                plot_root, project_id, "service_detail", service_id=sid
            )
        except FileNotFoundError:
            continue
    return canvases


def _bump_node_version_in_canvas(canvas: CanvasDoc, node_id: str, to_v: str) -> CanvasDoc:
    """Return a copy of ``canvas`` with ``node_id``'s version replaced."""
    new_nodes = [
        n.model_copy(update={"version": to_v}) if n.id == node_id else n for n in canvas.nodes
    ]
    return canvas.model_copy(update={"nodes": new_nodes})


# ---------------------------------------------------------------------------
# v0.22.0 (D-2026-05-17-H) — publish dirty tracking
# ---------------------------------------------------------------------------

# Fields excluded from the dirty snapshot. Visual placement / size / color
# / shape / icon / collapsed are user state but do NOT influence the
# published MD content, so editing them must not flip a clean node to
# dirty.
_DIRTY_VISUAL_FIELDS: frozenset[str] = frozenset(
    {"x", "y", "width", "height", "color", "shape", "icon", "collapsed"}
)

# Fields excluded from the dirty snapshot for non-content reasons:
#   - id: node identity, never compared
#   - version: moves with publish; the bump itself is not new content
#   - is_root: structural metadata; only set at creation
#   - details_path: legacy MD path; v0.17 JSON SSOT made it inert for the
#     10 publish-eligible kinds
#   - owner: multi-user prep; not user content
#   - _publish_baseline / publish_baseline: the baseline itself
#   - _md_warnings: never persisted; server decoration only
# v0.26.0 (D-2026-05-25-A) — ``parent_id`` removed from this exclusion
# list alongside the field. Structural reparenting is now expressed
# via directed edges and *is* picked up by the dirty snapshot via the
# incident-edge slice (already part of the snapshot).
_DIRTY_NON_CONTENT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "version",
        "is_root",
        "details_path",
        "owner",
        "publish_baseline",
        "_publish_baseline",
        "_md_warnings",
    }
)


def _incident_edges(edges: list[SketchEdge], node_id: str) -> list[SketchEdge]:
    """Edges where ``node_id`` is either endpoint."""
    return [e for e in edges if e.source == node_id or e.target == node_id]


def _dirty_snapshot(node: SketchNode, incident_edges: list[SketchEdge]) -> dict[str, Any]:
    """Capture the dirty-relevant slice of a node + its incident edges.

    Includes: typed-text fields + label + body + ``kind`` discriminator +
    incident edges (sorted, edge ``id`` excluded).
    Excludes: visual fields (``_DIRTY_VISUAL_FIELDS``), structural / identity
    fields (``_DIRTY_NON_CONTENT_FIELDS``).
    """
    node_raw = node.model_dump(by_alias=True)
    for f in _DIRTY_VISUAL_FIELDS | _DIRTY_NON_CONTENT_FIELDS:
        node_raw.pop(f, None)
    edges_raw = [
        {k: v for k, v in e.model_dump(by_alias=True).items() if k != "id"} for e in incident_edges
    ]
    edges_raw.sort(
        key=lambda d: (
            d.get("source", "") or "",
            d.get("target", "") or "",
            d.get("sourceHandle", "") or "",
            d.get("targetHandle", "") or "",
            d.get("label", "") or "",
        )
    )
    return {"node": node_raw, "edges": edges_raw}


def is_node_dirty(node: SketchNode, incident_edges: list[SketchEdge]) -> bool:
    """``True`` when the node has been edited (content / edges) since its
    last publish. ``True`` when no baseline exists yet (initial publish
    is always allowed)."""
    if node.publish_baseline is None:
        return True
    return _dirty_snapshot(node, incident_edges) != node.publish_baseline


def _patch_node_in_canvas(canvas: CanvasDoc, node_id: str, patch: dict[str, Any]) -> CanvasDoc:
    """Return a copy of ``canvas`` with ``node_id``'s listed fields
    replaced via ``model_copy(update=patch)``. Preserves all other
    fields — important for mirror sync where canvas-local state
    (e.g. ``is_root`` on the ServiceDetail mirror vs ``False`` on the
    services master) must remain canvas-specific."""
    new_nodes = [n.model_copy(update=patch) if n.id == node_id else n for n in canvas.nodes]
    return canvas.model_copy(update={"nodes": new_nodes})


def publish_node(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    node_id: str,
    *,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Publish ``node_id`` on the named canvas.

    Flow (per [D-2026-05-16-E] + [D-2026-05-17-C] Phase 4):
      1. Load every canvas in the project (Phase 4 needs the full
         ancestor walk).
      2. Locate the target node; validate eligibility (``can_publish``).
      3. Compute ``from_v`` / ``to_v`` (MAJOR bump for the target).
      4. MAJOR-bump the target's ``version`` in **every** canvas it
         appears in (mirror sync — e.g. a service node has presences
         in both Services and ServiceDetail).
      5. Render the published MD content via ``render_node_md`` and
         write to ``<canvas_dir>/published/{kind}-{slug}-{to_v}.md``.
         The MD anchor canvas is the one the user published from
         (``canvas_kind``).
      6. Walk the ancestor chain (``propagation.walk_ancestors``).
         For each logical ancestor, MINOR-bump its ``version`` in
         every canvas where it has file-presence (mirror sync again).
      7. Persist every touched canvas (write_canvas).
      8. Create a single git commit via ``publish_snapshot`` with
         5 base ``Publish-*:`` trailers + one
         ``Publish-Propagated-Ancestor:`` per ancestor.

    Returns ``{node_id, from_version, to_version, md_path, sha,
    propagated}``. ``propagated`` is a list of
    ``{node_id, from_version, to_version, canvases}`` so clients can
    refresh the affected inspector badges in one round-trip.

    Raises ``KeyError`` if ``node_id`` not on the canvas;
    ``PublishNotEligibleError`` if the kind/role disallows publish.
    """
    project_dir = _ensure_project(plot_root, project_id)
    # v0.23.x (D-2026-05-17-J) — snapshot any pre-publish working-tree
    # state into its own commit so a future ``git revert`` of the
    # publish commit cannot wipe unrelated files (e.g. untracked
    # canvas.json in a fresh project).
    ensure_clean_working_tree(project_dir)
    canvases = _load_all_canvases(plot_root, project_id)
    start_canvas_key = (
        f"service_detail:{service_id}" if canvas_kind == "service_detail" else canvas_kind
    )
    start_canvas = canvases.get(start_canvas_key)
    if start_canvas is None:
        raise FileNotFoundError(f"canvas {canvas_kind!r} (service_id={service_id!r}) not found")

    by_id = {n.id: n for n in start_canvas.nodes}
    if node_id not in by_id:
        raise KeyError(f"node {node_id!r} not on canvas {canvas_kind!r}")
    node = by_id[node_id]
    if not can_publish(node):
        raise PublishNotEligibleError(
            f"node {node_id!r} (kind={node.kind!r}, is_root={node.is_root}) is not publish-eligible"
        )

    from_v = node.version
    to_v = bump_major(from_v)
    bumped = node.model_copy(update={"version": to_v})

    canvas_path = _canvas_file(plot_root, project_id, canvas_kind, service_id)
    canvas_dir = canvas_path.parent
    md_path = published_md_path(canvas_dir, kind=node.kind, node_id=node.id, version=to_v)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        render_node_md(bumped, canvas=canvas_kind),
        encoding="utf-8",
    )

    touched: dict[str, CanvasDoc] = {}

    # v0.22.0 (D-2026-05-17-H) — compute the post-publish dirty baseline
    # using the bumped node + incident edges of the canvas the user
    # published from. Publish-eligible nodes only exist in a single
    # canvas (service masters live in ``services``; their ServiceDetail
    # mirror is ``is_root`` and therefore publish-ineligible), so the
    # start_canvas's edges are the right baseline source.
    incident = _incident_edges(start_canvas.edges, node_id)
    new_baseline = _dirty_snapshot(bumped, incident)

    # Step 4 — MAJOR-bump the target in every canvas it appears in
    # (mirror sync) and stamp the dirty baseline. Patch only ``version``
    # + ``publish_baseline`` so other fields stay canvas-local — most
    # importantly ``is_root`` (services master is False, ServiceDetail
    # mirror is True). v0.26.0 (D-2026-05-25-A): parent_id no longer
    # in this list — containment is now per-canvas directed edges.
    version_baseline_patch: dict[str, Any] = {
        "version": to_v,
        "publish_baseline": new_baseline,
    }
    for key, canvas in canvases.items():
        if any(n.id == node_id for n in canvas.nodes):
            touched[key] = _patch_node_in_canvas(canvas, node_id, version_baseline_patch)

    # Refresh the index for ancestor walking with the post-MAJOR-bump
    # canvases so versions in trailers reflect the real `from_v` we
    # are about to bump (every ancestor stays at its old version
    # until MINOR'd here).
    effective_canvases = {**canvases, **touched}
    ancestors = walk_ancestors(node_id, effective_canvases)

    propagated: list[tuple[str, str, str]] = []
    propagated_records: list[dict[str, Any]] = []
    for ancestor in ancestors:
        # The ancestor's current version is identical across mirrors
        # (kept in sync by every prior publish that touched it).
        sample_canvas_key = ancestor.canvas_keys[0]
        sample_canvas = effective_canvases[sample_canvas_key]
        sample_node = next(n for n in sample_canvas.nodes if n.id == ancestor.node_id)
        anc_from = sample_node.version
        anc_to = bump_minor(anc_from)
        for key in ancestor.canvas_keys:
            base = touched.get(key, effective_canvases[key])
            touched[key] = _bump_node_version_in_canvas(base, ancestor.node_id, anc_to)
        propagated.append((ancestor.node_id, anc_from, anc_to))
        propagated_records.append(
            {
                "node_id": ancestor.node_id,
                "from_version": anc_from,
                "to_version": anc_to,
                "canvases": list(ancestor.canvas_keys),
            }
        )

    for key, canvas in touched.items():
        write_canvas(plot_root, project_id, canvas)

    commit = publish_snapshot(
        project_dir,
        node_id=node.id,
        kind=node.kind,
        canvas=canvas_kind,
        label=node.label,
        from_v=from_v,
        to_v=to_v,
        propagated=propagated,
    )

    return {
        "node_id": node.id,
        "from_version": from_v,
        "to_version": to_v,
        "md_path": str(md_path.relative_to(project_dir)),
        "sha": commit["sha"],
        "propagated": propagated_records,
    }


# ---------------------------------------------------------------------------
# v0.23.x (D-2026-05-17-J) — unpublish
# ---------------------------------------------------------------------------


class UnpublishNotEligibleError(ValueError):
    """Raised by ``unpublish_node`` when there's nothing to undo
    (the node has never been published)."""


def unpublish_node(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    node_id: str,
    *,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Revert the most recent publish of ``node_id`` via ``git revert``.

    Flow:
      1. Validate target canvas + node exist.
      2. Locate the latest publish commit via the
         ``Publish-Node-Id: <node_id>`` trailer.
      3. ``git revert --no-edit <sha>`` — creates a new commit that
         undoes the canvas.json bump(s) + removes the published MD
         file in one step.
      4. Re-read the canvas to capture the new version.

    Returns ``{node_id, from_version, to_version, reverted_sha,
    revert_commit_sha}``.

    Raises ``KeyError`` if the node isn't on the canvas;
    ``UnpublishNotEligibleError`` if no publish commit exists for it.
    """
    project_dir = _ensure_project(plot_root, project_id)
    canvas = read_canvas(plot_root, project_id, canvas_kind, service_id)
    node = next((n for n in canvas.nodes if n.id == node_id), None)
    if node is None:
        raise KeyError(f"node {node_id!r} not on canvas {canvas_kind!r}")
    from_v = node.version
    publish_sha = find_latest_publish_commit(project_dir, node_id)
    if publish_sha is None:
        raise UnpublishNotEligibleError(f"node {node_id!r} has no publish commit to revert")
    revert_sha = revert_publish(project_dir, publish_sha)
    # Re-read the canvas via the regular path to get the new version
    # (the revert restored the previous value).
    canvas_after = read_canvas(plot_root, project_id, canvas_kind, service_id)
    node_after = next((n for n in canvas_after.nodes if n.id == node_id), None)
    to_v = node_after.version if node_after else from_v
    return {
        "node_id": node_id,
        "from_version": from_v,
        "to_version": to_v,
        "reverted_sha": publish_sha,
        "revert_commit_sha": revert_sha,
    }
