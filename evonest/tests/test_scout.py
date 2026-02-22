"""Tests for core/scout.py — external search-based mutation generation."""

from __future__ import annotations

from pathlib import Path

from evonest.core.config import EvonestConfig
from evonest.core.scout import (
    _make_finding_id,
    apply_scout_results,
    build_scout_prompt,
    parse_scout_json,
    should_run_scout,
)
from evonest.core.state import ProjectState

# ── should_run_scout ──────────────────────────────────────


def test_should_run_scout_disabled() -> None:
    config = EvonestConfig()
    config.scout_enabled = False
    progress = {"total_cycles": 15, "last_scout_cycle": 0}
    assert should_run_scout(progress, config) is False


def test_should_run_scout_zero_cycles() -> None:
    config = EvonestConfig()
    progress = {"total_cycles": 0}
    assert should_run_scout(progress, config) is False


def test_should_run_scout_not_yet() -> None:
    config = EvonestConfig()
    config.scout_cycle_interval = 10
    progress = {"total_cycles": 5, "last_scout_cycle": 0}
    assert should_run_scout(progress, config) is False


def test_should_run_scout_ready() -> None:
    config = EvonestConfig()
    config.scout_cycle_interval = 10
    progress = {"total_cycles": 10, "last_scout_cycle": 0}
    assert should_run_scout(progress, config) is True


def test_should_run_scout_after_previous() -> None:
    config = EvonestConfig()
    config.scout_cycle_interval = 10
    progress = {"total_cycles": 25, "last_scout_cycle": 15}
    assert should_run_scout(progress, config) is True


def test_should_run_scout_too_soon_after_previous() -> None:
    config = EvonestConfig()
    config.scout_cycle_interval = 10
    progress = {"total_cycles": 20, "last_scout_cycle": 15}
    assert should_run_scout(progress, config) is False


# ── build_scout_prompt ────────────────────────────────────


