"""D-2026-06-09-C — git lives at the workspace (.plot/), not per project.

The per-project git repo (one .git per .plot/{project_id}) is replaced by a
single workspace-level repo at .plot/. One workspace = one history = N
projects (user: "워크스페이스에만 깃이 있어야 한다").

This pins the boundary: create_project must init/reuse the single repo at
plot_root (= {project_path}/.plot), and must NOT create a per-project .git.
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.folder_io import create_project
from plot_mcp.workspace import resolve_plot_root


def test_git_inits_at_workspace_not_per_project(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "proj-a", "A")
    # The single repo lives at the workspace (.plot/).
    assert (plot_root / ".git").is_dir()
    # And there is NO per-project repo.
    assert not (plot_root / "proj-a" / ".git").exists()


def test_tag_endpoints_target_the_workspace_repo(tmp_path: Path) -> None:
    """D-2026-06-10-H — v0.53.0 missed the tag/at-tag/publish endpoint call
    sites: they still passed `plot_root / project_id` to git ops, and
    `tag_snapshot`'s self-heal silently re-created a PER-PROJECT repo. Tags
    must land in the single workspace repo; no per-project .git may appear."""
    from starlette.testclient import TestClient

    from plot_mcp.broadcast import BroadcastHub
    from plot_mcp.git_store import list_tags
    from plot_mcp.http_app import create_http_app

    client = TestClient(create_http_app(hub=BroadcastHub(enable_watchers=False)))
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "proj-a", "A")

    r = client.post(
        "/api/projects/proj-a/tags",
        params={"project_path": str(tmp_path)},
        json={"name": "session-1"},
    )
    assert r.status_code == 201
    # The tag lives in the WORKSPACE repo…
    assert "session-1" in [t["name"] for t in list_tags(plot_root)]
    # …and no per-project repo was self-healed into existence.
    assert not (plot_root / "proj-a" / ".git").exists()
    # The list endpoint reads the same workspace repo.
    listed = client.get(
        "/api/projects/proj-a/tags", params={"project_path": str(tmp_path)}
    )
    assert "session-1" in [t["name"] for t in listed.json()["tags"]]


def test_at_tag_reads_project_files_from_the_workspace_repo(tmp_path: Path) -> None:
    """Files in the workspace repo sit under `{project_id}/…`, so the at-tag
    reader must prefix paths with the project id."""
    from starlette.testclient import TestClient

    from plot_mcp.broadcast import BroadcastHub
    from plot_mcp.http_app import create_http_app

    client = TestClient(create_http_app(hub=BroadcastHub(enable_watchers=False)))
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "proj-a", "A")
    client.post(
        "/api/projects/proj-a/tags",
        params={"project_path": str(tmp_path)},
        json={"name": "snap-1"},
    )
    r = client.get(
        "/api/projects/proj-a/at-tag/snap-1",
        params={"project_path": str(tmp_path)},
    )
    assert r.status_code == 200, r.text
    assert r.json()["project"]["id"] == "proj-a"


def test_two_projects_share_one_workspace_repo(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "proj-a", "A")
    create_project(plot_root, "proj-b", "B")
    # Exactly one repo, at the workspace root — shared by both projects.
    assert (plot_root / ".git").is_dir()
    assert not (plot_root / "proj-a" / ".git").exists()
    assert not (plot_root / "proj-b" / ".git").exists()
