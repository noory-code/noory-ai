"""Model and effort tiers: the one reader of `model_tiers` and `tier_routing`.

A project names tiers in `.stage/settings.json` and gives each tier the model and
effort every venue understands, written in that venue's own vocabulary:

    "model_tiers": {
      "scout":    {"claude": {"model": "haiku",  "effort": "low"}},
      "standard": {"claude": {"model": "sonnet", "effort": "medium"}}
    },
    "tier_routing": {"*": "standard", "chore": "scout",
                     "development": {"action": "standard", "*": "standard"}}

Declaration order is cost order: the first tier is the cheapest. Registration,
the driver, the Agent-call hook, and the audit read tiers only through this
module, so they always agree on what a tier means and which one costs more.
A project without `model_tiers` gets no tier anywhere.
"""

# The hook must run wherever `python3` points on a host machine (3.9+).
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import read_settings  # noqa: E402

MODEL_TIERS_KEY = "model_tiers"
TIER_ROUTING_KEY = "tier_routing"
TIER_FIELD = "tier"
VENUE_TIER_KEYS = ("model", "effort")
WILDCARD = "*"
_MODEL_SUFFIX_RE = re.compile(r"\[[^\]]*\]$")


@dataclass(frozen=True)
class VenueTier:
    """One venue's values for one tier; an omitted value is the empty string."""

    model: str = ""
    effort: str = ""


