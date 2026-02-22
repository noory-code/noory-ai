"""Background subprocess entry point for evonest operations.

Called by MCP tools via subprocess.Popen so long-running operations
(analyze / evolve / improve) run detached from the MCP server process.

Usage:
    python -m evonest._runner analyze <project> [--persona-id X] [--group G]
                                                 [--adversarial-id A] [--level L]
                                                 [--observe-mode M] [--all-personas]
    python -m evonest._runner evolve  <project> [--cycles N] [--no-meta] [--no-scout]
                                                 [--cautious] [--level L] ...
    python -m evonest._runner improve <project> [--proposal-id P]
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path


def _setup_logging(log_path: Path) -> None:
    """Configure root evonest logger to write to log_path (overwrite each run)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    root = logging.getLogger("evonest")
    root.setLevel(logging.DEBUG)
    root.handlers.clear()
    root.addHandler(handler)
    # Also print to stderr so the spawning process can redirect if needed
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
    root.addHandler(stderr_handler)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evonest._runner")
    sub = parser.add_subparsers(dest="command", required=True)

    # analyze
    p_analyze = sub.add_parser("analyze")
    p_analyze.add_argument("project")
    p_analyze.add_argument("--persona-id")
    p_analyze.add_argument("--adversarial-id")
    p_analyze.add_argument("--group")
    p_analyze.add_argument("--all-personas", action="store_true")
    p_analyze.add_argument("--observe-mode")
    p_analyze.add_argument("--level")

    # evolve
    p_evolve = sub.add_parser("evolve")
    p_evolve.add_argument("project")
    p_evolve.add_argument("--cycles", type=int)
    p_evolve.add_argument("--no-meta", action="store_true")
    p_evolve.add_argument("--no-scout", action="store_true")
    p_evolve.add_argument("--observe-mode")
    p_evolve.add_argument("--persona-id")
    p_evolve.add_argument("--adversarial-id")
    p_evolve.add_argument("--group")
    p_evolve.add_argument("--all-personas", action="store_true")
    p_evolve.add_argument("--cautious", action="store_true")
    p_evolve.add_argument("--level")

    # improve
    p_improve = sub.add_parser("improve")
    p_improve.add_argument("project")
    p_improve.add_argument("--proposal-id")

    return parser


async def _run(args: argparse.Namespace) -> str:
    if args.command == "analyze":
        from evonest.core.orchestrator import run_analyze

        return await run_analyze(
            project=args.project,
            persona_id=args.persona_id,
            adversarial_id=args.adversarial_id,
            group=args.group,
            all_personas=args.all_personas,
            observe_mode=args.observe_mode,
            level=args.level,
        )

    if args.command == "evolve":
        from evonest.core.orchestrator import run_cycles

        return await run_cycles(
            project=args.project,
            cycles=args.cycles,
            no_meta=args.no_meta,
            no_scout=args.no_scout,
            observe_mode=args.observe_mode,
            persona_id=args.persona_id,
            adversarial_id=args.adversarial_id,
            group=args.group,
            all_personas=args.all_personas,
            cautious=args.cautious,
            level=args.level,
        )

    if args.command == "improve":
        from evonest.core.improve import run_improve

        return await run_improve(
            project=args.project,
            proposal_id=args.proposal_id,
        )

    raise ValueError(f"Unknown command: {args.command}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    project = Path(args.project)
    log_path = project / ".evonest" / "logs" / "current.log"
    _setup_logging(log_path)

    logger = logging.getLogger("evonest")
    proj_name = project.name
    logger.info("evonest %s started for %s", args.command, proj_name)

    from evonest.core.notify import notify

    try:
        result = asyncio.run(_run(args))
        logger.info("evonest %s completed:\n%s", args.command, result)
        notify(f"Evonest [{proj_name}] — {args.command} ✅", result[:100])
    except Exception as exc:
        logger.error("evonest %s failed: %s", args.command, exc, exc_info=True)
        notify(f"Evonest [{proj_name}] — {args.command} ❌", str(exc)[:100])
        sys.exit(1)


if __name__ == "__main__":
    main()
