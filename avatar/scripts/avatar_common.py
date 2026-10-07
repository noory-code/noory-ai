from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


JsonObject = dict[str, Any]
VERSION_DIGEST_FIELDS = (
    "statement",
    "applies_when",
    "exceptions",
    "notes",
    "overrides",
    "confirmation",
    "ai_confidence",
    "origin",
    "reason",
    "supersedes",
    "recorded_at",
)


class AvatarError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def complete_origin(origin: object) -> object:
    if not isinstance(origin, dict):
        return origin
    return {
        **origin,
        "quote_sha256": hashlib.sha256(origin["quote"].encode("utf-8")).hexdigest(),
        "source_sha256": origin.get("source_sha256"),
        "captured_at": origin.get("captured_at") or now(),
    }
