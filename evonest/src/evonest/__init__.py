"""Evonest — Autonomous code evolution engine."""

import json
import logging
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("evonest")
except PackageNotFoundError:
    __version__ = "unknown"


def configure_logging(
    level: str = "INFO", format_type: str = "text", output: str = "stderr"
) -> None:
    """Configure logging settings.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format ("text" or "json")
        output: Log output target ("stdout", "stderr", or a file path)
    """
    logger = logging.getLogger("evonest")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    # Configure output target
    handler: logging.Handler
    if output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif output == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    else:
        # Treat as file path
        handler = logging.FileHandler(Path(output))

    # Configure formatter
    if format_type == "json":

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": self.formatTime(record, self.datefmt),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data, ensure_ascii=False)

        formatter: logging.Formatter = JsonFormatter()
    else:
        # Text format (default)
        fmt = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


_CLI_COMMANDS = {
    "init", "run", "status", "history", "progress", "config", "identity", "backlog",
    "analyze", "improve", "evolve", "personas",
}


def main() -> None:
    """Entry point: run MCP server by default, CLI if subcommand given."""
    # Load logging config from settings file (if it exists)
    try:
        from evonest.core.config import EvonestConfig

        cwd = Path.cwd()
        config = EvonestConfig.load(cwd)
        configure_logging(
            level=config.logging.level,
            format_type=config.logging.format,
            output=config.logging.output,
        )
    except Exception:
        # Use default config on settings load failure
        configure_logging()

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
