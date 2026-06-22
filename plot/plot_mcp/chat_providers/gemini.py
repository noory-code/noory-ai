"""Gemini chat driver — transport is the ``agy`` (Antigravity) CLI (D-2026-06-22-A).

Google is consolidating Gemini onto Antigravity, so the in-app ``gemini``
provider drives ``agy -p`` rather than the ``gemini`` binary. ``agy`` has no
``--output-format stream-json`` mode: ``agy -p`` prints the assistant's reply
as plain text, so each stdout line is passed straight through as a ``delta``
(newline preserved). ``--dangerously-skip-permissions`` auto-approves inner
tool calls — Plot is the canvas surface that owns user trust, so the CLI
doesn't need a second confirmation layer (the role gemini's ``-y`` played).

**Stateless:** agy emits no session id on stdout, and its ``--continue``
resumes the *most-recent* conversation globally — which would cross Plot's
per-(project × scope) thread isolation (D-2026-06-13-H). So this provider does
not resume; every turn is an independent ``agy -p`` call. In-scope multi-turn
continuity is a filed follow-up (D-2026-06-22-A).
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.chat_providers.base import (
    ChatStreamEvent,
    _SubprocessChatProvider,
    _SubprocessFactory,
)


class GeminiProvider(_SubprocessChatProvider):
    """``agy -p --dangerously-skip-permissions [--model <m>] <prompt>`` driver."""

    def __init__(
        self,
        workspace_root: Path,
        *,
        cli_path: str = "agy",
        subprocess_factory: _SubprocessFactory | None = None,
    ) -> None:
        super().__init__(
            workspace_root,
            cli_path=cli_path,
            subprocess_factory=subprocess_factory,
        )

    def _build_command(self, user_message: str) -> list[str]:
        cmd = [self._cli_path, "-p", "--dangerously-skip-permissions"]
        cmd += self._model_args()
        # Stateless: no resume flag. agy's --continue is most-recent-global,
        # which would cross per-scope threads (D-2026-06-22-A); agy emits no
        # session id to resume a specific thread either. Prompt is positional.
        cmd += [user_message]
        return cmd

    def _parse_line(
        self, turn_id: str, line: bytes, accumulator: list[str]
    ) -> ChatStreamEvent | None:
        # Plain-text passthrough: agy -p has no stream-json. Each stdout line
        # (newline preserved) is one delta; the base joins the accumulator for
        # the turn_complete recap.
        text = line.decode("utf-8", errors="replace")
        if not text:
            return None
        accumulator.append(text)
        return ChatStreamEvent(type="delta", turn_id=turn_id, text=text)
