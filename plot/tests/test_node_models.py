"""Per-kind node-class round-trip + invariant tests.

v0.15 Phase 1 (Server SSOT). Covers all 11 non-Foundation kinds split
out of the god ``SketchNode``:

  - v0.14.16 — actor / actor_ref / service / category / 3 ref kinds
  - v0.14.17 — metric / step / rule / content + 15-way SketchNode union

Foundation kinds (project / mission / core_value / identity) have
their own coverage in ``test_canvas_doc.py`` and ``test_md_template.py``.

The round-trip pattern mirrors ``test_canvas_doc.py`` —
``Cls.model_validate(Cls(...).model_dump()) == original``.

The discriminated-union dispatch is tested via ``SketchNodeAdapter`` —
the public ``TypeAdapter`` exposed alongside ``SketchNode`` for raw-dict
validation.
"""

from __future__ import annotations

import pytest

from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CategoryNode,
    ContentNode,
    IdentityRefNode,
    MetricNode,
    MissionRefNode,
    RuleNode,
    ServiceNode,
    SketchNodeAdapter,
    StepNode,
    ValueRefNode,
)

# ---------------------------------------------------------------------------
# round-trip — every kind must survive model_dump / model_validate intact
# ---------------------------------------------------------------------------


def test_actor_round_trip() -> None:
    n = ActorNode(
        id="actor-1",
        label="Operator",
        motivation="run the show",
        pain="too many tabs",
        side="operator",
    )
    assert ActorNode.model_validate(n.model_dump()) == n


def test_actor_ref_round_trip() -> None:
    n = ActorRefNode(
        id="ref-1",
        label="Operator instance",
        ref_actor_id="actor-1",
        gives="moderation",
        receives="reputation",
    )
    assert ActorRefNode.model_validate(n.model_dump()) == n


def test_service_round_trip() -> None:
    n = ServiceNode(
        id="svc-1",
        label="Sign-up",
        target_side="user",
        what="onboard new users",
        value_created="access",
        scope="end-to-end onboarding",
        trigger="user lands on /signup",
        how="email + password",
        outcome="account exists",
        do="show progress",
        dont="ask for irrelevant fields",
    )
    assert ServiceNode.model_validate(n.model_dump()) == n


def test_category_round_trip() -> None:
    n = CategoryNode(id="cat-1", label="Admin", theme="operator system management")
    assert CategoryNode.model_validate(n.model_dump()) == n


def test_mission_ref_round_trip() -> None:
    n = MissionRefNode(id="mref-1", label="Mission ref", ref_mission_id="m-1")
    assert MissionRefNode.model_validate(n.model_dump()) == n


def test_value_ref_round_trip() -> None:
    n = ValueRefNode(id="vref-1", label="Value ref", ref_value_id="cv-1")
    assert ValueRefNode.model_validate(n.model_dump()) == n


def test_identity_ref_round_trip() -> None:
    n = IdentityRefNode(id="iref-1", label="Identity ref", ref_identity_id="id-1")
    assert IdentityRefNode.model_validate(n.model_dump()) == n


# ---------------------------------------------------------------------------
# invariants — each ref kind requires its matching id field
# ---------------------------------------------------------------------------


def test_actor_ref_without_ref_actor_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_actor_id"):
        ActorRefNode(id="ref-1", label="Orphan")


def test_actor_ref_with_blank_ref_actor_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_actor_id"):
        ActorRefNode(id="ref-1", label="Orphan", ref_actor_id="")


def test_mission_ref_without_ref_mission_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_mission_id"):
        MissionRefNode(id="mref-1", label="Orphan")


def test_value_ref_without_ref_value_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_value_id"):
        ValueRefNode(id="vref-1", label="Orphan")


def test_identity_ref_without_ref_identity_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_identity_id"):
        IdentityRefNode(id="iref-1", label="Orphan")


