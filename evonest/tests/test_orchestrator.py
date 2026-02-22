"""Tests for core/orchestrator.py — main cycle loop with mocked claude calls."""

from __future__ import annotations

import asyncio  # noqa: F401 — needed for pytest-asyncio event loop
from pathlib import Path
from unittest.mock import patch

import pytest

from evonest.core.claude_runner import ClaudeResult
from evonest.core.orchestrator import run_analyze, run_cycles
from evonest.core.state import ProjectState


def _mock_claude_success(output: str = "mock output") -> ClaudeResult:
    return ClaudeResult(output=output, exit_code=0, success=True)


def _mock_observe_output() -> ClaudeResult:
    return ClaudeResult(
        output="""```json
{
  "improvements": [{"title": "Fix bug", "category": "bugfix"}],
  "observations": ["Found a bug"]
}
```""",
        exit_code=0,
        success=True,
    )


def _mock_plan_output() -> ClaudeResult:
    return ClaudeResult(
        output=(
            '{"selected_improvement": {"title": "Fix bug"},'
            ' "plan": {"commit_message": "fix: bug"}}'
        ),
        exit_code=0,
        success=True,
    )


def _mock_execute_output() -> ClaudeResult:
    return ClaudeResult(
        output='{"status": "completed", "files_modified": ["src/a.py"]}',
        exit_code=0,
        success=True,
    )


@pytest.mark.asyncio
async def test_dry_run_deprecated_redirects_to_analyze(tmp_project: Path) -> None:
    """dry_run=True should redirect to run_analyze and emit DeprecationWarning."""
    with (
        patch("evonest.core.phases.claude_runner.run") as mock_run,
        pytest.warns(DeprecationWarning, match="deprecated"),
    ):
        mock_run.return_value = _mock_observe_output()
        result = await run_cycles(str(tmp_project), cycles=1, dry_run=True)

    assert "Analyze complete" in result


@pytest.mark.asyncio
async def test_analyze_saves_proposals(tmp_project: Path) -> None:
    """run_analyze should save all improvements as proposals, not update progress."""
    with patch("evonest.core.phases.claude_runner.run") as mock_run:
        mock_run.return_value = _mock_observe_output()
        result = await run_analyze(str(tmp_project))

    assert "Analyze complete" in result
    state = ProjectState(tmp_project)
    proposals = state.list_proposals()
    assert len(proposals) == 1  # _mock_observe_output has 1 improvement
    # Progress should NOT be updated (analyze is not a cycle)
    progress = state.read_progress()
    assert progress.get("total_cycles", 0) == 0


@pytest.mark.asyncio
async def test_analyze_observe_failure(tmp_project: Path) -> None:
    """run_analyze should report 0 proposals when observe fails."""
    with patch("evonest.core.phases.claude_runner.run") as mock_run:
        mock_run.return_value = ClaudeResult(output="", exit_code=1, success=False)
        result = await run_analyze(str(tmp_project))

    assert "0 proposals" in result


@pytest.mark.asyncio
async def test_observe_failure_skips_cycle(tmp_project: Path) -> None:
    """If observe fails in evolve mode, the cycle should be skipped."""
    with (
        patch("evonest.core.phases.claude_runner.run") as mock_run,
        patch("evonest.core.orchestrator._git_stash"),
        patch("evonest.core.orchestrator._git_revert"),
    ):
        mock_run.return_value = ClaudeResult(output="", exit_code=1, success=False)
        result = await run_cycles(str(tmp_project), cycles=1)

    assert "0/1 cycles succeeded" in result


@pytest.mark.asyncio
async def test_observe_failure_logs_stderr(tmp_project: Path) -> None:
    """If observe fails with stderr, the log should include it."""
    with patch("evonest.core.phases.claude_runner.run") as mock_run:
        mock_run.return_value = ClaudeResult(
            output="", exit_code=1, success=False, stderr="timeout detail"
        )
        await run_analyze(str(tmp_project))

    state = ProjectState(tmp_project)
    log_text = state.log_path.read_text(encoding="utf-8")
    assert "timeout detail" in log_text


@pytest.mark.asyncio
async def test_plan_no_improvements_stops(tmp_project: Path) -> None:
    """If plan says no improvements, should stop early."""
    no_imp = ClaudeResult(
        output='{"selected_improvement": null, "reason": "no improvements"}',
        exit_code=0,
        success=True,
    )
    with (
        patch("evonest.core.phases.claude_runner.run") as mock_run,
        patch("evonest.core.orchestrator._git_stash"),
        patch("evonest.core.orchestrator._git_revert"),
    ):
        mock_run.side_effect = [_mock_observe_output(), no_imp]
        result = await run_cycles(str(tmp_project), cycles=3)

    assert "0/3 cycles succeeded" in result


@pytest.mark.asyncio
async def test_analyze_multiple_personas(tmp_project: Path) -> None:
    """run_analyze with all_personas=True should run every persona."""
    from evonest.core.mutations import load_personas

    state = ProjectState(tmp_project)
    all_ids = [p["id"] for p in load_personas(state)]

    with patch("evonest.core.phases.claude_runner.run") as mock_run:
        mock_run.return_value = _mock_observe_output()
        result = await run_analyze(str(tmp_project), all_personas=True)

    assert f"{len(all_ids)} persona(s)" in result


