"""Chat Layer-3 framing delivered as an authoritative system prompt (Lever 2).

The per-canvas framing used to be glued into the *user message*, where the
model reads it as "part of the conversation" rather than a binding instruction
— so it drifted and the agent invented project facts (context starvation, see
``docs/idea/chat/00-problem.md``). Lever 2 moves the framing into a real system
prompt and adds a constant hallucination guard ("ground every claim in the
provided context / read the canvas, never invent"). Providers map it per CLI:
claude has a native ``--append-system-prompt`` flag; codex (whose ``exec`` takes
the prompt as a positional arg with no system-prompt flag) falls back to
prepending it to the message.
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.chat_context import (
    HALLUCINATION_GUARD,
    build_framing_preamble,
    build_system_prompt,
)
from plot_mcp.chat_providers.claude_code import ClaudeCodeProvider
from plot_mcp.chat_providers.codex import CodexProvider

# --- build_system_prompt (chat_context SSOT) -------------------------------


def test_system_prompt_includes_guard_and_framing_for_a_canvas() -> None:
    sp = build_system_prompt("foundation")
    assert HALLUCINATION_GUARD in sp
    assert build_framing_preamble("foundation") in sp


def test_system_prompt_is_guard_only_for_project_scope() -> None:
    # ``project`` is cross-canvas — no per-canvas framing — but the guard
    # (read, don't invent) is universal and must still be present.
    sp = build_system_prompt("project")
    assert HALLUCINATION_GUARD in sp
    assert build_framing_preamble("project") == ""


def test_system_prompt_uses_base_scope_for_parametric_feature() -> None:
    assert build_framing_preamble("feature:x") in build_system_prompt("feature:x")


# --- claude: native --append-system-prompt flag ----------------------------


def test_claude_command_carries_system_prompt_as_flag(tmp_path: Path) -> None:
    p = ClaudeCodeProvider(workspace_root=tmp_path)
    p.set_system_prompt("BE GROUNDED")
    cmd = p._build_command("fix this")
    assert "--append-system-prompt" in cmd
    assert cmd[cmd.index("--append-system-prompt") + 1] == "BE GROUNDED"
    # The system text must NOT leak into the user message (the last arg).
    assert cmd[-1] == "fix this"


def test_claude_command_omits_system_prompt_flag_when_unset(tmp_path: Path) -> None:
    p = ClaudeCodeProvider(workspace_root=tmp_path)
    assert "--append-system-prompt" not in p._build_command("hi")


# --- codex: no system-prompt flag → prepend to the message -----------------


def test_codex_prepends_system_prompt_to_message(tmp_path: Path) -> None:
    p = CodexProvider(workspace_root=tmp_path)
    p.set_system_prompt("BE GROUNDED")
    cmd = p._build_command("fix this")
    # codex exec takes the prompt as the trailing positional arg; the system
    # text rides in front of the user's message.
    assert cmd[-1].startswith("BE GROUNDED")
    assert "fix this" in cmd[-1]
    # No claude-style flag.
    assert "--append-system-prompt" not in cmd


def test_codex_message_unchanged_when_system_prompt_unset(tmp_path: Path) -> None:
    p = CodexProvider(workspace_root=tmp_path)
    assert p._build_command("hi")[-1] == "hi"
