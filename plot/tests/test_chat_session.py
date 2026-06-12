"""R7 chat — subprocess driver tests (D-2026-06-12-D, Phase C step C1).

Pins three responsibilities of ``plot_mcp.chat_session``:

  1. ``_parse_stream_line`` decodes Claude Code's ``stream-json`` output into
     ``ChatStreamEvent`` instances, dropping system / tool_use frames and
     accumulating partial text deltas.
  2. ``ChatSessionRegistry`` returns the same provider for one workspace path
     across calls (so two turns in a row keep the CLI's ``--session-id``)
     and surrenders it on ``reset``.
  3. ``ClaudeCodeProvider.stream_turn`` shells out with the documented flags,
     yields ``turn_start`` → ``delta`` × N → ``turn_complete`` on success,
     and ``error`` on non-zero exit. The subprocess is faked here — real CLI
     invocation belongs to the end-to-end smoke (Phase C step C7), not unit
     tests that have to stay hermetic on CI.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from plot_mcp.chat_session import (
    ChatSessionRegistry,
    ChatStreamEvent,
    ClaudeCodeProvider,
    CodexProvider,
    GeminiProvider,
    _parse_stream_line,
)

# ---------------------------------------------------------------------------
# _parse_stream_line
# ---------------------------------------------------------------------------


def test_parse_stream_line_extracts_text_from_assistant_message() -> None:
    accumulator: list[str] = []
    line = json.dumps(
        {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "Hello, world!"}]},
        }
    ).encode()
    event = _parse_stream_line("turn-1", line, accumulator)
    assert event is not None
    assert event.type == "delta"
    assert event.text == "Hello, world!"
    assert accumulator == ["Hello, world!"]


def test_parse_stream_line_extracts_text_from_content_block_delta() -> None:
    accumulator: list[str] = []
    line = json.dumps(
        {
            "type": "stream_event",
            "event": {
                "type": "content_block_delta",
                "delta": {"type": "text_delta", "text": "chunk"},
            },
        }
    ).encode()
    event = _parse_stream_line("turn-1", line, accumulator)
    assert event is not None
    assert event.type == "delta"
    assert event.text == "chunk"
    assert accumulator == ["chunk"]


def test_parse_stream_line_drops_system_init() -> None:
    accumulator: list[str] = []
    line = json.dumps(
        {"type": "system", "subtype": "init", "session_id": "abc"}
    ).encode()
    assert _parse_stream_line("turn-1", line, accumulator) is None
    assert accumulator == []


def test_parse_stream_line_drops_invalid_json() -> None:
    accumulator: list[str] = []
    assert _parse_stream_line("turn-1", b"not json at all", accumulator) is None
    assert _parse_stream_line("turn-1", b"", accumulator) is None
    assert _parse_stream_line("turn-1", b"   ", accumulator) is None
    assert accumulator == []


def test_parse_stream_line_drops_tool_use_message() -> None:
    accumulator: list[str] = []
    line = json.dumps(
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"cmd": "ls"}}
                ]
            },
        }
    ).encode()
    # Tool-use frames carry no text → no delta should land. Future work may
    # surface tool calls in the panel; for v0.64.0 we keep the surface
    # text-only.
    assert _parse_stream_line("turn-1", line, accumulator) is None
    assert accumulator == []


# ---------------------------------------------------------------------------
# ChatSessionRegistry
# ---------------------------------------------------------------------------


class _FakeProvider:
    """Stand-in for ClaudeCodeProvider — counts how often it was constructed."""

    def __init__(self, workspace_root: Path, provider_name: str = "claude-code") -> None:
        self.workspace_root = workspace_root
        self.provider_name = provider_name


def test_registry_returns_same_provider_for_same_workspace_and_name(
    tmp_path: Path,
) -> None:
    created: list[tuple[Path, str]] = []

    def factory(root: Path, name: str) -> Any:
        created.append((root, name))
        return _FakeProvider(root, name)

    registry = ChatSessionRegistry(factory=factory)
    ws = tmp_path / "ws"
    ws.mkdir()

    first = registry.get_or_create(ws, "claude-code")
    second = registry.get_or_create(ws, "claude-code")
    assert first is second
    assert created == [(ws.resolve(), "claude-code")]


def test_registry_keys_by_resolved_path(tmp_path: Path) -> None:
    """Two distinct strings that point at the same directory share a session."""
    created: list[tuple[Path, str]] = []

    def factory(root: Path, name: str) -> Any:
        created.append((root, name))
        return _FakeProvider(root, name)

    registry = ChatSessionRegistry(factory=factory)
    ws = tmp_path / "ws"
    ws.mkdir()
    alias = tmp_path / "ws" / "."  # same dir, different string form

    first = registry.get_or_create(ws, "claude-code")
    second = registry.get_or_create(alias, "claude-code")
    assert first is second
    assert len(created) == 1


def test_registry_keeps_separate_sessions_per_provider(tmp_path: Path) -> None:
    """Switching CLI must not overwrite the other CLI's session."""
    created: list[tuple[Path, str]] = []

    def factory(root: Path, name: str) -> Any:
        created.append((root, name))
        return _FakeProvider(root, name)

    registry = ChatSessionRegistry(factory=factory)
    ws = tmp_path / "ws"
    ws.mkdir()

    claude = registry.get_or_create(ws, "claude-code")
    codex = registry.get_or_create(ws, "codex")
    assert claude is not codex
    # Resume Claude after touching Codex — must be the original instance.
    claude_again = registry.get_or_create(ws, "claude-code")
    assert claude_again is claude


