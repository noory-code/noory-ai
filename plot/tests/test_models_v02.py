"""v0.2 model validators — kind, parent_id, composition rules."""

from __future__ import annotations

import pytest

from plot_mcp.models import SketchDoc, SketchEdge, SketchNode


def _base_nodes(extra: list[SketchNode] | None = None) -> list[SketchNode]:
    return [
        SketchNode(id="svc-a", kind="service", label="Service A"),
        SketchNode(id="actor-h", kind="actor", label="Hero"),
        *(extra or []),
    ]


def test_v01_files_load_with_none_kind() -> None:
    """Legacy v0.1 sketches have no kind field — must still validate."""
    doc = SketchDoc(
        id="legacy",
        nodes=[
            SketchNode(id="n1", label="Anon"),
            SketchNode(id="n2", label="Also anon"),
        ],
    )
    assert all(n.kind is None and n.parent_id is None for n in doc.nodes)


def test_rule_inside_service_ok() -> None:
    SketchDoc(
        id="ok",
        nodes=_base_nodes(
            [SketchNode(id="r1", kind="rule", parent_id="svc-a", label="Pricing")]
        ),
    )


def test_content_inside_service_ok() -> None:
    SketchDoc(
        id="ok",
        nodes=_base_nodes(
            [SketchNode(id="c1", kind="content", parent_id="svc-a", label="Image")]
        ),
    )


def test_rule_without_parent_rejected() -> None:
    with pytest.raises(ValueError, match="requires a parent_id"):
        SketchDoc(
            id="bad",
            nodes=_base_nodes(
                [SketchNode(id="r1", kind="rule", label="Free-floating rule")]
            ),
        )


def test_rule_inside_actor_rejected() -> None:
    with pytest.raises(ValueError, match="must be a child of a service"):
        SketchDoc(
            id="bad",
            nodes=_base_nodes(
                [SketchNode(id="r1", kind="rule", parent_id="actor-h", label="X")]
            ),
        )


def test_sub_service_inside_service_ok() -> None:
    """Decomposition: a service nested under another service."""
    SketchDoc(
        id="ok",
        nodes=_base_nodes(
            [SketchNode(id="svc-b", kind="service", parent_id="svc-a", label="Sub")]
        ),
    )


def test_sub_actor_inside_actor_ok() -> None:
    SketchDoc(
        id="ok",
        nodes=_base_nodes(
            [SketchNode(id="actor-h2", kind="actor", parent_id="actor-h", label="Team")]
        ),
    )


def test_parent_id_self_rejected() -> None:
    with pytest.raises(ValueError, match="cannot be its own parent"):
        SketchDoc(
            id="bad",
            nodes=[SketchNode(id="n1", kind="service", parent_id="n1", label="Loop")],
        )


def test_parent_id_unknown_rejected() -> None:
    with pytest.raises(ValueError, match="points to unknown node"):
        SketchDoc(
            id="bad",
            nodes=[
                SketchNode(id="n1", kind="service", parent_id="ghost", label="A"),
            ],
        )


def test_parent_chain_cycle_rejected() -> None:
    """a -> b -> a must raise."""
    with pytest.raises(ValueError, match="cycle"):
        SketchDoc(
            id="bad",
            nodes=[
                SketchNode(id="a", kind="service", parent_id="b", label="A"),
                SketchNode(id="b", kind="service", parent_id="a", label="B"),
            ],
        )


def test_edge_value_form_round_trip() -> None:
    doc = SketchDoc(
        id="ok",
        nodes=_base_nodes(),
        edges=[
            SketchEdge(
                id="e1",
                source="actor-h",
                target="svc-a",
                action_verb="create",
                value_form=["effort", "cognitive"],
            )
        ],
    )
    assert doc.edges[0].value_form == ["effort", "cognitive"]
    assert doc.edges[0].action_verb == "create"


def test_edge_defaults_when_absent() -> None:
    doc = SketchDoc(
        id="ok",
        nodes=_base_nodes(),
        edges=[SketchEdge(id="e1", source="actor-h", target="svc-a")],
    )
    assert doc.edges[0].action_verb is None
    assert doc.edges[0].value_form == []


def test_collapsed_default_false() -> None:
    doc = SketchDoc(id="ok", nodes=_base_nodes())
    assert all(n.collapsed is False for n in doc.nodes)
