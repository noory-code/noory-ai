"""Actor + service node classes (D-2026-06-11-B).

Extracted from the models.py god module. Contains the 7 non-Foundation
canvas-anchor node kinds: actor / actor_ref / service / category +
mission_ref / value_ref / identity_ref. The four ref classes carry their
own ``@model_validator`` that mirrors the dispatch ``_ref_kind_requires_ref_id``
on the retired god ``SketchNode``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from plot_mcp.models_kinds import BaseNodeFields


class ActorNode(BaseNodeFields):
    """v0.15 Phase 1: ``actor`` kind. A class of people in the value
    economy (PHILOSOPHY P5, IDENTITY.md ``Actor as class``).

    D-2026-06-15-J: the actor entity carries **identity only** — ``side``
    (Surface) + ``body``. ``motivation`` / ``pain`` are NOT here: per
    PHILOSOPHY P3 (Participation is Asymmetric) they are defined by the
    service and now live on ``actor_ref`` (per-service stake)."""

    kind: Literal["actor"] = "actor"
    side: Literal["operator", "user"] | None = None
    body: str = ""


class ActorRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``actor_ref`` kind. References an actor master that
    lives on the Actors canvas. Carries the actor's **per-service stake**:
    ``gives`` / ``receives`` (value flow, PHILOSOPHY P6 weakened form) +
    ``motivation`` / ``pain`` (why this actor participates here / what
    hurts here — D-2026-06-15-J, PHILOSOPHY P3). ``side`` mirrors the
    referenced actor's side so the canvas can colour-code without
    dereferencing the master each render (identity, not authored here)."""

    kind: Literal["actor_ref"] = "actor_ref"
    ref_actor_id: str | None = None
    gives: str = ""
    receives: str = ""
    motivation: str = ""
    pain: str = ""
    side: Literal["operator", "user"] | None = None

    @model_validator(mode="after")
    def _ref_actor_id_required(self) -> ActorRefNode:
        if not self.ref_actor_id:
            raise ValueError(f"node {self.id!r} of kind 'actor_ref' requires ref_actor_id")
        return self


class ServiceNode(BaseNodeFields):
    """v0.15 Phase 1: ``service`` kind. The value-creating hub
    (PHILOSOPHY P5). Top-level (parent_id None) and sub-service share
    the same shape — the Inspector surfaces different fields per role.

    D-2026-06-15-K: ``problem`` is the one-line need the service solves
    (a service is the process of solving a problem). It is the anchor;
    ``what`` / ``value_created`` / ``outcome`` are the solution side."""

    kind: Literal["service"] = "service"
    problem: str = ""
    target_side: Literal["operator", "user", "both"] | None = None
    what: str = ""
    value_created: str = ""
    scope: str = ""
    trigger: str = ""
    how: str = ""
    outcome: str = ""
    do: str = ""
    dont: str = ""
    body: str = ""


class CategoryNode(BaseNodeFields):
    """v0.15 Phase 1: ``category`` kind. Thematic grouping of services on
    the Services canvas; a pure container with no value creation of its
    own. ``theme`` is the one-line statement of the common thread."""

    kind: Literal["category"] = "category"
    theme: str = ""
    body: str = ""


class MissionRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``mission_ref`` kind. References a Foundation
    Mission master; lets a service declare which Mission it answers to.
    v0.24.x (D-2026-05-17-M): ``notes_in_context`` for service-context
    typed notes (4-ref symmetry with ActorRefNode's gives/receives)."""

    kind: Literal["mission_ref"] = "mission_ref"
    ref_mission_id: str | None = None
    notes_in_context: str = ""

    @model_validator(mode="after")
    def _ref_mission_id_required(self) -> MissionRefNode:
        if not self.ref_mission_id:
            raise ValueError(f"node {self.id!r} of kind 'mission_ref' requires ref_mission_id")
        return self


class ValueRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``value_ref`` kind. References a Foundation
    CoreValue master; lets a service declare which Core Value it
    answers to. v0.24.x (D-2026-05-17-M): ``notes_in_context``."""

    kind: Literal["value_ref"] = "value_ref"
    ref_value_id: str | None = None
    notes_in_context: str = ""

    @model_validator(mode="after")
    def _ref_value_id_required(self) -> ValueRefNode:
        if not self.ref_value_id:
            raise ValueError(f"node {self.id!r} of kind 'value_ref' requires ref_value_id")
        return self


class IdentityRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``identity_ref`` kind. References a Foundation
    Identity master; lets a service declare which Identity aspect it
    expresses. v0.24.x (D-2026-05-17-M): ``notes_in_context``."""

    kind: Literal["identity_ref"] = "identity_ref"
    ref_identity_id: str | None = None
    notes_in_context: str = ""

    @model_validator(mode="after")
    def _ref_identity_id_required(self) -> IdentityRefNode:
        if not self.ref_identity_id:
            raise ValueError(f"node {self.id!r} of kind 'identity_ref' requires ref_identity_id")
        return self
