"""MCP interface adapter — exposes use cases as MCP tools.

Tools delegate to the :class:`Container`. The container is built lazily on
the first tool call so that an unconfigured project (no `.noory/rag/settings.json`)
returns clear errors instead of crashing at startup.
"""

from __future__ import annotations

import tarfile
from pathlib import Path
from typing import Any

from . import __version__
from .application.rebalancer import MergeDecision, SummaryDecision
from .container import Container
from .domain.models import ChunkData, EntityData, RelationData
from .infrastructure import feedback_json as feedback_io
from .infrastructure import probes_json as probes_io
from .infrastructure import settings_json as settings_io
from .infrastructure import snapshot as snap
from .infrastructure.paths import RagPaths, RagPathsConfigError
from .infrastructure.settings_json import Settings


# -------------------------------------------------------------- Tool registry


class ToolRegistry:
    """Thin abstraction so we can self-document tools for --probe."""

    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}

    def add(self, name: str, description: str, schema: dict[str, Any]) -> None:
        self._tools[name] = {"description": description, "schema": schema}

    def names(self) -> list[str]:
        return sorted(self._tools.keys())

    def describe(self) -> list[dict[str, Any]]:
        return [{"name": n, **self._tools[n]} for n in self.names()]


REGISTRY = ToolRegistry()


# --------------------------------------------------------------- Tool helpers


class _State:
    """Mutable singleton lazily holding the wired Container.

    ``_settings_mtime_ns`` records the ``settings.json`` mtime observed when
    the container was wired. ``get`` rebuilds the container when the file
    changed on disk, so external edits are never served stale. Tests that
    inject a hand-wired container must pin ``_settings_mtime_ns`` too.
    """

    container: Container | None = None
    paths: RagPaths | None = None
    _settings_mtime_ns: int | None = None

    @staticmethod
    def _mtime_ns(file: Path) -> int | None:
        try:
            return file.stat().st_mtime_ns
        except OSError:
            return None

    @classmethod
    def get(cls) -> Container:
        if cls.container is not None and cls.paths is not None:
            if cls._mtime_ns(cls.paths.settings_file) != cls._settings_mtime_ns:
                cls.reset()  # settings.json changed on disk — rebuild
        if cls.container is None:
            cls.paths = cls.paths or RagPaths.from_cwd()
            cls._settings_mtime_ns = cls._mtime_ns(cls.paths.settings_file)
            settings = settings_io.load(cls.paths.settings_file)
            cls.container = Container.wire(cls.paths, settings)
        return cls.container

    @classmethod
    def get_paths_or_err(cls) -> tuple[RagPaths | None, dict[str, Any] | None]:
        """Resolve `RagPaths` or return a structured error response.

        Tools that don't yet have a wired Container (e.g. settings ops) use
        this so missing env config surfaces as a clean MCP error rather than
        an unhandled exception.
        """
        try:
            return RagPaths.from_cwd(), None
        except RagPathsConfigError as e:
            return None, _err(str(e))

    @classmethod
    def reset(cls) -> None:
        if cls.container is not None:
            cls.container.close()
        cls.container = None
        cls.paths = None
        cls._settings_mtime_ns = None


def _err(msg: str) -> dict[str, Any]:
    return {"ok": False, "error": msg}


def _bounds_err(name: str, value: int, lo: int, hi: int) -> dict[str, Any] | None:
    """Structured error when a numeric arg falls outside its REGISTRY schema bounds."""
    if lo <= value <= hi:
        return None
    return _err(f"{name} out of range [{lo}, {hi}]: {value}")


_CORRUPT_MANIFEST_WARNING = (
    "manifest.json was corrupt and has been ignored — all files are treated "
    "as new (full reindex)"
)


# ---------------------------------------------------------------- Tool impls


def tool_get_settings() -> dict[str, Any]:
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    if not paths.settings_file.exists():
        return _err("settings not found; run /rag:init-rag")
    return {"ok": True, "settings": settings_io.load(paths.settings_file).to_dict()}


REGISTRY.add(
    "rag_get_settings",
    "Return the current `.noory/rag/settings.json` contents.",
    {"type": "object", "properties": {}},
)


def tool_set_settings(settings: dict[str, Any]) -> dict[str, Any]:
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    try:
        parsed = settings_io.validate_dict(settings)
    except settings_io.SettingsError as e:
        return _err(f"invalid settings: {e}")
    paths.ensure_state_layout()
    settings_io.save(paths.settings_file, parsed)
    _State.reset()
    return {"ok": True}


