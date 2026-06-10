"""Per-node publish/unpublish: dirty detection, version bumps, git snapshots.

Split out of the folder_io god-module (D-2026-06-10-D). folder_io.py re-exports
everything, so import sites and tests are unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from plot_mcp.canvas_io import list_service_details, read_canvas, write_canvas  # noqa: F401
from plot_mcp.git_store import (
    ensure_clean_working_tree,
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
    CanvasDoc,
    CanvasKind,
    SketchEdge,
    SketchNode,
)
from plot_mcp.propagation import walk_ancestors
from plot_mcp.storage import (  # noqa: F401
    _canvas_file,
    _ensure_project,
    _project_dir,
    _project_file,
    _read_json,
    _write_json,
)

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
    ensure_clean_working_tree(plot_root)
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
        plot_root,
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
    _ensure_project(plot_root, project_id)  # validate; git is workspace-level
    canvas = read_canvas(plot_root, project_id, canvas_kind, service_id)
    node = next((n for n in canvas.nodes if n.id == node_id), None)
    if node is None:
        raise KeyError(f"node {node_id!r} not on canvas {canvas_kind!r}")
    from_v = node.version
    publish_sha = find_latest_publish_commit(plot_root, node_id)
    if publish_sha is None:
        raise UnpublishNotEligibleError(f"node {node_id!r} has no publish commit to revert")
    revert_sha = revert_publish(plot_root, publish_sha)
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
