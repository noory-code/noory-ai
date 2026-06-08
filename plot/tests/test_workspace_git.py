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


def test_two_projects_share_one_workspace_repo(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "proj-a", "A")
    create_project(plot_root, "proj-b", "B")
    # Exactly one repo, at the workspace root — shared by both projects.
    assert (plot_root / ".git").is_dir()
    assert not (plot_root / "proj-a" / ".git").exists()
    assert not (plot_root / "proj-b" / ".git").exists()
