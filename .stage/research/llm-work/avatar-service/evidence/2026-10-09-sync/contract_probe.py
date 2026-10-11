"""Fictional, offline probe of a proposed Avatar sync data contract.

This is research code. It does not read Avatar data, encrypt, or use the network.
"""

from __future__ import annotations

import copy
from datetime import date
import unittest
from uuid import UUID, uuid4


ACTIONS = {
    "constraint_set": "user",
    "evidence_requested": "user",
    "correction_given": "user",
    "constraint_missed": "assistant",
    "outcome_checked": "user",
    "outcome_unknown": "user",
}


def validate(packet: object) -> list[dict[str, str]]:
    if type(packet) is not dict or set(packet) != {"schema", "events"}:
        raise ValueError("Unexpected packet fields")
    if type(packet["schema"]) is not int or packet["schema"] != 1:
        raise ValueError("Unknown schema")
    events = packet["events"]
    if type(events) is not list or len(events) > 10000:
        raise ValueError("Invalid event list")
    checked = []
    for event in events:
        if type(event) is not dict or set(event) != {
            "id", "week", "actor", "action", "status"
        }:
            raise ValueError("Unexpected event fields")
        if any(type(value) is not str for value in event.values()):
            raise ValueError("Event fields must be strings")
        try:
            identifier = UUID(event["id"])
        except ValueError as error:
            raise ValueError("Invalid event ID") from error
        if identifier.version != 4 or str(identifier) != event["id"]:
            raise ValueError("Event ID must be a canonical random UUID")
        week = event["week"]
        if len(week) != 8 or week[4:6] != "-W" or not (
            week[:4].isdigit() and week[6:].isdigit()
        ):
            raise ValueError("Invalid week")
        try:
            date.fromisocalendar(int(week[:4]), int(week[6:]), 1)
        except ValueError as error:
            raise ValueError("Invalid ISO week") from error
        if event["action"] not in ACTIONS or event["actor"] != ACTIONS[event["action"]]:
            raise ValueError("Invalid action or actor")
        expected = "unknown" if event["action"] == "outcome_unknown" else "observed"
        if event["status"] != expected:
            raise ValueError("Invalid evidence status")
        checked.append(dict(event))
    return checked


def merge(*packets: object) -> dict[str, object]:
    by_id: dict[str, dict[str, str]] = {}
    conflicts: set[str] = set()
    duplicates = 0
    for packet in packets:
        for event in validate(packet):
            identifier = event["id"]
            if identifier in conflicts:
                continue
            if identifier not in by_id:
                by_id[identifier] = event
            elif by_id[identifier] == event:
                duplicates += 1
            else:
                del by_id[identifier]
                conflicts.add(identifier)
    counts = {action: 0 for action in ACTIONS}
    for event in by_id.values():
        counts[event["action"]] += 1
    return {"counts": counts, "duplicates": duplicates, "conflicts": len(conflicts)}


def fictional_event(action: str, identifier: str | None = None) -> dict[str, str]:
    return {
        "id": identifier or str(uuid4()),
        "week": "2026-W41",
        "actor": ACTIONS[action],
        "action": action,
        "status": "unknown" if action == "outcome_unknown" else "observed",
    }


class SyncContractProbe(unittest.TestCase):
    def test_two_devices_add_distinct_observations(self) -> None:
        first = {"schema": 1, "events": [fictional_event("constraint_set")]}
        second = {"schema": 1, "events": [fictional_event("evidence_requested")]}
        result = merge(first, second)
        self.assertEqual(result["counts"]["constraint_set"], 1)
        self.assertEqual(result["counts"]["evidence_requested"], 1)

    def test_shared_id_deduplicates_only_same_observation(self) -> None:
        event = fictional_event("constraint_set")
        packet = {"schema": 1, "events": [event]}
        result = merge(packet, copy.deepcopy(packet))
        self.assertEqual(result["counts"]["constraint_set"], 1)
        self.assertEqual(result["duplicates"], 1)

    def test_conflicting_readings_are_not_counted(self) -> None:
        event = fictional_event("constraint_set")
        changed = {**event, "action": "evidence_requested"}
        result = merge({"schema": 1, "events": [event]},
                       {"schema": 1, "events": [changed]})
        self.assertEqual(result["conflicts"], 1)
        self.assertEqual(sum(result["counts"].values()), 0)

    def test_raw_text_and_extra_fields_stop_the_packet(self) -> None:
        event = fictional_event("constraint_set")
        event["raw_text"] = "FICTIONAL_CUSTOMER_SECRET"
        with self.assertRaises(ValueError):
            merge({"schema": 1, "events": [event]})

    def test_text_cannot_hide_in_an_allowed_field(self) -> None:
        event = fictional_event("constraint_set")
        event["week"] = "FICTIONAL_CUSTOMER_SECRET"
        with self.assertRaises(ValueError):
            merge({"schema": 1, "events": [event]})

    def test_new_schema_requires_a_new_decision(self) -> None:
        with self.assertRaises(ValueError):
            merge({"schema": 2, "events": []})


if __name__ == "__main__":
    unittest.main()
