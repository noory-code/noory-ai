"""CanvasDoc + per-canvas-kind validators for Plot v0.2 multi-canvas split.

Each canvas enforces its own allowed ``NodeKind`` set and structural rules.
See the ``Target Data Model`` section of the v0.2 plan.
"""

from __future__ import annotations

import pytest

from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    CategoryNode,
    ContentNode,
    CoreValueNode,
    IdentityNode,
    IdentityRefNode,
    MetricNode,
    MissionNode,
    MissionRefNode,
    ProjectNode,
    RuleNode,
    ServiceNode,
    SketchEdge,
    SketchNode,
    SketchNodeAdapter,
    StepNode,
    ValueRefNode,
)

# ---------------------------------------------------------------------------
# core canvas
# ---------------------------------------------------------------------------


def _core_seed_nodes() -> list[SketchNode]:
    """Minimal valid core-canvas content: project anchor + 1 mission + 1 identity."""
    return [
        ProjectNode(id="project", label="Project", shape="circle"),
        MissionNode(id="mission", label="M"),
        IdentityNode(id="identity", label="Voice"),
    ]


def test_core_canvas_minimum_seed_ok() -> None:
    CanvasDoc(canvas_id="foundation", canvas_kind="foundation", nodes=_core_seed_nodes())


def test_core_canvas_multiple_core_values_ok() -> None:
    CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            CoreValueNode(id="cv1", label="빠름"),
            CoreValueNode(id="cv2", label="정확함"),
        ],
    )


def test_core_canvas_multiple_missions_ok() -> None:
    """v0.5: Mission is 1..N (was exactly 1)."""
    CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            MissionNode(id="m2", label="M2"),
            MissionNode(id="m3", label="M3"),
        ],
    )


def test_core_canvas_multiple_identities_ok() -> None:
    """v0.5: Identity is 1..N peers (was exactly 1 + facet children)."""
    CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            IdentityNode(id="energy", label="Energy"),
            IdentityNode(id="speech", label="Speech style"),
        ],
    )


def test_core_canvas_missing_mission_rejected() -> None:
    with pytest.raises(ValueError, match="mission"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                ProjectNode(id="project", label="Project", shape="circle"),
                IdentityNode(id="identity", label="I"),
            ],
        )


def test_core_canvas_missing_identity_rejected() -> None:
    with pytest.raises(ValueError, match="identity"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                ProjectNode(id="project", label="Project", shape="circle"),
                MissionNode(id="mission", label="M"),
            ],
        )


def test_core_canvas_missing_project_accepted() -> None:
    """v0.13 Phase 0: project anchor moved to ProjectDoc.anchors.
    Foundation no longer requires a project node in nodes."""
    canvas = CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            MissionNode(id="mission", label="M"),
            IdentityNode(id="identity", label="I"),
        ],
    )
    assert all(n.kind != "project" for n in canvas.nodes)


def test_core_canvas_two_projects_rejected() -> None:
    """v0.13 Phase 0: legacy project nodes tolerated for backwards compat
    but at most one (the eviction migrator removes them entirely)."""
    with pytest.raises(ValueError, match="legacy project"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                *_core_seed_nodes(),
                ProjectNode(id="p2", label="P2", shape="circle"),
            ],
        )


def test_core_canvas_nested_project_rejected() -> None:
    """Project anchor must be top-level."""
    with pytest.raises(ValueError, match="top-level"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                MissionNode(id="mission", label="M"),
                IdentityNode(id="identity", label="I"),
                ProjectNode(
                    id="project",
                    label="P",
                    shape="circle",
                    parent_id="mission",
                ),
            ],
        )


def test_mission_node_carries_typed_fields() -> None:
    """v0.10: mission nodes have ``what_we_do`` / ``why`` / ``direction``
    typed fields stored directly on the node — Plot is the sole editor
    so they go straight into canvas.json, not into details.md."""
    n = MissionNode(
        id="mission-1",
        label="Mission",
        what_we_do="우리는 매일 서로의 팬이 되는 커뮤니티를 운영한다",
        why="사람들이 서로 빛나게 하고 싶어서",
        direction="누구나 히어로인 일상으로",
    )
    assert n.what_we_do.startswith("우리는 매일")
    assert "히어로" in n.direction


