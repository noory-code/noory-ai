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
from pydantic import ValidationError

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
    # D-2026-06-15-J: actor is identity-only (side + body).
    n = ActorNode(
        id="actor-1",
        label="Operator",
        side="operator",
        body="운영자 페르소나",
    )
    assert ActorNode.model_validate(n.model_dump()) == n


def test_actor_ref_round_trip() -> None:
    # D-2026-06-15-J: actor_ref carries per-service stake (motivation/pain)
    # alongside the value flow (gives/receives).
    n = ActorRefNode(
        id="ref-1",
        label="Operator instance",
        ref_actor_id="actor-1",
        gives="moderation",
        receives="reputation",
        motivation="이 서비스를 안전하게 운영",
        pain="신고가 너무 많다",
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
    """An ActorNode with only id+kind set serialises identity-only typed
    fields (side/body). D-2026-06-15-J: motivation/pain are no longer
    actor fields — they moved to actor_ref as per-service stake.
    """
    n = ActorNode(id="actor-min", label="Actor")
    dumped = n.model_dump()
    assert dumped["side"] is None
    assert dumped["body"] == ""
    assert "motivation" not in dumped
    assert "pain" not in dumped


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


# ---------------------------------------------------------------------------
# v0.15.9 Phase 5.1 — exhaustive 15-kind adapter sweep
#
# Pins the structural contract: every kind in the 15-way union must
# survive ``Adapter.validate_python(Class(...).model_dump())`` intact,
# returning the same class. A drift in a typed-field default or a
# missing class registration fails this sweep.
# ---------------------------------------------------------------------------


from plot_mcp.models import (  # noqa: E402  (kept at bottom for clarity)
    CoreValueNode,
    IdentityNode,
    MissionNode,
    ProjectNode,
)

_ALL_KIND_CLASSES = {
    "project": ProjectNode,
    "mission": MissionNode,
    "core_value": CoreValueNode,
    "identity": IdentityNode,
    "actor": ActorNode,
    "actor_ref": ActorRefNode,
    "service": ServiceNode,
    "category": CategoryNode,
    "mission_ref": MissionRefNode,
    "value_ref": ValueRefNode,
    "identity_ref": IdentityRefNode,
    "metric": MetricNode,
    "step": StepNode,
    "rule": RuleNode,
    "content": ContentNode,
}


def _make_minimal(kind: str):
    """Build the smallest valid instance for a given kind. Ref kinds
    need a non-empty discriminator id (per the ref-validator), so we
    supply the minimum payload each kind enforces."""
    cls = _ALL_KIND_CLASSES[kind]
    base = {"id": f"{kind}-1", "label": kind}
    if kind == "actor_ref":
        return cls(**base, ref_actor_id=f"{kind}-master")
    if kind == "mission_ref":
        return cls(**base, ref_mission_id=f"{kind}-master")
    if kind == "value_ref":
        return cls(**base, ref_value_id=f"{kind}-master")
    if kind == "identity_ref":
        return cls(**base, ref_identity_id=f"{kind}-master")
    return cls(**base)


@pytest.mark.parametrize("kind", sorted(_ALL_KIND_CLASSES.keys()))
def test_adapter_dispatches_every_kind(kind: str) -> None:
    """Every kind in the 15-way union round-trips via the adapter
    and returns an instance of its own class."""
    instance = _make_minimal(kind)
    raw = instance.model_dump()
    parsed = SketchNodeAdapter.validate_python(raw)
    expected_cls = _ALL_KIND_CLASSES[kind]
    assert isinstance(parsed, expected_cls), (
        f"adapter returned {type(parsed).__name__} for kind={kind}, "
        f"expected {expected_cls.__name__}"
    )
    assert parsed.kind == kind


@pytest.mark.parametrize("kind", sorted(_ALL_KIND_CLASSES.keys()))
def test_every_kind_round_trip_idempotent(kind: str) -> None:
    """``model_validate(instance.model_dump())`` must equal the original."""
    cls = _ALL_KIND_CLASSES[kind]
    instance = _make_minimal(kind)
    second = cls.model_validate(instance.model_dump())
    assert second == instance


def test_union_covers_all_15_kinds() -> None:
    """Sanity: the adapter's discriminated union exposes 15 distinct
    classes (catches a drop / duplicate during a future refactor)."""
    assert len(_ALL_KIND_CLASSES) == 15
    assert len({c.__name__ for c in _ALL_KIND_CLASSES.values()}) == 15


# ---------------------------------------------------------------------------
# v0.17.2 Phase 2 (D-2026-05-16-C) — BaseNodeFields.version field
# ---------------------------------------------------------------------------


def test_base_fields_version_default() -> None:
    """Omitting ``version`` lands as the canonical default ``"v1.0"`` —
    the backward-compat path for pre-Phase-2 canvases."""
    node = MissionNode(id="n1")
    assert node.version == "v1.0"


@pytest.mark.parametrize("valid", ["v1.0", "v0.1", "v123.456", "v10.20"])
def test_base_fields_version_accepts_valid(valid: str) -> None:
    """Any string matching ``^v\\d+\\.\\d+$`` lands without error."""
    node = MissionNode(id="n1", version=valid)
    assert node.version == valid


@pytest.mark.parametrize(
    "invalid",
    [
        "1.0",  # missing ``v`` prefix
        "v1",  # missing minor
        "v1.0.0",  # 3-component (Phase 3+ must open a fresh D-id to widen)
        "vX.Y",  # non-numeric
        "",  # empty
        "v1.",  # trailing dot
        "v.1",  # leading dot
        "V1.0",  # uppercase ``V``
    ],
)
def test_base_fields_version_rejects_invalid(invalid: str) -> None:
    """The regex contract rejects malformed version strings loudly."""
    with pytest.raises(ValidationError, match="version must match"):
        MissionNode(id="n1", version=invalid)


@pytest.mark.parametrize("kind", sorted(_ALL_KIND_CLASSES.keys()))
def test_base_fields_version_round_trips_for_every_kind(kind: str) -> None:
    """The ``version`` field round-trips intact for all 15 kinds —
    catches drift between Pydantic dump and adapter validate paths."""
    instance = _make_minimal(kind)
    raw = instance.model_dump()
    assert raw["version"] == "v1.0"
    parsed = SketchNodeAdapter.validate_python(raw)
    assert parsed.version == "v1.0"
