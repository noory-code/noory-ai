"""R7 chat — endpoint + streaming-bridge tests (D-2026-06-12-D, Phase C step C2).

The endpoint stays thin: validate, look up provider, schedule the streaming
task. The bridge (``stream_chat_turn``) is where most of the logic lives and
is tested directly.

End-to-end POST → WS is exercised at the registry/bridge level (sync drain
into a fake hub). The HTTP layer is a thin shell around it — those tests
only cover request validation + 202 acceptance + the registry/hub wiring.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from starlette.testclient import TestClient

from plot_mcp.broadcast import BroadcastHub
from plot_mcp.chat_session import (
    ChatProvider,
    ChatSessionRegistry,
    ChatStreamEvent,
)
from plot_mcp.endpoints_chat import stream_chat_turn
from plot_mcp.http_app import create_http_app

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeHub:
    """Captures every ``notify_event`` call so tests can assert event order."""

    def __init__(self) -> None:
        self.events: list[tuple[Path, str, dict[str, Any] | None]] = []

    async def notify_event(
        self,
        plot_root: Path,
        event_name: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.events.append((plot_root, event_name, payload))


class _CannedProvider(ChatProvider):
    """Yields a pre-baked event list, recording every call."""

    def __init__(self, events: list[ChatStreamEvent]) -> None:
        self._events = events
        self.calls: list[str] = []

    async def stream_turn(self, user_message: str) -> Any:
        self.calls.append(user_message)
        for event in self._events:
            yield event


class _ExplodingProvider(ChatProvider):
    async def stream_turn(self, user_message: str) -> Any:
        raise RuntimeError("provider blew up mid-turn")
        yield  # pragma: no cover — required to make this an async generator


# ---------------------------------------------------------------------------
# stream_chat_turn — the unit-tested core
# ---------------------------------------------------------------------------


async def test_stream_chat_turn_broadcasts_each_event(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    hub = _FakeHub()
    provider = _CannedProvider(
        [
            ChatStreamEvent(type="turn_start", turn_id="t1"),
            ChatStreamEvent(type="delta", turn_id="t1", text="hi "),
            ChatStreamEvent(type="delta", turn_id="t1", text="there"),
            ChatStreamEvent(type="turn_complete", turn_id="t1", text="hi there"),
        ]
    )

    await stream_chat_turn(provider, hub, ws, "hello")  # type: ignore[arg-type]

    assert provider.calls == ["hello"]
    assert [name for (_, name, _) in hub.events] == [
        "chat_stream_event",
        "chat_stream_event",
        "chat_stream_event",
        "chat_stream_event",
    ]
    types = [payload["type"] for (_, _, payload) in hub.events]  # type: ignore[index]
    assert types == ["turn_start", "delta", "delta", "turn_complete"]
    last_payload = hub.events[-1][2]
    assert last_payload is not None
    assert last_payload["text"] == "hi there"


async def test_stream_chat_turn_broadcasts_error_on_provider_crash(
    tmp_path: Path,
) -> None:
    ws = tmp_path / "ws"
    ws.mkdir()
    hub = _FakeHub()
    provider = _ExplodingProvider()

    await stream_chat_turn(provider, hub, ws, "hi")  # type: ignore[arg-type]

    assert len(hub.events) == 1
    payload = hub.events[0][2]
    assert payload is not None
    assert payload["type"] == "error"
    assert payload["error_message"] is not None
    assert "blew up" in payload["error_message"]


# ---------------------------------------------------------------------------
# HTTP layer — request validation + wiring
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    return ws


@pytest.fixture
def fake_provider() -> _CannedProvider:
    return _CannedProvider(
        [
            ChatStreamEvent(type="turn_start", turn_id="t1"),
            ChatStreamEvent(type="delta", turn_id="t1", text="ok"),
            ChatStreamEvent(type="turn_complete", turn_id="t1", text="ok"),
        ]
    )


@pytest.fixture
def app_client(fake_provider: _CannedProvider) -> TestClient:
    # ``(_root, _name) -> provider`` — same fake regardless of which CLI the
    # workspace selected; that's enough for the endpoint-wiring tests.
    registry = ChatSessionRegistry(factory=lambda _root, _name: fake_provider)
    return TestClient(
        create_http_app(
            hub=BroadcastHub(enable_watchers=False),
            chat_registry_instance=registry,
        )
    )


def _select_provider(client: TestClient, workspace: Path, name: str) -> None:
    """Persist the workspace's chat-CLI choice via the public API so /send
    can dispatch to the right provider. v0.64.1: /send now reads
    `<workspace>/.noory/plot/chat-provider` and 400s when missing."""
    resp = client.put(
        f"/api/chat/provider?project_path={workspace}",
        json={"provider": name},
    )
    assert resp.status_code == 200, resp.text


def test_chat_send_requires_project_path(app_client: TestClient) -> None:
    resp = app_client.post("/api/chat/send", json={"message": "hi"})
    assert resp.status_code == 400
    assert "project_path" in resp.json()["error"]


def test_chat_send_requires_message(
    app_client: TestClient, workspace: Path
) -> None:
    resp = app_client.post(
        "/api/chat/send",
        json={"project_path": str(workspace), "message": ""},
    )
    assert resp.status_code == 400
    assert "message" in resp.json()["error"]


def test_chat_send_rejects_invalid_json(app_client: TestClient) -> None:
    resp = app_client.post(
        "/api/chat/send",
        content=b"{not valid",
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 400


def test_chat_send_400s_when_no_provider_selected(
    app_client: TestClient, workspace: Path, fake_provider: _CannedProvider
) -> None:
    """v0.64.1 — without a persisted selection, /send must 400 instead of
    silently spawning a default CLI the user didn't agree to."""
    resp = app_client.post(
        "/api/chat/send",
        json={"project_path": str(workspace), "message": "explain plot"},
    )
    assert resp.status_code == 400
    assert "provider" in resp.json()["error"]
    assert fake_provider.calls == []


