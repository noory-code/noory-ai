"""Watcher for `.plot/sketches/*.json` → WebSocket notifications.

Only one kind of event (``sketch``) is emitted — there's no separate
`layout` channel because position is part of the sketch JSON itself.
Debounced so atomic rename-saves don't double-fire.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

_log = logging.getLogger(__name__)


def _is_sketch_file(path: str) -> bool:
    p = Path(path)
    return p.suffix == ".json" and "sketches" in p.parts


class WorkspaceWatcher:
    """Watches ``{plot_root}/sketches/`` recursively.

    ``on_change`` is awaited once per debounce window.
    """

    def __init__(
        self,
        plot_root: Path,
        on_change: Callable[[], Awaitable[None]],
        loop: asyncio.AbstractEventLoop,
        debounce_ms: int = 200,
    ) -> None:
        self._plot_root = plot_root
        self._on_change = on_change
        self._loop = loop
        self._debounce = debounce_ms / 1000.0
        self._timer: asyncio.TimerHandle | None = None
        self._observer: BaseObserver | None = None
        self._dirty = False

    def start(self) -> None:
        if self._observer is not None:
            return
        handler = _Handler(self._record)
        observer = Observer()
        target = self._plot_root / "sketches"
        target.mkdir(exist_ok=True)
        observer.schedule(handler, str(target), recursive=True)
        observer.start()
        self._observer = observer
        _log.info("watcher started on %s", target)

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._dirty = False

    def _record(self) -> None:
        self._loop.call_soon_threadsafe(self._schedule_fire)

    def _schedule_fire(self) -> None:
        self._dirty = True
        if self._timer is not None:
            self._timer.cancel()
        self._timer = self._loop.call_later(self._debounce, self._fire)

    def _fire(self) -> None:
        self._timer = None
        if not self._dirty:
            return
        self._dirty = False
        asyncio.create_task(self._safe_call())  # noqa: RUF006

    async def _safe_call(self) -> None:
        try:
            await self._on_change()
        except Exception:
            _log.exception("watcher on_change callback failed")


class _Handler(FileSystemEventHandler):
    def __init__(self, notify: Callable[[], None]) -> None:
        self._notify = notify

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = str(event.src_path)
        dest = getattr(event, "dest_path", "") or ""
        if _is_sketch_file(src) or (dest and _is_sketch_file(str(dest))):
            self._notify()
