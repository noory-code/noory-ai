"""Folder-based project IO for Plot v0.8 (wrapper-less canvas-grouped layout).

Layout
------

    .plot/{project_id}/
      project.json                   — ProjectDoc metadata
      foundation/canvas.json         — CanvasDoc (canvas_kind = "foundation")
      actors/canvas.json             — CanvasDoc (canvas_kind = "actors")
      services/
        canvas.json                  — top-view (canvas_kind = "services")
        {service_id}/
          index.md                   — Service node long-form (opt-in)
          detail.json                — CanvasDoc (canvas_kind = "service_detail")
"""

from __future__ import annotations

from pathlib import Path

import pytest

from plot_mcp.folder_io import (
    create_project,
    delete_project,
    list_service_details,
    publish_node,
    read_canvas,
    read_project,
    write_canvas,
    write_project,
)
from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    CategoryNode,
    ServiceNode,
    StepNode,
)
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    return resolve_plot_root(str(tmp_path))


# ---------------------------------------------------------------------------
# create_project
# ---------------------------------------------------------------------------


def test_create_project_builds_folder_layout(plot_root: Path) -> None:
    proj = create_project(plot_root, "alpha", "Alpha")
    assert proj.id == "alpha"
    assert proj.name == "Alpha"
    assert proj.version == 3  # v0.13 Phase 0
    folder = plot_root / "alpha"
    assert folder.is_dir()
    assert (folder / "project.json").is_file()
    assert (folder / "foundation" / "canvas.json").is_file()
    assert (folder / "actors" / "canvas.json").is_file()
    assert (folder / "services" / "canvas.json").is_file()


def test_create_project_seeds_foundation_without_project_node(plot_root: Path) -> None:
    """v0.13 Phase 0: project anchor moved to ProjectDoc.anchors. Foundation
    canvas seeds Mission + Core value + Identity pillars only — no project node.
    """
    create_project(plot_root, "alpha", "Alpha")
    foundation = read_canvas(plot_root, "alpha", "foundation")
    kinds = sorted({n.kind for n in foundation.nodes if n.kind is not None})
    assert kinds == ["core_value", "identity", "mission"]
    # v0.26.0 (D-2026-05-25-A) — parent_id field removed; the prior
    # "all peers" check is now trivially satisfied by the field's
    # absence.
    assert not any(hasattr(n, "parent_id") for n in foundation.nodes)
    assert all(n.kind != "project" for n in foundation.nodes)


def test_create_project_seeds_actors_canvas(plot_root: Path) -> None:
    """v0.13 Phase 0: actors canvas seeds Operator + User only (no project node)."""
    create_project(plot_root, "alpha", "Alpha")
    actors = read_canvas(plot_root, "alpha", "actors")
    assert actors.canvas_kind == "actors"
    kinds = sorted({n.kind for n in actors.nodes if n.kind})
    assert kinds == ["actor"]
    assert all(n.kind != "project" for n in actors.nodes)


def test_create_project_seeds_services_canvas(plot_root: Path) -> None:
    """v0.13 Phase 0: services canvas starts empty (no project node)."""
    create_project(plot_root, "alpha", "Alpha")
    overview = read_canvas(plot_root, "alpha", "services")
    assert overview.canvas_kind == "services"
    assert all(n.kind != "project" for n in overview.nodes)


def test_create_project_seeds_anchors_in_project_doc(plot_root: Path) -> None:
    """v0.13 Phase 0: ProjectDoc carries anchor placements per canvas."""
    proj = create_project(plot_root, "alpha", "Alpha")
    assert "foundation" in proj.anchors
    assert "actors" in proj.anchors
    assert "services" in proj.anchors
    assert proj.anchors["foundation"].shape == "circle"


def test_create_duplicate_raises(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    with pytest.raises(FileExistsError):
        create_project(plot_root, "alpha", "Again")


# ---------------------------------------------------------------------------
# read / write
# ---------------------------------------------------------------------------


def test_read_project_returns_metadata(plot_root: Path) -> None:
    proj = create_project(plot_root, "alpha", "Alpha")
    loaded = read_project(plot_root, "alpha")
    assert loaded.id == "alpha"
    assert loaded.name == "Alpha"
    assert loaded.created == proj.created


def test_write_project_updates_timestamp(plot_root: Path) -> None:
    proj = create_project(plot_root, "alpha", "Alpha")
    before = proj.updated
    renamed = proj.model_copy(update={"name": "Renamed"})
    write_project(plot_root, renamed)
    loaded = read_project(plot_root, "alpha")
    assert loaded.name == "Renamed"
    assert loaded.updated >= before


def test_read_missing_project_raises(plot_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_project(plot_root, "ghost")


def test_write_canvas_round_trip(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    canvas = CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="user", label="사용자"),
            ActorNode(id="admin", label="관리자"),
        ],
    )
    write_canvas(plot_root, "alpha", canvas)
    loaded = read_canvas(plot_root, "alpha", "actors")
    # v0.11.4 read backfills the project anchor; just check the actor labels.
    actor_labels = sorted(n.label for n in loaded.nodes if n.kind == "actor")
    assert actor_labels == ["관리자", "사용자"]