def test_registry_reset_one_provider_keeps_others(tmp_path: Path) -> None:
    created: list[tuple[Path, str]] = []

    def factory(root: Path, name: str) -> Any:
        created.append((root, name))
        return _FakeProvider(root, name)

    registry = ChatSessionRegistry(factory=factory)
    ws = tmp_path / "ws"
    ws.mkdir()

    claude = registry.get_or_create(ws, "claude-code")
    codex = registry.get_or_create(ws, "codex")
    registry.reset(ws, "claude-code")

    assert registry.get_or_create(ws, "claude-code") is not claude  # new
    assert registry.get_or_create(ws, "codex") is codex  # untouched


def test_registry_reset_all_providers_for_workspace(tmp_path: Path) -> None:
    created: list[tuple[Path, str]] = []

    def factory(root: Path, name: str) -> Any:
        created.append((root, name))
        return _FakeProvider(root, name)

    registry = ChatSessionRegistry(factory=factory)
    ws = tmp_path / "ws"
    ws.mkdir()

    claude = registry.get_or_create(ws, "claude-code")
    codex = registry.get_or_create(ws, "codex")
    registry.reset(ws)  # no provider_name → wipe all for this workspace

    assert registry.get_or_create(ws, "claude-code") is not claude
    assert registry.get_or_create(ws, "codex") is not codex


# ---------------------------------------------------------------------------
# ClaudeCodeProvider.stream_turn (with a fake subprocess factory)
# ---------------------------------------------------------------------------


class _FakeStdout:
    """Async-iterable that yields canned bytes lines, then EOF."""

    def __init__(self, lines: list[bytes]) -> None:
        self._lines = lines
        self._idx = 0

    def __aiter__(self) -> _FakeStdout:
        return self

    async def __anext__(self) -> bytes:
        if self._idx >= len(self._lines):
            raise StopAsyncIteration
        line = self._lines[self._idx]
        self._idx += 1
        return line


class _FakeStderr:
    def __init__(self, payload: bytes = b"") -> None:
        self._payload = payload

    async def read(self) -> bytes:
        return self._payload


class _FakeProcess:
    """Stand-in for ``asyncio.subprocess.Process``."""

    def __init__(
        self, *, stdout_lines: list[bytes], returncode: int, stderr: bytes = b""
    ) -> None:
        self.stdout = _FakeStdout(stdout_lines)
        self.stderr = _FakeStderr(stderr)
        self._returncode = returncode
        self.returncode: int | None = None
        self.killed = False
        self.spawn_args: list[str] = []
        self.spawn_cwd: str | None = None

    async def wait(self) -> int:
        self.returncode = self._returncode
        return self._returncode

    def kill(self) -> None:
        self.killed = True


