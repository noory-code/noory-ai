"""Edge semantic classifier — v0.30.0 (D-2026-05-31-C).

The truth table here is the byte-for-byte mirror of
``viewer/src/flow/edgeSemantics.ts`` (and its vitest
``tests/edge-semantics.test.ts``). Keeping the two identical is what
lets the stored ``relation`` field be assigned consistently whether an
edge is created in the viewer or migrated on the server.
"""

from __future__ import annotations

import pytest

from plot_mcp.edge_semantics import classify_edge

# (canvas_kind, source_kind) -> expected relation. Mirror of the TS
# vitest cases exactly.
_CASES = [
    # actors canvas: every edge is inheritance (single edge type)
    ("actors", "actor", "inheritance"),
    ("actors", "project", "inheritance"),
    # foundation essence masters -> injection
    ("foundation", "mission", "injection"),
    ("foundation", "core_value", "injection"),
    ("foundation", "identity", "injection"),
    # (mission_ref / value_ref / identity_ref retired 2026-06-20 — D-2026-06-20-G)
    # actor_ref (the subject) is flow, not injection
    ("feature", "actor_ref", "flow"),
    # step / decision / service / category -> flow
    ("feature", "step", "flow"),
    ("feature", "decision", "flow"),
    ("services", "service", "flow"),
    ("services", "category", "flow"),
    # entity↔entity rough relationship (entities canvas) -> flow
    # (D-2026-06-20-Q step 7 / D-2026-06-17-J)
    ("entities", "entity", "flow"),
    # unknown / None sources -> flow
    ("foundation", None, "flow"),
    ("services", "bogus", "flow"),
]


@pytest.mark.parametrize("canvas_kind,source_kind,expected", _CASES)
def test_classify_edge(canvas_kind: str, source_kind: str | None, expected: str) -> None:
    assert classify_edge(canvas_kind, source_kind) == expected


def test_entity_edges_default_to_flow() -> None:
    """D-2026-06-20-Q step 7 — an entity↔entity edge is a rough, directed
    conceptual link (flow), editable; never a meaningless / FK / cardinality
    line. Pins the documented fallthrough so a future classify change can't
    silently re-route entity edges."""
    assert classify_edge("entities", "entity") == "flow"


def test_relation_value_set_is_the_pinned_three() -> None:
    """SSOT guard for the engine half of ``SketchEdge.relation``.

    The stored ``relation`` field is read on both sides (D-2026-05-31-C).
    After the open-core cut (D-2026-06-20-L / -M) the viewer ``EdgeRelation``
    union moved to the app repo, so the former cross-repo regex parity is
    re-homed in the app's vitest (``edge-semantics.test.ts``). This pins the
    engine value set explicitly so neither half can quietly drift from the
    agreed three relations."""
    import typing

    from plot_mcp.models import SketchEdge

    py_values = set(typing.get_args(SketchEdge.model_fields["relation"].annotation))
    assert py_values == {"flow", "injection", "inheritance"}
