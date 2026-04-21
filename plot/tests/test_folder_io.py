"""Folder-based project IO for Plot v0.2 multi-canvas.

Layout
------

    .plot/sketches/{project_id}/
      project.json                   — ProjectDoc metadata
      core.json                      — CanvasDoc (canvas_kind = "core")
      actors.json                    — CanvasDoc (canvas_kind = "actors")
      services-overview.json         — CanvasDoc (canvas_kind = "services_overview")
      services-detail/
        {service_node_id}.json       — CanvasDoc (canvas_kind = "service_detail")
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
from plot_mcp.models import CanvasDoc, SketchNode
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
    assert proj.version == 2
    folder = plot_root / "sketches" / "alpha"
    assert folder.is_dir()
    assert (folder / "project.json").is_file()
    assert (folder / "core.json").is_file()
    assert (folder / "actors.json").is_file()
    assert (folder / "services-overview.json").is_file()
    # services-detail folder may be empty but should exist for listing consistency
    assert (folder / "services-detail").is_dir()


def test_create_project_seeds_core_with_mission_and_identity(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    core = read_canvas(plot_root, "alpha", "core")
    kinds = sorted({n.kind for n in core.nodes if n.kind is not None})
    assert "core" in kinds
    assert "mission" in kinds
    assert "identity" in kinds


def test_create_project_seeds_actors_canvas_empty_root(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    actors = read_canvas(plot_root, "alpha", "actors")
    # Actors canvas can start empty — no seed node required.
    assert actors.canvas_kind == "actors"
    assert all(n.kind == "actor" for n in actors.nodes)


def test_create_project_seeds_services_overview_empty(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    overview = read_canvas(plot_root, "alpha", "services_overview")
    assert overview.canvas_kind == "services_overview"
    assert overview.nodes == []


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
            SketchNode(id="user", kind="actor", label="사용자"),
            SketchNode(id="admin", kind="actor", label="관리자"),
        ],
    )
    write_canvas(plot_root, "alpha", canvas)
    loaded = read_canvas(plot_root, "alpha", "actors")
    labels = sorted(n.label for n in loaded.nodes)
    assert labels == ["관리자", "사용자"]


def test_write_canvas_rejects_wrong_project(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    with pytest.raises(FileNotFoundError):
        write_canvas(
            plot_root,
            "ghost",
            CanvasDoc(canvas_id="actors", canvas_kind="actors"),
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


def test_write_and_list_service_detail(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    detail = CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=[SketchNode(id="order", kind="service", label="주문")],
    )
    write_canvas(plot_root, "alpha", detail)
    assert list_service_details(plot_root, "alpha") == ["order"]
    loaded = read_canvas(plot_root, "alpha", "service_detail", service_id="order")
    assert loaded.service_ref == "order"
    assert loaded.nodes[0].id == "order"


def test_detail_canvas_path_uses_service_id(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    detail = CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=[SketchNode(id="order", kind="service", label="O")],
    )
    write_canvas(plot_root, "alpha", detail)
    assert (plot_root / "sketches" / "alpha" / "services-detail" / "order.json").is_file()


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_project_removes_folder(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    delete_project(plot_root, "alpha")
    assert not (plot_root / "sketches" / "alpha").exists()


def test_delete_missing_project_raises(plot_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        delete_project(plot_root, "never-existed")


# ---------------------------------------------------------------------------
# git repo wiring (v0.4)
# ---------------------------------------------------------------------------


def test_create_project_initialises_git_repo(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    assert (plot_root / "sketches" / "alpha" / ".git").is_dir()


def test_create_project_leaves_git_repo_empty(plot_root: Path) -> None:
    """Quiet-repo principle: no automatic commits, HEAD doesn't resolve."""
    import subprocess

    create_project(plot_root, "alpha", "Alpha")
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=plot_root / "sketches" / "alpha",
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
            nodes=[SketchNode(id="u", kind="actor", label="U")],
        ),
    )
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=plot_root / "sketches" / "alpha",
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0  # still no commits
