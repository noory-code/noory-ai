"""Module-size guard (D-2026-06-10-D) — the monorepo 500-line rule, enforced.

`folder_io.py` grew to 1413 lines (3x the rule) as the storage god-module.
The split turns it into a facade over focused modules; this test keeps every
engine module under the rule and pins the facade to staying thin, so the god
module cannot quietly re-grow.
"""

from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parent.parent / "plot_mcp"

# The monorepo SoC rule: review/split at 500 lines.
CEILING = 500
# The facade only re-exports; it must stay an index, not a home for logic.
# 180 covers the isort one-import-per-block style for ~45 names + docstring.
FACADE_CEILING = 180


def _loc(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


# Pre-existing god modules, grandfathered at their 2026-06-10 size — a
# RATCHET: they may shrink, never grow. Splitting them is tracked debt
# (plot/docs/ROADMAP.md Track 1.4). Remove an entry once its module is split.
GRANDFATHERED: dict[str, int] = {
    "models.py": 993,
    "api_endpoints.py": 965,
    "migrate.py": 916,
}


def test_no_engine_module_exceeds_the_500_line_rule() -> None:
    offenders = {
        p.name: _loc(p)
        for p in PKG.glob("*.py")
        if _loc(p) > GRANDFATHERED.get(p.name, CEILING)
    }
    assert offenders == {}, f"modules over their ceiling (500 or ratchet): {offenders}"


def test_grandfathered_entries_are_still_needed() -> None:
    """When a debt module drops under 500, its ratchet entry must go."""
    stale = {n: _loc(PKG / n) for n in GRANDFATHERED if _loc(PKG / n) <= CEILING}
    assert stale == {}, f"split done — remove from GRANDFATHERED: {stale}"


def test_folder_io_is_a_thin_facade() -> None:
    assert _loc(PKG / "folder_io.py") <= FACADE_CEILING
