"""WebSocket fan-out between workspace watchers and browser clients."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from starlette.websockets import WebSocket

from plot_mcp.watcher import WorkspaceWatcher

_SINGLETON_CANVAS_KINDS = {"foundation", "actors", "services"}


def _describe_change(plot_root: Path, changed_path: Path) -> dict[str, Any] | None:
    """Map a changed file to ``{project_id, canvas_kind?, service_id?}``.

    v0.8 layout:
      - ``{project_id}/{canvas_kind}/canvas.json`` for singleton canvases
      - ``{project_id}/services/{service_id}/detail.json`` for details
      - ``{project_id}/project.json`` for project metadata

    Returns ``None`` for anything else (attachments, leftover files, etc.).
    """
    try:
        rel = changed_path.relative_to(plot_root)
    except ValueError:
        return None
    parts = rel.parts
    if not parts:
        return None
    project_id = parts[0]
    descriptor: dict[str, Any] = {"project_id": project_id}
    # parts examples:
    #   ("alpha", "project.json")
    #   ("alpha", "foundation", "canvas.json")
    #   ("alpha", "services", "canvas.json")
    #   ("alpha", "services", "order", "detail.json")
    #   ("alpha", "foundation", "mission-1", "details.md")
    #   ("alpha", "services", "order", "details.md")
    if len(parts) == 3 and parts[2] == "canvas.json" and parts[1] in _SINGLETON_CANVAS_KINDS:
        descriptor["canvas_kind"] = parts[1]
    elif len(parts) == 4 and parts[1] == "services" and parts[3] == "detail.json":
        descriptor["canvas_kind"] = "service_detail"
        descriptor["service_id"] = parts[2]
    elif len(parts) == 4 and parts[3] == "details.md" and parts[1] in _SINGLETON_CANVAS_KINDS:
        # v0.9 per-node details.md: a viewer that has the parent canvas
        # open should reload to pick up external edits.
        descriptor["canvas_kind"] = parts[1]
    elif len(parts) == 4 and parts[1] == "services" and parts[3] == "details.md":
        # services/{sid}/details.md — service node's long-form. Reloading
        # the services top-view is enough because the details file is
        # only fetched lazily by the Inspector when the service is selected.
        descriptor["canvas_kind"] = "services"
    elif len(parts) == 3 and parts[1] == "foundation" and parts[2].endswith(".md"):
        # v0.13 Phase 4: per-node MD template under foundation/ — any
        # .md file directly under the foundation/ folder belongs to a
        # foundation node. Reloading the foundation canvas is enough
        # since the API merges typed text from these files on read.
        descriptor["canvas_kind"] = "foundation"
    # project.json and anything else → project-level event without canvas_kind
    return descriptor


class BroadcastHub:
    """One watcher per plot_root, created on first subscription.

    Tests that don't want a real filesystem watcher may pass
    ``enable_watchers=False``; ``notify`` still fans out to subscribers.
    """

    def __init__(self, *, enable_watchers: bool = True) -> None:
        self._subs: dict[Path, set[WebSocket]] = {}
        self._watchers: dict[Path, WorkspaceWatcher] = {}
        self._lock = asyncio.Lock()
        self._enable_watchers = enable_watchers

    async def subscribe(self, ws: WebSocket, plot_root: Path) -> None:
        async with self._lock:
            if plot_root not in self._subs:
                self._subs[plot_root] = set()
                if self._enable_watchers:
                    self._watchers[plot_root] = self._start_watcher(plot_root)
            self._subs[plot_root].add(ws)

    async def unsubscribe(self, ws: WebSocket, plot_root: Path) -> None:
        async with self._lock:
            subs = self._subs.get(plot_root)
            if subs is None:
                return
            subs.discard(ws)
            if not subs:
                self._subs.pop(plot_root, None)
                watcher = self._watchers.pop(plot_root, None)
                if watcher is not None:
                    watcher.stop()

    async def notify(self, plot_root: Path, payload: dict[str, Any] | None = None) -> None:
        """Broadcast a ``project_changed`` event to every subscriber of ``plot_root``.

        ``payload`` is the ``{project_id, canvas_kind?, service_id?}``
        descriptor produced by ``_describe_change``. ``None`` is treated
        as a generic project-level event.
        """
        await self.notify_event(plot_root, "project_changed", payload)

    async def notify_event(
        self,
        plot_root: Path,
        event_name: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Broadcast an arbitrary event to subscribers of ``plot_root``.

        Generalisation of :meth:`notify` introduced for R7 chat
        (D-2026-06-12-D): the WS room is shared between project-change
        events and chat-stream events, demultiplexed by ``event`` on the
        viewer side.
        """
        body: dict[str, Any] = {"event": event_name}
        if payload:
            body.update(payload)
        async with self._lock:
            targets = list(self._subs.get(plot_root, ()))
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(body)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                subs = self._subs.get(plot_root)
                if subs is not None:
                    for ws in dead:
                        subs.discard(ws)

    def subscription_count(self, plot_root: Path) -> int:
        return len(self._subs.get(plot_root, ()))

    def _start_watcher(self, plot_root: Path) -> WorkspaceWatcher:
        loop = asyncio.get_running_loop()

        async def on_change(paths: set[Path]) -> None:
            # Group by descriptor so two writes to the same canvas
            # within a debounce window fire one event, not two.
            descriptors: dict[tuple[str, str, str | None], dict[str, Any]] = {}
            for p in paths:
                d = _describe_change(plot_root, p)
                if d is None:
                    continue
                key = (
                    d["project_id"],
                    d.get("canvas_kind", ""),
                    d.get("service_id"),
                )
                descriptors.setdefault(key, d)
            if not descriptors:
                await self.notify(plot_root)  # generic fallback
                return
            for d in descriptors.values():
                await self.notify(plot_root, d)

        watcher = WorkspaceWatcher(plot_root, on_change=on_change, loop=loop)
        watcher.start()
        return watcher

    async def shutdown(self) -> None:
        async with self._lock:
            for watcher in self._watchers.values():
                watcher.stop()
            self._watchers.clear()
            self._subs.clear()
