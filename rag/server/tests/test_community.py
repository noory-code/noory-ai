"""Unit tests for :mod:`rag_mcp.infrastructure.community_leiden`."""

from __future__ import annotations

from rag_mcp.infrastructure.community_leiden import LeidenCommunityDetector


def test_empty_graph_returns_empty() -> None:
    det = LeidenCommunityDetector()
    assert det.detect([], []) == {}


def test_isolated_nodes_get_distinct_communities() -> None:
    det = LeidenCommunityDetector()
    assignment = det.detect(["a", "b", "c"], [])
    assert set(assignment.keys()) == {"a", "b", "c"}
    assert len(set(assignment.values())) == 3


def test_two_clusters_detected() -> None:
    det = LeidenCommunityDetector()
    nodes = ["a", "b", "c", "x", "y", "z"]
    # Two tight triangles.
    edges = [
        ("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0),
        ("x", "y", 1.0), ("y", "z", 1.0), ("x", "z", 1.0),
    ]
    assignment = det.detect(nodes, edges, seed=7)
    # Membership for the two triangles should be intra-equal, inter-different.
    assert assignment["a"] == assignment["b"] == assignment["c"]
    assert assignment["x"] == assignment["y"] == assignment["z"]
    assert assignment["a"] != assignment["x"]


def test_seed_is_stable() -> None:
    det = LeidenCommunityDetector()
    nodes = ["a", "b", "c", "d"]
    edges = [("a", "b", 1.0), ("c", "d", 1.0)]
    first = det.detect(nodes, edges, seed=42)
    second = det.detect(nodes, edges, seed=42)
    assert first == second
