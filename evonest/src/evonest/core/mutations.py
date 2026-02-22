"""Mutation selection — merge built-in + project extensions, weighted random.

Built-in mutations live in the package's mutations/ directory (read-only).
Project-specific dynamic mutations live in .evonest/dynamic-*.json.
At runtime, both are merged and weighted random selection picks one.
"""

from __future__ import annotations

import json
import random
from importlib import resources
from typing import Any

from evonest.core.state import ProjectState


def _load_builtin(filename: str) -> list[dict[str, Any]]:
    """Load a built-in mutation file from the package."""
    ref = resources.files("evonest") / "mutations" / filename
    try:
        data: list[dict] = json.loads(ref.read_text(encoding="utf-8"))  # type: ignore[type-arg]
        return data
    except (FileNotFoundError, OSError):
        return []


def list_all_personas(state: ProjectState) -> list[dict[str, Any]]:
    """Return all personas (built-in + dynamic) without any filtering."""
    return _load_builtin("personas.json") + state.read_dynamic_personas()


def list_all_adversarials(state: ProjectState) -> list[dict[str, Any]]:
    """Return all adversarials (built-in + dynamic) without any filtering."""
    return _load_builtin("adversarial.json") + state.read_dynamic_adversarials()


def load_personas(
    state: ProjectState,
    active_groups: list[str] | None = None,
    disabled_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Merge built-in + dynamic personas, optionally filtered by group and disabled list."""
    all_personas = _load_builtin("personas.json") + state.read_dynamic_personas()
    if active_groups:
        filtered = [p for p in all_personas if p.get("group") in active_groups]
        all_personas = filtered if filtered else all_personas
    if disabled_ids:
        all_personas = [p for p in all_personas if p.get("id") not in disabled_ids]
    return all_personas


def load_adversarials(
    state: ProjectState,
    disabled_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Merge built-in + dynamic adversarials, optionally filtered by disabled list."""
    all_adv = _load_builtin("adversarial.json") + state.read_dynamic_adversarials()
    if disabled_ids:
        all_adv = [a for a in all_adv if a.get("id") not in disabled_ids]
    return all_adv


def weighted_random_select(
    items: list[dict[str, Any]],
    stats: dict[str, Any],
    stats_key: str,
) -> int:
    """Select a random index from items using weight-based probability.

    Args:
        items: List of mutation dicts (each with 'id').
        stats: The progress dict (or sub-dict) containing per-id stats.
        stats_key: Key in progress to look up stats ('persona_stats' or 'adversarial_stats').

    Returns:
        Selected index.
    """
    if not items:
        return 0

    stat_bucket = stats.get(stats_key, {})
    weights = []
    for item in items:
        item_id = item.get("id", "")
        item_stats = stat_bucket.get(item_id, {})
        w = item_stats.get("weight", 1.0)
        weights.append(w)

    total = sum(weights)
    if total <= 0:
        return random.randrange(len(items))

    rand_val = random.uniform(0, total)
    cumulative = 0.0
    for i, w in enumerate(weights):
        cumulative += w
        if rand_val < cumulative:
            return i

    return len(items) - 1


def select_mutation(
    state: ProjectState,
    adversarial_probability: float = 0.2,
    config: object = None,
    *,
    persona_id: str | None = None,
    adversarial_id: str | None = None,
    group: str | None = None,
) -> dict[str, Any]:
    """Select persona + optional adversarial + stimuli for a cycle.

    Args:
        persona_id: If set, force this persona instead of random selection.
        adversarial_id: If set, force this adversarial (or "none" to disable).
        group: If set, restrict random persona selection to this group.
               Overrides config.active_groups.

    Returns a dict with:
        persona_id, persona_name, persona_text,
        adversarial_id, adversarial_name, adversarial_section,
        stimuli_section, decisions_section
    """
    progress = state.read_progress()

    # 1. Persona selection (forced or weighted random)
    active_groups: list[str] | None = None
    if group:
        active_groups = [group]
    elif config is not None:
        cfg_groups = getattr(config, "active_groups", None)
        if cfg_groups:
            active_groups = cfg_groups
    disabled_personas: list[str] = getattr(config, "disabled_personas", None) or []
    disabled_adversarials: list[str] = getattr(config, "disabled_adversarials", None) or []
    personas = load_personas(state, active_groups, disabled_personas or None)
    selected_persona = None
    if persona_id:
        # forced persona_id: search full pool (ignore group filter and disabled list)
        all_personas = load_personas(state)
        selected_persona = next((p for p in all_personas if p.get("id") == persona_id), None)
    if selected_persona is None and personas:
        idx = weighted_random_select(personas, progress, "persona_stats")
        selected_persona = personas[idx]
    if selected_persona:
        persona_id = selected_persona.get("id", "generalist")
        persona_name = selected_persona.get("name", "Generalist")
        persona_text = selected_persona.get(
            "perspective", "You are a generalist software engineer."
        )
    else:
        persona_id = "generalist"
        persona_name = "Generalist"
        persona_text = (
            "You are a generalist software engineer. Look for the highest-impact improvement."
        )

    # 2. Adversarial challenge (forced, disabled, or probability-based weighted)
    selected_adversarial_id = None
    adversarial_name = None
    adversarial_section = ""

    adversarials = load_adversarials(state, disabled_adversarials or None)
    if adversarial_id == "none":
        pass  # explicitly disabled
    elif adversarial_id:
        adv = next((a for a in adversarials if a.get("id") == adversarial_id), None)
        if adv:
            selected_adversarial_id = adv.get("id")
            adversarial_name = adv.get("name", "")
            challenge = adv.get("challenge", "")
            target = adv.get("target", ".")
            adversarial_section = (
                f"## Adversarial Challenge: {adversarial_name}\n\n"
                f"{challenge}\n\n"
                f"Target directory: {target}"
            )
    elif adversarials and random.random() < adversarial_probability:
        adv_idx = weighted_random_select(adversarials, progress, "adversarial_stats")
        adv = adversarials[adv_idx]
        selected_adversarial_id = adv.get("id")
        adversarial_name = adv.get("name", "")
        challenge = adv.get("challenge", "")
        target = adv.get("target", ".")
        adversarial_section = (
            f"## Adversarial Challenge: {adversarial_name}\n\n"
            f"{challenge}\n\n"
            f"Target directory: {target}"
        )
    adversarial_id = selected_adversarial_id

    # 3. External stimuli
    stimuli = state.consume_stimuli()
    stimuli_section = ""
    if stimuli:
        parts = []
        for s in stimuli:
            parts.append(f"---\n{s}")
        stimuli_section = "## External Stimuli\n" + "\n".join(parts)

    # 4. Human decisions
    decisions = state.consume_decisions()
    decisions_section = ""
    if decisions:
        parts = []
        for d in decisions:
            parts.append(f"---\n{d}")
        decisions_section = "## Human Decisions\n" + "\n".join(parts)

    return {
        "persona_id": persona_id,
        "persona_name": persona_name,
        "persona_text": persona_text,
        "adversarial_id": adversarial_id,
        "adversarial_name": adversarial_name,
        "adversarial_section": adversarial_section,
        "stimuli_section": stimuli_section,
        "decisions_section": decisions_section,
    }
