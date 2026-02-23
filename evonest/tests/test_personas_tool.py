"""Tests for tools/personas.py — evonest_personas MCP tool."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evonest.tools.personas import evonest_personas


@pytest.mark.asyncio
async def test_list_personas(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="list")
    assert "## Personas" in result
    assert "## Adversarials" in result
    assert "security-auditor" in result
    assert "break-interfaces" in result


@pytest.mark.asyncio
async def test_list_filter_group(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="list", group="biz")
    assert "### biz" in result
    assert "### tech" not in result
    assert "## Adversarials" not in result  # adversarials hidden when group filter


@pytest.mark.asyncio
async def test_disable_persona(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="disable", ids=["security-auditor"])
    assert "Disabled: security-auditor" in result

    # Verify config.json was updated
    config = json.loads((tmp_project / ".evonest" / "config.json").read_text(encoding="utf-8"))
    assert config["personas"]["security-auditor"] is False


@pytest.mark.asyncio
async def test_enable_persona(tmp_project: Path) -> None:
    # First disable
    await evonest_personas(str(tmp_project), action="disable", ids=["security-auditor"])
    # Then enable
    result = await evonest_personas(str(tmp_project), action="enable", ids=["security-auditor"])
    assert "Enabled: security-auditor" in result

    config = json.loads((tmp_project / ".evonest" / "config.json").read_text(encoding="utf-8"))
    assert config["personas"]["security-auditor"] is True


@pytest.mark.asyncio
async def test_disable_adversarial(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="disable", ids=["break-interfaces"])
    assert "Disabled: break-interfaces" in result

    config = json.loads((tmp_project / ".evonest" / "config.json").read_text(encoding="utf-8"))
    assert config["adversarials"]["break-interfaces"] is False


@pytest.mark.asyncio
async def test_unknown_id_returns_error(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="disable", ids=["nonexistent-persona"])
    assert "Error: unknown IDs" in result


@pytest.mark.asyncio
async def test_missing_ids_returns_error(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="disable")
    assert "Error: ids required" in result


@pytest.mark.asyncio
async def test_unknown_action_returns_error(tmp_project: Path) -> None:
    result = await evonest_personas(str(tmp_project), action="foobar")
    assert "Error: unknown action" in result
