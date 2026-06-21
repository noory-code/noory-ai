"""Claude Code CLI driver (``claude --print``).

The first turn passes ``--session-id <uuid>`` so Plot mints the
conversation id; every later turn passes ``--resume <uuid>`` so the CLI
loads its persisted transcript and the conversation continues naturally.
``--include-partial-messages`` flips the JSONL stream into incremental
``content_block_delta`` events so the dock shows text as it's produced.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from plot_mcp.chat_providers.base import (
    ChatStreamEvent,
    _decode_jsonl,
    _SubprocessChatProvider,
    _SubprocessFactory,
)


class ClaudeCodeProvider(_SubprocessChatProvider):
    """One subprocess per turn, conversation continuity via ``--session-id``."""

    def __init__(
        self,
        workspace_root: Path,
        *,
        session_id: str | None = None,
        cli_path: str = "claude",
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        super().__init__(
            workspace_root,
            cli_path=cli_path,
            subprocess_factory=subprocess_factory,
        )
        # Claude is the only CLI where Plot mints the session id; the others
        # report theirs through the first event of the first turn.
        self._session_id = session_id or str(uuid4())

    def _build_command(self, user_message: str) -> list[str]:
        cmd = [
            self._cli_path,
            "--print",
            "--output-format",
            "stream-json",
            "--include-partial-messages",
            "--verbose",  # stream-json requires verbose mode
            # D-2026-06-21-C — auto-allow the user's own Plot MCP tools. Headless
            # ``-p`` can't show a permission prompt, so without this the agent
            # dead-ends ("press Allow" with nothing to press). Scoped to
            # ``mcp__plot__*`` ONLY — Bash / Write / filesystem keep default
            # behaviour, so the in-app agent can't silently touch anything
            # outside the user's .noory/plot data (which is git-recoverable and
            # surfaced on the canvas per build-through-discussion).
            "--allowedTools",
            "mcp__plot__*",
            # D-2026-06-21-I — ground the in-app agent ONLY in the workspace:
            # load only workspace-local settings (no parent / global CLAUDE.md
            # auto-discovery, no user-scope config) and keep the memory paths /
            # cwd / env out of the system prompt. OAuth subscription auth is
            # untouched (this is NOT --bare, which would force an API key). The
            # ``plot`` MCP still loads (it lives in ~/.claude.json, read
            # independently of --setting-sources). Auto-memory is killed via the
            # ``CLAUDE_CODE_DISABLE_AUTO_MEMORY`` env (see ``_spawn_env``).
            "--setting-sources",
            "local",
            "--exclude-dynamic-system-prompt-sections",
            *self._model_args(),
        ]
        if self._first_turn:
            assert self._session_id is not None  # ctor guarantees this
            cmd += ["--session-id", self._session_id]
        else:
            assert self._session_id is not None
            cmd += ["--resume", self._session_id]
        cmd.append(user_message)
        return cmd

    def _spawn_env(self) -> dict[str, str] | None:
        # D-2026-06-21-I — disable Claude Code auto-memory for the in-app agent
        # so it can't pull in the user's saved memories from outside the
        # workspace. Merge over the inherited env (None would REPLACE it).
        return {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}

    def _parse_line(
        self, turn_id: str, line: bytes, accumulator: list[str]
    ) -> ChatStreamEvent | None:
        return _parse_claude_line(turn_id, line, accumulator)


def _parse_claude_line(
    turn_id: str, line: bytes, accumulator: list[str]
) -> ChatStreamEvent | None:
    """Decode one Claude Code ``stream-json`` line into a ``delta`` event.

    Streaming text comes from the **partial** frames only (D-2026-06-21-B):
      ``{"type":"stream_event", "event":{"type":"content_block_delta",
         "delta":{"type":"text_delta", "text":"..."}}}``

    With ``--include-partial-messages`` the CLI ALSO emits a final full
    ``assistant`` recap message carrying the same complete block text. Counting
    both doubles the reply ("살펴볼게요.살펴볼게요."), so the recap is ignored
    here — the partials are the single source of the streamed text.
    """
    obj = _decode_jsonl(line)
    if obj is None:
        return None
    # The first line is a ``system`` / ``init`` frame naming the model the CLI
    # loaded — surface it as a ``meta`` event so the viewer can show the real
    # default (D-2026-06-21-Z). It carries no reply text, so report it before
    # the text path.
    model = _extract_anthropic_model(obj)
    if model:
        return ChatStreamEvent(type="meta", turn_id=turn_id, model=model)
    text = _extract_anthropic_text(obj)
    if not text:
        return None
    accumulator.append(text)
    return ChatStreamEvent(type="delta", turn_id=turn_id, text=text)


def _extract_anthropic_model(obj: dict[str, Any]) -> str | None:
    """The model id from the ``system`` / ``init`` frame, or ``None``.

    Claude Code's first stream-json line is
    ``{"type":"system","subtype":"init",...,"model":"claude-..."}`` (D-2026-06-21-Z).
    """
    if obj.get("type") == "system" and obj.get("subtype") == "init":
        model = obj.get("model")
        if isinstance(model, str) and model:
            return model
    return None


def _extract_anthropic_text(obj: dict[str, Any]) -> str:
    """Streamed text from a partial ``content_block_delta`` frame, or ``""``.

    The full ``assistant`` recap message is intentionally NOT a source — the
    partials already carry the complete text, and counting the recap doubles
    the reply (D-2026-06-21-B)."""
    event = obj.get("event")
    if isinstance(event, dict):
        delta = event.get("delta")
        if isinstance(delta, dict) and delta.get("type") == "text_delta":
            t = delta.get("text")
            if isinstance(t, str):
                return t
    return ""
