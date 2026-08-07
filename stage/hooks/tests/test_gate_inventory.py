"""The gate inventory in hooks/README.md must not fall behind the hooks.

A gate is only discoverable by hitting it, so the README table is the one place
that lists them all. Nothing stops a new gate from landing without a row, and a
table that is silently one gate short is worse than none — a reader trusts it.

These tests pin the shape of the gate surface. When one fails, the change is
probably correct and the table needs the matching edit.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

HOOKS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOOKS_ROOT))

README = HOOKS_ROOT / "README.md"
GUARD = HOOKS_ROOT / "stage_guard.py"

# Raise these together with a new row in the README table. The three counts
# measure different things and are meant to disagree: 18 places in the guard can
# deny, several of them reaching one gate by two paths; 10 functions build a deny
# message (`*_blockers` helpers return reason lists and are not counted); the
# README groups the result into 14 gates a reader has to know about.
EXPECTED_DENY_SITES = 18
EXPECTED_BLOCKER_FUNCTIONS = 10
EXPECTED_DOCUMENTED_GATES = 14


def blocker_function_names() -> set[str]:
    names: set[str] = set()
    for path in sorted(HOOKS_ROOT.glob("*.py")):
        # Nested too: four of these are closures inside the function that calls
        # them, and an anchored `^def` silently misses them.
        for match in re.finditer(
            r"^\s*def (\w*blocker)\(", path.read_text(encoding="utf-8"), re.MULTILINE
        ):
            names.add(match.group(1))
    return names


class GateInventoryTest(unittest.TestCase):
    def test_deny_site_count_matches_the_documented_inventory(self):
        sites = len(re.findall(r"return deny\(", GUARD.read_text(encoding="utf-8")))
        self.assertEqual(
            EXPECTED_DENY_SITES,
            sites,
            "stage_guard.py gained or lost a deny site. Update the gate table in "
            "hooks/README.md, then set EXPECTED_DENY_SITES to the new count.",
        )

    def test_blocker_function_count_matches_the_documented_inventory(self):
        names = blocker_function_names()
        self.assertEqual(
            EXPECTED_BLOCKER_FUNCTIONS,
            len(names),
            "The set of *_blocker functions changed: "
            f"{sorted(names)}. Update the gate table in hooks/README.md, then set "
            "EXPECTED_BLOCKER_FUNCTIONS to the new count.",
        )

    def test_readme_table_names_every_gate_and_its_next_step(self):
        rows = [
            line
            for line in README.read_text(encoding="utf-8").splitlines()
            if line.startswith("| ") and line.count("|") == 5
        ]
        # One header row, one separator row, then one row per gate.
        gate_rows = [
            row
            for row in rows
            if not row.startswith("| Gate ") and not re.fullmatch(r"\|[-| ]+\|", row)
        ]
        self.assertEqual(
            EXPECTED_DOCUMENTED_GATES,
            len(gate_rows),
            "The gate table should carry one row per gate; found "
            f"{len(gate_rows)}.",
        )
        for row in gate_rows:
            clears_by = row.split("|")[4].strip()
            self.assertTrue(
                clears_by,
                f"A gate row states no way to clear it: {row}",
            )


if __name__ == "__main__":
    unittest.main()
