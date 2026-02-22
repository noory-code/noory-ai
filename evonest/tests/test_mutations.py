"""Tests for core/mutations.py."""

from __future__ import annotations

import random
from pathlib import Path

from evonest.core.mutations import (
    list_all_adversarials,
    list_all_personas,
    load_adversarials,
    load_personas,
    select_mutation,
    weighted_random_select,
)
from evonest.core.state import ProjectState


def test_list_all_personas(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    personas = list_all_personas(state)
    assert len(personas) >= 15
    # Should include all groups
    groups = {p.get("group") for p in personas}
    assert "tech" in groups
    assert "biz" in groups
    assert "quality" in groups


def test_list_all_adversarials(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    adversarials = list_all_adversarials(state)
    assert len(adversarials) >= 8
    ids = [a["id"] for a in adversarials]
    assert "break-interfaces" in ids


def test_list_all_includes_dynamic(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_dynamic_personas(
        [{"id": "custom-x", "name": "Custom X", "perspective": "X."}]
    )
    personas = list_all_personas(state)
    ids = [p["id"] for p in personas]
    assert "custom-x" in ids
    assert "security-auditor" in ids


def test_load_builtin_personas(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    personas = load_personas(state)
    assert len(personas) >= 15  # 15 built-in (including biz-logic personas)
    ids = [p["id"] for p in personas]
    assert "security-auditor" in ids
    assert "chaos-engineer" in ids
    assert "ecosystem-scanner" in ids
    assert "domain-modeler" in ids
    assert "product-strategist" in ids
    assert "spec-reviewer" in ids


def test_load_builtin_adversarials(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    adversarials = load_adversarials(state)
    assert len(adversarials) >= 8  # 8 built-in
    ids = [a["id"] for a in adversarials]
    assert "break-interfaces" in ids
    assert "corrupt-state" in ids


def test_load_merges_dynamic(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_dynamic_personas(
        [
            {"id": "custom-tester", "name": "Custom Tester", "perspective": "Test stuff."},
        ]
    )
    personas = load_personas(state)
    ids = [p["id"] for p in personas]
    assert "security-auditor" in ids  # built-in
    assert "custom-tester" in ids  # dynamic


def test_load_merges_dynamic_adversarials(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.write_dynamic_adversarials(
        [
            {"id": "custom-adv", "name": "Custom", "challenge": "Do something."},
        ]
    )
    adversarials = load_adversarials(state)
    ids = [a["id"] for a in adversarials]
    assert "break-interfaces" in ids  # built-in
    assert "custom-adv" in ids  # dynamic


def test_weighted_random_select_uniform() -> None:
    items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    stats: dict = {}

    # With no stats, all weights are 1.0, so distribution should be roughly uniform
    counts = {"a": 0, "b": 0, "c": 0}
    random.seed(42)
    for _ in range(3000):
        idx = weighted_random_select(items, stats, "persona_stats")
        counts[items[idx]["id"]] += 1

    # Each should get roughly 1000. Allow wide margin.
    for c in counts.values():
        assert 500 < c < 1500


def test_weighted_random_select_weighted() -> None:
    items = [{"id": "high"}, {"id": "low"}]
    stats = {
        "persona_stats": {
            "high": {"weight": 3.0},
            "low": {"weight": 0.2},
        }
    }

    counts = {"high": 0, "low": 0}
    random.seed(42)
    for _ in range(3000):
        idx = weighted_random_select(items, stats, "persona_stats")
        counts[items[idx]["id"]] += 1

    # "high" should dominate (3.0 / 3.2 = ~94%)
    assert counts["high"] > counts["low"] * 5


def test_weighted_random_select_empty() -> None:
    assert weighted_random_select([], {}, "persona_stats") == 0


def test_select_mutation_returns_persona(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    random.seed(42)
    mutation = select_mutation(state, adversarial_probability=0.0)

    assert mutation["persona_id"]
    assert mutation["persona_name"]
    assert mutation["persona_text"]
    assert mutation["adversarial_id"] is None
    assert mutation["adversarial_section"] == ""


def test_select_mutation_with_adversarial(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    # Force adversarial (100% probability)
    random.seed(42)
    mutation = select_mutation(state, adversarial_probability=1.0)

    assert mutation["adversarial_id"] is not None
    assert mutation["adversarial_name"]
    assert "Adversarial Challenge" in mutation["adversarial_section"]


def test_select_mutation_consumes_stimuli(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.add_stimulus("Focus on auth module")

    mutation = select_mutation(state, adversarial_probability=0.0)
    assert "External Stimuli" in mutation["stimuli_section"]
    assert "Focus on auth module" in mutation["stimuli_section"]

    # Stimuli should be consumed (moved to .processed/)
    assert state.consume_stimuli() == []


def test_select_mutation_consumes_decisions(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    state.add_decision("Prioritize security fixes")

    mutation = select_mutation(state, adversarial_probability=0.0)
    assert "Human Decisions" in mutation["decisions_section"]
    assert "Prioritize security fixes" in mutation["decisions_section"]

    # Decisions should be consumed (deleted)
    assert state.consume_decisions() == []


def test_select_mutation_no_stimuli_or_decisions(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    mutation = select_mutation(state, adversarial_probability=0.0)
    assert mutation["stimuli_section"] == ""
    assert mutation["decisions_section"] == ""


# --- disabled_ids filtering ---


def test_load_personas_disabled_ids(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    all_personas = load_personas(state)
    assert any(p["id"] == "security-auditor" for p in all_personas)

    filtered = load_personas(state, disabled_ids=["security-auditor"])
    ids = [p["id"] for p in filtered]
    assert "security-auditor" not in ids
    assert len(filtered) == len(all_personas) - 1


def test_load_adversarials_disabled_ids(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    all_adv = load_adversarials(state)
    assert any(a["id"] == "break-interfaces" for a in all_adv)

    filtered = load_adversarials(state, disabled_ids=["break-interfaces"])
    ids = [a["id"] for a in filtered]
    assert "break-interfaces" not in ids
    assert len(filtered) == len(all_adv) - 1


def test_select_mutation_respects_disabled_personas(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)

    class FakeConfig:
        active_groups: list[str] = []
        disabled_personas = ["security-auditor", "chaos-engineer"]
        disabled_adversarials: list[str] = []

    random.seed(42)
    for _ in range(20):
        mutation = select_mutation(
            state, adversarial_probability=0.0, config=FakeConfig()
        )
        assert mutation["persona_id"] not in ("security-auditor", "chaos-engineer")


def test_forced_persona_ignores_disabled(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)

    class FakeConfig:
        active_groups: list[str] = []
        disabled_personas = ["security-auditor"]
        disabled_adversarials: list[str] = []

    # Even though security-auditor is disabled, forcing it via persona_id works
    mutation = select_mutation(
        state,
        adversarial_probability=0.0,
        config=FakeConfig(),
        persona_id="security-auditor",
    )
    assert mutation["persona_id"] == "security-auditor"
