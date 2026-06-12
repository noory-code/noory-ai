"""Gemini CLI driver (``gemini -y --output-format stream-json``).

The ``init`` event carries ``session_id`` which we capture, so later
turns can pass ``--resume <id>``. ``-y`` (YOLO mode) skips per-action
approvals — Plot is the canvas surface that owns user trust, so the
inner tool calls don't need a second confirmation layer. (Mirrors how
every interactive CLI behaves when run inside an IDE plugin.)
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.chat_providers.base import (
    ChatStreamEvent,
    _decode_jsonl,
    _SubprocessChatProvider,
    _SubprocessFactory,
)


class GeminiProvider(_SubprocessChatProvider):
    """``gemini -y --output-format stream-json -p <prompt>`` driver."""

    def __init__(
        self,
        workspace_root: Path,
        *,
        cli_path: str = "gemini",
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        super().__init__(
            workspace_root,
            cli_path=cli_path,
            subprocess_factory=subprocess_factory,
        )

    def _build_command(self, user_message: str) -> list[str]:
        cmd = [self._cli_path, "-y", "--output-format", "stream-json"]
        if not self._first_turn and self._session_id is not None:
            cmd += ["--resume", self._session_id]
        cmd += ["-p", user_message]
        return cmd

    def _parse_line(
        self, turn_id: str, line: bytes, accumulator: list[str]
    ) -> ChatStreamEvent | None:
        obj = _decode_jsonl(line)
        if obj is None:
            return None
        event_type = obj.get("type")
        if event_type == "init":
            sid = obj.get("session_id")
            if isinstance(sid, str) and sid:
                self._session_id = sid
            return None
        if event_type == "message" and obj.get("role") == "assistant":
            content = obj.get("content")
            if isinstance(content, str) and content:
                accumulator.append(content)
                return ChatStreamEvent(
                    type="delta", turn_id=turn_id, text=content
                )
        return None
