#!/usr/bin/env python3
"""Skill facade for the canonical scripts/migrate_stage.py CLI."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[2] / "scripts" / "migrate_stage.py"),
        run_name="__main__",
    )