REGISTRY.add(
    "rag_set_settings",
    "Write `.noory/rag/settings.json` with the given object after schema validation.",
    {
        "type": "object",
        "properties": {"settings": {"type": "object"}},
        "required": ["settings"],
    },
)


def tool_diff_files(source_path: str | None = None) -> dict[str, Any]:
    container = _State.get()
    sources = list(container.settings.sources)
    if source_path is not None:
        sources = [s for s in sources if s.path == source_path]
        if not sources:
            return _err(f"source not found in settings: {source_path}")
    diff = container.indexer.diff(sources)
    resp: dict[str, Any] = {"ok": True, **diff.to_dict()}
    if container.manifest.corrupt_detected:
        resp["warning"] = _CORRUPT_MANIFEST_WARNING
    return resp


REGISTRY.add(
    "rag_diff_files",
    "Walk configured sources and return added/changed/removed files vs. manifest.",
    {
        "type": "object",
        "properties": {"source_path": {"type": "string"}},
    },
)


def tool_upsert_chunks(
    file: str,
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]] | None = None,
    relations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    container = _State.get()
    chunk_models = [
        ChunkData(text=str(c["text"]), meta=dict(c.get("meta") or {})) for c in chunks
    ]
    entity_models = [
        EntityData(
            id=str(e["id"]),
            name=str(e.get("name", e["id"])),
            type=str(e.get("type", "concept")),
            chunk_indices=list(e.get("chunk_indices") or []),
        )
        for e in (entities or [])
    ]
    relation_models = [
        RelationData(
            src_id=str(r["src_id"]),
            dst_id=str(r["dst_id"]),
            type=str(r.get("type", "RELATED_TO")),
            weight=float(r.get("weight", 1.0)),
        )
        for r in (relations or [])
    ]
    result = container.indexer.upsert_file(
        file, chunk_models, entity_models, relation_models
    )
    resp: dict[str, Any] = {
        "ok": True,
        "chunk_ids": result.chunk_ids,
        "entity_ids": result.entity_ids,
    }

    # Update manifest for this file (incremental).
    file_abs = (container.paths.project_root / file).resolve()
    if file_abs.exists():
        hashes = container.manifest.load()
        if container.manifest.corrupt_detected:
            resp["warning"] = _CORRUPT_MANIFEST_WARNING
        hashes[file] = container.sources.hash_file(file_abs)
        container.manifest.save(hashes)

    return resp


REGISTRY.add(
    "rag_upsert_chunks",
    "Upsert pre-chunked text + extracted entities/relations for one file.",
    {
        "type": "object",
        "properties": {
            "file": {"type": "string"},
            "chunks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "meta": {"type": "object"},
                    },
                    "required": ["text"],
                },
            },
            "entities": {"type": "array"},
            "relations": {"type": "array"},
        },
        "required": ["file", "chunks"],
    },
)


def tool_delete_file(path: str) -> dict[str, Any]:
    container = _State.get()
    container.indexer.delete_file(path)
    hashes = container.manifest.load()
    if path in hashes:
        del hashes[path]
        container.manifest.save(hashes)
    return {"ok": True}


REGISTRY.add(
    "rag_delete_file",
    "Remove a file's chunks, entities-mentions, and manifest entry.",
    {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
)


def tool_search(query: str, k: int = 8, expand_depth: int | None = None) -> dict[str, Any]:
    k = int(k)
    if (bounds := _bounds_err("k", k, 1, 64)) is not None:
        return bounds
    try:
        container = _State.get()
    except (RagPathsConfigError, settings_io.SettingsError) as e:
        return _err(str(e))
    depth = int(
        expand_depth if expand_depth is not None else container.settings.graph.expand_depth
    )
    if (bounds := _bounds_err("expand_depth", depth, 0, 4)) is not None:
        return bounds
    result = container.searcher.search(query, k=k, expand_depth=depth)
    return {
        "ok": True,
        "chunks": [
            {
                "chunk_id": h.chunk_id,
                "rel_path": h.rel_path,
                "chunk_idx": h.chunk_idx,
                "text": h.text,
                "meta": h.meta,
                "distance": h.distance,
            }
            for h in result.chunks
        ],
        "entities": [
            {
                "id": e.id,
                "name": e.name,
                "type": e.type,
                "community_id": e.community_id,
                "summary": e.summary,
            }
            for e in result.entities
        ],
        "subgraph": {
            "nodes": [
                {"id": n.id, "name": n.name, "type": n.type} for n in result.subgraph.nodes
            ],
            "edges": [
                {"src": s, "dst": d, "type": t, "weight": w}
                for s, d, t, w in result.subgraph.edges
            ],
        },
    }


REGISTRY.add(
    "rag_search",
    "Hybrid vector + graph search. Returns chunks, mentioned entities, expanded subgraph.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "k": {"type": "integer", "minimum": 1, "maximum": 64},
            "expand_depth": {"type": "integer", "minimum": 0, "maximum": 4},
        },
        "required": ["query"],
    },
)


