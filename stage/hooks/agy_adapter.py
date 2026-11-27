#!/usr/bin/env python3
"""Antigravity lifecycle-hook adapter for Stage guards.

Translates Antigravity stdin/stdout JSON payloads into Stage's canonical
`stage_guard` hook contract so Stage rules stay in one place.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

import stage_guard  # noqa: E402

_EVENT_ALIASES = {
    "session-start": "SessionStart",
    "sessionstart": "SessionStart",
    "pre-invocation": "PreInvocation",
    "preinvocation": "PreInvocation",
    "pre-tool-use": "PreToolUse",
    "pretooluse": "PreToolUse",
    "post-tool-use": "PostToolUse",
    "posttooluse": "PostToolUse",
    "stop": "Stop",
}

_WRITE_TO_FILE_TOOLS = {"write_to_file", "write_file"}
_EDIT_FILE_TOOLS = {
    "edit_file",
    "replace_file_content",
    "multi_replace_file_content",
    "sed_file",
}


def _first_str(mapping: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _translate_tool(raw_name: str, raw_args: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    tool_input = dict(raw_args)
    if raw_name in _WRITE_TO_FILE_TOOLS:
        target = _first_str(raw_args, "TargetFile", "Path", "file_path", "path")
        if target and "file_path" not in tool_input:
            tool_input["file_path"] = target
        return "Write", tool_input
    if raw_name in _EDIT_FILE_TOOLS:
        target = _first_str(raw_args, "TargetFile", "Path", "file_path", "path")
        if target and "file_path" not in tool_input:
            tool_input["file_path"] = target
        return "Edit", tool_input
    if raw_name == "notebook_edit":
        target = _first_str(raw_args, "NotebookPath", "TargetFile", "Path", "file_path", "path")
        if target and "file_path" not in tool_input:
            tool_input["file_path"] = target
        return "NotebookEdit", tool_input
    if raw_name == "run_command":
        cmd = _first_str(raw_args, "CommandLine", "command", "cmd")
        if cmd and "command" not in tool_input:
            tool_input["command"] = cmd
        return "Bash", tool_input
    if raw_name == "ask_question":
        return "AskUserQuestion", tool_input

    target = _first_str(raw_args, "Path", "TargetFile")
    if target and "file_path" not in tool_input:
        tool_input["file_path"] = target
    return raw_name, tool_input


def translate_payload(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Convert an Antigravity hook stdin JSON object into Stage's canonical payload."""
    normalized = event.strip().replace("_", "-").lower()
    raw_event = str(payload.get("hookEventName") or payload.get("hook_event_name") or "")
    canonical_event = _EVENT_ALIASES.get(normalized) or raw_event or event

    translated: dict[str, Any] = {
        "hook_event_name": canonical_event,
        "session_id": str(payload.get("conversationId") or payload.get("session_id") or ""),
    }

    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        workspace_paths = payload.get("workspacePaths")
        if isinstance(workspace_paths, list):
            cwd = next((item for item in workspace_paths if isinstance(item, str) and item), "")
    if isinstance(cwd, str) and cwd:
        translated["cwd"] = cwd

    tool_call = payload.get("toolCall")
    if isinstance(tool_call, dict):
        call_id = str(tool_call.get("id") or "")
        if call_id:
            translated["tool_use_id"] = call_id
        raw_name = str(tool_call.get("name") or "")
        raw_args = tool_call.get("args")
        args_dict = dict(raw_args) if isinstance(raw_args, dict) else {}
        mapped_name, mapped_input = _translate_tool(raw_name, args_dict)
        translated["tool_name"] = mapped_name
        translated["tool_input"] = mapped_input
    else:
        if "tool_name" in payload or "toolName" in payload:
            translated["tool_name"] = stage_guard.tool_name(payload)
        if "tool_input" in payload or "toolInput" in payload:
            translated["tool_input"] = stage_guard.tool_input(payload)
        if "tool_use_id" in payload:
            translated["tool_use_id"] = payload["tool_use_id"]

    error = payload.get("error")
    if isinstance(error, str) and error:
        translated["tool_response"] = {"error": error, "is_error": True}

    return translated


def _inject_message(text: str) -> dict[str, Any]:
    if not text:
        return {}
    return {"injectSteps": [{"systemMessage": {"systemMessage": text}}]}


def handle_agy_event(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Run the matching Stage hook handler and return Antigravity hook JSON."""
    normalized = (
        event.strip() or str(payload.get("hookEventName") or payload.get("hook_event_name") or "")
    ).strip().replace("_", "-").lower()
    translated = translate_payload(normalized, payload)

    if normalized in {"session-start", "sessionstart"}:
        result = stage_guard.handle_event("session-start", translated)
        context = str((result.get("hookSpecificOutput") or {}).get("additionalContext") or "")
        return _inject_message(context)

    if normalized in {"pre-invocation", "preinvocation"}:
        workspace_root = stage_guard.resolve_workspace_root(translated)
        context, _ = stage_guard.purpose_tool_context(workspace_root, translated)
        return _inject_message(context)

    if normalized in {"pre-tool-use", "pretooluse"}:
        result = stage_guard.handle_event("pre-tool-use", translated)
        hook_output = result.get("hookSpecificOutput")
        if isinstance(hook_output, dict) and hook_output.get("permissionDecision") == "deny":
            reason = str(
                hook_output.get("permissionDecisionReason")
                or result.get("systemMessage")
                or "Blocked by Stage guard."
            )
            extra = str(hook_output.get("additionalContext") or "")
            if extra and extra not in reason:
                reason = f"{reason}\n\n{extra}"
            return {"decision": "deny", "reason": reason}
        # Antigravity treats `{}` on PreToolUse as a denial, so an allowed call
        # must emit an explicit allow decision.
        return {"decision": "allow"}

    if normalized in {"post-tool-use", "posttooluse"}:
        stage_guard.handle_event("post-tool-use", translated)
        return {}

    if normalized == "stop":
        stage_guard.handle_event("stop", translated)
        return {}

    return {}


def main(argv: list[str] | None = None) -> int:
    stage_guard.configure_stdio()
    args = list(sys.argv[1:] if argv is None else argv)
    event = args[0] if args else ""
    normalized = event.strip().replace("_", "-").lower()
    try:
        payload = stage_guard.load_payload()
        output = handle_agy_event(event, payload)
    except Exception as exc:  # noqa: BLE001 - fail closed on PreToolUse, never double-run fallback
        output = (
            {"decision": "deny", "reason": f"Stage guard adapter error: {exc}"}
            if normalized in {"pre-tool-use", "pretooluse"}
            else {}
        )
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
