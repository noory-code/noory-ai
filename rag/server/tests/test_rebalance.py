"""Unit tests for :class:`rag_mcp.application.rebalancer.Rebalancer`."""

from __future__ import annotations

from rag_mcp.application.rebalancer import (
    MergeDecision,
    Rebalancer,
    SummaryDecision,
)
from rag_mcp.infrastructure.community_leiden import LeidenCommunityDetector
from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex


def _open_graph(tmp_state) -> KuzuGraphIndex:
    g = KuzuGraphIndex(tmp_state.graph_dir)
    _ = g.conn
    return g


def test_prep_surfaces_aliases_and_communities(tmp_state) -> None:
    g = _open_graph(tmp_state)
    # Two entities with same lowercased name → alias candidate.
    g.upsert_entity("e1", "Riverpod", "library")
    g.upsert_entity("e2", "riverpod", "library")
    # An unrelated tight cluster.
    g.upsert_entity("t1", "MockTail", "library")
    g.upsert_entity("t2", "Patrol", "library")
    g.upsert_entity("t3", "WidgetTest", "library")
    g.relate("t1", "t2", weight=1.0)
    g.relate("t2", "t3", weight=1.0)
    g.relate("t1", "t3", weight=1.0)

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    prep = rb.prep()
    alias_pairs = {(c.keep_id, c.drop_id) for c in prep.alias_candidates}
    assert alias_pairs == {("e1", "e2")}
    assert prep.communities, "Leiden should produce at least one community"
    g.close()


def test_commit_merges_entities(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "Riverpod", "library")
    g.upsert_entity("e2", "riverpod", "library")
    g.upsert_entity("e3", "Notifier", "concept")
    g.relate("e2", "e3", weight=1.0)

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    result = rb.commit([MergeDecision(keep_id="e1", drop_id="e2")], summaries=[])
    assert result.merged == 1

    # e2 is gone; e1 now connects to e3.
    assert g.find_entity_by_name("riverpod").id == "e1"  # keeps "Riverpod" name
    names = {e.name for e in g.expand_neighbors(["e1"], depth=1).nodes}
    assert "Notifier" in names
    g.close()


def test_merge_repoints_mentions_to_kept_entity(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "AuthFlow", "concept")
    g.upsert_entity("e2", "authflow", "concept")
    g.upsert_chunk("c1", "a.md", 0)
    g.mention("c1", "e2")

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    rb.commit([MergeDecision(keep_id="e1", drop_id="e2")], summaries=[])

    mentioned = {e.id for e in g.entities_mentioned_by_chunks(["c1"])}
    assert mentioned == {"e1"}, "chunk mention must survive the merge, repointed to keep"
    assert g.stats()["mentions"] == 1
    g.close()


def test_merge_preserves_relation_type_weight_direction(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "AuthFlow", "concept")
    g.upsert_entity("e2", "authflow", "concept")
    g.upsert_entity("e3", "Session", "concept")
    g.upsert_entity("e4", "LoginPage", "concept")
    g.relate("e2", "e3", rtype="USES", weight=2.5)  # outgoing from drop
    g.relate("e4", "e2", rtype="DEPENDS_ON", weight=3.0)  # incoming to drop

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    rb.commit([MergeDecision(keep_id="e1", drop_id="e2")], summaries=[])

    edges = set(g.expand_neighbors(["e1"], depth=1).edges)
    assert ("e1", "e3", "USES", 2.5) in edges
    assert ("e4", "e1", "DEPENDS_ON", 3.0) in edges
    g.close()


def test_merge_drops_self_loop(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "AuthFlow", "concept")
    g.upsert_entity("e2", "authflow", "concept")
    g.relate("e1", "e2", rtype="ALIAS_OF", weight=1.0)
    g.relate("e2", "e1", rtype="ALIAS_OF", weight=1.0)

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    rb.commit([MergeDecision(keep_id="e1", drop_id="e2")], summaries=[])

    assert all(src != dst for src, dst, _ in g.all_edges()), "no keep->keep self-loop"
    assert g.stats()["relations"] == 0
    g.close()


def test_merge_dedups_mentions_when_chunk_mentions_both(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "AuthFlow", "concept")
    g.upsert_entity("e2", "authflow", "concept")
    g.upsert_chunk("c1", "a.md", 0)
    g.mention("c1", "e1")
    g.mention("c1", "e2")

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    rb.commit([MergeDecision(keep_id="e1", drop_id="e2")], summaries=[])

    assert g.stats()["mentions"] == 1, "chunk already mentioning keep must not get a dup"
    assert {e.id for e in g.entities_mentioned_by_chunks(["c1"])} == {"e1"}
    g.close()


def test_merge_keeps_higher_weight_on_relation_collision(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "AuthFlow", "concept")
    g.upsert_entity("e2", "authflow", "concept")
    g.upsert_entity("e3", "Session", "concept")
    g.relate("e1", "e3", rtype="USES", weight=1.0)
    g.relate("e2", "e3", rtype="USES", weight=5.0)

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    rb.commit([MergeDecision(keep_id="e1", drop_id="e2")], summaries=[])

    assert g.stats()["relations"] == 1
    edges = set(g.expand_neighbors(["e1"], depth=1).edges)
    assert ("e1", "e3", "USES", 5.0) in edges, "same (src, rel_type, dst): higher weight wins"
    g.close()


def test_commit_summary_propagates_to_members(tmp_state) -> None:
    g = _open_graph(tmp_state)
    g.upsert_entity("e1", "A", "library", community_id=7)
    g.upsert_entity("e2", "B", "library", community_id=7)

    rb = Rebalancer(graph=g, community=LeidenCommunityDetector())
    rb.commit(
        merges=[],
        summaries=[SummaryDecision(community_id=7, summary="topic about A and B")],
    )
    rows = g.list_entities(community_id=7)
    assert all(r.summary == "topic about A and B" for r in rows)
    g.close()
