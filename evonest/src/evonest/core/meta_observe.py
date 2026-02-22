"""Meta-observation — dynamic mutation generation and TTL management.

Analyzes evolution performance to generate project-specific personas
and adversarial challenges. Dynamic mutations are stored in
.evonest/dynamic-*.json with expiration cycles (TTL).
"""

from __future__ import annotations

import json
import re
from importlib import resources
from typing import Any

from evonest.core.config import EvonestConfig
from evonest.core.history import build_history_summary
from evonest.core.mutations import load_adversarials, load_personas
from evonest.core.progress import build_convergence_context
from evonest.core.state import ProjectState


def expire_dynamic_mutations(state: ProjectState, current_cycle: int) -> dict[str, int]:
    """Remove expired dynamic mutations. Returns counts of removed items."""
    removed = {"personas": 0, "adversarials": 0}

    # Expire personas
    personas = state.read_dynamic_personas()
    kept = [p for p in personas if p.get("expires_cycle", 999999) > current_cycle]
    removed["personas"] = len(personas) - len(kept)
    if removed["personas"] > 0:
        state.write_dynamic_personas(kept)

    # Expire adversarials
    adversarials = state.read_dynamic_adversarials()
    kept = [a for a in adversarials if a.get("expires_cycle", 999999) > current_cycle]
    removed["adversarials"] = len(adversarials) - len(kept)
    if removed["adversarials"] > 0:
        state.write_dynamic_adversarials(kept)

    return removed


def build_meta_prompt(state: ProjectState, config: EvonestConfig) -> str:
    """Build the full meta-observe prompt from template + context."""
    # Load the prompt template
    ref = resources.files("evonest") / "prompts" / "meta_observe.md"
    try:
        template = ref.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        template = ""

    # Current personas/adversarials lists
    personas = load_personas(state)
    adversarials = load_adversarials(state)

    persona_list = "\n".join(f"- {p.get('id')}: {p.get('name')}" for p in personas) or "none"
    adversarial_list = (
        "\n".join(f"- {a.get('id')}: {a.get('name')}" for a in adversarials) or "none"
    )

    # Progress summary
    progress = state.read_progress()
    progress_summary = json.dumps(
        {
            "total_cycles": progress.get("total_cycles", 0),
            "total_successes": progress.get("total_successes", 0),
            "total_failures": progress.get("total_failures", 0),
            "persona_stats": {
                k: {
                    "uses": v.get("uses", 0),
                    "successes": v.get("successes", 0),
                    "weight": v.get("weight", 1.0),
                }
                for k, v in progress.get("persona_stats", {}).items()
            },
            "convergence_flags": progress.get("convergence_flags", {}),
        },
        indent=2,
    )

    # Backlog summary
    backlog = state.read_backlog()
    items = backlog.get("items", [])
    backlog_summary = json.dumps(
        {
            "total_items": len(items),
            "pending": sum(1 for i in items if i.get("status") == "pending"),
            "stale": sum(1 for i in items if i.get("status") == "stale"),
            "categories": sorted(set(i.get("category", "general") for i in items)),
        },
        indent=2,
    )

    # History + convergence
    history_summary = build_history_summary(state, count=10)
    convergence_info = build_convergence_context(state)

    # Assemble
    parts = [
        template,
        "\n---\n",
        f"## Current Personas\n{persona_list}",
        f"\n## Current Adversarial Challenges\n{adversarial_list}",
        f"\n## Progress Statistics\n```json\n{progress_summary}\n```",
        f"\n## Backlog Summary\n```json\n{backlog_summary}\n```",
    ]

    if history_summary:
        parts.append(f"\n{history_summary}")
    if convergence_info:
        parts.append(f"\n{convergence_info}")

    # Identity
    identity = state.read_identity()
    if identity:
        parts.append(f"\n---\n\n## Project Identity\n\n{identity}")

    return "\n".join(parts)


def parse_meta_json(output: str) -> dict | None:  # type: ignore[type-arg]
    """Extract JSON from meta-observe output (inside ```json ... ``` block)."""
    match = re.search(r"```json\s*\n(.*?)```", output, re.DOTALL)
    if not match:
        return None
    try:
        data: dict = json.loads(match.group(1))  # type: ignore[type-arg]
        return data
    except (json.JSONDecodeError, ValueError):
        return None


def apply_meta_results(
    state: ProjectState,
    meta_output: str,
    config: EvonestConfig,
    current_cycle: int,
) -> dict[str, Any]:
    """Apply meta-observe results: add new dynamic mutations, generate auto-stimuli,
    and save strategic advice.

    Returns a summary dict of what was applied.
    """
    result = {
        "expired_personas": 0,
        "expired_adversarials": 0,
        "added_personas": 0,
        "added_adversarials": 0,
        "auto_stimuli": 0,
        "advice_saved": False,
    }

    # 1. Expire old dynamic mutations
    expired = expire_dynamic_mutations(state, current_cycle)
    result["expired_personas"] = expired["personas"]
    result["expired_adversarials"] = expired["adversarials"]

    # 2. Parse the meta JSON output
    meta_json = parse_meta_json(meta_output)
    if meta_json is None:
        state.log("  Meta-observe: JSON parse failed, skipping application")
        return result

    expires_cycle = current_cycle + config.dynamic_mutation_ttl_cycles

    # 3. Add new personas (up to cap)
    current_dynamic = state.read_dynamic_personas()
    existing_ids = {p.get("id") for p in load_personas(state)}

    for p in meta_json.get("new_personas", []):
        if len(current_dynamic) >= config.max_dynamic_personas:
            break
        pid = p.get("id")
        if not pid or pid in existing_ids:
            continue
        p["dynamic"] = True
        p["expires_cycle"] = expires_cycle
        current_dynamic.append(p)
        existing_ids.add(pid)
        result["added_personas"] += 1

    if result["added_personas"] > 0:
        state.write_dynamic_personas(current_dynamic)

    # 4. Add new adversarials (up to cap)
    current_dyn_adv = state.read_dynamic_adversarials()
    existing_adv_ids = {a.get("id") for a in load_adversarials(state)}

    for a in meta_json.get("new_adversarials", []):
        if len(current_dyn_adv) >= config.max_dynamic_adversarials:
            break
        aid = a.get("id")
        if not aid or aid in existing_adv_ids:
            continue
        a["dynamic"] = True
        a["expires_cycle"] = expires_cycle
        current_dyn_adv.append(a)
        existing_adv_ids.add(aid)
        result["added_adversarials"] += 1

    if result["added_adversarials"] > 0:
        state.write_dynamic_adversarials(current_dyn_adv)

    # 5. Generate auto-stimuli
    for stimulus_text in meta_json.get("auto_stimuli", []):
        if not stimulus_text:
            continue
        content = f"# Auto-Generated Stimulus (Meta-Observe)\n\n{stimulus_text}"
        state.add_stimulus(content)
        result["auto_stimuli"] += 1

    # 6. Save strategic advice (guru wisdom from accumulated experience)
    advice_data = meta_json.get("advice")
    if isinstance(advice_data, dict) and advice_data.get("strategic_direction"):
        advice_data["generated_cycle"] = current_cycle
        state.write_advice(advice_data)
        result["advice_saved"] = True

    return result


def should_run_meta(progress: dict, config: EvonestConfig) -> bool:  # type: ignore[type-arg]
    """Check if meta-observe should run this cycle."""
    total_cycles: int = progress.get("total_cycles", 0)
    if total_cycles == 0:
        return False
    last_meta: int = progress.get("last_meta_cycle", 0)
    return bool((total_cycles - last_meta) >= config.meta_cycle_interval)
