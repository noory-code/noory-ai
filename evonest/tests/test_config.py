"""Tests for core/config.py — EvonestConfig."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evonest.core.config import EvonestConfig


def test_defaults() -> None:
    config = EvonestConfig()
    assert config.model == "sonnet"
    assert config.max_cycles_per_run == 5
    assert config.dry_run is False
    assert config.adversarial_probability == 0.2
    assert config.verify.build is None
    assert config.max_turns.observe == 25


def test_load_from_project(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    assert config.model == "sonnet"
    assert config._config_path == tmp_project / ".evonest" / "config.json"


def test_load_with_overrides(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project, model="opus", dry_run=True)
    assert config.model == "opus"
    assert config.dry_run is True


def test_load_project_config(tmp_project: Path) -> None:
    cfg_path = tmp_project / ".evonest" / "config.json"
    data = json.loads(cfg_path.read_text())
    data["model"] = "haiku"
    data["verify"] = {"build": "make build", "test": "make test"}
    cfg_path.write_text(json.dumps(data))

    config = EvonestConfig.load(tmp_project)
    assert config.model == "haiku"
    assert config.verify.build == "make build"
    assert config.verify.test == "make test"


def test_override_beats_project_config(tmp_project: Path) -> None:
    cfg_path = tmp_project / ".evonest" / "config.json"
    data = json.loads(cfg_path.read_text())
    data["model"] = "haiku"
    cfg_path.write_text(json.dumps(data))

    config = EvonestConfig.load(tmp_project, model="opus")
    assert config.model == "opus"


def test_set_simple(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("model", "opus")
    assert config.model == "opus"


def test_set_coerce_types(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("max_cycles_per_run", "10")
    assert config.max_cycles_per_run == 10

    config.set("dry_run", "true")
    assert config.dry_run is True

    config.set("adversarial_probability", "0.5")
    assert config.adversarial_probability == 0.5


def test_set_dotted(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("verify.build", "npm run build")
    assert config.verify.build == "npm run build"

    config.set("max_turns.observe", "30")
    assert config.max_turns.observe == 30


def test_save_and_reload(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("model", "opus")
    config.set("verify.test", "pytest")
    config.save()

    reloaded = EvonestConfig.load(tmp_project)
    assert reloaded.model == "opus"
    assert reloaded.verify.test == "pytest"


def test_to_dict(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    d = config.to_dict()
    assert "_config_path" not in d
    assert "model" in d
    assert "verify" in d
    assert isinstance(d["verify"], dict)


def test_to_json(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    j = config.to_json()
    data = json.loads(j)
    assert data["model"] == "sonnet"


# ── observe_mode / deep_cycle_interval round-trip ────────


def test_observe_mode_defaults() -> None:
    config = EvonestConfig()
    assert config.observe_mode == "auto"
    assert config.deep_cycle_interval == 10
    assert config.observe_turns_quick_ratio == 0.10
    assert config.observe_turns_deep_ratio == 0.50
    assert config.observe_turns_min_quick == 15
    assert config.observe_turns_min_deep == 30
    assert config.max_turns.observe_deep == 100


def test_observe_mode_roundtrip(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("observe_mode", "deep")
    config.set("deep_cycle_interval", "20")
    config.set("observe_turns_quick_ratio", "0.2")
    config.set("max_turns.observe_deep", "150")
    config.save()

    reloaded = EvonestConfig.load(tmp_project)
    assert reloaded.observe_mode == "deep"
    assert reloaded.deep_cycle_interval == 20
    assert reloaded.observe_turns_quick_ratio == 0.2
    assert reloaded.max_turns.observe_deep == 150


def test_observe_mode_in_to_dict(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    d = config.to_dict()
    assert "observe_mode" in d
    assert "deep_cycle_interval" in d
    assert "observe_turns_quick_ratio" in d
    assert "max_turns" in d
    assert "observe_deep" in d["max_turns"]


def test_validate_adversarial_probability_range() -> None:
    config = EvonestConfig()
    config.adversarial_probability = 1.5
    with pytest.raises(ValueError, match="adversarial_probability"):
        config._validate()

    config.adversarial_probability = -0.1
    with pytest.raises(ValueError, match="adversarial_probability"):
        config._validate()

    config.adversarial_probability = 0.0
    config._validate()  # boundary: OK

    config.adversarial_probability = 1.0
    config._validate()  # boundary: OK


def test_validate_max_cycles_per_run() -> None:
    config = EvonestConfig()
    config.max_cycles_per_run = 0
    with pytest.raises(ValueError, match="max_cycles_per_run"):
        config._validate()

    config.max_cycles_per_run = 1
    config._validate()  # OK


def test_validate_active_level_invalid() -> None:
    config = EvonestConfig()
    config.active_level = "ultra"
    with pytest.raises(ValueError, match="active_level"):
        config._validate()


def test_validate_active_level_custom(tmp_project: Path) -> None:
    """A custom level defined in levels dict should be valid."""
    cfg_path = tmp_project / ".evonest" / "config.json"
    data = json.loads(cfg_path.read_text())
    data["levels"]["ultra"] = {"model": "opus", "observe_mode": "deep"}
    data["active_level"] = "ultra"
    cfg_path.write_text(json.dumps(data))

    config = EvonestConfig.load(tmp_project)
    assert config.active_level == "ultra"  # no ValidationError


# ── personas / adversarials toggle map ────────


def test_personas_default_empty_dict() -> None:
    config = EvonestConfig()
    assert config.personas == {}
    assert config.adversarials == {}
    assert config.disabled_persona_ids == []
    assert config.disabled_adversarial_ids == []


def test_disabled_persona_ids_property() -> None:
    config = EvonestConfig()
    config.personas = {"a": True, "b": False, "c": True}
    assert config.disabled_persona_ids == ["b"]


def test_disabled_adversarial_ids_property() -> None:
    config = EvonestConfig()
    config.adversarials = {"x": False, "y": True}
    assert config.disabled_adversarial_ids == ["x"]


def test_personas_roundtrip(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.personas["chaos-engineer"] = False
    config.adversarials["break-interfaces"] = False
    config.save()

    reloaded = EvonestConfig.load(tmp_project)
    assert reloaded.personas["chaos-engineer"] is False
    assert reloaded.adversarials["break-interfaces"] is False
    assert reloaded.personas.get("security-auditor") is True  # from template


def test_set_dotted_personas(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("personas.chaos-engineer", "false")
    assert config.personas["chaos-engineer"] is False
    config.set("personas.chaos-engineer", "true")
    assert config.personas["chaos-engineer"] is True


def test_set_dotted_adversarials(tmp_project: Path) -> None:
    config = EvonestConfig.load(tmp_project)
    config.set("adversarials.break-interfaces", "false")
    assert config.adversarials["break-interfaces"] is False


def test_legacy_disabled_personas_migration(tmp_project: Path) -> None:
    """Old config with disabled_personas is automatically migrated."""
    cfg_path = tmp_project / ".evonest" / "config.json"
    data = json.loads(cfg_path.read_text())
    # Write old format
    data.pop("personas", None)
    data.pop("adversarials", None)
    data["disabled_personas"] = ["chaos-engineer"]
    data["disabled_adversarials"] = ["break-interfaces"]
    cfg_path.write_text(json.dumps(data))

    config = EvonestConfig.load(tmp_project)
    assert config.personas.get("chaos-engineer") is False
    assert config.adversarials.get("break-interfaces") is False
    assert config.disabled_persona_ids == ["chaos-engineer"]
    assert config.disabled_adversarial_ids == ["break-interfaces"]


def test_legacy_migration_save_removes_old_keys(tmp_project: Path) -> None:
    """After migration and save, old keys are gone."""
    cfg_path = tmp_project / ".evonest" / "config.json"
    data = json.loads(cfg_path.read_text())
    data.pop("personas", None)
    data.pop("adversarials", None)
    data["disabled_personas"] = ["chaos-engineer"]
    data["disabled_adversarials"] = []
    cfg_path.write_text(json.dumps(data))

    config = EvonestConfig.load(tmp_project)
    config.save()

    saved = json.loads(cfg_path.read_text())
    assert "disabled_personas" not in saved
    assert "disabled_adversarials" not in saved
    assert "personas" in saved
    assert "adversarials" in saved
    assert saved["personas"]["chaos-engineer"] is False


# ── adversarial input tests ────────


@pytest.mark.parametrize(
    "key,value,should_fail",
    [
        ("", "value", True),
        ("model", "x" * 10000, False),
        ("verify.build", "../../../etc/passwd", False),
        ("model", "test\x00value", False),
    ],
)
def test_set_adversarial_inputs(tmp_project: Path, key: str, value: str, should_fail: bool) -> None:
    """설정 키/값에 대한 adversarial 입력 테스트."""
    config = EvonestConfig.load(tmp_project)

    if should_fail:
        with pytest.raises((ValueError, KeyError)):
            config.set(key, value)
    else:
        config.set(key, value)
        if key:
            parts = key.split(".")
            obj = config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            result = getattr(obj, parts[-1])
            assert result == value


def test_load_with_path_traversal(tmp_path: Path) -> None:
    """프로젝트 경로에 path traversal 시도 테스트."""
    malicious_path = tmp_path / ".." / ".." / ".." / "etc" / "passwd"
    with pytest.raises(FileNotFoundError):
        EvonestConfig.load(malicious_path)
