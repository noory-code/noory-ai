#!/usr/bin/env python3
"""Refresh project-local Stage guidance from the current plugin templates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import guidance_docs  # noqa: E402
import init_stage  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh .stage guidance from the current localized templates."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing .stage. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the refresh plan without changing files.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=(
            "Guidance paths relative to .stage. Omit to refresh safe defaults; files whose "
            "templates contain populated tables are replaced only when named explicitly."
        ),
    )
    return parser.parse_args(argv)


def _selected_paths(raw_paths: list[str], available: set[Path]) -> tuple[list[Path], list[str]]:
    selected: list[Path] = []
    errors: list[str] = []
    for raw_path in raw_paths:
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts or relative not in available:
            errors.append(
                f"unknown guidance path: {raw_path} (use a template-backed path relative to .stage)"
            )
            continue
        if relative not in selected:
            selected.append(relative)
    return selected, errors


def refresh_project(
    project_root: Path,
    raw_paths: list[str],
    *,
    dry_run: bool,
) -> int:
    stage_root = project_root / ".stage"
    if not stage_root.is_dir():
        print(f"error: Stage root not found: {stage_root}")
        return 1

    available_paths = guidance_docs.guidance_paths()
    available = set(available_paths)
    selected, errors = _selected_paths(raw_paths, available)
    for error in errors:
        print(f"error: {error}")
    if errors:
        return 1

    explicitly_selected = bool(raw_paths)
    candidates = selected if explicitly_selected else available_paths
    settings = guidance_docs.load_settings(stage_root)
    raw_overrides = settings.get("guidance_overrides", [])
    overrides = (
        {Path(value) for value in raw_overrides}
        if isinstance(raw_overrides, list)
        and all(isinstance(value, str) for value in raw_overrides)
        else set()
    )
    language = guidance_docs.project_language(stage_root)
    refused = False

    for relative in candidates:
        if not explicitly_selected and relative in overrides:
            print(f"skipped {relative.as_posix()} (declared guidance override)")
            continue

        template_path = guidance_docs.localized_template(relative, language)
        template_text = template_path.read_text(encoding="utf-8")
        target = stage_root / relative
        project_text = target.read_text(encoding="utf-8") if target.is_file() else None
        plan = guidance_docs.plan_refresh(
            template_text,
            project_text,
            selected=explicitly_selected,
        )

        display = relative.as_posix()
        if plan.action == "refused":
            refused = True
            print(f"refused {display} ({plan.reason})")
            continue
        if plan.action == "skipped":
            print(f"skipped {display} ({plan.reason})")
            continue
        assert plan.content is not None
        if project_text == plan.content:
            print(f"unchanged {display}")
            continue
        if dry_run:
            print(f"would refresh {display}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(plan.content, encoding="utf-8")
        print(f"refreshed {display}")

    return 1 if refused else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return refresh_project(
        Path(args.project_root).resolve(),
        args.paths,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
