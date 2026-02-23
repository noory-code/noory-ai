"""Evonest — Autonomous code evolution engine."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("evonest")
except PackageNotFoundError:
    __version__ = "unknown"


_CLI_COMMANDS = {"init", "run", "status", "history", "progress", "config", "identity", "backlog"}


def main() -> None:
    """Entry point: run MCP server by default, CLI if subcommand given."""
    import sys

    if len(sys.argv) > 1 and (
        sys.argv[1] in _CLI_COMMANDS or sys.argv[1] in ("--help", "-h", "--version")
    ):
        from evonest.cli import cli_main

        if sys.argv[1] == "--version":
            print(f"evonest {__version__}")
            return
        cli_main()
    else:
        from evonest.server import serve

        serve()