def tool_search_graph(entity: str, depth: int = 2) -> dict[str, Any]:
    depth = int(depth)
    if (bounds := _bounds_err("depth", depth, 1, 4)) is not None:
        return bounds
    container = _State.get()
    subgraph = container.searcher.search_graph(entity, depth=depth)
    return {
        "ok": True,
        "nodes": [{"id": n.id, "name": n.name, "type": n.type} for n in subgraph.nodes],
        "edges": [
            {"src": s, "dst": d, "type": t, "weight": w}
            for s, d, t, w in subgraph.edges
        ],
    }


REGISTRY.add(
    "rag_search_graph",
    "Graph-only N-hop expansion from a seed entity (by name or id).",
    {
        "type": "object",
        "properties": {
            "entity": {"type": "string"},
            "depth": {"type": "integer", "minimum": 1, "maximum": 4},
        },
        "required": ["entity"],
    },
)


def tool_list_entities(q: str | None = None, community_id: int | None = None) -> dict[str, Any]:
    container = _State.get()
    entities = container.graph.list_entities(q=q, community_id=community_id)
    return {
        "ok": True,
        "entities": [
            {
                "id": e.id,
                "name": e.name,
                "type": e.type,
                "community_id": e.community_id,
                "summary": e.summary,
            }
            for e in entities
        ],
    }


REGISTRY.add(
    "rag_list_entities",
    "List entities, optionally filtered by name substring and/or community id.",
    {
        "type": "object",
        "properties": {
            "q": {"type": "string"},
            "community_id": {"type": "integer"},
        },
    },
)


def tool_rebalance_prep() -> dict[str, Any]:
    container = _State.get()
    prep = container.rebalancer.prep()
    return {
        "ok": True,
        "alias_candidates": [
            {"keep_id": c.keep_id, "drop_id": c.drop_id, "name": c.name}
            for c in prep.alias_candidates
        ],
        "communities": [
            {
                "community_id": c.community_id,
                "member_ids": c.member_ids,
                "needs_summary": c.needs_summary,
            }
            for c in prep.communities
        ],
    }


REGISTRY.add(
    "rag_rebalance_prep",
    "Recompute communities (Leiden) and surface alias / summary-needed candidates.",
    {"type": "object", "properties": {}},
)


