"""Smoke test — verify the package structure is correct."""

from __future__ import annotations

from pathlib import Path


def test_version() -> None:
    from evonest import __version__

    assert __version__ == "0.2.0"


def test_mutations_exist() -> None:
    mutations_dir = Path(__file__).parent.parent / "src" / "evonest" / "mutations"
    assert (mutations_dir / "personas.json").exists()
    assert (mutations_dir / "adversarial.json").exists()


def test_prompts_exist() -> None:
    prompts_dir = Path(__file__).parent.parent / "src" / "evonest" / "prompts"
    for name in ("observe.md", "plan.md", "execute.md", "verify.md", "meta_observe.md"):
        assert (prompts_dir / name).exists(), f"Missing prompt: {name}"


def test_templates_exist() -> None:
    templates_dir = Path(__file__).parent.parent / "src" / "evonest" / "templates"
    for name in ("config.json", "identity.md", "progress.json", "backlog.json"):
        assert (templates_dir / name).exists(), f"Missing template: {name}"
