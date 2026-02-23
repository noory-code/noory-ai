"""Tests for MCP server tool registrations and tool wrappers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# --- Server setup ---


def test_server_instance_exists() -> None:
    """FastMCP server should be importable."""
    from evonest.server import mcp

    assert mcp.name == "evonest"


def test_all_tools_registered() -> None:
    """All MCP tools should be registered."""
    from evonest.server import mcp

    tool_names = {t.name for t in mcp._tool_manager.list_tools()}
    expected = {
        "evonest_init",
        "evonest_run",  # deprecated but kept for backward compat
        "evonest_analyze",  # new
        "evonest_improve",  # new
        "evonest_evolve",  # new
        "evonest_status",
        "evonest_history",
        "evonest_config",
        "evonest_identity",
        "evonest_progress",
        "evonest_backlog",
        "evonest_stimuli",
        "evonest_decide",
    }
    assert expected.issubset(tool_names), f"Missing: {expected - tool_names}"


# --- Tool wrappers (call async functions directly) ---


@pytest.mark.asyncio
async def test_tool_init(tmp_path: Path) -> None:
    """evonest_init should create .evonest/ directory."""
    from evonest.tools.init import evonest_init

    result = await evonest_init(str(tmp_path))
    assert "Initialized" in result
    assert (tmp_path / ".evonest" / "config.json").exists()
    assert (tmp_path / ".evonest" / "identity.md").exists()
    assert (tmp_path / ".evonest" / "progress.json").exists()
    assert (tmp_path / ".evonest" / "backlog.json").exists()


@pytest.mark.asyncio
async def test_tool_status(tmp_project: Path) -> None:
    """evonest_status should return status summary."""
    from evonest.tools.status import evonest_status

    result = await evonest_status(str(tmp_project))
    assert "Project:" in result
    assert "Cycles:" in result


@pytest.mark.asyncio
async def test_tool_history_empty(tmp_project: Path) -> None:
    """evonest_history should work with no history."""
    from evonest.tools.history import evonest_history

    result = await evonest_history(str(tmp_project))
    assert "No cycle history" in result


@pytest.mark.asyncio
async def test_tool_config_read(tmp_project: Path) -> None:
    """evonest_config should return config JSON."""
    from evonest.tools.config import evonest_config

    result = await evonest_config(str(tmp_project))
    data = json.loads(result)
    assert "model" in data
    assert "max_cycles_per_run" in data


@pytest.mark.asyncio
async def test_tool_config_update(tmp_project: Path) -> None:
    """evonest_config should update settings."""
    from evonest.tools.config import evonest_config

    result = await evonest_config(str(tmp_project), settings={"model": "opus"})
    assert "Updated" in result
    assert "model" in result

    # Verify persisted
    result2 = await evonest_config(str(tmp_project))
    data = json.loads(result2)
    assert data["model"] == "opus"


@pytest.mark.asyncio
async def test_tool_identity_read(tmp_project: Path) -> None:
    """evonest_identity should return identity content."""
    from evonest.tools.identity import evonest_identity

    result = await evonest_identity(str(tmp_project))
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_tool_identity_write(tmp_project: Path) -> None:
    """evonest_identity should update identity content."""
    from evonest.tools.identity import evonest_identity

    await evonest_identity(str(tmp_project), content="# Test Project\nA test.")
    result = await evonest_identity(str(tmp_project))
    assert "# Test Project" in result


@pytest.mark.asyncio
async def test_tool_progress(tmp_project: Path) -> None:
    """evonest_progress should return progress report."""
    from evonest.tools.progress import evonest_progress

    result = await evonest_progress(str(tmp_project))
    assert "Total cycles:" in result


@pytest.mark.asyncio
async def test_tool_backlog_list_empty(tmp_project: Path) -> None:
    """evonest_backlog list should work with empty backlog."""
    from evonest.tools.backlog import evonest_backlog

    result = await evonest_backlog(str(tmp_project), action="list")
    assert "empty" in result.lower()


@pytest.mark.asyncio
async def test_tool_backlog_add(tmp_project: Path) -> None:
    """evonest_backlog add should add items."""
    from evonest.tools.backlog import evonest_backlog

    result = await evonest_backlog(
        str(tmp_project), action="add", item={"title": "Test item", "priority": "high"}
    )
    assert "Added" in result

    result2 = await evonest_backlog(str(tmp_project), action="list")
    assert "Test item" in result2


@pytest.mark.asyncio
async def test_tool_backlog_prune(tmp_project: Path) -> None:
    """evonest_backlog prune should work."""
    from evonest.tools.backlog import evonest_backlog

    result = await evonest_backlog(str(tmp_project), action="prune")
    assert "Pruned" in result


@pytest.mark.asyncio
async def test_tool_stimuli(tmp_project: Path) -> None:
    """evonest_stimuli should save a stimulus file."""
    from evonest.tools.stimuli import evonest_stimuli

    result = await evonest_stimuli(str(tmp_project), content="Focus on security next cycle")
    assert "Stimulus saved" in result

    # Verify file exists
    stimuli_dir = tmp_project / ".evonest" / "stimuli"
    files = list(stimuli_dir.glob("stimulus-*.md"))
    assert len(files) == 1
    assert "Focus on security" in files[0].read_text()


@pytest.mark.asyncio
async def test_tool_decide(tmp_project: Path) -> None:
    """evonest_decide should save a decision file."""
    from evonest.tools.decide import evonest_decide

    result = await evonest_decide(str(tmp_project), content="Use PostgreSQL for the DB layer")
    assert "Decision saved" in result

    # Verify file exists
    decisions_dir = tmp_project / ".evonest" / "decisions"
    files = list(decisions_dir.glob("decision-*.md"))
    assert len(files) == 1
    assert "PostgreSQL" in files[0].read_text()


@pytest.mark.asyncio
async def test_tool_run_dry_run(tmp_project: Path) -> None:
    """evonest_run with dry_run should redirect to analyze (deprecated)."""
    import warnings
    from unittest.mock import patch

    from evonest.core.claude_runner import ClaudeResult
    from evonest.tools.run import evonest_run

    mock_observe = ClaudeResult(
        output='```json\n{"improvements": [{"title": "Test"}], "observations": ["x"]}\n```',
        exit_code=0,
        success=True,
    )

    with (
        patch("evonest.core.phases.claude_runner.run") as mock_run,
        warnings.catch_warnings(record=True),
    ):
        warnings.simplefilter("always")
        mock_run.return_value = mock_observe
        result = await evonest_run(
            str(tmp_project),
            cycles=1,
            dry_run=True,
            no_meta=True,
        )

    assert "Analyze complete" in result


# --- evonest_proposals ---


@pytest.mark.asyncio
async def test_proposals_empty(tmp_project: Path) -> None:
    """No proposals → clear message."""
    from evonest.tools.proposals import evonest_proposals

    result = await evonest_proposals(str(tmp_project))
    assert result == "No pending proposals."


@pytest.mark.asyncio
async def test_proposals_list_shows_title_and_priority(tmp_project: Path) -> None:
    """Proposals list shows title, priority, persona, and filename."""
    from evonest.core.state import ProjectState
    from evonest.tools.proposals import evonest_proposals

    state = ProjectState(str(tmp_project))
    state.proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal_file = state.proposals_dir / "proposal-0001-20260101-000000-000001.md"
    proposal_file.write_text(
        "# 제안: 테스트 개선\n\n**우선순위**: high\n**작성 페르소나**: architect\n\n내용",
        encoding="utf-8",
    )

    result = await evonest_proposals(str(tmp_project))

    assert "테스트 개선" in result
    assert "high" in result
    assert "architect" in result
    assert "proposal-0001-20260101-000000-000001.md" in result
    assert "evonest_improve" in result


@pytest.mark.asyncio
async def test_proposals_list_sorted_by_priority(tmp_project: Path) -> None:
    """Proposals are sorted high → medium → low."""
    from evonest.core.state import ProjectState
    from evonest.tools.proposals import evonest_proposals

    state = ProjectState(str(tmp_project))
    state.proposals_dir.mkdir(parents=True, exist_ok=True)
    for name, priority in [
        ("proposal-0001-20260101-000000-000001.md", "low"),
        ("proposal-0002-20260101-000000-000002.md", "high"),
        ("proposal-0003-20260101-000000-000003.md", "medium"),
    ]:
        (state.proposals_dir / name).write_text(
            f"# 제안: {priority} 항목\n\n**우선순위**: {priority}\n**작성 페르소나**: test\n",
            encoding="utf-8",
        )

    result = await evonest_proposals(str(tmp_project))

    idx_high = result.index("high 항목")
    idx_medium = result.index("medium 항목")
    idx_low = result.index("low 항목")
    assert idx_high < idx_medium < idx_low


# ── adversarial input tests ────────


@pytest.mark.asyncio
async def test_tool_identity_corrupted_file(tmp_project: Path) -> None:
    """손상된 identity.md 파일로 identity 도구 테스트."""
    from evonest.tools.identity import evonest_identity

    identity_path = tmp_project / ".evonest" / "identity.md"
    identity_path.write_text(
        "\x00\xff\xfe" + "corrupted content", encoding="utf-8", errors="ignore"
    )

    result = await evonest_identity(str(tmp_project))
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_tool_identity_write_with_null_bytes(tmp_project: Path) -> None:
    """null 바이트가 포함된 내용으로 identity 업데이트 시도."""
    from evonest.tools.identity import evonest_identity

    content_with_null = "# Test\x00Project\nContent"
    await evonest_identity(str(tmp_project), content=content_with_null)
    result = await evonest_identity(str(tmp_project))
    assert isinstance(result, str)
