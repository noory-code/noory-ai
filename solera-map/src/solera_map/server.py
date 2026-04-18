"""Combined MCP (stdio) + HTTP (localhost) server for solera-map.

The process runs a single asyncio event loop hosting:
- FastMCP stdio transport for Claude Code tool calls
- Starlette + uvicorn HTTP server for the browser-side viewer

Both share a common GraphStore that reads Solera workspace files.
"""

from __future__ import annotations

import asyncio
import sys


def run() -> None:
    """Entry point invoked by `python -m solera_map`.

    Stub: wiring is implemented incrementally in subsequent phases.
    """
    print("solera-map server stub — implementation pending", file=sys.stderr)
    asyncio.run(_serve())


async def _serve() -> None:
    # Placeholder. Real implementation will:
    #   - build GraphStore from a target project_path
    #   - launch FastMCP stdio server + uvicorn HTTP server concurrently
    #   - attach a watchdog file watcher that broadcasts changes over WebSocket
    await asyncio.sleep(0)
