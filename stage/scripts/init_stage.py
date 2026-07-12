#!/usr/bin/env python3
"""Initialize a project-local .stage harness from the bundled templates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
LOCALE_ROOT = PLUGIN_ROOT / "templates" / "locales"
# Same contract as stage_paths.LANGUAGE_TAG_RE; duplicated literal only because
# this script must stay runnable standalone before any .stage exists.
LANGUAGE_TAG_RE = re.compile(r"^[a-z]{2,8}(-[a-z0-9]{2,8})*$")
DEFAULT_LANGUAGE = "en"


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
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=(
            "Human-readable Stage document language (lowercase IETF-style tag, e.g. en, ko). "
            "Locale template files are used when bundled; other files fall back to English. "
            "Machine-readable fields stay language-neutral."
        ),
    )
    return parser.parse_args()


def template_source(relative_path: Path, language: str) -> Path:
    """The canonical English template, or its locale overlay when bundled."""
    if language != DEFAULT_LANGUAGE:
        candidate = LOCALE_ROOT / language / relative_path
        if candidate.is_file():
            return candidate
    return TEMPLATE_ROOT / relative_path


def copy_templates(
    project_root: Path, force: bool, language: str = DEFAULT_LANGUAGE
) -> tuple[list[Path], list[Path]]:
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

        shutil.copyfile(template_source(relative_path, language), target_path)
        created.append(target_path)

    settings_path = stage_root / "settings.json"
    if settings_path in created and language != DEFAULT_LANGUAGE:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["language"] = language
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

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
    if not LANGUAGE_TAG_RE.match(args.language):
        raise ValueError(
            f"Invalid language tag: {args.language!r} (expected e.g. 'en', 'ko', 'pt-br')"
        )

    created, skipped = copy_templates(project_root, args.force, args.language)

    print(f"Stage root: {project_root / '.stage'}")
    print(f"Language: {args.language}")
    print(f"Created or updated files: {len(created)}")
    print(f"Preserved existing files: {len(skipped)}")
    for path in created:
        print(f"  write {path.relative_to(project_root)}")
    for path in skipped:
        print(f"  keep  {path.relative_to(project_root)}")


if __name__ == "__main__":
    main()
