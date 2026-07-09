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
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
GIT_GLOBAL_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
WORK_OPEN_STATUSES = {"active", "review", "blocked"}
WORK_FINAL_STATUSES = {"completed", "archived", "rejected"}
VERIFICATION_DONE = {"passed", "not_required"}
RETROSPECTIVE_DONE = {"completed"}
PROMOTION_FINAL = {"approved", "promoted", "deferred", "not_applicable", "rejected"}
REDIRECT_RE = re.compile(r"(?:^|[\s])(?:>>|[0-9]?>)\s*(?P<path>[^&|;\s]+)")
PATCH_FILE_RE = re.compile(r"^\*{3} (?:Add|Update|Delete) File: (?P<path>.+)$|^\*{3} Move to: (?P<move>.+)$", re.MULTILINE)
STAGE_DELETE_RE = re.compile(
    r"("
    r"\brm\s+(?:-[A-Za-z]*[rf][A-Za-z]*|-[A-Za-z]*[fr][A-Za-z]*)\s+[^;&|]*\.stage\b"
    r"|"
    r"\bRemove-Item\b[^;&|]*\.stage\b[^;&|]*(?:-Recurse|-Force)"
    r"|"
    r"\brmdir\s+(?:/s|/S)\s+[^;&|]*\.stage\b"
    r")"
)


@dataclass(frozen=True)
class WorkItem:
    path: Path
    item_id: str
    title: str
    status: str
    verification: str
    retrospective: str
    promotion: str
    scope: tuple[str, ...]
    promotes: tuple[str, ...]
    retrospective_ref: str = ""
    kind: str = ""
    parent: str = ""


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


