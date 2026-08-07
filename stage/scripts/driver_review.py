#!/usr/bin/env python3
"""Read an independent reviewer's verdict, and tell a real one from a broken run.

A reviewer writes its judgement to a file. Two things can go wrong and they must
not be confused: the reviewer judged and said no, or the reviewer never got to
judge at all. Treating the second as a rejection burns an attempt on a card that
was never reviewed, so every reader here fails closed and names which of the two
it saw.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (
    STAGE_ROOT / "hooks",
    STAGE_ROOT / "scripts",
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import load_review_verdict  # noqa: E402


def load_driver_review_verdict(
    path: Path,
) -> tuple[dict[str, object] | None, str]:
    """Load a first-round verdict or a driver-merged re-review verdict."""

    verdict, error = load_review_verdict(path)
    if not error:
        return verdict, ""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None, error
    if not isinstance(raw, dict) or set(raw) != {"criteria", "approved"}:
        return None, error
    criteria = raw["criteria"]
    approved = raw["approved"]
    if not isinstance(criteria, list) or not criteria or type(approved) is not bool:
        return None, error
    if not all(
        isinstance(entry, dict) and "reviewed_in_round" in entry
        for entry in criteria
    ):
        return None, error

    normalized: list[dict[str, object]] = []
    seen_criteria: set[str] = set()
    for entry in criteria:
        if not isinstance(entry, dict) or set(entry) != {
            "criterion",
            "verdict",
            "reason",
            "reviewed_in_round",
        }:
            return None, (
                "each merged review criterion must contain exactly `criterion`, "
                "`verdict`, `reason`, and `reviewed_in_round`"
            )
        criterion = entry["criterion"]
        criterion_verdict = entry["verdict"]
        reason = entry["reason"]
        reviewed_in_round = entry["reviewed_in_round"]
        if not all(
            isinstance(value, str)
            for value in (criterion, criterion_verdict, reason)
        ):
            return None, "review criterion values must be strings"
        if (
            not criterion.strip()
            or not reason.strip()
            or "\n" in criterion
            or "\r" in criterion
            or "\n" in reason
            or "\r" in reason
        ):
            return None, (
                "review criterion and reason must be non-empty one-line strings"
            )
        if criterion in seen_criteria:
            return None, "review verdict criteria must be unique"
        if criterion_verdict not in {"PASS", "FAIL"}:
            return None, "review criterion verdict must be `PASS` or `FAIL`"
        if (
            type(reviewed_in_round) is not int
            or reviewed_in_round < 1
        ):
            return None, (
                "reviewed_in_round must be a positive integer"
            )
        seen_criteria.add(criterion)
        normalized.append(
            {
                "criterion": criterion,
                "verdict": criterion_verdict,
                "reason": reason,
                "reviewed_in_round": reviewed_in_round,
            }
        )

    all_passed = all(
        entry["verdict"] == "PASS" for entry in normalized
    )
    if approved != all_passed:
        return None, (
            "review verdict approved must be true exactly when every criterion passes"
        )
    return {"criteria": normalized, "approved": approved}, ""


def review_verdict_error(path: Path) -> str:
    """Return the driver verdict error for full or merged reviews."""

    verdict, error = load_driver_review_verdict(path)
    if error:
        return error
    if verdict is None or verdict["approved"] is not True:
        return "review verdict did not approve the work item"
    return ""


def review_verdict_failures(path: Path) -> list[str]:
    """Return failed criteria from a full or merged driver verdict."""

    verdict, error = load_driver_review_verdict(path)
    if error or verdict is None:
        return []
    criteria = verdict["criteria"]
    assert isinstance(criteria, list)
    return [
        entry["criterion"]
        for entry in criteria
        if isinstance(entry, dict) and entry.get("verdict") == "FAIL"
        and isinstance(entry.get("criterion"), str)
    ]


def merge_narrow_review_verdict(
    previous: dict[str, object],
    current: dict[str, object],
    destination: Path,
) -> str:
    """Merge reviewed criteria into the prior complete verdict with round provenance."""

    previous_criteria = previous.get("criteria")
    current_criteria = current.get("criteria")
    if not isinstance(previous_criteria, list) or not isinstance(
        current_criteria, list
    ):
        return "cannot merge review verdict without criteria arrays"

    previous_by_criterion = {
        entry["criterion"]: entry
        for entry in previous_criteria
        if isinstance(entry, dict) and isinstance(entry.get("criterion"), str)
    }
    current_by_criterion = {
        entry["criterion"]: entry
        for entry in current_criteria
        if isinstance(entry, dict) and isinstance(entry.get("criterion"), str)
    }
    unknown = [
        criterion
        for criterion in current_by_criterion
        if criterion not in previous_by_criterion
    ]
    if unknown:
        return (
            "narrow review returned criteria absent from the previous verdict: "
            + ", ".join(unknown)
        )
    missing_failures = [
        entry["criterion"]
        for entry in previous_criteria
        if isinstance(entry, dict)
        and entry.get("verdict") == "FAIL"
        and entry.get("criterion") not in current_by_criterion
    ]
    if missing_failures:
        return (
            "narrow review omitted previously failed criteria: "
            + ", ".join(missing_failures)
        )

    prior_rounds = [
        entry.get("reviewed_in_round", 1)
        for entry in previous_criteria
        if isinstance(entry, dict)
    ]
    current_round = max(
        round_number
        for round_number in prior_rounds
        if type(round_number) is int
    ) + 1
    merged: list[dict[str, object]] = []
    for previous_entry in previous_criteria:
        assert isinstance(previous_entry, dict)
        criterion = previous_entry["criterion"]
        assert isinstance(criterion, str)
        current_entry = current_by_criterion.get(criterion)
        if current_entry is None:
            merged.append(
                {
                    "criterion": criterion,
                    "verdict": previous_entry["verdict"],
                    "reason": previous_entry["reason"],
                    "reviewed_in_round": previous_entry.get(
                        "reviewed_in_round", 1
                    ),
                }
            )
            continue
        merged.append(
            {
                "criterion": criterion,
                "verdict": current_entry["verdict"],
                "reason": current_entry["reason"],
                "reviewed_in_round": current_round,
            }
        )

    payload = {
        "criteria": merged,
        "approved": all(
            entry["verdict"] == "PASS" for entry in merged
        ),
    }
    try:
        destination.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return f"cannot write merged review verdict file: {exc}"
    return ""


def retryable_review_infrastructure_failure(
    *,
    close_ok: bool,
    close_output: str,
    verdict_file: Path,
) -> bool:
    """Return whether close failed before the reviewer produced a usable result.

    A missing verdict can be the direct consequence of a transport failure. Once
    the reviewer writes a verdict file, malformed or rejecting content is a review
    result and must spend the attempt even when the prose also contains an
    infrastructure marker.
    """

    if close_ok or not infrastructure_failure(close_output):
        return False
    verdict_error = review_verdict_error(verdict_file)
    return verdict_error in {"", "review verdict file is missing"}


def infrastructure_failure(output: str) -> bool:
    """Recognize a command transport/tool failure that must not spend a work round."""

    lowered = output.lower()
    return any(
        marker in lowered
        for marker in (
            "timed out",
            "command not found",
            "[exit 126]",
            "[exit 127]",
            "terminated by signal",
            "killed by signal",
        )
    )
