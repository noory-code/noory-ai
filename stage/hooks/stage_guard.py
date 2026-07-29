#!/usr/bin/env python3
"""Stage hook guard.

The hook keeps Stage rules executable without depending on host-specific shell
scripts. It accepts Claude hook JSON on stdin and writes hook JSON on stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Sibling modules load by bare name; make the hooks dir importable whether this
# file is run directly (hooks.json), imported (`import stage_guard`), or loaded
# by file path (`spec_from_file_location` in the CLI and tests).
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import (  # noqa: E402  (after sys.path bootstrap)
    ACTIVE_TOPOLOGY_V4,
    DEFAULT_EXCLUDED_PREFIXES,
    STAGE_SCHEMA_VERSION,
    active_topology,
    clean_path_text,
    configured_write_tools,
    entry_relative_to_workspace,
    governance_broken,
    is_outside_workspace,
    is_source_path,
    is_stage_internal_path,
    LANGUAGE_TAG_RE,
    load_governance,
    REVIEW_STAGES,
    REVIEW_STRENGTHS,
    load_review_config,
    normalize_path_text,
    path_has_prefix,
    path_targets_stage_archive,
    path_targets_stage_official,
    resolve_review_command,
    schema_migration_banner,
    path_targets_stage_past,
    path_targets_stage_root,
    relative_to_workspace,
    stage_real_root,
    stage_relative_forms,
)
import stage_topology  # noqa: E402
from stage_record_paths import (  # noqa: E402
    hierarchy_parent_record_path,
    work_record_scale,
)
from stage_roadmap_gate import (  # noqa: E402
    projected_closure_promotion_blocker,
    reattribution_blocker,
)
from stage_shell import (  # noqa: E402  (after sys.path bootstrap)
    _restore_sentinels,
    command_deletes_stage,
    interpreter_inline_stage_write,
    shell_delete_paths,
    shell_tokens,
    shell_write_paths,
)
from stage_git import (  # noqa: E402  (after sys.path bootstrap)
    command_has_git_commit,
    git_commit_all_requested,
    git_commit_pathspec_files,
    iter_git_commands,
)
from stage_work import (  # noqa: E402  (after sys.path bootstrap)
    AUDIT_FIELD_DEFAULTS,
    VENUE_EXCEPTION_AUTHORIZATION,
    VENUE_SPLIT_TOKEN,
    decision_status,
    venue_exception_error,
    PROMOTION_FINAL,
    PROMOTION_VALUES,
    RETROSPECTIVE_DONE,
    RETROSPECTIVE_VALUES,
    REVIEW_DONE,
    REVIEW_VALUES,
    STATUS_VALUES,
    VERIFICATION_DONE,
    VERIFICATION_VALUES,
    WORK_FINAL_STATUSES,
    WORK_OPEN_STATUSES,
    WORK_PLANNED_STATUSES,
    WorkItem,
    archive_target_item_id,
    archive_target_retro_id,
    changed_files,
    commit_blocker,
    frontmatter_field_from_text,
    git_add_paths_from_command,
    item_completion_blockers,
    item_from_fields,
    item_is_completed,
    item_is_open,
    item_promotes_path,
    load_all_work_items,
    load_work_items,
    parse_frontmatter,
    parse_index_rows,
    projected_file_text,
    projected_patch_text,
    read_existing_text,
    retrospective_ref_id,
    source_registration_blocker,
    split_scope,
    stage_completion_blockers,
    staged_files,
    work_item_enum_error,
    work_item_relative,
)
from stage_runtime import (  # noqa: E402  (after sys.path bootstrap)
    SESSION_SUMMARY_KEEP,
    consume_claims_for,
    migrate_legacy_runtime,
    pending_intent_files_for_work_item,
    promotion_blocker,
    prune_question_ack_markers,
    prune_session_summaries,
    runtime_slot_name,
    sessions_root,
    write_intent_file,
)
from stage_context import (  # noqa: E402  (after sys.path bootstrap)
    CONSUMER_CONTEXT_MAX_LINES,
    SESSION_CONTEXT_LINE_LIMIT,
    consumer_context_lines,
    open_question_lines,
    session_context,
    summarize_stage,
)


SHELL_TOOLS = {"Bash", "run_in_terminal"}
WRITE_TOOLS = {
    "Edit",
    "MultiEdit",
    "NotebookEdit",
    "Write",
    "apply_patch",
    "create_file",
    "editFiles",
    "edit_files",
    "edit_notebook_file",
    "multi_replace_string_in_file",
    "replace_string_in_file",
}

OS_SCRIPT_SUFFIXES = (".sh", ".bash", ".zsh", ".fish", ".ps1", ".cmd", ".bat")
SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".dart",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".scss",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".adoc"}
PATCH_FILE_RE = re.compile(r"^\*{3} (?:Add|Update|Delete) File: (?P<path>.+)$|^\*{3} Move to: (?P<move>.+)$", re.MULTILINE)


def configure_stdio() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_workspace_root(payload: dict[str, Any]) -> Path:
    # Claude Code sets CLAUDE_PROJECT_DIR; Codex sets no workspace env var and
    # instead runs hooks with cwd = workspace plus a `cwd` payload field.
    for key in ("CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()

    for key in ("cwd", "workspace_root", "workspaceRoot", "project_root", "projectRoot"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return Path(value).expanduser().resolve()

    return Path.cwd().resolve()


def normalize_event(event: str | None, payload: dict[str, Any]) -> str:
    candidate = event or payload.get("hook_event_name") or payload.get("hookEventName") or ""
    return str(candidate).strip().replace("_", "-").lower()


def tool_name(payload: dict[str, Any]) -> str:
    value = payload.get("tool_name") or payload.get("toolName") or payload.get("tool")
    return str(value or "")


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input") or payload.get("toolInput") or {}
    return value if isinstance(value, dict) else {}


def iter_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(iter_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(iter_strings(item))
    return strings


def collect_explicit_paths(payload: dict[str, Any]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(path: str) -> None:
        # Keep `..` (clean, not normalize): a symlink-then-`..` target must reach
        # relative_to_workspace intact so the filesystem resolve — not a lexical
        # pre-collapse — decides where the write truly lands.
        cleaned = clean_path_text(path)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            found.append(cleaned)

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                visit(child_value, str(child_key))
            return
        if isinstance(value, list):
            for child_value in value:
                visit(child_value, key)
            return
        if not isinstance(value, str):
            return

        lowered_key = key.lower()
        if "path" in lowered_key or "file" in lowered_key:
            add(value)

    visit(payload)
    return found


def command_text(payload: dict[str, Any]) -> str:
    data = tool_input(payload)
    for key in ("command", "cmd", "script"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return ""


def pre_tool_allow() -> dict[str, Any]:
    """Allow = empty output (exit 0, no stdout).

    Cross-host contract: Claude Code treats exit 0 with no stdout as "no opinion"
    — the call falls through to the host's normal permission flow (an explicit
    `permissionDecision: "allow"` would bypass permission prompts, which is not
    this gate's job). Codex additionally rejects `permissionDecision: "allow"`
    without `updatedInput` as unsupported output (the hook run is marked failed).
    """
    return {}


def deny(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def continue_output(message: str | None = None) -> dict[str, Any]:
    """Non-blocking event output: `systemMessage` only, or empty.

    Cross-host contract: Codex's Stop parser accepts `decision` only as the
    literal `"block"` — any other value fails deserialization and marks the hook
    run failed ("invalid stop hook JSON output"). Both hosts accept a bare
    `systemMessage` and treat empty stdout as "proceed".
    """
    if message:
        return {"systemMessage": message}
    return {}




def session_slot(payload: dict[str, Any]) -> str:
    """Concurrency dimension for `.runtime/`: both hosts send `session_id` in hook stdin."""
    return runtime_slot_name(str(payload.get("session_id") or "default"))


# AskUserQuestion = Claude Code; request_user_input = Codex (core tool name).
QUESTION_TOOLS = {"AskUserQuestion", "request_user_input"}


def question_purpose_reminder(workspace_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Remind once per question to derive the answer from purpose and principles first.

    The ack marker is per session: another session's pending question must not
    consume this session's reminder (or vice versa).
    """
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return pre_tool_allow()
    marker = stage_root / ".runtime" / "question-ack" / session_slot(payload)
    if marker.exists():
        try:
            marker.unlink()
        except OSError:
            pass
        return pre_tool_allow()
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), encoding="utf-8")
    except OSError:
        return pre_tool_allow()
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        principles_path = next(
            path
            for path in stage_topology.get_zone("canon", "official").index_surfaces
            if path.endswith("principles.md")
        )
        return deny(
            "Stage question gate: before asking, re-read the work item's Purpose and "
            f"`{principles_path}`. If the answer follows from the purpose or a principle, "
            "decide and report in one line instead of asking. If the user's decision is genuinely "
            "required (value judgment, conflicting principles, irreversible impact), ask again — "
            "this reminder fires once per question."
        )
    return deny(
        "Stage question gate: before asking, re-read the work item's Purpose and "
        "`past/canon/principles.md`. If the answer follows from the purpose or a principle, "
        "decide and report in one line instead of asking. If the user's decision is genuinely "
        "required (value judgment, conflicting principles, irreversible impact), ask again — "
        "this reminder fires once per question."
    )


