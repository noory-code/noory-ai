"""Unit tests for :mod:`rag_mcp.infrastructure.graph_kuzu`."""

from __future__ import annotations

from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex


def _open(tmp_state) -> KuzuGraphIndex:
    g = KuzuGraphIndex(tmp_state.graph_dir)
    _ = g.conn  # force init
    return g


def test_entity_upsert_and_find(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_entity("e1", "Riverpod", "library")
    found = g.find_entity_by_name("riverpod")
    assert found is not None
    assert found.id == "e1"
    assert found.type == "library"
    g.close()


def test_chunk_mention_and_lookup(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_chunk("c1", "a.md", 0)
    g.upsert_chunk("c2", "a.md", 1)
    g.upsert_entity("eA", "Riverpod", "library")
    g.upsert_entity("eB", "Notifier", "concept")
    g.mention("c1", "eA")
    g.mention("c1", "eB")
    g.mention("c2", "eA")

    mentioned = g.entities_mentioned_by_chunks(["c1"])
    names = sorted(e.name for e in mentioned)
    assert names == ["Notifier", "Riverpod"]
    g.close()


def test_relate_and_expand(tmp_state) -> None:
    g = _open(tmp_state)
    for ident, name in [("e1", "Riverpod"), ("e2", "Notifier"), ("e3", "Provider")]:
        g.upsert_entity(ident, name, "library")
    g.relate("e1", "e2", weight=2.0)
    g.relate("e2", "e3", weight=1.0)

    sub = g.expand_neighbors(["e1"], depth=2)
    ids = {n.id for n in sub.nodes}
    assert {"e1", "e2", "e3"}.issubset(ids)
    edge_keys = {(s, d) for s, d, _, _ in sub.edges}
    assert ("e1", "e2") in edge_keys
    g.close()


def test_expand_neighbors_depth_zero_is_no_expansion(tmp_state) -> None:
    """depth=0 must be honored (schema minimum is 0), not silently clamped to 1."""
    g = _open(tmp_state)
    for ident, name in [("e1", "Riverpod"), ("e2", "Notifier")]:
        g.upsert_entity(ident, name, "library")
    g.relate("e1", "e2", weight=2.0)

    sub = g.expand_neighbors(["e1"], depth=0)
    assert sub.nodes == []
    assert sub.edges == []
    g.close()


def test_delete_chunks_detaches_mentions(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_entity("e1", "X", "library")
    g.upsert_chunk("c1", "a.md", 0)
    g.mention("c1", "e1")
    assert g.stats()["mentions"] == 1
    g.delete_chunks_by_path("a.md")
    assert g.stats()["mentions"] == 0
    g.close()


def test_chunks_mentioning(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_entity("eA", "Riverpod", "library")
    g.upsert_entity("eB", "Notifier", "concept")
    for cid in ("c1", "c2", "c3"):
        g.upsert_chunk(cid, "a.md", 0)
    g.mention("c1", "eA")
    g.mention("c2", "eA")
    g.mention("c3", "eB")

    assert g.chunks_mentioning("eA") == ["c1", "c2"]
    assert g.chunks_mentioning("eB") == ["c3"]
    assert g.chunks_mentioning("missing") == []
    g.close()


def test_relations_of_returns_both_directions(tmp_state) -> None:
    g = _open(tmp_state)
    for ident in ("e1", "e2", "e3"):
        g.upsert_entity(ident, ident.upper(), "concept")
    g.relate("e1", "e2", rtype="USES", weight=2.0)
    g.relate("e3", "e1", rtype="DEPENDS_ON", weight=1.5)
    g.relate("e2", "e3", rtype="USES", weight=9.0)  # not incident to e1

    rels = set(g.relations_of("e1"))
    assert rels == {("e1", "e2", "USES", 2.0), ("e3", "e1", "DEPENDS_ON", 1.5)}
    g.close()


def test_relate_same_pair_distinct_types_coexist(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_entity("e1", "A", "concept")
    g.upsert_entity("e2", "B", "concept")
    g.relate("e1", "e2", rtype="USES", weight=2.0)
    g.relate("e1", "e2", rtype="DEPENDS_ON", weight=1.0)
    g.relate("e1", "e2", rtype="USES", weight=3.0)  # same type: update in place

    edges = set(g.expand_neighbors(["e1"], depth=1).edges)
    assert ("e1", "e2", "USES", 3.0) in edges
    assert ("e1", "e2", "DEPENDS_ON", 1.0) in edges
    assert g.stats()["relations"] == 2
    g.close()


def test_relate_before_endpoints_creates_stub_entities(tmp_state) -> None:
    """A relation upserted before its endpoint entities must not be dropped:
    relate() merges stub Entity nodes so the edge lands with type/weight/direction."""
    g = _open(tmp_state)
    g.relate("eA", "eB", rtype="USES", weight=2.5)

    stats = g.stats()
    assert stats["relations"] == 1
    assert stats["entities"] == 2
    assert set(g.relations_of("eA")) == {("eA", "eB", "USES", 2.5)}
    g.close()


def test_relate_stub_enriched_by_later_upsert_keeps_relation(tmp_state) -> None:
    """A later real upsert_entity enriches the stub in place — the relation
    survives and no duplicate node appears."""
    g = _open(tmp_state)
    g.relate("eA", "eB", rtype="USES", weight=2.5)
    g.upsert_entity("eA", "Alpha", "library")
    g.upsert_entity("eB", "Beta", "concept")

    found = g.find_entity_by_name("Alpha")
    assert found is not None
    assert found.id == "eA"
    assert found.type == "library"
    assert set(g.relations_of("eA")) == {("eA", "eB", "USES", 2.5)}
    assert g.stats()["entities"] == 2
    g.close()


def test_relate_with_one_existing_endpoint_stubs_only_missing(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_entity("eA", "Alpha", "library")
    g.relate("eA", "eB", rtype="DEPENDS_ON", weight=1.5)

    stats = g.stats()
    assert stats["relations"] == 1
    assert stats["entities"] == 2
    found = g.find_entity_by_name("Alpha")
    assert found is not None and found.type == "library"  # untouched by relate()
    assert set(g.relations_of("eB")) == {("eA", "eB", "DEPENDS_ON", 1.5)}
    g.close()


def test_list_entities_filter(tmp_state) -> None:
    g = _open(tmp_state)
    g.upsert_entity("e1", "Riverpod", "library")
    g.upsert_entity("e2", "Drift", "library")
    g.upsert_entity("e3", "RiverpodNotifier", "concept")
    rows = g.list_entities(q="river")
    names = {r.name for r in rows}
    assert "Riverpod" in names and "RiverpodNotifier" in names and "Drift" not in names
    g.close()
