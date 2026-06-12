"""Codex CLI driver (``codex exec --json``).

Codex emits JSONL events with ``thread.started`` / ``turn.started`` /
``item.completed`` / ``turn.completed``. The first event of the first
turn carries ``thread_id`` — we capture it so later turns can
``codex exec resume <id>``. ``--skip-git-repo-check`` keeps Codex from
refusing to run when the user opened Plot on a folder that isn't a git
repo (yet). The working directory is set via ``cwd=`` on the spawn, not
Codex's ``-C`` flag, so every provider shares one root-resolution path.
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.chat_providers.base import (
    ChatStreamEvent,
    _decode_jsonl,
    _SubprocessChatProvider,
    _SubprocessFactory,
)


class CodexProvider(_SubprocessChatProvider):
    """``codex exec --json`` driver with thread-id continuity."""

    def __init__(
        self,
        workspace_root: Path,
        *,
        cli_path: str = "codex",
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        super().__init__(
            workspace_root,
            cli_path=cli_path,
            subprocess_factory=subprocess_factory,
        )

    def _build_command(self, user_message: str) -> list[str]:
        # Until we've captured a thread_id, every turn starts a fresh session
        # — this also covers the "first turn never emitted thread.started"
        # crash-recovery path so we don't try to ``resume None``.
        if self._first_turn or self._session_id is None:
            return [
                self._cli_path,
                "exec",
                "--json",
                "--skip-git-repo-check",
                user_message,
            ]
        return [
            self._cli_path,
            "exec",
            "resume",
            self._session_id,
            "--json",
            "--skip-git-repo-check",
            user_message,
        ]

    def _parse_line(
        self, turn_id: str, line: bytes, accumulator: list[str]
    ) -> ChatStreamEvent | None:
        obj = _decode_jsonl(line)
        if obj is None:
            return None
        event_type = obj.get("type")
        if event_type == "thread.started":
            tid = obj.get("thread_id")
            if isinstance(tid, str) and tid:
                self._session_id = tid
            return None
        if event_type == "item.completed":
            item = obj.get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message":
                text = item.get("text")
                if isinstance(text, str) and text:
                    accumulator.append(text)
                    return ChatStreamEvent(
                        type="delta", turn_id=turn_id, text=text
                    )
        return None