def test_chat_send_accepts_valid_request_and_calls_provider(
    app_client: TestClient, workspace: Path, fake_provider: _CannedProvider
) -> None:
    _select_provider(app_client, workspace, "claude-code")
    resp = app_client.post(
        "/api/chat/send",
        json={"project_path": str(workspace), "message": "explain plot"},
    )
    assert resp.status_code == 202
    assert resp.json() == {"accepted": True}
    # The async task fired during the synchronous TestClient call (Starlette's
    # TestClient drives the loop to completion before returning the response).
    assert fake_provider.calls == ["explain plot"]


def test_chat_send_dispatches_each_provider_to_its_own_session(
    workspace: Path,
) -> None:
    """Two workspaces with two different selected CLIs land at two distinct
    provider rows in the registry — the dispatch is by (workspace, name),
    not just workspace."""
    calls: list[tuple[Path, str]] = []

    class _RecordingProvider(ChatProvider):
        def __init__(self, name: str) -> None:
            self.name = name

        async def stream_turn(self, user_message: str) -> Any:
            calls.append((Path(user_message[:1]), self.name))
            if False:
                yield  # pragma: no cover — async generator marker

    registry = ChatSessionRegistry(
        factory=lambda _root, name: _RecordingProvider(name)
    )
    client = TestClient(
        create_http_app(
            hub=BroadcastHub(enable_watchers=False),
            chat_registry_instance=registry,
        )
    )
    _select_provider(client, workspace, "codex")
    client.post(
        "/api/chat/send",
        json={"project_path": str(workspace), "message": "a"},
    )
    _select_provider(client, workspace, "gemini")
    client.post(
        "/api/chat/send",
        json={"project_path": str(workspace), "message": "b"},
    )
    assert [name for (_, name) in calls] == ["codex", "gemini"]


def test_chat_reset_drops_all_provider_sessions_for_workspace(
    app_client: TestClient, workspace: Path, fake_provider: _CannedProvider
) -> None:
    _select_provider(app_client, workspace, "claude-code")
    # Prime the registry.
    app_client.post(
        "/api/chat/send",
        json={"project_path": str(workspace), "message": "first"},
    )
    assert fake_provider.calls == ["first"]

    resp = app_client.post(
        "/api/chat/reset", json={"project_path": str(workspace)}
    )
    assert resp.status_code == 200
    assert resp.json() == {"reset": True}


def test_chat_reset_requires_project_path(app_client: TestClient) -> None:
    resp = app_client.post("/api/chat/reset", json={})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# notify_event — generalisation of notify()
# ---------------------------------------------------------------------------


async def test_broadcast_notify_event_uses_supplied_event_name(
    tmp_path: Path,
) -> None:
    """A real ``BroadcastHub`` (no watchers) keeps event_name fidelity end-to-end."""
    from plot_mcp.broadcast import BroadcastHub

    ws_path = tmp_path / "ws"
    ws_path.mkdir()
    hub = BroadcastHub(enable_watchers=False)

    captured: list[dict[str, Any]] = []

    class _StubWebSocket:
        async def send_json(self, body: dict[str, Any]) -> None:
            captured.append(body)

    stub = _StubWebSocket()
    await hub.subscribe(stub, ws_path)  # type: ignore[arg-type]
    await hub.notify_event(ws_path, "chat_stream_event", {"type": "delta", "text": "x"})
    await hub.notify(ws_path)  # back-compat path stays "project_changed"

    assert captured == [
        {"event": "chat_stream_event", "type": "delta", "text": "x"},
        {"event": "project_changed"},
    ]
