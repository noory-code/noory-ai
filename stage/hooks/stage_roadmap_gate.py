"""Schema-v4 closure promotion and milestone re-attribution write gates."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from stage_paths import (
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    entry_relative_to_workspace,
    stage_relative_forms,
)
import stage_roadmap
import stage_roadmap_closure
from stage_runtime import closure_promotion_revalidation_blocker
import stage_topology
from stage_work import (
    DECISION_FINAL_STATUSES,
    frontmatter_field_from_text,
    projected_file_text,
    projected_patch_text,
    read_existing_text,
    split_scope,
    work_item_relative,
)


SHELL_TOOLS = {"Bash", "run_in_terminal"}
PATCH_FILE_RE = re.compile(
    r"^\*{3} (?:Add|Update|Delete) File: (?P<path>.+)$|"
    r"^\*{3} Move to: (?P<move>.+)$",
    re.MULTILINE,
)


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input") or payload.get("toolInput") or {}
    return value if isinstance(value, dict) else {}


def _iter_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(_iter_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(_iter_strings(item))
    return strings


def _projected_work_targets(
    workspace_root: Path, payload: dict[str, Any], name: str
) -> list[tuple[str, str]]:
    data = _tool_input(payload)
    if name == "apply_patch":
        targets: list[tuple[str, str]] = []
        for patch_text in _iter_strings(data):
            for match in PATCH_FILE_RE.finditer(patch_text):
                raw = match.group("path") or match.group("move") or ""
                relative = work_item_relative(raw, workspace_root)
                if relative:
                    targets.append(
                        (
                            relative,
                            projected_patch_text(patch_text, relative, workspace_root),
                        )
                    )
        return targets

    target = next(
        (
            value
            for key in ("file_path", "path", "filePath")
            if isinstance((value := data.get(key)), str) and value
        ),
        "",
    )
    if not target:
        return []
    relative = work_item_relative(target, workspace_root)
    if not relative:
        return []
    existing = read_existing_text(workspace_root, relative)
    return [(relative, projected_file_text(existing, name, data))]


def _projected_paths_with_prefix(
    workspace_root: Path,
    payload: dict[str, Any],
    name: str,
    prefixes: tuple[str, ...],
) -> list[tuple[str, str]]:
    data = _tool_input(payload)
    if name == "apply_patch":
        targets: list[tuple[str, str]] = []
        for patch_text in _iter_strings(data):
            for match in PATCH_FILE_RE.finditer(patch_text):
                raw = match.group("path") or match.group("move") or ""
                relative = next(
                    (
                        form
                        for form in stage_relative_forms(raw, workspace_root)
                        if any(form.startswith(prefix) for prefix in prefixes)
                    ),
                    "",
                )
                if relative:
                    targets.append(
                        (
                            relative,
                            projected_patch_text(patch_text, relative, workspace_root),
                        )
                    )
        return targets

    target = next(
        (
            value
            for key in ("file_path", "path", "filePath")
            if isinstance((value := data.get(key)), str) and value
        ),
        "",
    )
    if not target:
        return []
    relative = next(
        (
            form
            for form in stage_relative_forms(target, workspace_root)
            if any(form.startswith(prefix) for prefix in prefixes)
        ),
        "",
    )
    if not relative:
        return []
    existing = read_existing_text(workspace_root, relative)
    return [(relative, projected_file_text(existing, name, data))]


def _same_change_supersedes_closure(
    workspace_root: Path,
    payload: dict[str, Any],
    name: str,
    closure: stage_roadmap_closure.EffectiveClosure,
) -> bool:
    pending = stage_topology.get_zone("decisions", "pending").canonical_path
    official = stage_topology.get_zone("decisions", "official").canonical_path
    decisions = _projected_paths_with_prefix(
        workspace_root,
        payload,
        name,
        (f".stage/{pending}/", f".stage/{official}/"),
    )
    milestones = _projected_paths_with_prefix(
        workspace_root, payload, name, (".stage/roadmap/milestones/",)
    )
    milestone_relative = (
        f".stage/roadmap/milestones/{closure.milestone_id}.md"
    )
    projected_milestone = next(
        (
            text
            for relative, text in milestones
            if Path(relative).stem == closure.milestone_id
        ),
        read_existing_text(workspace_root, milestone_relative),
    )
    projected_refs = split_scope(
        frontmatter_field_from_text(projected_milestone, "decision_refs")
    )
    for relative, text in decisions:
        decision_id = frontmatter_field_from_text(text, "id") or Path(relative).stem
        if decision_id not in projected_refs:
            continue
        if frontmatter_field_from_text(text, "roadmap_item") != closure.milestone_id:
            continue
        if frontmatter_field_from_text(text, "supersedes") != closure.decision_id:
            continue
        status = frontmatter_field_from_text(text, "status").lower()
        transition = frontmatter_field_from_text(text, "transition").lower()
        if (
            status in DECISION_FINAL_STATUSES
            and transition in stage_roadmap.PURSUIT_TRANSITIONS
        ):
            return True
    return False


def reattribution_blocker(
    workspace_root: Path,
    payload: dict[str, Any],
    name: str,
    shell_targets: list[str],
) -> str:
    """Protect work membership frozen by an effective v4 milestone closure."""

    stage_root = workspace_root / ".stage"
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return ""
    closures = stage_roadmap_closure.effective_closures(stage_root)
    if not closures:
        return ""

    if name in SHELL_TOOLS:
        for raw in shell_targets:
            relative = work_item_relative(raw, workspace_root)
            if not relative:
                continue
            existing = read_existing_text(workspace_root, relative)
            work_item_id = (
                frontmatter_field_from_text(existing, "id") or Path(relative).stem
            )
            milestone = frontmatter_field_from_text(existing, "milestone")
            for closure in closures:
                protected_ids = {entry.work_item_id for entry in closure.entries}
                if work_item_id not in protected_ids and not (
                    closure.basis_issues and milestone == closure.milestone_id
                ):
                    continue
                return (
                    "Stage roadmap re-attribution gate violation: a shell write targets "
                    f"{work_item_id}, whose milestone is frozen by effective closure "
                    f"{closure.decision_id}. Use a projected file-write change set so Stage "
                    "can prove the milestone field is unchanged or can validate a decided "
                    "reopen decision that supersedes the closure."
                )

    for relative, projected in _projected_work_targets(
        workspace_root, payload, name
    ):
        existing = read_existing_text(workspace_root, relative)
        old_milestone = frontmatter_field_from_text(existing, "milestone")
        new_milestone = frontmatter_field_from_text(projected, "milestone")
        if old_milestone == new_milestone:
            continue
        work_item_id = (
            frontmatter_field_from_text(existing, "id")
            or frontmatter_field_from_text(projected, "id")
            or Path(relative).stem
        )
        for closure in closures:
            protected_ids = {entry.work_item_id for entry in closure.entries}
            protected = work_item_id in protected_ids
            if closure.basis_issues and old_milestone == closure.milestone_id:
                protected = True
            if not protected:
                continue
            if _same_change_supersedes_closure(
                workspace_root, payload, name, closure
            ):
                continue
            return (
                "Stage roadmap re-attribution gate violation: changing "
                f"{work_item_id} milestone from `{old_milestone or 'empty'}` to "
                f"`{new_milestone or 'empty'}` is frozen by effective closure "
                f"{closure.decision_id}. Carry a decided reopen decision that supersedes "
                "that closure and append it to the milestone decision_refs in the same "
                "change set."
            )
    return ""


def _work_projection_overlays(
    workspace_root: Path,
    payload: dict[str, Any],
    name: str,
    shell_targets: list[str],
) -> tuple[dict[str, str | None], str]:
    if name in SHELL_TOOLS:
        work_targets = [
            raw for raw in shell_targets if work_item_relative(raw, workspace_root)
        ]
        if work_targets:
            return {}, (
                "the promotion change set also writes W cards through a shell command, "
                "so their projected terminal state cannot be proven"
            )
        return {}, ""
    if name != "apply_patch":
        return (
            {
                relative.removeprefix(".stage/"): projected
                for relative, projected in _projected_work_targets(
                    workspace_root, payload, name
                )
            },
            "",
        )

    overlays: dict[str, str | None] = {}
    header_re = re.compile(
        r"^\*{3} (?P<action>Add|Update|Delete) File: (?P<path>.+)$",
        re.MULTILINE,
    )
    for patch_text in _iter_strings(_tool_input(payload)):
        current_source = ""
        for line in patch_text.splitlines():
            file_match = re.match(
                r"^\*{3} (?:Add|Update|Delete) File: (.+)$", line
            )
            if file_match:
                current_source = file_match.group(1)
                continue
            move_match = re.match(r"^\*{3} Move to: (.+)$", line)
            if move_match and (
                work_item_relative(current_source, workspace_root)
                or work_item_relative(move_match.group(1), workspace_root)
            ):
                return {}, "a W-card move in the promotion change set is not projectable"
        for match in header_re.finditer(patch_text):
            raw = match.group("path")
            relative = work_item_relative(raw, workspace_root)
            if not relative:
                continue
            key = relative.removeprefix(".stage/")
            overlays[key] = (
                None
                if match.group("action") == "Delete"
                else projected_patch_text(patch_text, relative, workspace_root)
            )
    return overlays, ""


def projected_closure_promotion_blocker(
    workspace_root: Path,
    payload: dict[str, Any],
    name: str,
    write_targets: list[str],
    shell_targets: list[str],
) -> str:
    """Revalidate the post-call projection, not only the on-disk pre-state."""

    stage_root = workspace_root / ".stage"
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return ""
    official_root = stage_topology.get_zone("decisions", "official").canonical_path
    pending_root = stage_topology.get_zone("decisions", "pending").canonical_path
    closure_sources: dict[str, Path] = {}
    for raw in write_targets:
        relative = entry_relative_to_workspace(raw, workspace_root)
        prefix = f".stage/{official_root}/"
        if not relative.startswith(prefix) or not relative.endswith(".md"):
            continue
        decision_id = Path(relative).stem
        pending = stage_root / pending_root / f"{decision_id}.md"
        official = stage_root / official_root / f"{decision_id}.md"
        source = pending if pending.is_file() else official
        fields = {
            field: frontmatter_field_from_text(
                read_existing_text(
                    workspace_root,
                    str(source.relative_to(workspace_root)),
                ),
                field,
            )
            for field in ("transition",)
        }
        if fields["transition"].lower() in stage_roadmap.CLOSURE_TRANSITIONS:
            closure_sources[decision_id] = source
    if not closure_sources:
        return ""

    overlays, projection_error = _work_projection_overlays(
        workspace_root, payload, name, shell_targets
    )
    if projection_error:
        return (
            "Stage closure promotion revalidation denied: "
            f"{projection_error}. Promote the closure in an isolated projected write."
        )
    blocker = closure_promotion_revalidation_blocker(
        stage_root, workspace_root, write_targets, overlays
    )
    if blocker:
        return blocker

    decisions = _projected_paths_with_prefix(
        workspace_root,
        payload,
        name,
        (f".stage/{pending_root}/", f".stage/{official_root}/"),
    )
    for decision_id, source in closure_sources.items():
        projected = next(
            (text for relative, text in decisions if Path(relative).stem == decision_id),
            "",
        )
        if not projected:
            continue
        source_text = read_existing_text(
            workspace_root, str(source.relative_to(workspace_root))
        )
        immutable_fields = (
            "id",
            "roadmap_item",
            "transition",
            "predecessor",
            "supersedes",
        )
        changed_fields = [
            field
            for field in immutable_fields
            if frontmatter_field_from_text(source_text, field)
            != frontmatter_field_from_text(projected, field)
        ]
        if changed_fields:
            return (
                "Stage closure promotion revalidation denied for "
                f"{decision_id}: immutable closure field(s) changed during promotion: "
                + ", ".join(changed_fields)
            )
        expected = stage_roadmap_closure.load_closure_basis(source)
        actual = stage_roadmap_closure.parse_closure_basis(projected)
        if expected != actual:
            return (
                "Stage closure promotion revalidation denied for "
                f"{decision_id}: the frozen basis or completion-criteria attestation "
                "changed during promotion; both are immutable."
            )
    return ""
