"""Tests for doc_updater — _collect_targets, _parse_llm_output, apply_doc_changes."""

from __future__ import annotations

import json
from pathlib import Path

from evonest.core.doc_updater import (
    DocChange,
    _collect_targets,
    _parse_llm_output,
    apply_doc_changes,
    format_changes_summary,
)

# ---------------------------------------------------------------------------
# _collect_targets
# ---------------------------------------------------------------------------


def test_collect_targets_empty(tmp_path: Path) -> None:
    result = _collect_targets(tmp_path, "all")
    assert result == {}


def test_collect_targets_skills(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skills" / "mypkg"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# skill content")

    result = _collect_targets(tmp_path, "skills")
    assert "skills/mypkg/SKILL.md" in result
    assert result["skills/mypkg/SKILL.md"] == "# skill content"


def test_collect_targets_claude_commands(tmp_path: Path) -> None:
    cmd_dir = tmp_path / ".claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "deploy.md").write_text("deploy command")

    result = _collect_targets(tmp_path, "commands")
    assert ".claude/commands/deploy.md" in result


def test_collect_targets_all(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# instructions")
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "style.md").write_text("style rules")

    result = _collect_targets(tmp_path, "all")
    assert "CLAUDE.md" in result
    assert ".claude/rules/style.md" in result


def test_collect_targets_invalid_target_returns_empty(tmp_path: Path) -> None:
    # Unknown target should not crash — it maps to empty glob list
    result = _collect_targets(tmp_path, "nonexistent_category")
    assert result == {}


# ---------------------------------------------------------------------------
# _parse_llm_output
# ---------------------------------------------------------------------------


def _make_json(files: list[dict]) -> str:  # type: ignore[type-arg]
    return json.dumps({"files": files})


def test_parse_llm_output_basic() -> None:
    raw = _make_json([
        {
            "path": "skills/foo/SKILL.md",
            "action": "update",
            "current_content": "old",
            "new_content": "new",
            "reason": "param renamed",
        }
    ])
    changes = _parse_llm_output(raw)
    assert len(changes) == 1
    assert changes[0].path == "skills/foo/SKILL.md"
    assert changes[0].new_content == "new"
    assert changes[0].reason == "param renamed"


def test_parse_llm_output_strips_code_fence() -> None:
    raw = '```json\n' + _make_json([
        {"path": "CLAUDE.md", "action": "update", "new_content": "x", "reason": "r"}
    ]) + "\n```"
    changes = _parse_llm_output(raw)
    assert len(changes) == 1
    assert changes[0].path == "CLAUDE.md"


def test_parse_llm_output_strips_preamble() -> None:
    raw = "Here are the proposed changes:\n\n" + _make_json([
        {"path": "CLAUDE.md", "action": "update", "new_content": "x", "reason": "r"}
    ])
    changes = _parse_llm_output(raw)
    assert len(changes) == 1


def test_parse_llm_output_empty_files() -> None:
    changes = _parse_llm_output(json.dumps({"files": []}))
    assert changes == []


def test_parse_llm_output_invalid_json() -> None:
    changes = _parse_llm_output("not json at all")
    assert changes == []


def test_parse_llm_output_skips_malformed_entry() -> None:
    raw = _make_json([
        {"path": "ok.md", "action": "update", "new_content": "x", "reason": "r"},
        {"broken": True},  # missing required keys
    ])
    changes = _parse_llm_output(raw)
    assert len(changes) == 1
    assert changes[0].path == "ok.md"


def test_parse_llm_output_create_action() -> None:
    raw = _make_json([
        {"path": ".claude/agents/new.md", "action": "create", "new_content": "y", "reason": "new"}
    ])
    changes = _parse_llm_output(raw)
    assert changes[0].action == "create"


# ---------------------------------------------------------------------------
# apply_doc_changes
# ---------------------------------------------------------------------------


def test_apply_doc_changes_update(tmp_path: Path) -> None:
    target = tmp_path / "skills" / "foo" / "SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("old content")

    changes = [DocChange(
        path="skills/foo/SKILL.md",
        action="update",
        current_content="old content",
        new_content="new content",
        reason="test",
    )]
    applied = apply_doc_changes(tmp_path, changes)

    assert applied == ["skills/foo/SKILL.md"]
    assert target.read_text() == "new content"


def test_apply_doc_changes_create(tmp_path: Path) -> None:
    changes = [DocChange(
        path=".claude/agents/helper.md",
        action="create",
        current_content="",
        new_content="# Helper Agent",
        reason="new agent",
    )]
    applied = apply_doc_changes(tmp_path, changes)

    assert applied == [".claude/agents/helper.md"]
    assert (tmp_path / ".claude" / "agents" / "helper.md").read_text() == "# Helper Agent"


def test_apply_doc_changes_returns_empty_on_no_changes(tmp_path: Path) -> None:
    applied = apply_doc_changes(tmp_path, [])
    assert applied == []


# ---------------------------------------------------------------------------
# format_changes_summary
# ---------------------------------------------------------------------------


def test_format_changes_summary_no_changes() -> None:
    msg = format_changes_summary([])
    assert "up to date" in msg


def test_format_changes_summary_with_changes() -> None:
    changes = [
        DocChange("skills/foo/SKILL.md", "update", "", "x", "param renamed"),
        DocChange("CLAUDE.md", "update", "", "y", "test count updated"),
    ]
    msg = format_changes_summary(changes)
    assert "2 file(s)" in msg
    assert "skills/foo/SKILL.md" in msg
    assert "param renamed" in msg
