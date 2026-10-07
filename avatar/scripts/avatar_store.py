from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

from avatar_common import (
    AvatarError,
    JsonObject,
    canonical_json,
    complete_origin,
    digest,
    now,
)
from avatar_projection import has_newer, validate_history, version_digests
from avatar_view import check as read_check
from avatar_view import export as read_export
from avatar_view import show as read_show


class AvatarStore:
    def __init__(self, home: Path) -> None:
        self.home = home
        self.path = home / "avatar.db"

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    def _connect(self, create: bool = True) -> sqlite3.Connection:
        if create:
            self.home.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        if create:
            self._initialize(connection)
        return connection

    @staticmethod
    def _initialize(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            );
            INSERT OR IGNORE INTO meta(key, value) VALUES ('generation', 0);
            CREATE TABLE IF NOT EXISTS requests (
                idempotency_key TEXT PRIMARY KEY,
                payload_digest TEXT NOT NULL,
                response_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS choices (
                id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS criteria (
                id TEXT PRIMARY KEY,
                current_version INTEGER NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS criterion_versions (
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                PRIMARY KEY (id, version)
            );
            CREATE TABLE IF NOT EXISTS criterion_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL,
                version INTEGER NOT NULL,
                kind TEXT NOT NULL,
                generation INTEGER NOT NULL,
                origin_json TEXT,
                reason TEXT,
                recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projections (
                envelope_digest TEXT PRIMARY KEY,
                producer TEXT NOT NULL,
                generation INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projection_versions (
                ref TEXT PRIMARY KEY,
                version_digest TEXT NOT NULL
            );
            """
        )

    @contextmanager
    def _write(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _generation(connection: sqlite3.Connection) -> int:
        row = connection.execute("SELECT value FROM meta WHERE key = 'generation'").fetchone()
        return int(row["value"])

    @classmethod
    def _increment_generation(cls, connection: sqlite3.Connection) -> int:
        connection.execute("UPDATE meta SET value = value + 1 WHERE key = 'generation'")
        return cls._generation(connection)

    @staticmethod
    def _request_digest(action: str, payload: JsonObject) -> str:
        return digest({"action": action, "payload": payload})

    @classmethod
    def _replay(
        cls, connection: sqlite3.Connection, key: str, action: str, payload: JsonObject
    ) -> Optional[JsonObject]:
        row = connection.execute(
            "SELECT payload_digest, response_json FROM requests WHERE idempotency_key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        if row["payload_digest"] != cls._request_digest(action, payload):
            raise AvatarError(
                "E_IDEMPOTENCY_CONFLICT", "The idempotency key was used for another request."
            )
        response = json.loads(row["response_json"])
        response["replayed"] = True
        return response

    @classmethod
    def _remember(
        cls,
        connection: sqlite3.Connection,
        key: str,
        action: str,
        payload: JsonObject,
        response: JsonObject,
    ) -> None:
        connection.execute(
            "INSERT INTO requests(idempotency_key, payload_digest, response_json) VALUES (?, ?, ?)",
            (key, cls._request_digest(action, payload), canonical_json(response)),
        )

    def add_choice(self, key: str, payload: JsonObject) -> JsonObject:
        with self._write() as connection:
            replay = self._replay(connection, key, "choice_add", payload)
            if replay is not None:
                return replay
            choice_id = f"CH-{uuid.uuid4().hex[:12]}"
            recorded_at = now()
            connection.execute(
                "INSERT INTO choices(id, payload_json, recorded_at) VALUES (?, ?, ?)",
                (choice_id, canonical_json({**payload, "origin": complete_origin(payload["origin"])}), recorded_at),
            )
            generation = self._increment_generation(connection)
            response = {
                "id": choice_id,
                "generation": generation,
                "recorded_at": recorded_at,
                "replayed": False,
            }
            self._remember(connection, key, "choice_add", payload, response)
            return response

    def propose(self, key: str, payload: JsonObject) -> JsonObject:
        with self._write() as connection:
            replay = self._replay(connection, key, "criterion_propose", payload)
            if replay is not None:
                return replay
            criterion_id = f"PC-{uuid.uuid4().hex[:12]}"
            version = self._criterion_payload(payload, version=1, confirmation="none")
            recorded_at = now()
            version["recorded_at"] = recorded_at
            connection.execute(
                "INSERT INTO criteria(id, current_version, revoked) VALUES (?, 1, 0)",
                (criterion_id,),
            )
            self._insert_version(connection, criterion_id, 1, version)
            generation = self._increment_generation(connection)
            self._insert_event(connection, criterion_id, 1, "proposed", generation, version)
            response = self._criterion_response(criterion_id, 1, generation)
            self._remember(connection, key, "criterion_propose", payload, response)
            return response

    def confirm(
        self, criterion_id: str, version: int, key: str, payload: JsonObject
    ) -> JsonObject:
        request = {"id": criterion_id, "version": version, "payload": payload}
        with self._write() as connection:
            replay = self._replay(connection, key, "criterion_confirm", request)
            if replay is not None:
                return replay
            current = self._require_current(connection, criterion_id, version)
            next_version = version + 1
            updated = dict(current)
            updated.update(
                {
                    "version": next_version,
                    "confirmation": "user_confirmed",
                    "origin": payload["origin"],
                    "reason": payload.get("reason", "Confirmed by the user."),
                    "supersedes": f"avatar:{criterion_id}@{version}",
                    "recorded_at": now(),
                }
            )
            self._insert_version(connection, criterion_id, next_version, updated)
            connection.execute(
                "UPDATE criteria SET current_version = ? WHERE id = ?", (next_version, criterion_id)
            )
            generation = self._increment_generation(connection)
            self._insert_event(connection, criterion_id, next_version, "confirmed", generation, updated)
            response = self._criterion_response(criterion_id, next_version, generation)
            self._remember(connection, key, "criterion_confirm", request, response)
            return response

    def revise(self, criterion_id: str, key: str, payload: JsonObject) -> JsonObject:
        request = {"id": criterion_id, "payload": payload}
        base_version = int(payload["base_version"])
        with self._write() as connection:
            replay = self._replay(connection, key, "criterion_revise", request)
            if replay is not None:
                return replay
            current = self._require_current(connection, criterion_id, base_version)
            next_version = base_version + 1
            updated = dict(current)
            for field in (
                "statement",
                "applies_when",
                "exceptions",
                "notes",
                "overrides",
                "ai_confidence",
                "origin",
            ):
                if field in payload:
                    updated[field] = payload[field]
            updated["origin"] = payload.get("origin")
            updated.update(
                {
                    "version": next_version,
                    "confirmation": "none",
                    "reason": payload["reason"],
                    "supersedes": f"avatar:{criterion_id}@{base_version}",
                    "recorded_at": now(),
                }
            )
            self._insert_version(connection, criterion_id, next_version, updated)
            connection.execute(
                "UPDATE criteria SET current_version = ? WHERE id = ?", (next_version, criterion_id)
            )
            generation = self._increment_generation(connection)
            self._insert_event(connection, criterion_id, next_version, "revised", generation, updated)
            response = self._criterion_response(criterion_id, next_version, generation)
            self._remember(connection, key, "criterion_revise", request, response)
            return response

    def revoke(self, criterion_id: str, key: str, payload: JsonObject) -> JsonObject:
        request = {"id": criterion_id, "payload": payload}
        base_version = int(payload["base_version"])
        with self._write() as connection:
            replay = self._replay(connection, key, "criterion_revoke", request)
            if replay is not None:
                return replay
            self._require_current(connection, criterion_id, base_version)
            connection.execute("UPDATE criteria SET revoked = 1 WHERE id = ?", (criterion_id,))
            generation = self._increment_generation(connection)
            event_payload = {"origin": payload["origin"], "reason": payload["reason"]}
            self._insert_event(
                connection, criterion_id, base_version, "revoked", generation, event_payload
            )
            response = {
                "ref": f"avatar:{criterion_id}@{base_version}",
                "generation": generation,
                "revoked": True,
                "replayed": False,
            }
            self._remember(connection, key, "criterion_revoke", request, response)
            return response

    def attach_projection(self, key: str, payload: JsonObject) -> JsonObject:
        with self._write() as connection:
            replay = self._replay(connection, key, "source_attach", payload)
            if replay is not None:
                return replay
            envelope_digest = digest(payload)
            duplicate = connection.execute(
                "SELECT 1 FROM projections WHERE envelope_digest = ?", (envelope_digest,)
            ).fetchone()
            if duplicate is not None:
                response = {
                    "duplicate": True,
                    "generation": int(payload["generation"]),
                    "newer_projection_exists": self._has_newer_projection(connection, payload),
                    "replayed": False,
                }
                self._remember(connection, key, "source_attach", payload, response)
                return response

            version_digests = self._projection_version_digests(payload)
            for ref, version_digest in version_digests.items():
                row = connection.execute(
                    "SELECT version_digest FROM projection_versions WHERE ref = ?", (ref,)
                ).fetchone()
                if row is not None and row["version_digest"] != version_digest:
                    raise AvatarError(
                        "E_PROJECTION_CONFLICT", f"Projected version {ref} changed content."
                    )

            self._validate_projection_history(connection, payload, envelope_digest)
            fetched_at = now()
            connection.execute(
                """INSERT INTO projections(
                       envelope_digest, producer, generation, payload_json, fetched_at
                   ) VALUES (?, ?, ?, ?, ?)""",
                (
                    envelope_digest,
                    payload["producer"],
                    int(payload["generation"]),
                    canonical_json(payload),
                    fetched_at,
                ),
            )
            for ref, version_digest in version_digests.items():
                connection.execute(
                    "INSERT OR IGNORE INTO projection_versions(ref, version_digest) VALUES (?, ?)",
                    (ref, version_digest),
                )
            generation = self._increment_generation(connection)
            response = {
                "duplicate": False,
                "generation": int(payload["generation"]),
                "avatar_generation": generation,
                "fetched_at": fetched_at,
                "newer_projection_exists": self._has_newer_projection(connection, payload),
                "replayed": False,
            }
            self._remember(connection, key, "source_attach", payload, response)
            return response

    def show(
        self, choice_id: Optional[str] = None, criterion_id: Optional[str] = None
    ) -> JsonObject:
        return read_show(self.path, choice_id, criterion_id)

    def check(self, refs: list[str]) -> JsonObject:
        return read_check(self.path, refs)

    def export(self, producer_version: str) -> JsonObject:
        return read_export(self.path, producer_version)

    @staticmethod
    def _criterion_payload(payload: JsonObject, version: int, confirmation: str) -> JsonObject:
        return {
            "version": version,
            "statement": payload["statement"],
            "applies_when": payload.get("applies_when", []),
            "exceptions": payload.get("exceptions", []),
            "notes": payload.get("notes", []),
            "overrides": payload.get("overrides", []),
            "confirmation": confirmation,
            "ai_confidence": payload.get("ai_confidence"),
            "origin": payload.get("origin"),
            "reason": payload.get("reason", "Proposed from recorded choices."),
            "supersedes": None,
            "from_choices": payload.get("from_choices", []),
        }

    @staticmethod
    def _criterion_response(criterion_id: str, version: int, generation: int) -> JsonObject:
        return {
            "id": criterion_id,
            "ref": f"avatar:{criterion_id}@{version}",
            "generation": generation,
            "replayed": False,
        }

    @staticmethod
    def _insert_version(
        connection: sqlite3.Connection, criterion_id: str, version: int, payload: JsonObject
    ) -> None:
        payload["origin"] = complete_origin(payload.get("origin"))
        connection.execute(
            """INSERT INTO criterion_versions(id, version, payload_json, recorded_at)
               VALUES (?, ?, ?, ?)""",
            (criterion_id, version, canonical_json(payload), payload["recorded_at"]),
        )

    @staticmethod
    def _insert_event(
        connection: sqlite3.Connection,
        criterion_id: str,
        version: int,
        kind: str,
        generation: int,
        payload: JsonObject,
    ) -> None:
        connection.execute(
            """INSERT INTO criterion_events(
                   id, version, kind, generation, origin_json, reason, recorded_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                criterion_id,
                version,
                kind,
                generation,
                canonical_json(complete_origin(payload.get("origin"))),
                payload.get("reason"),
                now(),
            ),
        )

    @staticmethod
    def _require_current(
        connection: sqlite3.Connection, criterion_id: str, version: int
    ) -> JsonObject:
        criterion = connection.execute(
            "SELECT current_version, revoked FROM criteria WHERE id = ?", (criterion_id,)
        ).fetchone()
        if criterion is None:
            raise AvatarError("E_NOT_FOUND", f"Criterion {criterion_id} does not exist.")
        if criterion["revoked"]:
            raise AvatarError("E_REVOKED", f"Criterion {criterion_id} is revoked.")
        if int(criterion["current_version"]) != version:
            raise AvatarError("E_VERSION_CONFLICT", "The base version is not current.")
        row = connection.execute(
            "SELECT payload_json FROM criterion_versions WHERE id = ? AND version = ?",
            (criterion_id, version),
        ).fetchone()
        return json.loads(row["payload_json"])

    @staticmethod
    def _projection_version_digests(payload: JsonObject) -> dict[str, str]:
        return version_digests(payload)

    @staticmethod
    def _has_newer_projection(connection: sqlite3.Connection, payload: JsonObject) -> bool:
        return has_newer(connection, payload)

    @staticmethod
    def _validate_projection_history(
        connection: sqlite3.Connection, payload: JsonObject, envelope_digest: str
    ) -> None:
        validate_history(connection, payload, envelope_digest)
