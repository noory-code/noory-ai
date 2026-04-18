"""Tests for the workspace → Graph parser."""

from __future__ import annotations

import json
from pathlib import Path

from solera_map.graph import (
    build_graph,
    parse_frontmatter,
    parse_sections,
    read_concept_graph,
    read_concepts,
    read_milestones,
    read_releases,
    read_stories,
)

# ---------------------------------------------------------------------------
# Unit: markdown helpers
# ---------------------------------------------------------------------------


def test_parse_frontmatter_roundtrip() -> None:
    text = "---\nfoo: bar\nnums:\n  - 1\n  - 2\n---\nBody line\n"
    fm, body = parse_frontmatter(text)
    assert fm == {"foo": "bar", "nums": [1, 2]}
    assert body == "Body line\n"


def test_parse_frontmatter_absent() -> None:
    fm, body = parse_frontmatter("# Hello\n")
    assert fm == {}
    assert body == "# Hello\n"


def test_parse_sections_splits_on_h1() -> None:
    body = "# Intent\nthe north star\n\n# Current Design\na thing\n\n# Current Shape\nanother\n"
    sections = parse_sections(body)
    assert sections["Intent"] == "the north star"
    assert sections["Current Design"] == "a thing"
    assert sections["Current Shape"] == "another"


# ---------------------------------------------------------------------------
# Fixture helper
# ---------------------------------------------------------------------------


def _write_concept(workspace: Path, concept_id: str, status: str = "active") -> None:
    d = workspace / "concepts"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{concept_id}.md").write_text(
        f"---\n"
        f"id: {concept_id}\n"
        f"name: {concept_id.title()}\n"
        f"status: {status}\n"
        f"created: 2026-04-01\n"
        f"---\n\n"
        f"# Intent\nNorth star for {concept_id}.\n\n"
        f"# Current Design\nIdeal for {concept_id}.\n\n"
        f"# Current Shape\nBuilt so far for {concept_id}.\n\n"
        f"# Horizon\nFuture of {concept_id}.\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Concepts
# ---------------------------------------------------------------------------


def test_read_concepts_parses_sections(tmp_path: Path) -> None:
    _write_concept(tmp_path, "authentication")
    _write_concept(tmp_path, "search")

    concepts = read_concepts(tmp_path)

    assert {c.id for c in concepts} == {"authentication", "search"}
    auth = next(c for c in concepts if c.id == "authentication")
    assert auth.intent == "North star for authentication."
    assert auth.current_design == "Ideal for authentication."
    assert auth.current_shape == "Built so far for authentication."
    assert auth.horizon == "Future of authentication."
    assert auth.status == "active"
    assert auth.parent is None


def test_read_concepts_captures_parent(tmp_path: Path) -> None:
    d = tmp_path / "concepts"
    d.mkdir(parents=True)
    (d / "app.md").write_text(
        "---\nid: app\nname: App\nstatus: active\n---\n\n# Intent\nTop.\n",
        encoding="utf-8",
    )
    (d / "me-tab.md").write_text(
        "---\nid: me-tab\nname: Me Tab\nstatus: active\nparent: app\n---\n\n# Intent\nChild.\n",
        encoding="utf-8",
    )
    (d / "profile.md").write_text(
        "---\nid: profile\nname: Profile\nstatus: active\nparent: me-tab\n---\n\n"
        "# Intent\nGrandchild.\n",
        encoding="utf-8",
    )

    concepts = {c.id: c for c in read_concepts(tmp_path)}

    assert concepts["app"].parent is None
    assert concepts["me-tab"].parent == "app"
    assert concepts["profile"].parent == "me-tab"


def test_read_concepts_skips_index_file(tmp_path: Path) -> None:
    _write_concept(tmp_path, "foo")
    (tmp_path / "concepts" / "_index.md").write_text("# index\n", encoding="utf-8")

    concepts = read_concepts(tmp_path)

    assert {c.id for c in concepts} == {"foo"}


def test_read_concepts_missing_dir_returns_empty(tmp_path: Path) -> None:
    assert read_concepts(tmp_path) == []


# ---------------------------------------------------------------------------
# Concept edges
# ---------------------------------------------------------------------------


def test_read_concept_graph(tmp_path: Path) -> None:
    (tmp_path / "concept-graph.json").write_text(
        json.dumps(
            {
                "edges": [
                    {
                        "from": "auth",
                        "to": "profile",
                        "label": "depends on",
                        "created": "2026-04-18",
                    },
                    {"from": "auth", "to": "onboarding", "label": "used by"},
                ]
            }
        ),
        encoding="utf-8",
    )

    edges = read_concept_graph(tmp_path)

    assert len(edges) == 2
    assert edges[0].from_id == "auth"
    assert edges[0].to_id == "profile"
    assert edges[0].label == "depends on"
    assert edges[0].created == "2026-04-18"
    assert edges[1].label == "used by"
    # Each edge has a unique id
    assert edges[0].id != edges[1].id


def test_read_concept_graph_missing(tmp_path: Path) -> None:
    assert read_concept_graph(tmp_path) == []


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------


