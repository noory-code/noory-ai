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
    """로깅 구성을 설정합니다.

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 로그 포맷 ("text" 또는 "json")
        output: 로그 출력 대상 ("stdout", "stderr", 또는 파일 경로)
    """
    logger = logging.getLogger("evonest")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 기존 핸들러 제거
    logger.handlers.clear()

    # 출력 대상 설정
    handler: logging.Handler
    if output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif output == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    else:
        # 파일 경로로 간주
        handler = logging.FileHandler(Path(output))

    # 포맷터 설정
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
        # 텍스트 포맷 (기본)
        fmt = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


_CLI_COMMANDS = {"init", "run", "status", "history", "progress", "config", "identity", "backlog"}


def main() -> None:
    """Entry point: run MCP server by default, CLI if subcommand given."""
    # 설정 파일에서 로깅 구성 로드 (존재하는 경우)
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
        # 설정 로드 실패 시 기본 구성 사용
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
