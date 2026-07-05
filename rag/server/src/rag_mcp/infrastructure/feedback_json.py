"""Persistence for `.noory/rag/feedback.json` — user feedback on search results.

Feedback is the signal that lets the index self-improve: a good/bad verdict on
a search result, recorded against the (query, rel_path) that produced it. Kept
separate from `settings.json` — personal, gitignored by default, never shared
(like `probes.json`).

JSON schema:
    {"feedback": [{"query": str, "rel_path": str,
                   "verdict": "good"|"bad", "ts": str}]}

``aggregate_boosts`` reduces the log to a per-``rel_path`` net score
(good=+1, bad=-1) that the searcher uses to re-rank. The key is ``rel_path``
(NOT the volatile chunk id) so boosts survive re-indexing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

VERDICTS = ("good", "bad")


class _FeedbackEntry(BaseModel):
    query: str
    rel_path: str
    verdict: str
    ts: str = ""

    @field_validator("query", "rel_path")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must be non-empty")
        return v

    @field_validator("verdict")
    @classmethod
    def _valid_verdict(cls, v: str) -> str:
        if v not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}")
        return v


class _FeedbackFile(BaseModel):
    feedback: list[_FeedbackEntry] = Field(default_factory=list)


class FeedbackError(Exception):
    """Raised on invalid feedback file / payload."""


def load(feedback_file: Path) -> list[dict[str, Any]]:
    """Read feedback records. Empty list if the file does not exist yet."""
    if not feedback_file.exists():
        return []
    try:
        raw = json.loads(feedback_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise FeedbackError(f"invalid JSON in {feedback_file}: {e}") from e
    try:
        parsed = _FeedbackFile.model_validate(raw)
    except ValidationError as e:
        raise FeedbackError(f"feedback schema invalid: {e}") from e
    return [e.model_dump() for e in parsed.feedback]


def append(
    feedback_file: Path, query: str, rel_path: str, verdict: str, ts: str = ""
) -> dict[str, Any]:
    """Validate and append one feedback record; returns the stored entry."""
    try:
        entry = _FeedbackEntry(query=query, rel_path=rel_path, verdict=verdict, ts=ts)
    except ValidationError as e:
        raise FeedbackError(str(e)) from e
    records = load(feedback_file)
    records.append(entry.model_dump())
    feedback_file.parent.mkdir(parents=True, exist_ok=True)
    feedback_file.write_text(
        json.dumps({"feedback": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return entry.model_dump()


def aggregate_boosts(records: list[dict[str, Any]]) -> dict[str, float]:
    """Net verdict per rel_path: good=+1, bad=-1."""
    boosts: dict[str, float] = {}
    for r in records:
        delta = 1.0 if r.get("verdict") == "good" else -1.0
        boosts[r["rel_path"]] = boosts.get(r["rel_path"], 0.0) + delta
    return boosts
