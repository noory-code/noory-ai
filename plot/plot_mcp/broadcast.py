"""WebSocket fan-out between workspace watchers and browser clients."""

from __future__ import annotations

import asyncio
from pathlib import Path

from starlette.websockets import WebSocket

from plot_mcp.watcher import WorkspaceWatcher


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

    async def notify(self, plot_root: Path) -> None:
        """Broadcast ``sketch_changed`` to every subscriber of ``plot_root``."""
        async with self._lock:
            targets = list(self._subs.get(plot_root, ()))
        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json({"event": "sketch_changed"})
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

        async def on_change() -> None:
            await self.notify(plot_root)

        watcher = WorkspaceWatcher(plot_root, on_change=on_change, loop=loop)
        watcher.start()
        return watcher

    async def shutdown(self) -> None:
        async with self._lock:
            for watcher in self._watchers.values():
                watcher.stop()
            self._watchers.clear()
            self._subs.clear()
