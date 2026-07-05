"""Persistence for `.noory/rag/probes.json` — the user's evaluation probes.

Probes are intentionally kept in a separate file from `settings.json`:
- `settings.json` is a sharable indexing policy (`/rag:rag-share-guide`).
- `probes.json` is personal evaluation material that should not be pushed
  onto teammates. Both files live inside `.noory/rag/`, which is gitignored
  by default — but the SoC keeps intent explicit.

JSON schema:
    {
        "probes": [
            { "id": "<kebab>", "query": "<text>", "note": "<optional>" },
            ...
        ]
    }

Duplicate `id` is rejected at write time. `id` is non-empty; `query` is
non-empty. Probes have no domain-side dependency on Settings or any port,
so this module stays in `infrastructure/` and is used directly by the MCP
interface layer.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

from ..domain.models import Probe

_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-]*$")


class _ProbeJSON(BaseModel):
    id: str
    query: str
    note: str = ""

    @field_validator("id")
    @classmethod
    def _valid_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("probe id must be non-empty")
        if not _ID_PATTERN.match(v):
            raise ValueError(
                "probe id must match [A-Za-z0-9][A-Za-z0-9_-]* (kebab/snake-case)"
            )
        return v

    @field_validator("query")
    @classmethod
    def _valid_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("probe query must be non-empty")
        return v

    def to_domain(self) -> Probe:
        return Probe(id=self.id, query=self.query, note=self.note)


class _ProbesFile(BaseModel):
    probes: list[_ProbeJSON] = Field(default_factory=list)

    @field_validator("probes")
    @classmethod
    def _unique_ids(cls, v: list[_ProbeJSON]) -> list[_ProbeJSON]:
        seen: set[str] = set()
        for p in v:
            if p.id in seen:
                raise ValueError(f"duplicate probe id: {p.id}")
            seen.add(p.id)
        return v


class ProbesError(Exception):
    """Raised on invalid probes file / payload."""


def load(probes_file: Path) -> tuple[Probe, ...]:
    """Read probes from disk. Returns empty tuple if the file does not exist
    (i.e. user has not registered any probes yet)."""
    if not probes_file.exists():
        return ()
    try:
        raw = json.loads(probes_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ProbesError(f"invalid JSON in {probes_file}: {e}") from e
    try:
        parsed = _ProbesFile.model_validate(raw)
    except ValidationError as e:
        raise ProbesError(f"probes schema invalid: {e}") from e
    return tuple(p.to_domain() for p in parsed.probes)


def save(probes_file: Path, probes: list[Probe] | tuple[Probe, ...]) -> None:
    """Validate and persist probes. Overwrites the entire file (probes are
    edited as a whole list — the MCP `rag_set_probes` tool replaces all)."""
    payload = {
        "probes": [{"id": p.id, "query": p.query, "note": p.note} for p in probes]
    }
    try:
        _ProbesFile.model_validate(payload)
    except ValidationError as e:
        raise ProbesError(f"probes schema invalid: {e}") from e
    probes_file.parent.mkdir(parents=True, exist_ok=True)
    probes_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_payload(data: Any) -> tuple[Probe, ...]:
    """Validate a dict-shaped payload (as received from MCP) into Probes."""
    try:
        parsed = _ProbesFile.model_validate(data)
    except ValidationError as e:
        raise ProbesError(str(e)) from e
    return tuple(p.to_domain() for p in parsed.probes)
