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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
from lifecycle_paths import relative_record_link, v4_lifecycle_paths  # noqa: E402
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    load_venue_routing,
    schema_migration_banner,
)
from stage_work import (  # noqa: E402
    VENUE_SPLIT_TOKEN,
    WORK_PLANNED_STATUSES,
    parse_frontmatter,
    venue_exception_error,
)

# Work fields a present card must carry, in template order, with start values.
WORK_FIELD_DEFAULTS = (
    ("status", "active"),
    ("verification", "pending"),
    ("retrospective", "pending"),
    ("retrospective_ref", ""),
    ("promotion", "pending"),
    ("scope", ""),
    ("promotes", ""),
    ("decision_refs", ""),
)
FRONTMATTER_ORDER = (
    "id",
    "title",
    "kind",
    "venue",
    "parent",
    "priority",
    "status",
    "verification",
    "retrospective",
    "retrospective_ref",
    "promotion",
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
    return parser.parse_args()


def body_after_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


def build_frontmatter(fields: dict[str, str]) -> str:
    lines = ["---"]
    order = list(FRONTMATTER_ORDER)
    if "milestone" in fields:
        order.insert(order.index("parent") + 1, "milestone")
    for key in order:
        lines.append(f"{key}: {fields.get(key, '')}".rstrip())
    lines.append("---")
    return "\n".join(lines) + "\n"


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
    else:
        planned_root = Path("future", "backlog", "items").as_posix()
        current_root = Path("present", "work", "items").as_posix()
        index_relative = Path("future", "backlog", "index.md").as_posix()
        active_relative = Path("present", "work", "active.md").as_posix()

    source_path = stage_root / planned_root / f"{args.item}.md"
    if not source_path.is_file():
        candidates = sorted((stage_root / planned_root).glob(f"{args.item}-*.md"))
        if len(candidates) == 1:
            source_path = candidates[0]
        else:
            print(f"{args.item}: no planned card in {planned_root}", file=sys.stderr)
            return 1
    target_path = stage_root / current_root / f"{args.item}.md"
    if target_path.exists():
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

    kind = (fields.get("kind") or "").strip().lower()
    venue = args.venue or (fields.get("venue") or "").strip()
    routing = load_venue_routing(stage_root)
    routed = routing.get(kind, "")
    exception_reason = ""
    if routed == VENUE_SPLIT_TOKEN:
        exception_reason = (
            f"kind `{kind}` is declared mixed (`{VENUE_SPLIT_TOKEN}`): split this card into "
            "design and implementation cards with `parent` lineage, or pass --decision <DE-id> "
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
    for key, default in WORK_FIELD_DEFAULTS:
        if key == "scope":
            fields[key] = args.scope
        elif key == "decision_refs":
            existing = (fields.get(key) or "").strip()
            if args.decision and args.decision not in existing:
                fields[key] = f"{existing}, {args.decision}".strip(", ")
            else:
                fields[key] = existing
        elif key == "status":
            fields[key] = "active"
        else:
            fields.setdefault(key, default)
            if not fields[key]:
                fields[key] = default

    body = body_after_frontmatter(text)
    for section in RECORD_SECTIONS:
        if section + "\n" not in body and not body.rstrip().endswith(section):
            body = body.rstrip() + f"\n\n{section}\n"
    body = body.rstrip() + "\n"

    target_path.write_text(build_frontmatter(fields) + "\n" + body, encoding="utf-8")
    source_path.unlink()

    active_path = stage_root / active_relative
    active_link = relative_record_link(
        active_relative, f"{current_root}/{args.item}.md"
    )
    title = (fields.get("title") or "").strip()[:60]
    row = (
        f"| {args.item} | {kind} | {venue} | {title} | active | {args.owner or venue} | "
        f"[{active_link}]({active_link}) |"
    )
    active_text = active_path.read_text(encoding="utf-8") if active_path.exists() else ""
    if not re.search(rf"\({re.escape(active_link)}\)", active_text):
        active_path.write_text(active_text.rstrip("\n") + "\n" + row + "\n", encoding="utf-8")

    index_path = stage_root / index_relative
    if index_path.exists():
        planned_link = relative_record_link(
            index_relative, f"{planned_root}/{source_path.name}"
        )
        lines = index_path.read_text(encoding="utf-8").splitlines()
        kept = [
            line
            for line in lines
            if not (line.lstrip().startswith("|") and f"({planned_link})" in line)
        ]
        if len(kept) != len(lines):
            index_path.write_text("\n".join(kept) + "\n", encoding="utf-8")

    print(f"{args.item}: started (moved to {current_root}, status active)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
