"""sqlite-vec adapter implementing :class:`VectorIndexPort`.

Schema (created on first connect):
  chunks(id INTEGER PK AUTOINCREMENT, rel_path TEXT NOT NULL, chunk_idx INT NOT NULL,
         text TEXT NOT NULL, meta_json TEXT NOT NULL DEFAULT '{}')
  vec_chunks vec0(embedding float[<dim>])     -- rowid mirrors chunks.id

``add_file`` is destructive-then-insert: prior rows for the same ``rel_path``
are deleted before the new chunks are inserted. This keeps the upsert path
simple and avoids stale vector ↔ row mismatches.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import numpy as np

from ..domain.models import ChunkData, SearchHit


class SqliteVecIndex:
    def __init__(self, db_path: Path, dim: int):
        self.db_path = db_path
        self.dim = int(dim)
        self._conn: sqlite3.Connection | None = None

    # -------------------------------------------------------------- lifecycle

    def _connect(self) -> sqlite3.Connection:
        import sqlite_vec

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        conn.row_factory = sqlite3.Row
        return conn

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = self._connect()
            self._init_schema(self._conn)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              rel_path TEXT NOT NULL,
              chunk_idx INTEGER NOT NULL,
              text TEXT NOT NULL,
              meta_json TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chunks_rel_path ON chunks(rel_path)"
        )
        conn.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(embedding float[{self.dim}])"
        )
        conn.commit()

    @contextmanager
    def _txn(self) -> Iterator[sqlite3.Connection]:
        conn = self.conn
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    # ----------------------------------------------------------------- writes

    def delete_file(self, rel_path: str) -> int:
        with self._txn() as conn:
            ids = [
                int(r[0])
                for r in conn.execute(
                    "SELECT id FROM chunks WHERE rel_path = ?", (rel_path,)
                ).fetchall()
            ]
            if ids:
                qmarks = ",".join("?" * len(ids))
                conn.execute(f"DELETE FROM vec_chunks WHERE rowid IN ({qmarks})", ids)
                conn.execute(f"DELETE FROM chunks WHERE id IN ({qmarks})", ids)
            return len(ids)

    def add_file(
        self,
        rel_path: str,
        chunks: list[ChunkData],
        embeddings: np.ndarray,
    ) -> list[int]:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        if embeddings.ndim != 2 or embeddings.shape[1] != self.dim:
            raise ValueError(
                f"embedding shape mismatch: got {embeddings.shape}, expected (N, {self.dim})"
            )
        self.delete_file(rel_path)
        ids: list[int] = []
        with self._txn() as conn:
            for idx, (chunk, vec) in enumerate(zip(chunks, embeddings)):
                cur = conn.execute(
                    "INSERT INTO chunks(rel_path, chunk_idx, text, meta_json) VALUES (?, ?, ?, ?)",
                    (
                        rel_path,
                        idx,
                        chunk.text,
                        json.dumps(chunk.meta, ensure_ascii=False),
                    ),
                )
                chunk_id = int(cur.lastrowid)
                conn.execute(
                    "INSERT INTO vec_chunks(rowid, embedding) VALUES (?, ?)",
                    (chunk_id, np.asarray(vec, dtype=np.float32).tobytes()),
                )
                ids.append(chunk_id)
        return ids

    # ------------------------------------------------------------------ reads

    def search(self, query_vec: np.ndarray, k: int = 8) -> list[SearchHit]:
        q = np.asarray(query_vec, dtype=np.float32)
        if q.shape != (self.dim,):
            raise ValueError(f"query_vec shape {q.shape} != ({self.dim},)")
        rows = self.conn.execute(
            """
            SELECT c.id AS id, c.rel_path AS rel_path, c.chunk_idx AS chunk_idx,
                   c.text AS text, c.meta_json AS meta_json, v.distance AS distance
            FROM vec_chunks v
            JOIN chunks c ON c.id = v.rowid
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance
            """,
            (q.tobytes(), int(k)),
        ).fetchall()
        return [
            SearchHit(
                chunk_id=int(r["id"]),
                rel_path=r["rel_path"],
                chunk_idx=int(r["chunk_idx"]),
                text=r["text"],
                meta=json.loads(r["meta_json"] or "{}"),
                distance=float(r["distance"]),
            )
            for r in rows
        ]

    def list_files(self) -> list[str]:
        return [
            r[0]
            for r in self.conn.execute(
                "SELECT DISTINCT rel_path FROM chunks ORDER BY rel_path"
            ).fetchall()
        ]

    def stats(self) -> dict[str, int]:
        files = self.conn.execute(
            "SELECT COUNT(DISTINCT rel_path) FROM chunks"
        ).fetchone()[0]
        chunks = self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return {"files": int(files), "chunks": int(chunks)}

    def get_chunk(self, chunk_id: int) -> SearchHit | None:
        row = self.conn.execute(
            "SELECT id, rel_path, chunk_idx, text, meta_json FROM chunks WHERE id = ?",
            (chunk_id,),
        ).fetchone()
        if row is None:
            return None
        return SearchHit(
            chunk_id=int(row["id"]),
            rel_path=row["rel_path"],
            chunk_idx=int(row["chunk_idx"]),
            text=row["text"],
            meta=json.loads(row["meta_json"] or "{}"),
            distance=0.0,
        )
