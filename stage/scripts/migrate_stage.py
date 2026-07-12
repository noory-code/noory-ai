#!/usr/bin/env python3
"""Migrate a project-local .stage to the v2 plugin-owned operations layout.

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

from stage_paths import STAGE_SCHEMA_VERSION  # noqa: E402
from stage_work import parse_frontmatter  # noqa: E402

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
        description="Migrate .stage to the v2 plugin-owned operations layout."
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
    return parser.parse_args()


def plugin_common_docs() -> dict[str, Path]:
    return {
        path.name: path
        for path in sorted(OPERATIONS_ROOT.glob("*.md"))
        if path.name not in PROJECT_OWNED_NAMES
    }


def load_settings(stage_root: Path) -> dict[str, object] | None:
    settings_path = stage_root / "settings.json"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
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


def stamp_schema_version(stage_root: Path, settings: dict[str, object], dry_run: bool) -> None:
    settings["schema_version"] = STAGE_SCHEMA_VERSION
    settings.setdefault("operations_overrides", [])
    if not dry_run:
        (stage_root / "settings.json").write_text(
            json.dumps(settings, indent=2) + "\n", encoding="utf-8"
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


def migrate(project_root: Path, dry_run: bool) -> int:
    stage_root = project_root / ".stage"
    if not stage_root.is_dir():
        print(f"Stage root not found: {stage_root}")
        return 1
    settings = load_settings(stage_root)
    if settings is None:
        print("settings.json is missing or unreadable; repair it first.")
        return 1

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

    migrate_backlog(stage_root, dry_run)

    if drift:
        print(f"Unresolved ownership drift: {len(drift)} file(s); schema_version not stamped.")
        return 1
    if settings.get("schema_version") != STAGE_SCHEMA_VERSION:
        stamp_schema_version(stage_root, settings, dry_run)
        print(f"  stamp  settings.json schema_version = {STAGE_SCHEMA_VERSION}")
    print("Migration " + ("plan complete (dry run)." if dry_run else "complete."))
    return 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    raise SystemExit(migrate(project_root, args.dry_run))


if __name__ == "__main__":
    main()
