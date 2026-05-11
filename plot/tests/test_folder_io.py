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
    read_canvas,
    read_project,
    write_canvas,
    write_project,
)
from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    ServiceNode,
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
    assert all(n.parent_id is None for n in foundation.nodes)
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
    """v0.11 — every service_detail needs ≥ 2 actor_refs."""
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
