#!/usr/bin/env python3
"""Stage hook guard.

The hook keeps Stage rules executable without depending on host-specific shell
scripts. It accepts Claude hook JSON on stdin and writes hook JSON on stdout.
"""

from __future__ import annotations

import hashlib
import json
import uuid
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
    DEFAULT_EXCLUDED_PREFIXES,
    clean_path_text,
    entry_relative_to_workspace,
    governance_broken,
    is_outside_workspace,
    is_source_path,
    is_stage_internal_path,
    load_governance,
    normalize_path_text,
    path_has_prefix,
    path_targets_stage_archive,
    path_targets_stage_past,
    path_targets_stage_root,
    relative_to_workspace,
    stage_real_root,
    stage_relative_forms,
)
from stage_shell import (  # noqa: E402  (after sys.path bootstrap)
    _restore_sentinels,
    command_deletes_stage,
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
    PROMOTION_FINAL,
    RETROSPECTIVE_DONE,
    VERIFICATION_DONE,
    WORK_FINAL_STATUSES,
    WORK_OPEN_STATUSES,
    WorkItem,
    archive_target_item_id,
    archive_target_retro_id,
    changed_files,
    commit_blocker,
    frontmatter_field_from_text,
    git_add_paths_from_command,
    item_completion_blockers,
    item_is_completed,
    item_is_open,
    item_promotes_path,
    load_archive_work_items,
    load_work_items,
    parse_frontmatter,
    projected_file_text,
    projected_patch_text,
    read_existing_text,
    retrospective_ref_id,
    source_registration_blocker,
    split_scope,
    stage_completion_blockers,
    staged_files,
    work_item_relative,
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

STAGE_MUTATION_TOOLS = SHELL_TOOLS | WRITE_TOOLS
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


def runtime_slot_name(value: str) -> str:
    """Filesystem-safe slot name for per-session/per-item runtime files."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", value.strip())
    return cleaned or "default"


def session_slot(payload: dict[str, Any]) -> str:
    """Concurrency dimension for `.runtime/`: both hosts send `session_id` in hook stdin."""
    return runtime_slot_name(str(payload.get("session_id") or "default"))


def intents_root(stage_root: Path) -> Path:
    return stage_root / ".runtime" / "intents"


def migrate_legacy_runtime(stage_root: Path) -> None:
    """Move 0.1.0 single-slot runtime files into the per-item/per-session layout.

    Projects initialized by the 0.1.0 release may hold a pending
    `promote-intent.json` or a `session-summary.md`; ignoring them would deny a
    legitimately prepared promotion or drop the last handoff.
    """
    runtime = stage_root / ".runtime"
    legacy_intent = runtime / "promote-intent.json"
    if legacy_intent.exists():
        try:
            data = json.loads(legacy_intent.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, dict):
            declared = intent_paths(data)
            written = [write_intent_file(stage_root, data, one) for one in declared]
            if all(target is not None for target in written):
                try:
                    legacy_intent.unlink()
                except OSError:
                    pass
    # A crashed session can leave `*.json.claim-*` reservation files behind;
    # the reservation itself already consumed the intent, so finishing the
    # deletion after a day is safe.
    now = datetime.now(timezone.utc).timestamp()
    try:
        for claim in intents_root(stage_root).glob("*.json.claim-*"):
            try:
                if now - claim.stat().st_mtime > 24 * 60 * 60:
                    claim.unlink()
            except OSError:
                pass
    except OSError:
        pass
    legacy_summary = runtime / "session-summary.md"
    if legacy_summary.exists():
        sessions = sessions_root(stage_root)
        try:
            sessions.mkdir(parents=True, exist_ok=True)
            # Never overwrite or drop an existing handoff: a taken `legacy.md`
            # slot means a prior migration or a live session already owns it, so
            # claim a fresh numbered slot instead of unlinking the incoming one.
            target = sessions / "legacy.md"
            index = 1
            while target.exists():
                target = sessions / f"legacy-{index}.md"
                index += 1
            legacy_summary.replace(target)
        except OSError:
            pass


def write_intent_file(stage_root: Path, intent: dict[str, Any], path_value: str) -> Path | None:
    """Persist a single-path intent; the slot is (work item, canonical path).

    The path is canonicalized to the ENTRY-relative workspace form (parents
    resolved, leaf kept as named) before slotting and storage, so replanting
    the same target as absolute vs relative stays idempotent while two aliased
    leaves stay distinct slots. The filename embeds the basename plus a digest
    of the full path — bounded regardless of target depth. A slot collision
    with a DIFFERENT logical (item, path) pair falls through to a numbered
    suffix instead of overwriting someone else's pending authorization.
    """
    root = intents_root(stage_root)
    try:
        workspace_root = stage_root.parent.resolve()
    except OSError:
        workspace_root = stage_root.parent
    normalized = entry_relative_to_workspace(path_value, workspace_root)
    record = {**intent, "paths": [normalized]}
    item = str(intent.get("work_item") or "intent")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]
    basename = runtime_slot_name(Path(normalized).name)[:40]
    base = f"{runtime_slot_name(item)}--{basename}-{digest}"
    try:
        root.mkdir(parents=True, exist_ok=True)
        for index in range(20):
            target = root / (base + ("" if index == 0 else f"-{index}") + ".json")
            if target.exists():
                try:
                    existing = json.loads(target.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    existing = None
                same_slot = (
                    isinstance(existing, dict)
                    and str(existing.get("work_item") or "") == item
                    and [entry_relative_to_workspace(p, workspace_root) for p in intent_paths(existing)]
                    == [normalized]
                )
                if not same_slot:
                    continue
            target.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            return target
    except OSError:
        pass
    return None


def read_intent_files(stage_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    try:
        files = sorted(intents_root(stage_root).glob("*.json"))
    except OSError:
        return []
    intents: list[tuple[Path, dict[str, Any]]] = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            intents.append((path, data))
    return intents


def load_promotion_intents(stage_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """All pending intents — one file per (work item, path) so authorizing a
    write consumes state by an atomic rename reservation, never by rewriting a
    shared file."""
    migrate_legacy_runtime(stage_root)
    intents = read_intent_files(stage_root)
    split_any = False
    for path, data in intents:
        declared = intent_paths(data)
        if len(declared) <= 1:
            continue
        # Normalize a multi-path file (pre-split layout) into per-path slots.
        if all(write_intent_file(stage_root, data, one) is not None for one in declared):
            split_any = True
            try:
                path.unlink()
            except OSError:
                pass
    if split_any:
        return read_intent_files(stage_root)
    return intents


def intent_paths(intent: dict[str, Any]) -> list[str]:
    # Cleaned, NOT dot-collapsed (see split_scope): a legacy intent spelled
    # with `..` must reach entry canonicalization intact.
    raw = intent.get("paths")
    if isinstance(raw, list):
        return [clean_path_text(str(item)) for item in raw if str(item).strip()]
    raw_path = intent.get("path")
    if isinstance(raw_path, str) and raw_path.strip():
        return [clean_path_text(raw_path)]
    return []


def promotion_blocker(workspace_root: Path, target_paths: list[str]) -> str:
    """Per-path intents make consumption an atomic rename reservation.

    Each pending intent covers exactly one path (the loader normalizes
    multi-path files), so authorizing a write never rewrites another intent's
    state — the read-modify-write race that could resurrect an already
    consumed authorization cannot occur. Acquisition is the rename to a claim
    file; the losing concurrent session is denied.
    """
    stage_root = workspace_root / ".stage"
    intents = load_promotion_intents(stage_root)
    if not intents:
        return (
            "Stage promotion gate violation: modifying `.stage/past/` requires an out-of-band "
            "promotion intent. Run `stage-retrospective`, then create one with "
            "`scripts/promote_intent.py` (writes `.stage/.runtime/intents/<work-item>--<path>.json`)."
        )

    # Entry-canonical matching: an intent authorizes the exact entry it names,
    # never a sibling alias of the same resolved target.
    requested = {entry_relative_to_workspace(path, workspace_root) for path in target_paths}
    by_path: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for intent_file, intent in intents:
        for declared in intent_paths(intent):
            by_path.setdefault(entry_relative_to_workspace(declared, workspace_root), []).append(
                (intent_file, intent)
            )

    selected: dict[Path, dict[str, Any]] = {}
    covered_paths: dict[Path, list[str]] = {}
    for path in sorted(requested):
        matching = by_path.get(path, [])
        if not matching:
            return (
                "Stage promotion gate violation: no pending intent's paths match the "
                f"modification targets ({path})."
            )
        if len(matching) > 1:
            # Fail closed on ambiguity: consuming an arbitrary intent could let
            # one work item's write ride another item's authorization.
            names = ", ".join(sorted(intent_file.name for intent_file, _ in matching))
            return (
                "Stage promotion gate violation: multiple pending intents cover the modification "
                f"targets ({names}). Remove or narrow the intents so exactly one matches."
            )
        intent_file, intent = matching[0]
        selected[intent_file] = intent
        covered_paths.setdefault(intent_file, []).append(path)

    # Validate every involved intent before consuming any (no partial consume
    # on a failing multi-target write).
    for intent_file, intent in selected.items():
        error = intent_validation_blocker(
            stage_root,
            workspace_root,
            intent_file,
            intent,
            covered_paths[intent_file],
            set(covered_paths[intent_file]),
        )
        if error:
            return error

    # Atomic reservation: rename is the acquisition point. If another session
    # already consumed an intent between validation and here, acquisition
    # fails and this write is denied instead of riding the same one-shot
    # authorization. Deterministic (name) order keeps partial overlaps
    # fail-fast; acquired claims are rolled back on failure.
    claimed: list[tuple[Path, Path]] = []
    for intent_file in sorted(selected, key=lambda path: path.name):
        claim = intent_file.with_name(f"{intent_file.name}.claim-{uuid.uuid4().hex[:8]}")
        try:
            intent_file.rename(claim)
        except OSError:
            for original, taken in claimed:
                try:
                    taken.rename(original)
                except OSError:
                    pass
            return (
                "Stage promotion gate violation: a pending intent for these targets was just "
                "consumed by another session. Re-plant the intent if this write is still intended."
            )
        claimed.append((intent_file, claim))
    for _, claim in claimed:
        try:
            claim.unlink()
        except OSError:
            pass
    return ""


def intent_validation_blocker(
    stage_root: Path,
    workspace_root: Path,
    intent_file: Path,
    intent: dict[str, Any],
    target_paths: list[str],
    requested: set[str],
) -> str:
    """Validate one path-matching intent; consumes it and returns "" on success."""
    work_item_id = str(intent.get("work_item") or "").strip()
    if not work_item_id:
        return "Stage promotion gate violation: the promotion intent has no work_item."

    items = load_work_items(stage_root) + load_archive_work_items(stage_root)
    matched = [item for item in items if item.item_id == work_item_id or item.path.stem == work_item_id]
    if not matched:
        return f"Stage promotion gate violation: work_item `{work_item_id}` was not found."

    item = matched[0]
    intent_type = str(intent.get("type") or "promotion").strip().lower()
    if intent_type == "archive":
        if not all(path_targets_stage_archive(path) for path in target_paths):
            return "Stage archive gate violation: an archive intent may only target `.stage/past/work/archive/`."
        item_targets = [path for path in target_paths if archive_target_item_id(path, workspace_root)]
        retro_targets = [path for path in target_paths if archive_target_retro_id(path, workspace_root)]
        if len(item_targets) + len(retro_targets) != len(target_paths):
            return (
                "Stage archive gate violation: archive targets must be "
                "`items/<id>.md` or `retrospectives/<id>.md`."
            )
        item_ids = {archive_target_item_id(path, workspace_root) for path in item_targets}
        if item_targets and item_ids != {item.item_id}:
            return "Stage archive gate violation: the items/ target filename must match the work_item ID."
        ref_id = retrospective_ref_id(item)
        for path in retro_targets:
            if not ref_id or archive_target_retro_id(path, workspace_root) != ref_id:
                return (
                    "Stage archive gate violation: the retrospectives/ target filename must match "
                    "the work item's retrospective_ref."
                )
        if item.status not in {"completed", "rejected", "archived"}:
            return (
                f"Stage archive gate violation: work_item `{work_item_id}` status must be "
                f"completed/rejected. status `{item.status}`"
            )
        blockers = item_completion_blockers(item) if item_is_completed(item) else []
        if blockers:
            return (
                "Stage archive gate violation: close the completed item's verification, retrospective, "
                "and promotion decision first. " + " / ".join(blockers)
            )
        return ""

    blockers = item_completion_blockers(item)
    if blockers or not item_is_completed(item) or item.promotion not in {"approved", "promoted"}:
        detail = " / ".join(blockers) if blockers else f"{work_item_id}: status `{item.status}`"
        if item.promotion not in {"approved", "promoted"}:
            detail = f"{work_item_id}: promotion `{item.promotion}`"
        return "Stage promotion gate violation: the linked work item is not in a completed state. " + detail
    if not all(item_promotes_path(item, path, workspace_root) for path in target_paths):
        return "Stage promotion gate violation: the target paths do not match the work item's promotes list."

    return ""


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
    items = load_work_items(stage_root) + load_archive_work_items(stage_root)

    # Post-state status per work-item ID: disk first, then this call's projected
    # edits overlaid — so a patch that finalizes a parent AND opens a child under
    # it in the same call is judged against the parent's FINAL status, not its
    # stale on-disk status.
    status_by_id: dict[str, str] = {}
    for item in items:
        status_by_id.setdefault(item.item_id, item.status)
    projected_id_by_stem: dict[str, str] = {}
    for relative, projected in targets:
        projected_id = frontmatter_field_from_text(projected, "id") or Path(relative).stem
        projected_id_by_stem[Path(relative).stem] = projected_id
        status_by_id[projected_id] = (
            frontmatter_field_from_text(projected, "status") or "active"
        ).lower()

    for relative, projected in targets:
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


def validate_pre_tool(payload: dict[str, Any]) -> dict[str, Any]:
    name = tool_name(payload)
    if name in QUESTION_TOOLS:
        return question_purpose_reminder(resolve_workspace_root(payload), payload)
    if name and name not in STAGE_MUTATION_TOOLS:
        return pre_tool_allow()

    # Shell semantics apply only to shell tools: on Codex, apply_patch carries
    # its PATCH BODY under tool_input.command, and parsing that as a shell
    # command extracted junk targets (diff lines, markdown links) and could
    # trip the delete/commit gates on mere content (live false deny, 2026-07-10).
    command = command_text(payload) if name in SHELL_TOOLS else ""
    explicit_paths = collect_explicit_paths(payload)
    shell_write_targets: list[str] = []
    if command:
        shell_write_targets = shell_write_paths(command)
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
    workspace_root = resolve_workspace_root(payload)
    stage_root = workspace_root / ".stage"

    # An explicit `.stage` delete is always blocked; a strict-ancestor delete
    # (`rm -rf .`) is filtered inside command_deletes_stage to fire only when a
    # `.stage` exists, so a pre-init workspace is not over-denied.
    if command and command_deletes_stage(command, workspace_root):
        return deny(
            "Stage rule violation: deleting `.stage` entirely is blocked. "
            "Modify only the specific files you need so official artifacts, current work status, "
            "and plans are not lost."
        )

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
        return any(
            path_targets_stage_past(form) for form in stage_relative_forms(raw, workspace_root)
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

    past_gate_raw = explicit_paths if name in WRITE_TOOLS else shell_write_targets
    # The promotion gate consumes exact-entry authorizations, so hand it the
    # entry-canonical form (parents resolved, leaf kept as named).
    target_past_paths = [
        entry_relative_to_workspace(raw, workspace_root)
        for raw in past_gate_raw
        if targets_past(raw)
    ]
    if target_past_paths:
        blocker = promotion_blocker(workspace_root, target_past_paths)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and governance_broken(stage_root):
        write_targets = explicit_paths if name in WRITE_TOOLS else shell_write_targets
        external_targets = [
            path for path in write_targets if not is_stage_internal_path(path, workspace_root)
        ]
        if external_targets:
            return deny(
                "Stage governance violation: `.stage/settings.json` exists but is unreadable or "
                "malformed, so the governed scope cannot be trusted. Repair `.stage/settings.json` "
                "before modifying other files."
            )

    if stage_root.exists() and name in WRITE_TOOLS:
        blocker = hierarchy_blocker(workspace_root, payload, name)
        if blocker:
            return deny(blocker)
        # Write/Edit/MultiEdit are CONTENT writes — they follow a symlink target
        # and modify the dereferenced file (not the entry). apply_patch mixes
        # add/update/delete, so it stays entry-based (best-effort).
        follows = name in {"Write", "Edit", "MultiEdit"}
        blocker = source_registration_blocker(workspace_root, explicit_paths, follows)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command:
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

    return pre_tool_allow()


def read_if_exists(path: Path, limit: int = 1400) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def session_context(workspace_root: Path) -> str:
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        # The stage-init session itself must still see host instructions.
        return (
            "## Stage\n"
            "This project has no `.stage/`. If the Stage harness applies to this project, "
            "create the artifact structure first with `stage-init`."
            + consumer_context_section(workspace_root, pre_init=True)
        )

    parts = [
        "## Stage context",
        "- Global time axis: `past` is official, `present` is in progress, `future` is planned.",
        "- Space axis: `canon`, `model`, `decisions`, `work`, `state`, `operations` divide responsibility.",
        "- Core principles (full catalog: `past/canon/principles.md`):",
        "  SSOT — one owning location per durable fact. MECE — no overlap, no known gaps.",
        "  Fail Fast — surface wrong premises early. AHA — no abstraction before repetition.",
        "  Completion — external view + internal view + retrospective, all three.",
        "  Honesty — never assert unverified facts; no partial completion, no silent substitution.",
        "- Cite the governing principles in every decision record and retrospective.",
        "- Register an active work item in `.stage/present/work/items/` before modifying governed files "
        "(nearly all files are governed by default; see `.stage/settings.json`).",
        "- Modifying `past` requires a pending intent (`scripts/promote_intent.py`) and a completed work item.",
        "- Artifact map — W work `present/work/items` · R retro `present/work/retrospectives` · "
        "DE decision `present/work/decisions` · D approved `past/decisions/records` · "
        "O/Q/A/K state `present/state/*` · B backlog `future/backlog/items` · P proposal · M milestone. "
        "Full catalog: `operations/artifacts.md`; routing: `index.md`.",
    ]

    snippets: list[tuple[str, Path | None]] = [
        ("Current state", stage_root / "present" / "state" / "current.md"),
        ("Active work", stage_root / "present" / "work" / "active.md"),
        ("Review candidates", stage_root / "present" / "work" / "review.md"),
    ]
    for title, path in snippets:
        body = read_if_exists(path) if path is not None else ""
        if body:
            parts.append(f"\n### {title}\n{body}")

    consumer_section = consumer_context_section(workspace_root)
    if consumer_section:
        parts.append(consumer_section)

    questions = open_question_lines(stage_root)
    if questions:
        parts.append("\n### Open questions\n" + "\n".join(questions))
    backlog = selected_backlog_lines(stage_root)
    if backlog:
        parts.append("\n### Selected backlog\n" + "\n".join(backlog))

    recent_bodies = [
        body
        for body in (read_if_exists(path) for path in latest_session_summaries(stage_root))
        if body
    ]
    if recent_bodies:
        heading = "Most recent session" if len(recent_bodies) == 1 else "Most recent sessions (concurrent)"
        parts.append(f"\n### {heading}\n" + "\n\n".join(recent_bodies))

    return "\n".join(parts)


# Host-project instruction sources, relative to the workspace root. Stage
# works without any of them; when present they are project norms the session
# must actively use (and challenge when wrong) rather than ignore.
CONSUMER_CONTEXT_FILES: tuple[str, ...] = (
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
)
CONSUMER_CONTEXT_DIRS: tuple[str, ...] = (
    ".claude/rules",
    ".claude/skills",
    ".agents/skills",
)
CONSUMER_CONTEXT_MAX_LINES = 10


def agents_instruction_file(directory: Path) -> str | None:
    """Codex reads AGENTS.override.md INSTEAD of AGENTS.md when both exist —
    listing both would mark an intentional override as a contradiction."""
    for name in ("AGENTS.override.md", "AGENTS.md"):
        if (directory / name).is_file():
            return name
    return None


def directory_instruction_lines(directory: Path, prefix: str = "") -> list[str]:
    """Instruction sources of one directory — the same list applies to the
    workspace root and to each monorepo package one level down."""
    lines: list[str] = []
    for relative in CONSUMER_CONTEXT_FILES:
        if (directory / relative).is_file():
            lines.append(f"- `{prefix}{relative}`")
    agents_name = agents_instruction_file(directory)
    if agents_name:
        lines.append(f"- `{prefix}{agents_name}`")
    for relative in CONSUMER_CONTEXT_DIRS:
        candidate = directory / relative
        try:
            count = sum(1 for entry in candidate.iterdir() if not entry.name.startswith("."))
        except OSError:
            continue
        if count:
            lines.append(f"- `{prefix}{relative}/` ({count} entries)")
    return lines


# Dependency/build trees are not project-owned: a third-party package must not
# be able to inject "host instructions" into the session.
UNOWNED_DIR_NAMES = {
    "node_modules",
    "vendor",
    "third_party",
    "external",
    "dist",
    "build",
    "target",
    "venv",
}


def child_directories(directory: Path, workspace_root: Path) -> list[Path]:
    try:
        resolved_root = workspace_root.resolve()
    except OSError:
        resolved_root = workspace_root
    children: list[Path] = []
    try:
        entries = sorted(directory.iterdir())
    except OSError:
        return []
    for entry in entries:
        if entry.name.startswith(".") or entry.name in UNOWNED_DIR_NAMES:
            continue
        try:
            if not entry.is_dir():
                continue
            # A symlink escaping the workspace is not project-owned either.
            if not entry.resolve().is_relative_to(resolved_root):
                continue
        except OSError:
            continue
        children.append(entry)
    return children


def active_scope_paths(stage_root: Path) -> set[str]:
    """Full scoped subtree paths of the packages current or next work touches,
    from open work items' `scope`. Full paths (not just the first segment) so a
    two-level scope like `packages/zapp` prioritizes that exact subtree's
    instructions over its 10 alphabetical siblings under `packages/` (P35). A
    selected backlog item's relevant scope is its realizing work item's scope,
    already open here — backlog records carry no scope of their own."""
    scopes: set[str] = set()
    try:
        items = load_work_items(stage_root)
    except OSError:
        return scopes
    for item in items:
        if item.status not in WORK_OPEN_STATUSES:
            continue
        for scope in item.scope:
            normalized = normalize_path_text(scope).strip("/")
            if normalized and normalized != "*":
                scopes.add(normalized)
    return scopes


def _instruction_source_dir(line: str) -> str:
    """The owning package directory of an inventory line like
    ``- `pkg/.claude/CLAUDE.md` ``. Metadata containers (`.claude`, `.agents`,
    `.github`) are stripped so the source attributes to the package (`pkg`),
    which is what a work-item scope names."""
    inner = line.split("`", 2)
    if len(inner) < 2:
        return ""
    ref = inner[1].rstrip("/")
    ref = ref.rsplit("/", 1)[0] if "/" in ref else ""
    segments = ref.split("/") if ref else []
    trimmed: list[str] = []
    for segment in segments:
        if segment in {".claude", ".agents", ".github"}:
            break
        trimmed.append(segment)
    return "/".join(trimmed)


def _scope_prioritized(source_dir: str, scopes: set[str]) -> bool:
    """A source is prioritized if its directory and a scope path are on the same
    branch (one is a prefix of the other)."""
    for scope in scopes:
        if source_dir == scope or source_dir.startswith(scope + "/") or scope.startswith(source_dir + "/"):
            return True
    return False


def consumer_context_lines(
    workspace_root: Path,
    limit: int = CONSUMER_CONTEXT_MAX_LINES,
    stage_root: Path | None = None,
) -> list[str]:
    root_lines = directory_instruction_lines(workspace_root)

    # Monorepo packages carry their own subtree-scoped instructions; container
    # layouts (packages/foo, apps/web) put them two levels down. Discovery is
    # bounded to depth 2 and the total line cap below.
    package_lines: list[str] = []
    for child in child_directories(workspace_root, workspace_root):
        package_lines.extend(directory_instruction_lines(child, prefix=f"{child.name}/"))
        for grandchild in child_directories(child, workspace_root):
            package_lines.extend(
                directory_instruction_lines(
                    grandchild, prefix=f"{child.name}/{grandchild.name}/"
                )
            )

    # Sources on the branch of an active work item's scope come first so the cap
    # never drops the guide governing the work at hand — full-path, not first
    # segment, so `packages/zapp` beats `packages/a00…`.
    scopes = active_scope_paths(stage_root) if stage_root else set()
    package_lines.sort(
        key=lambda line: (not _scope_prioritized(_instruction_source_dir(line), scopes),)
    )
    lines = root_lines + package_lines

    if len(lines) > limit:
        overflow = len(lines) - limit
        lines = lines[:limit] + [f"- …and {overflow} more instruction sources"]
    return lines


CONSUMER_CONTEXT_DIRECTIVE = (
    "- Consult these when planning and executing — they are project norms, "
    "not optional reading. Root-level sources bind everywhere; a source inside "
    "a package directory binds work under that subtree only; within a source, "
    "honor its own applicability (a path-scoped rule or a trigger-scoped skill "
    "applies only per its own declaration). If an applicable "
    "instruction contradicts observed reality or Stage truth, do not silently "
    "deviate or silently obey: register the conflict as an open question "
    "(`present/state/questions/`) with your proposed correction and ask the "
    "user to fix the instruction."
)

# Before stage-init there is no question family to write into.
CONSUMER_CONTEXT_DIRECTIVE_PRE_INIT = (
    "- Consult these when planning and executing — they are project norms, "
    "not optional reading. Root-level sources bind everywhere; a source inside "
    "a package directory binds work under that subtree only; within a source, "
    "honor its own applicability (a path-scoped rule or a trigger-scoped skill "
    "applies only per its own declaration). If an applicable "
    "instruction contradicts observed reality, raise it with the user directly "
    "(Stage question records become available after `stage-init`)."
)


def consumer_context_section(workspace_root: Path, pre_init: bool = False) -> str:
    stage_root = None if pre_init else workspace_root / ".stage"
    consumer = consumer_context_lines(workspace_root, stage_root=stage_root)
    if not consumer:
        return ""
    directive = CONSUMER_CONTEXT_DIRECTIVE_PRE_INIT if pre_init else CONSUMER_CONTEXT_DIRECTIVE
    return (
        "\n### Project instructions (host-defined)\n"
        + "\n".join(consumer)
        + "\n"
        + directive
    )


SESSION_CONTEXT_RECORD_LIMIT = 3
SESSION_CONTEXT_LINE_LIMIT = 160


def id_sort_key(item_id: str) -> tuple[int, str]:
    """Numeric ID portion first: lexical order misranks variable-width IDs
    (Q-999 would outrank Q-1000)."""
    match = re.search(r"(\d+)", item_id)
    return (int(match.group(1)) if match else -1, item_id)


def bounded_record_line(
    item_id: str, title: str, suffix: str, limit: int = SESSION_CONTEXT_LINE_LIMIT
) -> str:
    """One bounded line per injected record — the budget caps size, not just
    count. Overlength truncates the TITLE while reserving the suffix: the
    `(blocks: ...)` / `(priority: ...)` linkage is the actionable part."""
    prefix = f"- {item_id} ".rstrip() + (" " if title or suffix else "")
    title = " ".join(title.split())
    room = max(8, limit - len(prefix) - len(suffix))
    if len(title) > room:
        title = title[: room - 1] + "…"
    return (prefix + title + suffix).rstrip()


def record_files(directory: Path) -> list[Path]:
    """Individual record files of an artifact family (skips index/template files)."""
    try:
        files = sorted(directory.glob("*.md"))
    except OSError:
        return []
    return [
        path
        for path in files
        if not path.name.startswith("_") and path.name.lower() != "readme.md"
    ]


def open_question_lines(stage_root: Path, limit: int = SESSION_CONTEXT_RECORD_LIMIT) -> list[str]:
    """Every record under `present/state/questions/` is open by definition —
    answered questions are promoted out of the directory. Newest first."""
    records: list[tuple[str, str, str]] = []
    for path in record_files(stage_root / "present" / "state" / "questions"):
        fields = parse_frontmatter(path)
        records.append(
            (
                fields.get("id") or path.stem,
                fields.get("title") or "",
                fields.get("work_items") or "",
            )
        )
    # Sort by the frontmatter ID (filenames may diverge from it), numerically.
    records.sort(key=lambda entry: id_sort_key(entry[0]), reverse=True)
    lines: list[str] = []
    for item_id, title, blocked in records[:limit]:
        suffix = f" (blocks: {blocked})" if blocked else ""
        lines.append(bounded_record_line(item_id, title, suffix))
    if len(records) > limit:
        lines.append(f"- …and {len(records) - limit} more in `present/state/questions/`")
    return lines


def selected_backlog_lines(stage_root: Path, limit: int = SESSION_CONTEXT_RECORD_LIMIT) -> list[str]:
    """Backlog records with `status: selected` — the queue the session should
    pick up next. Ordered by ID for determinism."""
    lines: list[str] = []
    selected: list[tuple[str, str, str]] = []
    for path in record_files(stage_root / "future" / "backlog" / "items"):
        fields = parse_frontmatter(path)
        if (fields.get("status") or "").lower() != "selected":
            continue
        item_id = fields.get("id") or path.stem
        selected.append((item_id, fields.get("title") or "", fields.get("priority") or ""))
    selected.sort(key=lambda entry: id_sort_key(entry[0]))
    for item_id, title, priority in selected[:limit]:
        suffix = f" (priority: {priority})" if priority else ""
        lines.append(bounded_record_line(item_id, title, suffix))
    if len(selected) > limit:
        lines.append(f"- …and {len(selected) - limit} more in `future/backlog/items/`")
    return lines


QUESTION_ACK_MAX_AGE_SECONDS = 24 * 60 * 60


def prune_question_ack_markers(stage_root: Path) -> None:
    """Ack markers live seconds (deny → re-ask); anything older is an abandoned session's."""
    root = stage_root / ".runtime" / "question-ack"
    now = datetime.now(timezone.utc).timestamp()
    try:
        markers = list(root.iterdir())
    except OSError:
        return
    for marker in markers:
        try:
            if now - marker.stat().st_mtime > QUESTION_ACK_MAX_AGE_SECONDS:
                marker.unlink()
        except OSError:
            pass


def handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    workspace_root = resolve_workspace_root(payload)
    prune_question_ack_markers(workspace_root / ".stage")
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": session_context(workspace_root),
        }
    }


