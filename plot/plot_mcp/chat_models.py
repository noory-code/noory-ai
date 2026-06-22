"""Per-provider chat model catalogue (D-2026-06-22-B).

Populates the in-app chat model selector from each CLI's own live catalogue
instead of a hardcoded list (reverses D-2026-06-16-C for codex, which went
stale immediately as vendors shipped new models):

  * codex  → ``~/.codex/models_cache.json`` (every ``visibility == "list"`` +
    ``supported_in_api`` model; codex keeps it fresh). Each model is expanded
    into one combined entry per ``supported_reasoning_levels`` (D-2026-06-22-C):
    ``id`` is ``"<slug>:<effort>"``, ``label`` is ``"<display> (<Effort>)"``;
    ``CodexProvider`` splits the id back into ``--model`` + a
    ``-c model_reasoning_effort=`` override. A model with no levels stays bare.
  * claude → the CLI's own documented aliases (still static — claude publishes
    stable aliases, D-2026-06-16-C).

(gemini → ``agy models`` temporarily removed 2026-06-23, re-add in October.)

Fail-soft: any source error (cache missing / unreadable) yields an empty list
so the selector falls back to its Custom… free-text entry.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from plot_mcp.mcp_registration import ProviderName


class ModelOption(BaseModel):
    """One selectable chat model. ``id`` is passed to the CLI as ``--model``;
    ``label`` is what the selector shows."""

    id: str
    label: str


# claude publishes stable aliases, so this stays static (D-2026-06-16-C).
CLAUDE_MODELS: list[ModelOption] = [
    ModelOption(id="fable", label="fable"),
    ModelOption(id="opus", label="opus"),
    ModelOption(id="sonnet", label="sonnet"),
]

_DEFAULT_CODEX_CACHE = Path.home() / ".codex" / "models_cache.json"

# Pretty labels for codex reasoning levels (D-2026-06-22-C); fall back to a
# plain capitalize for any level the cache adds later.
_EFFORT_LABEL = {"low": "Low", "medium": "Medium", "high": "High", "xhigh": "xHigh"}


def _codex_reasoning_efforts(entry: dict[str, Any]) -> list[str]:
    """The effort levels a codex model supports, in cache order."""
    levels = entry.get("supported_reasoning_levels")
    if not isinstance(levels, list):
        return []
    out: list[str] = []
    for level in levels:
        if isinstance(level, dict):
            effort = level.get("effort")
            if isinstance(effort, str) and effort:
                out.append(effort)
    return out


def parse_codex_models(cache: dict[str, Any]) -> list[ModelOption]:
    """Listed, API-supported models from a codex ``models_cache.json`` dict.

    Hidden / non-API / malformed entries are skipped — a bad cache yields
    fewer options, never an error.
    """
    out: list[ModelOption] = []
    models = cache.get("models")
    if not isinstance(models, list):
        return out
    for entry in models:
        if not isinstance(entry, dict):
            continue
        slug = entry.get("slug")
        if not isinstance(slug, str) or not slug:
            continue
        if entry.get("visibility") != "list":
            continue
        if not entry.get("supported_in_api"):
            continue
        display = entry.get("display_name")
        label = display if isinstance(display, str) and display else slug
        efforts = _codex_reasoning_efforts(entry)
        if efforts:
            # One combined entry per level (D-2026-06-22-C). id "<slug>:<effort>"
            # is split back by CodexProvider into --model + reasoning-effort.
            for effort in efforts:
                pretty = _EFFORT_LABEL.get(effort, effort.capitalize())
                out.append(ModelOption(id=f"{slug}:{effort}", label=f"{label} ({pretty})"))
        else:
            out.append(ModelOption(id=slug, label=label))
    return out


def list_models(
    provider: ProviderName,
    *,
    codex_cache_path: Path | None = None,
) -> list[ModelOption]:
    """The model catalogue for one provider (fail-soft → ``[]`` on any error)."""
    if provider == "claude-code":
        return list(CLAUDE_MODELS)
    if provider == "codex":
        path = codex_cache_path if codex_cache_path is not None else _DEFAULT_CODEX_CACHE
        try:
            cache = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(cache, dict):
            return []
        return parse_codex_models(cache)
    return []
