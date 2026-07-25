#!/usr/bin/env python3
"""Migrate a project-local .stage through the current Stage schema.

Contract (DE-00000002): common operations docs are plugin-owned and no longer
copied into consuming projects. This migration is idempotent and never deletes
content that differs from the current plugin copy:

- a project common doc byte-identical to the plugin copy is deleted (and its
  index.md routing row dropped);
- a differing, undeclared copy is kept and reported — declare it in
  settings.json `operations_overrides` or remove it, then re-run;
- `operations/verification.md` is rewritten to the project-policy form
  (kind -> passed table only) when its prose matches the known legacy
  template; otherwise it is kept untouched and reported;
- `schema_version` is stamped only once no undeclared drift remains.

v3 (DE-00000007): backlog entries become planned `W-` work cards and the `B-`
family retires. A realized or rejected `B-` item is removed from the tree (its
execution record lives in the archived work card; git history keeps the file);
any other `B-` item converts to a planned `W-` card with a fresh id and its
body preserved. Never deletes a body that has no surviving record.

v4 (W-00000037): perform the fail-closed one-shot responsibility-topology
relocation through ``stage_topology.V3_TO_V4_RELOCATIONS``. The transaction
uses git moves, a runtime maintenance marker and journal, marker-last schema
stamping, an audit that allows guidance-drift warnings to remain visible for
the explicit refresh command, and a deterministic pre-commit ``--abort`` path.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
OPERATIONS_ROOT = PLUGIN_ROOT / "operations"
HOOK_ROOT = PLUGIN_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from stage_paths import (  # noqa: E402
    STAGE_SCHEMA_VERSION,
    read_settings,
    write_setting_preserving_comments,
)
from stage_work import parse_frontmatter  # noqa: E402
import stage_schema_v4_migration as v4_migration  # noqa: E402

# The project policy surface and plain directory docs are never treated as
# shadows of plugin-owned common docs.
PROJECT_OWNED_NAMES = frozenset({"verification.md", "README.md"})

# Non-table lines of every template generation that shipped verification.md
# as a copied common doc. A project verification.md whose prose stays within
# this set carries no project-authored prose and is safe to rewrite.
LEGACY_VERIFICATION_PROSE = frozenset(
    {
        "# Verification",
        "This document owns the verification rules.",
        "## Rules",
        "- Both external-perspective and internal-perspective completion are required.",
        "- Tests or equivalent verification must match the change.",
        "- If the project declares a linter or formatter (a config file or a documented "
        "command exists), it must pass; if none is declared, this criterion is skipped.",
        "- New behavior needs a verification path.",
        "- `verification: passed` records evidence produced in the session that sets it — "
        "the stated checks actually run, with their output observed, not the checks that "
        "were merely supposed to run.",
        "- Work without a retrospective is not complete.",
        "## What `passed` means per kind",
        "`verification: passed` on a work item is valid only against the criterion declared "
        "for its `kind`. Projects extend this table; the audit warns when a work item uses "
        "a kind that has no row here.",
    }
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate a project-local .stage through the current schema."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing .stage. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the planned actions without changing any file.",
    )
    parser.add_argument(
        "--abort",
        action="store_true",
        help=(
            "Restore migration-owned staged/working-tree changes before the migration "
            "is committed. After commit, use git revert instead."
        ),
    )
    return parser.parse_args()


def plugin_common_docs() -> dict[str, Path]:
    return {
        path.name: path
        for path in sorted(OPERATIONS_ROOT.glob("*.md"))
        if path.name not in PROJECT_OWNED_NAMES
    }


def load_settings(stage_root: Path) -> dict[str, object] | None:
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return None
    return data if isinstance(data, dict) else None


def declared_overrides(settings: dict[str, object]) -> set[str]:
    overrides = settings.get("operations_overrides")
    if isinstance(overrides, list):
        return {name for name in overrides if isinstance(name, str)}
    return set()


def table_data_rows(lines: list[str]) -> list[str]:
    rows: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        first = stripped.strip("|").split("|")[0].strip().strip("`")
        if first.lower() == "kind" or set(first) <= {"-", ":", " "}:
            continue
        rows.append(stripped)
    return rows


def rewrite_verification(project_file: Path, dry_run: bool) -> str:
    """Rewrite verification.md to the project-policy form; return the action."""
    template_file = TEMPLATE_ROOT / "operations" / "verification.md"
    template_lines = template_file.read_text(encoding="utf-8").splitlines()
    project_lines = project_file.read_text(encoding="utf-8").splitlines()

    if project_lines == template_lines:
        return "unchanged"

    explainable = LEGACY_VERIFICATION_PROSE | {
        line.strip() for line in template_lines if not line.strip().startswith("|")
    }
    for line in project_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("|"):
            continue
        if stripped not in explainable:
            return "kept (project-authored prose; review manually)"

    prefix = []
    for line in template_lines:
        prefix.append(line)
        if set(line.strip().strip("|").replace("|", "").strip()) <= {"-", ":", " "} and (
            line.strip().startswith("|")
        ):
            break
    body = "\n".join(prefix + table_data_rows(project_lines)) + "\n"
    if not dry_run:
        project_file.write_text(body, encoding="utf-8")
    return "rewritten (kind table preserved)"


def drop_index_rows(stage_root: Path, deleted: list[str], dry_run: bool) -> int:
    index_path = stage_root / "index.md"
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0
    targets = {f"`operations/{name}`" for name in deleted}
    kept = [
        line
        for line in lines
        if not (line.lstrip().startswith("|") and any(target in line for target in targets))
    ]
    dropped = len(lines) - len(kept)
    if dropped and not dry_run:
        index_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return dropped


def stamp_schema_version(
    stage_root: Path,
    settings: dict[str, object],
    version: int,
    dry_run: bool,
) -> None:
    settings["schema_version"] = version
    settings.setdefault("operations_overrides", [])
    if not dry_run:
        settings_path, _data, error = read_settings(stage_root)
        if error is not None:
            raise error
        write_setting_preserving_comments(
            settings_path, settings, "schema_version", version
        )


def next_work_number(stage_root: Path) -> int:
    numbers = [0]
    id_re = re.compile(r"^W-(\d{3,})")
    for base in ("present/work/items", "past/work/archive/items", "future/backlog/items"):
        for path in (stage_root / base).glob("W-*.md"):
            match = id_re.match(path.stem)
            if match:
                numbers.append(int(match.group(1)))
    return max(numbers) + 1


def migrate_backlog(stage_root: Path, dry_run: bool) -> None:
    """v3: convert `B-` backlog items to planned `W-` work cards (DE-00000007)."""
    backlog_dir = stage_root / "future" / "backlog" / "items"
    index_path = stage_root / "future" / "backlog" / "index.md"
    if not backlog_dir.is_dir():
        return
    b_files = [
        path
        for path in sorted(backlog_dir.glob("B-*.md"))
        if path.name not in ("README.md", "_template.md")
    ]
    if not b_files:
        return

    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    id_map: dict[str, str] = {}
    number = next_work_number(stage_root)
    removed: list[str] = []

    for path in b_files:
        fields = parse_frontmatter(path)
        old_id = (fields.get("id") or path.stem).strip()
        status = (fields.get("status") or "").strip().lower()
        realized = bool((fields.get("realized_by") or "").strip())
        if realized or status == "rejected":
            if not dry_run:
                path.unlink()
            removed.append(old_id)
            reason = "realized by " + fields.get("realized_by", "") if realized else "rejected"
            print(f"  delete backlog {path.name} ({reason.strip()}; git history keeps the file)")
            continue
        new_id = f"W-{number:08d}"
        number += 1
        id_map[old_id] = new_id
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^id:[ \t]*.*$", f"id: {new_id}", text, count=1, flags=re.MULTILINE)
        text = re.sub(
            r"^realized_by:[ \t]*.*\n", "", text, count=1, flags=re.MULTILINE
        )
        text = text.replace(f"# {old_id}", f"# {new_id}", 1)
        if not dry_run:
            (backlog_dir / f"{new_id}.md").write_text(text, encoding="utf-8")
            path.unlink()
        print(f"  convert backlog {path.name} -> {new_id}.md (planned work card)")
        index_text = index_text.replace(f"| {old_id} |", f"| {new_id} |").replace(
            f"(items/{path.name})", f"(items/{new_id}.md)"
        )

    # Parent references between converted cards follow the id map.
    for old_id, new_id in id_map.items():
        for path in backlog_dir.glob("W-*.md"):
            text = path.read_text(encoding="utf-8")
            if f"parent: {old_id}" in text:
                if not dry_run:
                    path.write_text(
                        text.replace(f"parent: {old_id}", f"parent: {new_id}"),
                        encoding="utf-8",
                    )

    if index_path.exists():
        lines = index_text.splitlines()
        kept = [
            line
            for line in lines
            if not (
                line.lstrip().startswith("|")
                and any(f"| {old_id} |" in line for old_id in removed)
            )
        ]
        if not dry_run:
            index_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
        if len(kept) != len(lines):
            print(f"  update backlog index ({len(lines) - len(kept)} closed rows removed)")


def migrate_operations(
    stage_root: Path, settings: dict[str, object], dry_run: bool
) -> list[str]:
    overrides = declared_overrides(settings)
    operations_root = stage_root / "operations"
    deleted: list[str] = []
    drift: list[str] = []

    for name, plugin_path in plugin_common_docs().items():
        project_path = operations_root / name
        if not project_path.is_file():
            continue
        if name in overrides:
            print(f"  keep   operations/{name} (declared override)")
            continue
        if project_path.read_bytes() == plugin_path.read_bytes():
            if not dry_run:
                project_path.unlink()
            deleted.append(name)
            print(f"  delete operations/{name} (identical to the plugin-owned copy)")
        else:
            drift.append(name)
            print(
                f"  keep   operations/{name} (differs from the plugin-owned copy; "
                "declare it in operations_overrides or remove it, then re-run)"
            )

    verification = operations_root / "verification.md"
    if verification.is_file():
        action = rewrite_verification(verification, dry_run)
        print(f"  {action.split(' ')[0].ljust(6)} operations/verification.md ({action})")

    dropped = drop_index_rows(stage_root, deleted, dry_run)
    if dropped:
        print(f"  update index.md ({dropped} routing rows for deleted docs removed)")

    return drift


def strict_audit_findings(project_root: Path):
    import audit_stage

    return [
        finding
        for finding in audit_stage.Audit(project_root).run()
        if finding.code != "TEMPLATE004"
    ]


def abort(project_root: Path) -> int:
    stage_root = project_root / ".stage"
    if not stage_root.exists():
        print(f"Stage root not found: {stage_root}")
        return 1
    return v4_migration.abort(project_root, stage_root)


def migrate(project_root: Path, dry_run: bool) -> int:
    stage_root = project_root / ".stage"
    if not stage_root.exists():
        print(f"Stage root not found: {stage_root}")
        return 1
    if not stage_root.is_dir():
        print(f"Stage root is not a directory: {stage_root}")
        return 1
    settings = load_settings(stage_root)
    if settings is None:
        print("settings.json is missing or unreadable; repair it first.")
        return 1
    schema_version = settings.get("schema_version")
    if type(schema_version) is int and schema_version > STAGE_SCHEMA_VERSION:
        print(
            f"Project schema v{schema_version} is newer than this plugin's "
            f"v{STAGE_SCHEMA_VERSION} contract; migration is refused."
        )
        return 1
    if type(schema_version) is int and schema_version == STAGE_SCHEMA_VERSION:
        print(f"Stage project already uses schema v{STAGE_SCHEMA_VERSION}; no migration needed.")
        return 0

    try:
        checked = v4_migration.preflight(
            project_root, stage_root, settings, dry_run
        )
    except v4_migration.MigrationError as exc:
        print(f"Migration refused: {exc}")
        return 1

    if dry_run:
        drift = migrate_operations(stage_root, settings, True)
        migrate_backlog(stage_root, True)
        if drift:
            print(
                f"Unresolved ownership drift: {len(drift)} file(s); migration would stop."
            )
            return 1
        for origin, destination in checked.moves:
            print(f"  move   .stage/{origin} -> .stage/{destination}")
        print("  patch  .stage/index.md (recognized topology section only)")
        print(f"  stamp  settings.json schema_version = {STAGE_SCHEMA_VERSION} (marker-last)")
        print("Migration plan complete (dry run); no files or git state changed.")
        return 0

    print(
        "Preflight passed. Close every other agent/editor window before continuing; "
        "the schema-v4 maintenance marker now denies concurrent Stage writes."
    )
    journal = v4_migration.begin(stage_root, checked, schema_version)
    try:
        drift = migrate_operations(stage_root, settings, False)
        if drift:
            raise v4_migration.MigrationError(
                f"Unresolved ownership drift: {len(drift)} file(s); schema_version was not stamped."
            )

        migrate_backlog(stage_root, False)
        # The v2->v3 compatibility pass can replace tracked backlog files before
        # the v3 directory itself is relocated.  Record that intermediate state
        # in the index so the following registry-driven ``git mv`` can move the
        # directory as one unit.  Runtime transaction files remain unstaged.
        v4_migration.stage_changes(project_root)
        v4_migration.relocate(project_root, stage_root, checked, journal)
        rewritten = v4_migration.rewrite_moved_markdown(stage_root)
        journal["rewritten"] = rewritten
        v4_migration.save_journal(stage_root, journal)
        v4_migration.create_v4_indexes(stage_root, settings, journal)
        # Compatibility migrations above may have narrowly edited routing rows.
        # Rebuild the already-recognized topology patch from that current index so
        # those edits are not overwritten by the preflight snapshot.
        patched_index = v4_migration.prepare_index_patch(stage_root, settings, False)
        v4_migration.patch_project_index(stage_root, patched_index, journal)

        leftovers = v4_migration.verify_no_legacy_references(stage_root)
        if leftovers:
            raise v4_migration.MigrationError(
                "Post-relocation verification found a legacy reference in a durable "
                "machine-readable field or live document link: " + ", ".join(leftovers)
            )

        stamp_schema_version(
            stage_root, settings, STAGE_SCHEMA_VERSION, False
        )
        print(f"  stamp  settings.json schema_version = {STAGE_SCHEMA_VERSION}")
        v4_migration.stage_changes(project_root)

        findings = strict_audit_findings(project_root)
        if findings:
            stamp_schema_version(stage_root, settings, 3, False)
            v4_migration.stage_changes(project_root)
            detail = "; ".join(
                f"{finding.severity.upper()} {finding.code}"
                + (f" [{finding.path}]" if finding.path else "")
                + f": {finding.message}"
                for finding in findings[:20]
            )
            raise v4_migration.MigrationError(
                "Strict post-migration audit failed; settings.json was restored to the "
                f"schema-v3 marker. Findings: {detail}"
            )

        v4_migration.finish(stage_root, journal)
    except (v4_migration.MigrationError, OSError, ValueError) as exc:
        v4_migration.fail(stage_root, journal, str(exc))
        print(f"Migration stopped fail-closed: {exc}")
        print(
            "The maintenance marker remains. Before any commit, run the stage-migrate "
            "abort path (`migrate_stage.py --abort`) to restore the clean v3 tree."
        )
        return 1

    print(
        "Schema-v4 migration complete with no blocking audit findings. Guidance drift remains "
        "a non-blocking audit warning until the explicit refresh command is run."
    )
    print(
        "All migration changes are staged; this command does not commit. Review them, then "
        "commit with: git commit -m \"chore(stage): migrate project harness to schema v4\""
    )
    print(
        "Before committing, `migrate_stage.py --abort` restores the staged/working tree. "
        "After committing, rollback means `git revert <migration-commit>`."
    )
    return 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    if args.abort and args.dry_run:
        print("--abort and --dry-run are mutually exclusive.")
        raise SystemExit(2)
    raise SystemExit(abort(project_root) if args.abort else migrate(project_root, args.dry_run))


if __name__ == "__main__":
    main()