def test_actor_does_not_carry_foreign_typed_fields() -> None:
    """v0.15: per-kind classes own only their own typed fields. An
    ActorNode must not carry Mission's ``what_we_do`` or CoreValue's
    ``definition`` etc. — that god-pool pattern is gone."""
    n = ActorNode(id="x", label="User")
    for foreign in (
        "what_we_do",
        "why",
        "direction",
        "definition",
        "description",
        "do",
        "dont",
        "what",
        "value_created",
        "scope",
        "trigger",
        "how",
        "outcome",
        "theme",
        "target",
        "measurement",
        "policy",
        "enforcement",
        "actor_permissions",
        "format",
        "producer_actor_id",
        "consumer_actor_id",
    ):
        assert not hasattr(n, foreign), (
            f"ActorNode unexpectedly carries foreign field {foreign!r} (god-pool regression)"
        )


def test_core_value_carries_typed_fields() -> None:
    """v0.10 Step 2: core_value nodes carry ``definition`` plus the shared
    ``do`` / ``dont`` AI-first pair. Stored on the node, no details.md."""
    n = CoreValueNode(
        id="cv-tolerance",
        label="관용",
        definition="다름을 인정하고 있는 그대로 받아들임",
        do="다른 의견을 먼저 듣는다",
        dont="틀렸다고 단정한다",
    )
    assert n.definition.startswith("다름을 인정")
    assert "먼저 듣는다" in n.do
    assert "단정한다" in n.dont


def test_identity_carries_typed_fields() -> None:
    """v0.10 Step 2: identity nodes carry ``description`` plus the shared
    Do/Don't pair so an LLM can mimic the persona deterministically."""
    n = IdentityNode(
        id="id-voice",
        label="Voice",
        description="따뜻하고 진솔한 1:1 대화처럼 말한다",
        do="이름을 부른다",
        dont="공지글 같은 말투로 쓴다",
    )
    assert "따뜻하고" in n.description
    assert "이름을 부른다" in n.do
    assert "공지글 같은" in n.dont


def test_value_and_identity_typed_fields_round_trip_in_canvas() -> None:
    """Foundation canvas serialises and parses Step 2 typed fields end-to-end."""
    doc = CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            CoreValueNode(
                id="cv1",
                label="Trust",
                definition="우리는 서로의 의도를 의심하지 않는다",
                do="동기를 먼저 묻는다",
                dont="비난부터 한다",
            ),
            IdentityNode(
                id="id1",
                label="Energy",
                description="조용하고 또렷하다",
                do="짧고 단단하게 말한다",
                dont="장황하게 늘어놓는다",
            ),
        ],
    )
    parsed = CanvasDoc.model_validate(doc.model_dump())
    cv = next(n for n in parsed.nodes if n.id == "cv1")
    ident = next(n for n in parsed.nodes if n.id == "id1")
    assert cv.definition.startswith("우리는 서로")
    assert cv.do == "동기를 먼저 묻는다"
    assert ident.description == "조용하고 또렷하다"
    assert ident.dont == "장황하게 늘어놓는다"


def test_node_details_path_absolute_rejected() -> None:
    with pytest.raises(ValueError, match="relative"):
        MissionNode(id="n1", label="M", details_path="/etc/passwd")


def test_node_details_path_traversal_rejected() -> None:
    with pytest.raises(ValueError, match=r"\.\."):
        MissionNode(id="n1", label="M", details_path="workspace/../etc")


def test_node_details_path_blank_rejected() -> None:
    with pytest.raises(ValueError, match="blank"):
        MissionNode(id="n1", label="M", details_path="   ")


def test_node_details_path_valid() -> None:
    n = MissionNode(
        id="n1",
        label="M",
        details_path="workspace/core/mission-mission",
    )
    assert n.details_path == "workspace/core/mission-mission"


