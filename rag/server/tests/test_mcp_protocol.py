"""Smoke test for the MCP server's tool registration.

We don't yet drive the full JSON-RPC handshake here — that requires a running
event loop, and FastMCP defers its session creation to the transport. Instead
we validate the in-process registry surface (every advertised tool can be
described, schemas are well-formed) and that the ``--probe`` mode emits the
same set.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]


def test_registry_describes_all_tools() -> None:
    from rag_mcp.server import REGISTRY, build_fastmcp

    names = REGISTRY.names()
    assert {
        "rag_get_settings",
        "rag_set_settings",
        "rag_diff_files",
        "rag_upsert_chunks",
        "rag_delete_file",
        "rag_search",
        "rag_search_graph",
        "rag_list_entities",
        "rag_rebalance_prep",
        "rag_rebalance_commit",
        "rag_stats",
        "rag_export",
        "rag_import",
        "rag_get_probes",
        "rag_set_probes",
        "rag_evaluate",
        "rag_record_feedback",
        "rag_get_feedback",
    } <= set(names)

    for entry in REGISTRY.describe():
        assert "description" in entry and entry["description"]
        assert "schema" in entry and entry["schema"]["type"] == "object"

    # FastMCP app should build cleanly even if we never start its loop.
    app = build_fastmcp()
    assert app is not None


def test_probe_mode_emits_full_tool_list() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "rag_mcp", "--probe"],
        cwd=SERVER_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["server"] == "rag"
    tool_names = {t["name"] for t in payload["tools"]}
    assert "rag_search" in tool_names
    # 13 core + 3 probe-evaluation + 2 feedback = 18. Keep this as a tripwire so
    # dropping or renaming a tool requires deliberate test+registry updates.
    assert len(tool_names) == 18
