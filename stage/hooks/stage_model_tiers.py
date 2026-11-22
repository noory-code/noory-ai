"""Model and effort tiers: the one reader of `model_tiers`, `tier_routing`,
`model_fallbacks`, and `usage_limit_patterns`.

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

`model_fallbacks` and `usage_limit_patterns` say what the driver does when a
venue's model stops on a usage limit (`load_fallback_config`):

    "model_fallbacks": {"agy": [["claude-sonnet-5-5-high", "gpt-oss"],
                                ["gemini-4-argon-medium"]]},
    "usage_limit_patterns": {"agy": ["RESOURCE_EXHAUSTED", "code 429"]}

Each venue lists groups of models in preference order; one group shares one
usage limit. Both keys stand without `model_tiers`.
"""

# The hook must run wherever `python3` points on a host machine (3.9+).
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import read_settings  # noqa: E402

MODEL_TIERS_KEY = "model_tiers"
TIER_ROUTING_KEY = "tier_routing"
MODEL_FALLBACKS_KEY = "model_fallbacks"
USAGE_LIMIT_PATTERNS_KEY = "usage_limit_patterns"
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


@dataclass(frozen=True)
class FallbackConfig:
    """Parsed `model_fallbacks` and `usage_limit_patterns`.

    `groups[venue]` holds that venue's model groups in preference order, each a
    tuple of models sharing one usage limit. `patterns[venue]` holds compiled
    usage-limit patterns. A malformed setting leaves both empty and says why in
    `errors`: readers that must not fail (the driver) then never fall back, and
    the audit reports the errors.
    """

    groups: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    patterns: dict[str, tuple[re.Pattern[str], ...]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def declares(self, venue: str) -> bool:
        """Whether either setting names `venue`."""

        key = venue.strip().lower()
        return key in self.groups or key in self.patterns

    def usage_limit_match(self, venue: str, output: str) -> str:
        """The first `venue` pattern found in `output`, or "" when none matches."""

        for pattern in self.patterns.get(venue.strip().lower(), ()):
            if pattern.search(output):
                return pattern.pattern
        return ""

    def next_model(self, venue: str, limited: Sequence[str]) -> str:
        """First model of the first `venue` group none of whose models hit a limit.

        `limited` lists the models that already stopped on a usage limit this
        turn; a group holding any of them is spent, because its models share the
        limit. A model outside every group (the tier's model, or "" for the
        command's own default) spends no group. "" means every group is spent.
        """

        spent = {model_alias(model) for model in limited if model_alias(model)}
        for group in self.groups.get(venue.strip().lower(), ()):
            if not any(model_alias(model) in spent for model in group):
                return group[0]
        return ""


def _venue_key(raw: Any, setting: str, errors: list[str]) -> str:
    key = raw.strip().lower() if isinstance(raw, str) else ""
    if not key or key == WILDCARD:
        errors.append(f"`{setting}` has an invalid venue name {raw!r}")
        return ""
    return key


def _parse_fallbacks(raw: Any, errors: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        errors.append(f"`{MODEL_FALLBACKS_KEY}` must be an object of venue names")
        return {}
    parsed: dict[str, tuple[tuple[str, ...], ...]] = {}
    for venue_name, groups in raw.items():
        venue = _venue_key(venue_name, MODEL_FALLBACKS_KEY, errors)
        if not venue:
            continue
        where = f"`{MODEL_FALLBACKS_KEY}.{venue_name}`"
        if not isinstance(groups, list) or not groups:
            errors.append(f"{where} must be a non-empty list of model groups")
            continue
        seen: set[str] = set()
        venue_groups: list[tuple[str, ...]] = []
        for index, group in enumerate(groups):
            if (
                not isinstance(group, list)
                or not group
                or any(not isinstance(model, str) or not model.strip() for model in group)
            ):
                errors.append(
                    f"{where}[{index}] must be a non-empty list of non-empty model strings"
                )
                venue_groups = []
                break
            models = tuple(model.strip() for model in group)
            repeated = sorted(model for model in models if model_alias(model) in seen)
            if repeated or len({model_alias(model) for model in models}) != len(models):
                errors.append(f"{where} names a model in more than one place: {list(models)}")
                venue_groups = []
                break
            seen.update(model_alias(model) for model in models)
            venue_groups.append(models)
        if venue_groups:
            parsed[venue] = tuple(venue_groups)
    return parsed


def _parse_patterns(raw: Any, errors: list[str]) -> dict[str, tuple[re.Pattern[str], ...]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        errors.append(f"`{USAGE_LIMIT_PATTERNS_KEY}` must be an object of venue names")
        return {}
    parsed: dict[str, tuple[re.Pattern[str], ...]] = {}
    for venue_name, patterns in raw.items():
        venue = _venue_key(venue_name, USAGE_LIMIT_PATTERNS_KEY, errors)
        if not venue:
            continue
        where = f"`{USAGE_LIMIT_PATTERNS_KEY}.{venue_name}`"
        if (
            not isinstance(patterns, list)
            or not patterns
            or any(not isinstance(pattern, str) or not pattern.strip() for pattern in patterns)
        ):
            errors.append(f"{where} must be a non-empty list of non-empty regular expressions")
            continue
        compiled: list[re.Pattern[str]] = []
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern))
            except re.error as exc:
                errors.append(f"{where} has an invalid regular expression {pattern!r}: {exc}")
                compiled = []
                break
        if compiled:
            parsed[venue] = tuple(compiled)
    return parsed


def parse_fallback_config(settings: Any) -> FallbackConfig:
    """Parse fallback settings from an already-loaded settings object."""

    if not isinstance(settings, dict):
        return FallbackConfig()
    errors: list[str] = []
    groups = _parse_fallbacks(settings.get(MODEL_FALLBACKS_KEY), errors)
    patterns = _parse_patterns(settings.get(USAGE_LIMIT_PATTERNS_KEY), errors)
    if errors:
        return FallbackConfig(errors=errors)
    return FallbackConfig(groups=groups, patterns=patterns)


def load_fallback_config(stage_root: Path) -> FallbackConfig:
    """Read fallback settings; unreadable settings carry nothing and no errors."""

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return FallbackConfig()
    return parse_fallback_config(data)