def test_core_canvas_actor_kind_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                *_core_seed_nodes(),
                ActorNode(id="a1", label="Stray"),
            ],
        )


# ---------------------------------------------------------------------------
# actors canvas
# ---------------------------------------------------------------------------


def test_actors_canvas_two_actors_ok() -> None:
    """v0.11 — actors canvas requires ≥ 2 actor classes."""
    CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="operator", label="운영자", side="operator"),
            ActorNode(id="user", label="사용자", side="user"),
        ],
    )


def test_actors_canvas_single_actor_rejected() -> None:
    """v0.11 — IDENTITY.md baseline: ≥ 2 actor classes required."""
    with pytest.raises(ValueError, match="2 actor"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[ActorNode(id="user", label="사용자")],
        )


def test_actors_canvas_sub_actor_via_parent_id_ok() -> None:
    CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="team", label="Team", side="user"),
            ActorNode(id="member", parent_id="team", label="Member", side="user"),
        ],
    )


def test_actors_canvas_service_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                ServiceNode(id="s1", label="Stray service"),
            ],
        )


def test_actors_canvas_actor_ref_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                ActorRefNode(id="r1", ref_actor_id="user", label="ref"),
            ],
        )


# ---------------------------------------------------------------------------
# services canvas
# ---------------------------------------------------------------------------


def test_overview_top_level_services_ok() -> None:
    """v0.12 — services canvas: project + category + service (nested in category)."""
    CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="commerce", label="Commerce"),
            ServiceNode(id="order", parent_id="commerce", label="주문"),
            ServiceNode(id="pay", parent_id="commerce", label="결제"),
        ],
    )


def test_overview_service_without_category_parent_rejected() -> None:
    """v0.12 — service must be nested inside a category."""
    with pytest.raises(ValueError, match="category"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[ServiceNode(id="order", label="주문")],
        )


def test_overview_nested_category_rejected() -> None:
    """v0.12 — categories must be top-level (no category-of-categories)."""
    with pytest.raises(ValueError, match="top-level"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[
                CategoryNode(id="parent", label="Parent"),
                CategoryNode(id="child", parent_id="parent", label="Child"),
            ],
        )


def test_overview_services_rejects_foundation_refs() -> None:
    """v0.11.5 — services canvas no longer admits foundation refs (they
    moved to service_detail)."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[
                ServiceNode(id="order", label="주문"),
                MissionRefNode(
                    id="mr",
                    ref_mission_id="mission",
                    label="→ M",
                ),
            ],
        )


def test_overview_empty_canvas_ok() -> None:
    """An empty services canvas (no services yet) is fine."""
    CanvasDoc(canvas_id="services", canvas_kind="services", nodes=[])


def test_overview_nested_service_rejected() -> None:
    """Overview forbids decomposition — that's what Detail canvases are for."""
    with pytest.raises(ValueError, match="nested"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[
                ServiceNode(id="order", label="주문"),
                ServiceNode(id="order-sub", parent_id="order", label="Sub"),
            ],
        )


def test_overview_actor_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[ActorNode(id="a1", label="Stray")],
        )


# ---------------------------------------------------------------------------
# service_detail canvas
# ---------------------------------------------------------------------------


def _detail_seed(canvas_id: str = "order") -> list[SketchNode]:
    """Minimum valid service_detail content (v0.11): root service + two
    actor_refs (operator + user) to satisfy IDENTITY.md baseline."""
    return [
        ServiceNode(id=canvas_id, label="주문"),
        ActorRefNode(
            id=f"{canvas_id}-op-ref",
            label="→ operator",
            ref_actor_id="operator",
            side="operator",
        ),
        ActorRefNode(
            id=f"{canvas_id}-user-ref",
            label="→ user",
            ref_actor_id="user",
            side="user",
        ),
    ]


def test_detail_canvas_minimum_ok() -> None:
    CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=_detail_seed(),
    )


def test_detail_canvas_under_two_actor_refs_rejected() -> None:
    """v0.11 — service_detail requires ≥ 2 actor_refs (IDENTITY.md baseline)."""
    with pytest.raises(ValueError, match="actor_ref"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[ServiceNode(id="order", label="주문")],
        )


