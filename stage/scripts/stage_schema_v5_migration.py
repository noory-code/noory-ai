"""Fail-closed schema-v4 to schema-v5 work hierarchy migration.

Schema v5 removes the flat work-card shape.  This module is the only reader of
that retired shape: it snapshots the pre-migration Stage tree, installs a
maintenance marker, moves every flat card into an epic/story/action location,
rewrites live index links from the resulting files, refreshes the work guidance,
and stamps the schema marker last.
"""

from __future__ import annotations

import base64
import json
import posixpath
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK_ROOT = PLUGIN_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

from stage_paths import read_settings, write_setting_preserving_comments  # noqa: E402
from stage_record_paths import record_paths, work_record_scale  # noqa: E402
from stage_work import parse_frontmatter  # noqa: E402
import refresh_decision_index  # noqa: E402


SCHEMA_VERSION = 5
WORK_ROOTS = (
    "work/planned",
    "work/current",
    "official/work/archive/items",
)
ARCHIVE_ROOT = "official/work/archive/items"
CURRENT_ROOT = "work/current"
PLANNED_ROOT = "work/planned"
JOURNAL_RELATIVE = Path(".runtime/schema-v5-migration-journal.json")
MAINTENANCE_MARKER_RELATIVE = Path(".runtime/schema-v5-maintenance.json")
WORK_GUIDANCE_RELATIVES = tuple(
    Path(root) / name
    for root in WORK_ROOTS
    for name in ("README.md", "_template.md", "_epic.md", "_story.md")
)
INDEX_ROOTS = {
    Path("work/active.md"): CURRENT_ROOT,
    Path("work/review.md"): CURRENT_ROOT,
    Path("work/planned/index.md"): PLANNED_ROOT,
    Path("official/work/archive/index.md"): ARCHIVE_ROOT,
}
FRONTMATTER_FIELD_RE = re.compile(
    r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?P<value>.*)$"
)
WORK_ROW_RE = re.compile(r"^\|\s*(?P<id>W-\d{3,})\s*\|")
MARKDOWN_LINK_RE = re.compile(r"\]\((?P<target><[^>]+>|[^\s)]+)\)")


class MigrationError(RuntimeError):
    """A fail-closed migration refusal."""


@dataclass(frozen=True)
class ExistingRecord:
    item_id: str
    root: str
    relative: str
    scale: str


@dataclass(frozen=True)
class CardMove:
    item_id: str
    source: str
    destination: str
    source_root: str
    destination_root: str
    restored_status: str
    retrospective_ref: str


