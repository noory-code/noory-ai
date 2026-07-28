"""Schema-v4 roadmap records and decision-chain evaluation.

Roadmap records never author lifecycle status.  Their ``decision_refs`` field
owns chain membership, and transition decisions own the state changes.  This
module is read-only so the audit, session context, and lifecycle CLIs can share
one structural interpretation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import stage_topology
from stage_record_paths import record_paths
from stage_work import DECISION_FINAL_STATUSES, parse_frontmatter, split_scope


ROADMAP_PLANNED = "planned"
ROADMAP_ACTIVE = "active"
ROADMAP_CLOSED = "closed"
ROADMAP_INVALID = "invalid"

PURSUIT_TRANSITIONS = {"pursuit", "pursuit_open", "reopen"}
CLOSURE_TRANSITIONS = {"closure", "close"}


@dataclass(frozen=True)
class ChainIssue:
    """One deterministic decision-chain integrity failure."""

    code: str
    message: str
    path: Path


@dataclass(frozen=True)
class TransitionDecision:
    """The chain-relevant fields of one decision record."""

    decision_id: str
    path: Path
    status: str
    transition: str
    roadmap_item: str
    predecessor: str
    supersedes: str


@dataclass(frozen=True)
class RoadmapState:
    """Computed state and evidence for one theme or milestone."""

    record_id: str
    status: str
    effective_head: str | None
    issues: tuple[ChainIssue, ...]


@dataclass(frozen=True)
class RoadmapRecord:
    """Display and relationship fields read from one roadmap record."""

    record_id: str
    path: Path
    title: str
    theme: str
    period: str
    decision_refs: tuple[str, ...]


def _decision_id(ref: str) -> str:
    value = ref.strip().replace("\\", "/").rstrip("/")
    return Path(value).stem


def _decision_path(stage_root: Path, ref: str) -> Path:
    value = ref.strip().replace("\\", "/")
    if value.startswith(".stage/"):
        value = value[len(".stage/") :]
    if "/" in value:
        return stage_root / value
    artifact_id = _decision_id(value)
    try:
        candidates = stage_topology.resolve_artifact_reference(
            artifact_id
        ).candidate_paths
    except ValueError:
        return stage_root / "decisions" / "pending" / f"{artifact_id}.md"
    paths = tuple(stage_root / candidate for candidate in candidates)
    return next((path for path in paths if path.exists()), paths[0])


def _heading_title(path: Path, record_id: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(
        rf"^#\s+{re.escape(record_id)}(?:\s+(.*?))?\s*$", text, re.MULTILINE
    )
    return (match.group(1) or "").strip() if match else ""


def _section(path: Path, heading: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(
        rf"^##[ \t]+{re.escape(heading)}[ \t]*$(.*?)(?=^##[ \t]+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return ""
    return " ".join(line.strip() for line in match.group(1).splitlines() if line.strip())


def load_roadmap_record(path: Path) -> RoadmapRecord:
    """Read one status-free theme or milestone record."""

    fields = parse_frontmatter(path)
    record_id = (fields.get("id") or path.stem).strip()
    return RoadmapRecord(
        record_id=record_id,
        path=path,
        title=_heading_title(path, record_id),
        theme=(fields.get("theme") or "").strip(),
        period=_section(path, "Period"),
        decision_refs=split_scope(fields.get("decision_refs", "")),
    )


def roadmap_record_paths(stage_root: Path, zone_name: str) -> tuple[Path, ...]:
    """Return deterministic record paths for one roadmap zone."""

    zone = stage_topology.get_zone("roadmap", zone_name)
    prefix = "TH" if zone_name == "themes" else "M"
    return record_paths(stage_root / zone.canonical_path, pattern=f"{prefix}-*.md")


def roadmap_records(stage_root: Path, zone_name: str) -> tuple[RoadmapRecord, ...]:
    return tuple(load_roadmap_record(path) for path in roadmap_record_paths(stage_root, zone_name))


def _load_decisions(
    stage_root: Path, record: RoadmapRecord
) -> tuple[dict[str, TransitionDecision], list[ChainIssue]]:
    decisions: dict[str, TransitionDecision] = {}
    issues: list[ChainIssue] = []
    for raw_ref in record.decision_refs:
        decision_id = _decision_id(raw_ref)
        path = _decision_path(stage_root, raw_ref)
        if not path.is_file():
            issues.append(
                ChainIssue(
                    "CHAIN001",
                    f"Decision-chain reference is missing: {raw_ref}",
                    record.path,
                )
            )
            continue
        fields = parse_frontmatter(path)
        actual_id = (fields.get("id") or path.stem).strip()
        if actual_id != decision_id:
            issues.append(
                ChainIssue(
                    "CHAIN001",
                    f"Decision-chain reference {raw_ref} resolves to {actual_id or 'no id'}.",
                    path,
                )
            )
            continue
        if actual_id in decisions:
            continue
        decisions[actual_id] = TransitionDecision(
            decision_id=actual_id,
            path=path,
            status=(fields.get("status") or "").strip().lower(),
            transition=(fields.get("transition") or "").strip().lower(),
            roadmap_item=(fields.get("roadmap_item") or "").strip(),
            predecessor=_decision_id(fields.get("predecessor", "")),
            supersedes=_decision_id(fields.get("supersedes", "")),
        )
    return decisions, issues


def _cycle_issue(decisions: dict[str, TransitionDecision]) -> ChainIssue | None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(decision_id: str, trail: tuple[str, ...]) -> ChainIssue | None:
        if decision_id in visiting:
            start = trail.index(decision_id)
            cycle = trail[start:] + (decision_id,)
            return ChainIssue(
                "CHAIN002",
                "Decision chain forms a cycle: " + " -> ".join(cycle),
                decisions[decision_id].path,
            )
        if decision_id in visited:
            return None
        visiting.add(decision_id)
        decision = decisions[decision_id]
        for target in (decision.predecessor, decision.supersedes):
            if target:
                issue = visit(target, trail + (decision_id,))
                if issue is not None:
                    return issue
        visiting.remove(decision_id)
        visited.add(decision_id)
        return None

    for decision_id in decisions:
        issue = visit(decision_id, ())
        if issue is not None:
            return issue
    return None


def decision_chain_issues(stage_root: Path, record_path: Path) -> tuple[ChainIssue, ...]:
    """Validate references and graph shape for one roadmap record's chain."""

    record = load_roadmap_record(record_path)
    decisions, issues = _load_decisions(stage_root, record)
    for decision in decisions.values():
        if decision.roadmap_item != record.record_id:
            issues.append(
                ChainIssue(
                    "CHAIN005",
                    f"Decision {decision.decision_id} targets roadmap item "
                    f"{decision.roadmap_item or 'empty'}, not {record.record_id}.",
                    decision.path,
                )
            )
        if decision.transition not in PURSUIT_TRANSITIONS | CLOSURE_TRANSITIONS:
            issues.append(
                ChainIssue(
                    "CHAIN006",
                    f"Decision {decision.decision_id} has unknown roadmap transition "
                    f"{decision.transition or 'empty'}.",
                    decision.path,
                )
            )
        for field, target in (
            ("predecessor", decision.predecessor),
            ("supersedes", decision.supersedes),
        ):
            if target and target not in decisions:
                issues.append(
                    ChainIssue(
                        "CHAIN001",
                        f"Decision {decision.decision_id} has dangling {field}: {target}",
                        decision.path,
                    )
                )
    if any(issue.code == "CHAIN001" for issue in issues):
        return tuple(issues)

    cycle = _cycle_issue(decisions)
    if cycle is not None:
        issues.append(cycle)
        return tuple(issues)

    superseded = {
        decision.supersedes for decision in decisions.values() if decision.supersedes
    }
    children: dict[str, list[str]] = {}
    for decision in decisions.values():
        if decision.predecessor:
            children.setdefault(decision.predecessor, []).append(decision.decision_id)
    for predecessor, successors in children.items():
        effective_successors = [item for item in successors if item not in superseded]
        if len(effective_successors) > 1:
            issues.append(
                ChainIssue(
                    "CHAIN003",
                    f"Decision chain forks at {predecessor}: "
                    + ", ".join(sorted(effective_successors)),
                    decisions[predecessor].path,
                )
            )

    predecessor_targets = {
        decision.predecessor for decision in decisions.values() if decision.predecessor
    }
    heads = set(decisions) - predecessor_targets - superseded
    if len(heads) > 1:
        issues.append(
            ChainIssue(
                "CHAIN004",
                "Decision chain has multiple effective heads: " + ", ".join(sorted(heads)),
                record.path,
            )
        )
    return tuple(issues)


