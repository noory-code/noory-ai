"""D-2026-06-09-D — dev-only debug channel for WKWebView introspection.

The viewer POSTs a screen snapshot (theme, per-node computed colours, layout
rects, watermark presence) to ``/api/debug``; an external agent GETs it to
verify what it cannot see directly (CDP tools can't attach to the Tauri
WKWebView on macOS). In-memory, not part of the product surface.
"""

from __future__ import annotations

from starlette.testclient import TestClient

from plot_mcp.broadcast import BroadcastHub
from plot_mcp.debug_endpoints import reset_debug_store
from plot_mcp.http_app import create_http_app


def _client() -> TestClient:
    return TestClient(create_http_app(hub=BroadcastHub(enable_watchers=False)))


def test_debug_store_empty_initially() -> None:
    reset_debug_store()
    r = _client().get("/api/debug")
    assert r.status_code == 200
    assert r.json() == {}


def test_debug_post_then_get_roundtrip() -> None:
    reset_debug_store()
    client = _client()
    snap = {
        "theme": "dark",
        "watermark": False,
        "nodes": [{"id": "a", "fg": "rgb(15, 23, 42)", "rect": {"w": 150, "h": 150}}],
    }
    pr = client.post("/api/debug", json=snap)
    assert pr.status_code == 200
    r = client.get("/api/debug")
    assert r.json()["latest"] == snap


def test_debug_post_overwrites_latest() -> None:
    reset_debug_store()
    client = _client()
    client.post("/api/debug", json={"v": 1})
    client.post("/api/debug", json={"v": 2})
    assert _client().get("/api/debug").json()["latest"] == {"v": 2}


def test_debug_post_rejects_invalid_json() -> None:
    reset_debug_store()
    r = _client().post(
        "/api/debug", content=b"not json", headers={"content-type": "application/json"}
    )
    assert r.status_code == 400