def test_detail_canvas_service_ref_must_match_canvas_id() -> None:
    with pytest.raises(ValueError, match="service_ref"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="pay",  # mismatch
            nodes=_detail_seed(),
        )


def test_detail_canvas_service_ref_required() -> None:
    with pytest.raises(ValueError, match="service_ref"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            nodes=_detail_seed(),
        )


def test_detail_canvas_sub_services_rules_contents_ok() -> None:
    CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=[
            *_detail_seed(),
            ServiceNode(id="sub1", parent_id="order", label="장바구니"),
            RuleNode(id="r1", parent_id="order", label="가격 규칙"),
            ContentNode(id="c1", parent_id="order", label="썸네일"),
        ],
    )


def test_detail_canvas_actor_ref_ok() -> None:
    CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=[
            *_detail_seed(),
            ActorRefNode(
                id="ref-user",
                ref_actor_id="user",  # references actor in actors canvas
                label="사용자",
            ),
        ],
    )


def test_detail_canvas_actor_ref_without_ref_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_actor_id"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[
                *_detail_seed(),
                ActorRefNode(id="bad-ref", label="Orphan"),
            ],
        )


# ---------------------------------------------------------------------------
# v0.10 Step 3 — Foundation reference kinds (Symbol/Component pattern)
# ---------------------------------------------------------------------------


def test_mission_ref_requires_ref_mission_id() -> None:
    with pytest.raises(ValueError, match="ref_mission_id"):
        MissionRefNode(id="mr", label="→ Mission")


def test_value_ref_requires_ref_value_id() -> None:
    with pytest.raises(ValueError, match="ref_value_id"):
        ValueRefNode(id="vr", label="→ Trust")


def test_identity_ref_requires_ref_identity_id() -> None:
    with pytest.raises(ValueError, match="ref_identity_id"):
        IdentityRefNode(id="ir", label="→ Voice")


def test_foundation_refs_valid_when_id_set() -> None:
    MissionRefNode(id="mr", label="→ M", ref_mission_id="m1")
    ValueRefNode(id="vr", label="→ V", ref_value_id="cv1")
    IdentityRefNode(id="ir", label="→ I", ref_identity_id="id1")


def test_services_canvas_rejects_foundation_refs_v0_11_5() -> None:
    """v0.11.5 — foundation refs no longer admitted on the services top
    view. Use service_detail for alignment ownership."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[
                ServiceNode(id="auth", label="Auth"),
                MissionRefNode(id="mr1", label="→ M", ref_mission_id="m1"),
            ],
        )


def test_service_detail_accepts_foundation_refs() -> None:
    """Sub-service composition canvas accepts the four ref kinds together."""
    CanvasDoc(
        canvas_id="auth",
        canvas_kind="service_detail",
        service_ref="auth",
        nodes=[
            ServiceNode(id="auth", label="Auth"),
            ActorRefNode(id="ar1", label="→ user", ref_actor_id="user", side="user"),
            ActorRefNode(id="ar2", label="→ op", ref_actor_id="operator", side="operator"),
            MissionRefNode(id="mr1", label="→ M", ref_mission_id="m1"),
            ValueRefNode(id="vr1", label="→ Trust", ref_value_id="cv1"),
            IdentityRefNode(id="ir1", label="→ Voice", ref_identity_id="id1"),
        ],
    )


def test_actors_canvas_rejects_foundation_refs() -> None:
    """Foundation refs only make sense on Services-side canvases."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                ActorNode(id="user", label="U", side="user"),
                ActorNode(id="op", label="O", side="operator"),
                MissionRefNode(id="mr", label="→ M", ref_mission_id="m1"),
            ],
        )


