"""Edge semantic taxonomy — default assigner for ``SketchEdge.relation``.

v0.30.0 (D-2026-05-31-C). ``relation`` ("flow" | "injection" |
"inheritance") is STORED on the edge — the one wire SSOT read by both
the viewer (fold / layout / styling) and the server
(``propagation.py`` publish MINOR-bump). A viewer-only derivation would
drift from the server's independent directed-edge hierarchy walk
(plot-design-red-team A8).

``classify_edge`` only decides the DEFAULT when an edge is drawn or
migrated; once stored, ``edge.relation`` is authoritative. This is the
Python mirror of ``viewer/src/flow/edgeSemantics.ts::classifyEdge`` — a
parity test (``tests/test_edge_semantics.py``) keeps the two truth
tables byte-identical.
"""

from __future__ import annotations

# Essence kinds whose outgoing edges inject essence into the target: the
# foundation masters and their consumer-plane refs. ``actor_ref`` is
# deliberately excluded — it is the sequence *subject*, not an overlay
# (mirrors ``foundationRefKinds.FOUNDATION_REF_KINDS`` on the viewer).
ESSENCE_SOURCE_KINDS: frozenset[str] = frozenset(
    {
        "mission",
        "core_value",
        "identity",
        "mission_ref",
        "value_ref",
        "identity_ref",
    }
)


def classify_edge(canvas_kind: str, source_kind: str | None) -> str:
    """Default relation for an edge, from its canvas + source-node kind.

    Order matters: actors-canvas edges are always inheritance (single
    edge type), then essence sources are injection, else flow.
    """
    if canvas_kind == "actors":
        return "inheritance"
    if source_kind is not None and source_kind in ESSENCE_SOURCE_KINDS:
        return "injection"
    return "flow"
