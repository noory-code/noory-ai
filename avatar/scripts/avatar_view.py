from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from avatar_common import AvatarError, JsonObject, canonical_json, now
from avatar_projection import criterion_id as projection_criterion_id


def show(
    path: Path, choice_id: Optional[str] = None, criterion_id: Optional[str] = None
) -> JsonObject:
    if store_absent(path):
        if choice_id or criterion_id:
            raise AvatarError("E_NOT_FOUND", "The requested record does not exist.")
        return {"choices": [], "criteria": [], "projections": [], "review_candidates": []}
    connection = connect(path)
    try:
        choices = read_choices(connection, choice_id)
        return {
            "choices": choices,
            "criteria": read_criteria(connection, criterion_id),
            "projections": read_projections(connection),
            "review_candidates": review_candidates(choices),
        }
    finally:
        connection.close()


def check(path: Path, refs: list[str]) -> JsonObject:
    if store_absent(path):
        return {
            "generation": 0,
            "checked_at": now(),
            "results": [unknown_or_scope_mismatch(ref) for ref in refs],
            "store": "absent",
        }
    connection = connect(path)
    try:
        generation = connection.execute(
            "SELECT value FROM meta WHERE key = 'generation'"
        ).fetchone()["value"]
        return {
            "generation": int(generation),
            "checked_at": now(),
            "results": [check_ref(connection, ref) for ref in refs],
        }
    finally:
        connection.close()


def export(path: Path, producer_version: str) -> JsonObject:
    result: JsonObject = {
        "schema": "criteria-snapshot/1",
        "producer": "avatar",
        "producer_version": producer_version,
        "generation": 0,
        "checked_at": now(),
        "scope": {"kind": "personal", "key": "personal"},
        "criteria": [],
        "retired": [],
    }
    if store_absent(path):
        result["store"] = "absent"
        return result
    connection = connect(path)
    try:
        result["generation"] = int(
            connection.execute("SELECT value FROM meta WHERE key = 'generation'").fetchone()["value"]
        )
        for criterion in read_criteria(connection, None):
            current_version = criterion["current_version"]
            for version in criterion["versions"]:
                ref = version["ref"]
                if version["version"] == current_version:
                    if criterion["revoked"]:
                        result["retired"].append({"ref": ref, "status": "revoked"})
                    elif version["confirmation"] == "user_confirmed":
                        result["criteria"].append(version)
                else:
                    result["retired"].append(
                        {
                            "ref": ref,
                            "status": "superseded",
                            "by": f"avatar:{criterion['id']}@{current_version}",
                        }
                    )
        return result
    finally:
        connection.close()


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", timeout=30, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    connection.execute("BEGIN")
    return connection


def store_absent(path: Path) -> bool:
    if path.parent.exists() and not path.parent.is_dir():
        raise OSError("Avatar home must be a directory.")
    if path.exists() and not path.is_file():
        raise OSError("Avatar database must be a file.")
    return not path.exists()


def read_choices(
    connection: sqlite3.Connection, choice_id: Optional[str]
) -> list[JsonObject]:
    query = "SELECT id, payload_json, recorded_at FROM choices"
    parameters: tuple[object, ...] = ()
    if choice_id is not None:
        query += " WHERE id = ?"
        parameters = (choice_id,)
    query += " ORDER BY recorded_at, id"
    choices = []
    for row in connection.execute(query, parameters):
        item = json.loads(row["payload_json"])
        item.update({"id": row["id"], "recorded_at": row["recorded_at"]})
        choices.append(item)
    if choice_id is not None and not choices:
        raise AvatarError("E_NOT_FOUND", f"Choice {choice_id} does not exist.")
    return choices