def test_service_node_carries_typed_fields() -> None:
    """v0.10 Step 4: service nodes carry shared (what / value_created / scope
    / do / dont) and sub-service-only (trigger / how / outcome) typed fields.
    The model accepts every field on every service; the Inspector decides
    which ones to surface for top-level vs sub-service."""
    n = ServiceNode(
        id="auth",
        label="Auth",
        what="외부 사용자가 자기 ID로 들어올 수 있게 하는 서비스",
        value_created="신원 확인된 세션",
        scope="ID/PW + OAuth + MFA. 세션 발급까지.",
        do="실패 메시지를 일반화한다",
        dont="ID 존재 여부를 누설한다",
    )
    assert n.what.startswith("외부 사용자")
    assert n.value_created == "신원 확인된 세션"
    assert "MFA" in n.scope
    assert "일반화" in n.do
    assert "누설" in n.dont


def test_sub_service_typed_fields_round_trip() -> None:
    """Sub-service-specific fields persist and are readable by id."""
    detail = CanvasDoc(
        canvas_id="auth",
        canvas_kind="service_detail",
        service_ref="auth",
        nodes=[
            ServiceNode(id="auth", label="Auth"),
            ServiceNode(
                id="login",
                parent_id="auth",
                label="Login",
                value_created="유효한 세션 토큰",
                trigger="사용자가 로그인 버튼을 누른다",
                how="ID/PW 검증 후 세션 발급",
                outcome="홈 화면으로 리다이렉트",
            ),
            ActorRefNode(id="ar-op", label="→ op", ref_actor_id="operator", side="operator"),
            ActorRefNode(id="ar-user", label="→ user", ref_actor_id="user", side="user"),
        ],
    )
    parsed = CanvasDoc.model_validate(detail.model_dump())
    login = next(n for n in parsed.nodes if n.id == "login")
    assert login.trigger.startswith("사용자가")
    assert login.outcome == "홈 화면으로 리다이렉트"


# ---------------------------------------------------------------------------
# v0.10 Step 5 — metric / step composition kinds
# ---------------------------------------------------------------------------


def test_metric_node_carries_typed_fields() -> None:
    n = MetricNode(
        id="m-login-rate",
        label="Login success rate",
        target=">99%",
        measurement="OK 응답 / 전체 요청 (5분 윈도우)",
    )
    assert n.target == ">99%"
    assert "OK 응답" in n.measurement


def test_step_node_carries_typed_fields() -> None:
    n = StepNode(
        id="s-verify",
        label="Verify credentials",
        order=2,
        outcome="세션 토큰 발급 OR 401 반환",
    )
    assert n.order == 2
    assert "세션 토큰" in n.outcome


def test_step_order_optional() -> None:
    """Unordered steps (parallel branches) leave ``order`` at ``None``."""
    n = StepNode(id="s-async", label="Send email")
    assert n.order is None


def test_service_detail_accepts_metric_and_step() -> None:
    CanvasDoc(
        canvas_id="auth",
        canvas_kind="service_detail",
        service_ref="auth",
        nodes=[
            ServiceNode(id="auth", label="Auth"),
            MetricNode(
                id="m1",
                parent_id="auth",
                label="Login success rate",
                target=">99%",
            ),
            StepNode(
                id="s1",
                parent_id="auth",
                label="Verify credentials",
                order=1,
            ),
            ActorRefNode(id="ar-op", label="→ op", ref_actor_id="operator", side="operator"),
            ActorRefNode(id="ar-user", label="→ user", ref_actor_id="user", side="user"),
        ],
    )


def test_metric_requires_service_parent() -> None:
    """Like rule/content, metric/step are composition kinds and must live
    inside a service. Top-level placement is rejected."""
    with pytest.raises(ValueError, match="parent_id"):
        CanvasDoc(
            canvas_id="auth",
            canvas_kind="service_detail",
            service_ref="auth",
            nodes=[
                ServiceNode(id="auth", label="Auth"),
                MetricNode(id="m1", label="Stray"),
            ],
        )


def test_step_requires_service_parent() -> None:
    with pytest.raises(ValueError, match="parent_id"):
        CanvasDoc(
            canvas_id="auth",
            canvas_kind="service_detail",
            service_ref="auth",
            nodes=[
                ServiceNode(id="auth", label="Auth"),
                StepNode(id="s1", label="Stray"),
            ],
        )


