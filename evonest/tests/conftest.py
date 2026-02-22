"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal .evonest/ project for testing."""
    evonest_dir = tmp_path / ".evonest"
    evonest_dir.mkdir()

    # Copy templates
    templates = Path(__file__).parent.parent / "src" / "evonest" / "templates"
    for f in templates.iterdir():
        (evonest_dir / f.name).write_text(f.read_text())

    # Create subdirectories
    (evonest_dir / "history").mkdir()
    (evonest_dir / "logs").mkdir()
    (evonest_dir / "stimuli").mkdir()
    (evonest_dir / "stimuli" / ".processed").mkdir()
    (evonest_dir / "decisions").mkdir()
    (evonest_dir / "proposals").mkdir()

    # Create empty dynamic mutation files
    for name in ("dynamic-personas.json", "dynamic-adversarials.json"):
        (evonest_dir / name).write_text(json.dumps([]))

    # Create empty advisor + environment + scout cache files
    for name in ("advice.json", "environment.json", "scout.json"):
        (evonest_dir / name).write_text(json.dumps({}))

    return tmp_path
