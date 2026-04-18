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
