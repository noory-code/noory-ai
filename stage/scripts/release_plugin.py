#!/usr/bin/env python3
"""Release queued changelog entries for one repository plugin."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
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
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--bump",
        choices=("patch", "minor", "major"),
        help="Explicit semantic-version component to increment.",
    )
    mode.add_argument(
        "--check-released",
        action="store_true",
        help=(
            "Release nothing; list lines that released changelog sections gained after the "
            "commit that wrote their heading, and exit 1 when there are any."
        ),
    )
    parser.add_argument(
        "--since",
        metavar="VERSION",
        help=(
            "With --check-released: check only release sections at or after this x.y.z "
            "version, so older history does not fail the check."
        ),
    )
    parser.add_argument(
        "--repository-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root. Defaults to the root containing this script.",
    )
    args = parser.parse_args()
    if args.since is not None:
        if not args.check_released:
            parser.error("argument --since: only allowed with --check-released")
        if VERSION_RE.fullmatch(args.since) is None:
            parser.error(f"argument --since: version is not semantic x.y.z: {args.since}")
    return args


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


@dataclass(frozen=True)
class SectionIntrusion:
    """Lines a released section holds now that the commit writing its heading did not."""

    heading: str
    release_commit: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class ReleasedSectionCheck:
    intrusions: tuple[SectionIntrusion, ...]
    # Release headings no commit added in a non-merge diff (uncommitted, or written while
    # resolving a merge); they have nothing to compare against.
    unrecorded_headings: tuple[str, ...]


def run_git(repository_root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repository_root,
            input=stdin,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ReleaseError("git is not installed") from exc
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ReleaseError(f"git {args[0]} failed: {message}")
    return result.stdout


def release_sections(changelog: str) -> dict[str, list[str]]:
    """Map each release heading to its body lines, without line endings."""

    sections: dict[str, list[str]] = {}
    body: list[str] | None = None
    for raw_line in changelog.splitlines():
        line = raw_line.rstrip("\r")
        if line.startswith("## "):
            body = None
            if RELEASE_HEADING_RE.fullmatch(line) is not None and line not in sections:
                body = sections[line] = []
            continue
        if body is not None:
            body.append(line)
    return sections


def heading_release_commits(
    repository_root: Path, changelog_path: str, headings: set[str]
) -> dict[str, str]:
    """Return, for each heading, the oldest non-merge commit whose diff added that line.

    A release adds its heading and nothing else to the changelog, so that commit holds the
    section exactly as released. Merge commits are skipped: a merge that carries a heading in
    from the other parent did not write it.
    """

    log = run_git(
        repository_root,
        "log",
        "--reverse",
        "--no-merges",
        "--no-renames",
        "--no-color",
        "--no-ext-diff",
        "--unified=0",
        "--format=%x00%H",
        "-p",
        "--",
        changelog_path,
    ).decode("utf-8", errors="replace")
    commits: dict[str, str] = {}
    commit = ""
    for raw_line in log.splitlines():
        line = raw_line.rstrip("\r")
        if line.startswith("\x00"):
            commit = line[1:]
        elif line.startswith("+## ") and commit:
            heading = line[1:]
            if heading in headings and heading not in commits:
                commits[heading] = commit
    return commits


def read_blobs(repository_root: Path, objects: list[str]) -> dict[str, str]:
    """Read `<commit>:<path>` objects through one `git cat-file --batch` process."""

    if not objects:
        return {}
    output = run_git(
        repository_root,
        "cat-file",
        "--batch",
        stdin="".join(f"{name}\n" for name in objects).encode("utf-8"),
    )
    contents: dict[str, str] = {}
    offset = 0
    for name in objects:
        header_end = output.index(b"\n", offset)
        header = output[offset:header_end].decode("utf-8", errors="replace").split()
        if len(header) != 3 or header[1] != "blob":
            raise ReleaseError(f"git cannot read {name}: {' '.join(header)}")
        size = int(header[2])
        start = header_end + 1
        contents[name] = output[start : start + size].decode("utf-8", errors="replace")
        offset = start + size + 1
    return contents


def version_key(version: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(version)
    if match is None:
        raise ReleaseError(f"version is not semantic x.y.z: {version}")
    major, minor, patch = (int(value) for value in match.groups())
    return major, minor, patch


def heading_version(heading: str) -> str:
    match = RELEASE_HEADING_RE.fullmatch(heading)
    if match is None:
        raise ReleaseError(f"not a release heading: {heading}")
    return match.group(1)


def check_released_sections(
    repository_root: Path, plugin: str, since: str | None = None
) -> ReleasedSectionCheck:
    """Compare each released section with the one its release commit wrote.

    With `since`, only sections whose version is at or after it are compared, so history that
    predates the check cannot fail it (W-00000396).

    A card branch that forked before a release and adds a line to the old `## Unreleased` merges
    without a conflict, and git can place that line under the released heading (W-00000384).
    Blank lines are ignored; only lines with text are reported, with repeated lines counted.
    """

    if PLUGIN_NAME_RE.fullmatch(plugin) is None:
        raise ReleaseError(f"plugin must be a repository directory name: {plugin!r}")
    repository_root = repository_root.expanduser().resolve()
    changelog_file = repository_root / plugin / "CHANGELOG.md"
    try:
        changelog = changelog_file.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ReleaseError(f"changelog not found: {changelog_file}") from exc

    # A shallow checkout's oldest commit seems to add every heading, so each section would
    # be compared with itself and the check would pass whatever was merged (W-00000410).
    if run_git(repository_root, "rev-parse", "--is-shallow-repository").strip() == b"true":
        raise ReleaseError(
            "the checkout is shallow, so release commits cannot be found; fetch the whole "
            "history first (`git fetch --unshallow`, or `fetch-depth: 0` in actions/checkout)"
        )

    changelog_path = f"{plugin}/CHANGELOG.md"
    sections = release_sections(changelog)
    if since is not None:
        floor = version_key(since)
        sections = {
            heading: body
            for heading, body in sections.items()
            if version_key(heading_version(heading)) >= floor
        }
    commits = heading_release_commits(repository_root, changelog_path, set(sections))
    released_texts = read_blobs(
        repository_root,
        [f"{commit}:{changelog_path}" for commit in dict.fromkeys(commits.values())],
    )

    intrusions: list[SectionIntrusion] = []
    for heading, body in sections.items():
        commit = commits.get(heading)
        if commit is None:
            continue
        released = release_sections(released_texts[f"{commit}:{changelog_path}"])
        remaining = Counter(line for line in released.get(heading, []) if line.strip())
        added: list[str] = []
        for line in body:
            if not line.strip():
                continue
            if remaining[line] > 0:
                remaining[line] -= 1
            else:
                added.append(line)
        if added:
            intrusions.append(SectionIntrusion(heading, commit, tuple(added)))
    unrecorded = tuple(heading for heading in sections if heading not in commits)
    return ReleasedSectionCheck(tuple(intrusions), unrecorded)


def render_released_section_check(plugin: str, check: ReleasedSectionCheck) -> str:
    lines: list[str] = []
    for heading in check.unrecorded_headings:
        lines.append(f"Not checked, no commit added this heading: {heading}")
    if not check.intrusions:
        lines.append(f"{plugin}/CHANGELOG.md: no released section gained lines after its release")
        return "\n".join(lines) + "\n"
    lines.append(
        f"{plugin}/CHANGELOG.md: released sections gained lines after their release commit; "
        "move them under '## Unreleased':"
    )
    for intrusion in check.intrusions:
        lines.append(f"{intrusion.heading} (released in {intrusion.release_commit[:12]})")
        lines.extend(f"+ {line}" for line in intrusion.lines)
    return "\n".join(lines) + "\n"


def main() -> None:
    # Changelog headings carry an em dash; a Windows console defaults to cp1252 or cp949,
    # which would write it as bytes a UTF-8 reader cannot decode (W-00000393).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parse_args()
    if args.check_released:
        try:
            check = check_released_sections(
                Path(args.repository_root), args.plugin, since=args.since
            )
        except (OSError, ReleaseError) as exc:
            print(f"Check failed: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        print(render_released_section_check(args.plugin, check), end="")
        raise SystemExit(1 if check.intrusions else 0)
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
