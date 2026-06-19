"""Codegen drift guard — committed ``wire.gen.ts`` must equal fresh output.

Migration Phase A (D-2026-06-20-A). ``plot_mcp/ts_codegen.py`` generates the
viewer's ``XxxJson`` wire interfaces from the Pydantic models. The generated
file is committed (so the viewer builds without a Python step) and consumed by
every per-kind domain class. This test pins the committed file byte-for-byte
against fresh generation: a model change without ``uv run python -m
plot_mcp.ts_codegen`` fails here loudly. It replaces the cross-side regex
parity (``test_schema_parity.py::test_per_kind_field_parity``) that died the
moment the viewer left the repo — the generated artifact survives the split,
the regex did not.
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.ts_codegen import generate_wire_ts

_GEN_PATH = (
    Path(__file__).resolve().parent.parent / "viewer" / "src" / "domain" / "wire.gen.ts"
)


def test_generated_file_is_committed_and_current() -> None:
    """The committed ``wire.gen.ts`` must equal what the models generate NOW.
    Drift = a Pydantic model changed without regenerating the TS wire types."""
    assert _GEN_PATH.is_file(), (
        f"missing {_GEN_PATH} — run: uv run python -m plot_mcp.ts_codegen"
    )
    committed = _GEN_PATH.read_text(encoding="utf-8")
    assert committed == generate_wire_ts(), (
        "wire.gen.ts is stale — a model changed without regenerating. "
        "Run: uv run python -m plot_mcp.ts_codegen"
    )
