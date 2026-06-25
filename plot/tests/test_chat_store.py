"""Chat conversation persistence (D-2026-06-26-B).

In-memory chat died on an app restart and the user lost real work. Conversations
now persist to ``.noory/plot/chat/<scope>.json`` — one append-only log per scope,
engine-side — so they survive a restart and travel with the project.
"""

from __future__ import annotations

import pytest

from plot_mcp.chat_store import (
    append_assistant,
    append_user,
    list_conversations,
    read_conversation,
)
from plot_mcp.project_io import create_project
from plot_mcp.workspace import resolve_plot_root


def _project(tmp_path):
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "alpha", "Alpha")
    return plot_root, "alpha"


def test_append_user_creates_file_with_title(tmp_path):
    plot_root, pid = _project(tmp_path)
    append_user(plot_root, pid, "foundation", "claude-code", "user_1", "Define the mission")
    doc = read_conversation(plot_root, pid, "foundation")
    assert doc.scope == "foundation"
    assert doc.provider == "claude-code"
    assert doc.title == "Define the mission"  # first user message
    assert doc.created == doc.updated
    assert [(m.role, m.text) for m in doc.messages] == [("user", "Define the mission")]


def test_append_assistant_appends_and_bumps_updated(tmp_path):
    plot_root, pid = _project(tmp_path)
    append_user(plot_root, pid, "foundation", "claude-code", "user_1", "Hi")
    created = read_conversation(plot_root, pid, "foundation").created
    append_assistant(plot_root, pid, "foundation", "claude-code", "turn_1", "Hello back")
    doc = read_conversation(plot_root, pid, "foundation")
    assert [m.role for m in doc.messages] == ["user", "assistant"]
    assert doc.created == created  # unchanged
    assert doc.updated >= created  # advanced (or equal at worst)
    assert doc.title == "Hi"  # never overwritten


def test_parametric_scope_filename_and_roundtrip(tmp_path):
    plot_root, pid = _project(tmp_path)
    append_user(plot_root, pid, "service:abc123", "codex", "user_1", "Refund flow")
    # ':' is sanitised to '__' on disk, fs-safe
    assert (plot_root / "chat" / "service__abc123.json").exists()
    # round-trips back through read + list
    assert read_conversation(plot_root, pid, "service:abc123").scope == "service:abc123"
    scopes = [c["scope"] for c in list_conversations(plot_root, pid)]
    assert "service:abc123" in scopes


def test_traversal_in_scope_id_is_rejected(tmp_path):
    plot_root, pid = _project(tmp_path)
    with pytest.raises(ValueError):
        append_user(plot_root, pid, "service:../../evil", "codex", "user_1", "x")


def test_empty_conversation_not_written(tmp_path):
    plot_root, pid = _project(tmp_path)
    # No turn ran — clicking into a scope writes nothing.
    assert list_conversations(plot_root, pid) == []
    assert not (plot_root / "chat").exists()


def test_list_sorted_by_updated_desc(tmp_path):
    plot_root, pid = _project(tmp_path)
    append_user(plot_root, pid, "foundation", "claude-code", "user_1", "first")
    append_user(plot_root, pid, "actors", "claude-code", "user_2", "second")
    scopes = [c["scope"] for c in list_conversations(plot_root, pid)]
    assert scopes == ["actors", "foundation"]  # newest-updated first


def test_read_missing_conversation_raises(tmp_path):
    plot_root, pid = _project(tmp_path)
    with pytest.raises(FileNotFoundError):
        read_conversation(plot_root, pid, "entities")


def test_survives_simulated_restart(tmp_path):
    """The regression for the actual bug: write, then read from a fresh root
    handle (process-equivalent) — the transcript is still there."""
    plot_root, pid = _project(tmp_path)
    append_user(plot_root, pid, "project", "claude-code", "user_1", "the mission")
    append_assistant(plot_root, pid, "project", "claude-code", "turn_1", "pinned it")
    fresh_root = resolve_plot_root(str(tmp_path))  # as if a new engine process opened it
    doc = read_conversation(fresh_root, pid, "project")
    assert [m.text for m in doc.messages] == ["the mission", "pinned it"]
