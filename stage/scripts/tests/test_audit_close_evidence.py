"""WORK030 and REVIEW003: the evidence a close leaves, and the commands that produce it."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

STAGE = Path(__file__).resolve().parents[2]
SCRIPTS = STAGE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import audit_close_evidence  # noqa: E402

AUDIT = SCRIPTS / "audit_stage.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"
FINDING = re.compile(r"^(ERROR|WARNING) ((?:WORK030|REVIEW003)) \[([^\]]*)\]: (.*)$", re.MULTILINE)
LOAD = (
    "- Load at close {day}: attempts 1, review FAIL rounds 0, repeated findings 0, "
    "driver rounds 0, driver failures 0 (timed out 0)\n"
)
CARD = """---
id: {item_id}
title: Sample
kind: chore
venue: claude
scope: src/
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-{number:08d}
promotion: not_applicable
review: not_required
---

# {item_id} Sample

## Purpose

Something.

## Success criteria

- It works

## Verification

{verification}
"""
METHOD_PROMPT = (
    "python3 review.py \"Write criteria with the keys criterion, verdict, method, and reason; "
    "method is ran, read, or unable.\""
)
OLD_PROMPT = "python3 review.py \"Read the card and write criteria with criterion, verdict, reason.\""


class LoadLineUnitTest(unittest.TestCase):
    def findings(self, cards: dict[str, str]) -> list[tuple[str, str]]:
        found: list[tuple[str, str]] = []
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, text in cards.items():
                path = Path(tmp) / f"{name}.md"
                path.write_text(text, encoding="utf-8")
                paths.append(path)
            audit_close_evidence.audit_load_lines(
                paths, lambda code, message, path: found.append((code, Path(path).stem))
            )
        return found

    def test_a_card_closed_after_the_projects_first_load_line_is_reported(self):
        found = self.findings(
            {
                "old": "- Checks at close 2026-11-20: 1 passed — `x`\n",
                "first": "- Checks at close 2026-11-23: 1 passed\n" + LOAD.format(day="2026-11-23"),
                "same-day": "- Checks at close 2026-11-23: 1 passed — `x`\n",
                "later": "- Checks at close 2026-11-25: 1 passed — `x`\n",
                "later-with": "- Checks at close 2026-11-26: 1 passed\n"
                + LOAD.format(day="2026-11-26"),
                "open": "Not closed.\n",
            }
        )

        self.assertEqual([("WORK030", "later")], found)

    def test_a_project_that_never_wrote_the_line_gets_no_finding(self):
        found = self.findings(
            {f"card{n}": f"- Checks at close 2026-11-{n:02d}: 1 passed\n" for n in range(1, 30)}
        )

        self.assertEqual([], found)

    def test_a_reopened_card_is_judged_by_its_last_close(self):
        found = self.findings(
            {
                "first": "- Checks at close 2026-11-23: 1 passed\n" + LOAD.format(day="2026-11-23"),
                "twice": "- Checks at close 2026-11-01: 1 passed\n"
                "- Checks at close 2026-12-01: 1 passed\n",
            }
        )

        self.assertEqual([("WORK030", "twice")], found)


class ReviewMethodUnitTest(unittest.TestCase):
    def test_a_command_says_method_only_with_the_key_and_its_three_values(self):
        self.assertTrue(audit_close_evidence.says_method(METHOD_PROMPT))
        self.assertFalse(audit_close_evidence.says_method(OLD_PROMPT))
        self.assertFalse(
            audit_close_evidence.says_method("judge by a sound method; read the files")
        )
        # `ran` inside another word is not the value.
        self.assertFalse(
            audit_close_evidence.says_method("method: read, unable, or a warranty check")
        )

    def test_reviewers_and_strengths_are_read_and_empty_levels_are_skipped(self):
        review = {
            "reviewers": {"codex": OLD_PROMPT, "claude": METHOD_PROMPT},
            "strengths": {"off": None, "light": "", "standard": OLD_PROMPT, "deep": METHOD_PROMPT},
            "stages": {"implementation": "standard"},
        }
        found: list[tuple[str, str]] = []

        audit_close_evidence.audit_review_methods(
            review, Path("settings.json"), lambda code, message, path: found.append((code, message))
        )

        self.assertEqual(["REVIEW003", "REVIEW003"], [code for code, _message in found])
        self.assertTrue(found[0][1].startswith("review.reviewers.codex does not tell"))
        self.assertTrue(found[1][1].startswith("review.strengths.standard does not tell"))
        # The values are matched as written in a verdict: `Read the card` is not `read`.
        self.assertIn("missing the word(s) `method`, `ran`, `read`, `unable`)", found[0][1])

    def test_a_malformed_review_block_is_left_to_the_other_review_codes(self):
        for review in (None, [], {"strengths": "x", "reviewers": 3}):
            found: list[str] = []
            audit_close_evidence.audit_review_methods(
                review, Path("settings.json"), lambda code, message, path: found.append(code)
            )
            self.assertEqual([], found)


class AuditCommandTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, self.stage)
        (self.stage / "settings.jsonc").unlink()
        self.write_settings({"schema_version": 5})

    def write_settings(self, settings: dict) -> None:
        (self.stage / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

    def write_card(self, number: int, verification: str) -> None:
        item_id = f"W-{number:08d}"
        folder = self.stage / "work" / "current" / item_id
        folder.mkdir(parents=True)
        (folder / "_story.md").write_text(
            CARD.format(item_id=item_id, number=number, verification=verification),
            encoding="utf-8",
        )

    def findings(self) -> list[tuple[str, str, str, str]]:
        proc = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(self.root)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return FINDING.findall(proc.stdout)

    def test_the_audit_names_the_card_closed_without_a_load_line(self):
        self.write_card(1, "- Checks at close 2026-11-23: 1 passed\n" + LOAD.format(day="2026-11-23"))
        self.write_card(2, "- Checks at close 2026-11-24: 1 passed — `x`\n")
        self.write_card(3, "- Checks at close 2026-11-22: 1 passed — `x`\n")

        found = self.findings()

        self.assertEqual(
            [("WARNING", "WORK030", ".stage/work/current/W-00000002/_story.md")],
            [(level, code, path) for level, code, path, _message in found],
        )
        self.assertIn("Closed on 2026-11-24 with no `- Load at close` line", found[0][3])
        self.assertIn("since 2026-11-23", found[0][3])

    def test_the_audit_names_the_review_command_that_does_not_say_method(self):
        self.write_settings(
            {
                "schema_version": 5,
                "review": {
                    "reviewers": {"codex": METHOD_PROMPT},
                    "strengths": {"off": None, "standard": OLD_PROMPT},
                    "stages": {"implementation": "standard"},
                },
            }
        )

        found = self.findings()

        self.assertEqual(
            [("WARNING", "REVIEW003", ".stage/settings.json")],
            [(level, code, path) for level, code, path, _message in found],
        )
        self.assertIn("review.strengths.standard", found[0][3])

    def test_settings_whose_commands_say_method_and_no_closed_cards_report_nothing(self):
        self.write_settings(
            {
                "schema_version": 5,
                "review": {
                    "strengths": {"standard": METHOD_PROMPT},
                    "stages": {"implementation": "standard"},
                },
            }
        )

        self.assertEqual([], self.findings())


if __name__ == "__main__":
    unittest.main()