def summarize_stage(stage_root: Path) -> str:
    items = load_work_items(stage_root)
    open_items = [item.item_id for item in items if item_is_open(item)]
    blockers = stage_completion_blockers(stage_root.parent)
    open_text = ", ".join(open_items) if open_items else "none"
    blocker_text = " / ".join(blockers) if blockers else "none"
    return (
        "# Stage Session Summary\n"
        f"- End time: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- Open work: {open_text}\n"
        f"- Completion blockers: {blocker_text}\n"
        "- Handoff condition: open work items carry current status and next actions\n"
    )


SESSION_SUMMARY_KEEP = 5


def sessions_root(stage_root: Path) -> Path:
    return stage_root / ".runtime" / "sessions"


def summaries_by_recency(stage_root: Path) -> list[Path]:
    """Session summaries newest-first; per-file stat so a concurrently pruned file is skipped."""
    stamped: list[tuple[float, Path]] = []
    try:
        candidates = list(sessions_root(stage_root).glob("*.md"))
    except OSError:
        return []
    for path in candidates:
        try:
            stamped.append((path.stat().st_mtime, path))
        except OSError:
            continue
    # Filename is a deterministic tiebreaker so coarse-resolution mtime ties
    # give a stable order instead of an arbitrary one.
    stamped.sort(key=lambda entry: (entry[0], entry[1].name), reverse=True)
    return [path for _, path in stamped]