def normalize_path_text(path: str) -> str:
    value = path.strip().strip("'\"`")
    value = value.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def collect_explicit_paths(payload: dict[str, Any]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(path: str) -> None:
        normalized = normalize_path_text(path)
        if normalized and normalized not in seen:
            seen.add(normalized)
            found.append(normalized)

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


def relative_to_workspace(path: str | Path, workspace_root: Path) -> str:
    candidate = Path(str(path)).expanduser()
    try:
        if candidate.is_absolute():
            return normalize_path_text(str(candidate.resolve().relative_to(workspace_root)))
    except (OSError, ValueError):
        pass
    return normalize_path_text(str(candidate))


def path_targets_stage_root(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/" in normalized or normalized.endswith("/.stage")


def path_targets_stage_past(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/past/" in normalized or normalized.startswith("/.stage/past/")


def path_targets_stage_archive(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/past/work/archive/" in normalized or normalized.startswith("/.stage/past/work/archive/")


def is_stage_internal_path(path: str, workspace_root: Path) -> bool:
    relative = relative_to_workspace(path, workspace_root)
    return relative == ".stage" or relative.startswith(".stage/")


def load_governance(stage_root: Path) -> dict[str, Any]:
    settings_path = stage_root / "settings.json"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    governance = data.get("governance")
    return governance if isinstance(governance, dict) else {}


def governance_broken(stage_root: Path) -> bool:
    """True when settings.json exists but cannot be trusted (fail-closed signal)."""
    settings_path = stage_root / "settings.json"
    if not settings_path.exists():
        return False
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    if not isinstance(data, dict):
        return True
    governance = data.get("governance")
    return governance is not None and not isinstance(governance, dict)


DEFAULT_EXCLUDED_PREFIXES = (".stage", ".git", ".discuss")


def path_has_prefix(relative: str, prefix: str) -> bool:
    clean = prefix.rstrip("/")
    return bool(clean) and (relative == clean or relative.startswith(clean + "/"))


def is_source_path(path: str, workspace_root: Path) -> bool:
    relative = relative_to_workspace(path, workspace_root)
    if not relative:
        return False
    if relative.startswith("/") or re.match(r"^[A-Za-z]:", relative):
        # Absolute path outside the workspace — not governed by this project.
        return False
    if any(path_has_prefix(relative, prefix) for prefix in DEFAULT_EXCLUDED_PREFIXES):
        return False

    governance = load_governance(workspace_root / ".stage")

    # Legacy allowlist mode: explicit governed paths/extensions narrow the scope.
    raw_paths = governance.get("paths")
    if isinstance(raw_paths, list):
        for raw_prefix in raw_paths:
            if path_has_prefix(relative, normalize_path_text(str(raw_prefix))):
                return True

    suffix = Path(relative).suffix.lower()
    raw_extensions = governance.get("extensions")
    if isinstance(raw_extensions, list) and raw_extensions:
        return suffix in {str(ext).lower() for ext in raw_extensions}
    if isinstance(raw_paths, list) and raw_paths:
        # Paths-only allowlist: anything outside the listed paths is ungoverned.
        return False

    # Broad default: every workspace file is governed unless excluded.
    raw_exclude_paths = governance.get("exclude_paths")
    if isinstance(raw_exclude_paths, list):
        for raw_prefix in raw_exclude_paths:
            if path_has_prefix(relative, normalize_path_text(str(raw_prefix))):
                return False
    raw_exclude_extensions = governance.get("exclude_extensions")
    if isinstance(raw_exclude_extensions, list) and suffix in {
        str(ext).lower() for ext in raw_exclude_extensions
    }:
        return False
    return True


def command_text(payload: dict[str, Any]) -> str:
    data = tool_input(payload)
    for key in ("command", "cmd", "script"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return ""


def shell_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=os.name != "nt")
    except ValueError:
        return []


def shell_write_paths(command: str) -> list[str]:
    paths: list[str] = []

    def add(path: str) -> None:
        normalized = normalize_path_text(path)
        if normalized and normalized not in paths:
            paths.append(normalized)

    for match in REDIRECT_RE.finditer(command):
        add(match.group("path"))

    tokens = shell_tokens(command)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        command_name = Path(token).name

        if command_name in {"cp", "mv"}:
            args: list[str] = []
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor] not in {"&&", "||", ";", "|"}:
                current = tokens[cursor]
                if not current.startswith("-"):
                    args.append(current)
                cursor += 1
            if len(args) >= 2:
                add(args[-1])
            index = cursor
            continue

        if command_name == "tee":
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor] not in {"&&", "||", ";", "|"}:
                current = tokens[cursor]
                if not current.startswith("-"):
                    add(current)
                cursor += 1
            index = cursor
            continue

        if command_name == "sed":
            cursor = index + 1
            in_place = False
            args: list[str] = []
            while cursor < len(tokens) and tokens[cursor] not in {"&&", "||", ";", "|"}:
                current = tokens[cursor]
                if current == "-i" or current.startswith("-i"):
                    in_place = True
                elif not current.startswith("-"):
                    args.append(current)
                cursor += 1
            if in_place and args:
                add(args[-1])
            index = cursor
            continue

        index += 1

    return paths


def iter_git_commands(command: str) -> list[tuple[str, list[str]]]:
    tokens = shell_tokens(command)
    commands: list[tuple[str, list[str]]] = []

    for index, token in enumerate(tokens):
        if Path(token).name != "git":
            continue

        cursor = index + 1
        while cursor < len(tokens):
            current = tokens[cursor]
            if current in GIT_GLOBAL_OPTIONS_WITH_VALUE:
                cursor += 2
                continue
            if current.startswith("--git-dir=") or current.startswith("--work-tree="):
                cursor += 1
                continue
            if current.startswith("-"):
                cursor += 1
                continue
            args: list[str] = []
            arg_cursor = cursor + 1
            while arg_cursor < len(tokens) and tokens[arg_cursor] not in {"&&", "||", ";", "|"}:
                args.append(tokens[arg_cursor])
                arg_cursor += 1
            commands.append((current, args))
            break
    return commands


def git_subcommand(command: str) -> str:
    commands = iter_git_commands(command)
    return commands[0][0] if commands else ""


def command_has_git_commit(command: str) -> bool:
    return any(subcommand == "commit" for subcommand, _args in iter_git_commands(command))


def git_add_paths_from_command(command: str, workspace_root: Path) -> list[str]:
    paths: list[str] = []
    for subcommand, args in iter_git_commands(command):
        if subcommand != "add":
            continue
        explicit: list[str] = []
        for arg in args:
            if arg in {"-A", "--all", "-u", "--update"}:
                explicit.extend(changed_files(workspace_root, include_untracked=arg in {"-A", "--all"}))
            elif arg.startswith("-"):
                continue
            elif arg in {".", ":"}:
                explicit.extend(changed_files(workspace_root, include_untracked=True))
            else:
                explicit.append(arg)
        if not explicit:
            explicit.extend(changed_files(workspace_root, include_untracked=True))
        for path in explicit:
            normalized = normalize_path_text(path)
            if normalized not in paths:
                paths.append(normalized)
    return paths


def git_commit_all_requested(command: str) -> bool:
    for subcommand, args in iter_git_commands(command):
        if subcommand != "commit":
            continue
        for arg in args:
            if arg == "--all" or arg.startswith("--all="):
                return True
            if arg.startswith("-") and not arg.startswith("--") and "a" in arg[1:]:
                return True
    return False


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


def parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    fields: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def split_scope(value: str) -> tuple[str, ...]:
    if not value:
        return ()
    parts = [normalize_path_text(part) for part in re.split(r"[,;]", value)]
    clean = tuple(part for part in parts if part)
    return clean


def load_work_items(stage_root: Path) -> list[WorkItem]:
    return load_items_from(stage_root / "present" / "work" / "items")


def load_archive_work_items(stage_root: Path) -> list[WorkItem]:
    return load_items_from(stage_root / "past" / "work" / "archive" / "items")


def load_items_from(items_root: Path) -> list[WorkItem]:
    if not items_root.exists():
        return []

    items: list[WorkItem] = []
    for path in sorted(items_root.glob("*.md")):
        if path.name in {"README.md", "_template.md"}:
            continue
        fields = parse_frontmatter(path)
        item_id = fields.get("id") or path.stem
        items.append(
            WorkItem(
                path=path,
                item_id=item_id,
                title=fields.get("title") or path.stem,
                status=(fields.get("status") or "active").lower(),
                verification=(fields.get("verification") or "pending").lower(),
                retrospective=(fields.get("retrospective") or "pending").lower(),
                promotion=(fields.get("promotion") or "pending").lower(),
                scope=split_scope(fields.get("scope", "")),
                promotes=split_scope(fields.get("promotes", "")),
                retrospective_ref=(fields.get("retrospective_ref") or "").strip(),
                kind=(fields.get("kind") or "").strip().lower(),
                parent=(fields.get("parent") or "").strip(),
            )
        )
    return items


def item_is_open(item: WorkItem) -> bool:
    return item.status in WORK_OPEN_STATUSES


def item_is_completed(item: WorkItem) -> bool:
    return item.status == "completed"


def item_completion_blockers(item: WorkItem) -> list[str]:
    blockers: list[str] = []
    if item.status not in WORK_OPEN_STATUSES | WORK_FINAL_STATUSES:
        blockers.append(f"{item.item_id}: unknown status `{item.status}`")
    if item_is_completed(item):
        if item.verification not in VERIFICATION_DONE:
            blockers.append(f"{item.item_id}: verification `{item.verification}`")
        if item.retrospective not in RETROSPECTIVE_DONE:
            blockers.append(f"{item.item_id}: retrospective `{item.retrospective}`")
        if item.promotion not in PROMOTION_FINAL:
            blockers.append(f"{item.item_id}: promotion `{item.promotion}`")
    return blockers


def item_matches_path(item: WorkItem, path: str, workspace_root: Path) -> bool:
    relative = relative_to_workspace(path, workspace_root)
    for scope in item.scope:
        normalized = normalize_path_text(scope)
        if normalized == "*":
            return True
        if normalized in {"", "."}:
            continue
        if relative == normalized or relative.startswith(normalized.rstrip("/") + "/"):
            return True
    return False


def item_promotes_path(item: WorkItem, path: str, workspace_root: Path) -> bool:
    relative = relative_to_workspace(path, workspace_root)
    for promoted_path in item.promotes:
        normalized = normalize_path_text(promoted_path)
        if normalized == relative:
            return True
    return False


def archive_target_item_id(path: str, workspace_root: Path) -> str:
    relative = relative_to_workspace(path, workspace_root)
    prefix = ".stage/past/work/archive/items/"
    if not relative.startswith(prefix):
        return ""
    name = Path(relative).name
    if name.lower().endswith(".md"):
        return name[:-3]
    return ""


def archive_target_retro_id(path: str, workspace_root: Path) -> str:
    relative = relative_to_workspace(path, workspace_root)
    prefix = ".stage/past/work/archive/retrospectives/"
    if not relative.startswith(prefix):
        return ""
    name = Path(relative).name
    if name.lower().endswith(".md"):
        return name[:-3]
    return ""


def retrospective_ref_id(item: WorkItem) -> str:
    ref = normalize_path_text(item.retrospective_ref)
    if not ref:
        return ""
    name = Path(ref).name
    return name[:-3] if name.lower().endswith(".md") else name


def fallback_index_blockers(stage_root: Path) -> list[str]:
    active = parse_index_rows(stage_root / "present" / "work" / "active.md")
    review = parse_index_rows(stage_root / "present" / "work" / "review.md")
    blockers: list[str] = []
    if active:
        blockers.append("Work item SSOT is missing: move active.md rows into items/*.md")
    if review:
        blockers.append("Review item SSOT is missing: move review.md rows into items/*.md or retrospectives/*.md")
    return blockers


def parse_index_rows(path: Path) -> list[list[str]]:
    if not path.exists():
        return []
    rows: list[list[str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and not all(re.fullmatch(r"\s*:?-{2,}:?\s*", cell) for cell in cells):
            rows.append(cells)
    return rows[1:] if len(rows) > 1 else []


def stage_completion_blockers(workspace_root: Path) -> list[str]:
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return []

    items = load_work_items(stage_root)
    if not items:
        return fallback_index_blockers(stage_root)

    blockers: list[str] = []
    for item in items:
        blockers.extend(item_completion_blockers(item))
    return blockers


def open_items_for_paths(workspace_root: Path, paths: list[str]) -> list[WorkItem]:
    stage_root = workspace_root / ".stage"
    items = [item for item in load_work_items(stage_root) if item_is_open(item)]
    if not paths:
        return items
    return [item for item in items if any(item_matches_path(item, path, workspace_root) for path in paths)]


def staged_files(workspace_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace_root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files(workspace_root: Path, *, include_untracked: bool = False) -> list[str]:
    commands = [
        ["git", "-C", str(workspace_root), "diff", "--name-only", "--diff-filter=ACMR"],
        ["git", "-C", str(workspace_root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
    ]
    if include_untracked:
        commands.append(["git", "-C", str(workspace_root), "ls-files", "--others", "--exclude-standard"])

    paths: list[str] = []
    seen: set[str] = set()
    for command in commands:
        try:
            result = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
            )
        except OSError:
            continue
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            path = normalize_path_text(line.strip())
            if path and path not in seen:
                seen.add(path)
                paths.append(path)
    return paths


def source_registration_blocker(workspace_root: Path, paths: list[str]) -> str:
    source_paths = [path for path in paths if is_source_path(path, workspace_root)]
    if not source_paths:
        return ""
    if open_items_for_paths(workspace_root, source_paths):
        return ""
    return (
        "Stage registration gate violation: before modifying governed files, register an active "
        "work item with a matching scope in `.stage/present/work/items/`. "
        "Targets: " + ", ".join(source_paths[:5])
    )


def commit_blocker(workspace_root: Path, paths: list[str]) -> str:
    source_paths = [path for path in paths if is_source_path(path, workspace_root)]
    if not source_paths:
        return ""

    items = load_work_items(workspace_root / ".stage")
    missing: list[str] = []
    blockers: list[str] = []
    for path in source_paths:
        matched = [item for item in items if item_matches_path(item, path, workspace_root)]
        if not matched:
            missing.append(path)
            continue
        for item in matched:
            if item_is_completed(item):
                blockers.extend(item_completion_blockers(item))

    if missing:
        return (
            "Stage commit gate violation: committed governed files are not registered to a work item. "
            "Targets: " + ", ".join(missing[:5])
        )
    if blockers:
        return (
            "Stage completion gate violation: close the completed item's verification, retrospective, "
            "and promotion decision first. " + " / ".join(blockers)
        )
    return ""


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
        target = sessions_root(stage_root) / "legacy.md"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                legacy_summary.unlink()
            else:
                legacy_summary.replace(target)
        except OSError:
            pass


def write_intent_file(stage_root: Path, intent: dict[str, Any], path_value: str) -> Path | None:
    """Persist a single-path intent; the slot is (work item, canonical path).

    The path is canonicalized to workspace-relative before slotting and
    storage, so replanting the same target as absolute vs relative stays
    idempotent. The filename embeds the basename plus a digest of the full
    path — bounded regardless of target depth. A slot collision with a
    DIFFERENT logical (item, path) pair falls through to a numbered suffix
    instead of overwriting someone else's pending authorization.
    """
    root = intents_root(stage_root)
    try:
        workspace_root = stage_root.parent.resolve()
    except OSError:
        workspace_root = stage_root.parent
    normalized = relative_to_workspace(path_value, workspace_root)
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
                    and [relative_to_workspace(p, workspace_root) for p in intent_paths(existing)]
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
    write consumes state by atomic unlink, never by rewriting a shared file."""
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
    raw = intent.get("paths")
    if isinstance(raw, list):
        return [normalize_path_text(str(item)) for item in raw if str(item).strip()]
    raw_path = intent.get("path")
    if isinstance(raw_path, str) and raw_path.strip():
        return [normalize_path_text(raw_path)]
    return []


def promotion_blocker(workspace_root: Path, target_paths: list[str]) -> str:
    """Per-path intents make consumption an atomic unlink.

    Each pending intent covers exactly one path (the loader normalizes
    multi-path files), so authorizing a write never rewrites another intent's
    state — the read-modify-write race that could resurrect an already
    consumed authorization cannot occur.
    """
    stage_root = workspace_root / ".stage"
    intents = load_promotion_intents(stage_root)
    if not intents:
        return (
            "Stage promotion gate violation: modifying `.stage/past/` requires an out-of-band "
            "promotion intent. Run `stage-retrospective`, then create one with "
            "`scripts/promote_intent.py` (writes `.stage/.runtime/intents/<work-item>--<path>.json`)."
        )

    requested = {relative_to_workspace(path, workspace_root) for path in target_paths}
    by_path: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for intent_file, intent in intents:
        for declared in intent_paths(intent):
            by_path.setdefault(relative_to_workspace(declared, workspace_root), []).append(
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


def frontmatter_field_from_text(text: str, field: str) -> str:
    # [ \t]* (not \s*): \s crosses the newline after an empty `field:` line and
    # would capture the NEXT line as the value (e.g. empty `parent:` followed by
    # `source:` read back as parent="source:" — a false hierarchy deny).
    match = re.search(rf"^{re.escape(field)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def read_existing_text(workspace_root: Path, relative: str) -> str:
    try:
        return (workspace_root / relative).read_text(encoding="utf-8")
    except OSError:
        return ""


def projected_file_text(existing: str, name: str, data: dict[str, Any]) -> str:
    """Best-effort post-edit file text for a Write/Edit/MultiEdit style tool call."""
    if name in {"Write", "create_file"}:
        content = data.get("content")
        return content if isinstance(content, str) else existing

    replacements: list[tuple[str, str]] = []
    edits = data.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                replacements.append(
                    (str(edit.get("old_string") or ""), str(edit.get("new_string") or ""))
                )
    for old_key, new_key in (("old_string", "new_string"), ("old_str", "new_str"), ("oldText", "newText")):
        new_value = data.get(new_key)
        if isinstance(new_value, str):
            old_value = data.get(old_key)
            replacements.append((old_value if isinstance(old_value, str) else "", new_value))

    text = existing
    for old, new in replacements:
        if old and old in text:
            text = text.replace(old, new)
        elif new:
            # Prepend immediately (fragment first so its field values win over stale
            # existing lines) so later edits apply sequentially to this fragment too.
            text = new + ("\n" + text if text else "")
    return text


def projected_patch_text(patch_text: str, target_relative: str, workspace_root: Path) -> str:
    """Best-effort post-patch file text for one file inside an apply_patch payload.

    A section counts toward the target when its File header matches, or when its
    `Move to:` destination matches — a moved file carries the source's existing text
    plus the section's hunks into the new path.
    """
    added: list[str] = []
    removed: set[str] = set()
    collecting = False
    base_relative = target_relative
    current_source = ""
    for line in patch_text.splitlines():
        if line.startswith("*** "):
            header = line[4:]
            matched_header = False
            for prefix in ("Add File: ", "Update File: ", "Delete File: "):
                if header.startswith(prefix):
                    current_source = relative_to_workspace(
                        normalize_path_text(header[len(prefix):]), workspace_root
                    )
                    collecting = current_source == target_relative
                    if collecting:
                        base_relative = current_source
                    matched_header = True
                    break
            if not matched_header:
                if header.startswith("Move to: "):
                    move_target = relative_to_workspace(
                        normalize_path_text(header[len("Move to: "):]), workspace_root
                    )
                    if move_target == target_relative and current_source:
                        collecting = True
                        base_relative = current_source
                elif header.strip() == "End Patch":
                    collecting = False
            continue
        if not collecting:
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.add(line[1:])
    existing = read_existing_text(workspace_root, base_relative)
    kept = [line for line in existing.splitlines() if line not in removed]
    return "\n".join(added + kept)


def hierarchy_item_targets(workspace_root: Path, payload: dict[str, Any], name: str) -> list[tuple[str, str]]:
    """(relative_path, projected_post_edit_text) for every targeted work item file."""
    data = tool_input(payload)
    prefix = ".stage/present/work/items/"
    targets: list[tuple[str, str]] = []

    if name == "apply_patch":
        for text_value in iter_strings(data):
            for match in PATCH_FILE_RE.finditer(text_value):
                raw = match.group("path") or match.group("move") or ""
                relative = relative_to_workspace(normalize_path_text(raw), workspace_root)
                if relative.startswith(prefix):
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
    relative = relative_to_workspace(target, workspace_root)
    if not relative.startswith(prefix):
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

    for relative, projected in targets:
        parent_id = frontmatter_field_from_text(projected, "parent")
        if not parent_id:
            continue

        target_stem = Path(relative).stem
        if parent_id == target_stem:
            return f"Stage hierarchy gate violation: a work item cannot be its own parent: {parent_id}"

        matched = [item for item in items if item.item_id == parent_id and item.path.stem != target_stem]
        if not matched:
            return f"Stage hierarchy gate violation: parent work item not found: {parent_id}"

        child_status = (frontmatter_field_from_text(projected, "status") or "active").lower()
        if matched[0].status in WORK_FINAL_STATUSES and child_status in WORK_OPEN_STATUSES:
            return (
                "Stage hierarchy gate violation: cannot open a child under a finalized parent "
                f"({matched[0].status}): {parent_id}"
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
            normalized = normalize_path_text(path)
            if normalized and normalized not in explicit_paths:
                explicit_paths.append(normalized)
    if name == "apply_patch":
        for text_value in iter_strings(tool_input(payload)):
            for match in PATCH_FILE_RE.finditer(text_value):
                normalized = normalize_path_text(match.group("path") or match.group("move") or "")
                if normalized and normalized not in explicit_paths:
                    explicit_paths.append(normalized)
    workspace_root = resolve_workspace_root(payload)
    stage_root = workspace_root / ".stage"

    if command and STAGE_DELETE_RE.search(command):
        return deny(
            "Stage rule violation: deleting `.stage` entirely is blocked. "
            "Modify only the specific files you need so official artifacts, current work status, "
            "and plans are not lost."
        )

    for path in explicit_paths:
        if path_targets_stage_root(path) and normalize_path_text(path).lower().endswith(OS_SCRIPT_SUFFIXES):
            return deny(
                "Stage portability rule violation: OS-specific executable scripts are not allowed "
                "inside `.stage`. Use the Python standard library or Markdown artifacts so behavior "
                "stays identical on Codex, Claude, Windows, Linux, and macOS."
            )

    past_gate_paths = explicit_paths if name in WRITE_TOOLS else shell_write_targets
    target_past_paths = [path for path in past_gate_paths if path_targets_stage_past(path)]
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
        blocker = source_registration_blocker(workspace_root, explicit_paths)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command:
        blocker = source_registration_blocker(workspace_root, shell_write_targets)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command and command_has_git_commit(command):
        files = staged_files(workspace_root)
        files.extend(path for path in git_add_paths_from_command(command, workspace_root) if path not in files)
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
        return (
            "## Stage\n"
            "This project has no `.stage/`. If the Stage harness applies to this project, "
            "create the artifact structure first with `stage-init`."
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
        ("Most recent session", latest_session_summary(stage_root)),
    ]
    for title, path in snippets:
        body = read_if_exists(path) if path is not None else ""
        if body:
            parts.append(f"\n### {title}\n{body}")

    return "\n".join(parts)


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
    stamped.sort(key=lambda entry: entry[0], reverse=True)
    return [path for _, path in stamped]


def latest_session_summary(stage_root: Path) -> Path | None:
    migrate_legacy_runtime(stage_root)
    files = summaries_by_recency(stage_root)
    return files[0] if files else None


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
