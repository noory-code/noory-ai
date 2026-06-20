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
    ("service_detail", "actor_ref", "flow"),
    # step / decision / service / category -> flow
    ("service_detail", "step", "flow"),
    ("service_detail", "decision", "flow"),
    ("services", "service", "flow"),
    ("services", "category", "flow"),
    # unknown / None sources -> flow
    ("foundation", None, "flow"),
    ("services", "bogus", "flow"),
]


@pytest.mark.parametrize("canvas_kind,source_kind,expected", _CASES)
def test_classify_edge(canvas_kind: str, source_kind: str | None, expected: str) -> None:
    assert classify_edge(canvas_kind, source_kind) == expected


def test_relation_value_set_matches_viewer() -> None:
    """SSOT guard: the Pydantic ``SketchEdge.relation`` Literal values
    must equal the viewer ``EdgeRelation`` union. The stored field is
    read on both sides (D-2026-05-31-C); the value sets must not drift.
    """
    import re
    import typing
    from pathlib import Path

    from plot_mcp.models import SketchEdge

    py_values = set(typing.get_args(SketchEdge.model_fields["relation"].annotation))

    ts_path = (
        Path(__file__).resolve().parents[1]
        / "viewer"
        / "src"
        / "flow"
        / "edgeSemantics.ts"
    )
    ts_src = ts_path.read_text(encoding="utf-8")
    match = re.search(r"export type EdgeRelation\s*=\s*([^;]+);", ts_src)
    assert match is not None, "EdgeRelation union not found in edgeSemantics.ts"
    ts_values = set(re.findall(r'"([a-z_]+)"', match.group(1)))

    assert py_values == ts_values, (
        f"SketchEdge.relation value set drift — "
        f"py-only={py_values - ts_values}, ts-only={ts_values - py_values}"
    )