def test_write_canvas_rejects_wrong_project(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    with pytest.raises(FileNotFoundError):
        write_canvas(
            plot_root,
            "ghost",
            CanvasDoc(
                canvas_id="actors",
                canvas_kind="actors",
                nodes=[
                    ActorNode(id="op", label="O", side="operator"),
                    ActorNode(id="user", label="U", side="user"),
                ],
            ),
        )


def test_read_missing_canvas_raises(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    # Valid project, but no such detail canvas
    with pytest.raises(FileNotFoundError):
        read_canvas(plot_root, "alpha", "service_detail", service_id="nope")


# ---------------------------------------------------------------------------
# services-detail
# ---------------------------------------------------------------------------


def test_list_service_details_empty_by_default(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    assert list_service_details(plot_root, "alpha") == []


def _detail_with_actor_refs(service_id: str = "order") -> CanvasDoc:
    """v0.27.16 (D-2026-05-28-K) — service_detail invariant loosened to
    ≥ 1 actor_ref. This fixture keeps the 2-actor seed because most
    folder_io tests don't care about the count — they exercise sync /
    publish / archive logic that needs *some* doc to bounce off. The
    invariant itself is covered by ``test_canvas_doc.py``."""
    return CanvasDoc(
        canvas_id=service_id,
        canvas_kind="service_detail",
        service_ref=service_id,
        nodes=[
            ServiceNode(id=service_id, label="주문"),
            ActorRefNode(
                id=f"{service_id}-op",
                label="→ op",
                ref_actor_id="operator",
                side="operator",
            ),
            ActorRefNode(
                id=f"{service_id}-user",
                label="→ user",
                ref_actor_id="user",
                side="user",
            ),
        ],
    )


def test_write_and_list_service_detail(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    detail = _detail_with_actor_refs("order")
    write_canvas(plot_root, "alpha", detail)
    assert list_service_details(plot_root, "alpha") == ["order"]
    loaded = read_canvas(plot_root, "alpha", "service_detail", service_id="order")
    assert loaded.service_ref == "order"
    assert loaded.nodes[0].id == "order"


def test_detail_canvas_path_uses_service_id(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    detail = _detail_with_actor_refs("order")
    write_canvas(plot_root, "alpha", detail)
    assert (plot_root / "alpha" / "services" / "order" / "detail.json").is_file()


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_project_removes_folder(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    delete_project(plot_root, "alpha")
    assert not (plot_root / "alpha").exists()


def test_delete_missing_project_raises(plot_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        delete_project(plot_root, "never-existed")


# ---------------------------------------------------------------------------
# git repo wiring (v0.4)
# ---------------------------------------------------------------------------


def test_create_project_initialises_git_repo(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    assert (plot_root / "alpha" / ".git").is_dir()


def test_create_project_leaves_git_repo_empty(plot_root: Path) -> None:
    """Quiet-repo principle: no automatic commits, HEAD doesn't resolve."""
    import subprocess

    create_project(plot_root, "alpha", "Alpha")
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=plot_root / "alpha",
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_write_canvas_does_not_commit(plot_root: Path) -> None:
    """Editing a canvas must not bump the git log — only tags do."""
    import subprocess

    create_project(plot_root, "alpha", "Alpha")
    write_canvas(
        plot_root,
        "alpha",
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                ActorNode(id="op", label="O", side="operator"),
                ActorNode(id="u", label="U", side="user"),
            ],
        ),
    )
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=plot_root / "alpha",
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0  # still no commits


# ---------------------------------------------------------------------------
# v0.16.38 — D-2026-05-13-N: anchor edges survive the defensive orphan-edge
# cleanup in ``_evict_legacy_project_anchor``.
# ---------------------------------------------------------------------------


def test_read_canvas_preserves_anchor_edges_across_repeated_reads(
    plot_root: Path,
) -> None:
    """Regression: anchor edges (source/target = PROJECT_ANCHOR_ID) must
    survive the defensive orphan-edge cleanup in
    ``_evict_legacy_project_anchor``. Prior to D-2026-05-13-N the
    cleanup's ``node_ids`` set excluded the synthetic anchor id, so
    every read stripped anchor edges from disk and the watcher fired,
    causing the refetch storm + on-screen 'edges disappear after
    reload' symptom (user 2026-05-13).

    This test: write a foundation canvas with two anchor edges, read
    it three times, assert canvas.json's edges array is unchanged and
    the file's mtime does not advance between reads (write would
    advance mtime — the storm trigger)."""
    from plot_mcp.folder_io import _canvas_file
    from plot_mcp.models import (
        PROJECT_ANCHOR_ID,
        CoreValueNode,
        IdentityNode,
        MissionNode,
        SketchEdge,
    )

    create_project(plot_root, "alpha", "Alpha")
    write_canvas(
        plot_root,
        "alpha",
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                MissionNode(id="m", label="Mission"),
                CoreValueNode(id="cv", label="CoreValue"),
                IdentityNode(id="id1", label="Identity"),
            ],
            edges=[
                SketchEdge(
                    id="e_anchor_1",
                    source=PROJECT_ANCHOR_ID,
                    target="m",
                ),
                SketchEdge(
                    id="e_anchor_2",
                    source="cv",
                    target=PROJECT_ANCHOR_ID,
                ),
            ],
        ),
    )

    canvas_path = _canvas_file(plot_root, "alpha", "foundation")
    mtime_baseline = canvas_path.stat().st_mtime

    # Three idle reads must leave the file untouched.
    for _ in range(3):
        doc = read_canvas(plot_root, "alpha", "foundation")
        assert len(doc.edges) == 2, "anchor edges must survive read — D-2026-05-13-N regression"
        edge_endpoints = {(e.source, e.target) for e in doc.edges}
        assert (PROJECT_ANCHOR_ID, "m") in edge_endpoints
        assert ("cv", PROJECT_ANCHOR_ID) in edge_endpoints

    mtime_after = canvas_path.stat().st_mtime
    assert mtime_after == mtime_baseline, (
        "canvas.json mtime advanced between idle reads — the defensive "
        "cleanup is rewriting anchor edges away. That's the v0.16.38 "
        "storm trigger D-2026-05-13-N must prevent."
    )


def test_orphan_non_anchor_edges_still_stripped(plot_root: Path) -> None:
    """The anchor whitelist must not break the original orphan-edge
    cleanup intent: edges referencing a truly missing node (not the
    anchor) should still be stripped on read."""
    import json

    from plot_mcp.folder_io import _canvas_file
    from plot_mcp.models import CoreValueNode, IdentityNode, MissionNode

    create_project(plot_root, "alpha", "Alpha")
    canvas_path = _canvas_file(plot_root, "alpha", "foundation")

    # Manually write a foundation canvas with an orphan edge bypassing
    # Pydantic validation — simulating a pre-v0.13.0 storage state.
    raw = {
        "canvas_id": "foundation",
        "canvas_kind": "foundation",
        "service_ref": None,
        "nodes": [
            MissionNode(id="m", label="M").model_dump(),
            CoreValueNode(id="cv", label="CV").model_dump(),
            IdentityNode(id="id1", label="Id").model_dump(),
        ],
        "edges": [
            {
                "id": "e_orphan",
                "source": "ghost_node",  # not in nodes, not the anchor
                "target": "m",
                "sourceHandle": None,
                "targetHandle": None,
                "label": None,
                "style": "solid",
                "action_verb": None,
                "value_form": [],
            },
        ],
    }
    canvas_path.write_text(json.dumps(raw), encoding="utf-8")

    # First read should strip the orphan edge.
    doc = read_canvas(plot_root, "alpha", "foundation")
    assert len(doc.edges) == 0, "orphan (non-anchor) edge must still be stripped"


# ---------------------------------------------------------------------------
# v0.17 Phase 1 — JSON SSOT (D-2026-05-16-A) absorption migrator
# ---------------------------------------------------------------------------


def _seed_foundation_with_md(
    plot_root: Path,
    project_id: str,
    *,
    json_mission_what_we_do: str = "",
    json_mission_body: str = "",
    md_what_we_do: str | None = "We help **users** discover.\n\n- A\n- B",
    md_why: str | None = "Because clarity matters.",
    md_direction: str | None = "Toward shared intent.",
    md_free_prose: str | None = "Longer notes here.\n## subsection\nWith MD syntax.",
    mission_label: str = "Mission",
    json_details_path: str | None = None,
) -> tuple[Path, Path]:
    """Helper: bootstrap a foundation canvas with the default mission +
    core_value + identity nodes (validator requires all three) and a
    legacy MD file alongside the mission node at the canonical path.
    Returns (canvas_path, md_path). Set md_* to None to skip writing
    that MD section; set json_* to pre-populate JSON values."""
    import json as _json

    from plot_mcp.folder_io import _canvas_file, _foundation_md_path
    from plot_mcp.models import CoreValueNode, IdentityNode, MissionNode

    create_project(plot_root, project_id, project_id.capitalize())
    canvas_path = _canvas_file(plot_root, project_id, "foundation")
    mission_dict = MissionNode(id="m", label=mission_label).model_dump()
    if json_mission_what_we_do:
        mission_dict["what_we_do"] = json_mission_what_we_do
    if json_mission_body:
        mission_dict["body"] = json_mission_body
    if json_details_path is not None:
        mission_dict["details_path"] = json_details_path
    core_value_dict = CoreValueNode(id="cv", label="Value").model_dump()
    identity_dict = IdentityNode(id="id1", label="Persona").model_dump()
    raw = {
        "canvas_id": "foundation",
        "canvas_kind": "foundation",
        "service_ref": None,
        "nodes": [mission_dict, core_value_dict, identity_dict],
        "edges": [],
    }
    canvas_path.write_text(_json.dumps(raw), encoding="utf-8")

    md_path = _foundation_md_path(plot_root, project_id, "mission", "m", mission_label)
    md_chunks: list[str] = [f"# {mission_label}", ""]
    if md_what_we_do is not None:
        md_chunks += ["## What we do", md_what_we_do, ""]
    if md_why is not None:
        md_chunks += ["## Why", md_why, ""]
    if md_direction is not None:
        md_chunks += ["## Direction", md_direction, ""]
    if md_free_prose is not None:
        md_chunks += ["---", md_free_prose]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md_chunks), encoding="utf-8")
    return canvas_path, md_path


def test_absorb_md_typed_text_into_json_basic(plot_root: Path) -> None:
    """JSON empty + MD populated → typed fields + body filled (MD-syntax
    strings preserved verbatim), MD moved to ``foundation/_legacy/``,
    details_path cleared to None."""
    from plot_mcp.folder_io import _legacy_md_dir

    canvas_path, md_path = _seed_foundation_with_md(plot_root, "alpha")

    doc = read_canvas(plot_root, "alpha", "foundation")
    mission = next(n for n in doc.nodes if n.kind == "mission")

    assert mission.what_we_do == "We help **users** discover.\n\n- A\n- B"
    assert mission.why == "Because clarity matters."
    assert mission.direction == "Toward shared intent."
    # parse_md_template normalises free-prose to rstripped + trailing "\n".
    assert mission.body == "Longer notes here.\n## subsection\nWith MD syntax.\n"
    assert mission.details_path is None

    assert not md_path.exists(), "original MD must be moved out of the canonical path"
    legacy_md = _legacy_md_dir(plot_root, "alpha") / md_path.name
    assert legacy_md.exists(), "legacy quarantine must contain the original MD"


def test_absorb_md_typed_text_into_json_both_populated_json_wins(plot_root: Path) -> None:
    """JSON populated + MD populated → JSON values retained; MD still
    quarantined."""
    from plot_mcp.folder_io import _legacy_md_dir

    canvas_path, md_path = _seed_foundation_with_md(
        plot_root,
        "alpha",
        json_mission_what_we_do="json-wins",
        json_mission_body="json-body-wins",
    )

    doc = read_canvas(plot_root, "alpha", "foundation")
    mission = next(n for n in doc.nodes if n.kind == "mission")
    assert mission.what_we_do == "json-wins"
    assert mission.body == "json-body-wins"
    # Fields that JSON didn't populate fall back to MD.
    assert mission.why == "Because clarity matters."
    assert not md_path.exists()
    legacy_md = _legacy_md_dir(plot_root, "alpha") / md_path.name
    assert legacy_md.exists(), "MD is quarantined regardless of conflict outcome"


def test_absorb_md_typed_text_into_json_no_md_file(plot_root: Path) -> None:
    """No MD on disk → no field absorption. details_path cleared only
    if it pointed at the canonical (absent) MD path."""
    import json as _json

    from plot_mcp.folder_io import _canvas_file, _foundation_md_path
    from plot_mcp.models import CoreValueNode, IdentityNode, MissionNode

    create_project(plot_root, "alpha", "Alpha")
    canonical_rel = str(
        _foundation_md_path(plot_root, "alpha", "mission", "m", "Mission").relative_to(
            plot_root / "alpha"
        )
    ).replace("\\", "/")

    canvas_path = _canvas_file(plot_root, "alpha", "foundation")
    mission_dict = MissionNode(id="m", label="Mission", what_we_do="kept").model_dump()
    mission_dict["details_path"] = canonical_rel
    raw = {
        "canvas_id": "foundation",
        "canvas_kind": "foundation",
        "service_ref": None,
        "nodes": [
            mission_dict,
            CoreValueNode(id="cv", label="Value").model_dump(),
            IdentityNode(id="id1", label="Persona").model_dump(),
        ],
        "edges": [],
    }
    canvas_path.write_text(_json.dumps(raw), encoding="utf-8")

    doc = read_canvas(plot_root, "alpha", "foundation")
    mission = next(n for n in doc.nodes if n.kind == "mission")
    assert mission.what_we_do == "kept"
    assert mission.details_path is None, "canonical-pointing details_path is cleared"


def test_absorb_md_typed_text_into_json_idempotent(plot_root: Path) -> None:
    """Calling read_canvas three times moves the MD exactly once; the
    _legacy/ directory carries one entry; mtime is stable on repeat."""
    from plot_mcp.folder_io import _legacy_md_dir

    canvas_path, md_path = _seed_foundation_with_md(plot_root, "alpha")
    read_canvas(plot_root, "alpha", "foundation")
    legacy_dir = _legacy_md_dir(plot_root, "alpha")
    legacy_entries_after_first = sorted(p.name for p in legacy_dir.iterdir())
    canvas_mtime_after_first = canvas_path.stat().st_mtime

    for _ in range(2):
        read_canvas(plot_root, "alpha", "foundation")

    legacy_entries_after_third = sorted(p.name for p in legacy_dir.iterdir())
    assert legacy_entries_after_third == legacy_entries_after_first, (
        "_legacy/ must not gain duplicates across repeated reads"
    )
    assert canvas_path.stat().st_mtime == canvas_mtime_after_first, (
        "canvas.json mtime must be stable on idle reads after the one-shot migration"
    )


def test_absorb_md_typed_text_into_json_preserves_md_syntax(plot_root: Path) -> None:
    """Typed field values + body retain MD syntax (bold, bullets,
    headings, newlines) verbatim."""
    raw_md_value = "**Bold** and `code`.\n\n- bullet one\n- bullet two"
    body_md = "## Long-form\n\nMore *italic* text.\n\n```python\nprint('hi')\n```"

    _seed_foundation_with_md(
        plot_root,
        "alpha",
        md_what_we_do=raw_md_value,
        md_free_prose=body_md,
    )

    doc = read_canvas(plot_root, "alpha", "foundation")
    mission = next(n for n in doc.nodes if n.kind == "mission")
    assert mission.what_we_do == raw_md_value
    # parse_md_template normalises free-prose to rstripped + trailing "\n".
    assert mission.body == body_md + "\n"


def test_absorb_md_typed_text_into_json_post_hr_text_lands_in_body(plot_root: Path) -> None:
    """The post-``---`` free-prose section maps to the new body field."""
    _seed_foundation_with_md(
        plot_root,
        "alpha",
        md_what_we_do="foo",
        md_why=None,
        md_direction=None,
        md_free_prose="long notes\n## subsection",
    )
    doc = read_canvas(plot_root, "alpha", "foundation")
    mission = next(n for n in doc.nodes if n.kind == "mission")
    assert mission.what_we_do == "foo"
    assert mission.body == "long notes\n## subsection\n"


def test_absorb_md_typed_text_into_json_duplicate_slug_collision(plot_root: Path) -> None:
    """A pre-existing _legacy entry at the same slug must not be
    overwritten; the migrator appends the short node-id suffix and
    keeps both files."""
    import json as _json

    from plot_mcp.folder_io import _canvas_file, _foundation_md_path, _legacy_md_dir
    from plot_mcp.models import CoreValueNode, IdentityNode, MissionNode

    create_project(plot_root, "alpha", "Alpha")
    canvas_path = _canvas_file(plot_root, "alpha", "foundation")

    legacy_dir = _legacy_md_dir(plot_root, "alpha")
    legacy_dir.mkdir(parents=True, exist_ok=True)
    existing = legacy_dir / "mission-mission.md"
    existing.write_text("# preexisting legacy content", encoding="utf-8")

    mission_dict = MissionNode(id="m_aaaaaaaa", label="Mission").model_dump()
    canvas_path.write_text(
        _json.dumps(
            {
                "canvas_id": "foundation",
                "canvas_kind": "foundation",
                "service_ref": None,
                "nodes": [
                    mission_dict,
                    CoreValueNode(id="cv", label="Value").model_dump(),
                    IdentityNode(id="id1", label="Persona").model_dump(),
                ],
                "edges": [],
            }
        ),
        encoding="utf-8",
    )
    md_path = _foundation_md_path(plot_root, "alpha", "mission", "m_aaaaaaaa", "Mission")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("# Mission\n\n## What we do\nnew content\n", encoding="utf-8")

    read_canvas(plot_root, "alpha", "foundation")

    assert existing.read_text(encoding="utf-8") == "# preexisting legacy content", (
        "pre-existing _legacy entry must not be overwritten"
    )
    suffixed = legacy_dir / "mission-mission-m_aaaaaa.md"
    assert suffixed.exists(), (
        f"collision-suffixed legacy file must be created; "
        f"have {sorted(p.name for p in legacy_dir.iterdir())}"
    )
    assert "new content" in suffixed.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# v0.18.0 Phase 3 (D-2026-05-16-E) — publish_node
# ---------------------------------------------------------------------------


def _foundation_mission_id(plot_root: Path, pid: str) -> str:
    """Helper: return the id of the seeded ``mission`` Foundation node."""
    canvas = read_canvas(plot_root, pid, "foundation")
    return next(n.id for n in canvas.nodes if n.kind == "mission")


def test_publish_node_writes_md_at_expected_path(plot_root: Path) -> None:
    """v0.23.0 (D-2026-05-17-I): layout is published/<kind>/<slug>/<version>.md."""
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    result = publish_node(plot_root, "alpha", "foundation", mid)
    md_full = plot_root / "alpha" / result["md_path"]
    assert md_full.is_file()
    assert md_full.name == "v2.0.md"
    # Path: foundation/published/mission/<slug>/v2.0.md
    assert result["md_path"].startswith("foundation/published/mission/")
    assert result["md_path"].endswith("/v2.0.md")


def test_publish_node_bumps_major_version(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    r1 = publish_node(plot_root, "alpha", "foundation", mid)
    assert r1["from_version"] == "v1.0" and r1["to_version"] == "v2.0"
    r2 = publish_node(plot_root, "alpha", "foundation", mid)
    assert r2["from_version"] == "v2.0" and r2["to_version"] == "v3.0"


def test_publish_node_persists_version_in_canvas_json(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)
    canvas = read_canvas(plot_root, "alpha", "foundation")
    mission = next(n for n in canvas.nodes if n.id == mid)
    assert mission.version == "v2.0"


def test_publish_node_always_bumps_on_repeat_writes_distinct_files(
    plot_root: Path,
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    r1 = publish_node(plot_root, "alpha", "foundation", mid)
    r2 = publish_node(plot_root, "alpha", "foundation", mid)
    p1 = plot_root / "alpha" / r1["md_path"]
    p2 = plot_root / "alpha" / r2["md_path"]
    assert p1.is_file() and p2.is_file()
    assert p1 != p2  # distinct filenames per publish version
    assert r1["sha"] != r2["sha"]


def test_publish_node_rejects_project_anchor(plot_root: Path) -> None:
    """Project anchor lives in ProjectDoc.anchors, not canvas.nodes.
    Attempting to publish via the canvas API surfaces as KeyError
    (anchor id not in nodes) — equivalent rejection."""
    create_project(plot_root, "alpha", "Alpha")
    with pytest.raises(KeyError):
        publish_node(plot_root, "alpha", "foundation", "__project_anchor__")


def test_publish_node_accepts_root_actor(plot_root: Path) -> None:
    """D-2026-05-19-C — actor master (is_root=True) publishes its own
    typed text directly. Replaces the pre-v0.24.10 rejection test."""
    create_project(plot_root, "alpha", "Alpha")
    actors = read_canvas(plot_root, "alpha", "actors")
    root_actor = ActorNode(id="root-actor", label="Root", is_root=True)
    new_actors = actors.model_copy(update={"nodes": [*actors.nodes, root_actor]})
    write_canvas(plot_root, "alpha", new_actors)
    result = publish_node(plot_root, "alpha", "actors", "root-actor")
    assert result["from_version"] == "v1.0"
    assert result["to_version"] == "v2.0"


# actor_ref ineligibility is unit-tested in test_md_publish.py
# (``test_can_publish_rejects_ref_kinds``); folder_io re-tests would
# need a contrived services-canvas seed (category + nested ref).


def test_publish_node_rejects_unknown_node(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    with pytest.raises(KeyError, match="not on canvas"):
        publish_node(plot_root, "alpha", "foundation", "no-such-node")


def test_publish_node_creates_git_commit_with_trailers(plot_root: Path) -> None:
    import subprocess

    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)
    project_dir = plot_root / "alpha"
    out = subprocess.run(
        ["git", "log", "--format=%s%n%b", "-1"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert out.startswith('publish: mission "Mission" → v2.0')
    assert "Publish-Node-Id: " in out
    assert "Publish-Kind: mission" in out
    assert "Publish-Canvas: foundation" in out
    assert "Publish-Version-From: v1.0" in out
    assert "Publish-Version-To: v2.0" in out


# ---------------------------------------------------------------------------
# v0.20.0 Phase 4 (D-2026-05-17-C) — MINOR propagation up ancestor chain
# ---------------------------------------------------------------------------


def _seed_services_with_step(plot_root: Path) -> tuple[str, str, str]:
    """Build a Services canvas with a category + service, plus a
    matching ServiceDetail canvas with a step node. Returns
    ``(category_id, service_id, step_id)``.

    v0.26.0 (D-2026-05-25-A) — containment is now expressed via
    directed edges instead of ``parent_id``."""
    from plot_mcp.models import SketchEdge

    def _edge(src: str, tgt: str) -> SketchEdge:
        return SketchEdge(id=f"e_{src}_{tgt}", source=src, target=tgt, directed=True)

    services = read_canvas(plot_root, "alpha", "services")
    category = CategoryNode(id="cat-acq", label="Customer Acquisition")
    service = ServiceNode(id="svc-onboarding", label="Onboarding")
    new_services = services.model_copy(
        update={
            "nodes": [category, service],
            "edges": [_edge("cat-acq", "svc-onboarding")],
        }
    )
    write_canvas(plot_root, "alpha", new_services)

    detail = CanvasDoc(
        canvas_id="svc-onboarding",
        canvas_kind="service_detail",
        service_ref="svc-onboarding",
        nodes=[
            ServiceNode(id="svc-onboarding", label="Onboarding"),
            StepNode(
                id="step-verify",
                label="Verify email",
                order=1,
            ),
            ActorRefNode(
                id="aref-user",
                ref_actor_id="user",
                side="user",
            ),
            ActorRefNode(
                id="aref-op",
                ref_actor_id="operator",
                side="operator",
            ),
        ],
        edges=[
            _edge("svc-onboarding", "step-verify"),
            _edge("svc-onboarding", "aref-user"),
            _edge("svc-onboarding", "aref-op"),
        ],
    )
    write_canvas(plot_root, "alpha", detail)
    return "cat-acq", "svc-onboarding", "step-verify"


def test_publish_step_propagates_minor_to_service_and_category(
    plot_root: Path,
) -> None:
    """Publishing a leaf step bumps the step MAJOR and propagates MINOR
    to (a) the root service mirror in detail.json, (b) the master
    service in services/canvas.json, (c) the parent category in
    services/canvas.json."""
    create_project(plot_root, "alpha", "Alpha")
    _cat, sid, step_id = _seed_services_with_step(plot_root)

    result = publish_node(plot_root, "alpha", "service_detail", step_id, service_id=sid)

    assert result["from_version"] == "v1.0"
    assert result["to_version"] == "v2.0"

    # Step itself: MAJOR-bumped in detail.json.
    detail = read_canvas(plot_root, "alpha", "service_detail", service_id=sid)
    step = next(n for n in detail.nodes if n.id == step_id)
    assert step.version == "v2.0"

    # Root service mirror in detail.json: MINOR-bumped to v1.1.
    root_service = next(n for n in detail.nodes if n.id == sid)
    assert root_service.version == "v1.1"

    # Master service in services/canvas.json: MINOR-bumped to v1.1.
    services = read_canvas(plot_root, "alpha", "services")
    master = next(n for n in services.nodes if n.id == sid)
    assert master.version == "v1.1"

    # Category in services/canvas.json: MINOR-bumped to v1.1.
    cat = next(n for n in services.nodes if n.id == "cat-acq")
    assert cat.version == "v1.1"


def test_publish_step_writes_single_commit_with_propagation_trailers(
    plot_root: Path,
) -> None:
    import subprocess

    create_project(plot_root, "alpha", "Alpha")
    _cat, sid, step_id = _seed_services_with_step(plot_root)
    publish_node(plot_root, "alpha", "service_detail", step_id, service_id=sid)

    project_dir = plot_root / "alpha"
    # Single commit since the seed (no commit), then publish (one commit).
    # Inspect the latest commit message.
    out = subprocess.run(
        ["git", "log", "--format=%s%n%b", "-1"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert out.startswith('publish: step "Verify email" → v2.0')
    # Base trailers (5) intact.
    assert "Publish-Node-Id: step-verify" in out
    assert "Publish-Kind: step" in out
    assert "Publish-Canvas: service_detail" in out
    assert "Publish-Version-From: v1.0" in out
    assert "Publish-Version-To: v2.0" in out
    # New propagation trailers — one per logical ancestor.
    propagation_lines = [
        ln for ln in out.splitlines() if ln.startswith("Publish-Propagated-Ancestor: ")
    ]
    assert len(propagation_lines) == 2
    propagated_ids = {ln.split(": ", 1)[1].split(" ", 1)[0] for ln in propagation_lines}
    assert propagated_ids == {sid, "cat-acq"}
    # The svc trailer records the v1.0→v1.1 transition.
    assert any(ln == f"Publish-Propagated-Ancestor: {sid} v1.0→v1.1" for ln in propagation_lines)
    assert any(ln == "Publish-Propagated-Ancestor: cat-acq v1.0→v1.1" for ln in propagation_lines)


def test_publish_service_propagates_to_category_only(plot_root: Path) -> None:
    """Publishing a service (not a step) MAJOR-bumps the service in both
    its files (Services master + ServiceDetail mirror) and MINOR-bumps
    the category."""
    create_project(plot_root, "alpha", "Alpha")
    _cat, sid, _step = _seed_services_with_step(plot_root)

    result = publish_node(plot_root, "alpha", "services", sid)
    assert result["to_version"] == "v2.0"

    # Master service: MAJOR-bumped.
    services = read_canvas(plot_root, "alpha", "services")
    master = next(n for n in services.nodes if n.id == sid)
    assert master.version == "v2.0"

    # Service mirror in detail.json: MAJOR-bumped (kept in sync).
    detail = read_canvas(plot_root, "alpha", "service_detail", service_id=sid)
    mirror = next(n for n in detail.nodes if n.id == sid)
    assert mirror.version == "v2.0"

    # Category: MINOR-bumped.
    cat = next(n for n in services.nodes if n.id == "cat-acq")
    assert cat.version == "v1.1"


def test_publish_foundation_node_has_no_propagation(plot_root: Path) -> None:
    """A Foundation top-level peer (mission) has no parent. Publish must
    not emit any ``Publish-Propagated-Ancestor`` trailers."""
    import subprocess

    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)

    project_dir = plot_root / "alpha"
    out = subprocess.run(
        ["git", "log", "--format=%s%n%b", "-1"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    propagation_lines = [
        ln for ln in out.splitlines() if ln.startswith("Publish-Propagated-Ancestor: ")
    ]
    assert propagation_lines == []


def test_migrate_assign_edge_relation_on_read(plot_root: Path) -> None:
    """v0.30.0 (D-2026-05-31-C) — a pre-v0.30 edge with no ``relation``
    key gets one assigned on first read via classify_edge(canvas,
    source-node kind). Idempotent: a second read does not rewrite."""
    import json

    from plot_mcp.folder_io import _canvas_file

    create_project(plot_root, "alpha", "Alpha")
    # Write a raw foundation canvas.json whose edges lack ``relation``
    # (simulating pre-v0.30 data): mission -> anchor (essence source =>
    # injection) and a non-essence edge (=> flow).
    path = _canvas_file(plot_root, "alpha", "foundation")
    raw = {
        "canvas_id": "foundation",
        "canvas_kind": "foundation",
        "nodes": [
            {"id": "m", "label": "Mission", "kind": "mission"},
            {"id": "id1", "label": "Identity", "kind": "identity"},
        ],
        "edges": [
            {"id": "e1", "source": "m", "target": "id1"},
            {"id": "e2", "source": "id1", "target": "m"},
        ],
    }
    path.write_text(json.dumps(raw), encoding="utf-8")

    doc = read_canvas(plot_root, "alpha", "foundation")
    by_id = {e.id: e for e in doc.edges}
    # mission source => injection; identity source => injection too
    # (both are essence masters on the foundation canvas).
    assert by_id["e1"].relation == "injection"
    assert by_id["e2"].relation == "injection"

    # Idempotent: a second read leaves the file's mtime unchanged.
    mtime = path.stat().st_mtime
    read_canvas(plot_root, "alpha", "foundation")
    assert path.stat().st_mtime == mtime, "second read must not rewrite"


def test_migrate_assign_edge_relation_actors_inheritance(plot_root: Path) -> None:
    """On the actors canvas every directed edge migrates to
    ``inheritance`` regardless of source kind (single edge type)."""
    import json

    from plot_mcp.folder_io import _canvas_file

    create_project(plot_root, "alpha", "Alpha")
    path = _canvas_file(plot_root, "alpha", "actors")
    raw = {
        "canvas_id": "actors",
        "canvas_kind": "actors",
        "nodes": [
            {"id": "a1", "label": "Operator", "kind": "actor"},
            {"id": "a2", "label": "User", "kind": "actor"},
        ],
        "edges": [
            {"id": "e1", "source": "a1", "target": "a2"},
        ],
    }
    path.write_text(json.dumps(raw), encoding="utf-8")

    doc = read_canvas(plot_root, "alpha", "actors")
    assert doc.edges[0].relation == "inheritance"
