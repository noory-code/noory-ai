"""Schema-v4 milestone closure snapshots and live-basis comparison."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import stage_roadmap
import stage_topology
from stage_record_paths import record_paths
from stage_work import parse_frontmatter, resolve_decision_record


TERMINAL_DISPOSITIONS = {"accepted", "rejected"}
FROZEN_BASIS_HEADING = "Frozen basis"
ATTESTATION_HEADING = "Completion-criteria attestation"


@dataclass(frozen=True)
class ClosureBasisEntry:
    """One immutable work-card outcome recorded by a closure decision."""

    work_item_id: str
    terminal_disposition: str


@dataclass(frozen=True)
class WorkSnapshot:
    """Live registry projection used for closure capture and revalidation."""

    work_item_id: str
    path: Path
    milestone: str
    status: str
    terminal_disposition: str
    archived: bool


@dataclass(frozen=True)
class EffectiveClosure:
    """An effective milestone closure and the frozen work ids it protects."""

    milestone_id: str
    decision_id: str
    decision_path: Path
    entries: tuple[ClosureBasisEntry, ...]
    basis_issues: tuple[str, ...]


def _section_text(text: str, heading: str) -> str | None:
    match = re.search(
        rf"^##[ \t]+{re.escape(heading)}[ \t]*$(.*?)(?=^##[ \t]+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match is not None else None


def parse_closure_basis(
    text: str,
) -> tuple[tuple[ClosureBasisEntry, ...], str, tuple[str, ...]]:
    """Parse the one canonical closure table and attestation sections."""

    issues: list[str] = []
    basis_text = _section_text(text, FROZEN_BASIS_HEADING)
    attestation_text = _section_text(text, ATTESTATION_HEADING)
    entries: list[ClosureBasisEntry] = []
    if basis_text is None:
        issues.append(f"missing `## {FROZEN_BASIS_HEADING}` section")
    else:
        table_lines = [
            line.strip() for line in basis_text.splitlines() if line.strip().startswith("|")
        ]
        expected_header = ("work item", "terminal_disposition")
        if not table_lines:
            issues.append("frozen basis has no table")
        else:
            header = tuple(
                cell.strip().lower() for cell in table_lines[0].strip("|").split("|")
            )
            if header != expected_header:
                issues.append(
                    "frozen basis header must be `Work item | terminal_disposition`"
                )
            seen: set[str] = set()
            for line in table_lines[1:]:
                cells = tuple(cell.strip() for cell in line.strip("|").split("|"))
                if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    continue
                if len(cells) != 2:
                    issues.append(f"malformed frozen basis row: {line}")
                    continue
                work_item_id, disposition = cells[0], cells[1].lower()
                if re.fullmatch(r"W-\d{3,}", work_item_id) is None:
                    issues.append(f"invalid frozen basis work id: {work_item_id or 'empty'}")
                    continue
                if disposition not in TERMINAL_DISPOSITIONS:
                    issues.append(
                        f"{work_item_id} has invalid frozen terminal_disposition "
                        f"`{disposition or 'missing'}`"
                    )
                    continue
                if work_item_id in seen:
                    issues.append(f"duplicate frozen basis work id: {work_item_id}")
                    continue
                seen.add(work_item_id)
                entries.append(ClosureBasisEntry(work_item_id, disposition))
    attestation = attestation_text or ""
    if not attestation:
        issues.append(f"missing `## {ATTESTATION_HEADING}` text")
    return tuple(entries), attestation, tuple(issues)


def load_closure_basis(
    decision_path: Path,
) -> tuple[tuple[ClosureBasisEntry, ...], str, tuple[str, ...]]:
    try:
        text = decision_path.read_text(encoding="utf-8")
    except OSError:
        return (), "", ("closure decision is unreadable",)
    return parse_closure_basis(text)


def _field_from_text(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def _snapshot(path: Path, relative: Path, text: str, archive_root: Path) -> WorkSnapshot:
    return WorkSnapshot(
        work_item_id=_field_from_text(text, "id") or path.stem,
        path=path,
        milestone=_field_from_text(text, "milestone"),
        status=_field_from_text(text, "status").lower(),
        terminal_disposition=_field_from_text(
            text, "terminal_disposition"
        ).lower(),
        archived=relative.is_relative_to(archive_root),
    )


def work_snapshots(
    stage_root: Path, overlays: dict[str, str | None] | None = None
) -> tuple[WorkSnapshot, ...]:
    """Read every v4 W location through the registry's reference policy."""

    roots = {
        Path(relative).parent
        for relative in stage_topology.resolve_artifact_reference(
            "W-00000000"
        ).candidate_paths
    }
    archive_root = Path(stage_topology.card_location_for_status("archived"))
    projected = overlays or {}
    seen: set[str] = set()
    snapshots: list[WorkSnapshot] = []
    for root in sorted(roots):
        for path in record_paths(stage_root / root, pattern="W-*.md"):
            relative = path.relative_to(stage_root)
            key = relative.as_posix()
            seen.add(key)
            text = projected.get(key)
            if key in projected and text is None:
                continue
            if text is None:
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    text = ""
            snapshots.append(_snapshot(path, relative, text, archive_root))
    for key, text in sorted(projected.items()):
        if key in seen or text is None:
            continue
        relative = Path(key)
        if relative.parent not in roots or not relative.name.startswith("W-"):
            continue
        snapshots.append(_snapshot(stage_root / relative, relative, text, archive_root))
    return tuple(snapshots)


