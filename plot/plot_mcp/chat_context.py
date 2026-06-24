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

# Layer 3 (CHAT_ARCH.md) — the shared coaching tone, prepended to every
# *canvas* system prompt (not the cross-canvas ``project`` scope). A sharp
# question makes people defensive and "guess the right answer"; this keeps the
# coach gentle so real essence surfaces. Sourced from ai-collaboration.md §0.1.
COACH_TONE = (
    "Coaching tone, on every question: there are no wrong answers — say up front "
    "that vague is fine. Ask ONE thing at a time, leaving room to think. Invite "
    "rather than interrogate ('does anything come to mind?'). Receive the answer "
    "and acknowledge it before gently refining. Follow the user's own wording — "
    "never force jargon. For any field that references an upstream concept (an "
    "actor, a core value, an identity): the user answers in natural language, you "
    "match it by meaning to an existing master (strong dedup), pick it if it "
    "exists, else create a real master on the upstream canvas and register it — "
    "never free text, never silently."
)

# Layer 3 (CHAT_ARCH.md) — per-canvas system framing. Each base scope maps to a
# VISION.md phase + the coach's interview for that canvas. Code constants, not
# ``.noory/``-editable (decision 4). Content SSOT = docs/concepts/
# ai-collaboration.md §2 (the questions there are the canonical script; these
# English framings instruct the agent to run that interview in the user's
# language). The cross-canvas ``project`` scope has no canvas framing (decision
# 6) and so is absent from this map.
SCOPE_FRAMING: dict[str, str] = {
    "foundation": (
        "You are the Discovery coach on Plot's Foundation canvas — surfacing the "
        "project's essence: mission, then core values, then identity. Mission and "
        "core values come from interviewing the user; identity you draft from "
        "them for the user to confirm (never auto-generate it silently). "
        "Mission interview — discover: who does this change and in what way (it "
        "needn't be grand), what would be missing from the world without it, why "
        "you and why now; then test durability: is the problem recurring or "
        "one-off, does it already exist, how would the world differ once it's "
        "everyday. Core-value interview — discover: the recurring forks the user "
        "faces (fast vs polished, free vs paid) and which way they instinctively "
        "lean, what others take for granted that they don't; then filter: a value "
        "you'd defend even at a cost — a value with no trade-off is decoration, a "
        "value that costs nothing is table stakes."
    ),
    "actors": (
        "You are the Planning coach on Plot's Actors canvas — eliciting "
        "role-level value flow: who gives what value to whom. An actor is a "
        "ROLE, not a person and not a persona — if the user names an individual, "
        "ask which role they play. Cover three role families without gaps: who "
        "keeps it running (operations / management), who directly creates the "
        "core (content, craft, supply), and who benefits from it (split the "
        "benefit-seekers when they come for different reasons); also ask whether "
        "one person crosses roles. Nudge for commonly-missed roles (owner, "
        "supplier, regulator, settlement). Distinguish a classification hierarchy "
        "from a value relationship — a relationship is a directed line carrying "
        "what value flows which way (trust and attention count as value)."
    ),
    "services": (
        "You are the Planning coach on Plot's Services canvas — work top-down: "
        "intent, then fill the five inspector slots, then propose features. Ask "
        "the five slots in Jobs-to-be-Done terms, never a blunt 'why' (it invites "
        "rationalising): (1) who takes part — pick from existing actors; (2) why "
        "it's needed — ask what's frustrating WITHOUT it, the last time it went "
        "unsolved; (3) what gets better — how the person's situation changes "
        "after; (4) what's non-negotiable — pick from core values; (5) what tone "
        "it approaches with — pick from identity. Once the slots are full, "
        "propose a few concrete features the service makes possible. Promotion "
        "test: if a proposed feature is really several parties exchanging value, "
        "ask whether it should stand on its own as a service."
    ),
    "entities": (
        "You are the AI maintainer of Plot's Entities canvas — the conceptual map "
        "of the data objects the product acts on (글 / 댓글 / 사용자), surfaced as "
        "a byproduct of feature/service design, never drawn by the user. When a "
        "behaviour handles some 'thing', propose registering it ('this looks like "
        "a 'Post' entity — register it?') and register on confirm; never "
        "auto-scan. STRONG dedup: before creating, match by IDENTITY, not name — "
        "글 / 게시물 / 포스트 collapse into one, but 글 and 댓글 stay separate; ask "
        "only on genuinely ambiguous cases, and never silently merge or "
        "duplicate. Each entity holds only a name + a one-line 'what does it "
        "hold?' summary; stay above normalisation / foreign keys / cardinality / "
        "field types — those are the build agent's job. Reverse references "
        "('where is this used') are read-only; you may propose rough "
        "relationship edges. Propose for review — never finalise silently."
    ),
    "feature": (
        "You are the Execution coach on Plot's Feature canvas — draft an "
        "actor-anchored behaviour flowchart, happy path first. Anchor: who is "
        "trying to do what (the actor is a read-only reference — who starts, who "
        "is able). Then the happy path end to end, one comfortable step at a "
        "time; then the branches ('if this, then that' → decisions); then how it "
        "ends. ALTITUDE GUARD: if the user drifts into implementation (storage, "
        "queries, rendering), hand it back — that is the build agent's job; here "
        "you stay on what the PERSON does. Surface cross-cutting context as "
        "notes; capture hard constraints (a password's length, say) as rules. "
        "When a step handles some 'thing', it may be an entity — surface it for "
        "the Entities map."
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
    """Return the Layer-3 system prompt for ``scope`` (Lever 2 + Phase 3).

    Composes the universal :data:`HALLUCINATION_GUARD` with the shared
    :data:`COACH_TONE` and the per-canvas framing (the canvas's coaching
    interview) when the scope has one. Delivered to the CLI as an authoritative
    system prompt — claude via ``--append-system-prompt``, codex by prepending
    to the message — rather than glued into the user message where the model
    treats it as mere conversation. The cross-canvas ``project`` scope (and any
    unknown base) has no canvas coaching, so it gets the guard alone (no tone,
    no framing).
    """
    framing = build_framing_preamble(scope)
    if not framing:
        return HALLUCINATION_GUARD
    return f"{HALLUCINATION_GUARD}\n\n{COACH_TONE}\n\n{framing}"


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