def test_services_canvas_rejects_metric() -> None:
    """metric/step belong inside service_detail, not on the overview."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[
                ServiceNode(id="auth", label="Auth"),
                MetricNode(id="m1", label="Stray"),
            ],
        )


# ---------------------------------------------------------------------------
# v0.10 Step 6 — rule + content typed-field polish
# ---------------------------------------------------------------------------


def test_rule_typed_fields_round_trip() -> None:
    n = RuleNode(
        id="r-pwd",
        label="Password policy",
        policy="비밀번호 8자 이상 + 숫자 + 특수문자",
        enforcement="가입 폼 + 비밀번호 변경 화면에서 검증",
        actor_permissions={"user": "RUD", "admin": "CRUD"},
    )
    assert n.policy.startswith("비밀번호 8자")
    assert n.enforcement.startswith("가입 폼")
    assert n.actor_permissions == {"user": "RUD", "admin": "CRUD"}


def test_content_typed_fields_round_trip() -> None:
    n = ContentNode(
        id="c-session",
        label="Session token",
        format="JWT (HS256)",
        producer_actor_id="auth-service",
        consumer_actor_id="user",
    )
    assert n.format == "JWT (HS256)"
    assert n.producer_actor_id == "auth-service"
    assert n.consumer_actor_id == "user"


def test_actor_permissions_default_empty() -> None:
    """A RuleNode without actor_permissions still validates and serialises
    through the SketchNode discriminated union (TypeAdapter dispatch)."""
    n = RuleNode(id="r1", label="R")
    assert n.actor_permissions == {}
    parsed = SketchNodeAdapter.validate_python(n.model_dump())
    assert isinstance(parsed, RuleNode)
    assert parsed.actor_permissions == {}


def test_actor_permissions_round_trip_through_canvas() -> None:
    """Permission dict survives a full CanvasDoc serialise/parse cycle."""
    canvas = CanvasDoc(
        canvas_id="auth",
        canvas_kind="service_detail",
        service_ref="auth",
        nodes=[
            ServiceNode(id="auth", label="Auth"),
            RuleNode(
                id="r1",
                parent_id="auth",
                label="Post permissions",
                policy="자기 글만 수정/삭제",
                actor_permissions={
                    "user": "RUD-self",
                    "admin": "CRUD-all",
                },
            ),
            ActorRefNode(id="ar-op", label="→ op", ref_actor_id="operator", side="operator"),
            ActorRefNode(id="ar-user", label="→ user", ref_actor_id="user", side="user"),
        ],
    )
    parsed = CanvasDoc.model_validate(canvas.model_dump())
    rule = next(n for n in parsed.nodes if n.id == "r1")
    assert rule.actor_permissions["user"] == "RUD-self"
    assert rule.actor_permissions["admin"] == "CRUD-all"


def test_foundation_canvas_rejects_foundation_refs() -> None:
    """Masters live on the Foundation canvas; refs would be a self-loop."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                *_core_seed_nodes(),
                MissionRefNode(id="mr", label="→ M", ref_mission_id="mission"),
            ],
        )


