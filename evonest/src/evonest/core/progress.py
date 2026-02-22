"""Progress tracking and weight calculation.

Tracks per-persona and per-adversarial statistics, area touch counts,
convergence flags. Recalculates selection weights after each cycle.

Weight formula: 1.0 + (success_rate * 0.5) - (failure_rate * 0.3) + recency_bonus
  - recency_bonus = 0.3 if unused for 3+ cycles
  - clamped to [0.2, 3.0]
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evonest.core.state import ProjectState

WEIGHT_MIN = 0.2
WEIGHT_MAX = 3.0
RECENCY_THRESHOLD = 3
RECENCY_BONUS = 0.3
CONVERGENCE_THRESHOLD = 3


def calculate_weight(
    uses: int, successes: int, failures: int, last_used_cycle: int, current_cycle: int
) -> float:
    """Calculate selection weight for a persona or adversarial."""
    if uses == 0:
        return 1.0
    success_rate = successes / uses
    failure_rate = failures / uses
    recency = RECENCY_BONUS if (current_cycle - last_used_cycle) >= RECENCY_THRESHOLD else 0.0
    weight = 1.0 + (success_rate * 0.5) - (failure_rate * 0.3) + recency
    return max(WEIGHT_MIN, min(WEIGHT_MAX, round(weight, 2)))


def update_progress(
    state: ProjectState,
    success: bool,
    persona_id: str,
    adversarial_id: str | None,
    changed_files: list[str],
) -> dict[str, Any]:
    """Update progress after a cycle completes. Returns updated progress dict."""
    progress = state.read_progress()

    # Basic counters
    progress["total_cycles"] = progress.get("total_cycles", 0) + 1
    if success:
        progress["total_successes"] = progress.get("total_successes", 0) + 1
    else:
        progress["total_failures"] = progress.get("total_failures", 0) + 1
    progress["last_run"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if success:
        progress["last_improvement"] = progress["last_run"]

    total_cycles = progress["total_cycles"]

    # Persona stats
    persona_stats = progress.setdefault("persona_stats", {})
    ps = persona_stats.setdefault(persona_id, {})
    ps["uses"] = ps.get("uses", 0) + 1
    if success:
        ps["successes"] = ps.get("successes", 0) + 1
    else:
        ps["failures"] = ps.get("failures", 0) + 1
    ps["last_used_cycle"] = total_cycles

    # Adversarial stats
    if adversarial_id:
        adv_stats = progress.setdefault("adversarial_stats", {})
        ads = adv_stats.setdefault(adversarial_id, {})
        ads["uses"] = ads.get("uses", 0) + 1
        if success:
            ads["successes"] = ads.get("successes", 0) + 1
        else:
            ads["failures"] = ads.get("failures", 0) + 1
        ads["last_used_cycle"] = total_cycles

    # Activation metrics (local only, no external telemetry)
    if success:
        activation = progress.setdefault("activation", {})
        if not activation.get("first_success_at"):
            activation["first_success_at"] = progress["last_run"]
        activation["successful_commits"] = activation.get("successful_commits", 0) + 1

    # Area touch counts + convergence
    if success and changed_files:
        area_counts = progress.setdefault("area_touch_counts", {})
        convergence = progress.setdefault("convergence_flags", {})
        for file_path in changed_files:
            if not file_path:
                continue
            area = file_path.split("/")[0]
            area_counts[area] = area_counts.get(area, 0) + 1
            if area_counts[area] >= CONVERGENCE_THRESHOLD:
                convergence[area] = True

    state.write_progress(progress)
    return progress


def recalculate_weights(
    state: ProjectState,
    persona_ids: list[str],
    adversarial_ids: list[str],
) -> dict[str, Any]:
    """Recalculate all weights based on current stats. Returns updated progress."""
    progress = state.read_progress()
    total_cycles = progress.get("total_cycles", 0)
    if total_cycles == 0:
        return progress

    # Persona weights
    persona_stats = progress.get("persona_stats", {})
    for pid in persona_ids:
        ps = persona_stats.get(pid, {})
        ps["weight"] = calculate_weight(
            uses=ps.get("uses", 0),
            successes=ps.get("successes", 0),
            failures=ps.get("failures", 0),
            last_used_cycle=ps.get("last_used_cycle", 0),
            current_cycle=total_cycles,
        )
        persona_stats[pid] = ps

    # Adversarial weights
    adv_stats = progress.get("adversarial_stats", {})
    for aid in adversarial_ids:
        ads = adv_stats.get(aid, {})
        ads["weight"] = calculate_weight(
            uses=ads.get("uses", 0),
            successes=ads.get("successes", 0),
            failures=ads.get("failures", 0),
            last_used_cycle=ads.get("last_used_cycle", 0),
            current_cycle=total_cycles,
        )
        adv_stats[aid] = ads

    progress["persona_stats"] = persona_stats
    progress["adversarial_stats"] = adv_stats
    state.write_progress(progress)
    return progress


def get_progress_report(project: str | Path) -> str:
    """Return a detailed progress report as formatted text."""
    state = ProjectState(project)
    progress = state.read_progress()

    total = progress.get("total_cycles", 0)
    successes = progress.get("total_successes", 0)
    rate = round(successes / total * 100) if total > 0 else 0

    lines = [
        f"Total cycles: {total}",
        f"Success rate: {rate}% ({successes}/{total})",
        f"Last run: {progress.get('last_run', 'never')}",
        f"Last improvement: {progress.get('last_improvement', 'never')}",
        "",
    ]

    # Persona weights
    persona_stats = progress.get("persona_stats", {})
    if persona_stats:
        lines.append("Persona weights:")
        for pid, ps in sorted(
            persona_stats.items(), key=lambda x: x[1].get("weight", 1.0), reverse=True
        ):
            w = ps.get("weight", 1.0)
            u = ps.get("uses", 0)
            s = ps.get("successes", 0)
            f = ps.get("failures", 0)
            lines.append(f"  {pid}: weight={w:.2f} (uses={u}, success={s}, fail={f})")

    # Adversarial weights
    adv_stats = progress.get("adversarial_stats", {})
    if adv_stats:
        lines.append("")
        lines.append("Adversarial weights:")
        for aid, ads in sorted(
            adv_stats.items(), key=lambda x: x[1].get("weight", 1.0), reverse=True
        ):
            w = ads.get("weight", 1.0)
            u = ads.get("uses", 0)
            lines.append(f"  {aid}: weight={w:.2f} (uses={u})")

    # Area touches
    area_counts = progress.get("area_touch_counts", {})
    if area_counts:
        lines.append("")
        lines.append("Area touch counts:")
        for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
            flag = " [CONVERGED]" if progress.get("convergence_flags", {}).get(area) else ""
            lines.append(f"  {area}: {count}{flag}")

    return "\n".join(lines)


def build_convergence_context(state: ProjectState) -> str:
    """Build convergence warning text for phase prompts."""
    progress = state.read_progress()
    flags = progress.get("convergence_flags", {})
    area_counts = progress.get("area_touch_counts", {})

    converged = {k: v for k, v in flags.items() if v}
    if not converged:
        return ""

    lines = [
        "## Convergence Warning",
        "",
        "The following areas have been touched 3+ times. "
        "Consider focusing elsewhere to avoid diminishing returns:",
        "",
    ]
    for area in sorted(converged):
        count = area_counts.get(area, 0)
        lines.append(f"- **{area}**: touched {count} times")

    return "\n".join(lines)
