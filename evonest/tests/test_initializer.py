"""Tests for core/initializer.py — init_project."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from evonest.core.initializer import (
    _clean_identity_draft,
    _draft_identity_via_claude,
    init_project,
)


@pytest.fixture(autouse=True)
def _mock_claude_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip actual claude -p call during init tests."""
    monkeypatch.setattr(
        "evonest.core.initializer._draft_identity_via_claude",
        lambda project: None,
    )


def test_init_creates_structure(tmp_path: Path) -> None:
    result = init_project(tmp_path)
    assert "Initialized" in result

    evonest_dir = tmp_path / ".evonest"
    assert evonest_dir.is_dir()
    assert (evonest_dir / "history").is_dir()
    assert (evonest_dir / "logs").is_dir()
    assert (evonest_dir / "stimuli").is_dir()
    assert (evonest_dir / "stimuli" / ".processed").is_dir()
    assert (evonest_dir / "decisions").is_dir()


def test_init_creates_templates(tmp_path: Path) -> None:
    init_project(tmp_path)
    evonest_dir = tmp_path / ".evonest"

    assert (evonest_dir / "config.json").exists()
    assert (evonest_dir / "identity.md").exists()
    assert (evonest_dir / "progress.json").exists()
    assert (evonest_dir / "backlog.json").exists()

    # Verify JSON is valid and has expected structure
    config = json.loads((evonest_dir / "config.json").read_text())
    assert config["active_level"] == "standard"
    assert "levels" in config
    assert config["levels"]["standard"]["model"] == "sonnet"

    progress = json.loads((evonest_dir / "progress.json").read_text())
    assert progress["total_cycles"] == 0


def test_init_creates_dynamic_mutations(tmp_path: Path) -> None:
    init_project(tmp_path)
    evonest_dir = tmp_path / ".evonest"

    personas = json.loads((evonest_dir / "dynamic-personas.json").read_text())
    assert personas == []

    adversarials = json.loads((evonest_dir / "dynamic-adversarials.json").read_text())
    assert adversarials == []


def test_init_creates_advice_and_environment(tmp_path: Path) -> None:
    init_project(tmp_path)
    evonest_dir = tmp_path / ".evonest"

    advice = json.loads((evonest_dir / "advice.json").read_text())
    assert advice == {}

    environment = json.loads((evonest_dir / "environment.json").read_text())
    assert environment == {}


def test_init_creates_gitignore(tmp_path: Path) -> None:
    init_project(tmp_path)
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert ".evonest/" in gitignore.read_text()


def test_init_appends_to_existing_gitignore(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules/\n")

    init_project(tmp_path)
    content = gitignore.read_text()
    assert "node_modules/" in content
    assert ".evonest/" in content


def test_init_skips_gitignore_if_already_present(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("# Evonest\n.evonest/\n")

    init_project(tmp_path)
    content = gitignore.read_text()
    assert content.count(".evonest") == 1


def test_init_idempotent(tmp_path: Path) -> None:
    init_project(tmp_path)
    # Modify identity
    (tmp_path / ".evonest" / "identity.md").write_text("# My Project")

    # Re-init should not overwrite existing files
    init_project(tmp_path)
    assert (tmp_path / ".evonest" / "identity.md").read_text() == "# My Project"


def test_init_missing_directory() -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        init_project("/nonexistent/path/12345")


def test_init_returns_next_steps(tmp_path: Path) -> None:
    result = init_project(tmp_path)
    assert "Next steps" in result
    assert "identity.md" in result
    assert "config.json" in result


def test_init_uses_claude_draft_when_available(tmp_path: Path) -> None:
    """init_project uses Claude-generated draft for identity.md when claude succeeds."""
    draft_content = "# My Project\n\n## Mission\nDo great things.\n"
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.output = draft_content

    with patch("evonest.core.initializer._draft_identity_via_claude", return_value=draft_content):
        init_project(tmp_path)

    identity = (tmp_path / ".evonest" / "identity.md").read_text()
    assert identity == draft_content


def test_init_falls_back_to_template_when_claude_fails(tmp_path: Path) -> None:
    """init_project falls back to blank template when Claude draft returns None."""
    with patch("evonest.core.initializer._draft_identity_via_claude", return_value=None):
        init_project(tmp_path)

    identity = (tmp_path / ".evonest" / "identity.md").read_text()
    # Blank template has the placeholder sections
    assert "## Mission" in identity
    assert "## Boundaries" in identity


def test_draft_identity_returns_none_on_failure(tmp_path: Path) -> None:
    """_draft_identity_via_claude returns None when claude_runner fails."""
    mock_result = MagicMock()
    mock_result.success = False
    mock_result.output = ""

    with patch("evonest.core.claude_runner.run", return_value=mock_result):
        result = _draft_identity_via_claude(tmp_path)

    assert result is None


# ── _clean_identity_draft tests ──────────────────────────


def test_clean_strips_preamble_and_code_fence() -> None:
    raw = (
        "Perfect. I have all the information needed. "
        "Here's the identity.md draft:\n"
        "```markdown\n"
        "# Project Identity\n\n## Mission\nDo stuff.\n"
        "```"
    )
    result = _clean_identity_draft(raw)
    assert result.startswith("# Project Identity")
    assert "Perfect" not in result
    assert "```" not in result


def test_clean_strips_preamble_without_fence() -> None:
    raw = "Sure! Here is the identity:\n\n# Project Identity\n\n## Mission\nBuild things."
    result = _clean_identity_draft(raw)
    assert result.startswith("# Project Identity")
    assert "Sure" not in result


def test_clean_preserves_clean_output() -> None:
    raw = "# Project Identity\n\n## Mission\nAlready clean."
    result = _clean_identity_draft(raw)
    assert result == raw


def test_clean_handles_plain_code_fence() -> None:
    raw = "```\n# Project Identity\n\n## Mission\nPlain fence.\n```"
    result = _clean_identity_draft(raw)
    assert result.startswith("# Project Identity")
    assert "```" not in result


def test_clean_handles_md_fence_tag() -> None:
    raw = "```md\n# Project Identity\n\n## Mission\nMd fence.\n```"
    result = _clean_identity_draft(raw)
    assert result.startswith("# Project Identity")
    assert "```" not in result
