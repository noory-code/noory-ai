#!/usr/bin/env python3
"""Create a Stage promotion intent file."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Stage promotion intent file.")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to the current directory.")
    parser.add_argument("--work-item", required=True, help="Work item ID linked to the promotion.")
    parser.add_argument("--path", action="append", required=True, help=".stage/past/ path to modify. Repeatable.")
    parser.add_argument(
        "--type",
        choices=("promotion", "archive"),
        default="promotion",
        help="Intent type. Defaults to promotion.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    stage_root = project_root / ".stage"
    if not stage_root.exists():
        raise FileNotFoundError(f"Stage root not found: {stage_root}")

    runtime_root = stage_root / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    intent_path = runtime_root / "promote-intent.json"
    data = {
        "type": args.type,
        "work_item": args.work_item,
        "paths": args.path,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    intent_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Intent created: {intent_path}")


if __name__ == "__main__":
    main()
