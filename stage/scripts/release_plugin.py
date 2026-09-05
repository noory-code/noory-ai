#!/usr/bin/env python3
"""Release queued changelog entries for one repository plugin."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

PLUGIN_NAME_RE = re.compile(r"[A-Za-z0-9_-]+")
VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
RELEASE_HEADING_RE = re.compile(
    r"## \[?(\d+\.\d+\.\d+)\]?(?: — \d{4}-\d{2}-\d{2})?"
)
MANIFEST_PATHS = (
    Path(".claude-plugin/plugin.json"),
    Path(".codex-plugin/plugin.json"),
)


class ReleaseError(ValueError):
    """A release precondition was not met."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Release one plugin's queued Unreleased changelog entries."
    )
    parser.add_argument(
        "plugin",
        help="Plugin directory name relative to the repository root.",
    )
    parser.add_argument(
        "--bump",
        choices=("patch", "minor", "major"),
        required=True,
        help="Explicit semantic-version component to increment.",
    )
    parser.add_argument(
        "--repository-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root. Defaults to the root containing this script.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReleaseError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ReleaseError(f"manifest must contain a JSON object: {path}")
    return data


def manifest_version(data: dict[str, object], path: Path) -> str:
    version = data.get("version")
    if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
        raise ReleaseError(f"manifest version is not semantic x.y.z: {path}")
    return version


def replace_manifest_version(
    manifest: str,
    *,
    current_version: str,
    released_version: str,
    path: Path,
) -> str:
    version_field_re = re.compile(
        r'(?P<prefix>"version"\s*:\s*")'
        r'(?P<version>[^"]*)'
        r'(?P<suffix>")'
    )
    matches = list(version_field_re.finditer(manifest))
    if len(matches) != 1:
        raise ReleaseError(
            f"expected exactly one manifest version field: {path}; "
            f"found {len(matches)}"
        )
    match = matches[0]
    if match.group("version") != current_version:
        raise ReleaseError(
            f"manifest version field does not match parsed version: {path}"
        )
    return (
        manifest[: match.start("version")]
        + released_version
        + manifest[match.end("version") :]
    )


def next_version(current: str, bump: str) -> str:
    match = VERSION_RE.fullmatch(current)
    if match is None:
        raise ReleaseError(f"version is not semantic x.y.z: {current}")
    major, minor, patch = (int(value) for value in match.groups())
    if bump == "patch":
        patch += 1
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ReleaseError(f"unsupported version bump: {bump}")
    return f"{major}.{minor}.{patch}"


def title_unreleased_section(
    changelog: str,
    *,
    current_version: str,
    released_version: str,
    release_date: date,
) -> str:
    lines = changelog.splitlines(keepends=True)
    unreleased_indices = [
        index
        for index, line in enumerate(lines)
        if line.rstrip("\r\n") == "## Unreleased"
    ]
    if len(unreleased_indices) != 1:
        raise ReleaseError(
            f"expected exactly one '## Unreleased' section; found {len(unreleased_indices)}"
        )

    unreleased_index = unreleased_indices[0]
    next_heading_index = next(
        (
            index
            for index in range(unreleased_index + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        None,
    )
    if next_heading_index is None:
        raise ReleaseError("latest released changelog section is missing")

    unreleased_body = "".join(lines[unreleased_index + 1 : next_heading_index])
    if not unreleased_body.strip():
        raise ReleaseError("Unreleased section is empty")

    latest_heading = lines[next_heading_index].rstrip("\r\n")
    latest_match = RELEASE_HEADING_RE.fullmatch(latest_heading)
    if latest_match is None:
        raise ReleaseError(
            f"latest changelog heading is not a release version: {latest_heading}"
        )
    changelog_version = latest_match.group(1)
    if changelog_version != current_version:
        raise ReleaseError(
            f"latest changelog version {changelog_version} does not match "
            f"manifest version {current_version}"
        )

    line_ending = (
        "\r\n"
        if lines[unreleased_index].endswith("\r\n")
        else "\n"
        if lines[unreleased_index].endswith("\n")
        else ""
    )
    lines[unreleased_index] = (
        f"## Unreleased{line_ending}"
        f"{line_ending}"
        f"## {released_version} — {release_date.isoformat()}{line_ending}"
    )
    return "".join(lines)


def write_atomically(targets: dict[Path, str]) -> None:
    prepared: list[tuple[Path, Path, Path]] = []
    replaced: list[tuple[Path, Path]] = []
    try:
        for target, content in targets.items():
            if not target.is_file():
                raise ReleaseError(f"release target not found: {target}")
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{target.name}.",
                suffix=".release",
                dir=target.parent,
                text=True,
            )
            temporary_path = Path(temporary_name)
            with os.fdopen(
                descriptor,
                "w",
                encoding="utf-8",
                newline="",
            ) as handle:
                handle.write(content)
            os.chmod(temporary_path, target.stat().st_mode)

            backup_descriptor, backup_name = tempfile.mkstemp(
                prefix=f".{target.name}.",
                suffix=".backup",
                dir=target.parent,
            )
            os.close(backup_descriptor)
            backup_path = Path(backup_name)
            shutil.copy2(target, backup_path)
            prepared.append((target, temporary_path, backup_path))

        for target, temporary_path, backup_path in prepared:
            temporary_path.replace(target)
            replaced.append((target, backup_path))
    except Exception:
        for target, backup_path in reversed(replaced):
            if backup_path.exists():
                backup_path.replace(target)
        raise
    finally:
        for _, temporary_path, backup_path in prepared:
            temporary_path.unlink(missing_ok=True)
            backup_path.unlink(missing_ok=True)


def release_plugin(
    repository_root: Path,
    plugin: str,
    bump: str,
    *,
    release_date: date,
) -> str:
    if PLUGIN_NAME_RE.fullmatch(plugin) is None:
        raise ReleaseError(
            f"plugin must be a repository directory name: {plugin!r}"
        )

    repository_root = repository_root.expanduser().resolve()
    plugin_root = (repository_root / plugin).resolve()
    if plugin_root.parent != repository_root or not plugin_root.is_dir():
        raise ReleaseError(f"plugin directory not found: {plugin_root}")

    # A plugin may target one host only, in which case that host's manifest is the whole set. A
    # plugin with no manifest at all is not releasable.
    present_paths = tuple(
        relative_path
        for relative_path in MANIFEST_PATHS
        if (plugin_root / relative_path).is_file()
    )
    if not present_paths:
        rendered = ", ".join(path.as_posix() for path in MANIFEST_PATHS)
        raise ReleaseError(f"no plugin manifest found under {plugin_root}: expected {rendered}")

    manifests = {
        relative_path: load_manifest(plugin_root / relative_path)
        for relative_path in present_paths
    }
    manifest_contents = {
        relative_path: (plugin_root / relative_path).read_text(encoding="utf-8")
        for relative_path in present_paths
    }
    versions = {
        relative_path: manifest_version(data, plugin_root / relative_path)
        for relative_path, data in manifests.items()
    }
    unique_versions = set(versions.values())
    if len(unique_versions) != 1:
        rendered = ", ".join(
            f"{relative_path.as_posix()}={version}"
            for relative_path, version in versions.items()
        )
        raise ReleaseError(f"plugin manifest versions do not match: {rendered}")
    current_version = unique_versions.pop()
    released_version = next_version(current_version, bump)

    changelog_path = plugin_root / "CHANGELOG.md"
    try:
        changelog = changelog_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ReleaseError(f"changelog not found: {changelog_path}") from exc
    released_changelog = title_unreleased_section(
        changelog,
        current_version=current_version,
        released_version=released_version,
        release_date=release_date,
    )

    targets = {changelog_path: released_changelog}
    for relative_path in present_paths:
        targets[plugin_root / relative_path] = replace_manifest_version(
            manifest_contents[relative_path],
            current_version=current_version,
            released_version=released_version,
            path=plugin_root / relative_path,
        )
    write_atomically(targets)
    return released_version


def main() -> None:
    args = parse_args()
    try:
        released_version = release_plugin(
            Path(args.repository_root),
            args.plugin,
            args.bump,
            release_date=date.today(),
        )
    except (OSError, ReleaseError) as exc:
        print(f"Release failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"Released {args.plugin} {released_version}")


if __name__ == "__main__":
    main()
