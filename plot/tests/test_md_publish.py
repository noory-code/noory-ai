"""v0.18.0 Phase 3 (D-2026-05-16-E) — uniform MD render tests.

Covers ``plot_mcp.md_publish.render_node_md`` + ``published_md_path`` +
``can_publish`` + ``bump_major``. Parametric over the 15-kind union.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from plot_mcp.md_publish import (
    bump_major,
    bump_minor,
    can_publish,
    published_md_path,
    render_node_md,
)
from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
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
    StepNode,
    ValueRefNode,
)

# ---------------------------------------------------------------------------
# bump_major
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "from_v,to_v",
    [
        ("v1.0", "v2.0"),
        ("v2.3", "v3.0"),
        ("v0.1", "v1.0"),
        ("v9.7", "v10.0"),
        ("v100.500", "v101.0"),
    ],
)
def test_bump_major_basic(from_v: str, to_v: str) -> None:
    assert bump_major(from_v) == to_v


def test_bump_major_rejects_malformed() -> None:
    with pytest.raises(ValueError, match="invalid version format"):
        bump_major("1.0")
    with pytest.raises(ValueError, match="invalid version format"):
        bump_major("v1")


# ---------------------------------------------------------------------------
# bump_minor — v0.20.0 Phase 4 (D-2026-05-17-C)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "from_v,to_v",
    [
        ("v1.0", "v1.1"),
        ("v2.3", "v2.4"),
        ("v0.0", "v0.1"),
        ("v9.7", "v9.8"),
        ("v100.500", "v100.501"),
    ],
)
def test_bump_minor_basic(from_v: str, to_v: str) -> None:
    assert bump_minor(from_v) == to_v


def test_bump_minor_preserves_major() -> None:
    """MAJOR component stays put; only MINOR increments."""
    assert bump_minor("v9.4") == "v9.5"
    assert bump_minor("v42.0") == "v42.1"


def test_bump_minor_rejects_malformed() -> None:
    with pytest.raises(ValueError, match="invalid version format"):
        bump_minor("1.0")
    with pytest.raises(ValueError, match="invalid version format"):
        bump_minor("v1")


# ---------------------------------------------------------------------------
# can_publish — eligibility table per D-2026-05-16-E §1.2
# ---------------------------------------------------------------------------


def test_can_publish_rejects_project_anchor() -> None:
    assert can_publish(ProjectNode(id="p1")) is False


def test_can_publish_rejects_is_root() -> None:
    assert can_publish(ActorNode(id="actor-root", is_root=True)) is False
    assert can_publish(ServiceNode(id="svc-root", is_root=True)) is False


@pytest.mark.parametrize(
    "ref_cls",
    [ActorRefNode, MissionRefNode, ValueRefNode, IdentityRefNode],
)
def test_can_publish_rejects_ref_kinds(ref_cls: type) -> None:
    # ref nodes require their ``ref_*_id`` field; supply a placeholder.
    kw = {f: "target-id" for f in ref_cls.model_fields if f.startswith("ref_")}
    node = ref_cls(id="ref-1", **kw)
    assert can_publish(node) is False


def test_can_publish_accepts_typical_kinds() -> None:
    assert can_publish(MissionNode(id="m1")) is True
    assert can_publish(CoreValueNode(id="cv1")) is True
    assert can_publish(IdentityNode(id="id1")) is True
    assert can_publish(ActorNode(id="a1", is_root=False)) is True
    assert can_publish(ServiceNode(id="s1", is_root=False)) is True
    assert can_publish(CategoryNode(id="c1")) is True
    assert can_publish(MetricNode(id="metric1")) is True
    assert can_publish(StepNode(id="step1")) is True
    assert can_publish(RuleNode(id="r1")) is True
    assert can_publish(ContentNode(id="cn1")) is True


# ---------------------------------------------------------------------------
# render_node_md — shape parametrised across kinds
# ---------------------------------------------------------------------------


def test_render_mission_full_round_trip() -> None:
    node = MissionNode(
        id="msn_xyz789",
        label="Tolerance",
        version="v2.0",
        what_we_do="We listen first.",
        why="To preserve diverse opinions.",
        direction="Listen → respond → reflect.",
        body="Free-form rationale paragraph.",
    )
    md = render_node_md(node, canvas="foundation")

    # frontmatter parse
    parts = md.split("---", 2)
    assert parts[0] == "" and parts[1].strip() and parts[2].strip()
    fm = yaml.safe_load(parts[1])
    assert fm["id"] == "msn_xyz789"
    assert fm["kind"] == "mission"
    assert fm["version"] == "v2.0"
    assert fm["label"] == "Tolerance"
    assert fm["parent_id"] is None
    assert fm["canvas"] == "foundation"
    assert "published_at" in fm

    # H2 sections — 4 typed fields (what_we_do / why / direction / body)
    body = parts[2]
    assert "## What we do" in body
    assert "## Why" in body
    assert "## Direction" in body
    assert "## Body" in body
    assert "We listen first." in body
    assert "Free-form rationale paragraph." in body


def test_render_step_with_non_string_field_emits_inline_yaml() -> None:
    """``order: int`` (StepNode) must round-trip via inline YAML inside
    the H2 body."""
    node = StepNode(id="s1", label="Sign in", order=2, outcome="session")
    md = render_node_md(node, canvas="services")
    # ``order`` field renders as YAML scalar; ``outcome`` as raw string.
    assert "## Order" in md
    assert "## Outcome" in md
    assert "session" in md
    # ``order: 2`` somewhere after ## Order heading.
    order_section = md.split("## Order", 1)[1].split("## Outcome", 1)[0]
    assert order_section.strip() == "2"


def test_render_rule_with_dict_field_emits_inline_yaml() -> None:
    node = RuleNode(
        id="r1",
        label="GDPR",
        policy="explicit consent",
        enforcement="checkbox",
        actor_permissions={"user": "RUD", "admin": "CRUD"},
    )
    md = render_node_md(node, canvas="foundation")
    assert "## Actor permissions" in md
    perm_section = md.split("## Actor permissions", 1)[1]
    # YAML dict serialised as multi-line key: value
    assert "user: RUD" in perm_section
    assert "admin: CRUD" in perm_section


def test_render_empty_typed_fields_keep_headings() -> None:
    """Empty fields emit the H2 heading with no body — keeps the
    per-kind MD shape stable across publish versions."""
    node = MissionNode(id="m1", label="Mission")  # all typed fields empty
    md = render_node_md(node, canvas="foundation")
    assert "## What we do" in md
    assert "## Why" in md
    assert "## Direction" in md
    assert "## Body" in md
    # All sections present even though empty — diff-friendly invariant.
    h2_count = md.count("\n## ")
    assert h2_count == 4


@pytest.mark.parametrize(
    "cls,extra",
    [
        (MissionNode, {}),
        (CoreValueNode, {}),
        (IdentityNode, {}),
        (ActorNode, {}),
        (ServiceNode, {}),
        (CategoryNode, {}),
        (MetricNode, {}),
        (StepNode, {}),
        (RuleNode, {}),
        (ContentNode, {}),
    ],
)
def test_render_yaml_frontmatter_has_all_7_keys(cls: type, extra: dict) -> None:
    """Frontmatter contract: every published MD has exactly 7 YAML keys
    in the canonical order Phase 4 / 5 parsers depend on."""
    node = cls(id="n1", label="L", version="v1.0", **extra)
    md = render_node_md(node, canvas="foundation")
    fm = yaml.safe_load(md.split("---", 2)[1])
    expected = {"id", "kind", "version", "label", "parent_id", "canvas", "published_at"}
    assert set(fm.keys()) == expected


# ---------------------------------------------------------------------------
# published_md_path
# ---------------------------------------------------------------------------


def test_published_md_path_uses_kind_node_id_version(tmp_path: Path) -> None:
    """v0.24.3 (D-2026-05-18-A): layout is ``published/<kind>/<node_id>/<version>.md``."""
    p = published_md_path(
        tmp_path / "foundation",
        kind="mission",
        node_id="mission",
        version="v2.0",
    )
    assert p == tmp_path / "foundation" / "published" / "mission" / "mission" / "v2.0.md"


def test_published_md_path_uses_node_id_verbatim_for_ascii_safety(tmp_path: Path) -> None:
    """The path uses node id directly — no slugification. Node ids are
    ASCII per Plot's id policy; even if a user smuggles non-ASCII in,
    the path reflects exactly what they typed (no surprise transform)."""
    p = published_md_path(
        tmp_path / "foundation",
        kind="core_value",
        node_id="core-tolerance",
        version="v1.0",
    )
    assert p == tmp_path / "foundation" / "published" / "core_value" / "core-tolerance" / "v1.0.md"


def test_published_md_path_handles_id_with_dashes(tmp_path: Path) -> None:
    p = published_md_path(
        tmp_path / "foundation",
        kind="core_value",
        node_id="core-value-1",
        version="v3.0",
    )
    assert p == tmp_path / "foundation" / "published" / "core_value" / "core-value-1" / "v3.0.md"
