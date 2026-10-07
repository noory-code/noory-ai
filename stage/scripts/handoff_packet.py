#!/usr/bin/env python3
"""Build an explicit handoff from live criteria and recorded Stage evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE / "hooks"))
from stage_work import load_items_from

from driver_subtree import ancestor_chain
from handoff_conditions import classify
from handoff_producers import check_refs, command, snapshot, validate_config
from handoff_sources import PacketError, evidence, record_lines, relative_path, section, source_status

DECISION_ORDER = """Follow the user's current explicit instruction. Start with the purpose chain.
When purpose answers the question, proceed. Otherwise use criteria classified as applies.
For partial criteria, classify the actual file again and record
`Condition judgment: <ref> path=<file> -> applies` before applying it to that file.
If that file still needs note judgments, record its narrowed path as needs_judgment and satisfy
every note before applying it. A partial scope never removes the note requirements.
For needs_judgment, first satisfy all code-checkable conditions, then record each note as
`Condition judgment: <ref> note="<original note>" -> met|not_met because <reason>`.
Every note must be met. Never apply unresolved or not_applicable criteria.
Resolve conflicting criteria through the current user instruction, then project purpose,
then explicit overrides supported by a user quote. If none resolves the conflict, defer that
choice. Ask the user only when missing information prevents progress, and state what is missing.
Immediately before each choice that depends on a criterion, run its check command below.
Record `Applied criteria: <ref>, <ref>` in the card's Progress, or `Applied criteria: none`.
Prior evidence does not replace acceptance checks or independent review."""


def build_packet(root: Path, item_id: str, project_key: str, config: dict) -> str:
    root = root.resolve()
    validate_config(config)
    if not project_key.strip():
        raise PacketError("E_SCOPE_REQUIRED: project key must not be empty")
    items = load_items_from(root / ".stage/work/current")
    matches = [item for item in items if item.item_id == item_id]
    if len(matches) != 1:
        raise PacketError("E_WORK_INVALID: expected exactly one current work card")
    item = matches[0]
    chain = ancestor_chain(item, items) + [item]
    bodies = {}
    for card in chain:
        relative_path(root, card.path.relative_to(root).as_posix())
        bodies[card.item_id] = card.path.read_text(encoding="utf-8")
    body = bodies[item.item_id]
    progress = section(body, "Progress") or ""
    lines = [f"# Handoff: {item.item_id}", "", "## Purpose chain", ""]
    for card in chain:
        lines += [f"### {card.item_id}", "", section(bodies[card.item_id], "Purpose") or "Purpose missing; do not invent one.", ""]
    lines += ["## Criteria as of check", "", "These criteria were current at the reported check. Recheck before using them.", ""]
    commands = []
    for name in ("distill", "avatar"):
        if name not in config:
            lines += [f"{name}: Criteria were not queried; absence is not established.", ""]
            continue
        data = snapshot(name, config[name], project_key, root)
        if "error" in data:
            lines += [f"Could not check {name} criteria: {data['error']}. Do not use any earlier criteria as current.", ""]
            continue
        lines += [f"{name} — generation: {data['generation']}; checked_at: {data['checked_at']}", ""]
        if data.get("store") == "absent":
            lines += ["store: absent", ""]
        eligible = []
        if not data["criteria"]:
            lines += ["No current criteria.", ""]
        for criterion in data["criteria"]:
            classification = classify(criterion, list(item.scope), item.kind, root)
            source = source_status(criterion["origin"], root, project_key)
            if source in {"changed", "missing", "rejected_ref"}:
                classification["status"] = "unresolved"
            status = classification["status"]
            lines += [f"### {status}", "", f"- {criterion['ref']}: {criterion['statement']}",
                      f"- targets: {json.dumps(classification['targets'], ensure_ascii=False)}",
                      f"- excluded: {json.dumps(classification['excluded'], ensure_ascii=False)}",
                      f"- source_status: {source}"]
            for field in ("applies_when", "exceptions", "notes", "overrides", "confirmation", "ai_confidence", "origin"):
                lines.append(f"- {field}: {json.dumps(criterion.get(field), ensure_ascii=False)}")
            lines.append("")
            if status in {"applies", "partial", "needs_judgment"}:
                eligible.append(criterion["ref"])
        if eligible:
            commands.append((name, command(name, config[name], project_key, eligible)))
    lines += ["## Prior result evidence", "", *evidence(progress, root), "", "## Stale judgments", ""]
    applied_lines = record_lines(progress, "Applied criteria")
    applied = set()
    unparsed = []
    explicitly_none = False
    for line in applied_lines:
        if line.startswith("Unparsed record:"):
            unparsed.append(line)
            continue
        value = line.split(":", 1)[1].strip()
        if value == "none":
            explicitly_none = True
            continue
        for ref in value.split(","):
            if re.fullmatch(r"(?:distill:CR|avatar:PC)-[0-9a-f]{12}@[1-9][0-9]*", ref.strip()):
                applied.add(ref.strip())
            elif f"Unparsed record: {line}" not in unparsed:
                unparsed.append(f"Unparsed record: {line}")
    for name in ("distill", "avatar"):
        refs = sorted(ref for ref in applied if ref.startswith(name + ":"))
        if not refs:
            continue
        states = check_refs(name, config[name], project_key, root, refs) if name in config else {ref: "unknown (not queried)" for ref in refs}
        for ref in refs:
            lines.append(f"- {ref}: {states[ref]}. Revisit non-current judgments; do not automatically undo work.")
    if explicitly_none:
        lines.append("Explicitly applied no criteria.")
    elif not applied_lines:
        lines.append("No applied-criteria record.")
    lines += unparsed
    lines += record_lines(progress, "Condition judgment")
    lines += ["", "## Decision order", "", DECISION_ORDER, "", "## Check before each criterion-dependent choice", "",
              "Run each JSON argv array without a shell. Apply a criterion only when its status is eligible_current.",
              "Any other status, non-zero exit, or timeout: do not apply it. Refresh the packet or defer that choice.", ""]
    for name, argv in commands:
        lines.append(f"{name}: {json.dumps(argv, ensure_ascii=False)}")
    if not commands:
        lines.append("No applicable criteria have a check command in this packet.")
    lines += ["", "## Remaining work", "", "### Success criteria", "", section(body, "Success criteria") or "Not recorded.",
              "", "### Next action", "", section(body, "Next action") or "Not recorded.", ""]
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("item_id")
    parser.add_argument("--project-key", required=True)
    parser.add_argument("--producers", type=Path)
    args = parser.parse_args()
    try:
        config = {}
        if args.producers:
            try:
                config = json.loads(args.producers.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                raise PacketError(f"E_PRODUCERS_INVALID: {error}") from error
        print(build_packet(args.project_root, args.item_id, args.project_key, config), end="")
    except (PacketError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