def test_read_milestones(tmp_path: Path) -> None:
    d = tmp_path / "milestones"
    d.mkdir()
    (d / "mvp.md").write_text(
        "---\nid: mvp\nname: MVP\nstatus: agreed\n---\n\n"
        "# Scope\n- authentication\n- onboarding\n\n"
        "# Exit Criteria\nAll concepts painted.\n",
        encoding="utf-8",
    )

    milestones = read_milestones(tmp_path)

    assert len(milestones) == 1
    assert milestones[0].id == "mvp"
    assert milestones[0].status == "agreed"
    assert milestones[0].scope == ["authentication", "onboarding"]


def test_read_milestones_with_wikilink_scope(tmp_path: Path) -> None:
    """Support Obsidian-style `[[../concepts/id]]` scope entries (banas-style)."""
    d = tmp_path / "milestones"
    d.mkdir()
    (d / "pre-v3.md").write_text(
        "---\nid: pre-v3\nname: Pre-v3\nstatus: released\n---\n\n"
        "# Scope\n"
        "- [[../concepts/authentication]] — as of v3 migration\n"
        "- [[../concepts/admin]]\n"
        "- [[../concepts/onboarding|Onboarding label]] — note\n",
        encoding="utf-8",
    )

    milestones = read_milestones(tmp_path)

    assert milestones[0].scope == ["authentication", "admin", "onboarding"]


def test_parse_frontmatter_handles_malformed_yaml() -> None:
    """Real banas workspace has unquoted titles with colons; don't hard-fail."""
    text = "---\ntitle: TS-001: 인증\nid: ts-001\n---\nBody\n"

    fm, body = parse_frontmatter(text)

    # Malformed YAML collapses to empty dict; body still usable.
    assert fm == {}
    assert body == "Body\n"


# ---------------------------------------------------------------------------
# Stories + Action Items
# ---------------------------------------------------------------------------


def test_read_stories_and_acts(tmp_path: Path) -> None:
    story_dir = tmp_path / "stories" / "US-001-google-login"
    story_dir.mkdir(parents=True)
    (story_dir / "_story.md").write_text(
        "---\n"
        "id: US-001\n"
        "name: google-login\n"
        "type: US\n"
        "status: 🔄\n"
        "contributes_to: [authentication]\n"
        "belongs_to: mvp\n"
        "---\n\n"
        "# Story\nBody.\n",
        encoding="utf-8",
    )
    (story_dir / "ACT-001-provider.md").write_text(
        "---\nid: ACT-001\nname: provider\nstatus: ✅\n---\n",
        encoding="utf-8",
    )
    (story_dir / "ACT-002-screen.md").write_text(
        "---\nid: ACT-002\nname: screen\nstatus: 🔄\ndepends_on: [ACT-001]\n---\n",
        encoding="utf-8",
    )

    stories, acts = read_stories(tmp_path)

    assert len(stories) == 1
    s = stories[0]
    assert s.id == "US-001"
    assert s.status == "in_progress"
    assert s.contributes_to == ["authentication"]
    assert s.belongs_to == "mvp"

    assert {a.id for a in acts} == {"ACT-001", "ACT-002"}
    done = next(a for a in acts if a.id == "ACT-001")
    assert done.status == "complete"
    chain = next(a for a in acts if a.id == "ACT-002")
    assert chain.depends_on == ["ACT-001"]
    assert chain.story_id == "US-001"


# ---------------------------------------------------------------------------
# Releases
# ---------------------------------------------------------------------------


def test_read_releases(tmp_path: Path) -> None:
    tag_dir = tmp_path / "releases" / "v0.1-mvp"
    tag_dir.mkdir(parents=True)
    (tag_dir / ".released").write_text(
        "release_tag: v0.1-mvp\n"
        "milestone_id: mvp\n"
        "released_at: 2026-04-18 10:00\n"
        "by: solera-release v1.0.1\n",
        encoding="utf-8",
    )

    releases = read_releases(tmp_path)

    assert len(releases) == 1
    assert releases[0].tag == "v0.1-mvp"
    assert releases[0].milestone_id == "mvp"


def test_read_releases_skips_dirs_without_marker(tmp_path: Path) -> None:
    incomplete = tmp_path / "releases" / "v0.2-wip"
    incomplete.mkdir(parents=True)
    # no .released marker

    assert read_releases(tmp_path) == []


# ---------------------------------------------------------------------------
# build_graph aggregate
# ---------------------------------------------------------------------------


def test_build_graph_end_to_end(tmp_path: Path) -> None:
    _write_concept(tmp_path, "authentication")
    _write_concept(tmp_path, "search")
    (tmp_path / "concept-graph.json").write_text(
        json.dumps({"edges": [{"from": "authentication", "to": "search", "label": "uses"}]}),
        encoding="utf-8",
    )

    graph = build_graph(tmp_path)

    assert {c.id for c in graph.concepts} == {"authentication", "search"}
    assert len(graph.concept_edges) == 1
    assert graph.concept_edges[0].label == "uses"
    assert graph.milestones == []
    assert graph.stories == []
    assert graph.releases == []