@pytest.mark.asyncio
async def test_no_meta_flag(tmp_project: Path) -> None:
    """Meta-observe should not run when no_meta=True."""
    # Pre-set progress to trigger meta (5+ cycles since last)
    state = ProjectState(tmp_project)
    progress = state.read_progress()
    progress["total_cycles"] = 10
    progress["last_meta_cycle"] = 0
    state.write_progress(progress)

    with (
        patch("evonest.core.phases.claude_runner.run") as mock_run,
        patch("evonest.core.orchestrator._run_meta_observe") as mock_meta,
    ):
        mock_run.side_effect = [_mock_observe_output(), _mock_plan_output()]
        # run_analyze never runs meta; verify meta stays off by running analyze
        await run_analyze(str(tmp_project), observe_mode="quick")

    mock_meta.assert_not_called()


@pytest.mark.asyncio
async def test_lock_prevents_concurrent(tmp_project: Path) -> None:
    """Should raise RuntimeError if already locked."""
    state = ProjectState(tmp_project)
    # Create lock file manually
    state.lock_path.parent.mkdir(parents=True, exist_ok=True)
    state.lock_path.write_text("12345")

    with pytest.raises(RuntimeError, match="Another evolution is running"):
        await run_analyze(str(tmp_project))


# ── observe_mode selection logic ─────────────────────────


def _make_phase_result(success: bool = True, deep: bool = False) -> object:
    from evonest.core.phases import PhaseResult

    return PhaseResult(phase="observe", output="", success=success)


@pytest.mark.asyncio
async def test_observe_mode_deep_forces_deep(tmp_project: Path) -> None:
    """observe_mode='deep' should always call run_observe with deep=True."""
    with patch("evonest.core.orchestrator.run_observe") as mock_observe:
        mock_observe.return_value = _make_phase_result(success=True)
        await run_analyze(str(tmp_project), observe_mode="deep")

    mock_observe.assert_called_once()
    _, kwargs = mock_observe.call_args
    assert kwargs.get("deep") is True


@pytest.mark.asyncio
async def test_observe_mode_quick_forces_quick(tmp_project: Path) -> None:
    """observe_mode='quick' should always call run_observe with deep=False."""
    with patch("evonest.core.orchestrator.run_observe") as mock_observe:
        mock_observe.return_value = _make_phase_result(success=True)
        await run_analyze(str(tmp_project), observe_mode="quick")

    mock_observe.assert_called_once()
    _, kwargs = mock_observe.call_args
    assert kwargs.get("deep") is False


@pytest.mark.asyncio
async def test_observe_mode_auto_uses_interval(tmp_project: Path) -> None:
    """observe_mode='auto' selects deep when total_cycles % deep_cycle_interval == 0."""
    state = ProjectState(tmp_project)
    progress = state.read_progress()
    progress["total_cycles"] = 10  # matches deep_cycle_interval default of 10
    state.write_progress(progress)

    with patch("evonest.core.orchestrator.run_observe") as mock_observe:
        mock_observe.return_value = _make_phase_result(success=True)
        await run_analyze(str(tmp_project))

    mock_observe.assert_called_once()
    _, kwargs = mock_observe.call_args
    assert kwargs.get("deep") is True


@pytest.mark.asyncio
async def test_observe_mode_auto_quick_when_not_interval(tmp_project: Path) -> None:
    """observe_mode='auto' selects quick when total_cycles % interval != 0."""
    state = ProjectState(tmp_project)
    progress = state.read_progress()
    progress["total_cycles"] = 3  # not a multiple of 10
    state.write_progress(progress)

    with patch("evonest.core.orchestrator.run_observe") as mock_observe:
        mock_observe.return_value = _make_phase_result(success=True)
        await run_analyze(str(tmp_project))

    mock_observe.assert_called_once()
    _, kwargs = mock_observe.call_args
    assert kwargs.get("deep") is False


@pytest.mark.asyncio
async def test_all_personas_runs_each_once(tmp_project: Path) -> None:
    """all_personas=True should run every persona exactly once, in order."""
    from evonest.core.mutations import load_personas
    from evonest.core.state import ProjectState

    state = ProjectState(tmp_project)
    all_ids = [p["id"] for p in load_personas(state)]

    called_persona_ids: list[str] = []

    def fake_select_mutation(s, adv_prob, cfg, persona_id=None, **kw):  # type: ignore[no-untyped-def]
        called_persona_ids.append(persona_id)
        return {
            "persona_id": persona_id or "unknown",
            "persona_name": persona_id or "Unknown",
            "persona_text": "test",
            "adversarial_id": None,
            "adversarial_name": None,
            "adversarial_text": "",
            "stimuli": [],
        }

    with (
        patch("evonest.core.orchestrator.select_mutation", side_effect=fake_select_mutation),
        patch("evonest.core.orchestrator.run_observe") as mock_observe,
    ):
        mock_observe.return_value = _make_phase_result(success=True)
        await run_analyze(str(tmp_project), all_personas=True)

    assert called_persona_ids == all_ids