def test_detail_canvas_actor_kind_rejected() -> None:
    """Raw actors belong in the Actor canvas, not Detail."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[
                *_detail_seed(),
                ActorNode(id="a1", label="Raw actor"),
            ],
        )


def test_detail_canvas_missing_root_service_rejected() -> None:
    with pytest.raises(ValueError, match="root service"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[],
        )


# ---------------------------------------------------------------------------
# shared validators (edges + parent_id) still apply
# ---------------------------------------------------------------------------


def test_edges_referencing_unknown_nodes_rejected() -> None:
    with pytest.raises(ValueError, match="unknown nodes"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[ActorNode(id="user", label="U")],
            edges=[SketchEdge(id="e1", source="user", target="ghost")],
        )


# ---------------------------------------------------------------------------
# v0.16.37 — D-2026-05-13-M (anchor edge 422 reject fix)
# ---------------------------------------------------------------------------


def test_edge_from_synthetic_anchor_to_user_node_accepted() -> None:
    """D-2026-05-04-B SPEC mandate: user may draw edges from / to the
    synthetic project anchor like any other node. The anchor itself
    lives in ``ProjectDoc.anchors``, not in ``canvas.nodes`` — the
    validator must whitelist its id so anchor edges don't 422 reject.
    Regression for D-2026-05-13-M (user complaint
    *"새로 고침하면 연결선이 사라지죠"*)."""
    from plot_mcp.models import PROJECT_ANCHOR_ID

    doc = CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="operator", label="Op"),
            ActorNode(id="user", label="U"),
        ],
        edges=[
            SketchEdge(
                id="e_anchor_to_user",
                source=PROJECT_ANCHOR_ID,
                target="user",
            ),
        ],
    )
    assert doc.edges[0].source == PROJECT_ANCHOR_ID
    assert doc.edges[0].target == "user"


def test_edge_from_user_node_to_synthetic_anchor_accepted() -> None:
    """Direction-symmetric companion of the above — D-2026-05-04-B's
    *"from / to the anchor"* covers both directions."""
    from plot_mcp.models import PROJECT_ANCHOR_ID

    doc = CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="operator", label="Op"),
            ActorNode(id="user", label="U"),
        ],
        edges=[
            SketchEdge(
                id="e_user_to_anchor",
                source="user",
                target=PROJECT_ANCHOR_ID,
            ),
        ],
    )
    assert doc.edges[0].target == PROJECT_ANCHOR_ID


def test_dangling_edge_error_message_reports_missing_endpoint_not_edge_id() -> None:
    """v0.16.37 bug fix: prior to D-2026-05-13-M, the validator's error
    message reported *edge ids* (``e_<timestamp>_<rand>``) as if they
    were missing node ids. This sent D-2026-05-13-I diagnosis down a
    wrong path. The fixed message reports the actual missing endpoint
    id."""
    with pytest.raises(ValueError, match=r"'ghost_node'") as exc:
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[ActorNode(id="user", label="U")],
            edges=[
                SketchEdge(
                    id="e_mp2vvxg9_k9cq",  # edge id — must NOT appear in msg
                    source="user",
                    target="ghost_node",
                ),
            ],
        )
    # Edge id must not be in the error message (the old bug).
    assert "e_mp2vvxg9_k9cq" not in str(exc.value)


def test_dangling_edge_reports_multiple_missing_endpoints_sorted() -> None:
    """When multiple edges have different missing endpoints, the error
    message lists each distinct missing id (sorted), not duplicates."""
    with pytest.raises(ValueError, match="unknown nodes") as exc:
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[ActorNode(id="user", label="U")],
            edges=[
                SketchEdge(id="e1", source="user", target="ghost_a"),
                SketchEdge(id="e2", source="ghost_b", target="user"),
                SketchEdge(id="e3", source="user", target="ghost_a"),
            ],
        )
    msg = str(exc.value)
    assert "ghost_a" in msg
    assert "ghost_b" in msg
    # 'user' is a valid node — must NOT be in the error.
    assert "'user'" not in msg
    # Edge ids must NOT appear.
    assert "'e1'" not in msg
    assert "'e2'" not in msg


def test_edge_with_one_anchor_one_ghost_endpoint_reports_only_ghost() -> None:
    """Anchor id is whitelisted; if only the *other* endpoint is
    missing, only that endpoint must appear in the error message."""
    from plot_mcp.models import PROJECT_ANCHOR_ID

    with pytest.raises(ValueError, match="unknown nodes") as exc:
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[ActorNode(id="user", label="U")],
            edges=[
                SketchEdge(
                    id="e_mixed",
                    source=PROJECT_ANCHOR_ID,
                    target="ghost_x",
                ),
            ],
        )
    msg = str(exc.value)
    assert "ghost_x" in msg
    assert PROJECT_ANCHOR_ID not in msg


def test_parent_cycle_rejected() -> None:
    with pytest.raises(ValueError, match="cycle"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                ActorNode(id="a", parent_id="b", label="A"),
                ActorNode(id="b", parent_id="a", label="B"),
            ],
        )
