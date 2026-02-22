"""EvonestConfig — 3-tier configuration resolution.

Resolution order:
1. Engine defaults (this dataclass)
2. Project config (.evonest/config.json)
3. Runtime overrides (MCP tool args / CLI flags)
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _strip_jsonc_comments(text: str) -> str:
    """Remove // line comments from a JSON string (JSONC support)."""
    return re.sub(r"(?m)\s*//[^\n]*", "", text)


@dataclass
class VerifyConfig:
    build: str | None = None
    test: str | None = None


@dataclass
class MaxTurnsConfig:
    observe: int = 25
    observe_deep: int = 100
    plan: int = 15
    execute: int = 25
    meta: int = 10
    scout: int = 15


@dataclass
class LevelConfig:
    """Per-level preset: model + observe depth + max turns."""

    model: str = "sonnet"
    observe_mode: str = "auto"
    max_turns: MaxTurnsConfig = field(default_factory=MaxTurnsConfig)


def _default_levels() -> dict[str, LevelConfig]:
    return {
        "quick": LevelConfig(
            model="haiku",
            observe_mode="quick",
            max_turns=MaxTurnsConfig(observe=15, observe_deep=40, plan=10, execute=20, meta=8, scout=10),
        ),
        "standard": LevelConfig(
            model="sonnet",
            observe_mode="auto",
            max_turns=MaxTurnsConfig(observe=25, observe_deep=100, plan=15, execute=25, meta=10, scout=15),
        ),
        "deep": LevelConfig(
            model="opus",
            observe_mode="deep",
            max_turns=MaxTurnsConfig(observe=50, observe_deep=150, plan=20, execute=35, meta=15, scout=20),
        ),
    }