def tool_rebalance_commit(
    merges: list[dict[str, Any]] | None = None,
    summaries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    container = _State.get()
    merge_decisions = [
        MergeDecision(keep_id=str(m["keep_id"]), drop_id=str(m["drop_id"]))
        for m in (merges or [])
    ]
    summary_decisions = [
        SummaryDecision(
            community_id=int(s["community_id"]),
            summary=str(s.get("summary", "")),
            member_summary=dict(s.get("member_summary") or {}),
        )
        for s in (summaries or [])
    ]
    result = container.rebalancer.commit(merge_decisions, summary_decisions)
    return {
        "ok": True,
        "merged": result.merged,
        "summaries_applied": result.summaries_applied,
    }


REGISTRY.add(
    "rag_rebalance_commit",
    "Apply Claude's rebalance judgments back to the graph.",
    {
        "type": "object",
        "properties": {
            "merges": {"type": "array"},
            "summaries": {"type": "array"},
        },
    },
)


def tool_stats() -> dict[str, Any]:
    container = _State.get()
    vstats = container.vector.stats()
    gstats = container.graph.stats()
    return {
        "ok": True,
        "files": vstats.get("files", 0),
        "chunks": vstats.get("chunks", 0),
        "entities": gstats.get("entities", 0),
        "relations": gstats.get("relations", 0),
        "mentions": gstats.get("mentions", 0),
        "communities": gstats.get("communities", 0),
        "embedding_model": container.settings.embedding.model,
        "embedding_dim": container.settings.embedding.dim,
    }


REGISTRY.add(
    "rag_stats",
    "Report file/chunk/entity/relation/community counts and embedding config.",
    {"type": "object", "properties": {}},
)


def tool_export(out_path: str) -> dict[str, Any]:
    container = _State.get()
    # Order matters: stats read the live handles, THEN close flushes them,
    # THEN the tarball is built from fully-committed files. Computing stats
    # after close would silently reopen the connections close just flushed.
    stats = tool_stats()
    container.close()  # flush DB handles
    out = Path(out_path).expanduser().resolve()
    header = snap.export_snapshot(
        container.paths.state_dir,
        out,
        embedding_model=container.settings.embedding.model,
        embedding_dim=container.settings.embedding.dim,
        plugin_version=__version__,
        stats=stats,
    )
    _State.reset()
    return {"ok": True, "out_path": str(out), "header": header.to_json()}


REGISTRY.add(
    "rag_export",
    "Bundle `.noory/rag/` into a portable tarball with a compatibility header.",
    {"type": "object", "properties": {"out_path": {"type": "string"}}, "required": ["out_path"]},
)


def tool_import(in_path: str, mode: str = "replace") -> dict[str, Any]:
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    if mode not in {"replace", "merge"}:
        return _err(f"unsupported import mode: {mode}")
    src = Path(in_path).expanduser().resolve()
    try:
        # Read snapshot header first to check compat against current settings (if any).
        if paths.settings_file.exists():
            settings = settings_io.load(paths.settings_file)
            expected_model = settings.embedding.model
            expected_dim = settings.embedding.dim
        else:
            # No settings yet: trust the snapshot's embedding spec.
            header = snap.read_header(src)
            expected_model = header.embedding_model
            expected_dim = header.embedding_dim

        header = snap.import_snapshot(
            src,
            paths.state_dir,
            expected_model=expected_model,
            expected_dim=expected_dim,
            plugin_major=__version__.split(".")[0],
            mode=mode,
        )
    except snap.IncompatibleSnapshot as e:
        return _err(str(e))
    except settings_io.SettingsError as e:
        return _err(str(e))
    except (tarfile.ReadError, KeyError, EOFError, OSError, ValueError) as e:
        # Corrupt / truncated / not-a-tarball snapshots must surface as the
        # structured error shape, not as raw tarfile internals.
        return _err(f"unreadable snapshot {src}: {e}")
    _State.reset()
    return {"ok": True, "header": header.to_json()}


REGISTRY.add(
    "rag_import",
    "Restore `.noory/rag/` from a snapshot tarball. Refuses on incompatible embedding model/dim.",
    {
        "type": "object",
        "properties": {
            "in_path": {"type": "string"},
            "mode": {"type": "string", "enum": ["replace", "merge"]},
        },
        "required": ["in_path"],
    },
)


# ----------------------------------------------------------------- Probes API
#
# Probes are the user's representative questions, persisted to
# `.noory/rag/probes.json` (separate from `settings.json` so they are never
# shared via `/rag:rag-share-guide`). Three tools:
#
#   * rag_get_probes — read current probes (empty list if file absent)
#   * rag_set_probes — overwrite the whole list (Claude composes the new
#     list when the user runs `/rag:rag-probe-add` or `-remove`)
#   * rag_evaluate  — batch-run every probe through hybrid search; the
#     plugin returns raw search hits, the Claude session interprets them
#     into a diagnostic (no LLM-in-server design preserved).


def tool_get_probes() -> dict[str, Any]:
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    try:
        probes = probes_io.load(paths.probes_file)
    except probes_io.ProbesError as e:
        return _err(f"invalid probes: {e}")
    return {
        "ok": True,
        "probes": [{"id": p.id, "query": p.query, "note": p.note} for p in probes],
    }


REGISTRY.add(
    "rag_get_probes",
    "Return the current `.noory/rag/probes.json` contents (empty list if unset).",
    {"type": "object", "properties": {}},
)


def tool_set_probes(probes: list[dict[str, Any]]) -> dict[str, Any]:
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    try:
        domain_probes = probes_io.validate_payload({"probes": probes})
    except probes_io.ProbesError as e:
        return _err(f"invalid probes: {e}")
    paths.state_dir.mkdir(parents=True, exist_ok=True)
    try:
        probes_io.save(paths.probes_file, domain_probes)
    except probes_io.ProbesError as e:
        return _err(f"failed to save probes: {e}")
    return {"ok": True, "count": len(domain_probes)}


REGISTRY.add(
    "rag_set_probes",
    "Replace `.noory/rag/probes.json` with the given probe list (full overwrite).",
    {
        "type": "object",
        "properties": {
            "probes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "query": {"type": "string"},
                        "note": {"type": "string"},
                    },
                    "required": ["id", "query"],
                },
            }
        },
        "required": ["probes"],
    },
)