def _terminal_blocker(snapshot: WorkSnapshot) -> str:
    if snapshot.archived:
        if snapshot.status != "archived":
            return f"archive card has status {snapshot.status or 'missing'}, not archived"
    elif snapshot.status != "rejected":
        return f"status {snapshot.status or 'missing'} is non-terminal"
    if snapshot.terminal_disposition not in TERMINAL_DISPOSITIONS:
        return f"terminal_disposition is {snapshot.terminal_disposition or 'missing'}"
    if not snapshot.archived and snapshot.terminal_disposition != "rejected":
        return "an unarchived terminal card must be explicitly rejected"
    return ""


def closure_capture(
    stage_root: Path, milestone_id: str
) -> tuple[tuple[ClosureBasisEntry, ...], tuple[str, ...]]:
    """Return an exact terminal basis, or deterministic close-time blockers."""

    linked = [item for item in work_snapshots(stage_root) if item.milestone == milestone_id]
    by_id: dict[str, list[WorkSnapshot]] = {}
    for snapshot in linked:
        by_id.setdefault(snapshot.work_item_id, []).append(snapshot)
    blockers: list[str] = []
    entries: list[ClosureBasisEntry] = []
    for work_item_id in sorted(by_id):
        matches = by_id[work_item_id]
        if len(matches) != 1:
            locations = ", ".join(str(item.path.relative_to(stage_root)) for item in matches)
            blockers.append(f"{work_item_id}: appears in multiple registry locations ({locations})")
            continue
        snapshot = matches[0]
        blocker = _terminal_blocker(snapshot)
        if blocker:
            blockers.append(f"{work_item_id}: {blocker}")
            continue
        entries.append(ClosureBasisEntry(work_item_id, snapshot.terminal_disposition))
    return tuple(entries), tuple(blockers)


def closure_basis_diff(
    stage_root: Path,
    decision_path: Path,
    overlays: dict[str, str | None] | None = None,
) -> tuple[str, ...]:
    """Compare one frozen closure basis with the exact live milestone membership."""

    fields = parse_frontmatter(decision_path)
    milestone_id = (fields.get("roadmap_item") or "").strip()
    entries, _attestation, basis_issues = load_closure_basis(decision_path)
    diffs = [f"closure basis invalid: {issue}" for issue in basis_issues]
    if re.fullmatch(r"M-\d{3,}", milestone_id) is None:
        diffs.append(f"closure roadmap_item is invalid: {milestone_id or 'missing'}")
        return tuple(diffs)

    snapshots = work_snapshots(stage_root, overlays)
    by_id: dict[str, list[WorkSnapshot]] = {}
    for snapshot in snapshots:
        by_id.setdefault(snapshot.work_item_id, []).append(snapshot)
    expected = {entry.work_item_id: entry for entry in entries}
    for work_item_id in sorted(expected):
        entry = expected[work_item_id]
        matches = by_id.get(work_item_id, [])
        if not matches:
            diffs.append(
                f"{work_item_id}: expected terminal_disposition "
                f"`{entry.terminal_disposition}`, actual `missing`"
            )
            continue
        if len(matches) != 1:
            locations = ", ".join(str(item.path.relative_to(stage_root)) for item in matches)
            diffs.append(
                f"{work_item_id}: expected one registry card, actual duplicates ({locations})"
            )
            continue
        actual = matches[0]
        if actual.milestone != milestone_id:
            diffs.append(
                f"{work_item_id}: expected milestone `{milestone_id}`, actual "
                f"`{actual.milestone or 'missing'}`"
            )
        blocker = _terminal_blocker(actual)
        if blocker:
            diffs.append(
                f"{work_item_id}: expected terminal_disposition "
                f"`{entry.terminal_disposition}`, actual `{blocker}`"
            )
        elif actual.terminal_disposition != entry.terminal_disposition:
            diffs.append(
                f"{work_item_id}: expected terminal_disposition "
                f"`{entry.terminal_disposition}`, actual "
                f"`{actual.terminal_disposition}`"
            )

    for snapshot in sorted(snapshots, key=lambda item: (item.work_item_id, str(item.path))):
        if snapshot.milestone != milestone_id or snapshot.work_item_id in expected:
            continue
        actual = snapshot.terminal_disposition or _terminal_blocker(snapshot)
        diffs.append(
            f"{snapshot.work_item_id}: expected `absent`, actual "
            f"terminal_disposition `{actual or 'missing'}`"
        )
    return tuple(diffs)


def effective_closures(stage_root: Path) -> tuple[EffectiveClosure, ...]:
    """Return structurally effective milestone closures and their frozen bases."""

    closures: list[EffectiveClosure] = []
    for record in stage_roadmap.roadmap_records(stage_root, "milestones"):
        state = stage_roadmap.roadmap_record_state(stage_root, record.path)
        if state.status != stage_roadmap.ROADMAP_CLOSED or state.effective_head is None:
            continue
        decision_path = resolve_decision_record(stage_root, state.effective_head)
        entries, _attestation, basis_issues = load_closure_basis(decision_path)
        closures.append(
            EffectiveClosure(
                milestone_id=record.record_id,
                decision_id=state.effective_head,
                decision_path=decision_path,
                entries=entries,
                basis_issues=basis_issues,
            )
        )
    return tuple(closures)