@dataclass(frozen=True)
class TierConfig:
    """Parsed tier settings.

    `tiers` is None when the project declares no `model_tiers` or declares a
    malformed table; `errors` says which. Readers that must not fail (hooks,
    the driver) treat None as "no tier"; registration and the audit report the
    errors.
    """

    tiers: dict[str, dict[str, VenueTier]] | None = None
    routing: dict[str, str | dict[str, str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def rank(self, tier: str) -> int | None:
        """Position of `tier` in cost order, or None when it is not declared."""

        if self.tiers is None:
            return None
        names = list(self.tiers)
        name = tier.strip().lower()
        return names.index(name) if name in names else None

    def values(self, tier: str, venue: str) -> VenueTier | None:
        """The venue's values for `tier`, or None when either is not declared."""

        if self.tiers is None:
            return None
        return self.tiers.get(tier.strip().lower(), {}).get(venue.strip().lower())

    def route(self, kind: str, scale: str) -> str:
        """Tier routed for a work kind and scale, or "" when none applies."""

        if self.tiers is None:
            return ""
        entry = self.routing.get(kind.strip().lower())
        if isinstance(entry, str):
            return entry
        if isinstance(entry, dict):
            chosen = entry.get(scale.strip().lower()) or entry.get(WILDCARD)
            if chosen:
                return chosen
        top = self.routing.get(WILDCARD)
        return top if isinstance(top, str) else ""

    def model_rank(self, venue: str, model: str) -> int | None:
        """Rank of the cheapest tier whose `venue` model is `model`, or None."""

        if self.tiers is None:
            return None
        for index, venues in enumerate(self.tiers.values()):
            values = venues.get(venue.strip().lower())
            if values is not None and values.model and model_matches(values.model, model):
                return index
        return None


def model_alias(model: str) -> str:
    """A model value without a trailing bracket qualifier such as `[1m]`."""

    return _MODEL_SUFFIX_RE.sub("", model.strip()).strip().lower()


def model_matches(declared: str, actual: str) -> bool:
    """Whether an actual model id (or alias) is the declared tier model.

    `claude-haiku-5-5` matches `haiku`; `opus` matches `opus[1m]`. Both sides
    lose a trailing bracket qualifier, then the declared alias must occur in the
    actual id.
    """

    alias = model_alias(declared)
    observed = model_alias(actual)
    return bool(alias) and bool(observed) and alias in observed


def _parse_tiers(raw: Any, errors: list[str]) -> dict[str, dict[str, VenueTier]] | None:
    if not isinstance(raw, dict) or not raw:
        errors.append(f"`{MODEL_TIERS_KEY}` must be a non-empty object of tier names")
        return None
    tiers: dict[str, dict[str, VenueTier]] = {}
    for tier_name, venues in raw.items():
        name = tier_name.strip().lower() if isinstance(tier_name, str) else ""
        if not name or name == WILDCARD:
            errors.append(f"`{MODEL_TIERS_KEY}` has an invalid tier name {tier_name!r}")
            continue
        if not isinstance(venues, dict) or not venues:
            errors.append(
                f"`{MODEL_TIERS_KEY}.{name}` must be a non-empty object of venue names"
            )
            continue
        parsed: dict[str, VenueTier] = {}
        for venue_name, values in venues.items():
            venue = venue_name.strip().lower() if isinstance(venue_name, str) else ""
            where = f"`{MODEL_TIERS_KEY}.{name}.{venue_name}`"
            if not venue or not isinstance(values, dict) or not values:
                errors.append(f"{where} must be an object with `model` and/or `effort`")
                continue
            unknown = sorted(str(key) for key in values if key not in VENUE_TIER_KEYS)
            if unknown:
                errors.append(f"{where} has unknown keys {unknown}; allowed: model, effort")
                continue
            if any(not isinstance(value, str) or not value.strip() for value in values.values()):
                errors.append(f"{where} values must be non-empty strings")
                continue
            parsed[venue] = VenueTier(
                model=str(values.get("model", "")).strip(),
                effort=str(values.get("effort", "")).strip(),
            )
        tiers[name] = parsed
    return tiers


def _parse_routing(
    raw: Any, tier_names: set[str], errors: list[str]
) -> dict[str, str | dict[str, str]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        errors.append(f"`{TIER_ROUTING_KEY}` must be an object of work kinds")
        return {}

    def tier_value(value: Any, where: str) -> str:
        name = value.strip().lower() if isinstance(value, str) else ""
        if name not in tier_names:
            errors.append(
                f"{where} names tier {value!r}, which `{MODEL_TIERS_KEY}` does not declare "
                f"(declared: {sorted(tier_names)})"
            )
            return ""
        return name

    routing: dict[str, str | dict[str, str]] = {}
    for kind, entry in raw.items():
        key = kind.strip().lower() if isinstance(kind, str) else ""
        where = f"`{TIER_ROUTING_KEY}.{kind}`"
        if not key:
            errors.append(f"`{TIER_ROUTING_KEY}` has an invalid kind {kind!r}")
            continue
        if isinstance(entry, dict):
            if key == WILDCARD:
                errors.append(f"{where} must name one tier")
                continue
            scales: dict[str, str] = {}
            for scale, value in entry.items():
                scale_key = scale.strip().lower() if isinstance(scale, str) else ""
                name = tier_value(value, f"`{TIER_ROUTING_KEY}.{kind}.{scale}`")
                if scale_key and name:
                    scales[scale_key] = name
            routing[key] = scales
        elif isinstance(entry, str):
            name = tier_value(entry, where)
            if name:
                routing[key] = name
        else:
            errors.append(f"{where} must name a tier or map scales to tiers")
    return routing


def parse_tier_config(settings: Any) -> TierConfig:
    """Parse tier settings from an already-loaded settings object."""

    if not isinstance(settings, dict):
        return TierConfig()
    has_tiers = MODEL_TIERS_KEY in settings
    has_routing = TIER_ROUTING_KEY in settings
    if not has_tiers:
        if has_routing:
            return TierConfig(
                errors=[f"`{TIER_ROUTING_KEY}` needs `{MODEL_TIERS_KEY}` to name its tiers"]
            )
        return TierConfig()
    errors: list[str] = []
    tiers = _parse_tiers(settings.get(MODEL_TIERS_KEY), errors)
    routing = _parse_routing(
        settings.get(TIER_ROUTING_KEY), set(tiers or {}), errors
    )
    if errors:
        return TierConfig(errors=errors)
    return TierConfig(tiers=tiers, routing=routing)


def load_tier_config(stage_root: Path) -> TierConfig:
    """Read tier settings; unreadable settings carry no tiers and no errors."""

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return TierConfig()
    return parse_tier_config(data)


def registration_tier(stage_root: Path, kind: str, scale: str) -> str:
    """The tier a new card of `kind` and `scale` records, or "" for none."""

    return load_tier_config(stage_root).route(kind, scale)