# ---------------------------------------------------------------------------
# defaults — confirm wire-format parity with god ``SketchNode``
# ---------------------------------------------------------------------------


def test_actor_defaults_match_sketchnode_actor_defaults() -> None:
    """An ActorNode with only id+kind set must serialise the same typed
    fields (motivation/pain/side) that god SketchNode emits for an actor.
    """
    n = ActorNode(id="actor-min", label="Actor")
    dumped = n.model_dump()
    assert dumped["motivation"] == ""
    assert dumped["pain"] == ""
    assert dumped["side"] is None


def test_service_defaults_match_sketchnode_service_defaults() -> None:
    n = ServiceNode(id="svc-min", label="Service")
    dumped = n.model_dump()
    for key in ("what", "value_created", "scope", "trigger", "how", "outcome", "do", "dont"):
        assert dumped[key] == ""
    assert dumped["target_side"] is None


def test_category_defaults_match_sketchnode_category_defaults() -> None:
    n = CategoryNode(id="cat-min", label="Category")
    assert n.model_dump()["theme"] == ""


# ---------------------------------------------------------------------------
# v0.14.17 — composition kinds (metric / step / rule / content)
# ---------------------------------------------------------------------------


def test_metric_round_trip() -> None:
    n = MetricNode(id="m1", label="Latency", target="<200ms", measurement="p95")
    assert MetricNode.model_validate(n.model_dump()) == n


def test_step_round_trip_with_order() -> None:
    n = StepNode(id="s1", label="Sign in", order=1, outcome="session token")
    assert StepNode.model_validate(n.model_dump()) == n


def test_step_round_trip_without_order() -> None:
    """``order = None`` keeps the step unordered (parallel branches)."""
    n = StepNode(id="s1", label="Either path")
    assert n.order is None
    assert StepNode.model_validate(n.model_dump()) == n


def test_rule_round_trip() -> None:
    n = RuleNode(
        id="r1",
        label="GDPR opt-in",
        policy="explicit consent",
        enforcement="checkbox + audit log",
        actor_permissions={"user": "RUD", "admin": "CRUD"},
    )
    assert RuleNode.model_validate(n.model_dump()) == n


def test_content_round_trip() -> None:
    n = ContentNode(
        id="c1",
        label="Receipt",
        format="application/json",
        producer_actor_id="checkout",
        consumer_actor_id="user",
    )
    assert ContentNode.model_validate(n.model_dump()) == n


# ---------------------------------------------------------------------------
# v0.14.17 — discriminated-union dispatch via SketchNodeAdapter
# ---------------------------------------------------------------------------


def test_adapter_dispatches_actor() -> None:
    raw = ActorNode(id="a", label="Actor", side="user").model_dump()
    parsed = SketchNodeAdapter.validate_python(raw)
    assert isinstance(parsed, ActorNode)
    assert parsed.side == "user"


def test_adapter_dispatches_metric() -> None:
    raw = MetricNode(id="m", label="M", target="x", measurement="y").model_dump()
    parsed = SketchNodeAdapter.validate_python(raw)
    assert isinstance(parsed, MetricNode)
    assert parsed.target == "x"


def test_adapter_dispatches_actor_ref_with_validator() -> None:
    raw = ActorRefNode(id="ref", label="R", ref_actor_id="a").model_dump()
    parsed = SketchNodeAdapter.validate_python(raw)
    assert isinstance(parsed, ActorRefNode)
    assert parsed.ref_actor_id == "a"


def test_adapter_rejects_unknown_kind() -> None:
    """The discriminator must reject an unknown kind, not silently dispatch
    to a fallback class."""
    with pytest.raises(ValueError, match="kind"):
        SketchNodeAdapter.validate_python({"id": "x", "kind": "ghost"})


def test_adapter_rejects_missing_kind() -> None:
    """Discriminated union requires the discriminator field to be present."""
    with pytest.raises(ValueError, match="kind"):
        SketchNodeAdapter.validate_python({"id": "x"})
