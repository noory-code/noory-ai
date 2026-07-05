"""Entry point: ``python -m rag_mcp [--probe]``."""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rag_mcp")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Print registered tools as JSON to stdout and exit",
    )
    args = parser.parse_args(argv)

    from .server import probe, serve

    if args.probe:
        sys.stdout.write(json.dumps(probe(), indent=2, ensure_ascii=False) + "\n")
        return 0
    serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
