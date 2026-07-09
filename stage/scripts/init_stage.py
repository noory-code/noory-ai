#!/usr/bin/env python3
"""Initialize a project-local .stage harness from the bundled templates."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "project-stage"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize the .stage project harness.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root where .stage is created. Defaults to the current directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing .stage files with template files.",
    )
    return parser.parse_args()


def copy_templates(project_root: Path, force: bool) -> tuple[list[Path], list[Path]]:
    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"Template root not found: {TEMPLATE_ROOT}")

    stage_root = project_root / ".stage"
    created: list[Path] = []
    skipped: list[Path] = []

    for template_path in sorted(TEMPLATE_ROOT.rglob("*")):
        if template_path.is_dir():
            continue

        relative_path = template_path.relative_to(TEMPLATE_ROOT)
        target_path = stage_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if target_path.exists() and not force:
            skipped.append(target_path)
            continue

        shutil.copyfile(template_path, target_path)
        created.append(target_path)

    return created, skipped


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        raise FileNotFoundError(f"Project root not found: {project_root}")
    if not project_root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {project_root}")

    created, skipped = copy_templates(project_root, args.force)

    print(f"Stage root: {project_root / '.stage'}")
    print(f"Created or updated files: {len(created)}")
    print(f"Preserved existing files: {len(skipped)}")
    for path in created:
        print(f"  write {path.relative_to(project_root)}")
    for path in skipped:
        print(f"  keep  {path.relative_to(project_root)}")


if __name__ == "__main__":
    main()