def tool_evaluate(
    probe_ids: list[str] | None = None,
    k: int = 5,
    expand_depth: int | None = None,
) -> dict[str, Any]:
    """Run every registered probe (or a filtered subset) through hybrid
    search and return the raw hits. The caller (Claude session) interprets
    them — this tool deliberately does NOT score or judge."""
    k = int(k)
    if (bounds := _bounds_err("k", k, 1, 32)) is not None:
        return bounds
    container = _State.get()
    try:
        probes = probes_io.load(container.paths.probes_file)
    except probes_io.ProbesError as e:
        return _err(f"invalid probes: {e}")

    if not probes:
        return _err(
            "no probes registered; add one with /rag:rag-probe-add "
            "(or call rag_set_probes)"
        )

    if probe_ids is not None:
        wanted = set(probe_ids)
        probes = tuple(p for p in probes if p.id in wanted)
        if not probes:
            return _err(f"no probes matched ids: {sorted(wanted)}")

    depth = int(
        expand_depth
        if expand_depth is not None
        else container.settings.graph.expand_depth
    )
    if (bounds := _bounds_err("expand_depth", depth, 0, 4)) is not None:
        return bounds

    results: list[dict[str, Any]] = []
    for probe in probes:
        hit = container.searcher.search(probe.query, k=k, expand_depth=depth)
        chunks = [
            {
                "chunk_id": c.chunk_id,
                "rel_path": c.rel_path,
                "chunk_idx": c.chunk_idx,
                "text": c.text,
                "distance": c.distance,
            }
            for c in hit.chunks
        ]
        results.append(
            {
                "probe_id": probe.id,
                "query": probe.query,
                "note": probe.note,
                "top_k": len(chunks),
                "chunks": chunks,
                "entities": [
                    {"id": e.id, "name": e.name, "type": e.type}
                    for e in hit.entities
                ],
                # Cheap aggregates the Claude session can lean on while
                # composing a diagnostic. No judgement embedded here.
                "stats": {
                    "min_distance": (
                        min((c.distance for c in hit.chunks), default=None)
                    ),
                    "max_distance": (
                        max((c.distance for c in hit.chunks), default=None)
                    ),
                    "unique_files": len({c.rel_path for c in hit.chunks}),
                },
            }
        )

    return {"ok": True, "k": int(k), "expand_depth": int(depth), "results": results}


REGISTRY.add(
    "rag_evaluate",
    "Run every registered probe through hybrid search and return raw hits "
    "+ cheap stats. Claude interprets the results into a diagnostic.",
    {
        "type": "object",
        "properties": {
            "probe_ids": {"type": "array", "items": {"type": "string"}},
            "k": {"type": "integer", "minimum": 1, "maximum": 32},
            "expand_depth": {"type": "integer", "minimum": 0, "maximum": 4},
        },
    },
)


# --------------------------------------------------------------- Feedback API
#
# Feedback is the self-improvement signal: a good/bad verdict on a search
# result, stored in `.noory/rag/feedback.json` (personal, gitignored). The
# searcher re-ranks by per-rel_path net verdict (see application.searcher).


def tool_record_feedback(query: str, rel_path: str, verdict: str) -> dict[str, Any]:
    """Record a good/bad verdict on a search result (query, rel_path)."""
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    try:
        entry = feedback_io.append(paths.feedback_file, query, rel_path, verdict)
    except feedback_io.FeedbackError as e:
        return _err(f"invalid feedback: {e}")
    return {"ok": True, "recorded": entry}


REGISTRY.add(
    "rag_record_feedback",
    "Record a good/bad verdict on a search result (query + rel_path). Feeds the "
    "self-improving re-rank; stored in `.noory/rag/feedback.json` (personal).",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "rel_path": {"type": "string"},
            "verdict": {"type": "string", "enum": ["good", "bad"]},
        },
        "required": ["query", "rel_path", "verdict"],
    },
)


def tool_get_feedback() -> dict[str, Any]:
    """Return all recorded feedback + per-rel_path net boosts."""
    paths, err = _State.get_paths_or_err()
    if err is not None:
        return err
    assert paths is not None
    try:
        records = feedback_io.load(paths.feedback_file)
    except feedback_io.FeedbackError as e:
        return _err(f"invalid feedback: {e}")
    return {
        "ok": True,
        "feedback": records,
        "boosts": feedback_io.aggregate_boosts(records),
        "count": len(records),
    }


