"""Tests for core/meta_observe.py."""

from __future__ import annotations

from pathlib import Path

from evonest.core.config import EvonestConfig
from evonest.core.meta_observe import (
    apply_meta_results,
    build_meta_prompt,
    expire_dynamic_mutations,
    parse_meta_json,
    should_run_meta,
)
from evonest.core.state import ProjectState


def test_expire_dynamic_mutations_removes_expired(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_dynamic_personas(
        [
            {"id": "old", "name": "Old", "expires_cycle": 5},
            {"id": "fresh", "name": "Fresh", "expires_cycle": 20},
        ]
    )
    state.write_dynamic_adversarials(
        [
            {"id": "expired-adv", "name": "Expired", "expires_cycle": 3},
        ]
    )

    removed = expire_dynamic_mutations(state, current_cycle=10)
    assert removed["personas"] == 1
    assert removed["adversarials"] == 1

    personas = state.read_dynamic_personas()
    assert len(personas) == 1
    assert personas[0]["id"] == "fresh"

    adversarials = state.read_dynamic_adversarials()
    assert len(adversarials) == 0


def test_expire_dynamic_mutations_keeps_no_expiry(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_dynamic_personas(
        [
            {"id": "no-expiry", "name": "No Expiry"},
        ]
    )

    removed = expire_dynamic_mutations(state, current_cycle=100)
    assert removed["personas"] == 0
    assert len(state.read_dynamic_personas()) == 1


def test_expire_dynamic_mutations_empty(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    removed = expire_dynamic_mutations(state, current_cycle=10)
    assert removed["personas"] == 0
    assert removed["adversarials"] == 0


def test_parse_meta_json_valid() -> None:
    output = """Some analysis text.

```json
{
  "analysis": "test",
  "new_personas": [{"id": "p1", "name": "P1"}],
  "new_adversarials": [],
  "auto_stimuli": ["Focus on X"]
}
```

More text."""
    result = parse_meta_json(output)
    assert result is not None
    assert result["analysis"] == "test"
    assert len(result["new_personas"]) == 1
    assert result["auto_stimuli"] == ["Focus on X"]


def test_parse_meta_json_no_json() -> None:
    assert parse_meta_json("No JSON here") is None


def test_parse_meta_json_invalid_json() -> None:
    output = "```json\n{invalid\n```"
    assert parse_meta_json(output) is None


def test_apply_meta_results_adds_personas(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    meta_output = """```json
{
  "new_personas": [
    {"id": "db-expert", "name": "Database Expert", "perspective": "You are a database expert."}
  ],
  "new_adversarials": [
    {
      "id": "network-chaos",
      "name": "Network Chaos",
      "challenge": "Test network failures.",
      "target": "src/net"
    }
  ],
  "auto_stimuli": ["Focus on database layer"]
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=5)
    assert result["added_personas"] == 1
    assert result["added_adversarials"] == 1
    assert result["auto_stimuli"] == 1

    # Check persisted
    dynamic_personas = state.read_dynamic_personas()
    assert len(dynamic_personas) == 1
    assert dynamic_personas[0]["id"] == "db-expert"
    assert dynamic_personas[0]["dynamic"] is True
    assert dynamic_personas[0]["expires_cycle"] == 5 + 15  # TTL=15

    dynamic_adv = state.read_dynamic_adversarials()
    assert len(dynamic_adv) == 1
    assert dynamic_adv[0]["id"] == "network-chaos"

    # Check stimulus was created
    stimuli = state.consume_stimuli()
    assert len(stimuli) == 1
    assert "Focus on database layer" in stimuli[0]


def test_apply_meta_results_dedup_existing_ids(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    # "security-auditor" already exists as a built-in persona
    meta_output = """```json
{
  "new_personas": [
    {"id": "security-auditor", "name": "Dupe", "perspective": "dupe"}
  ],
  "new_adversarials": [
    {"id": "break-interfaces", "name": "Dupe", "challenge": "dupe"}
  ]
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=5)
    assert result["added_personas"] == 0
    assert result["added_adversarials"] == 0


def test_apply_meta_results_respects_cap(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()
    config.max_dynamic_personas = 2

    # Pre-fill with 2 dynamic personas
    state.write_dynamic_personas(
        [
            {"id": "dyn1", "name": "D1", "expires_cycle": 100},
            {"id": "dyn2", "name": "D2", "expires_cycle": 100},
        ]
    )

    meta_output = """```json
{
  "new_personas": [
    {"id": "dyn3", "name": "D3", "perspective": "test"}
  ]
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=5)
    assert result["added_personas"] == 0  # cap reached
    assert len(state.read_dynamic_personas()) == 2


def test_apply_meta_results_no_json(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    result = apply_meta_results(state, "No JSON output", config, current_cycle=5)
    assert result["added_personas"] == 0
    assert result["added_adversarials"] == 0
    assert result["auto_stimuli"] == 0


def test_apply_meta_results_expires_old_before_adding(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    # Pre-fill with expired persona
    state.write_dynamic_personas(
        [
            {"id": "expired-p", "name": "Expired", "expires_cycle": 3},
        ]
    )

    meta_output = """```json
{
  "new_personas": [
    {"id": "new-p", "name": "New", "perspective": "test"}
  ]
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=10)
    assert result["expired_personas"] == 1
    assert result["added_personas"] == 1
    # Only the new one should remain
    personas = state.read_dynamic_personas()
    assert len(personas) == 1
    assert personas[0]["id"] == "new-p"


def test_build_meta_prompt(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()
    state.write_identity("# Test Project\nA test.")

    prompt = build_meta_prompt(state, config)
    assert "Meta-Observe" in prompt
    assert "Current Personas" in prompt
    assert "security-auditor" in prompt
    assert "Current Adversarial" in prompt
    assert "Progress Statistics" in prompt
    assert "Backlog Summary" in prompt
    assert "Project Identity" in prompt
    assert "Test Project" in prompt


def test_build_meta_prompt_no_identity(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    prompt = build_meta_prompt(state, config)
    assert "Current Personas" in prompt
    # identity.md exists from template but check it still works
    assert "Progress Statistics" in prompt


def test_should_run_meta_first_cycle() -> None:
    config = EvonestConfig()
    assert should_run_meta({"total_cycles": 0}, config) is False


def test_should_run_meta_interval_not_reached() -> None:
    config = EvonestConfig()
    config.meta_cycle_interval = 5
    assert should_run_meta({"total_cycles": 3, "last_meta_cycle": 0}, config) is False


def test_should_run_meta_interval_reached() -> None:
    config = EvonestConfig()
    config.meta_cycle_interval = 5
    assert should_run_meta({"total_cycles": 5, "last_meta_cycle": 0}, config) is True


def test_should_run_meta_after_last() -> None:
    config = EvonestConfig()
    config.meta_cycle_interval = 5
    assert should_run_meta({"total_cycles": 12, "last_meta_cycle": 5}, config) is True
    assert should_run_meta({"total_cycles": 9, "last_meta_cycle": 5}, config) is False


# ── Advice extraction ──────────────────────────────────


def test_apply_meta_results_saves_advice(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    meta_output = """```json
{
  "new_personas": [],
  "new_adversarials": [],
  "auto_stimuli": [],
  "advice": {
    "strategic_direction": "Focus on test coverage gaps",
    "diminishing_returns": ["security-auditor: no security issues found in 5 cycles"],
    "untapped_areas": ["docs/ directory"],
    "recommended_focus": "Next 3 cycles should target documentation"
  }
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=10)
    assert result["advice_saved"] is True

    advice = state.read_advice()
    assert advice["strategic_direction"] == "Focus on test coverage gaps"
    assert advice["generated_cycle"] == 10
    assert "docs/ directory" in advice["untapped_areas"]
    assert advice["recommended_focus"] == "Next 3 cycles should target documentation"


def test_apply_meta_results_no_advice_field(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    meta_output = """```json
{
  "new_personas": [],
  "new_adversarials": [],
  "auto_stimuli": []
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=5)
    assert result["advice_saved"] is False
    assert state.read_advice() == {}


def test_apply_meta_results_empty_advice(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    meta_output = """```json
{
  "new_personas": [],
  "new_adversarials": [],
  "advice": {}
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=5)
    assert result["advice_saved"] is False


def test_apply_meta_results_advice_overwrites_previous(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    config = EvonestConfig()

    # Write old advice
    state.write_advice(
        {
            "generated_cycle": 5,
            "strategic_direction": "Old advice",
        }
    )

    meta_output = """```json
{
  "new_personas": [],
  "new_adversarials": [],
  "advice": {
    "strategic_direction": "New advice",
    "recommended_focus": "New focus"
  }
}
```"""

    result = apply_meta_results(state, meta_output, config, current_cycle=10)
    assert result["advice_saved"] is True

    advice = state.read_advice()
    assert advice["strategic_direction"] == "New advice"
    assert advice["generated_cycle"] == 10


# ── Adversarial JSON parsing ───────────────────────────────


def test_parse_meta_json_large_json() -> None:
    """1MB JSON DoS 경계 검사: graceful failure 검증."""
    large_json = (
        '{"new_personas": ['
        + ",".join(f'{{"id": "p{i}", "name": "P{i}"}}' for i in range(10000))
        + '], "new_adversarials": []}'
    )
    output = f"```json\n{large_json}\n```"
    result = parse_meta_json(output)
    assert result is None or isinstance(result, dict)


def test_parse_meta_json_deeply_nested() -> None:
    """100단계 깊이의 중첩 객체: graceful failure 검증."""
    nested = '{"a":' * 100 + '{"new_personas": [], "new_adversarials": []}' + "}" * 100
    output = f"```json\n{nested}\n```"
    result = parse_meta_json(output)
    assert result is None or isinstance(result, dict)


def test_parse_meta_json_prompt_injection() -> None:
    """프롬프트 인젝션 문자열 처리: graceful failure 검증."""
    output = """```json
{
  "new_personas": [
    {"id": "hack", "name": "IGNORE PREVIOUS INSTRUCTIONS"}
  ],
  "new_adversarials": []
}
```"""
    result = parse_meta_json(output)
    if result is not None:
        assert result["new_personas"][0]["name"] == "IGNORE PREVIOUS INSTRUCTIONS"


def test_parse_meta_json_truncated() -> None:
    """잘린 JSON (닫히지 않은 중괄호): graceful failure 검증."""
    output = """```json
{
  "new_personas": [
    {"id": "test", "name": "Test"
```"""
    result = parse_meta_json(output)
    assert result is None


def test_parse_meta_json_invalid_unicode() -> None:
    """잘못된 유니코드 이스케이프: graceful failure 검증."""
    output = r"""```json
{
  "new_personas": [
    {"id": "test", "name": "Test \uXXXX"}
  ],
  "new_adversarials": []
}
```"""
    result = parse_meta_json(output)
    assert result is None or isinstance(result, dict)