@dataclass(frozen=True)
class Preflight:
    original_schema_version: int
    original_head: str
    moves: tuple[CardMove, ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _head(project_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def pending_promotion_files(stage_root: Path) -> list[Path]:
    intents_root = stage_root / ".runtime/intents"
    pending: list[Path] = []
    if intents_root.is_dir():
        pending.extend(
            path
            for path in sorted(intents_root.iterdir())
            if path.is_file()
            and (path.name.endswith(".json") or ".json.claim-" in path.name)
        )
    legacy = stage_root / ".runtime/promote-intent.json"
    if legacy.is_file() or legacy.is_symlink():
        pending.append(legacy)
    return pending


def snapshot_tree(stage_root: Path) -> dict[str, bytes]:
    """Return the durable Stage file tree, excluding machine-owned runtime state."""

    snapshot: dict[str, bytes] = {}
    if not stage_root.is_dir():
        return snapshot
    for path in sorted(stage_root.rglob("*")):
        relative = path.relative_to(stage_root)
        if not path.is_file() or relative.parts[0] == ".runtime":
            continue
        snapshot[relative.as_posix()] = path.read_bytes()
    return snapshot


def _encoded_snapshot(stage_root: Path) -> dict[str, str]:
    return {
        relative: base64.b64encode(content).decode("ascii")
        for relative, content in snapshot_tree(stage_root).items()
    }


def _flat_cards(stage_root: Path) -> dict[str, tuple[Path, str, dict[str, Any]]]:
    cards: dict[str, tuple[Path, str, dict[str, Any]]] = {}
    for root_name in WORK_ROOTS:
        root = stage_root / root_name
        if not root.is_dir():
            continue
        # This direct flat scan is intentionally migration-only.  Runtime
        # scanners accept the schema-v5 hierarchy and never branch on v4.
        for path in sorted(root.glob("W-*.md")):
            fields = parse_frontmatter(path)
            item_id = str(fields.get("id") or "").strip()
            if not re.fullmatch(r"W-\d{3,}", item_id):
                raise MigrationError(
                    f"Flat work card has no valid W id: {path.relative_to(stage_root)}"
                )
            if item_id in cards:
                raise MigrationError(f"Duplicate flat work id: {item_id}")
            cards[item_id] = (path, root_name, fields)
    return cards


def _existing_hierarchy(stage_root: Path) -> dict[str, ExistingRecord]:
    records: dict[str, ExistingRecord] = {}
    for root_name in WORK_ROOTS:
        root = stage_root / root_name
        if not root.is_dir():
            continue
        for path in record_paths(root):
            if path.parent == root or path.name in {
                "README.md",
                "_template.md",
                "index.md",
            }:
                continue
            try:
                scale = work_record_scale(root, path)
            except ValueError as exc:
                raise MigrationError(str(exc)) from exc
            fields = parse_frontmatter(path)
            item_id = str(fields.get("id") or "").strip()
            if not re.fullmatch(r"W-\d{3,}", item_id):
                continue
            if item_id in records:
                raise MigrationError(f"Duplicate hierarchical work id: {item_id}")
            records[item_id] = ExistingRecord(
                item_id=item_id,
                root=root_name,
                relative=path.relative_to(stage_root).as_posix(),
                scale=scale,
            )
    return records


def _children(
    cards: dict[str, tuple[Path, str, dict[str, Any]]]
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for item_id, (_path, _root, fields) in cards.items():
        parent = str(fields.get("parent") or "").strip()
        if parent:
            result.setdefault(parent, []).append(item_id)
    return result


def _flat_chain(
    item_id: str,
    cards: dict[str, tuple[Path, str, dict[str, Any]]],
    existing: dict[str, ExistingRecord],
) -> tuple[list[str], ExistingRecord | None]:
    chain = [item_id]
    seen = {item_id}
    cursor = item_id
    while True:
        parent = str(cards[cursor][2].get("parent") or "").strip()
        if not parent:
            return list(reversed(chain)), None
        if parent in seen:
            raise MigrationError(
                "Flat work parent chain forms a cycle: "
                + " -> ".join(list(reversed(chain)) + [parent])
            )
        if parent in existing:
            return list(reversed(chain)), existing[parent]
        if parent not in cards:
            raise MigrationError(
                f"Flat work card {cursor} names missing parent {parent}"
            )
        seen.add(parent)
        chain.append(parent)
        cursor = parent


def _destination_below_existing(
    parent: ExistingRecord, item_id: str
) -> tuple[str, str]:
    parent_path = Path(parent.relative)
    if parent.scale == "epic":
        return (
            parent.root,
            (parent_path.parent / item_id / "_story.md").as_posix(),
        )
    if parent.scale == "story":
        return (
            parent.root,
            (parent_path.parent / f"{item_id}.md").as_posix(),
        )
    raise MigrationError(
        f"Flat work card cannot be placed below action parent {parent.item_id}"
    )


def _destination_for(
    item_id: str,
    cards: dict[str, tuple[Path, str, dict[str, Any]]],
    existing: dict[str, ExistingRecord],
    child_ids: dict[str, list[str]],
) -> tuple[str, str]:
    chain, existing_parent = _flat_chain(item_id, cards, existing)
    if existing_parent is not None:
        root, destination = _destination_below_existing(
            existing_parent, chain[0]
        )
        base = Path(destination)
        if len(chain) == 1:
            return root, destination
        if base.name != "_story.md":
            raise MigrationError(
                f"Parent chain below story {existing_parent.item_id} exceeds action depth"
            )
        if len(chain) > 2:
            raise MigrationError(
                f"Parent chain for {item_id} exceeds epic/story/action depth"
            )
        return root, (base.parent / f"{chain[1]}.md").as_posix()

    root_id = chain[0]
    root = cards[root_id][1]
    root_base = Path(root) / root_id
    if len(chain) == 1:
        name = "_epic.md" if child_ids.get(root_id) else "_story.md"
        return root, (root_base / name).as_posix()
    if len(chain) == 2:
        return root, (root_base / chain[1] / "_story.md").as_posix()
    if len(chain) == 3:
        return root, (root_base / chain[1] / f"{chain[2]}.md").as_posix()
    raise MigrationError(
        f"Parent chain for {item_id} exceeds epic/story/action depth"
    )


def _restored_status(
    fields: dict[str, Any], source_root: str, destination_root: str
) -> str:
    status = str(fields.get("status") or "").strip()
    if source_root == ARCHIVE_ROOT and destination_root != ARCHIVE_ROOT:
        disposition = str(fields.get("terminal_disposition") or "accepted").strip()
        return "rejected" if disposition == "rejected" else "completed"
    if source_root != ARCHIVE_ROOT and destination_root == ARCHIVE_ROOT:
        raise MigrationError(
            f"Open/planned card with status {status!r} cannot move below an archived parent"
        )
    return status


def preflight(project_root: Path, stage_root: Path) -> Preflight:
    if not stage_root.is_dir():
        raise MigrationError(f"Stage root not found: {stage_root}")
    settings_path, settings, error = read_settings(stage_root)
    if error is not None or not isinstance(settings, dict):
        raise MigrationError(f"{settings_path.name} is missing or unreadable")
    version = settings.get("schema_version")
    if type(version) is not int or version != 4:
        raise MigrationError(
            f"Schema-v5 migration requires schema v4; found {version!r}"
        )
    present = [
        relative.as_posix()
        for relative in (MAINTENANCE_MARKER_RELATIVE, JOURNAL_RELATIVE)
        if (stage_root / relative).exists()
    ]
    if present:
        raise MigrationError(
            "An existing schema-v5 migration transaction blocks restart: "
            + ", ".join(present)
            + ". Run the abort path first."
        )
    pending_promotions = pending_promotion_files(stage_root)
    if pending_promotions:
        rendered = ", ".join(
            path.relative_to(stage_root).as_posix()
            for path in pending_promotions
        )
        raise MigrationError(
            "Pending promotion machinery must finish before migration: "
            + rendered
        )

    cards = _flat_cards(stage_root)
    existing = _existing_hierarchy(stage_root)
    overlap = sorted(set(cards) & set(existing))
    if overlap:
        raise MigrationError(
            "Work ids exist in both flat and hierarchical shapes: "
            + ", ".join(overlap)
        )
    child_ids = _children(cards)
    moves: list[CardMove] = []
    destinations: dict[str, str] = {}
    for item_id, (source, source_root, fields) in sorted(cards.items()):
        destination_root, destination = _destination_for(
            item_id, cards, existing, child_ids
        )
        previous = destinations.get(destination)
        if previous is not None:
            raise MigrationError(
                f"Migration destination collision: {previous} and {item_id} -> {destination}"
            )
        destination_path = stage_root / destination
        if destination_path.exists():
            raise MigrationError(
                f"Migration destination already exists: {destination}"
            )
        destinations[destination] = item_id
        moves.append(
            CardMove(
                item_id=item_id,
                source=source.relative_to(stage_root).as_posix(),
                destination=destination,
                source_root=source_root,
                destination_root=destination_root,
                restored_status=_restored_status(
                    fields, source_root, destination_root
                ),
                retrospective_ref=str(
                    fields.get("retrospective_ref") or ""
                ).strip(),
            )
        )
    return Preflight(
        original_schema_version=version,
        original_head=_head(project_root),
        moves=tuple(moves),
    )


def begin(stage_root: Path, checked: Preflight) -> dict[str, Any]:
    journal = {
        "migration": "schema-v4-to-v5",
        "status": "active",
        "started_at": utc_now(),
        "original_head": checked.original_head,
        "original_schema_version": checked.original_schema_version,
        "snapshot": _encoded_snapshot(stage_root),
        "moves": [
            {
                "item_id": move.item_id,
                "source": move.source,
                "destination": move.destination,
                "status": "planned",
            }
            for move in checked.moves
        ],
    }
    _write_json(stage_root / JOURNAL_RELATIVE, journal)
    _write_json(
        stage_root / MAINTENANCE_MARKER_RELATIVE,
        {
            "migration": "schema-v4-to-v5",
            "started_at": journal["started_at"],
            "journal": JOURNAL_RELATIVE.as_posix(),
        },
    )
    return journal


def save_journal(stage_root: Path, journal: dict[str, Any]) -> None:
    _write_json(stage_root / JOURNAL_RELATIVE, journal)


def fail(stage_root: Path, journal: dict[str, Any], reason: str) -> None:
    journal["status"] = "failed"
    journal["failed_at"] = utc_now()
    journal["failure"] = reason
    save_journal(stage_root, journal)


def _without_parent(text: str) -> str:
    lines = text.splitlines(keepends=True)
    in_frontmatter = False
    separators = 0
    output = []
    for line in lines:
        if line.rstrip("\r\n") == "---":
            separators += 1
            in_frontmatter = separators == 1
            output.append(line)
            continue
        if separators == 2:
            in_frontmatter = False
        match = FRONTMATTER_FIELD_RE.match(line.rstrip("\r\n"))
        if in_frontmatter and match is not None and match.group("key") == "parent":
            continue
        output.append(line)
    return "".join(output)


def _set_status(text: str, status: str) -> str:
    lines = text.splitlines(keepends=True)
    in_frontmatter = False
    separators = 0
    for index, line in enumerate(lines):
        if line.rstrip("\r\n") == "---":
            separators += 1
            in_frontmatter = separators == 1
            continue
        if separators == 2:
            in_frontmatter = False
        match = FRONTMATTER_FIELD_RE.match(line.rstrip("\r\n"))
        if in_frontmatter and match is not None and match.group("key") == "status":
            newline = "\n" if line.endswith("\n") else ""
            lines[index] = f"status: {status}{newline}"
            return "".join(lines)
    raise MigrationError("Work card has no status field")


def _move_retrospective(
    stage_root: Path, move: CardMove, journal: dict[str, Any]
) -> None:
    if (
        move.source_root != ARCHIVE_ROOT
        or move.destination_root == ARCHIVE_ROOT
        or not move.retrospective_ref
    ):
        return
    source_root = stage_root / "official/work/archive/retrospectives"
    destination_root = stage_root / "work/retrospectives"
    source = source_root / f"{move.retrospective_ref}.md"
    if not source.is_file():
        return
    destination = destination_root / source.name
    if destination.exists():
        raise MigrationError(
            f"Retrospective destination already exists: {destination.relative_to(stage_root)}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.replace(destination)
    journal.setdefault("retrospectives", []).append(
        {
            "source": source.relative_to(stage_root).as_posix(),
            "destination": destination.relative_to(stage_root).as_posix(),
        }
    )
    save_journal(stage_root, journal)


def relocate_work_records(
    stage_root: Path, checked: Preflight, journal: dict[str, Any]
) -> None:
    by_id = {
        entry["item_id"]: entry
        for entry in journal.get("moves", [])
        if isinstance(entry, dict) and isinstance(entry.get("item_id"), str)
    }
    for move in checked.moves:
        source = stage_root / move.source
        destination = stage_root / move.destination
        if not source.is_file():
            raise MigrationError(f"Migration source disappeared: {move.source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = _without_parent(source.read_text(encoding="utf-8"))
        text = _set_status(text, move.restored_status)
        destination.write_text(text, encoding="utf-8")
        source.unlink()
        _move_retrospective(stage_root, move, journal)
        entry = by_id.get(move.item_id)
        if entry is not None:
            entry["status"] = "done"
        save_journal(stage_root, journal)


def _record_locations(stage_root: Path) -> dict[str, tuple[str, Path]]:
    locations: dict[str, tuple[str, Path]] = {}
    for root_name in WORK_ROOTS:
        root = stage_root / root_name
        if not root.is_dir():
            continue
        for path in record_paths(root):
            if path.name in {"README.md", "_template.md", "index.md"}:
                continue
            try:
                work_record_scale(root, path)
            except ValueError:
                continue
            fields = parse_frontmatter(path)
            item_id = str(fields.get("id") or "").strip()
            if item_id:
                locations[item_id] = (root_name, path)
    return locations


def rewrite_indexes(stage_root: Path) -> list[str]:
    locations = _record_locations(stage_root)
    rewritten: list[str] = []
    for relative, expected_root in INDEX_ROOTS.items():
        path = stage_root / relative
        if not path.is_file():
            continue
        output: list[str] = []
        changed = False
        indexed_ids: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
            row = WORK_ROW_RE.match(line)
            if row is None:
                output.append(line)
                continue
            item_id = row.group("id")
            located = locations.get(item_id)
            if located is None or located[0] != expected_root:
                changed = True
                continue
            indexed_ids.add(item_id)
            destination = posixpath.relpath(
                located[1].relative_to(stage_root).as_posix(),
                relative.parent.as_posix(),
            )

            def replace(match: re.Match[str]) -> str:
                return f"]({destination})"

            updated = MARKDOWN_LINK_RE.sub(replace, line, count=1)
            changed = changed or updated != line
            output.append(updated)
        if relative == Path("work/review.md"):
            for item_id, (root_name, record) in sorted(locations.items()):
                if root_name != CURRENT_ROOT or item_id in indexed_ids:
                    continue
                fields = parse_frontmatter(record)
                status = str(fields.get("status") or "").strip()
                if status not in {"review", "completed", "rejected"}:
                    continue
                destination = posixpath.relpath(
                    record.relative_to(stage_root).as_posix(),
                    relative.parent.as_posix(),
                )
                verification = str(fields.get("verification") or "").strip()
                retrospective = str(fields.get("retrospective") or "").strip()
                promotion = str(fields.get("promotion") or "").strip()
                output.append(
                    f"| {item_id} | {verification} | {retrospective} | "
                    f"{promotion} | [{destination}]({destination}) |\n"
                )
                changed = True
        if changed:
            path.write_text("".join(output), encoding="utf-8")
            rewritten.append(relative.as_posix())
    return rewritten


def _guidance_source(relative: Path, language: str) -> Path:
    if language and language != "en":
        localized = PLUGIN_ROOT / "templates" / "v4" / "locales" / language / relative
        if localized.is_file():
            return localized
    return PLUGIN_ROOT / "templates" / "v4" / "project-stage" / relative


def refresh_work_guidance(
    stage_root: Path, settings: dict[str, object]
) -> list[str]:
    language = settings.get("language")
    language_value = language if isinstance(language, str) else "en"
    overrides = settings.get("guidance_overrides")
    preserved = {
        value for value in overrides if isinstance(value, str)
    } if isinstance(overrides, list) else set()
    refreshed: list[str] = []
    for relative in WORK_GUIDANCE_RELATIVES:
        if relative.as_posix() in preserved:
            continue
        source = _guidance_source(relative, language_value)
        if not source.is_file():
            raise MigrationError(f"Schema-v5 guidance source is missing: {source}")
        target = stage_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file() and target.read_bytes() == source.read_bytes():
            continue
        shutil.copyfile(source, target)
        refreshed.append(relative.as_posix())
    return refreshed


def stamp_schema_version(
    stage_root: Path, settings: dict[str, object], version: int
) -> None:
    settings_path, _data, error = read_settings(stage_root)
    if error is not None:
        raise MigrationError(f"{settings_path.name} is unreadable: {error}")
    write_setting_preserving_comments(
        settings_path, settings, "schema_version", version
    )


def verify_new_shape(stage_root: Path) -> None:
    leftovers = [
        path.relative_to(stage_root).as_posix()
        for root_name in WORK_ROOTS
        for path in sorted((stage_root / root_name).glob("W-*.md"))
    ]
    if leftovers:
        raise MigrationError(
            "Flat schema-v4 work cards remain: " + ", ".join(leftovers)
        )
    for root_name in WORK_ROOTS:
        root = stage_root / root_name
        if not root.is_dir():
            continue
        for path in record_paths(root):
            if path.name in {"README.md", "_template.md", "index.md"}:
                continue
            work_record_scale(root, path)
            fields = parse_frontmatter(path)
            if "parent" in fields:
                raise MigrationError(
                    "Schema-v5 work record still has parent frontmatter: "
                    + path.relative_to(stage_root).as_posix()
                )


def finish(stage_root: Path, journal: dict[str, Any]) -> None:
    journal["status"] = "complete"
    journal["completed_at"] = utc_now()
    save_journal(stage_root, journal)
    for relative in (MAINTENANCE_MARKER_RELATIVE, JOURNAL_RELATIVE):
        try:
            (stage_root / relative).unlink()
        except FileNotFoundError:
            pass


def migrate(
    project_root: Path,
    dry_run: bool,
    *,
    audit: bool = False,
    audit_findings: Callable[[Path], list[Any]] | None = None,
) -> int:
    stage_root = project_root / ".stage"
    settings_path, settings, error = read_settings(stage_root)
    if error is not None or not isinstance(settings, dict):
        print(f"Migration refused: {settings_path.name} is missing or unreadable")
        return 1
    if settings.get("schema_version") == SCHEMA_VERSION:
        print("Stage project already uses schema v5; no migration needed.")
        return 0
    try:
        checked = preflight(project_root, stage_root)
    except MigrationError as exc:
        print(f"Migration refused: {exc}")
        return 1
    if dry_run:
        for move in checked.moves:
            print(f"  move   .stage/{move.source} -> .stage/{move.destination}")
        print("  rewrite work indexes from actual record paths")
        print("  refresh schema-v5 work guidance and templates")
        print("  stamp  settings schema_version = 5 (marker-last)")
        print("Schema-v5 migration plan complete (dry run); no files changed.")
        return 0

    journal = begin(stage_root, checked)
    try:
        relocate_work_records(stage_root, checked, journal)
        journal["rewritten_indexes"] = rewrite_indexes(stage_root)
        decision_index_path = stage_root / refresh_decision_index.INDEX_RELATIVE
        journal["refreshed_decision_index"] = (
            refresh_decision_index.refresh_index(project_root)
            if decision_index_path.is_file()
            else False
        )
        journal["refreshed_guidance"] = refresh_work_guidance(
            stage_root, settings
        )
        save_journal(stage_root, journal)
        verify_new_shape(stage_root)
        stamp_schema_version(stage_root, settings, SCHEMA_VERSION)
        if audit:
            if audit_findings is None:
                import audit_stage

                findings = audit_stage.Audit(project_root).run()
            else:
                findings = audit_findings(project_root)
            findings = [
                finding for finding in findings if finding.severity == "error"
            ]
            if findings:
                detail = "; ".join(
                    f"{finding.severity.upper()} {finding.code}"
                    + (f" [{finding.path}]" if finding.path else "")
                    + f": {finding.message}"
                    for finding in findings[:20]
                )
                raise MigrationError(
                    "Strict post-migration audit failed: " + detail
                )
        finish(stage_root, journal)
    except (MigrationError, OSError, ValueError) as exc:
        fail(stage_root, journal, str(exc))
        print(f"Schema-v5 migration stopped fail-closed: {exc}")
        print(
            "The maintenance marker remains. Run migrate_stage.py --abort "
            "before any commit to restore the exact pre-migration tree."
        )
        return 1
    print(
        f"Schema-v5 migration complete: {len(checked.moves)} flat work card(s) "
        "moved into the hierarchy."
    )
    print(
        "This command does not commit. Its successful transaction journal was removed; "
        "review the working tree before committing."
    )
    return 0


def abort(project_root: Path, stage_root: Path) -> int:
    journal = _load_json(stage_root / JOURNAL_RELATIVE)
    if journal is None:
        print(
            "No schema-v5 migration journal exists; there is no deterministic "
            "migration to abort."
        )
        return 1
    if (
        journal.get("migration") != "schema-v4-to-v5"
        or journal.get("status") not in {"active", "failed"}
    ):
        print(
            "Schema-v5 migration journal does not describe the active or failed "
            "schema-v4-to-v5 transaction; abort is refused."
        )
        return 1
    original_head = journal.get("original_head")
    current_head = _head(project_root)
    if (
        isinstance(original_head, str)
        and original_head
        and current_head
        and current_head != original_head
    ):
        print(
            "The migration has been committed (HEAD changed). --abort is refused; "
            "use git revert <migration-commit>."
        )
        return 1
    encoded = journal.get("snapshot")
    if not isinstance(encoded, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in encoded.items()
    ):
        print("Schema-v5 migration journal has no valid snapshot; abort is refused.")
        return 1

    for path in sorted(
        (
            candidate
            for candidate in stage_root.rglob("*")
            if candidate.is_file()
            and candidate.relative_to(stage_root).parts[0] != ".runtime"
        ),
        reverse=True,
    ):
        path.unlink()
    for path in sorted(
        (
            candidate
            for candidate in stage_root.rglob("*")
            if candidate.is_dir()
            and candidate.relative_to(stage_root).parts[0] != ".runtime"
        ),
        key=lambda candidate: len(candidate.parts),
        reverse=True,
    ):
        try:
            path.rmdir()
        except OSError:
            pass
    for relative, value in encoded.items():
        target = stage_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(value.encode("ascii")))
    for relative in (MAINTENANCE_MARKER_RELATIVE, JOURNAL_RELATIVE):
        try:
            (stage_root / relative).unlink()
        except FileNotFoundError:
            pass
    print("Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.")
    return 0
