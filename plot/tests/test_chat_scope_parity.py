"""Server ↔ Viewer parity for the ChatScope wire enum (D-2026-06-13-H).

The chat redesign scopes conversations per canvas kind plus one shared
``project`` scope. The scope literal is a cross-cutting wire value: the
viewer sends it on ``POST /api/chat/send`` and demultiplexes incoming
``chat_stream_event`` payloads on it, while the engine keys chat sessions
on it. Both sides must agree on the exact member set — otherwise a scope
the viewer sends would silently land in a session the engine never reads,
or an event the engine emits would route to a bucket the viewer doesn't
render.

Mirrors ``test_schema_parity.py``'s regex-not-compiler approach for the
TS side: the literal union form is stable, and if a future commit changes
the idiom this parser is the brittle piece and fails here loudly.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import get_args

from plot_mcp.chat_providers.base import ChatScope, is_valid_scope

_PLOT_ROOT = Path(__file__).resolve().parent.parent
_TYPES_TS = _PLOT_ROOT / "viewer" / "src" / "types.ts"

# Match ``export type ChatScope = "a" | "b" | ...;`` — body up to the
# first semicolon, members extracted from the quoted literals.
_SCOPE_RE = re.compile(r"export\s+type\s+ChatScope\s*=([^;]*);", re.DOTALL)
_MEMBER_RE = re.compile(r'"([a-z_]+)"')
# The one parametric member is a template literal — ``feature`` carries
# an instance id suffix (Layer 1, CHAT_ARCH.md). Match the base prefix so the
# parity check compares the same *base* set on both sides.
_TEMPLATE_MEMBER_RE = re.compile(r"`([a-z_]+):\$\{string\}`")

_EXPECTED_SCOPES = {
    "project",
    "foundation",
    "actors",
    "services",
    "entities",
    "feature",
}


def _ts_scope_members() -> set[str]:
    src = _TYPES_TS.read_text(encoding="utf-8")
    match = _SCOPE_RE.search(src)
    assert match is not None, f"ChatScope type not found in {_TYPES_TS}"
    body = match.group(1)
    members = set(_MEMBER_RE.findall(body))
    members |= set(_TEMPLATE_MEMBER_RE.findall(body))
    return members


def test_chat_scope_parity() -> None:
    """Python ``ChatScope`` literal members == TS ``ChatScope`` members."""
    py_members = set(get_args(ChatScope))
    ts_members = _ts_scope_members()
    assert py_members == ts_members, (
        f"ChatScope drift: "
        f"missing_in_ts={py_members - ts_members}, "
        f"missing_in_py={ts_members - py_members}"
    )


def test_chat_scope_is_project_plus_canvas_kinds() -> None:
    """The scope set is exactly ``project`` + the five canvas kinds
    (foundation / actors / services / entities / feature) — pins the member
    set so neither side can quietly add another."""
    assert set(get_args(ChatScope)) == _EXPECTED_SCOPES


def test_feature_scope_accepts_id_suffix() -> None:
    """Layer 1 (CHAT_ARCH.md): ``feature`` is the one parametric
    member — a wire scope carries the service instance id as
    ``feature:<id>`` so each service gets its own thread."""
    assert is_valid_scope("feature:svc_123")
    assert is_valid_scope("feature:any-id-shape")
    # Singleton base scopes stay valid bare.
    for base in ("project", "foundation", "actors", "services", "entities"):
        assert is_valid_scope(base)
    # An empty id is not a real instance, and a typo is still rejected.
    assert not is_valid_scope("feature:")
    assert not is_valid_scope("bogus")
