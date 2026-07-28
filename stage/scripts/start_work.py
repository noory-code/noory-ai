#!/usr/bin/env python3
"""Start a planned work card: move it from work/planned to work/current.

The card keeps its identity (DE-00000007); starting is a physical move plus the
work-field upgrade. This script enforces at the move what registration enforces
for direct present items: venue derivation from `venue_routing`, refusal of
split-marked kinds and policy-contradicting venues without a validated
exception decision (DE-00000005), and the mandatory `scope` declaration the
registration gate matches writes against.

Usage:
    start_work.py --project-root . W-00000001 --scope "src, docs" \
        [--venue claude] [--decision DE-00000001] [--owner claude]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
from lifecycle_paths import relative_record_link, v4_lifecycle_paths  # noqa: E402
from stage_record_paths import (  # noqa: E402
    record_path,
    record_paths,
    top_level_item_path,
    work_record_scale,
)
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    load_venue_routing,
    schema_migration_banner,
)
from stage_work import (  # noqa: E402
    VENUE_SPLIT_TOKEN,
    WORK_PLANNED_STATUSES,
    format_yaml_string_list,
    parse_bool_field,
    parse_frontmatter,
    parse_string_list,
    venue_exception_error,
)

# Work fields a present card must carry, in template order, with start values.
WORK_FIELD_DEFAULTS = (
    ("status", "active"),
    ("verification", "pending"),
    ("retrospective", "pending"),
    ("retrospective_ref", ""),
    ("promotion", "pending"),
    ("review", "not_required"),
    ("autonomous", "false"),
    ("scope", ""),
    ("promotes", ""),
    ("decision_refs", ""),
)
FRONTMATTER_ORDER = (
    "id",
    "title",
    "kind",
    "venue",
    "priority",
    "autonomous",
    "acceptance",
    "status",
    "verification",
    "retrospective",
    "retrospective_ref",
    "promotion",
    "review",
    "scope",
    "promotes",
    "decision_refs",
)
RECORD_SECTIONS = ("## Progress", "## Verification", "## Retrospective", "## Promotion decision")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move a planned card to present and start work.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("item", help="Planned card id (W-*) in work/planned.")
    parser.add_argument(
        "--scope",
        required=True,
        help="Paths this work may modify; the registration gate matches writes against these.",
    )
    parser.add_argument("--venue", default="", help="Override the venue derived from venue_routing.")
    parser.add_argument(
        "--decision",
        default="",
        help="Decision record id authorizing a venue-policy exception "
        "(decided/promoted with `authorizes: venue_exception`).",
    )
    parser.add_argument("--owner", default="", help="Owner shown in the active.md row.")
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="Mark the work item eligible for autonomous execution.",
    )
    parser.add_argument(
        "--acceptance",
        action="append",
        default=[],
        help="Stored verification command to add (repeatable).",
    )
    return parser.parse_args()


def body_after_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


def build_frontmatter(fields: dict[str, Any]) -> str:
    lines = ["---"]
    order = list(FRONTMATTER_ORDER)
    if (fields.get("parent") or "").strip():
        order.insert(order.index("venue") + 1, "parent")
    if "milestone" in fields:
        anchor = "parent" if "parent" in order else "venue"
        order.insert(order.index(anchor) + 1, "milestone")
    for key in order:
        if key == "acceptance":
            values = parse_string_list(fields.get(key))
            rendered = format_yaml_string_list(values)
            separator = "" if rendered.startswith("\n") else " "
            lines.append(f"{key}:{separator}{rendered}")
        else:
            lines.append(f"{key}: {fields.get(key, '')}".rstrip())
    lines.append("---")
    return "\n".join(lines) + "\n"


def ensure_record_sections(body: str) -> str:
    for section in RECORD_SECTIONS:
        if section + "\n" not in body and not body.rstrip().endswith(section):
            body = body.rstrip() + f"\n\n{section}\n"
    return body.rstrip() + "\n"


def started_fields(
    fields: dict[str, Any],
    *,
    scope: str | None,
    decision: str,
) -> dict[str, Any]:
    fields = dict(fields)
    if not (fields.get("parent") or "").strip():
        fields.pop("parent", None)
    original_status = (fields.get("status") or "").strip().lower()
    for key, default in WORK_FIELD_DEFAULTS:
        if key == "scope":
            if scope is not None:
                fields[key] = scope
        elif key == "decision_refs":
            existing = (fields.get(key) or "").strip()
            if decision and decision not in existing:
                fields[key] = f"{existing}, {decision}".strip(", ")
            else:
                fields[key] = existing
        elif key == "status":
            fields[key] = original_status if original_status == "rejected" else "active"
        else:
            fields.setdefault(key, default)
            if not fields[key]:
                fields[key] = default
    return fields


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    stage_root = project_root / ".stage"
    schema_blocker = schema_migration_banner(stage_root)
    if schema_blocker:
        print(schema_blocker, file=sys.stderr)
        return 2
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        planned_root = paths.planned_cards
        current_root = paths.current_cards
        index_relative = paths.planned_index
        active_relative = paths.active_index
        review_relative = paths.review_index
    else:
        planned_root = Path("future", "backlog", "items").as_posix()
        current_root = Path("present", "work", "items").as_posix()
        index_relative = Path("future", "backlog", "index.md").as_posix()
        active_relative = Path("present", "work", "active.md").as_posix()
        review_relative = Path("present", "work", "review.md").as_posix()

    source_path = record_path(stage_root / planned_root, args.item)
    if not source_path.is_file():
        candidates = record_paths(
            stage_root / planned_root, pattern=f"{args.item}-*.md"
        )
        if len(candidates) == 1:
            source_path = candidates[0]
        else:
            print(f"{args.item}: no planned card in {planned_root}", file=sys.stderr)
            return 1
    planned_dir = stage_root / planned_root
    current_dir = stage_root / current_root
    source_unit = top_level_item_path(planned_dir, source_path)
    target_unit = current_dir / source_unit.name
    if source_unit.is_dir():
        scale = work_record_scale(planned_dir, source_path)
        if scale not in {"epic", "story"} or source_path.parent != source_unit:
            print(
                f"{args.item}: start the top-level epic or story, not a nested item",
                file=sys.stderr,
            )
            return 1
        target_path = target_unit / source_path.relative_to(source_unit)
    else:
        target_path = target_unit
    if target_unit.exists():
        print(f"{args.item}: already exists in {current_root}", file=sys.stderr)
        return 1
    if not args.scope.strip() or args.scope.strip() == ".":
        print(f"{args.item}: --scope must declare the paths this work owns", file=sys.stderr)
        return 1

    text = source_path.read_text(encoding="utf-8")
    fields = parse_frontmatter(source_path)
    status = (fields.get("status") or "").strip().lower()
    if status not in WORK_PLANNED_STATUSES or status == "rejected":
        print(f"{args.item}: status `{status}` is not a startable planned status", file=sys.stderr)
        return 1

    acceptance = list(parse_string_list(fields.get("acceptance")))
    acceptance.extend(command for command in args.acceptance if command.strip())
    autonomous = args.autonomous or parse_bool_field(fields.get("autonomous"))
    if autonomous and not acceptance:
        print(
            f"{args.item}: autonomous work requires at least one --acceptance command",
            file=sys.stderr,
        )
        return 1
    fields["autonomous"] = "true" if autonomous else "false"
    fields["acceptance"] = acceptance

    kind = (fields.get("kind") or "").strip().lower()
    venue = args.venue or (fields.get("venue") or "").strip()
    routing = load_venue_routing(stage_root)
    routed = routing.get(kind, "")
    exception_reason = ""
    if routed == VENUE_SPLIT_TOKEN:
        exception_reason = (
            f"kind `{kind}` is declared mixed (`{VENUE_SPLIT_TOKEN}`): split this card into "
            "design and implementation hierarchy records, or pass --decision <DE-id> "
            "naming a decided decision with `authorizes: venue_exception`"
        )
    elif not venue and routed:
        venue = routed
        print(f"venue derived from venue_routing: {kind} -> {routed}")
    elif venue and routed and venue != routed:
        exception_reason = (
            f"venue `{venue}` contradicts venue_routing ({kind} -> {routed}); pass "
            "--decision <DE-id> naming a decided decision with `authorizes: venue_exception`"
        )

    if args.decision:
        error = venue_exception_error(stage_root, args.decision)
        if error:
            print(f"refusing: {error}", file=sys.stderr)
            return 1
        print(f"venue exception authorized by {args.decision}")
    elif exception_reason:
        print(f"refusing: {exception_reason}", file=sys.stderr)
        return 1

    fields["venue"] = venue
    fields = started_fields(fields, scope=args.scope, decision=args.decision)

    body = body_after_frontmatter(text)
    body = ensure_record_sections(body)

    source_records = (
        tuple(
            path
            for path in record_paths(planned_dir)
            if top_level_item_path(planned_dir, path) == source_unit
        )
        if source_unit.is_dir()
        else (source_path,)
    )
    deferred = [
        path
        for path in source_records
        if (parse_frontmatter(path).get("status") or "").strip().lower()
        == "deferred"
    ]
    if deferred:
        detail = ", ".join(
            (parse_frontmatter(path).get("id") or path.stem)
            for path in deferred
        )
        print(
            f"{args.item}: deferred descendants must be resolved before the "
            f"top-level hierarchy starts: {detail}",
            file=sys.stderr,
        )
        return 1
    rejected_containers = {
        path.parent
        for path in source_records
        if (parse_frontmatter(path).get("status") or "").strip().lower()
        == "rejected"
    }
    started_records: dict[Path, tuple[dict[str, Any], str]] = {
        source_path.relative_to(source_unit): (
            fields,
            build_frontmatter(fields) + "\n" + body,
        )
    }
    for child_path in source_records:
        if child_path == source_path:
            continue
        child_fields = parse_frontmatter(child_path)
        if any(
            container == child_path.parent or container in child_path.parents
            for container in rejected_containers
        ):
            child_fields["status"] = "rejected"
        child_kind = (child_fields.get("kind") or "").strip().lower()
        child_venue = (child_fields.get("venue") or "").strip()
        child_routed = routing.get(child_kind, "")
        if not child_venue and child_routed and child_routed != VENUE_SPLIT_TOKEN:
            child_fields["venue"] = child_routed
        child_fields = started_fields(
            child_fields,
            scope=(
                str(child_fields.get("scope") or "").strip()
                or args.scope
            ),
            decision=args.decision,
        )
        child_body = ensure_record_sections(
            body_after_frontmatter(child_path.read_text(encoding="utf-8"))
        )
        started_records[child_path.relative_to(source_unit)] = (
            child_fields,
            build_frontmatter(child_fields) + "\n" + child_body,
        )

    moved_ids = {
        item_id
        for record_fields, _content in started_records.values()
        if isinstance((item_id := record_fields.get("id")), str) and item_id
    }
    source_unit.rename(target_unit)
    for relative, (_record_fields, content) in started_records.items():
        (target_unit / relative).write_text(content, encoding="utf-8")

    active_path = stage_root / active_relative
    active_text = active_path.read_text(encoding="utf-8") if active_path.exists() else ""
    review_path = stage_root / review_relative
    review_text = review_path.read_text(encoding="utf-8") if review_path.exists() else ""
    for relative, (record_fields, _content) in started_records.items():
        record_status = (record_fields.get("status") or "").strip().lower()
        if record_status == "rejected":
            record_id = (record_fields.get("id") or "").strip()
            record_link = relative_record_link(
                review_relative,
                (target_unit / relative).relative_to(stage_root).as_posix(),
            )
            if not re.search(rf"\({re.escape(record_link)}\)", review_text):
                row = (
                    f"| {record_id} | {record_fields.get('verification', '')} | "
                    f"{record_fields.get('retrospective', '')} | "
                    f"{record_fields.get('promotion', '')} | "
                    f"[{record_link}]({record_link}) |"
                )
                review_text = review_text.rstrip("\n") + "\n" + row + "\n"
            continue
        record_id = (record_fields.get("id") or "").strip()
        record_kind = (record_fields.get("kind") or "").strip()
        record_venue = (record_fields.get("venue") or "").strip()
        record_title = (record_fields.get("title") or "").strip()[:60]
        record_link = relative_record_link(
            active_relative, (target_unit / relative).relative_to(stage_root).as_posix()
        )
        if re.search(rf"\({re.escape(record_link)}\)", active_text):
            continue
        row = (
            f"| {record_id} | {record_kind} | {record_venue} | {record_title} | active | "
            f"{args.owner or record_venue} | [{record_link}]({record_link}) |"
        )
        active_text = active_text.rstrip("\n") + "\n" + row + "\n"
    active_path.write_text(active_text, encoding="utf-8")
    review_path.write_text(review_text, encoding="utf-8")

    index_path = stage_root / index_relative
    if index_path.exists():
        lines = index_path.read_text(encoding="utf-8").splitlines()
        kept = [
            line
            for line in lines
            if not (
                line.lstrip().startswith("|")
                and any(line.lstrip().startswith(f"| {item_id} |") for item_id in moved_ids)
            )
        ]
        if len(kept) != len(lines):
            index_path.write_text("\n".join(kept) + "\n", encoding="utf-8")

    print(f"{args.item}: started (moved to {current_root}, status active)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