@dataclass
class EvonestConfig:
    """Evolution engine configuration with 3-tier resolution."""

    model: str = "sonnet"
    max_cycles_per_run: int = 5
    dry_run: bool = False
    meta_cycle_interval: int = 5
    max_dynamic_personas: int = 5
    max_dynamic_adversarials: int = 3
    dynamic_mutation_ttl_cycles: int = 15
    adversarial_probability: float = 0.2
    # "commit" (default) = direct commit; "pr" = branch + pull request
    code_output: str = "commit"
    # Scout: external search-based mutation generation
    scout_enabled: bool = True
    scout_cycle_interval: int = 10
    scout_min_relevance_score: int = 6
    # Persona group filter: empty = all groups, ["biz"] = biz only, etc.
    active_groups: list[str] = field(default_factory=list)
    # Per-ID toggle map: {persona_id: true/false}. Missing ID = enabled.
    # Forced persona_id / adversarial_id overrides these maps.
    personas: dict[str, bool] = field(default_factory=dict)
    adversarials: dict[str, bool] = field(default_factory=dict)
    # Observe mode: quick (sampled) vs deep (comprehensive)
    observe_mode: str = "auto"  # "auto" | "quick" | "deep"
    deep_cycle_interval: int = 10
    observe_turns_quick_ratio: float = 0.10
    observe_turns_deep_ratio: float = 0.50
    observe_turns_min_quick: int = 15
    observe_turns_min_deep: int = 30
    verify: VerifyConfig = field(default_factory=VerifyConfig)
    max_turns: MaxTurnsConfig = field(default_factory=MaxTurnsConfig)
    # Language for generated files (proposals, identity, advice). e.g. "korean", "english"
    language: str = "english"

    # Analysis depth level: "quick" | "standard" | "deep"
    # Applies model + observe_mode + max_turns preset from levels dict.
    active_level: str = "standard"
    # Per-level presets (model, observe_mode, max_turns)
    levels: dict[str, LevelConfig] = field(default_factory=_default_levels)

    # Internal: path to the config file for saving
    _config_path: Path | None = field(default=None, repr=False)

    @property
    def disabled_persona_ids(self) -> list[str]:
        """Return IDs explicitly set to false in the personas toggle map."""
        return [pid for pid, enabled in self.personas.items() if not enabled]

    @property
    def disabled_adversarial_ids(self) -> list[str]:
        """Return IDs explicitly set to false in the adversarials toggle map."""
        return [aid for aid, enabled in self.adversarials.items() if not enabled]

    @classmethod
    def load(cls, project: str | Path, **overrides: object) -> EvonestConfig:
        """Load config with 3-tier resolution."""
        from evonest.core.state import ProjectState

        state = ProjectState(project)
        config = cls()
        config._config_path = state.config_path

        # Tier 2: project config (JSONC supported — // comments are stripped)
        project_data: dict[str, object] = {}
        if state.config_path.exists():
            raw = state.config_path.read_text(encoding="utf-8")
            project_data = json.loads(_strip_jsonc_comments(raw))
            # Apply levels dict first so _apply_level uses customized presets
            if "levels" in project_data:
                config._apply_dict({"levels": project_data["levels"]})
            # Resolve active_level from project config (before applying preset)
            if "active_level" in project_data:
                config.active_level = str(project_data["active_level"])

        # Apply active_level preset as baseline (model, observe_mode, max_turns)
        config._apply_level(config.active_level)

        # Now apply full project config — explicit values override the preset
        if project_data:
            config._apply_dict(project_data)

        # Tier 3: runtime overrides (highest priority)
        if overrides:
            config._apply_dict(dict(overrides))

        config._validate()
        return config

    def _validate(self) -> None:
        """Validate config field ranges. Raises ValueError on invalid values."""
        if not 0.0 <= self.adversarial_probability <= 1.0:
            raise ValueError(
                f"adversarial_probability must be between 0.0 and 1.0, "
                f"got {self.adversarial_probability}"
            )
        if self.max_cycles_per_run < 1:
            raise ValueError(
                f"max_cycles_per_run must be >= 1, got {self.max_cycles_per_run}"
            )
        valid_levels = set(self.levels.keys()) | {"quick", "standard", "deep"}
        if self.active_level not in valid_levels:
            raise ValueError(
                f"active_level must be one of {sorted(valid_levels)}, "
                f"got '{self.active_level}'"
            )

    def _apply_level(self, level: str) -> None:
        """Apply a level preset (quick/standard/deep) to model/observe_mode/max_turns.

        Only applies if the level exists in self.levels. Runtime overrides
        applied after this call will take priority.
        """
        if level not in self.levels:
            return
        preset = self.levels[level]
        self.model = preset.model
        self.observe_mode = preset.observe_mode
        self.max_turns = MaxTurnsConfig(
            observe=preset.max_turns.observe,
            observe_deep=preset.max_turns.observe_deep,
            plan=preset.max_turns.plan,
            execute=preset.max_turns.execute,
            meta=preset.max_turns.meta,
            scout=preset.max_turns.scout,
        )

    def _migrate_legacy_toggles(self, data: dict[str, object]) -> None:
        """Convert legacy disabled_personas/disabled_adversarials to toggle maps.

        Mutates *data* in place: removes legacy keys and injects new format
        if the new keys are not already present.
        """
        if "disabled_personas" in data and "personas" not in data:
            old = data.pop("disabled_personas")
            if isinstance(old, list):
                merged = dict(self.personas)
                for pid in old:
                    merged[pid] = False
                data["personas"] = merged
        else:
            data.pop("disabled_personas", None)

        if "disabled_adversarials" in data and "adversarials" not in data:
            old = data.pop("disabled_adversarials")
            if isinstance(old, list):
                merged = dict(self.adversarials)
                for aid in old:
                    merged[aid] = False
                data["adversarials"] = merged
        else:
            data.pop("disabled_adversarials", None)

    def _apply_dict(self, data: dict[str, object]) -> None:
        """Apply a dictionary of settings to this config."""
        data = dict(data)  # shallow copy to avoid mutating caller's dict
        self._migrate_legacy_toggles(data)

        for key, value in data.items():
            if key.startswith("_"):
                continue
            if key == "verify" and isinstance(value, dict):
                self.verify = VerifyConfig(
                    build=value.get("build", self.verify.build),
                    test=value.get("test", self.verify.test),
                )
            elif key == "personas" and isinstance(value, dict):
                self.personas.update(value)
            elif key == "adversarials" and isinstance(value, dict):
                self.adversarials.update(value)
            elif key == "active_groups" and isinstance(value, list):
                self.active_groups = value
            elif key == "max_turns" and isinstance(value, dict):
                self.max_turns = MaxTurnsConfig(
                    observe=value.get("observe", self.max_turns.observe),
                    observe_deep=value.get("observe_deep", self.max_turns.observe_deep),
                    plan=value.get("plan", self.max_turns.plan),
                    execute=value.get("execute", self.max_turns.execute),
                    meta=value.get("meta", self.max_turns.meta),
                    scout=value.get("scout", self.max_turns.scout),
                )
            elif key == "levels" and isinstance(value, dict):
                for lvl_name, lvl_data in value.items():
                    if not isinstance(lvl_data, dict):
                        continue
                    existing = self.levels.get(lvl_name, LevelConfig())
                    mt_data = lvl_data.get("max_turns", {})
                    if isinstance(mt_data, dict):
                        turns = MaxTurnsConfig(
                            observe=mt_data.get("observe", existing.max_turns.observe),
                            observe_deep=mt_data.get("observe_deep", existing.max_turns.observe_deep),
                            plan=mt_data.get("plan", existing.max_turns.plan),
                            execute=mt_data.get("execute", existing.max_turns.execute),
                            meta=mt_data.get("meta", existing.max_turns.meta),
                            scout=mt_data.get("scout", existing.max_turns.scout),
                        )
                    else:
                        turns = existing.max_turns
                    self.levels[lvl_name] = LevelConfig(
                        model=lvl_data.get("model", existing.model),
                        observe_mode=lvl_data.get("observe_mode", existing.observe_mode),
                        max_turns=turns,
                    )
            elif hasattr(self, key):
                setattr(self, key, value)

    def set(self, key: str, value: object) -> None:
        """Set a single config value. Supports dot notation for nested keys.

        Raises ValueError if the key does not exist.
        """
        if "." in key:
            parts = key.split(".", 1)
            # Handle toggle maps: personas.<id> and adversarials.<id>
            if parts[0] in ("personas", "adversarials"):
                toggle_map: dict[str, bool] = getattr(self, parts[0])
                if isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes")
                toggle_map[parts[1]] = bool(value)
                return
            parent = getattr(self, parts[0], None)
            if parent is not None and hasattr(parent, parts[1]):
                current = getattr(parent, parts[1])
                if isinstance(current, int) and isinstance(value, str):
                    value = int(value)
                elif isinstance(current, float) and isinstance(value, str):
                    value = float(value)
                setattr(parent, parts[1], value)
                return
            raise ValueError(f"Unknown config key: {key}")
        if hasattr(self, key) and not key.startswith("_"):
            current = getattr(self, key)
            if isinstance(current, bool) and isinstance(value, str):
                value = value.lower() in ("true", "1", "yes")
            elif isinstance(current, int) and isinstance(value, str):
                value = int(value)
            elif isinstance(current, float) and isinstance(value, str):
                value = float(value)
            setattr(self, key, value)
        else:
            raise ValueError(f"Unknown config key: {key}")

    def save(self) -> None:
        """Write config back to .evonest/config.json."""
        if self._config_path is None:
            raise RuntimeError("Config path not set — load from a project first")
        data = self.to_dict()
        self._config_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dict (excluding internal fields)."""
        d = asdict(self)
        d.pop("_config_path", None)
        return d

    def to_json(self) -> str:
        """Return pretty-printed JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