def hierarchy_item_targets(workspace_root: Path, payload: dict[str, Any], name: str) -> list[tuple[str, str]]:
    """(relative_path, projected_post_edit_text) for every targeted work item file."""
    data = tool_input(payload)
    targets: list[tuple[str, str]] = []

    if name == "apply_patch":
        for text_value in iter_strings(data):
            for match in PATCH_FILE_RE.finditer(text_value):
                raw = match.group("path") or match.group("move") or ""
                relative = work_item_relative(raw, workspace_root)
                if relative:
                    targets.append(
                        (relative, projected_patch_text(text_value, relative, workspace_root))
                    )
        return targets

    target = ""
    for key in ("file_path", "path", "filePath"):
        value = data.get(key)
        if isinstance(value, str) and value:
            target = value
            break
    if not target:
        return []
    relative = work_item_relative(target, workspace_root)
    if not relative:
        return []
    existing = read_existing_text(workspace_root, relative)
    targets.append((relative, projected_file_text(existing, name, data)))
    return targets


def hierarchy_blocker(workspace_root: Path, payload: dict[str, Any], name: str) -> str:
    targets = hierarchy_item_targets(workspace_root, payload, name)
    if not targets:
        return ""

    stage_root = workspace_root / ".stage"
    items = load_all_work_items(stage_root)

    # Post-state status per work-item ID: disk first, then this call's projected
    # edits overlaid — so a patch that finalizes a parent AND opens a child under
    # it in the same call is judged against the parent's FINAL status, not its
    # stale on-disk status.
    status_by_id: dict[str, str] = {}
    item_by_path: dict[Path, WorkItem] = {}
    for item in items:
        status_by_id.setdefault(item.item_id, item.status)
        item_by_path[item.path] = item
    projected_id_by_stem: dict[str, str] = {}
    projected_by_path: dict[Path, tuple[str, str]] = {}
    for relative, projected in targets:
        projected_id = frontmatter_field_from_text(projected, "id") or Path(relative).stem
        projected_id_by_stem[Path(relative).stem] = projected_id
        projected_status = (frontmatter_field_from_text(projected, "status") or "active").lower()
        status_by_id[projected_id] = projected_status
        projected_by_path[workspace_root / relative] = (projected_id, projected_status)

    for relative, projected in targets:
        target_path = workspace_root / relative
        hierarchy_root = None
        for candidate in (
            stage_root / stage_topology.card_location_for_status("captured"),
            stage_root / stage_topology.card_location_for_status("active"),
            stage_root / stage_topology.card_location_for_status("archived"),
        ):
            try:
                target_path.relative_to(candidate)
            except ValueError:
                continue
            hierarchy_root = candidate
            break

        if hierarchy_root is not None:
            if target_path.parent == hierarchy_root and target_path.suffix == ".md":
                continue
            try:
                scale = work_record_scale(hierarchy_root, target_path)
            except ValueError as exc:
                return f"Stage hierarchy gate violation: {exc}"
            self_id, child_status = projected_by_path[target_path]
            parent_path = hierarchy_parent_record_path(hierarchy_root, target_path)
            if parent_path is None:
                continue
            projected_parent = projected_by_path.get(parent_path)
            disk_parent = item_by_path.get(parent_path)
            if projected_parent is not None:
                parent_id, parent_status = projected_parent
            elif disk_parent is not None:
                parent_id, parent_status = disk_parent.item_id, disk_parent.status
            else:
                expected = "story" if scale == "action" else "epic"
                return (
                    "Stage hierarchy gate violation: "
                    f"{expected} record not found at folder parent: {parent_path}"
                )
            if parent_id == self_id:
                return (
                    "Stage hierarchy gate violation: a work item cannot be "
                    f"its own folder parent: {parent_id}"
                )
            if (
                parent_status in WORK_FINAL_STATUSES
                and child_status not in WORK_FINAL_STATUSES
            ):
                return (
                    "Stage hierarchy gate violation: cannot open a child under "
                    f"a finalized folder parent ({parent_status}): {parent_id}"
                )
            continue

        parent_id = frontmatter_field_from_text(projected, "parent")
        if not parent_id:
            continue

        target_stem = Path(relative).stem
        self_id = projected_id_by_stem.get(target_stem, target_stem)
        if parent_id in {target_stem, self_id}:
            return f"Stage hierarchy gate violation: a work item cannot be its own parent: {parent_id}"

        parent_status = status_by_id.get(parent_id)
        if parent_status is None:
            return f"Stage hierarchy gate violation: parent work item not found: {parent_id}"

        child_status = (frontmatter_field_from_text(projected, "status") or "active").lower()
        if parent_status in WORK_FINAL_STATUSES and child_status in WORK_OPEN_STATUSES:
            return (
                "Stage hierarchy gate violation: cannot open a child under a finalized parent "
                f"({parent_status}): {parent_id}"
            )
    return ""