def roadmap_record_state(stage_root: Path, record_path: Path) -> RoadmapState:
    """Compute planned/active/closed solely from the effective decision head."""

    record = load_roadmap_record(record_path)
    if not record.decision_refs:
        return RoadmapState(record.record_id, ROADMAP_PLANNED, None, ())
    issues = decision_chain_issues(stage_root, record_path)
    if issues:
        return RoadmapState(record.record_id, ROADMAP_INVALID, None, issues)

    decisions, _ = _load_decisions(stage_root, record)
    effective = {
        decision_id: decision
        for decision_id, decision in decisions.items()
        if decision.status in DECISION_FINAL_STATUSES
    }
    if not effective:
        return RoadmapState(record.record_id, ROADMAP_PLANNED, None, ())
    predecessor_targets = {
        decision.predecessor
        for decision in effective.values()
        if decision.predecessor in effective
    }
    superseded = {
        decision.supersedes
        for decision in effective.values()
        if decision.supersedes in effective
    }
    heads = set(effective) - predecessor_targets - superseded
    if len(heads) != 1:
        return RoadmapState(record.record_id, ROADMAP_INVALID, None, issues)
    head_id = next(iter(heads))
    transition = effective[head_id].transition
    if transition in PURSUIT_TRANSITIONS:
        status = ROADMAP_ACTIVE
    elif transition in CLOSURE_TRANSITIONS:
        status = ROADMAP_CLOSED
    else:
        status = ROADMAP_INVALID
    return RoadmapState(record.record_id, status, head_id, issues)


def active_milestones(stage_root: Path) -> tuple[RoadmapRecord, ...]:
    """Return milestones with a valid pursuit head and no effective closure."""

    return tuple(
        record
        for record in roadmap_records(stage_root, "milestones")
        if roadmap_record_state(stage_root, record.path).status == ROADMAP_ACTIVE
    )
