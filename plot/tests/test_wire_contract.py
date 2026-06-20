"""Wire-contract snapshot — split-survivable schema parity (D-2026-06-10-E).

`test_schema_parity.py` reads BOTH sides (Pydantic + viewer TS) from disk, so
it silently dies the moment viewer/ leaves this repo (TECH_REVIEW step 1).
The replacement contract is a generated JSON snapshot committed TWICE:

    plot_mcp/wire_contract.json            (engine copy — this side)
    viewer/src/schema/wire-contract.json   (viewer copy — checked by vitest)

Each side verifies its own sources against its own committed copy, so both
guards survive the repo split. While the monorepo lasts, a sync test pins the
two copies byte-identical; at split time that single test moves to the
release pipeline (compare artifacts), and nothing else changes.

Regenerate after a deliberate schema change:

    uv run python -m plot_mcp.schema_export --wire
"""

from __future__ import annotations

import json
from pathlib import Path

from plot_mcp.schema_export import wire_contract

_PLOT_ROOT = Path(__file__).resolve().parent.parent
_ENGINE_COPY = _PLOT_ROOT / "plot_mcp" / "wire_contract.json"
_VIEWER_COPY = _PLOT_ROOT / "viewer" / "src" / "schema" / "wire-contract.json"


def test_engine_snapshot_matches_generated_contract() -> None:
    """The committed engine copy must equal what the models generate NOW.
    Drift = someone changed a Pydantic model without regenerating."""
    assert _ENGINE_COPY.is_file(), (
        f"missing {_ENGINE_COPY} — run: uv run python -m plot_mcp.schema_export --wire"
    )
    committed = json.loads(_ENGINE_COPY.read_text(encoding="utf-8"))
    assert committed == wire_contract(), (
        "wire_contract.json is stale — a model changed without regenerating. "
        "Run: uv run python -m plot_mcp.schema_export --wire"
    )


def test_contract_shape() -> None:
    c = wire_contract()
    assert c["schema_version"] >= 1
    assert "base_fields" in c and "id" in c["base_fields"]
    assert len(c["kinds"]) == 18
    for kind, fields in c["kinds"].items():
        assert "kind" in fields, f"{kind} must carry its discriminator"
        assert fields == sorted(fields), f"{kind} fields must be sorted (stable diffs)"


def test_monorepo_copies_are_identical() -> None:
    """MONOREPO-ONLY: pins the two committed copies byte-identical. At repo
    split, delete this test and compare the artifacts in the release
    pipeline instead — the per-side guards above/in vitest keep working."""
    assert _VIEWER_COPY.is_file(), (
        f"missing {_VIEWER_COPY} — run: uv run python -m plot_mcp.schema_export --wire"
    )
    assert _ENGINE_COPY.read_bytes() == _VIEWER_COPY.read_bytes()
