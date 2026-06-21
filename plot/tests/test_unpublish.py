"""v0.23.x (D-2026-05-17-J) — unpublish endpoint + server function tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from plot_mcp.folder_io import (
    UnpublishNotEligibleError,
    create_project,
    publish_node,
    read_canvas,
    unpublish_node,
)
from plot_mcp.http_app import create_http_app


@pytest.fixture()
def plot_root(tmp_path: Path) -> Path:
    # D-2026-06-11-C/D: workspace is the user's opened folder and IS the
    # git repo; .noory/plot/ lives inside it. Plot never auto-inits — but
    # tests that exercise publish/tag need a real repo, so we init here.
    from plot_mcp.git_store import init_workspace_repo
    from plot_mcp.workspace import resolve_plot_root
    init_workspace_repo(tmp_path)
    return resolve_plot_root(str(tmp_path))


@pytest.fixture()
def client(plot_root: Path) -> TestClient:
    app = create_http_app()
    return TestClient(app)


def _foundation_mission_id(plot_root: Path, project_id: str) -> str:
    canvas = read_canvas(plot_root, project_id, "foundation")
    return next(n.id for n in canvas.nodes if n.kind == "mission")


# ---------------------------------------------------------------------------
# unpublish_node (server function)
# ---------------------------------------------------------------------------


def test_unpublish_reverts_the_version_bump(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)  # v1.0 → v2.0

    result = unpublish_node(plot_root, "alpha", "foundation", mid)
    assert result["from_version"] == "v2.0"
    assert result["to_version"] == "v1.0"
    canvas_after = read_canvas(plot_root, "alpha", "foundation")
    mission_after = next(n for n in canvas_after.nodes if n.id == mid)
    assert mission_after.version == "v1.0"


def test_unpublish_removes_the_published_md_file(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)
    md_path = (
        plot_root / "foundation" / "published" / "mission" / "mission" / "v2.0.md"
    )
    assert md_path.is_file()

    unpublish_node(plot_root, "alpha", "foundation", mid)
    assert not md_path.exists()


def test_unpublish_writes_a_revert_commit(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)

    project_dir = plot_root
    sha_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    unpublish_node(plot_root, "alpha", "foundation", mid)

    sha_after = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert sha_after != sha_before
    subject = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    # `git revert` default subject starts with "Revert "
    assert subject.startswith("Revert ")


def test_unpublish_raises_when_node_never_published(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    with pytest.raises(UnpublishNotEligibleError):
        unpublish_node(plot_root, "alpha", "foundation", mid)


def test_unpublish_raises_keyerror_for_unknown_node(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    with pytest.raises(KeyError):
        unpublish_node(plot_root, "alpha", "foundation", "ghost")


# ---------------------------------------------------------------------------
# HTTP endpoint
# ---------------------------------------------------------------------------


def test_unpublish_endpoint_round_trip(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    client.post(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/publish",
        params={"project_path": str(plot_root.parent.parent)},
    )
    resp = client.post(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/unpublish",
        params={"project_path": str(plot_root.parent.parent)},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["from_version"] == "v2.0"
    assert body["to_version"] == "v1.0"
    assert len(body["reverted_sha"]) >= 7
    assert len(body["revert_commit_sha"]) >= 7


def test_unpublish_endpoint_409_when_no_publish_to_revert(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    resp = client.post(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/unpublish",
        params={"project_path": str(plot_root.parent.parent)},
    )
    assert resp.status_code == 409


def test_unpublish_endpoint_404_for_unknown_node(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    resp = client.post(
        "/api/projects/alpha/canvases/foundation/nodes/ghost/unpublish",
        params={"project_path": str(plot_root.parent.parent)},
    )
    assert resp.status_code == 404