def enum_validity_blocker(workspace_root: Path, payload: dict[str, Any], name: str) -> str:
    """Reject a work-item write whose PROJECTED frontmatter carries an invalid
    status/verification/retrospective/promotion value — the same enums the audit
    checks, caught before the bad value lands instead of after. Reuses the
    hierarchy projection (disk + this call's edits), so a patch that only touches
    the body is judged on the merged result, not the raw fragment."""
    for relative, projected in hierarchy_item_targets(workspace_root, payload, name):
        error = work_item_enum_error(projected, relative)
        if error:
            return error
    return ""


def mutation_targets(
    payload: dict[str, Any], name: str, workspace_root: Path
) -> tuple[str, list[str], list[str]]:
    """(command, explicit paths, shell write+delete targets) for one call.

    Shell semantics apply only to shell tools: on Codex, apply_patch carries
    its PATCH BODY under tool_input.command, and parsing that as a shell
    command extracted junk targets (diff lines, markdown links) and could
    trip the delete/commit gates on mere content (live false deny,
    2026-07-10). Deleting a governed file is a governed modification, so
    rm/del/Remove-Item operands join the write-target stream."""
    command = command_text(payload) if name in SHELL_TOOLS else ""
    explicit_paths = collect_explicit_paths(payload)
    shell_write_targets: list[str] = []
    if command:
        shell_write_targets = shell_write_paths(command, workspace_root)
        shell_write_targets.extend(
            path
            for path in shell_delete_paths(command, workspace_root)
            if path not in shell_write_targets
        )
        for path in shell_write_targets:
            if path and path not in explicit_paths:
                explicit_paths.append(path)
    if name == "apply_patch":
        for text_value in iter_strings(tool_input(payload)):
            for match in PATCH_FILE_RE.finditer(text_value):
                # Keep `..` (clean, not normalize) for symlink-safe resolve.
                cleaned = clean_path_text(match.group("path") or match.group("move") or "")
                if cleaned and cleaned not in explicit_paths:
                    explicit_paths.append(cleaned)
    return command, explicit_paths, shell_write_targets