def _build_fake_factory(
    process: _FakeProcess,
) -> Any:
    """Return a coroutine matching ``asyncio.create_subprocess_exec`` shape."""

    async def factory(*cmd: str, cwd: str | None = None, **_kwargs: Any) -> _FakeProcess:
        process.spawn_args = list(cmd)
        process.spawn_cwd = cwd
        return process

    return factory


async def _drain(provider: ClaudeCodeProvider, message: str) -> list[ChatStreamEvent]:
    return [event async for event in provider.stream_turn(message)]


async def test_stream_turn_yields_start_delta_complete_on_success(
    tmp_path: Path,
) -> None:
    process = _FakeProcess(
        stdout_lines=[
            json.dumps(
                {"type": "system", "subtype": "init", "session_id": "sid"}
            ).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [{"type": "text", "text": "Hello "}]
                    },
                }
            ).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [{"type": "text", "text": "world."}]
                    },
                }
            ).encode()
            + b"\n",
        ],
        returncode=0,
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = ClaudeCodeProvider(
        workspace_root=ws,
        session_id="fixed-session",
        cli_path="claude",
        subprocess_factory=_build_fake_factory(process),
    )

    events = await _drain(provider, "say hi")
    assert [e.type for e in events] == ["turn_start", "delta", "delta", "turn_complete"]
    assert events[1].text == "Hello "
    assert events[2].text == "world."
    assert events[3].text == "Hello world."  # accumulated
    # Spawn command uses --session-id on the first turn + cwd is the workspace.
    assert process.spawn_cwd == str(ws)
    assert "--session-id" in process.spawn_args
    assert "fixed-session" in process.spawn_args
    assert "--print" in process.spawn_args
    assert "--output-format" in process.spawn_args
    assert "stream-json" in process.spawn_args
    assert "say hi" in process.spawn_args


async def test_stream_turn_resumes_on_second_turn(tmp_path: Path) -> None:
    """First turn uses ``--session-id``; the next reuses ``--resume <id>``."""
    process_a = _FakeProcess(stdout_lines=[], returncode=0)
    process_b = _FakeProcess(stdout_lines=[], returncode=0)

    queue = [process_a, process_b]

    async def factory(*cmd: str, cwd: str | None = None, **_kwargs: Any) -> _FakeProcess:
        proc = queue.pop(0)
        proc.spawn_args = list(cmd)
        proc.spawn_cwd = cwd
        return proc

    ws = tmp_path / "ws"
    ws.mkdir()
    provider = ClaudeCodeProvider(
        workspace_root=ws,
        session_id="sid-1",
        cli_path="claude",
        subprocess_factory=factory,
    )

    await _drain(provider, "first")
    await _drain(provider, "second")

    assert "--session-id" in process_a.spawn_args
    assert "sid-1" in process_a.spawn_args
    assert "--resume" not in process_a.spawn_args

    assert "--resume" in process_b.spawn_args
    assert "sid-1" in process_b.spawn_args
    assert "--session-id" not in process_b.spawn_args


async def test_stream_turn_emits_error_on_non_zero_exit(tmp_path: Path) -> None:
    process = _FakeProcess(
        stdout_lines=[],
        returncode=2,
        stderr=b"not logged in",
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = ClaudeCodeProvider(
        workspace_root=ws,
        session_id="sid",
        cli_path="claude",
        subprocess_factory=_build_fake_factory(process),
    )

    events = await _drain(provider, "hi")
    assert events[0].type == "turn_start"
    assert events[-1].type == "error"
    assert events[-1].error_message is not None
    assert "not logged in" in events[-1].error_message
    # turn_complete must NOT fire on error
    assert not any(e.type == "turn_complete" for e in events)


async def test_stream_turn_kills_process_on_cancel(tmp_path: Path) -> None:
    """If the consumer abandons the iterator mid-stream, the subprocess dies."""
    # Infinite-ish stream of delta lines — we'll cancel after one.
    payload = json.dumps(
        {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "chunk"}]},
        }
    ).encode() + b"\n"

    class _HangingStdout:
        def __init__(self) -> None:
            self._first = True

        def __aiter__(self) -> _HangingStdout:
            return self

        async def __anext__(self) -> bytes:
            if self._first:
                self._first = False
                return payload
            await asyncio.sleep(60)  # would block forever
            raise StopAsyncIteration

    class _HangingProcess(_FakeProcess):
        def __init__(self) -> None:
            super().__init__(stdout_lines=[], returncode=0)
            self.stdout = _HangingStdout()  # type: ignore[assignment]

    process = _HangingProcess()

    async def factory(*cmd: str, cwd: str | None = None, **_: Any) -> _HangingProcess:
        process.spawn_args = list(cmd)
        process.spawn_cwd = cwd
        return process

    ws = tmp_path / "ws"
    ws.mkdir()
    provider = ClaudeCodeProvider(
        workspace_root=ws,
        session_id="sid",
        cli_path="claude",
        subprocess_factory=factory,
    )

    agen = provider.stream_turn("hi").__aiter__()
    # Pull turn_start + the first delta.
    first = await agen.__anext__()
    assert first.type == "turn_start"
    second = await agen.__anext__()
    assert second.type == "delta"
    # Closing the generator must trigger the finally → kill().
    await agen.aclose()
    assert process.killed


