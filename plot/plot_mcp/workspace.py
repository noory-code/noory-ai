"""Project path → Plot root resolution + HTTP port helpers.

Pure module: no I/O at import time, no asyncio, no Starlette. Every other
module in the package depends on ``resolve_plot_root``; isolating it keeps
the import graph flat.
"""

from __future__ import annotations

import logging
import os
import socket
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plot_mcp.models import DirTreeNode, ProjectDoc

_log = logging.getLogger(__name__)

DEFAULT_HTTP_PORT = 5190

# --- Workspace discovery / directory-tree picker (v0.32.0, D-2026-05-31-L) ---
#
# Directories we never descend INTO during discovery / tree-building. ``.plot``
# is listed so we don't walk into a project's data folder, but it is still
# *read* as a marker (presence of ``<dir>/.plot/`` => a project directory).
# Any dotdir is also pruned (see ``_should_prune``).
PRUNE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        ".plot",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }
)
MAX_DISCOVERY_DEPTH = 8
MAX_DISCOVERY_PROJECTS = 500
MAX_TREE_DEPTH = 6
MAX_TREE_CHILDREN = 200


def _should_prune(name: str) -> bool:
    """Dirs we never descend into: the explicit prune set + any dotdir."""
    return name in PRUNE_DIRS or name.startswith(".")


def enumerate_projects(plot_root: Path) -> list[ProjectDoc]:
    """Read every valid project directly under a ``.plot/`` root, newest first.

    Shared by ``projects_list_endpoint``, the ``list_projects`` MCP tool, and
    ``discover_projects`` (DRY — the scan loop used to be duplicated).
    """
    from plot_mcp.folder_io import read_project

    out: list[ProjectDoc] = []
    if not plot_root.is_dir():
        return out
    for child in sorted(plot_root.iterdir()):
        if not child.is_dir() or child.name == "sketches":
            continue
        try:
            out.append(read_project(plot_root, child.name))
        except (FileNotFoundError, ValueError):
            continue
    out.sort(key=lambda p: p.updated, reverse=True)
    return out


def discover_projects(workspace_root: Path) -> list[tuple[ProjectDoc, str]]:
    """Walk ``workspace_root`` for directories containing a ``.plot/`` and
    return ``(project, relative_dir)`` for every valid project, newest first.

    ``relative_dir`` is POSIX-relative to the workspace root (``"."`` for a
    root-level project). Heavy / dot directories are pruned from descent;
    depth and total count are capped. Symlinks are not followed.
    """
    root = Path(workspace_root).expanduser().resolve()
    results: list[tuple[ProjectDoc, str]] = []
    for current, dirs, _files in os.walk(root, followlinks=False):
        cur = Path(current)
        depth = len(cur.relative_to(root).parts)
        if (cur / ".plot").is_dir():
            rel = cur.relative_to(root).as_posix() or "."
            for proj in enumerate_projects(cur / ".plot"):
                results.append((proj, rel))
            if len(results) >= MAX_DISCOVERY_PROJECTS:
                dirs[:] = []
                break
        if depth >= MAX_DISCOVERY_DEPTH:
            dirs[:] = []
        else:
            dirs[:] = sorted(d for d in dirs if not _should_prune(d))
    results.sort(key=lambda pr: pr[0].updated, reverse=True)
    return results


def build_dir_tree(workspace_root: Path, max_depth: int = MAX_TREE_DEPTH) -> DirTreeNode:
    """Build the nested directory tree for the new-project picker.

    Each node carries ``rel`` (POSIX-relative, ``"."`` for root) and
    ``has_plot``. Same prune set as discovery; depth + per-dir breadth capped.
    """
    from plot_mcp.models import DirTreeNode

    root = Path(workspace_root).expanduser().resolve()

    def node_for(path: Path, depth: int) -> DirTreeNode:
        rel = path.relative_to(root).as_posix() or "."
        children: list[DirTreeNode] = []
        if depth < max_depth:
            try:
                entries = sorted(
                    p for p in path.iterdir() if p.is_dir() and not _should_prune(p.name)
                )
            except OSError:
                entries = []
            for child in entries[:MAX_TREE_CHILDREN]:
                children.append(node_for(child, depth + 1))
        return DirTreeNode(
            name=path.name or rel,
            rel=rel,
            has_plot=(path / ".plot").is_dir(),
            children=children,
        )

    return node_for(root, 0)


def resolve_plot_root(project_path: str) -> Path:
    """Resolve ``{project_path}/.plot/``, creating it on first access.

    Plot is schema-free — any project directory can host projects. The only
    convention is the ``.plot/`` dotfolder; each project lives at
    ``.plot/{project_id}/`` with its canvas folders beneath. v0.8 dropped
    the former ``sketches/`` intermediate directory.
    """
    base = Path(project_path).expanduser().resolve()
    if not base.exists():
        raise FileNotFoundError(f"project_path does not exist: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"project_path is not a directory: {base}")
    root = base / ".plot"
    root.mkdir(exist_ok=True)
    return root


def resolved_port() -> int:
    """Read the HTTP port from ``PLOT_PORT`` with a safe fallback."""
    raw = os.environ.get("PLOT_PORT")
    if not raw:
        return DEFAULT_HTTP_PORT
    try:
        return int(raw)
    except ValueError:
        _log.warning("Invalid PLOT_PORT=%r; falling back to %d", raw, DEFAULT_HTTP_PORT)
        return DEFAULT_HTTP_PORT


def port_is_free(port: int) -> bool:
    """Best-effort check for whether ``port`` is currently bindable on loopback."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def find_viewer_dist() -> Path | None:
    """Locate ``viewer/dist/`` produced by Vite.

    Plugin runtime path: ``${CLAUDE_PLUGIN_ROOT}/viewer/dist``.
    Dev path: walk up from this file until we find ``viewer/dist/index.html``.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        candidate = Path(env) / "viewer" / "dist"
        if (candidate / "index.html").exists():
            return candidate
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "viewer" / "dist"
        if (candidate / "index.html").exists():
            return candidate
    return None
