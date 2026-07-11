from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "src"))

from plainly.runtime import (  # noqa: E402
    load_catalog,
    read_style_file,
    resolve_style,
    settings_path,
)


def write_settings(path: Path, payload: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def target_settings(args: argparse.Namespace) -> Path:
    return settings_path(args.scope, Path(args.project_root), Path.home())


def add_scope_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project-root", default=".")


def build_parser() -> argparse.ArgumentParser:
    catalog = load_catalog(PLUGIN_ROOT)
    parser = argparse.ArgumentParser(description="Configure Plainly response styles.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="List built-in profiles.")

    show = commands.add_parser("show", help="Show the effective style.")
    show.add_argument("--project-root", default=".")

    set_profile = commands.add_parser("set-profile", help="Select a built-in profile.")
    set_profile.add_argument("profile", choices=tuple(catalog.profiles))
    add_scope_options(set_profile)

    set_file = commands.add_parser("set-file", help="Select an external UTF-8 style file.")
    set_file.add_argument("path")
    add_scope_options(set_file)

    reset = commands.add_parser("reset", help="Remove saved Plainly settings.")
    add_scope_options(reset)
    return parser


def run(args: argparse.Namespace) -> int:
    catalog = load_catalog(PLUGIN_ROOT)
    if args.command == "list":
        for name, profile in catalog.profiles.items():
            marker = " (default)" if name == catalog.default else ""
            print(f"{name}{marker}: {profile.description}")
        return 0

    if args.command == "show":
        resolved = resolve_style(PLUGIN_ROOT, Path(args.project_root))
        print(f"source: {resolved.source}")
        print(f"profile: {resolved.profile or 'external'}")
        for diagnostic in resolved.diagnostics:
            print(f"warning: {diagnostic}")
        return 0

    path = target_settings(args)
    if args.command == "set-profile":
        write_settings(path, {"profile": args.profile})
        print(f"Plainly profile set to {args.profile} ({args.scope}): {path}")
        return 0

    if args.command == "set-file":
        project_root = Path(args.project_root).expanduser().resolve()
        style_path = Path(args.path).expanduser()
        if not style_path.is_absolute():
            style_path = project_root / style_path
        style_path = style_path.resolve()
        _, error = read_style_file(style_path)
        if error:
            print(error, file=sys.stderr)
            return 2
        stored_path = str(style_path)
        if args.scope == "project":
            try:
                stored_path = style_path.relative_to(project_root).as_posix()
            except ValueError:
                print(
                    f"Plainly project style file must stay within project root "
                    f"{project_root}: {style_path}",
                    file=sys.stderr,
                )
                return 2
        write_settings(path, {"style_file": stored_path})
        print(f"Plainly external style set ({args.scope}): {style_path}")
        return 0

    if args.command == "reset":
        if path.exists():
            path.unlink()
            print(f"Plainly settings removed ({args.scope}): {path}")
        else:
            print(f"Plainly settings already use defaults ({args.scope}): {path}")
        return 0

    raise RuntimeError(f"Unhandled command: {args.command}")


def main() -> None:
    parser = build_parser()
    args: Any = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
