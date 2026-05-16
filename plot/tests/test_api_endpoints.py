"""HTTP endpoint tests for the v0.4 project / canvas / tag surface.

Legacy ``/api/sketches/*`` endpoints were removed in v0.4 — this file
now covers only the new project-based shape.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from plot_mcp.broadcast import BroadcastHub
from plot_mcp.http_app import create_http_app


@pytest.fixture
def app_client(tmp_path: Path) -> tuple[TestClient, str]:
    hub = BroadcastHub(enable_watchers=False)
    app = create_http_app(hub=hub)
    return TestClient(app), str(tmp_path)


# ---------------------------------------------------------------------------
# health + baseline
# ---------------------------------------------------------------------------


def test_health(app_client: tuple[TestClient, str]) -> None:
    client, _ = app_client
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "plot"}


def test_list_empty(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    resp = client.get("/api/projects", params={"project_path": project_path})
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"projects": [], "migrated": []}


def test_list_requires_project_path(app_client: tuple[TestClient, str]) -> None:
    client, _ = app_client
    resp = client.get("/api/projects")
    assert resp.status_code == 400


def test_nonexistent_project_path_is_404(app_client: tuple[TestClient, str]) -> None:
    client, _ = app_client
    resp = client.get(
        "/api/projects",
        params={"project_path": "/tmp/definitely-does-not-exist-plot-xyz-12345"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# project CRUD
# ---------------------------------------------------------------------------


def _create(client: TestClient, project_path: str, pid: str, name: str) -> dict:
    resp = client.post(
        "/api/projects",
        params={"project_path": project_path},
        json={"id": pid, "name": name},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_then_list(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    proj = _create(client, project_path, "alpha", "Alpha")
    assert proj["id"] == "alpha"
    assert proj["version"] == 3  # v0.13 Phase 0

    listed = client.get("/api/projects", params={"project_path": project_path}).json()
    assert [p["id"] for p in listed["projects"]] == ["alpha"]


def test_duplicate_create_is_409(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.post(
        "/api/projects",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Again"},
    )
    assert resp.status_code == 409


def test_create_missing_id_is_400(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    resp = client.post(
        "/api/projects",
        params={"project_path": project_path},
        json={"name": "No ID"},
    )
    assert resp.status_code == 400


def test_project_get_returns_details_and_tags(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/projects/alpha",
        params={"project_path": project_path},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "alpha"
    assert body["service_details"] == []
    assert body["tags"] == []


def test_project_rename(app_client: tuple[TestClient, str]) -> None:
    """v0.13 Phase 0: rename updates ProjectDoc.name only (no canvas node sync)."""
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.patch(
        "/api/projects/alpha",
        params={"project_path": project_path},
        json={"name": "Renamed"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"
    # foundation canvas no longer carries a project node — anchor label is
    # derived from ProjectDoc.name at render time.
    canvas_resp = client.get(
        "/api/projects/alpha/canvases/foundation",
        params={"project_path": project_path},
    )
    assert canvas_resp.status_code == 200
    assert all(n["kind"] != "project" for n in canvas_resp.json()["nodes"])


def test_project_rename_requires_name(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.patch(
        "/api/projects/alpha",
        params={"project_path": project_path},
        json={},
    )
    assert resp.status_code == 400


def test_project_delete(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.delete("/api/projects/alpha", params={"project_path": project_path})
    assert resp.status_code == 200
    resp = client.get("/api/projects/alpha", params={"project_path": project_path})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# canvas GET/PUT
# ---------------------------------------------------------------------------


def test_canvas_get_returns_seeded_core(
    app_client: tuple[TestClient, str],
) -> None:
    """v0.13 Phase 0: foundation seeds Mission + Core value + Identity (no project)."""
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/projects/alpha/canvases/foundation",
        params={"project_path": project_path},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["canvas_kind"] == "foundation"
    kinds = sorted({n["kind"] for n in body["nodes"] if n.get("kind")})
    assert kinds == ["core_value", "identity", "mission"]


def test_canvas_put_round_trips_actor(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/projects/alpha/canvases/actors",
        params={"project_path": project_path},
    )
    canvas = resp.json()
    canvas["nodes"].append(
        {
            "id": "guest",
            "kind": "actor",
            "label": "Guest",
            "body": "",
            "x": 0,
            "y": 0,
            "width": 120,
            "height": 120,
            "color": "#fecaca",
            "shape": "circle",
            "icon": "user",
            "parent_id": None,
            "collapsed": False,
            "is_root": False,
            "mission": "",
            "core_values": "",
            "identity": "",
            "ref_actor_id": None,
        }
    )
    resp = client.put(
        "/api/projects/alpha/canvases/actors",
        params={"project_path": project_path},
        json=canvas,
    )
    assert resp.status_code == 200
    reloaded = client.get(
        "/api/projects/alpha/canvases/actors",
        params={"project_path": project_path},
    ).json()
    assert any(n["id"] == "guest" for n in reloaded["nodes"])


def test_canvas_put_overview_auto_creates_detail(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    payload = {
        "canvas_id": "services",
        "canvas_kind": "services",
        "nodes": [
            {
                "id": "default-cat",
                "kind": "category",
                "label": "Default",
                "body": "",
                "x": 0,
                "y": -100,
                "width": 200,
                "height": 100,
                "color": "#e2e8f0",
                "shape": "rounded",
                "icon": None,
                "parent_id": None,
                "collapsed": False,
                "is_root": False,
                "mission": "",
                "core_values": "",
                "identity": "",
                "ref_actor_id": None,
            },
            {
                "id": "order",
                "kind": "service",
                "label": "주문",
                "body": "",
                "x": 0,
                "y": 0,
                "width": 160,
                "height": 80,
                "color": "#bae6fd",
                "shape": "rounded",
                "icon": "zap",
                "parent_id": "default-cat",
                "collapsed": False,
                "is_root": False,
                "mission": "",
                "core_values": "",
                "identity": "",
                "ref_actor_id": None,
            },
        ],
        "edges": [],
    }
    resp = client.put(
        "/api/projects/alpha/canvases/services",
        params={"project_path": project_path},
        json=payload,
    )
    assert resp.status_code == 200
    assert resp.json()["sync"]["created"] == ["order"]
    detail = client.get(
        "/api/projects/alpha/canvases/service_detail",
        params={"project_path": project_path, "service_id": "order"},
    )
    assert detail.status_code == 200
    assert detail.json()["service_ref"] == "order"


def test_canvas_get_unknown_kind_is_400(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/projects/alpha/canvases/bogus",
        params={"project_path": project_path},
    )
    assert resp.status_code == 400


def test_canvas_put_bad_body_is_422(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    # Edge referencing a non-existent node → model validator rejects.
    resp = client.put(
        "/api/projects/alpha/canvases/actors",
        params={"project_path": project_path},
        json={
            "canvas_id": "actors",
            "nodes": [],
            "edges": [{"id": "e1", "source": "ghost", "target": "nowhere"}],
        },
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# tags (session bookmarks)
# ---------------------------------------------------------------------------


def test_tags_empty_on_new_project(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
    )
    assert resp.status_code == 200
    assert resp.json() == {"tags": []}


def test_tag_create_then_list(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.post(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
        json={"name": "session-start", "message": "kickoff"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "session-start"

    listed = client.get(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
    ).json()
    assert [t["name"] for t in listed["tags"]] == ["session-start"]


def test_tag_duplicate_is_409(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    client.post(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
        json={"name": "dup"},
    )
    resp = client.post(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
        json={"name": "dup"},
    )
    assert resp.status_code == 409


def test_tag_delete(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    client.post(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
        json={"name": "doomed"},
    )
    resp = client.delete(
        "/api/projects/alpha/tags/doomed",
        params={"project_path": project_path},
    )
    assert resp.status_code == 200
    listed = client.get(
        "/api/projects/alpha/tags",
        params={"project_path": project_path},
    ).json()
    assert listed == {"tags": []}


def test_tag_delete_unknown_is_404(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.delete(
        "/api/projects/alpha/tags/ghost",
        params={"project_path": project_path},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# v0.1 auto-migration on list
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# v0.7 file + folder surface (Inspector MD editor)
# ---------------------------------------------------------------------------


def test_file_put_and_get_roundtrip(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    put = client.put(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "notes.md",
        },
        json={"content": "# Hello\n일상 속..."},
    )
    assert put.status_code == 200
    got = client.get(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "notes.md",
        },
    )
    assert got.status_code == 200
    assert got.json()["content"] == "# Hello\n일상 속..."


def test_file_get_missing_returns_empty_content(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "nothing.md",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == ""


def test_file_requires_project_id(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/files",
        params={"project_path": project_path, "path": "notes.md"},
    )
    assert resp.status_code == 400


def test_file_rejects_path_traversal(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "../../../etc/passwd",
        },
    )
    assert resp.status_code == 400


def test_file_rejects_absolute_path(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.get(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "/etc/passwd",
        },
    )
    assert resp.status_code == 400


def test_file_cannot_climb_into_other_project(
    app_client: tuple[TestClient, str],
) -> None:
    """v0.8 scoping: a file API call for project ``alpha`` can't walk up
    to ``beta`` via ``../beta/...``."""
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    _create(client, project_path, "beta", "Beta")
    resp = client.get(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "../beta/project.json",
        },
    )
    assert resp.status_code == 400


def test_file_rejects_disallowed_extension(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.put(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "foo.py",
        },
        json={"content": "import os"},
    )
    assert resp.status_code == 400


def test_file_put_does_not_touch_canvas(
    app_client: tuple[TestClient, str],
) -> None:
    """v0.9: writing a node's ``details.md`` is a leaf operation — the
    node's typed fields in canvas.json are untouched. (No more body cache
    sync; typed fields are the canvas-side source.)"""
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    core_before = client.get(
        "/api/projects/alpha/canvases/foundation",
        params={"project_path": project_path},
    ).json()
    mission = next(n for n in core_before["nodes"] if n["kind"] == "mission")
    mission["details_path"] = "core/mission-mission/details.md"
    client.put(
        "/api/projects/alpha/canvases/foundation",
        params={"project_path": project_path},
        json=core_before,
    ).raise_for_status()

    put = client.put(
        "/api/files",
        params={
            "project_path": project_path,
            "project_id": "alpha",
            "path": "core/mission-mission/details.md",
            "node_id": mission["id"],
        },
        json={"content": "긴 이야기..."},
    )
    assert put.status_code == 200
    body = put.json()
    assert "preview" not in body  # no canvas-side caching anymore

    core_after = client.get(
        "/api/projects/alpha/canvases/foundation",
        params={"project_path": project_path},
    ).json()
    refreshed_mission = next(n for n in core_after["nodes"] if n["id"] == mission["id"])
    # v0.17 Phase 1 (D-2026-05-16-A): Foundation typed-text kinds carry no
    # details_path in JSON. The absorption migrator clears the user-set
    # custom path on Mission/CoreValue/Identity unconditionally — JSON
    # SSOT now covers all MD-syntax fields (typed + body); per-node MD
    # editing surface is gone. The test's premise — "writing a file via
    # /api/files does not touch the canvas as a side-effect" — still
    # holds: the canvas mutation that cleared details_path was the PUT
    # at line above, not the file write.
    assert refreshed_mission["details_path"] is None


def test_folder_post_creates_unique_path(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    first = client.post(
        "/api/folders",
        params={"project_path": project_path},
        json={"project_id": "alpha", "path": "core/mission-mission"},
    )
    assert first.status_code == 201
    assert first.json()["path"] == "core/mission-mission"
    # Second request with the same name → server appends ``-2``.
    second = client.post(
        "/api/folders",
        params={"project_path": project_path},
        json={"project_id": "alpha", "path": "core/mission-mission"},
    )
    assert second.status_code == 201
    assert second.json()["path"] == "core/mission-mission-2"
    # index.md is seeded inside the created folder (under the project scope).
    assert (Path(project_path) / ".plot/alpha/core/mission-mission/index.md").is_file()


def test_list_migrates_v01_sketches_silently(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    sketches_dir = Path(project_path) / ".plot" / "sketches"
    sketches_dir.mkdir(parents=True, exist_ok=True)
    (sketches_dir / "legacy.json").write_text(
        json.dumps(
            {
                "id": "legacy",
                "name": "Legacy",
                "created": "2026-01-01",
                "updated": "2026-01-01T00:00:00+00:00",
                "version": 1,
                "nodes": [
                    {
                        "id": "core-root",
                        "label": "Legacy",
                        "kind": "core",
                    }
                ],
                "edges": [],
            }
        ),
        encoding="utf-8",
    )
    resp = client.get("/api/projects", params={"project_path": project_path})
    assert resp.status_code == 200
    body = resp.json()
    assert "legacy" in body["migrated"]
    assert any(p["id"] == "legacy" for p in body["projects"])


# ---------------------------------------------------------------------------
# v0.18.0 Phase 3 (D-2026-05-16-E) — publish endpoint
# ---------------------------------------------------------------------------


def _mission_id(client: TestClient, project_path: str, pid: str) -> str:
    canvas = client.get(
        f"/api/projects/{pid}/canvases/foundation",
        params={"project_path": project_path},
    ).json()
    return next(n["id"] for n in canvas["nodes"] if n["kind"] == "mission")


def test_publish_endpoint_round_trip(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    mid = _mission_id(client, project_path, "alpha")
    resp = client.post(
        f"/api/projects/alpha/canvases/foundation/nodes/{mid}/publish",
        params={"project_path": project_path},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["from_version"] == "v1.0"
    assert body["to_version"] == "v2.0"
    assert body["md_path"].startswith("foundation/published/")
    assert len(body["sha"]) == 40


def test_publish_endpoint_unknown_node_is_404(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    resp = client.post(
        "/api/projects/alpha/canvases/foundation/nodes/ghost/publish",
        params={"project_path": project_path},
    )
    assert resp.status_code == 404


def test_publish_endpoint_ineligible_root_is_409(
    app_client: tuple[TestClient, str],
) -> None:
    client, project_path = app_client
    _create(client, project_path, "alpha", "Alpha")
    # Seed an is_root actor via PUT canvas (default seed actors are non-root).
    actors = client.get(
        "/api/projects/alpha/canvases/actors",
        params={"project_path": project_path},
    ).json()
    actors["nodes"].append(
        {
            "id": "root-actor",
            "kind": "actor",
            "label": "Root",
            "is_root": True,
        }
    )
    put = client.put(
        "/api/projects/alpha/canvases/actors",
        params={"project_path": project_path},
        json=actors,
    )
    assert put.status_code in (200, 201)
    resp = client.post(
        "/api/projects/alpha/canvases/actors/nodes/root-actor/publish",
        params={"project_path": project_path},
    )
    assert resp.status_code == 409