REGISTRY.add(
    "rag_get_feedback",
    "Return recorded search feedback and per-rel_path net boosts (good=+1, "
    "bad=-1). Claude aggregates this into a feedback report.",
    {"type": "object", "properties": {}},
)


# ---------------------------------------------------------------- MCP wiring


def build_fastmcp():
    from mcp.server.fastmcp import FastMCP

    app = FastMCP("rag")

    @app.tool()
    def rag_get_settings() -> dict[str, Any]:
        """Return the current `.noory/rag/settings.json` contents."""
        return tool_get_settings()

    @app.tool()
    def rag_set_settings(settings: dict[str, Any]) -> dict[str, Any]:
        """Write `.noory/rag/settings.json` after schema validation."""
        return tool_set_settings(settings)

    @app.tool()
    def rag_diff_files(source_path: str | None = None) -> dict[str, Any]:
        """Return added/changed/removed files vs. manifest."""
        return tool_diff_files(source_path)

    @app.tool()
    def rag_upsert_chunks(
        file: str,
        chunks: list[dict[str, Any]],
        entities: list[dict[str, Any]] | None = None,
        relations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Upsert pre-chunked text + extracted entities/relations for one file."""
        return tool_upsert_chunks(file, chunks, entities, relations)

    @app.tool()
    def rag_delete_file(path: str) -> dict[str, Any]:
        """Remove a file's chunks and graph mentions."""
        return tool_delete_file(path)

    @app.tool()
    def rag_search(
        query: str, k: int = 8, expand_depth: int | None = None
    ) -> dict[str, Any]:
        """Hybrid vector + graph search."""
        return tool_search(query, k, expand_depth)

    @app.tool()
    def rag_search_graph(entity: str, depth: int = 2) -> dict[str, Any]:
        """Graph-only N-hop expansion from a seed entity."""
        return tool_search_graph(entity, depth)

    @app.tool()
    def rag_list_entities(
        q: str | None = None, community_id: int | None = None
    ) -> dict[str, Any]:
        """List entities, optionally filtered."""
        return tool_list_entities(q, community_id)

    @app.tool()
    def rag_rebalance_prep() -> dict[str, Any]:
        """Recompute communities and surface alias / summary candidates."""
        return tool_rebalance_prep()

    @app.tool()
    def rag_rebalance_commit(
        merges: list[dict[str, Any]] | None = None,
        summaries: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Apply rebalance judgments back to the graph."""
        return tool_rebalance_commit(merges, summaries)

    @app.tool()
    def rag_stats() -> dict[str, Any]:
        """Report index counts and embedding config."""
        return tool_stats()

    @app.tool()
    def rag_export(out_path: str) -> dict[str, Any]:
        """Bundle `.noory/rag/` into a portable tarball."""
        return tool_export(out_path)

    @app.tool()
    def rag_import(in_path: str, mode: str = "replace") -> dict[str, Any]:
        """Restore `.noory/rag/` from a snapshot tarball."""
        return tool_import(in_path, mode)

    @app.tool()
    def rag_get_probes() -> dict[str, Any]:
        """Return the user's registered evaluation probes."""
        return tool_get_probes()

    @app.tool()
    def rag_set_probes(probes: list[dict[str, Any]]) -> dict[str, Any]:
        """Replace `.noory/rag/probes.json` with the given probe list."""
        return tool_set_probes(probes)

    @app.tool()
    def rag_evaluate(
        probe_ids: list[str] | None = None,
        k: int = 5,
        expand_depth: int | None = None,
    ) -> dict[str, Any]:
        """Run every probe (or a subset) through hybrid search."""
        return tool_evaluate(probe_ids, k, expand_depth)

    @app.tool()
    def rag_record_feedback(query: str, rel_path: str, verdict: str) -> dict[str, Any]:
        """Record a good/bad verdict on a search result (query + rel_path)."""
        return tool_record_feedback(query, rel_path, verdict)

    @app.tool()
    def rag_get_feedback() -> dict[str, Any]:
        """Return recorded feedback + per-rel_path net boosts."""
        return tool_get_feedback()

    return app


def serve() -> None:
    app = build_fastmcp()
    app.run()


def probe() -> dict[str, Any]:
    """Return a JSON-serialisable description of every registered tool."""
    return {"server": "rag", "version": __version__, "tools": REGISTRY.describe()}
