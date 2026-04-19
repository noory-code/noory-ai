"""Endpoint tests via Starlette TestClient."""

from __future__ import annotations

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


def test_health(app_client: tuple[TestClient, str]) -> None:
    client, _ = app_client
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "plot"}


def test_list_empty(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    resp = client.get("/api/sketches", params={"project_path": project_path})
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_requires_project_path(app_client: tuple[TestClient, str]) -> None:
    client, _ = app_client
    resp = client.get("/api/sketches")
    assert resp.status_code == 400
    assert "project_path" in resp.json()["error"]


def test_create_then_list(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    resp = client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Alpha"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == "alpha"
    assert body["name"] == "Alpha"
    # List now returns one entry
    resp = client.get("/api/sketches", params={"project_path": project_path})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_create_duplicate_is_409(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Alpha"},
    )
    resp = client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Again"},
    )
    assert resp.status_code == 409


def test_create_missing_id_is_400(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    resp = client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"name": "No ID"},
    )
    assert resp.status_code == 400


def test_get_then_put(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Alpha"},
    )
    # GET
    resp = client.get("/api/sketches/alpha", params={"project_path": project_path})
    assert resp.status_code == 200
    doc = resp.json()
    # Add a node
    doc["nodes"].append(
        {"id": "n1", "label": "First", "x": 100, "y": 100, "color": "#fecaca"}
    )
    # PUT overwrites
    resp = client.put(
        "/api/sketches/alpha",
        params={"project_path": project_path},
        json=doc,
    )
    assert resp.status_code == 200
    resp = client.get("/api/sketches/alpha", params={"project_path": project_path})
    assert len(resp.json()["nodes"]) == 1


def test_put_with_bad_edge_is_422(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Alpha"},
    )
    resp = client.put(
        "/api/sketches/alpha",
        params={"project_path": project_path},
        json={
            "id": "alpha",
            "name": "Alpha",
            "nodes": [],
            "edges": [{"id": "e1", "source": "ghost", "target": "also-ghost"}],
        },
    )
    assert resp.status_code == 422


def test_delete(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    client.post(
        "/api/sketches",
        params={"project_path": project_path},
        json={"id": "alpha", "name": "Alpha"},
    )
    resp = client.delete("/api/sketches/alpha", params={"project_path": project_path})
    assert resp.status_code == 200
    resp = client.get("/api/sketches/alpha", params={"project_path": project_path})
    assert resp.status_code == 404


def test_get_missing_is_404(app_client: tuple[TestClient, str]) -> None:
    client, project_path = app_client
    resp = client.get("/api/sketches/ghost", params={"project_path": project_path})
    assert resp.status_code == 404


def test_get_nonexistent_project_path_is_404(app_client: tuple[TestClient, str]) -> None:
    client, _ = app_client
    resp = client.get(
        "/api/sketches",
        params={"project_path": "/tmp/definitely-does-not-exist-plot-xyz-12345"},
    )
    assert resp.status_code == 404
