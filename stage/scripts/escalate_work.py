#!/usr/bin/env python3
"""Escalate active/review Stage work to blocked plus a pending decision.

Usage:
    escalate_work.py --project-root . W-00000001 \
        --reason "Why work is blocked and what human decision is needed."
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
    hierarchy_parent_record_path,
    record_path,
    record_paths,
    work_record_scale,
)
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    schema_migration_banner,
)
from stage_work import parse_frontmatter, split_scope  # noqa: E402
import refresh_decision_index  # noqa: E402


ESCALATABLE_STATUSES = {"active", "review"}
DECISION_ID_RE = re.compile(r"^DE-(\d+)(?:-.*)?\.md$")
SECTION_HEADINGS = (
    "Question",
    "Options",
    "Principles applied",
    "Chosen direction",
    "Reason",
    "Follow-up",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Block an open work item and create its pending escalation decision."
    )
    parser.add_argument("--project-root", default=".", help="Project root (default: cwd).")
    parser.add_argument("item", help="Active/review work item id (W-*).")
    parser.add_argument(
        "--reason",
        required=True,
        help="Why work is blocked and what human decision is needed.",
    )
    return parser.parse_args()


def set_field(text: str, name: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(name)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def set_or_insert_field(text: str, name: str, value: str, *, after: str) -> str:
    updated = set_field(text, name, value)
    if updated != text or re.search(rf"^{re.escape(name)}:", text, re.MULTILINE):
        return updated
    inserted, count = re.subn(
        rf"^({re.escape(after)}:[^\n]*\n)",
        rf"\g<1>{name}: {value}\n",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"work card has no `{name}:` or `{after}:` field")
    return inserted


def next_decision_id(stage_root: Path) -> str:
    highest = 0
    for relative in ("decisions/pending", "official/decisions/records"):
        root = stage_root / relative
        for path in record_paths(root, pattern="DE-*.md") if root.exists() else ():
            match = DECISION_ID_RE.fullmatch(path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"DE-{highest + 1:08d}"


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = re.compile(
        rf"(^## {re.escape(heading)}[ \t]*\n)(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    updated, count = pattern.subn(
        lambda match: f"{match.group(1)}\n{body.strip()}\n\n", text, count=1
    )
    if count != 1:
        raise ValueError(f"decision template has no `## {heading}` section")
    return updated


def render_decision(
    template: str,
    decision_id: str,
    item_id: str,
    reason: str,
    *,
    failed_action: str = "",
) -> str:
    rendered = set_field(template, "id", decision_id)
    rendered = set_field(rendered, "work_item", item_id)
    rendered = set_field(rendered, "status", "open")
    rendered, count = re.subn(
        r"^# DE-[0-9]+(?:-[^ ]+)? .*$",
        f"# {decision_id} Escalation required for {item_id}",
        rendered,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("decision template has no decision title")

    question = reason
    follow_up = (
        f"After the decision is resolved, explicitly transition {item_id} before resuming work."
    )
    if failed_action:
        question = (
            f"Action {failed_action} failed within story {item_id}. {reason} "
            "How must the story be decomposed again?"
        )
        follow_up = (
            f"Read the evidence for failed action {failed_action}, then re-decompose story "
            f"{item_id} by splitting, merging, or redefining its actions before resuming it."
        )
    content = {
        "Question": question,
        "Options": "- Decide the action required to unblock the work item.",
        "Principles applied": (
            "- Fail Fast - stop work that cannot safely advance.\n"
            "- Honesty - record the blocker instead of claiming completion."
        ),
        "Chosen direction": "Pending human decision.",
        "Reason": question,
        "Follow-up": follow_up,
    }
    for heading in SECTION_HEADINGS:
        rendered = replace_section(rendered, heading, content[heading])
    return rendered.rstrip() + "\n"


def update_active_index(
    text: str,
    item_id: str,
    fields: dict[str, Any],
    active_relative: str,
    current_root: str,
    record_relative: str = "",
) -> str:
    lines = text.splitlines()
    found = False
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) >= 9 and cells[1].strip() == item_id:
            cells[5] = " blocked "
            lines[index] = "|".join(cells)
            found = True
    if not found:
        title = str(fields.get("title") or item_id).strip()[:60]
        kind = str(fields.get("kind") or "").strip()
        venue = str(fields.get("venue") or "").strip()
        item_link = relative_record_link(
            active_relative,
            record_relative or record_path(Path(current_root), item_id).as_posix(),
        )
        lines.append(
            f"| {item_id} | {kind} | {venue} | {title} | blocked | {venue} | "
            f"[{item_link}]({item_link}) |"
        )
    return "\n".join(lines) + "\n"


def drop_index_row(text: str, item_id: str) -> str:
    def is_item_row(line: str) -> bool:
        cells = line.split("|")
        return line.lstrip().startswith("|") and len(cells) > 1 and cells[1].strip() == item_id

    lines = [line for line in text.splitlines() if not is_item_row(line)]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    args = parse_args()
    reason = args.reason.strip()
    if not reason:
        print("--reason must be non-empty", file=sys.stderr)
        return 2

    project_root = Path(args.project_root).expanduser().resolve()
    stage_root = project_root / ".stage"
    schema_blocker = schema_migration_banner(stage_root)
    if schema_blocker:
        print(schema_blocker, file=sys.stderr)
        return 2
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        print("escalate_work requires a schema-v4 Stage project", file=sys.stderr)
        return 2

    paths = v4_lifecycle_paths()
    item_path = record_path(stage_root / paths.current_cards, args.item)
    if not item_path.is_file():
        print(f"{args.item}: no current work item at {item_path}", file=sys.stderr)
        return 2

    item_text = item_path.read_text(encoding="utf-8")
    fields = parse_frontmatter(item_path)
    status = str(fields.get("status") or "").strip().lower()
    if status not in ESCALATABLE_STATUSES:
        print(
            f"{args.item}: status `{status or 'missing'}` is not active/review; "
            "refusing to escalate",
            file=sys.stderr,
        )
        return 1

    current_items_root = stage_root / paths.current_cards
    target_path = item_path
    target_id = args.item
    target_fields = fields
    try:
        scale = work_record_scale(current_items_root, item_path)
    except ValueError as exc:
        print(f"{args.item}: {exc}; run stage-migrate", file=sys.stderr)
        return 1
    if scale == "action":
        parent_path = hierarchy_parent_record_path(current_items_root, item_path)
        if parent_path is None or not parent_path.is_file():
            print(
                f"{args.item}: action has no story location; refusing to escalate",
                file=sys.stderr,
            )
            return 1
        target_path = parent_path
        target_fields = parse_frontmatter(target_path)
        target_id = str(target_fields.get("id") or "").strip()
        if not target_id:
            print(
                f"{args.item}: story record has no id; refusing to escalate",
                file=sys.stderr,
            )
            return 1

    template_path = stage_root / "decisions/pending/_template.md"
    decision_index_path = stage_root / refresh_decision_index.INDEX_RELATIVE
    active_path = stage_root / paths.active_index
    review_path = stage_root / paths.review_index
    required = (template_path, decision_index_path, active_path)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print(f"Stage escalation prerequisite missing: {', '.join(missing)}", file=sys.stderr)
        return 2

    decision_id = next_decision_id(stage_root)
    decision_path = stage_root / "decisions/pending" / f"{decision_id}.md"
    try:
        decision_text = render_decision(
            template_path.read_text(encoding="utf-8"),
            decision_id,
            target_id,
            reason,
            failed_action=args.item if scale == "action" else "",
        )
        refresh_decision_index.render_index(
            stage_root, decision_index_path.read_text(encoding="utf-8")
        )
        records = [(item_path, fields)]
        if target_path != item_path:
            records.append((target_path, target_fields))
        updated_records: list[tuple[Path, str]] = []
        updated_active = active_path.read_text(encoding="utf-8")
        for record, record_fields in records:
            record_id = str(record_fields.get("id") or "").strip()
            updated_record = set_field(
                record.read_text(encoding="utf-8"), "status", "blocked"
            )
            if record == target_path:
                refs = list(
                    split_scope(str(record_fields.get("decision_refs") or ""))
                )
                if decision_id not in refs:
                    refs.append(decision_id)
                updated_record = set_or_insert_field(
                    updated_record,
                    "decision_refs",
                    ", ".join(refs),
                    after="promotes",
                )
            updated_records.append((record, updated_record))
            updated_active = update_active_index(
                updated_active,
                record_id,
                record_fields,
                paths.active_index,
                paths.current_cards,
                record.relative_to(stage_root).as_posix(),
            )
    except (OSError, ValueError) as exc:
        print(f"{args.item}: cannot prepare escalation: {exc}", file=sys.stderr)
        return 2

    decision_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with decision_path.open("x", encoding="utf-8") as handle:
            handle.write(decision_text)
        for record, updated_record in updated_records:
            record.write_text(updated_record, encoding="utf-8")
        active_path.write_text(updated_active, encoding="utf-8")
        if review_path.exists():
            review_text = review_path.read_text(encoding="utf-8")
            for record, _updated_record in updated_records:
                record_id = str(parse_frontmatter(record).get("id") or "").strip()
                review_text = drop_index_row(review_text, record_id)
            review_path.write_text(review_text, encoding="utf-8")
        refresh_decision_index.refresh_index(project_root)
    except (OSError, refresh_decision_index.IndexFormatError) as exc:
        print(f"{args.item}: escalation write failed: {exc}", file=sys.stderr)
        return 2

    detail = (
        f"; story {target_id} blocked for re-decomposition"
        if scale == "action"
        else ""
    )
    print(f"{args.item}: blocked{detail}; pending decision {decision_id} created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
