"""v0.23.0 (D-2026-05-17-I) — published-versions list endpoint + migration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from plot_mcp.folder_io import (
    _migrate_published_flat_to_kind_slug,
    create_project,
    publish_node,
    read_canvas,
)
from plot_mcp.http_app import create_http_app


@pytest.fixture()
def plot_root(tmp_path: Path) -> Path:
    plot = tmp_path / ".plot"
    plot.mkdir()
    return plot


@pytest.fixture()
def client(plot_root: Path) -> TestClient:
    app = create_http_app()
    return TestClient(app)


def _foundation_mission_id(plot_root: Path, project_id: str) -> str:
    canvas = read_canvas(plot_root, project_id, "foundation")
    return next(n.id for n in canvas.nodes if n.kind == "mission")


# ---------------------------------------------------------------------------
# new layout — published_md_path writes to <kind>/<slug>/<version>.md
# ---------------------------------------------------------------------------


def test_publish_node_writes_to_kind_slug_version_layout(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)
    expected = plot_root / "alpha" / "foundation" / "published" / "mission" / "mission" / "v2.0.md"
    assert expected.is_file()


def test_publish_node_three_times_creates_three_version_files(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)
    publish_node(plot_root, "alpha", "foundation", mid)
    publish_node(plot_root, "alpha", "foundation", mid)
    slug_dir = plot_root / "alpha" / "foundation" / "published" / "mission" / "mission"
    versions = sorted(p.name for p in slug_dir.iterdir())
    assert versions == ["v2.0.md", "v3.0.md", "v4.0.md"]


# ---------------------------------------------------------------------------
# migration — legacy flat files move into the new layout
# ---------------------------------------------------------------------------


def test_migration_moves_legacy_flat_files(plot_root: Path) -> None:
    """A pre-v0.23.0 layout (<canvas>/published/<kind>-<slug>-vN.M.md) is
    moved to <canvas>/published/<kind>/<slug>/vN.M.md on first call."""
    canvas_dir = plot_root / "alpha" / "foundation"
    pub = canvas_dir / "published"
    pub.mkdir(parents=True)
    (pub / "mission-mission-v2.0.md").write_text("old", encoding="utf-8")
    (pub / "mission-mission-v3.0.md").write_text("old", encoding="utf-8")
    (pub / "identity-voice-v1.0.md").write_text("old", encoding="utf-8")

    _migrate_published_flat_to_kind_slug(canvas_dir)

    assert (pub / "mission" / "mission" / "v2.0.md").is_file()
    assert (pub / "mission" / "mission" / "v3.0.md").is_file()
    assert (pub / "identity" / "voice" / "v1.0.md").is_file()
    # Legacy files removed (renamed).
    assert not (pub / "mission-mission-v2.0.md").exists()
    assert not (pub / "identity-voice-v1.0.md").exists()


def test_migration_is_idempotent(plot_root: Path) -> None:
    canvas_dir = plot_root / "alpha" / "foundation"
    pub = canvas_dir / "published"
    pub.mkdir(parents=True)
    (pub / "mission-mission-v2.0.md").write_text("old", encoding="utf-8")

    _migrate_published_flat_to_kind_slug(canvas_dir)
    # Second call must be a no-op (no flat files left to scan).
    _migrate_published_flat_to_kind_slug(canvas_dir)
    assert (pub / "mission" / "mission" / "v2.0.md").is_file()


def test_migration_skips_when_destination_exists(plot_root: Path) -> None:
    """If the new layout already has a file for the same version, the
    legacy file is left in place (no overwrite)."""
    canvas_dir = plot_root / "alpha" / "foundation"
    pub = canvas_dir / "published"
    (pub / "mission" / "mission").mkdir(parents=True)
    (pub / "mission" / "mission" / "v2.0.md").write_text("new", encoding="utf-8")
    (pub / "mission-mission-v2.0.md").write_text("legacy", encoding="utf-8")

    _migrate_published_flat_to_kind_slug(canvas_dir)

    assert (pub / "mission" / "mission" / "v2.0.md").read_text() == "new"
    # Legacy file preserved when destination already occupied.
    assert (pub / "mission-mission-v2.0.md").read_text() == "legacy"


def test_migration_ignores_non_matching_files(plot_root: Path) -> None:
    canvas_dir = plot_root / "alpha" / "foundation"
    pub = canvas_dir / "published"
    pub.mkdir(parents=True)
    (pub / "README.md").write_text("docs", encoding="utf-8")
    (pub / "not-a-version.md").write_text("docs", encoding="utf-8")

    _migrate_published_flat_to_kind_slug(canvas_dir)

    assert (pub / "README.md").is_file()
    assert (pub / "not-a-version.md").is_file()


# ---------------------------------------------------------------------------
# GET endpoint — list a node's published versions
# ---------------------------------------------------------------------------


def test_published_endpoint_empty_when_never_published(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    resp = client.get(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/published",
        params={"project_path": str(plot_root.parent)},
    )
    assert resp.status_code == 200
    assert resp.json() == {"versions": []}


def test_published_endpoint_returns_versions_newest_first(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)
    publish_node(plot_root, "alpha", "foundation", mid)
    publish_node(plot_root, "alpha", "foundation", mid)

    resp = client.get(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/published",
        params={"project_path": str(plot_root.parent)},
    )
    assert resp.status_code == 200
    versions = resp.json()["versions"]
    assert [v["version"] for v in versions] == ["v4.0", "v3.0", "v2.0"]


def test_published_endpoint_entries_carry_path_published_at_size(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    mid = _foundation_mission_id(plot_root, "alpha")
    publish_node(plot_root, "alpha", "foundation", mid)

    resp = client.get(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/published",
        params={"project_path": str(plot_root.parent)},
    )
    entry = resp.json()["versions"][0]
    assert entry["version"] == "v2.0"
    assert entry["path"].endswith("/v2.0.md")
    assert entry["published_at"] is not None  # frontmatter parsed
    assert entry["size"] > 0
    # sha can be None on systems without git; assert presence if string.
    assert entry["sha"] is None or isinstance(entry["sha"], str)


def test_published_endpoint_404_for_unknown_node(
    plot_root: Path, client: TestClient
) -> None:
    create_project(plot_root, "alpha", "Alpha")
    resp = client.get(
        "/api/projects/alpha/canvases/foundation/nodes/ghost/published",
        params={"project_path": str(plot_root.parent)},
    )
    assert resp.status_code == 404