def latest_session_summary(stage_root: Path) -> Path | None:
    migrate_legacy_runtime(stage_root)
    files = summaries_by_recency(stage_root)
    return files[0] if files else None


def latest_session_summaries(stage_root: Path) -> list[Path]:
    """The newest handoff plus any others sharing its mtime — on a coarse-
    resolution filesystem two sessions can Stop in the same tick, and injecting
    only one would silently drop a concurrent session's handoff (P30)."""
    migrate_legacy_runtime(stage_root)
    files = summaries_by_recency(stage_root)
    if not files:
        return []
    try:
        newest_mtime = files[0].stat().st_mtime
    except OSError:
        return files[:1]
    tied: list[Path] = []
    for path in files:
        try:
            if path.stat().st_mtime == newest_mtime:
                tied.append(path)
            else:
                break
        except OSError:
            continue
    return tied or files[:1]


SUMMARY_MIN_PRUNE_AGE_SECONDS = 24 * 60 * 60


def prune_session_summaries(
    stage_root: Path, keep: int = SESSION_SUMMARY_KEEP, keep_path: Path | None = None
) -> None:
    # keep_path pins the summary this Stop just wrote — mtime ties and
    # another host's clock running ahead must neither delete it nor let the
    # retained set exceed the cap, so the retained set is derived first and
    # keep_path swapped in for the oldest retained entry when necessary.
    # Additionally, a file younger than a day (by this host's clock) is never
    # pruned: under clock skew another session's just-written handoff can sort
    # below older files, and deleting it would lose a live session's handoff.
    # The cap is therefore soft for at most a day under skew.
    files = summaries_by_recency(stage_root)
    retained = files[:keep]
    if keep_path is not None and keep_path in files and keep_path not in retained:
        retained = retained[: keep - 1] + [keep_path]
    retained_set = set(retained)
    now = datetime.now(timezone.utc).timestamp()
    for stale in files:
        if stale in retained_set:
            continue
        try:
            if now - stale.stat().st_mtime < SUMMARY_MIN_PRUNE_AGE_SECONDS:
                continue
            stale.unlink()
        except OSError:
            pass


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
