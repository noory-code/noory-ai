"""Evonest MCP Server — FastMCP over stdio."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "evonest",
    instructions="Autonomous code evolution engine — observe, plan, execute, verify",
)

# Tool registrations are in tools/*.py — imported below
import evonest.tools.backlog  # noqa: E402, F401
import evonest.tools.config  # noqa: E402, F401
import evonest.tools.decide  # noqa: E402, F401
import evonest.tools.history  # noqa: E402, F401
import evonest.tools.identity  # noqa: E402, F401
import evonest.tools.init  # noqa: E402, F401
import evonest.tools.progress  # noqa: E402, F401
import evonest.tools.proposals  # noqa: E402, F401
import evonest.tools.analyze  # noqa: E402, F401
import evonest.tools.evolve  # noqa: E402, F401
import evonest.tools.improve  # noqa: E402, F401
import evonest.tools.run  # noqa: E402, F401
import evonest.tools.scout  # noqa: E402, F401
import evonest.tools.status  # noqa: E402, F401
import evonest.tools.stimuli  # noqa: E402, F401


def serve() -> None:
    """Start MCP server on stdio."""
    mcp.run(transport="stdio")