# ---------------------------------------------------------------------------
# Integration sanity — registry hands out a real ClaudeCodeProvider by default
# ---------------------------------------------------------------------------


def test_default_registry_factory_builds_claude_provider(tmp_path: Path) -> None:
    registry = ChatSessionRegistry()
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = registry.get_or_create(ws, "claude-code")
    assert isinstance(provider, ClaudeCodeProvider)


def test_default_registry_factory_builds_codex_provider(tmp_path: Path) -> None:
    from plot_mcp.chat_session import CodexProvider

    registry = ChatSessionRegistry()
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = registry.get_or_create(ws, "codex")
    assert isinstance(provider, CodexProvider)


def test_default_registry_factory_builds_gemini_provider(tmp_path: Path) -> None:
    from plot_mcp.chat_session import GeminiProvider

    registry = ChatSessionRegistry()
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = registry.get_or_create(ws, "gemini")
    assert isinstance(provider, GeminiProvider)


@pytest.fixture(autouse=True)
def _isolate_event_loop() -> Any:
    yield


# ---------------------------------------------------------------------------
# CodexProvider — `codex exec --json` parsing + resume command shape
# ---------------------------------------------------------------------------


async def test_codex_stream_yields_agent_message_text_and_captures_thread_id(
    tmp_path: Path,
) -> None:
    process = _FakeProcess(
        stdout_lines=[
            json.dumps({"type": "thread.started", "thread_id": "tid-abc"}).encode()
            + b"\n",
            json.dumps({"type": "turn.started"}).encode() + b"\n",
            # Tool work — should be dropped, not surfaced as a delta.
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "id": "item_1",
                        "type": "command_execution",
                        "command": "ls",
                        "status": "completed",
                    },
                }
            ).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "id": "item_2",
                        "type": "agent_message",
                        "text": "Repo has docs and src.",
                    },
                }
            ).encode()
            + b"\n",
            json.dumps(
                {"type": "turn.completed", "usage": {"input_tokens": 100}}
            ).encode()
            + b"\n",
        ],
        returncode=0,
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = CodexProvider(
        workspace_root=ws,
        cli_path="codex",
        subprocess_factory=_build_fake_factory(process),
    )
    events = await _drain(provider, "describe the repo")
    types = [e.type for e in events]
    assert types == ["turn_start", "delta", "turn_complete"]
    assert events[1].text == "Repo has docs and src."
    assert provider.session_id == "tid-abc"


async def test_codex_second_turn_uses_exec_resume_with_captured_thread_id(
    tmp_path: Path,
) -> None:
    captured_a = _FakeProcess(
        stdout_lines=[
            json.dumps({"type": "thread.started", "thread_id": "tid-xyz"}).encode()
            + b"\n",
        ],
        returncode=0,
    )
    captured_b = _FakeProcess(stdout_lines=[], returncode=0)
    queue = [captured_a, captured_b]

    async def factory(*cmd: str, cwd: str | None = None, **_: Any) -> _FakeProcess:
        proc = queue.pop(0)
        proc.spawn_args = list(cmd)
        proc.spawn_cwd = cwd
        return proc

    ws = tmp_path / "ws"
    ws.mkdir()
    provider = CodexProvider(
        workspace_root=ws, cli_path="codex", subprocess_factory=factory
    )
    await _drain(provider, "first")
    await _drain(provider, "second")

    assert "exec" in captured_a.spawn_args
    assert "resume" not in captured_a.spawn_args
    assert "first" in captured_a.spawn_args

    assert "resume" in captured_b.spawn_args
    assert "tid-xyz" in captured_b.spawn_args
    assert "second" in captured_b.spawn_args


