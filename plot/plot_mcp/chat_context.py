"""Shared chat-context builders — canvas framing + selection preamble.

Neutral domain module imported by BOTH delivery layers: the in-app HTTP chat
(``endpoints_chat.py``) and the external-agent MCP path (``mcp_tools.py``,
``get_viewer_context``). Keeping the framing constants + preamble shapes here is
the SSOT (D-2026-06-15-D) — the MCP layer must never import the HTTP endpoint
module.

Two independent pieces of per-turn context (CHAT_ARCH.md):
  * Layer 2 — ``build_context_preamble``: which canvas + what is selected.
  * Layer 3 — ``build_framing_preamble``: how the agent should help on this
    canvas (its VISION phase).
"""

from __future__ import annotations

from typing import Any

# Layer 2 (CHAT_ARCH.md) — how many selected nodes to spell out in the
# preamble before falling back to ids-only, so the prompt stays bounded.
SELECTION_DETAIL_CAP = 20

# Layer 3 (CHAT_ARCH.md) — per-canvas system framing. Each base scope maps to a
# VISION.md phase, which sets how the agent should help on that canvas. Code
# constants, not ``.noory/``-editable (decision 4). The cross-canvas ``project``
# scope has no canvas framing (decision 6) and so is absent from this map.
SCOPE_FRAMING: dict[str, str] = {
    "foundation": (
        "You are collaborating inside Plot's Foundation canvas (Discovery "
        "phase). Help the user surface and sharpen the project's essence — its "
        "core values, mission, and identity."
    ),
    "actors": (
        "You are collaborating inside Plot's Actors canvas (Planning phase). "
        "Help the user design the value-creation machinery — who acts and how "
        "value flows between them."
    ),
    "services": (
        "You are collaborating inside Plot's Services canvas (Planning phase). "
        "Help the user design the value-creation machinery — the services that "
        "deliver the mission and how they relate."
    ),
    "entities": (
        "You are collaborating inside Plot's Entities canvas (Planning phase), "
        "an AI-maintained conceptual map of the product's data objects (글 / "
        "댓글 / 사용자) — what the services act on. Surface and maintain entities "
        "as a byproduct of feature/service design: each entity holds only a "
        "name + a one-line 'what does it hold?' summary, plus rough "
        "relationships drawn as edges. Stay above the altitude of normalisation "
        "/ foreign keys / cardinality / field types — those are the external "
        "agent's job, not Plot's. Before adding an entity, strongly match it "
        "against the existing registry so 글 / 게시물 / 포스트 collapse into one; "
        "ask the user on genuinely ambiguous cases, and never silently merge or "
        "duplicate. Propose entities for the user to review — never finalise "
        "silently."
    ),
    "feature": (
        "You are collaborating inside Plot's Service-Detail canvas (Execution "
        "phase). Help the user break the plan into concrete steps, decisions, "
        "and rules for this one service."
    ),
}


def build_framing_preamble(scope: str) -> str:
    """Return the per-canvas system framing for ``scope`` (Layer 3).

    Maps the *base* scope to its VISION-phase framing, so a parametric
    ``feature:<id>`` resolves to the shared feature framing rather
    than a missing per-instance key. The cross-canvas ``project`` scope (and any
    unknown base) gets no framing.
    """
    base = scope.split(":", 1)[0]
    return SCOPE_FRAMING.get(base, "")


def build_context_preamble(scope: str, selection: Any) -> str:
    """Build the per-turn context preamble prepended to the CLI message.

    Tells the agent which canvas the user is on and what they have selected, so
    "fix this" resolves to the selected node (Layer 2). Returns "" when there's
    nothing to inject: the ``project`` scope is explicitly cross-canvas
    (decision 6), and an empty/malformed selection adds nothing. Selection is
    capped at ``SELECTION_DETAIL_CAP`` detailed nodes; the rest are listed as
    ids only so a large multi-select can't blow the context window (red-team A3).
    """
    if scope == "project" or not isinstance(selection, list) or not selection:
        return ""
    nodes = [n for n in selection if isinstance(n, dict)]
    if not nodes:
        return ""
    detailed = nodes[:SELECTION_DETAIL_CAP]
    rendered = ", ".join(
        f'{n.get("kind", "?")} "{n.get("label", "")}" ({n.get("id", "")})'
        for n in detailed
    )
    lines = [
        f"[Plot context] Active canvas: {scope}.",
        f"Selected ({len(nodes)}): {rendered}",
    ]
    if len(nodes) > SELECTION_DETAIL_CAP:
        overflow = ", ".join(
            str(n.get("id", "")) for n in nodes[SELECTION_DETAIL_CAP:]
        )
        lines.append(
            f"…and {len(nodes) - SELECTION_DETAIL_CAP} more: {overflow}"
        )
    return "\n".join(lines)