def test_build_scout_prompt_includes_identity(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_identity("# My Project\n\n## Ecosystem\nPython FastAPI")

    prompt = build_scout_prompt(state)

    assert "Project Identity" in prompt
    assert "My Project" in prompt
    assert "Python FastAPI" in prompt


def test_build_scout_prompt_includes_seen_findings(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_scout(
        {
            "findings": [
                {"id": "abc123", "title": "Old finding", "injected_as_stimulus": True},
            ]
        }
    )

    prompt = build_scout_prompt(state)
    assert "abc123" in prompt
    assert "Already Reported" in prompt


def test_build_scout_prompt_no_seen_findings(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)

    prompt = build_scout_prompt(state)
    # The dynamic "Already Reported Findings" section should not appear
    # when there are no prior findings (the template may reference it in general text)
    assert "## Already Reported Findings" not in prompt


# ── parse_scout_json ──────────────────────────────────────


def test_parse_scout_json_valid() -> None:
    output = """Some analysis.

```json
{
  "keywords_used": ["python", "fastapi"],
  "findings": [
    {"title": "FastAPI 0.100 released", "relevance_score": 8, "source_url": "https://example.com"}
  ]
}
```"""
    result = parse_scout_json(output)
    assert result is not None
    assert len(result["findings"]) == 1
    assert result["findings"][0]["title"] == "FastAPI 0.100 released"


def test_parse_scout_json_no_json() -> None:
    assert parse_scout_json("no json here") is None


def test_parse_scout_json_invalid_json() -> None:
    output = "```json\n{invalid}\n```"
    assert parse_scout_json(output) is None


def test_parse_scout_json_empty_findings() -> None:
    output = '```json\n{"keywords_used": [], "findings": []}\n```'
    result = parse_scout_json(output)
    assert result is not None
    assert result["findings"] == []


# ── _make_finding_id ──────────────────────────────────────


def test_make_finding_id_stable() -> None:
    id1 = _make_finding_id("FastAPI 0.100", "https://example.com")
    id2 = _make_finding_id("FastAPI 0.100", "https://example.com")
    assert id1 == id2


def test_make_finding_id_different_inputs() -> None:
    id1 = _make_finding_id("FastAPI 0.100", "https://example.com")
    id2 = _make_finding_id("FastAPI 0.101", "https://example.com")
    assert id1 != id2


def test_make_finding_id_length() -> None:
    fid = _make_finding_id("title", "url")
    assert len(fid) == 12


# ── apply_scout_results ───────────────────────────────────


def _scout_output(*findings: dict) -> str:
    import json

    data = {"keywords_used": ["test"], "findings": list(findings)}
    return f"```json\n{json.dumps(data)}\n```"


def test_apply_scout_results_injects_high_score(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()
    config.scout_min_relevance_score = 6

    output = _scout_output(
        {
            "title": "Important update",
            "source_url": "https://example.com",
            "relevance_score": 8,
            "summary": "Breaking change in core library.",
            "mutation_direction": "Update the API calls.",
        }
    )

    summary = apply_scout_results(state, output, config, 5)

    assert summary["findings_injected"] == 1
    assert summary["findings_skipped_score"] == 0

    # Should have created a stimulus
    stimuli = list((state.stimuli_dir).glob("*.md"))
    assert len(stimuli) == 1
    content = stimuli[0].read_text()
    assert "Important update" in content
    assert "Breaking change" in content


def test_apply_scout_results_skips_low_score(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()
    config.scout_min_relevance_score = 6

    output = _scout_output(
        {
            "title": "Minor update",
            "relevance_score": 3,
            "summary": "Small fix.",
        }
    )

    summary = apply_scout_results(state, output, config, 5)

    assert summary["findings_injected"] == 0
    assert summary["findings_skipped_score"] == 1

    # No stimulus created
    stimuli = list(state.stimuli_dir.glob("*.md"))
    assert len(stimuli) == 0


def test_apply_scout_results_dedup(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    finding = {
        "id": "fixed-id-001",
        "title": "Important update",
        "relevance_score": 9,
        "summary": "Breaking change.",
    }

    output = _scout_output(finding)
    apply_scout_results(state, output, config, 5)
    summary2 = apply_scout_results(state, output, config, 6)

    assert summary2["findings_skipped_duplicate"] == 1
    assert summary2["findings_injected"] == 0

    # Only one stimulus from first call
    stimuli = list(state.stimuli_dir.glob("*.md"))
    assert len(stimuli) == 1


def test_apply_scout_results_updates_cache(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    output = _scout_output(
        {
            "title": "New finding",
            "relevance_score": 8,
            "summary": "Summary.",
        }
    )

    apply_scout_results(state, output, config, 7)

    cache = state.read_scout()
    assert cache["last_scout_cycle"] == 7
    assert len(cache["findings"]) == 1
    assert cache["findings"][0]["injected_as_stimulus"] is True
    assert cache["findings"][0]["injected_cycle"] == 7


def test_apply_scout_results_no_json(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    summary = apply_scout_results(state, "no json output", config, 1)
    assert summary["findings_found"] == 0
    assert summary["findings_injected"] == 0


def test_apply_scout_results_mixed_scores(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()
    config.scout_min_relevance_score = 6

    output = _scout_output(
        {"title": "High score", "relevance_score": 9, "summary": "Critical."},
        {"title": "Low score", "relevance_score": 2, "summary": "Trivial."},
        {"title": "Border score", "relevance_score": 6, "summary": "Just enough."},
    )

    summary = apply_scout_results(state, output, config, 3)

    assert summary["findings_found"] == 3
    assert summary["findings_injected"] == 2  # score 9 and 6
    assert summary["findings_skipped_score"] == 1  # score 2


# ── state scout I/O ───────────────────────────────────────


def test_state_scout_roundtrip(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    data = {"last_scout_cycle": 5, "findings": [{"id": "abc", "title": "Test"}]}
    state.write_scout(data)
    loaded = state.read_scout()
    assert loaded["last_scout_cycle"] == 5
    assert len(loaded["findings"]) == 1


def test_state_scout_empty(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    cache = state.read_scout()
    assert isinstance(cache, dict)
