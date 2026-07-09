#!/usr/bin/env python3
"""Create Stage promotion intent files (one per declared path)."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

# Intent slotting/collision rules live in the hook guard (single behavior for
# CLI-created, migrated, and split intents).
_GUARD_PATH = Path(__file__).resolve().parents[1] / "hooks" / "stage_guard.py"
_SPEC = importlib.util.spec_from_file_location("stage_guard", _GUARD_PATH)
assert _SPEC is not None and _SPEC.loader is not None
stage_guard = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("stage_guard", stage_guard)
_SPEC.loader.exec_module(stage_guard)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Stage promotion intent files.")
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

    # One intent file per (work item, path): consumption is an atomic unlink,
    # and concurrent sessions preparing different paths of the same item do
    # not overwrite each other's pending intent.
    data = {
        "type": args.type,
        "work_item": args.work_item,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    for path_value in args.path:
        target = stage_guard.write_intent_file(stage_root, data, path_value)
        if target is None:
            raise OSError(f"Could not write intent for path: {path_value}")
        print(f"Intent created: {target}")


if __name__ == "__main__":
    main()
