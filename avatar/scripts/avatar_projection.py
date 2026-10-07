"""Validate and compare the recorded history of each external criterion."""
from __future__ import annotations

import json
import re
import sqlite3

from avatar_common import AvatarError, JsonObject, VERSION_DIGEST_FIELDS, digest


def criterion_id(payload: JsonObject) -> str:
    return payload["versions"][0]["ref"].split(":", 1)[1].split("@", 1)[0]


def validate(payload: JsonObject) -> None:
    if payload.get("producer") != "distill" or payload.get("schema") != "criteria-history/1":
        raise AvatarError("E_SOURCE_INVALID", "Only Distill criteria-history/1 input is accepted.")
    generation = payload.get("generation")
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 0:
        raise AvatarError("E_SOURCE_INVALID", "generation must be a non-negative integer.")
    versions, events = payload.get("versions"), payload.get("events")
    if not isinstance(versions, list) or not versions or not isinstance(events, list):
        raise AvatarError("E_SOURCE_INVALID", "A history needs versions and an event list.")
    refs = set()
    identifiers = set()
    for version in versions:
        ref = version.get("ref") if isinstance(version, dict) else None
        match = re.fullmatch(r"distill:(CR-[0-9a-f]{12})@([1-9][0-9]*)", ref) if isinstance(ref, str) else None
        if match is None or ref in refs:
            raise AvatarError("E_SOURCE_INVALID", "Version refs must be valid and unique.")
        refs.add(ref)
        identifiers.add(match.group(1))
        if not isinstance(version.get("statement"), str) or not version["statement"].strip():
            raise AvatarError("E_SOURCE_INVALID", "Each version needs a statement.")
        origin = version.get("origin")
        if not isinstance(origin, dict) or not isinstance(origin.get("quote"), str):
            raise AvatarError("E_SOURCE_INVALID", "Each version needs source evidence.")
    if len(identifiers) != 1 or payload.get("id", criterion_id(payload)) != criterion_id(payload):
        raise AvatarError("E_SOURCE_INVALID", "A history must describe exactly one criterion.")
    for event in events:
        if (not isinstance(event, dict) or not isinstance(event.get("ref"), str)
                or event["ref"] not in refs):
            raise AvatarError("E_SOURCE_INVALID", "Events must reference a version in this history.")


def version_digests(payload: JsonObject) -> dict[str, str]:
    return {
        version["ref"]: digest({field: version.get(field) for field in VERSION_DIGEST_FIELDS})
        for version in payload["versions"]
    }


def same_criterion_rows(connection: sqlite3.Connection, payload: JsonObject) -> list:
    rows = connection.execute(
        "SELECT generation, payload_json, envelope_digest FROM projections "
        "WHERE producer = ? ORDER BY generation DESC", (payload["producer"],)
    )
    return [row for row in rows if criterion_id(json.loads(row["payload_json"])) == criterion_id(payload)]


def has_newer(connection: sqlite3.Connection, payload: JsonObject) -> bool:
    return any(int(row["generation"]) > payload["generation"]
               for row in same_criterion_rows(connection, payload))


def validate_history(connection: sqlite3.Connection, payload: JsonObject, envelope: str) -> None:
    for row in same_criterion_rows(connection, payload):
        previous = json.loads(row["payload_json"])
        if payload.get("project") != previous.get("project"):
            raise AvatarError("E_PROJECTION_CONFLICT", "A criterion changed its project.")
        if payload["generation"] == row["generation"]:
            if row["envelope_digest"] != envelope:
                raise AvatarError("E_PROJECTION_CONFLICT", "One criterion generation has two histories.")
            continue
        older, newer = (previous, payload) if payload["generation"] > row["generation"] else (payload, previous)
        if newer["events"][:len(older["events"])] != older["events"]:
            raise AvatarError("E_PROJECTION_CONFLICT", "The histories disagree about earlier events.")
        older_refs = set(version_digests(older))
        if not older_refs.issubset(version_digests(newer)):
            raise AvatarError("E_PROJECTION_CONFLICT", "The newer history removed an earlier version.")