async def test_codex_first_turn_falls_back_to_fresh_exec_when_no_thread_id(
    tmp_path: Path,
) -> None:
    """If the first turn never emits thread.started (CLI crash, parse skip),
    the next turn must NOT call ``resume`` with ``None`` — fall through and
    start a fresh session instead."""
    a = _FakeProcess(stdout_lines=[], returncode=0)
    b = _FakeProcess(stdout_lines=[], returncode=0)
    queue = [a, b]

    async def factory(*cmd: str, cwd: str | None = None, **_: Any) -> _FakeProcess:
        proc = queue.pop(0)
        proc.spawn_args = list(cmd)
        proc.spawn_cwd = cwd
        return proc

    ws = tmp_path / "ws"
    ws.mkdir()
    provider = CodexProvider(workspace_root=ws, subprocess_factory=factory)
    await _drain(provider, "first")
    await _drain(provider, "second")

    assert "resume" not in b.spawn_args
    assert provider.session_id is None


# ---------------------------------------------------------------------------
# GeminiProvider — `gemini -y --output-format stream-json` parsing + resume
# ---------------------------------------------------------------------------


async def test_gemini_stream_yields_assistant_content_and_captures_session_id(
    tmp_path: Path,
) -> None:
    process = _FakeProcess(
        stdout_lines=[
            json.dumps(
                {
                    "type": "init",
                    "session_id": "sid-9",
                    "model": "gemini-2.0-flash-exp",
                }
            ).encode()
            + b"\n",
            # User-echo event should NOT surface — user message is already in
            # the panel from optimistic render.
            json.dumps(
                {"type": "message", "role": "user", "content": "List files"}
            ).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "message",
                    "role": "assistant",
                    "content": "Here ",
                    "delta": True,
                }
            ).encode()
            + b"\n",
            json.dumps(
                {
                    "type": "message",
                    "role": "assistant",
                    "content": "are the files.",
                    "delta": True,
                }
            ).encode()
            + b"\n",
            json.dumps({"type": "result", "status": "success"}).encode() + b"\n",
        ],
        returncode=0,
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    provider = GeminiProvider(
        workspace_root=ws,
        cli_path="gemini",
        subprocess_factory=_build_fake_factory(process),
    )
    events = await _drain(provider, "list files")
    types = [e.type for e in events]
    assert types == ["turn_start", "delta", "delta", "turn_complete"]
    assert events[1].text == "Here "
    assert events[2].text == "are the files."
    assert events[3].text == "Here are the files."
    assert provider.session_id == "sid-9"


async def test_gemini_second_turn_uses_resume_with_captured_session_id(
    tmp_path: Path,
) -> None:
    a = _FakeProcess(
        stdout_lines=[
            json.dumps({"type": "init", "session_id": "sid-7"}).encode() + b"\n",
        ],
        returncode=0,
    )
    b = _FakeProcess(stdout_lines=[], returncode=0)
    queue = [a, b]

    async def factory(*cmd: str, cwd: str | None = None, **_: Any) -> _FakeProcess:
        proc = queue.pop(0)
        proc.spawn_args = list(cmd)
        proc.spawn_cwd = cwd
        return proc

    ws = tmp_path / "ws"
    ws.mkdir()
    provider = GeminiProvider(
        workspace_root=ws, cli_path="gemini", subprocess_factory=factory
    )
    await _drain(provider, "first")
    await _drain(provider, "second")

    assert "--resume" not in a.spawn_args
    assert "--output-format" in a.spawn_args
    assert "stream-json" in a.spawn_args

    assert "--resume" in b.spawn_args
    assert "sid-7" in b.spawn_args