def claim_owner_id(payload: dict[str, Any]) -> str:
    """Correlates a reservation with the post that completes it: the host's
    tool_use_id when present (Codex sends it on both events), else the
    session slot — a mismatch is safe, the claim just ages into restore."""
    return str(payload.get("tool_use_id") or "") or session_slot(payload)


def handle_post_tool(payload: dict[str, Any]) -> dict[str, Any]:
    """Complete two-phase intent reservations after the tool ran.

    The pre gate reserved by renaming the intent to a claim; the arrival of
    PostToolUse confirms the tool executed, so the matching claims are
    consumed. This handler never blocks — the write already happened. A run
    whose post never arrives (crash, rejected permission, a host without the
    event) leaves its claim to the age-based restore instead."""
    name = tool_name(payload)
    workspace_root = resolve_workspace_root(payload)
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return {}
    write_tools = WRITE_TOOLS | configured_write_tools(stage_root)
    if name not in SHELL_TOOLS and name not in write_tools:
        return {}
    _command, explicit_paths, shell_write_targets = mutation_targets(
        payload, name, workspace_root
    )

    def targets_past(raw: str) -> bool:
        if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
            return any(
                path_targets_stage_official(form)
                for form in stage_relative_forms(raw, workspace_root)
            )
        return any(
            path_targets_stage_past(form) for form in stage_relative_forms(raw, workspace_root)
        )

    past_gate_raw = explicit_paths if name in write_tools else shell_write_targets
    target_past_paths = [
        entry_relative_to_workspace(raw, workspace_root)
        for raw in past_gate_raw
        if targets_past(raw)
    ]
    if target_past_paths:
        consume_claims_for(
            stage_root, workspace_root, target_past_paths, claim_owner_id(payload)
        )
    return {}


