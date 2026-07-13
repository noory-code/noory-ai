"""Fail-closed schema-v3 to schema-v4 Stage topology migration.

The relocation registry in ``stage_topology`` is the only path map.  This module owns
the git transaction, maintenance marker, journal, deterministic pre-commit abort, and
the narrow durable-reference rewrites required by the migration contract.
"""

from __future__ import annotations

import json
import posixpath
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import stage_topology


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
V3_TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
V3_LOCALE_ROOT = PLUGIN_ROOT / "templates" / "locales"
V4_TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "v4" / "project-stage"
V4_LOCALE_ROOT = PLUGIN_ROOT / "templates" / "v4" / "locales"
JOURNAL_RELATIVE = Path(".runtime/schema-v4-migration-journal.json")
INDEX_PROPOSAL_RELATIVE = Path(".runtime/schema-v4-index.proposed.md")
PATH_FIELDS = frozenset(
    {"promotes", "decision_refs", "retrospective_ref", "scope"}
)
MARKDOWN_LINK_RE = re.compile(r"(?P<prefix>\]\()(?P<destination><[^>]+>|[^\s)]+)")
CODE_SPAN_RE = re.compile(r"`(?P<value>[^`\n]+)`")
FRONTMATTER_FIELD_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?P<value>.*)$"
)


class MigrationError(RuntimeError):
    """A fail-closed migration refusal with an operator-facing explanation."""


@dataclass(frozen=True)
class Preflight:
    head: str
    moves: tuple[tuple[str, str], ...]
    patched_index: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _contains(root: str, path: str) -> bool:
    return path == root or path.startswith(root + "/")


def _legacy_roots() -> tuple[str, ...]:
    return tuple(
        sorted({origin.split("/", 1)[0] for origin in stage_topology.V3_TO_V4_RELOCATIONS})
    )


def _v4_roots() -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                destination.split("/", 1)[0]
                for destination in stage_topology.V3_TO_V4_RELOCATIONS.values()
            }
        )
    )


