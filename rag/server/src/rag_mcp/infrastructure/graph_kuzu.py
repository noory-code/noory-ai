"""Kuzu adapter implementing :class:`GraphIndexPort`.

Node tables:
  Chunk(id STRING PK, rel_path STRING, chunk_idx INT64)
  Entity(id STRING PK, name STRING, type STRING, community_id INT64, summary STRING)

Rel tables:
  MENTIONS(FROM Chunk TO Entity)
  RELATED(FROM Entity TO Entity, type STRING, weight DOUBLE)

RELATED edges are identified by (src, type, dst): ``relate`` upserts the edge
with the same type (overwriting its weight), while edges of distinct types
between the same node pair coexist.

``relate`` never drops a relation because an endpoint has not been upserted
yet: a relation implies both entities exist, so missing endpoints are MERGEd
as stub Entity nodes (name = id, type = "concept") and a later real
``upsert_entity`` enriches the stub in place.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.models import EntityRow, Subgraph


class KuzuGraphIndex:
    def __init__(self, db_dir: Path):
        self.db_dir = db_dir
        self._db: Any | None = None
        self._conn: Any | None = None

    # -------------------------------------------------------------- lifecycle

    def _open(self) -> None:
        import kuzu

        self.db_dir.parent.mkdir(parents=True, exist_ok=True)
        self._db = kuzu.Database(str(self.db_dir))
        self._conn = kuzu.Connection(self._db)
        self._init_schema()

    @property
    def conn(self) -> Any:
        if self._conn is None:
            self._open()
        return self._conn

    def close(self) -> None:
        self._conn = None
        self._db = None

    def _q(self, cypher: str, params: dict[str, Any] | None = None) -> Any:
        return self.conn.execute(cypher, parameters=params or {})

    def _init_schema(self) -> None:
        ddl = [
            (
                "CREATE NODE TABLE IF NOT EXISTS Chunk("
                "id STRING, rel_path STRING, chunk_idx INT64, PRIMARY KEY(id))"
            ),
            (
                "CREATE NODE TABLE IF NOT EXISTS Entity("
                "id STRING, name STRING, type STRING, community_id INT64, summary STRING,"
                " PRIMARY KEY(id))"
            ),
            "CREATE REL TABLE IF NOT EXISTS MENTIONS(FROM Chunk TO Entity)",
            (
                "CREATE REL TABLE IF NOT EXISTS RELATED("
                "FROM Entity TO Entity, type STRING, weight DOUBLE)"
            ),
        ]
        for query in ddl:
            self._q(query)

    # ------------------------------------------------------------ chunk nodes

    def upsert_chunk(self, chunk_id: str, rel_path: str, chunk_idx: int) -> None:
        self._q(
            "MERGE (c:Chunk {id: $id}) SET c.rel_path = $rp, c.chunk_idx = $ci",
            {"id": chunk_id, "rp": rel_path, "ci": int(chunk_idx)},
        )

    def delete_chunks_by_path(self, rel_path: str) -> None:
        self._q(
            "MATCH (c:Chunk {rel_path: $rp}) DETACH DELETE c",
            {"rp": rel_path},
        )

    # ----------------------------------------------------------- entity nodes

    def upsert_entity(
        self,
        entity_id: str,
        name: str,
        etype: str,
        *,
        community_id: int | None = None,
        summary: str = "",
    ) -> None:
        self._q(
            (
                "MERGE (e:Entity {id: $id}) "
                "SET e.name = $n, e.type = $t, e.community_id = $cid, e.summary = $sm"
            ),
            {
                "id": entity_id,
                "n": name,
                "t": etype,
                "cid": community_id if community_id is not None else -1,
                "sm": summary,
            },
        )

    def delete_entity(self, entity_id: str) -> None:
        self._q("MATCH (e:Entity {id: $id}) DETACH DELETE e", {"id": entity_id})

    # ----------------------------------------------------------------- edges

    def mention(self, chunk_id: str, entity_id: str) -> None:
        self._q(
            "MATCH (c:Chunk {id: $cid}), (e:Entity {id: $eid}) MERGE (c)-[:MENTIONS]->(e)",
            {"cid": chunk_id, "eid": entity_id},
        )

    def _merge_entity_stub(self, entity_id: str) -> None:
        """Ensure an Entity node exists without touching a real one.

        Stubs get name = id and type = "concept" (the same defaults the tool
        layer applies); a later ``upsert_entity`` overwrites them in place.
        """
        self._q(
            (
                "MERGE (e:Entity {id: $id}) "
                "ON CREATE SET e.name = $id, e.type = 'concept',"
                " e.community_id = -1, e.summary = ''"
            ),
            {"id": entity_id},
        )

    def relate(
        self,
        src_id: str,
        dst_id: str,
        *,
        rtype: str = "RELATED_TO",
        weight: float = 1.0,
    ) -> None:
        # A relation implies both endpoints exist. MERGE stubs for missing
        # endpoints so the edge is never silently dropped when relations
        # arrive before their entities (ordering-dependent upserts).
        self._merge_entity_stub(src_id)
        self._merge_entity_stub(dst_id)
        self._q(
            (
                "MATCH (a:Entity {id: $s}), (b:Entity {id: $d}) "
                "MERGE (a)-[r:RELATED {type: $t}]->(b) SET r.weight = $w"
            ),
            {"s": src_id, "d": dst_id, "t": rtype, "w": float(weight)},
        )

    def chunks_mentioning(self, entity_id: str) -> list[str]:
        result = self._q(
            (
                "MATCH (c:Chunk)-[:MENTIONS]->(e:Entity {id: $id}) "
                "RETURN c.id ORDER BY c.id"
            ),
            {"id": entity_id},
        )
        out: list[str] = []
        while result.has_next():
            out.append(result.get_next()[0])
        return out

    def relations_of(self, entity_id: str) -> list[tuple[str, str, str, float]]:
        result = self._q(
            (
                "MATCH (a:Entity)-[r:RELATED]->(b:Entity) "
                "WHERE a.id = $id OR b.id = $id "
                "RETURN a.id, b.id, r.type, r.weight"
            ),
            {"id": entity_id},
        )
        out: list[tuple[str, str, str, float]] = []
        while result.has_next():
            row = result.get_next()
            out.append((row[0], row[1], row[2] or "RELATED_TO", float(row[3] or 1.0)))
        return out

    # ----------------------------------------------------------------- reads

    @staticmethod
    def _row_to_entity(row: list[Any]) -> EntityRow:
        cid_raw = row[3]
        cid = int(cid_raw) if cid_raw is not None and cid_raw >= 0 else None
        return EntityRow(
            id=row[0],
            name=row[1],
            type=row[2],
            community_id=cid,
            summary=row[4] or "",
        )

    def _collect_entities(self, result: Any) -> list[EntityRow]:
        rows: list[EntityRow] = []
        while result.has_next():
            rows.append(self._row_to_entity(result.get_next()))
        return rows

    def find_entity_by_name(self, name: str) -> EntityRow | None:
        result = self._q(
            (
                "MATCH (e:Entity) WHERE lower(e.name) = lower($n) "
                "RETURN e.id, e.name, e.type, e.community_id, e.summary LIMIT 1"
            ),
            {"n": name},
        )
        if result.has_next():
            return self._row_to_entity(result.get_next())
        return None

    def list_entities(
        self, q: str | None = None, community_id: int | None = None
    ) -> list[EntityRow]:
        where: list[str] = []
        params: dict[str, Any] = {}
        if q:
            where.append("lower(e.name) CONTAINS lower($q)")
            params["q"] = q
        if community_id is not None:
            where.append("e.community_id = $cid")
            params["cid"] = int(community_id)
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        result = self._q(
            (
                f"MATCH (e:Entity){clause} "
                "RETURN e.id, e.name, e.type, e.community_id, e.summary "
                "ORDER BY e.name"
            ),
            params,
        )
        return self._collect_entities(result)

    def entities_mentioned_by_chunks(self, chunk_ids: list[str]) -> list[EntityRow]:
        if not chunk_ids:
            return []
        result = self._q(
            (
                "MATCH (c:Chunk)-[:MENTIONS]->(e:Entity) "
                "WHERE c.id IN $ids "
                "RETURN DISTINCT e.id, e.name, e.type, e.community_id, e.summary"
            ),
            {"ids": chunk_ids},
        )
        return self._collect_entities(result)

    def expand_neighbors(self, entity_ids: list[str], depth: int = 2) -> Subgraph:
        if not entity_ids:
            return Subgraph()
        depth = int(depth)
        if depth <= 0:
            return Subgraph()  # 0 = no graph expansion (honor the schema minimum)
        depth = min(depth, 4)
        nodes_result = self._q(
            (
                "MATCH (e:Entity)-[r:RELATED*1..%d]-(n:Entity) "
                "WHERE e.id IN $ids "
                "RETURN DISTINCT n.id, n.name, n.type, n.community_id, n.summary"
            )
            % depth,
            {"ids": entity_ids},
        )
        neighbors = self._collect_entities(nodes_result)

        scope_ids = list({*entity_ids, *(n.id for n in neighbors)})
        edges: list[tuple[str, str, str, float]] = []
        edges_result = self._q(
            (
                "MATCH (a:Entity)-[r:RELATED]->(b:Entity) "
                "WHERE a.id IN $ids AND b.id IN $ids "
                "RETURN a.id, b.id, r.type, r.weight"
            ),
            {"ids": scope_ids},
        )
        while edges_result.has_next():
            row = edges_result.get_next()
            edges.append((row[0], row[1], row[2] or "RELATED_TO", float(row[3] or 1.0)))

        seed_result = self._q(
            (
                "MATCH (e:Entity) WHERE e.id IN $ids "
                "RETURN e.id, e.name, e.type, e.community_id, e.summary"
            ),
            {"ids": entity_ids},
        )
        seeds = self._collect_entities(seed_result)
        all_nodes = {n.id: n for n in seeds}
        for n in neighbors:
            all_nodes.setdefault(n.id, n)
        return Subgraph(nodes=list(all_nodes.values()), edges=edges)

    def all_edges(self) -> list[tuple[str, str, float]]:
        result = self._q(
            "MATCH (a:Entity)-[r:RELATED]->(b:Entity) RETURN a.id, b.id, r.weight"
        )
        out: list[tuple[str, str, float]] = []
        while result.has_next():
            row = result.get_next()
            out.append((row[0], row[1], float(row[2] or 1.0)))
        return out

    def all_entity_ids(self) -> list[str]:
        result = self._q("MATCH (e:Entity) RETURN e.id ORDER BY e.id")
        out: list[str] = []
        while result.has_next():
            out.append(result.get_next()[0])
        return out

    def set_community(self, entity_id: str, community_id: int) -> None:
        self._q(
            "MATCH (e:Entity {id: $id}) SET e.community_id = $c",
            {"id": entity_id, "c": int(community_id)},
        )

    def set_summary(self, entity_id: str, summary: str) -> None:
        self._q(
            "MATCH (e:Entity {id: $id}) SET e.summary = $s",
            {"id": entity_id, "s": summary},
        )

    def stats(self) -> dict[str, int]:
        def _count(query: str) -> int:
            result = self._q(query)
            if result.has_next():
                return int(result.get_next()[0])
            return 0

        entities = _count("MATCH (e:Entity) RETURN COUNT(e)")
        relations = _count("MATCH ()-[r:RELATED]->() RETURN COUNT(r)")
        mentions = _count("MATCH ()-[m:MENTIONS]->() RETURN COUNT(m)")
        chunk_nodes = _count("MATCH (c:Chunk) RETURN COUNT(c)")

        communities_q = self._q(
            "MATCH (e:Entity) WHERE e.community_id >= 0 RETURN DISTINCT e.community_id"
        )
        communities = 0
        while communities_q.has_next():
            _ = communities_q.get_next()
            communities += 1
        return {
            "entities": entities,
            "relations": relations,
            "mentions": mentions,
            "chunk_nodes": chunk_nodes,
            "communities": communities,
        }
