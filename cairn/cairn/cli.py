"""The Cairn command line — record and query decisions.

``--root`` is the project directory; the log lives at ``.noory/cairn/`` under it.
A decision's body (the prose) is passed with ``--body`` or piped on stdin.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import CairnError
from .log import Log


def _log(root: Path) -> Log:
    return Log(root / ".noory" / "cairn")


def _cmd_record(log: Log, args: argparse.Namespace) -> int:
    body = args.body if args.body is not None else sys.stdin.read()
    decision = log.record(
        args.title, body, status=args.status, supersedes=args.supersedes
    )
    print(decision.id)
    return 0


def _cmd_list(log: Log, args: argparse.Namespace) -> int:
    for decision in log.decisions():
        print(f"{decision.id}  [{decision.status}]  {decision.title}")
    return 0


def _cmd_in_force(log: Log, args: argparse.Namespace) -> int:
    for decision in log.in_force():
        print(f"{decision.id}  {decision.title}")
    return 0


def _cmd_show(log: Log, args: argparse.Namespace) -> int:
    decision = log.get(args.id)
    print(f"# {decision.id}  [{decision.status}]  {decision.title}")
    if decision.supersedes:
        print(f"supersedes: {decision.supersedes}")
    print()
    print(decision.body)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cairn", description="An append-only decision log.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project directory")
    sub = parser.add_subparsers(dest="command", required=True)

    p_record = sub.add_parser("record", help="append a new decision")
    p_record.add_argument("title")
    p_record.add_argument("--status", choices=["proposed", "accepted"], default="accepted")
    p_record.add_argument("--supersedes", default=None, help="id of a decision this replaces")
    p_record.add_argument("--body", default=None, help="decision prose (else read from stdin)")
    p_record.set_defaults(func=_cmd_record)

    p_list = sub.add_parser("list", help="list every decision")
    p_list.set_defaults(func=_cmd_list)

    p_in_force = sub.add_parser("in-force", help="list decisions still in force")
    p_in_force.set_defaults(func=_cmd_in_force)

    p_show = sub.add_parser("show", help="print one decision")
    p_show.add_argument("id")
    p_show.set_defaults(func=_cmd_show)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result: int = args.func(_log(Path(args.root)), args)
    except CairnError as exc:
        print(f"error: {exc}")
        return 1
    return result
