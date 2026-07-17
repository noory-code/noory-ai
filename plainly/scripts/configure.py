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
    MAX_STYLE_BYTES,
    load_catalog,
    read_style_file,
    resolve_style,
    settings_path,
)


INTERVIEW_STYLE_FILENAME = "interview-style.md"
INTERVIEW_PRESETS = {
    ("standard", "direct", "conversational"): "baseline",
    ("shortest", "direct", "conversational"): "brief",
    ("standard", "step-by-step", "conversational"): "guided",
    ("standard", "direct", "formal"): "professional",
}


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
    return settings_path(Path(args.project_root))


def add_project_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-root", default=".")


def configure_style_file(project_root: Path, style_path: Path) -> tuple[bool, str]:
    resolved_root = project_root.expanduser().resolve()
    resolved_style = style_path.expanduser()
    if not resolved_style.is_absolute():
        resolved_style = resolved_root / resolved_style
    resolved_style = resolved_style.resolve()

    _, error = read_style_file(resolved_style)
    if error:
        return False, error
    try:
        stored_path = resolved_style.relative_to(resolved_root).as_posix()
    except ValueError:
        return (
            False,
            f"Plainly project style file must stay within project root "
            f"{resolved_root}: {resolved_style}",
        )
    write_settings(settings_path(resolved_root), {"style_file": stored_path})
    return True, f"Plainly project style set: {resolved_style}"


def interview_style(length: str, structure: str, tone: str) -> tuple[str | None, str | None]:
    catalog = load_catalog(PLUGIN_ROOT)
    preset = INTERVIEW_PRESETS.get((length, structure, tone))
    if preset is not None:
        return preset, None

    selected_profiles = [catalog.baseline]
    if length == "shortest":
        selected_profiles.append("brief")
    if structure == "step-by-step":
        selected_profiles.append("guided")
    if tone == "formal":
        selected_profiles.append("professional")

    parts: list[str] = []
    for name in selected_profiles:
        text, error = read_style_file(catalog.profiles[name].path)
        if error:
            raise RuntimeError(error)
        if text is None:
            raise RuntimeError(f"Plainly profile {name!r} has no style text")
        parts.append(text)
    return None, "\n\n".join(parts) + "\n"


def write_interview_style(project_root: Path, text: str) -> Path:
    encoded = text.encode("utf-8")
    if not encoded or len(encoded) > MAX_STYLE_BYTES:
        raise RuntimeError(
            f"Generated Plainly style must contain 1 to {MAX_STYLE_BYTES} UTF-8 bytes"
        )
    resolved_root = project_root.expanduser().resolve()
    directory = resolved_root / ".plainly"
    directory.mkdir(parents=True, exist_ok=True)
    path = (directory / INTERVIEW_STYLE_FILENAME).resolve()
    try:
        path.relative_to(resolved_root)
    except ValueError as exc:
        raise RuntimeError(
            f"Plainly interview style must stay within project root {resolved_root}: {path}"
        ) from exc
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return path


def build_parser() -> argparse.ArgumentParser:
    catalog = load_catalog(PLUGIN_ROOT)
    parser = argparse.ArgumentParser(description="Configure Plainly response styles.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="List built-in profiles.")

    show = commands.add_parser("show", help="Show the effective style.")
    add_project_root(show)

    set_profile = commands.add_parser("set-profile", help="Select a built-in profile.")
    set_profile.add_argument(
        "profile",
        choices=tuple(catalog.profiles) + tuple(catalog.aliases),
    )
    add_project_root(set_profile)

    set_file = commands.add_parser("set-file", help="Select an external UTF-8 style file.")
    set_file.add_argument("path")
    add_project_root(set_file)

    interview = commands.add_parser(
        "apply-interview",
        help="Apply the answers collected by the Plainly onboarding interview.",
    )
    interview.add_argument("--length", choices=("standard", "shortest"), required=True)
    interview.add_argument(
        "--structure",
        choices=("direct", "step-by-step"),
        required=True,
    )
    interview.add_argument("--tone", choices=("conversational", "formal"), required=True)
    add_project_root(interview)

    reset = commands.add_parser("reset", help="Remove saved Plainly settings.")
    add_project_root(reset)
    return parser


def run(args: argparse.Namespace) -> int:
    catalog = load_catalog(PLUGIN_ROOT)
    if args.command == "list":
        for name, profile in catalog.profiles.items():
            marker = " (default)" if name == catalog.default else ""
            print(f"{name}{marker}: {profile.description}")
        for alias, target in catalog.aliases.items():
            print(f"{alias} -> {target} (compatibility alias)")
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
        profile = catalog.aliases.get(args.profile, args.profile)
        write_settings(path, {"profile": profile})
        print(f"Plainly project profile set to {profile}: {path}")
        return 0

    if args.command == "set-file":
        project_root = Path(args.project_root).expanduser().resolve()
        configured, message = configure_style_file(project_root, Path(args.path))
        print(message, file=sys.stdout if configured else sys.stderr)
        return 0 if configured else 2

    if args.command == "apply-interview":
        project_root = Path(args.project_root).expanduser().resolve()
        profile, custom_text = interview_style(args.length, args.structure, args.tone)
        if custom_text is None:
            if profile is None:
                raise RuntimeError("Plainly interview did not select a profile or custom style")
            write_settings(settings_path(project_root), {"profile": profile})
            print(f"Plainly interview selected profile {profile}: {settings_path(project_root)}")
            return 0

        try:
            style_path = write_interview_style(project_root, custom_text)
        except (OSError, UnicodeError, RuntimeError) as exc:
            print(f"Cannot write Plainly interview style: {exc}", file=sys.stderr)
            return 2
        configured, message = configure_style_file(project_root, style_path)
        print(message, file=sys.stdout if configured else sys.stderr)
        return 0 if configured else 2

    if args.command == "reset":
        if path.exists():
            path.unlink()
            print(f"Plainly project settings removed: {path}")
        else:
            print(f"Plainly project settings already use defaults: {path}")
        return 0

    raise RuntimeError(f"Unhandled command: {args.command}")


def main() -> None:
    parser = build_parser()
    args: Any = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
