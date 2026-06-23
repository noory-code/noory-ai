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


# Layer 3 (CHAT_ARCH.md) — the constant anti-hallucination guard, prepended to
# every system prompt regardless of scope. The in-app agent gets almost no
# project content per turn (labels only, see ``docs/idea/chat/00-problem.md``),
# so without an explicit "read, don't invent" instruction it fills the blanks
# by inventing mission text / values / actors / entities. This guard tells it to
# ground every claim in the provided context, READ the canvas via its Plot MCP
# tools when it doesn't know, and otherwise ask — never fabricate. It also pins
# how "this" resolves (to the selected node). Lever 2, docs/idea/chat/01-levers.md.
HALLUCINATION_GUARD = (
    "Ground every statement in the Plot project context you are given and the "
    "canvas you can read with your Plot MCP tools (e.g. get_viewer_context). If "
    "you do not know something specific about THIS project — its mission text, "
    "core values, actors, services, features, or entities — read it with those "
    "tools or ask the user. Never invent project details. When the user says "
    '"this" / "it", resolve it to the node listed as selected in the context.'
)


def build_system_prompt(scope: str) -> str:
    """Return the Layer-3 system prompt for ``scope`` (Lever 2).

    Composes the universal :data:`HALLUCINATION_GUARD` with the per-canvas
    framing (when the scope has one). Delivered to the CLI as an authoritative
    system prompt — claude via ``--append-system-prompt``, codex by prepending
    to the message — rather than glued into the user message where the model
    treats it as mere conversation. The cross-canvas ``project`` scope (and any
    unknown base) has no framing, so it gets the guard alone.
    """
    framing = build_framing_preamble(scope)
    return f"{HALLUCINATION_GUARD}\n\n{framing}" if framing else HALLUCINATION_GUARD


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
        f'{n.get("kind", "?")} "{n.get("label", "")}" ({n.get("id", "")})' for n in detailed
    )
    lines = [
        f"[Plot context] Active canvas: {scope}.",
        f"Selected ({len(nodes)}): {rendered}",
    ]
    if len(nodes) > SELECTION_DETAIL_CAP:
        overflow = ", ".join(str(n.get("id", "")) for n in nodes[SELECTION_DETAIL_CAP:])
        lines.append(f"…and {len(nodes) - SELECTION_DETAIL_CAP} more: {overflow}")
    return "\n".join(lines)
