"""Scout — external search-based mutation generation.

Analyzes project identity to extract keywords, searches externally for
relevant developments, scores findings against project alignment, and
injects high-scoring findings as stimuli for the next evolution cycle.

Results are cached in .evonest/scout.json to prevent duplicate injection.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from evonest.core.config import EvonestConfig
from evonest.core.state import ProjectState


def should_run_scout(progress: dict, config: EvonestConfig) -> bool:  # type: ignore[type-arg]
    """Check if scout should run this cycle."""
    if not config.scout_enabled:
        return False
    total_cycles: int = progress.get("total_cycles", 0)
    if total_cycles == 0:
        return False
    last_scout: int = progress.get("last_scout_cycle", 0)
    return bool((total_cycles - last_scout) >= config.scout_cycle_interval)


def build_scout_prompt(state: ProjectState) -> str:
    """Build the scout prompt from template + project identity."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "scout.md"
    template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

    identity = state.read_identity()

    # Include already-seen finding IDs so Claude can avoid re-reporting them
    scout_cache = state.read_scout()
    seen_findings = scout_cache.get("findings", [])
    seen_ids = [f["id"] for f in seen_findings if f.get("id")]

    parts = [template]

    if identity:
        parts.append(f"\n---\n\n## Project Identity\n\n{identity}")

    if seen_ids:
        parts.append(
            "\n---\n\n## Already Reported Findings (do not repeat)\n\n"
            + "\n".join(f"- {fid}" for fid in seen_ids[-50:])
        )

    return "\n".join(parts)


def parse_scout_json(output: str) -> dict | None:  # type: ignore[type-arg]
    """Extract JSON from scout output (inside ```json ... ``` block)."""
    match = re.search(r"```json\s*\n(.*?)```", output, re.DOTALL)
    if not match:
        return None
    try:
        data: dict = json.loads(match.group(1))  # type: ignore[type-arg]
        return data
    except (json.JSONDecodeError, ValueError):
        return None


def _make_finding_id(title: str, source_url: str = "") -> str:
    """Generate a stable short ID from title + source_url."""
    raw = f"{title}|{source_url}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def apply_scout_results(
    state: ProjectState,
    scout_output: str,
    config: EvonestConfig,
    current_cycle: int,
) -> dict[str, Any]:
    """Apply scout results: inject qualifying findings as stimuli.

    Returns a summary dict of what was applied.
    """
    result = {
        "findings_found": 0,
        "findings_injected": 0,
        "findings_skipped_score": 0,
        "findings_skipped_duplicate": 0,
    }

    scout_json = parse_scout_json(scout_output)
    if scout_json is None:
        state.log("  Scout: JSON parse failed, skipping application")
        return result

    findings = scout_json.get("findings", [])
    if not findings:
        return result

    # Load existing cache
    cache = state.read_scout()
    existing_findings = cache.get("findings", [])
    existing_ids = {f["id"] for f in existing_findings if f.get("id")}

    result["findings_found"] = len(findings)

    for finding in findings:
        title = finding.get("title", "")
        source_url = finding.get("source_url", "")
        relevance = finding.get("relevance_score", 0)
        summary = finding.get("summary", "")
        mutation_direction = finding.get("mutation_direction", "")

        # Generate stable ID
        fid = finding.get("id") or _make_finding_id(title, source_url)
        finding["id"] = fid

        # Skip duplicates
        if fid in existing_ids:
            result["findings_skipped_duplicate"] += 1
            continue

        # Score threshold check
        if relevance < config.scout_min_relevance_score:
            result["findings_skipped_score"] += 1
            finding["injected_as_stimulus"] = False
            finding["injected_cycle"] = None
        else:
            # Inject as stimulus
            lines = [
                f"# Scout Finding: {title}",
                "",
                f"**Source**: {source_url}" if source_url else "",
                f"**Relevance**: {relevance}/10",
                "",
                "## Summary",
                "",
                summary,
            ]
            if mutation_direction:
                lines += ["", "## Suggested Direction", "", mutation_direction]
            content = "\n".join(line for line in lines if line is not None)
            state.add_stimulus(content)

            finding["injected_as_stimulus"] = True
            finding["injected_cycle"] = current_cycle
            result["findings_injected"] += 1

        existing_findings.append(finding)
        existing_ids.add(fid)

    # Save updated cache
    cache["last_scout_cycle"] = current_cycle
    cache["findings"] = existing_findings
    state.write_scout(cache)

    return result
