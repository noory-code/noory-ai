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

_log = logging.getLogger(__name__)

DEFAULT_HTTP_PORT = 5190


def resolve_plot_root(project_path: str) -> Path:
    """Resolve ``{project_path}/.plot/``, creating it on first access.

    Plot is schema-free — any project directory can host sketches. The only
    convention is the ``.plot/`` dotfolder. Unlike Solera, we don't require
    pre-existing content; a fresh project starts empty and writes are lazy.
    """
    base = Path(project_path).expanduser().resolve()
    if not base.exists():
        raise FileNotFoundError(f"project_path does not exist: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"project_path is not a directory: {base}")
    root = base / ".plot"
    root.mkdir(exist_ok=True)
    (root / "sketches").mkdir(exist_ok=True)
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