def validate_pre_tool(payload: dict[str, Any]) -> dict[str, Any]:
    name = tool_name(payload)
    workspace_root = resolve_workspace_root(payload)
    if name in QUESTION_TOOLS:
        return question_purpose_reminder(workspace_root, payload)
    stage_root = workspace_root / ".stage"
    # A project registers host/MCP file-writing tools the built-in allowlist
    # does not know (`extra_write_tools`); they are classified BEFORE the
    # unknown-name early allow, or the seam would never see them.
    write_tools = WRITE_TOOLS | configured_write_tools(stage_root)
    if name and name not in SHELL_TOOLS and name not in write_tools:
        return pre_tool_allow()

    command, explicit_paths, shell_write_targets = mutation_targets(
        payload, name, workspace_root
    )

    schema_targets = explicit_paths if name in write_tools else shell_write_targets
    follows_symlinks = name in {"Write", "Edit", "MultiEdit"} or (
        name not in WRITE_TOOLS
        and isinstance(tool_input(payload).get("content"), str)
    )
    governed_mutation = bool(command and command_has_git_commit(command)) or any(
        is_stage_internal_path(raw, workspace_root)
        or is_source_path(raw, workspace_root, follows_symlinks)
        for raw in schema_targets
    )
    if stage_root.exists() and governed_mutation:
        maintenance_marker = stage_root / stage_topology.MAINTENANCE_MARKER
        if maintenance_marker.exists():
            return deny(
                "Stage schema migration maintenance is active; governed project and `.stage` "
                "mutations are denied while the migration marker exists. Close other agent "
                "windows. The migration owner must finish or run the stage-migrate abort path."
            )

    # An explicit `.stage` delete is always blocked; a strict-ancestor delete
    # (`rm -rf .`) is filtered inside command_deletes_stage to fire only when a
    # `.stage` exists, so a pre-init workspace is not over-denied.
    if command and command_deletes_stage(command, workspace_root):
        return deny(
            "Stage rule violation: deleting `.stage` entirely is blocked. "
            "Modify only the specific files you need so official artifacts, current work status, "
            "and plans are not lost."
        )

    if stage_root.exists() and not governance_broken(stage_root):
        schema_blocker = schema_migration_banner(stage_root)
        # Once a project is behind the enforced contract, every mutation gate
        # fails closed for governed source and Stage-internal writes. Deliberately
        # excluded paths remain outside governance. A direct invocation of
        # stage-migrate/--abort has no shell write target and remains callable;
        # read-only commands likewise pass through.
        if governed_mutation and schema_blocker:
            return deny(schema_blocker)

    # Classify each write target by the UNION of its forms (resolved, entry,
    # lexical — see stage_relative_forms). Union is fail-closed: the resolved
    # form catches symlink/`..` re-entry into `.stage`, the entry form catches
    # an aliased parent whose leaf is an outward symlink, the lexical form
    # catches a degenerate `.stage -> .` and an unlink/move of a symlink whose
    # leaf sits in `.stage/past` (where resolve would deref away).
    def targets_root(raw: str) -> bool:
        return any(
            path_targets_stage_root(form) for form in stage_relative_forms(raw, workspace_root)
        )

    def targets_past(raw: str) -> bool:
        if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
            return any(
                path_targets_stage_official(form)
                for form in stage_relative_forms(raw, workspace_root)
            )
        return any(
            path_targets_stage_past(form) for form in stage_relative_forms(raw, workspace_root)
        )

    if stage_root.exists() and active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        write_targets = explicit_paths if name in write_tools else shell_write_targets
        for raw in write_targets:
            legacy_form = next(
                (
                    form
                    for form in stage_relative_forms(raw, workspace_root)
                    if stage_topology.is_legacy_path(form)
                ),
                None,
            )
            if legacy_form is None:
                continue
            replacements = stage_topology.legacy_replacement_paths(legacy_form)
            replacement_text = ", ".join(f"`.stage/{path}`" for path in replacements)
            retired_root = stage_topology.legacy_root(legacy_form)
            return deny(
                "Stage schema-v4 legacy-root violation: the write target resolves under a "
                f"retired schema-v3 root. `.stage/{retired_root}/` is retired in v4. Use the "
                f"registry-derived v4 replacement {replacement_text}."
            )

    for raw in explicit_paths:
        # Per-form conjunction: the SAME form must be both stage-internal and
        # script-suffixed — `.stage/run.sh -> outside.txt` leaves an executable
        # `.sh` entry inside `.stage` even though its resolve ends `.txt`, while
        # a `.md` entry pointing at an outside `.sh` leaves none.
        if any(
            path_targets_stage_root(form) and form.lower().endswith(OS_SCRIPT_SUFFIXES)
            for form in stage_relative_forms(raw, workspace_root)
        ):
            return deny(
                "Stage portability rule violation: OS-specific executable scripts are not allowed "
                "inside `.stage`. Use the Python standard library or Markdown artifacts so behavior "
                "stays identical on Codex, Claude, Windows, Linux, and macOS."
            )

    if stage_root.exists() and governance_broken(stage_root):
        write_targets = explicit_paths if name in write_tools else shell_write_targets
        external_targets = [
            path for path in write_targets if not is_stage_internal_path(path, workspace_root)
        ]
        if external_targets:
            return deny(
                "Stage governance violation: `.stage/settings.json` exists but is unreadable or "
                "malformed, so the governed scope cannot be trusted. Repair `.stage/settings.json` "
                "before modifying other files."
            )

    if stage_root.exists() and name in write_tools:
        blocker = hierarchy_blocker(workspace_root, payload, name)
        if blocker:
            return deny(blocker)
        blocker = enum_validity_blocker(workspace_root, payload, name)
        if blocker:
            return deny(blocker)
        blocker = reattribution_blocker(
            workspace_root, payload, name, shell_write_targets
        )
        if blocker:
            return deny(blocker)
        # Write/Edit/MultiEdit are CONTENT writes — they follow a symlink target
        # and modify the dereferenced file (not the entry). apply_patch mixes
        # add/update/delete, so it stays entry-based (best-effort). A
        # registered extra tool carrying a whole-file `content` is a content
        # write too.
        follows = name in {"Write", "Edit", "MultiEdit"} or (
            name not in WRITE_TOOLS and isinstance(tool_input(payload).get("content"), str)
        )
        blocker = source_registration_blocker(workspace_root, explicit_paths, follows)
        if blocker:
            return deny(blocker)

    if stage_root.exists():
        projected_targets = (
            explicit_paths if name in write_tools else shell_write_targets
        )
        blocker = projected_closure_promotion_blocker(
            workspace_root,
            payload,
            name,
            projected_targets,
            shell_write_targets,
        )
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command:
        if interpreter_inline_stage_write(command):
            return deny(
                "Stage guard cannot verify what opaque inline interpreter code writes, so a "
                "command that runs inline code (for example, python -c, node/perl -e, or an "
                "interpreter heredoc) and references `.stage` is refused. Use Write/Edit, which "
                "are gated and flow through work registration/promotion, or a named script file "
                "instead of inline interpreter code."
            )
        blocker = reattribution_blocker(
            workspace_root, payload, name, shell_write_targets
        )
        if blocker:
            return deny(blocker)
        blocker = source_registration_blocker(workspace_root, shell_write_targets)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command and command_has_git_commit(command):
        files = staged_files(workspace_root)
        files.extend(path for path in git_add_paths_from_command(command, workspace_root) if path not in files)
        files.extend(path for path in git_commit_pathspec_files(command, workspace_root) if path not in files)
        if git_commit_all_requested(command):
            files.extend(path for path in changed_files(workspace_root) if path not in files)
        blocker = commit_blocker(workspace_root, files)
        if blocker:
            return deny(blocker)

    # The promotion gate runs LAST: it consumes a pending intent by an atomic
    # rename reservation, so every deny-capable gate above must have passed —
    # otherwise a call denied later would burn the honest actor's one-shot
    # authorization. It takes the entry-canonical form (parents resolved,
    # leaf kept as named), the shape exact-entry authorizations compare.
    past_gate_raw = explicit_paths if name in write_tools else shell_write_targets
    target_past_paths = [
        entry_relative_to_workspace(raw, workspace_root)
        for raw in past_gate_raw
        if targets_past(raw)
    ]
    if target_past_paths:
        blocker = promotion_blocker(
            workspace_root, target_past_paths, claim_owner_id(payload)
        )
        if blocker:
            return deny(blocker)

    return pre_tool_allow()


def handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    workspace_root = resolve_workspace_root(payload)
    prune_question_ack_markers(workspace_root / ".stage")
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": session_context(workspace_root),
        }
    }


def handle_stop(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("stop_hook_active"):
        return continue_output()

    workspace_root = resolve_workspace_root(payload)
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return continue_output()

    # One summary per session so concurrent Claude/Codex sessions keep their
    # own handoff instead of last-write-wins on a single slot.
    migrate_legacy_runtime(stage_root)
    summary_path = sessions_root(stage_root) / f"{session_slot(payload)}.md"
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summarize_stage(stage_root), encoding="utf-8")
    except OSError as exc:
        return continue_output(f"Stage session summary write failed: {exc}")

    prune_session_summaries(stage_root, keep_path=summary_path)
    return continue_output(
        f"Stage session summary saved: .stage/.runtime/sessions/{summary_path.name}"
    )


def handle_event(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_event(event, payload)
    if normalized in {"session-start", "sessionstart"}:
        return handle_session_start(payload)
    if normalized in {"pre-tool-use", "pretooluse"}:
        return validate_pre_tool(payload)
    if normalized in {"post-tool-use", "posttooluse"}:
        return handle_post_tool(payload)
    if normalized == "stop":
        return handle_stop(payload)
    return continue_output()


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    args = list(sys.argv[1:] if argv is None else argv)
    event = args[0] if args else None
    payload = load_payload()
    output = handle_event(event or "", payload)
    # Empty output means "proceed": both hosts accept it, and Codex rejects
    # explicit allow/approve decisions as unsupported.
    if output:
        print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