def read_criteria(
    connection: sqlite3.Connection, criterion_id: Optional[str]
) -> list[JsonObject]:
    query = "SELECT id, current_version, revoked FROM criteria"
    parameters: tuple[object, ...] = ()
    if criterion_id is not None:
        query += " WHERE id = ?"
        parameters = (criterion_id,)
    query += " ORDER BY id"
    criteria = []
    for row in connection.execute(query, parameters):
        versions = []
        version_rows = connection.execute(
            "SELECT version, payload_json FROM criterion_versions WHERE id = ? ORDER BY version",
            (row["id"],),
        )
        for version_row in version_rows:
            version = json.loads(version_row["payload_json"])
            version["ref"] = f"avatar:{row['id']}@{version_row['version']}"
            versions.append(version)
        criteria.append(
            {
                "id": row["id"],
                "current_version": int(row["current_version"]),
                "revoked": bool(row["revoked"]),
                "versions": versions,
                "events": read_events(connection, row["id"]),
            }
        )
    if criterion_id is not None and not criteria:
        raise AvatarError("E_NOT_FOUND", f"Criterion {criterion_id} does not exist.")
    return criteria


def read_events(connection: sqlite3.Connection, identifier: str) -> list[JsonObject]:
    events = []
    for row in connection.execute(
        "SELECT * FROM criterion_events WHERE id = ? ORDER BY sequence", (identifier,)
    ):
        event = dict(row)
        event["origin"] = json.loads(event.pop("origin_json"))
        events.append(event)
    return events


def read_projections(connection: sqlite3.Connection) -> list[JsonObject]:
    rows = list(
        connection.execute(
            """SELECT producer, generation, payload_json, fetched_at
               FROM projections ORDER BY producer, generation DESC, fetched_at DESC"""
        )
    )
    highest: dict[str, int] = {}
    for row in rows:
        key = projection_criterion_id(json.loads(row["payload_json"]))
        highest[key] = max(highest.get(key, -1), row["generation"])
    return [
        {
            "producer": row["producer"],
            "generation": int(row["generation"]),
            "fetched_at": row["fetched_at"],
            "current_status_verified": False,
            "newer_projection_exists": row["generation"] < highest[
                projection_criterion_id(json.loads(row["payload_json"]))
            ],
            "history": json.loads(row["payload_json"]),
        }
        for row in rows
    ]


def review_candidates(choices: list[JsonObject]) -> list[JsonObject]:
    result = []
    for index, left in enumerate(choices):
        for right in choices[index + 1 :]:
            shared_refs = sorted(
                set(left.get("source_refs", [])) & set(right.get("source_refs", []))
            )
            if not shared_refs or left.get("chosen") == right.get("chosen"):
                continue
            result.append(
                {
                    "choice_ids": [left["id"], right["id"]],
                    "source_refs": shared_refs,
                    "conditions_differ": canonical_json(
                        left.get("context", {}).get("conditions", [])
                    )
                    != canonical_json(right.get("context", {}).get("conditions", [])),
                }
            )
    return result


def unknown_or_scope_mismatch(ref: str) -> JsonObject:
    status = "scope_mismatch" if not ref.startswith("avatar:") else "unknown"
    return {"ref": ref, "status": status}


def check_ref(connection: sqlite3.Connection, ref: str) -> JsonObject:
    if not ref.startswith("avatar:"):
        return {"ref": ref, "status": "scope_mismatch"}
    try:
        identifier, version_text = ref[len("avatar:") :].rsplit("@", 1)
        version = int(version_text)
    except (ValueError, TypeError):
        return {"ref": ref, "status": "unknown"}
    criterion = connection.execute(
        "SELECT current_version, revoked FROM criteria WHERE id = ?", (identifier,)
    ).fetchone()
    version_row = connection.execute(
        "SELECT payload_json FROM criterion_versions WHERE id = ? AND version = ?",
        (identifier, version),
    ).fetchone()
    if criterion is None or version_row is None:
        return {"ref": ref, "status": "unknown"}
    current_version = int(criterion["current_version"])
    if version != current_version:
        return {
            "ref": ref,
            "status": "superseded",
            "current": f"avatar:{identifier}@{current_version}",
        }
    if criterion["revoked"]:
        return {"ref": ref, "status": "revoked"}
    payload = json.loads(version_row["payload_json"])
    if payload["confirmation"] != "user_confirmed":
        return {"ref": ref, "status": "proposed"}
    return {"ref": ref, "status": "eligible_current"}
