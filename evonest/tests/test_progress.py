"""Tests for core/progress.py."""

from __future__ import annotations

from pathlib import Path

from evonest.core.progress import (
    build_convergence_context,
    calculate_weight,
    get_progress_report,
    recalculate_weights,
    update_progress,
)
from evonest.core.state import ProjectState


def test_weight_unused() -> None:
    assert calculate_weight(0, 0, 0, 0, 10) == 1.0


def test_weight_all_success() -> None:
    w = calculate_weight(10, 10, 0, 10, 10)
    assert w == 1.5  # 1.0 + (1.0 * 0.5) - 0 + 0


def test_weight_all_failure() -> None:
    w = calculate_weight(10, 0, 10, 10, 10)
    assert w == 0.7  # 1.0 + 0 - (1.0 * 0.3) + 0


def test_weight_recency_bonus() -> None:
    w = calculate_weight(5, 3, 2, 1, 10)
    # success_rate = 0.6, failure_rate = 0.4
    # 1.0 + (0.6*0.5) - (0.4*0.3) + 0.3 = 1.48
    assert w == 1.48


def test_weight_no_recency_bonus() -> None:
    w = calculate_weight(5, 3, 2, 9, 10)
    # 1.0 + 0.3 - 0.12 + 0 = 1.18
    assert w == 1.18


def test_weight_clamped_min() -> None:
    w = calculate_weight(10, 0, 10, 10, 10)
    assert w >= 0.2


def test_weight_clamped_max() -> None:
    w = calculate_weight(100, 100, 0, 0, 100)
    assert w <= 3.0


def test_update_progress_success(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    progress = update_progress(state, True, "security-auditor", None, ["src/auth.py"])

    assert progress["total_cycles"] == 1
    assert progress["total_successes"] == 1
    assert progress["total_failures"] == 0
    assert progress["persona_stats"]["security-auditor"]["uses"] == 1
    assert progress["persona_stats"]["security-auditor"]["successes"] == 1
    assert progress["area_touch_counts"]["src"] == 1


def test_update_progress_failure(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    progress = update_progress(state, False, "chaos-engineer", "break-interfaces", [])

    assert progress["total_cycles"] == 1
    assert progress["total_failures"] == 1
    assert progress["persona_stats"]["chaos-engineer"]["failures"] == 1
    assert progress["adversarial_stats"]["break-interfaces"]["failures"] == 1


def test_update_progress_convergence(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    for _ in range(3):
        update_progress(state, True, "test", None, ["src/parser.py"])

    progress = state.read_progress()
    assert progress["area_touch_counts"]["src"] == 3
    assert progress["convergence_flags"]["src"] is True


def test_update_progress_adversarial(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    progress = update_progress(state, True, "perf", "scale-100x", ["lib/cache.py"])
    assert "scale-100x" in progress["adversarial_stats"]
    assert progress["adversarial_stats"]["scale-100x"]["successes"] == 1


def test_recalculate_weights(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    update_progress(state, True, "security-auditor", None, [])
    update_progress(state, False, "chaos-engineer", None, [])

    progress = recalculate_weights(state, ["security-auditor", "chaos-engineer"], [])
    assert progress["persona_stats"]["security-auditor"]["weight"] > 1.0
    assert progress["persona_stats"]["chaos-engineer"]["weight"] < 1.0


def test_recalculate_weights_no_cycles(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    progress = recalculate_weights(state, ["test"], [])
    assert progress.get("total_cycles", 0) == 0


def test_get_progress_report(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    update_progress(state, True, "security-auditor", "break-interfaces", ["src/auth.py"])

    report = get_progress_report(tmp_project)
    assert "Total cycles: 1" in report
    assert "security-auditor" in report


def test_get_progress_report_empty(tmp_project: Path) -> None:
    report = get_progress_report(tmp_project)
    assert "Total cycles: 0" in report


def test_build_convergence_context_empty(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    assert build_convergence_context(state) == ""


def test_build_convergence_context(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    for _ in range(3):
        update_progress(state, True, "test", None, ["src/file.py"])

    context = build_convergence_context(state)
    assert "Convergence Warning" in context
    assert "src" in context


# --- Activation metrics ---


def test_activation_first_success_at(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    progress = update_progress(state, True, "test", None, [])

    activation = progress.get("activation", {})
    assert activation.get("first_success_at") is not None


def test_activation_first_success_at_not_overwritten(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    first = update_progress(state, True, "test", None, [])
    first_ts = first["activation"]["first_success_at"]

    second = update_progress(state, True, "test", None, [])
    assert second["activation"]["first_success_at"] == first_ts


def test_activation_successful_commits_increments(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    update_progress(state, True, "test", None, [])
    update_progress(state, True, "test", None, [])
    progress = update_progress(state, True, "test", None, [])

    assert progress["activation"]["successful_commits"] == 3


def test_activation_failure_does_not_count(tmp_project: Path) -> None:
    state = ProjectState(tmp_project)
    update_progress(state, False, "test", None, [])
    update_progress(state, False, "test", None, [])
    progress = state.read_progress()

    activation = progress.get("activation", {})
    assert activation.get("first_success_at") is None
    assert activation.get("successful_commits", 0) == 0
