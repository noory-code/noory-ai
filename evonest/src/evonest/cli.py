"""Evonest CLI — thin wrapper over core/ modules."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path


def cli_main() -> None:
    """CLI entry point."""
    # Logging setup — EVONEST_LOG_LEVEL=DEBUG to enable debug output
    log_level = os.environ.get("EVONEST_LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        prog="evonest",
        description="Autonomous code evolution engine",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    init_p = sub.add_parser("init", help="Initialize .evonest/ in a project")
    init_p.add_argument("path", help="Path to the target project")
    init_p.add_argument(
        "--level",
        choices=["quick", "standard", "deep"],
        default=None,
        help="Analysis depth level (skips interactive prompt if provided)",
    )

    # run
    run_p = sub.add_parser("run", help="Run evolution cycles")
    run_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    run_p.add_argument("--cycles", "-c", type=int, help="Number of cycles")
    run_p.add_argument("--dry-run", action="store_true", help="Dry run mode")
    run_p.add_argument("--no-meta", action="store_true", help="Skip meta-observe")
    run_p.add_argument("--no-scout", action="store_true", help="Skip scout phase")
    run_p.add_argument(
        "--observe-mode",
        choices=["auto", "quick", "deep"],
        default=None,
        help="Observe depth: quick (sampled), deep (comprehensive), auto (default)",
    )
    run_p.add_argument(
        "--persona", default=None, help="Force persona ID (e.g. product-strategist, architect)"
    )
    run_p.add_argument(
        "--adversarial",
        default=None,
        help="Force adversarial ID (e.g. corrupt-state), or 'none' to disable",
    )
    run_p.add_argument(
        "--group", default=None, help="Persona group to sample from (biz, tech, quality)"
    )
    run_p.add_argument(
        "--all-personas",
        action="store_true",
        help="Run every persona exactly once (in order). Overrides --cycles.",
    )

    # analyze
    analyze_p = sub.add_parser(
        "analyze", help="Observe-only: save all improvements as proposals (no code changes)"
    )
    analyze_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    analyze_p.add_argument("--persona", default=None, help="Force persona ID")
    analyze_p.add_argument(
        "--adversarial", default=None, help="Force adversarial ID, or 'none' to disable"
    )
    analyze_p.add_argument(
        "--group", default=None, help="Persona group filter (biz, tech, quality)"
    )
    analyze_p.add_argument(
        "--all-personas",
        action="store_true",
        help="Run every persona once (each produces its own batch of proposals)",
    )
    analyze_p.add_argument(
        "--observe-mode",
        choices=["auto", "quick", "deep"],
        default=None,
        help="Observe depth",
    )
    analyze_p.add_argument(
        "--level",
        choices=["quick", "standard", "deep"],
        default=None,
        help="Analysis depth preset: quick (haiku), standard (sonnet), deep (opus)",
    )

    # improve
    improve_p = sub.add_parser(
        "improve", help="Execute a proposal: select → Execute → Verify → commit/PR"
    )
    improve_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    improve_p.add_argument(
        "--proposal-id",
        default=None,
        help="Bare filename of proposal to execute (auto-selects by priority+age if omitted)",
    )

    # evolve
    evolve_p = sub.add_parser(
        "evolve", help="Full evolution: Observe → Plan → Execute → Verify → commit/PR"
    )
    evolve_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    evolve_p.add_argument("--cycles", "-c", type=int, help="Number of cycles")
    evolve_p.add_argument("--no-meta", action="store_true", help="Skip meta-observe")
    evolve_p.add_argument("--no-scout", action="store_true", help="Skip scout phase")
    evolve_p.add_argument(
        "--observe-mode", choices=["auto", "quick", "deep"], default=None, help="Observe depth"
    )
    evolve_p.add_argument("--persona", default=None, help="Force persona ID")
    evolve_p.add_argument(
        "--adversarial", default=None, help="Force adversarial ID, or 'none' to disable"
    )
    evolve_p.add_argument(
        "--group", default=None, help="Persona group filter (biz, tech, quality)"
    )
    evolve_p.add_argument(
        "--all-personas",
        action="store_true",
        help="Run every persona exactly once. Overrides --cycles.",
    )
    evolve_p.add_argument(
        "--cautious",
        action="store_true",
        help="Pause after Plan, show plan summary, prompt [y/N] before Execute",
    )
    evolve_p.add_argument(
        "--level",
        choices=["quick", "standard", "deep"],
        default=None,
        help="Analysis depth preset: quick (haiku), standard (sonnet), deep (opus)",
    )

    # status
    status_p = sub.add_parser("status", help="Show project status")
    status_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")

    # history
    hist_p = sub.add_parser("history", help="Show cycle history")
    hist_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    hist_p.add_argument("--count", "-n", type=int, default=10, help="Number of entries")

    # progress
    prog_p = sub.add_parser("progress", help="Show detailed progress")
    prog_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")

    # config
    config_p = sub.add_parser("config", help="View/update project config")
    config_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    config_p.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a config value")

    # identity
    id_p = sub.add_parser("identity", help="View/update project identity")
    id_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    id_p.add_argument("--set", metavar="FILE", help="Replace identity from file")
    id_p.add_argument("--refresh", action="store_true", help="Re-draft identity.md using Claude (shows diff, prompts for confirmation)")

    # backlog
    bl_p = sub.add_parser("backlog", help="Manage improvement backlog")
    bl_p.add_argument("project", nargs="?", default=None, help="Project path (default: cwd)")
    bl_p.add_argument(
        "action",
        nargs="?",
        default="list",
        choices=["list", "add", "remove", "prune"],
        help="Action to perform",
    )
    bl_p.add_argument("--title", help="Title for add action")
    bl_p.add_argument("--priority", default="medium", help="Priority for add action")
    bl_p.add_argument("--id", dest="item_id", help="Item ID for remove action")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        _dispatch(args)
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _resolve_project(project: str | None) -> str:
    """Resolve project path.

    Priority:
    1. Explicit argument
    2. EVONEST_PROJECT environment variable
    3. Walk up from cwd looking for .evonest/

    Raises FileNotFoundError if no .evonest/ found.
    """
    if project is not None:
        return project
    env = os.environ.get("EVONEST_PROJECT")
    if env:
        return env
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".evonest").is_dir():
            return str(parent)
    raise FileNotFoundError(
        "No .evonest/ found in current directory or any parent. "
        "Run: evonest init <path>"
    )


def _prompt_level() -> str:
    """Interactive level selection for `evonest init`.

    Returns one of: "quick", "standard", "deep".
    Defaults to "standard" on empty input or non-interactive environments.
    """
    choices = {
        "1": "quick",
        "2": "standard",
        "3": "deep",
    }
    prompt = (
        "\nSelect analysis depth level:\n"
        "  [1] quick    — fast scan, haiku model\n"
        "  [2] standard — balanced (default)\n"
        "  [3] deep     — thorough, opus model\n"
        "Choice [2]: "
    )
    try:
        answer = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        answer = ""
    return choices.get(answer, "standard")


def _dispatch(args: argparse.Namespace) -> None:
    """Route parsed arguments to core functions."""
    if args.command == "init":
        from evonest.core.initializer import init_project

        level = getattr(args, "level", None)
        if level is None:
            level = _prompt_level()
        print(init_project(args.path, level=level))

    elif args.command == "analyze":
        from evonest.core.orchestrator import run_analyze

        result = asyncio.run(
            run_analyze(
                project=_resolve_project(args.project),
                persona_id=args.persona,
                adversarial_id=args.adversarial,
                group=args.group,
                all_personas=args.all_personas,
                observe_mode=args.observe_mode,
                level=getattr(args, "level", None),
            )
        )
        print(result)

    elif args.command == "improve":
        from evonest.core.improve import run_improve

        result = asyncio.run(
            run_improve(
                project=_resolve_project(args.project),
                proposal_id=args.proposal_id,
            )
        )
        print(result)

    elif args.command == "evolve":
        from evonest.core.orchestrator import run_cycles
        from evonest.core.state import ProjectState

        _level = getattr(args, "level", None)
        _project = _resolve_project(args.project)
        if args.cautious:
            # Run Plan phase first
            plan_result = asyncio.run(
                run_cycles(
                    project=_project,
                    cycles=args.cycles,
                    no_meta=args.no_meta,
                    no_scout=args.no_scout,
                    observe_mode=args.observe_mode,
                    persona_id=args.persona,
                    adversarial_id=args.adversarial,
                    group=args.group,
                    all_personas=args.all_personas,
                    cautious=True,
                    level=_level,
                )
            )
            print(plan_result)
            if "CAUTIOUS MODE" in plan_result:
                try:
                    answer = input("\nProceed with Execute? [y/N]: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    answer = "n"
                if answer == "y":
                    resume_result = asyncio.run(run_cycles(project=_project, resume=True))
                    print(resume_result)
                else:
                    state = ProjectState(_project)
                    state.clear_pending()
                    print("Cancelled. No changes made.")
        else:
            result = asyncio.run(
                run_cycles(
                    project=_project,
                    cycles=args.cycles,
                    no_meta=args.no_meta,
                    no_scout=args.no_scout,
                    observe_mode=args.observe_mode,
                    persona_id=args.persona,
                    adversarial_id=args.adversarial,
                    group=args.group,
                    all_personas=args.all_personas,
                    cautious=False,
                    level=_level,
                )
            )
            print(result)

    elif args.command == "run":
        print(
            "WARNING: `evonest run` is deprecated. Use `evonest evolve` instead.",
            file=sys.stderr,
        )
        from evonest.core.orchestrator import run_cycles

        result = asyncio.run(
            run_cycles(
                project=_resolve_project(args.project),
                cycles=args.cycles,
                dry_run=args.dry_run,
                no_meta=args.no_meta,
                no_scout=args.no_scout,
                observe_mode=args.observe_mode,
                persona_id=args.persona,
                adversarial_id=args.adversarial,
                group=args.group,
                all_personas=args.all_personas,
            )
        )
        print(result)

    elif args.command == "status":
        from evonest.core.state import ProjectState

        state = ProjectState(_resolve_project(args.project))
        print(state.summary())

    elif args.command == "history":
        from evonest.core.history import get_recent_history

        print(get_recent_history(_resolve_project(args.project), args.count))

    elif args.command == "progress":
        from evonest.core.progress import get_progress_report

        print(get_progress_report(_resolve_project(args.project)))

    elif args.command == "config":
        from evonest.core.config import EvonestConfig

        cfg = EvonestConfig.load(_resolve_project(args.project))
        if args.set:
            try:
                cfg.set(args.set[0], args.set[1])
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            cfg.save()
            print(f"Set {args.set[0]} = {args.set[1]}")
        else:
            print(cfg.to_json())

    elif args.command == "identity":
        from evonest.core.state import ProjectState

        project_path = _resolve_project(args.project)
        state = ProjectState(project_path)
        if getattr(args, "refresh", False):
            from evonest.core.initializer import _draft_identity_via_claude

            print("Analyzing project to draft updated identity.md...")
            draft = _draft_identity_via_claude(Path(project_path))
            if not draft:
                print(
                    "Error: Could not generate draft (claude unavailable?)",
                    file=sys.stderr,
                )
                sys.exit(1)
            current = state.read_identity()
            print("--- Current identity.md ---")
            print(current)
            print("\n--- Proposed identity.md ---")
            print(draft)
            try:
                answer = input("\nUpdate identity? [y/N]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"
            if answer == "y":
                state.write_identity(draft)
                print("Identity updated.")
            else:
                print("Cancelled. No changes made.")
        elif args.set:
            content = Path(args.set).read_text(encoding="utf-8")
            state.write_identity(content)
            print("Identity updated.")
        else:
            print(state.read_identity())

    elif args.command == "backlog":
        from evonest.core.backlog import manage_backlog

        # Infer 'add' when --title is provided but action defaults to 'list'
        if args.title and args.action == "list":
            args.action = "add"

        item = None
        if args.action == "add" and args.title:
            item = {"title": args.title, "priority": args.priority}
        elif args.action == "remove" and args.item_id:
            item = {"id": args.item_id}
        print(manage_backlog(_resolve_project(args.project), args.action, item))