def _run_git(
    project_root: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise MigrationError(f"git {' '.join(args)} failed: {detail}")
    return result


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _runtime_path(path: str) -> bool:
    clean = path.replace("\\", "/").lstrip("./")
    return clean == ".stage/.runtime" or clean.startswith(".stage/.runtime/")


def dirty_paths(project_root: Path) -> list[str]:
    """Return git changes outside the runtime exemption."""

    result = _run_git(
        project_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    records = result.stdout.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        status = record[:2]
        path = record[3:]
        candidates = [path]
        if "R" in status or "C" in status:
            if index < len(records) and records[index]:
                candidates.append(records[index])
                index += 1
        paths.extend(candidate for candidate in candidates if not _runtime_path(candidate))
    return sorted(dict.fromkeys(paths))


def _stage_entries(stage_root: Path) -> list[Path]:
    return [
        path
        for path in stage_root.rglob("*")
        if JOURNAL_RELATIVE.parts[0] not in path.relative_to(stage_root).parts
    ]


def _under_relocation_source(relative: str) -> bool:
    return any(
        _contains(origin, relative)
        for origin in stage_topology.V3_TO_V4_RELOCATIONS
    )


def case_collision(stage_root: Path) -> tuple[str, str] | None:
    """Find a collision as if the filesystem compared every destination case-insensitively."""

    planned_by_fold: dict[str, str] = {}
    for path in _stage_entries(stage_root):
        relative = path.relative_to(stage_root).as_posix()
        if not _under_relocation_source(relative):
            continue
        destination = stage_topology.relocate_v3_path(relative)
        folded = destination.casefold()
        previous = planned_by_fold.get(folded)
        if previous is not None and previous != destination:
            return previous, destination
        planned_by_fold[folded] = destination

    for path in _stage_entries(stage_root):
        relative = path.relative_to(stage_root).as_posix()
        if _under_relocation_source(relative):
            continue
        planned = planned_by_fold.get(relative.casefold())
        if planned is not None:
            return relative, planned
    return None


def pending_promotion_files(stage_root: Path) -> list[Path]:
    intents_root = stage_root / ".runtime" / "intents"
    pending = []
    if intents_root.is_dir():
        pending.extend(
            path
            for path in sorted(intents_root.iterdir())
            if path.is_file()
            and (path.name.endswith(".json") or ".json.claim-" in path.name)
        )
    legacy = stage_root / ".runtime" / "promote-intent.json"
    if legacy.is_file() or legacy.is_symlink():
        pending.append(legacy)
    return pending


def _populated(root: Path) -> bool:
    if root.is_symlink() or root.is_file():
        return True
    if not root.is_dir():
        return False
    return any(path.is_file() or path.is_symlink() for path in root.rglob("*"))


def mixed_populated_roots(stage_root: Path) -> tuple[list[str], list[str]]:
    legacy = [root for root in _legacy_roots() if _populated(stage_root / root)]
    current = [root for root in _v4_roots() if _populated(stage_root / root)]
    return legacy, current


def unsupported_legacy_entries(stage_root: Path) -> list[str]:
    unsupported = []
    for legacy_root in _legacy_roots():
        root = stage_root / legacy_root
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not (path.is_file() or path.is_symlink()):
                continue
            relative = path.relative_to(stage_root).as_posix()
            if not _under_relocation_source(relative):
                unsupported.append(relative)
    return sorted(unsupported)


def _template_index_pairs() -> list[tuple[Path, Path]]:
    pairs = [(V3_TEMPLATE_ROOT / "index.md", V4_TEMPLATE_ROOT / "index.md")]
    if V3_LOCALE_ROOT.is_dir():
        for old_path in sorted(V3_LOCALE_ROOT.glob("*/index.md")):
            language = old_path.parent.name
            new_path = V4_LOCALE_ROOT / language / "index.md"
            if new_path.is_file():
                pairs.append((old_path, new_path))
    return pairs


def _topology_block(text: str) -> str | None:
    match = re.search(r"^##\s+", text, re.MULTILINE)
    return text[match.start() :] if match is not None else None


def _localized_v4_template(relative: Path, language: str) -> Path:
    if language and language != "en":
        localized = V4_LOCALE_ROOT / language / relative
        if localized.is_file():
            return localized
    return V4_TEMPLATE_ROOT / relative


def prepare_index_patch(
    stage_root: Path, settings: dict[str, object], dry_run: bool
) -> str:
    index_path = stage_root / "index.md"
    try:
        current = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MigrationError(f"Project index.md cannot be read: {exc}") from exc

    for old_path, new_path in _template_index_pairs():
        old_block = _topology_block(old_path.read_text(encoding="utf-8"))
        new_block = _topology_block(new_path.read_text(encoding="utf-8"))
        if old_block is None or new_block is None or old_block not in current:
            continue
        return current.replace(old_block, new_block, 1)

    language = settings.get("language")
    language_value = language if isinstance(language, str) else "en"
    proposal = _localized_v4_template(Path("index.md"), language_value).read_text(
        encoding="utf-8"
    )
    proposal_path = stage_root / INDEX_PROPOSAL_RELATIVE
    if not dry_run:
        proposal_path.parent.mkdir(parents=True, exist_ok=True)
        proposal_path.write_text(proposal, encoding="utf-8")
    raise MigrationError(
        "Project index.md topology section is customized and cannot be patched "
        "unambiguously. No topology changes were made. Manually merge the proposed v4 "
        f"index at `.stage/{INDEX_PROPOSAL_RELATIVE.as_posix()}` into the permanent "
        "`.stage/index.md`, commit that resolution, and rerun stage-migrate."
    )


def preflight(
    project_root: Path,
    stage_root: Path,
    settings: dict[str, object],
    dry_run: bool,
) -> Preflight:
    """Run every refusal before the maintenance marker or topology changes."""

    try:
        head = _run_git(project_root, "rev-parse", "--verify", "HEAD").stdout.strip()
    except MigrationError as exc:
        raise MigrationError(
            "Stage migration requires a git repository with a committed HEAD because all "
            "relocations use git mv and abort restores that exact commit."
        ) from exc

    marker_path = stage_root / stage_topology.MAINTENANCE_MARKER
    journal_path = stage_root / JOURNAL_RELATIVE
    if marker_path.exists() or journal_path.exists():
        present = [
            path.relative_to(stage_root).as_posix()
            for path in (marker_path, journal_path)
            if path.exists()
        ]
        raise MigrationError(
            "An existing schema-v4 migration transaction blocks restart: "
            + ", ".join(present)
            + ". Resume mode is deferred; run the stage-migrate abort path to restore "
            "the original clean v3 tree, then rerun the migration."
        )

    dirty = dirty_paths(project_root)
    if dirty:
        raise MigrationError(
            "Dirty git working tree; commit or discard every change outside "
            "`.stage/.runtime/` before migration. Blocking paths: " + ", ".join(dirty)
        )

    if stage_root.is_symlink():
        raise MigrationError(
            "The `.stage` root is a symlink. Replace it with a real project-local directory "
            "before migration; relocating through an aliased root is refused."
        )

    collision = case_collision(stage_root)
    if collision is not None:
        raise MigrationError(
            "Case-insensitive destination collision: "
            f"`{collision[0]}` conflicts with migration destination `{collision[1]}`. "
            "Rename the conflicting entry and commit that resolution before rerunning."
        )

    pending = pending_promotion_files(stage_root)
    if pending:
        names = [path.relative_to(stage_root).as_posix() for path in pending]
        raise MigrationError(
            "Pending promotion machinery blocks schema migration: "
            + ", ".join(names)
            + ". Complete or discard every pending intent/claim first, then rerun "
            "stage-migrate."
        )

    legacy, current = mixed_populated_roots(stage_root)
    if legacy and current:
        raise MigrationError(
            "Mixed populated topology is a hard error. Populated v3 roots: "
            f"{', '.join(legacy)}; populated v4 roots: {', '.join(current)}. "
            "Manually reconcile duplicate/conflicting artifacts into one v3 tree, remove "
            "the partial v4 roots, commit the resolution, and rerun stage-migrate."
        )

    unsupported = unsupported_legacy_entries(stage_root)
    if unsupported:
        raise MigrationError(
            "Legacy topology contains paths outside the registry relocation map: "
            + ", ".join(unsupported)
            + ". Move them to a recognized v3 family or resolve them manually, commit, and "
            "rerun stage-migrate."
        )

    patched_index = prepare_index_patch(stage_root, settings, dry_run)
    moves = tuple(
        (origin, destination)
        for origin, destination in stage_topology.V3_TO_V4_RELOCATIONS.items()
        if (stage_root / origin).exists() or (stage_root / origin).is_symlink()
    )
    if not moves and not current:
        raise MigrationError(
            "No populated schema-v3 topology was found; repair the project before migration."
        )
    return Preflight(head=head, moves=moves, patched_index=patched_index)


def begin(
    stage_root: Path, preflight_result: Preflight, original_schema_version: object
) -> dict[str, Any]:
    journal = {
        "migration": "schema-v3-to-v4",
        "status": "active",
        "started_at": utc_now(),
        "original_head": preflight_result.head,
        "original_schema_version": original_schema_version,
        "moves": [],
        "rewritten": [],
        "created": [],
    }
    _write_json(stage_root / JOURNAL_RELATIVE, journal)
    marker = {
        "migration": "schema-v3-to-v4",
        "started_at": journal["started_at"],
        "journal": JOURNAL_RELATIVE.as_posix(),
    }
    _write_json(stage_root / stage_topology.MAINTENANCE_MARKER, marker)
    return journal


def save_journal(stage_root: Path, journal: dict[str, Any]) -> None:
    _write_json(stage_root / JOURNAL_RELATIVE, journal)


def fail(stage_root: Path, journal: dict[str, Any], reason: str) -> None:
    journal["status"] = "failed"
    journal["failed_at"] = utc_now()
    journal["failure"] = reason
    save_journal(stage_root, journal)


def _has_git_content(path: Path) -> bool:
    if path.is_file() or path.is_symlink():
        return True
    return any(candidate.is_file() or candidate.is_symlink() for candidate in path.rglob("*"))


def relocate(
    project_root: Path,
    stage_root: Path,
    preflight_result: Preflight,
    journal: dict[str, Any],
) -> None:
    for origin, destination in preflight_result.moves:
        source = stage_root / origin
        target = stage_root / destination
        move = {"source": origin, "destination": destination, "status": "planned"}
        journal["moves"].append(move)
        save_journal(stage_root, journal)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir() and not source.is_symlink() and not _has_git_content(source):
            source.rename(target)
            move["method"] = "directory-rename"
        else:
            _run_git(
                project_root,
                "mv",
                "--",
                f".stage/{origin}",
                f".stage/{destination}",
            )
            move["method"] = "git-mv"
        move["status"] = "done"
        save_journal(stage_root, journal)

    for root_name in _legacy_roots():
        root = stage_root / root_name
        if not root.is_dir() or root.is_symlink():
            continue
        directories = sorted(
            (path for path in root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        )
        for directory in directories:
            try:
                directory.rmdir()
            except OSError:
                pass
        try:
            root.rmdir()
        except OSError:
            pass


def _inverse_relocate(path: str) -> str:
    matches = [
        destination
        for destination in stage_topology.V3_TO_V4_RELOCATIONS.values()
        if _contains(destination, path)
    ]
    if not matches:
        return path
    destination = max(matches, key=len)
    origin = next(
        source
        for source, candidate in stage_topology.V3_TO_V4_RELOCATIONS.items()
        if candidate == destination
    )
    return origin + path[len(destination) :]


def _separate_suffix(value: str) -> tuple[str, str]:
    positions = [position for marker in ("#", "?") if (position := value.find(marker)) >= 0]
    if not positions:
        return value, ""
    split_at = min(positions)
    return value[:split_at], value[split_at:]


def _direct_stage_reference(value: str) -> tuple[str, bool]:
    normalized = value.replace("\\", "/")
    if normalized.startswith(".stage/"):
        return normalized[len(".stage/") :], True
    return normalized, False


def rewrite_direct_reference(value: str) -> str:
    """Rewrite one durable scalar/list entry only when it names a registry path."""

    leading = value[: len(value) - len(value.lstrip())]
    trailing = value[len(value.rstrip()) :]
    core = value.strip()
    if not core:
        return value
    quote = ""
    if len(core) >= 2 and core[0] in {"'", '"'} and core[-1] == core[0]:
        quote = core[0]
        core = core[1:-1]
    path_value, suffix = _separate_suffix(core)
    trailing_slash = path_value.endswith("/")
    stage_relative, stage_prefixed = _direct_stage_reference(path_value)
    relocated = stage_topology.relocate_v3_path(stage_relative)
    if relocated == stage_relative:
        return value
    if trailing_slash and not relocated.endswith("/"):
        relocated += "/"
    prefix = ".stage/" if stage_prefixed else ""
    return leading + quote + prefix + relocated + suffix + quote + trailing


def rewrite_field_value(value: str) -> str:
    parts = re.split(r"([,;]\s*)", value)
    return "".join(
        part if index % 2 else rewrite_direct_reference(part)
        for index, part in enumerate(parts)
    )


def _rewrite_internal_reference(
    value: str, old_relative: str, new_relative: str
) -> str:
    wrapped = value.startswith("<") and value.endswith(">")
    raw = value[1:-1] if wrapped else value
    if not raw or raw.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return value
    path_value, suffix = _separate_suffix(raw)
    trailing_slash = path_value.endswith("/")
    direct, stage_prefixed = _direct_stage_reference(path_value)
    if stage_prefixed or stage_topology.is_legacy_path(direct):
        target = direct.strip("/")
        relocated = stage_topology.relocate_v3_path(target)
        rewritten = (".stage/" if stage_prefixed else "") + relocated
    else:
        if path_value.startswith("/"):
            return value
        target = posixpath.normpath(
            posixpath.join(posixpath.dirname(old_relative), path_value)
        )
        if target == ".." or target.startswith("../"):
            return value
        relocated = stage_topology.relocate_v3_path(target)
        rewritten = posixpath.relpath(relocated, posixpath.dirname(new_relative) or ".")
        if rewritten == ".":
            rewritten = "./"
    if trailing_slash and not rewritten.endswith("/"):
        rewritten += "/"
    result = rewritten + suffix
    return f"<{result}>" if wrapped else result


def _frontmatter_bounds(lines: list[str]) -> tuple[int, int] | None:
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return 1, index
    return None


def rewrite_markdown_text(text: str, old_relative: str, new_relative: str) -> str:
    lines = text.splitlines(keepends=True)
    bounds = _frontmatter_bounds(lines)
    if bounds is not None:
        start, end = bounds
        active_path_field = False
        for index in range(start, end):
            body = lines[index].rstrip("\r\n")
            newline = lines[index][len(body) :]
            match = FRONTMATTER_FIELD_RE.match(body)
            if match is not None:
                key = match.group("key")
                active_path_field = key in PATH_FIELDS
                if active_path_field:
                    value = match.group("value")
                    lines[index] = (
                        match.group("indent")
                        + key
                        + ":"
                        + rewrite_field_value(value)
                        + newline
                    )
                continue
            if active_path_field and re.match(r"^[ \t]+-\s*", body):
                prefix, value = re.split(r"(?<=-)\s*", body, maxsplit=1)
                lines[index] = prefix + " " + rewrite_direct_reference(value) + newline
            elif body.strip() and not body.startswith((" ", "\t")):
                active_path_field = False

    rewritten = "".join(lines)

    def replace_link(match: re.Match[str]) -> str:
        destination = _rewrite_internal_reference(
            match.group("destination"), old_relative, new_relative
        )
        return match.group("prefix") + destination

    rewritten = MARKDOWN_LINK_RE.sub(replace_link, rewritten)

    output_lines = []
    for line in rewritten.splitlines(keepends=True):
        historical_transition = (
            "→" in line
            or "->" in line
            or re.search(r"\brename(?:d|s|ing)?\b", line, re.IGNORECASE) is not None
        )

        def replace_code(match: re.Match[str]) -> str:
            value = match.group("value")
            if historical_transition or any(character.isspace() for character in value):
                return match.group(0)
            replacement = _rewrite_internal_reference(value, old_relative, new_relative)
            return f"`{replacement}`"

        output_lines.append(CODE_SPAN_RE.sub(replace_code, line))
    return "".join(output_lines)


def rewrite_moved_markdown(stage_root: Path) -> list[str]:
    rewritten_paths = []
    destination_roots = _v4_roots()
    for path in sorted(stage_root.rglob("*.md")):
        relative = path.relative_to(stage_root).as_posix()
        if relative.startswith(".runtime/") or not any(
            _contains(root, relative) for root in destination_roots
        ):
            continue
        old_relative = _inverse_relocate(relative)
        original = path.read_text(encoding="utf-8")
        rewritten = rewrite_markdown_text(original, old_relative, relative)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            rewritten_paths.append(relative)
    return rewritten_paths


def create_v4_indexes(
    stage_root: Path, settings: dict[str, object], journal: dict[str, Any]
) -> list[str]:
    language = settings.get("language")
    language_value = language if isinstance(language, str) else "en"
    relatives = [
        Path(stage_topology.get_zone("decisions", "pending").index_surfaces[0]),
        Path(stage_topology.get_zone("roadmap", "themes").index_surfaces[0]),
        Path(stage_topology.get_zone("roadmap", "milestones").index_surfaces[0]),
    ]
    created = []
    for relative in relatives:
        target = stage_root / relative
        if target.exists():
            continue
        source = _localized_v4_template(relative, language_value)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        created.append(relative.as_posix())
    journal["created"] = created
    save_journal(stage_root, journal)
    return created


def patch_project_index(
    stage_root: Path, patched_index: str, journal: dict[str, Any]
) -> None:
    (stage_root / "index.md").write_text(patched_index, encoding="utf-8")
    journal["rewritten"] = sorted(
        set(journal.get("rewritten", [])) | {"index.md"}
    )
    save_journal(stage_root, journal)


def _legacy_direct(value: str) -> bool:
    core = value.strip().strip("<>").strip("'\"")
    path_value, _suffix = _separate_suffix(core)
    direct, _stage_prefixed = _direct_stage_reference(path_value)
    return stage_topology.is_legacy_path(direct)


def verify_no_legacy_references(stage_root: Path) -> list[str]:
    leftovers = []
    for path in sorted(stage_root.rglob("*.md")):
        relative = path.relative_to(stage_root).as_posix()
        if relative.startswith(".runtime/"):
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        bounds = _frontmatter_bounds([line + "\n" for line in lines])
        if bounds is not None:
            start, end = bounds
            active_path_field = ""
            for index in range(start, end):
                line = lines[index]
                match = FRONTMATTER_FIELD_RE.match(line)
                if match is not None:
                    key = match.group("key")
                    active_path_field = key if key in PATH_FIELDS else ""
                    if active_path_field and any(
                        _legacy_direct(part)
                        for part in re.split(r"[,;]\s*", match.group("value"))
                        if part.strip()
                    ):
                        leftovers.append(f"{relative}:{index + 1}:{key}")
                    continue
                if active_path_field and re.match(r"^[ \t]+-\s*", line):
                    value = re.sub(r"^[ \t]+-\s*", "", line)
                    if _legacy_direct(value):
                        leftovers.append(
                            f"{relative}:{index + 1}:{active_path_field}"
                        )

        for match in MARKDOWN_LINK_RE.finditer(text):
            destination = match.group("destination").strip("<>")
            path_value, _suffix = _separate_suffix(destination)
            direct, _stage_prefixed = _direct_stage_reference(path_value)
            if stage_topology.is_legacy_path(direct):
                line_number = text.count("\n", 0, match.start()) + 1
                leftovers.append(f"{relative}:{line_number}:link")
                continue
            if path_value.startswith(("/", "#")) or re.match(
                r"^[A-Za-z][A-Za-z0-9+.-]*:", path_value
            ):
                continue
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(relative), path_value)
            )
            if target != ".." and not target.startswith("../") and stage_topology.is_legacy_path(target):
                line_number = text.count("\n", 0, match.start()) + 1
                leftovers.append(f"{relative}:{line_number}:link")
    return sorted(dict.fromkeys(leftovers))


def stage_changes(project_root: Path) -> None:
    _run_git(project_root, "add", "-A", "--", ".stage")
    _run_git(
        project_root,
        "reset",
        "-q",
        "HEAD",
        "--",
        ".stage/.runtime",
        check=False,
    )


def finish(stage_root: Path, journal: dict[str, Any]) -> None:
    marker = stage_root / stage_topology.MAINTENANCE_MARKER
    try:
        marker.unlink()
    except FileNotFoundError:
        pass
    journal["status"] = "complete"
    journal["completed_at"] = utc_now()
    save_journal(stage_root, journal)


def abort(project_root: Path, stage_root: Path) -> int:
    journal_path = stage_root / JOURNAL_RELATIVE
    journal = _load_json(journal_path)
    if journal is None:
        print(
            "No schema-v4 migration journal exists; there is no deterministic "
            "pre-commit migration to abort."
        )
        return 1
    original_head = journal.get("original_head")
    current_head = _run_git(project_root, "rev-parse", "--verify", "HEAD").stdout.strip()
    if not isinstance(original_head, str) or not original_head:
        print("Migration journal has no original HEAD; abort is refused.")
        return 1
    if current_head != original_head:
        print(
            "The migration has been committed (HEAD changed). `--abort` only restores the "
            "pre-commit staged/working tree; use `git revert <migration-commit>` now."
        )
        return 1

    _run_git(
        project_root,
        "restore",
        f"--source={original_head}",
        "--staged",
        "--worktree",
        "--",
        ".stage",
    )
    for root_name in _v4_roots():
        root = stage_root / root_name
        if not root.is_dir() or root.is_symlink():
            continue
        for directory in sorted(
            (path for path in root.rglob("*") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            try:
                directory.rmdir()
            except OSError:
                pass
        try:
            root.rmdir()
        except OSError:
            pass
    for relative in (
        Path(stage_topology.MAINTENANCE_MARKER),
        JOURNAL_RELATIVE,
        INDEX_PROPOSAL_RELATIVE,
    ):
        try:
            (stage_root / relative).unlink()
        except FileNotFoundError:
            pass
    remaining = dirty_paths(project_root)
    if remaining:
        print(
            "Abort restored migration-owned Stage changes, but unrelated changes remain: "
            + ", ".join(remaining)
        )
        return 1
    print("Schema-v4 migration aborted; the clean schema-v3 tree was restored.")
    return 0
