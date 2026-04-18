"""Tests for the HTTP API and workspace resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from solera_map.server import create_http_app, resolve_workspace


def _seed_workspace(workspace: Path) -> None:
    concepts = workspace / "concepts"
    concepts.mkdir(parents=True, exist_ok=True)
    (concepts / "auth.md").write_text(
        "---\nid: auth\nname: Auth\nstatus: active\n---\n\n"
        "# Intent\nUser proves identity.\n\n"
        "# Current Design\nPasswordless.\n\n"
        "# Current Shape\n(no Stories yet)\n",
        encoding="utf-8",
    )
    (workspace / "concept-graph.json").write_text(
        json.dumps({"edges": [{"from": "auth", "to": "auth", "label": "self"}]}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# resolve_workspace
# ---------------------------------------------------------------------------


def test_resolve_workspace_accepts_project_root(tmp_path: Path) -> None:
    _seed_workspace(tmp_path / "workspace")
    resolved = resolve_workspace(str(tmp_path))
    assert resolved == (tmp_path / "workspace").resolve()


def test_resolve_workspace_accepts_workspace_dir(tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    _seed_workspace(ws)
    resolved = resolve_workspace(str(ws))
    assert resolved == ws.resolve()


def test_resolve_workspace_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_workspace(str(tmp_path))


# ---------------------------------------------------------------------------
# HTTP endpoints
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_http_app())


def test_health_endpoint(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "solera-map"}


def test_graph_endpoint_requires_project_path(client: TestClient) -> None:
    r = client.get("/api/graph")
    assert r.status_code == 400
    assert "project_path" in r.json()["error"]


def test_graph_endpoint_returns_graph(client: TestClient, tmp_path: Path) -> None:
    _seed_workspace(tmp_path / "workspace")
    r = client.get("/api/graph", params={"project_path": str(tmp_path)})
    assert r.status_code == 200
    body = r.json()
    assert [c["id"] for c in body["concepts"]] == ["auth"]
    assert body["concept_edges"][0]["label"] == "self"
    assert body["milestones"] == []
    assert body["stories"] == []


def test_graph_endpoint_missing_workspace_returns_404(
    client: TestClient, tmp_path: Path
) -> None:
    r = client.get("/api/graph", params={"project_path": str(tmp_path)})
    assert r.status_code == 404
    assert "workspace" in r.json()["error"].lower()


# ---------------------------------------------------------------------------
# Layout endpoints
# ---------------------------------------------------------------------------


def test_layout_get_defaults_to_empty(client: TestClient, tmp_path: Path) -> None:
    _seed_workspace(tmp_path / "workspace")
    r = client.get("/api/layout", params={"project_path": str(tmp_path)})
    assert r.status_code == 200
    assert r.json() == {"nodes": {}}


def test_layout_put_and_get_roundtrip(client: TestClient, tmp_path: Path) -> None:
    _seed_workspace(tmp_path / "workspace")
    body = {
        "nodes": {
            "concept:auth": {"x": 120.5, "y": -40},
            "identity": {"x": 0, "y": 0, "collapsed": True},
        }
    }

    put_r = client.put(
        "/api/layout",
        params={"project_path": str(tmp_path)},
        json=body,
    )
    assert put_r.status_code == 200

    get_r = client.get("/api/layout", params={"project_path": str(tmp_path)})
    assert get_r.status_code == 200
    assert get_r.json() == body


def test_layout_put_requires_object_body(client: TestClient, tmp_path: Path) -> None:
    _seed_workspace(tmp_path / "workspace")
    r = client.put(
        "/api/layout",
        params={"project_path": str(tmp_path)},
        json=[1, 2, 3],
    )
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /api/concept/:id
# ---------------------------------------------------------------------------


def _write_concept(workspace: Path, concept_id: str, parent: str | None = None) -> None:
    concepts = workspace / "concepts"
    concepts.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"id: {concept_id}", f"name: {concept_id.title()}", "status: active"]
    if parent is not None:
        lines.append(f"parent: {parent}")
    lines.append("---")
    lines.append("")
    lines.append(f"# Intent\nseed intent for {concept_id}.\n")
    (concepts / f"{concept_id}.md").write_text("\n".join(lines), encoding="utf-8")


def test_concept_patch_sets_parent(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    _write_concept(ws, "app")
    _write_concept(ws, "profile")

    r = client.patch(
        "/api/concept/profile",
        params={"project_path": str(tmp_path)},
        json={"parent": "app"},
    )
    assert r.status_code == 200

    graph = client.get("/api/graph", params={"project_path": str(tmp_path)}).json()
    profile = next(c for c in graph["concepts"] if c["id"] == "profile")
    assert profile["parent"] == "app"


def test_concept_patch_clears_parent(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    _write_concept(ws, "app")
    _write_concept(ws, "profile", parent="app")

    r = client.patch(
        "/api/concept/profile",
        params={"project_path": str(tmp_path)},
        json={"parent": None},
    )
    assert r.status_code == 200

    graph = client.get("/api/graph", params={"project_path": str(tmp_path)}).json()
    profile = next(c for c in graph["concepts"] if c["id"] == "profile")
    assert profile["parent"] is None


def test_concept_patch_rejects_unknown_parent(
    client: TestClient, tmp_path: Path
) -> None:
    _write_concept(tmp_path / "workspace", "profile")
    r = client.patch(
        "/api/concept/profile",
        params={"project_path": str(tmp_path)},
        json={"parent": "ghost"},
    )
    assert r.status_code == 400


def test_concept_patch_rejects_self_parent(client: TestClient, tmp_path: Path) -> None:
    _write_concept(tmp_path / "workspace", "profile")
    r = client.patch(
        "/api/concept/profile",
        params={"project_path": str(tmp_path)},
        json={"parent": "profile"},
    )
    assert r.status_code == 400


def test_concept_patch_rejects_cycle(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    _write_concept(ws, "a")
    _write_concept(ws, "b", parent="a")
    _write_concept(ws, "c", parent="b")
    # Making `a` a child of `c` would loop c → b → a → c.
    r = client.patch(
        "/api/concept/a",
        params={"project_path": str(tmp_path)},
        json={"parent": "c"},
    )
    assert r.status_code == 400


def test_concept_patch_rejects_disallowed_fields(
    client: TestClient, tmp_path: Path
) -> None:
    _write_concept(tmp_path / "workspace", "profile")
    r = client.patch(
        "/api/concept/profile",
        params={"project_path": str(tmp_path)},
        json={"name": "hacked"},
    )
    assert r.status_code == 400


def test_concept_patch_returns_404_for_missing_concept(
    client: TestClient, tmp_path: Path
) -> None:
    (tmp_path / "workspace" / "concepts").mkdir(parents=True)
    r = client.patch(
        "/api/concept/missing",
        params={"project_path": str(tmp_path)},
        json={"parent": None},
    )
    assert r.status_code == 404
