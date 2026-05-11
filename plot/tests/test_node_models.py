"""Per-kind node-class round-trip + invariant tests.

v0.15 Phase 1 (Server SSOT). Covers the non-Foundation kinds split out
of the god ``SketchNode`` in v0.14.15 and the 4 composition kinds added
in v0.14.16. Foundation classes have their own coverage in
``test_canvas_doc.py`` and ``test_md_template.py``.

The round-trip pattern mirrors ``test_canvas_doc.py`` —
``Cls.model_validate(Cls(...).model_dump()) == original``.
"""

from __future__ import annotations

import pytest

from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CategoryNode,
    IdentityRefNode,
    MissionRefNode,
    ServiceNode,
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
