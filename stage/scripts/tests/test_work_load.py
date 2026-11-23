"""`work_load.py`: counting a card's load, the committed line, and the table over cards."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import work_load  # noqa: E402

CLI = SCRIPTS / "work_load.py"


def report(findings: list[str] | None = None) -> str:
    text = "\n### Executor report\nWhat changed: x\nWhy: y\n"
    if findings is not None:
        entries = [{"finding": f, "disposition": "accept", "reason": "r"} for f in findings]
        text += f"Review dispositions (JSON):\n{json.dumps(entries)}\n"
    return text


def failure(reason: str, role: str = "executor") -> str:
    return (
        f"\n### Driver failure\nRole: {role}\nReason: {reason}\nOutput:\n\n"
        "```text\nReason: not this one\n```\n"
    )


CARD = """---
id: {item_id}
kind: chore
venue: claude
scope: src/
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000001
promotion: not_applicable
---

# {item_id} Sample

## Verification

{verification}
"""


class CountLoadTest(unittest.TestCase):
    def test_empty_log_and_clean_card_is_one_attempt(self):
        load = work_load.count_load("", "## Verification\n")

        self.assertEqual(
            work_load.Load(
                attempts=1,
                review_fail_rounds=0,
                repeated_findings=0,
                driver_rounds=0,
                driver_failures=0,
                timeouts=0,
            ),
            load,
        )

    def test_driver_log_counts_reports_rounds_failures_and_timeouts(self):
        log = (
            "# Work log\n\n### Driver commands\nExecutor command: \"a\"\n"
            + failure("executor timed out after 900s")
            + "\n### Driver commands\nExecutor command: \"a\"\n"
            + report()
            + "\n### Reviewer report\nfails\n"
            + "\n### Driver commands\nExecutor command: \"a\"\n"
            + report(["criterion 2"])
            + failure("verification failed", role="driver")
            + report(["criterion 2", "criterion 3"])
            + report(["criterion 1"])
            + report([])
        )

        load = work_load.count_load(log, "")

        self.assertEqual(5, load.attempts)
        self.assertEqual(3, load.review_fail_rounds)
        self.assertEqual(1, load.repeated_findings)
        self.assertEqual(3, load.driver_rounds)
        self.assertEqual(2, load.driver_failures)
        self.assertEqual(1, load.timeouts)
        self.assertEqual(
            ("executor — executor timed out after 900s", "driver — verification failed"),
            load.failure_reasons,
        )

    def test_card_rejections_count_when_the_log_holds_no_answer_to_them(self):
        card = (
            "- Review at close 2026-11-22 by codex: rejected (1 PASS, 2 FAIL)\n"
            "- Review at close 2026-11-22 by codex: rejected (1 FAIL)\n"
            "Prose that quotes `- Review at close 2026-11-22 by x: rejected` is not a record.\n"
        )

        load = work_load.count_load(report(["criterion 1"]), card)

        self.assertEqual(2, load.review_fail_rounds)
        self.assertEqual(3, load.attempts)
        self.assertIsNone(load.repeated_findings)

    def test_one_round_seen_in_both_places_counts_once(self):
        card = "- Review at close 2026-11-22 by codex: rejected (1 FAIL)\n"

        load = work_load.count_load(report() + report(["criterion 1"]), card)

        self.assertEqual(1, load.review_fail_rounds)
        self.assertEqual(2, load.attempts)
        self.assertEqual(0, load.repeated_findings)

    def test_long_failure_reason_is_clipped_to_one_line(self):
        load = work_load.count_load(failure("x" * 500), "")

        self.assertEqual(work_load.MAX_REASON_CHARS, len(load.failure_reasons[0]))


class RecordLineTest(unittest.TestCase):
    def test_line_round_trips_through_the_parser(self):
        load = work_load.count_load(
            failure("executor timed out after 900s") + report(),
            "- Review at close 2026-11-22 by codex: rejected (1 FAIL)\n",
        )

        text = "## Verification\n\n" + work_load.load_record_lines(load, "2026-11-23") + "\n"
        day, parsed = work_load.parse_load_record(text)

        self.assertEqual("2026-11-23", day)
        self.assertEqual(
            work_load.Load(
                attempts=2,
                review_fail_rounds=1,
                repeated_findings=None,
                driver_rounds=0,
                driver_failures=1,
                timeouts=1,
            ),
            parsed,
        )
        self.assertIn("\n  - Driver failure: executor — executor timed out after 900s\n", text)

    def test_card_without_the_line_parses_as_none(self):
        self.assertIsNone(work_load.parse_load_record("- Checks at close 2026-11-23: 1 passed"))


class TableTest(unittest.TestCase):
    def make(self, cards: dict[str, str]) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage = root / ".stage"
        stage.mkdir()
        (stage / "settings.json").write_text('{"schema_version": 5}', encoding="utf-8")
        for location, verification in cards.items():
            card = stage / location / "_story.md"
            card.parent.mkdir(parents=True)
            card.write_text(
                CARD.format(item_id=card.parent.name, verification=verification),
                encoding="utf-8",
            )
        return tmp, root

    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), "--project-root", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_table_lists_closed_cards_from_current_and_archive_with_totals(self):
        recorded = work_load.load_record_lines(
            work_load.count_load(failure("executor timed out") + report() + report(["c"]), ""),
            "2026-11-24",
        )
        tmp, root = self.make(
            {
                "official/work/archive/items/W-00000001": (
                    "- Checks at close 2026-11-22: 1 passed — `x`\n"
                ),
                "official/work/archive/items/W-00000002": (
                    "- Review at close 2026-11-23 by codex: rejected (1 FAIL)\n"
                    "- Checks at close 2026-11-23: 1 passed — `x`\n"
                    "- Review at close 2026-11-23 by codex: approved (1 PASS)\n"
                ),
                "work/current/W-00000003": (
                    f"- Checks at close 2026-11-24: 1 passed — `x`\n{recorded}\n"
                ),
                "work/current/W-00000004": "Not closed yet.\n",
            }
        )
        with tmp:
            proc = self.run_cli(root, "--closed-since", "2026-11-23")

        self.assertEqual(0, proc.returncode, proc.stderr)
        rows = proc.stdout.strip().splitlines()
        self.assertEqual(
            [
                "| W-00000002 | 2026-11-23 | not recorded | 1 | not recorded | not recorded "
                "| not recorded | not recorded |",
                "| W-00000003 | 2026-11-24 | 2 | 1 | 0 | 0 | 1 | 1 |",
                "| Total (2 cards) |  | 2 (1) | 2 (2) | 0 (1) | 0 (1) | 1 (1) | 1 (1) |",
            ],
            rows[2:],
        )

    def test_named_cards_limit_the_table(self):
        tmp, root = self.make(
            {
                "official/work/archive/items/W-00000001": "- Checks at close 2026-11-22: 1 passed\n",
                "official/work/archive/items/W-00000002": "- Checks at close 2026-11-23: 1 passed\n",
            }
        )
        with tmp:
            proc = self.run_cli(root, "W-00000001")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("| W-00000001 |", proc.stdout)
        self.assertNotIn("| W-00000002 |", proc.stdout)

    def test_malformed_date_is_refused(self):
        tmp, root = self.make({})
        with tmp:
            proc = self.run_cli(root, "--closed-since", "yesterday")

        self.assertEqual(2, proc.returncode)
        self.assertIn("is not YYYY-MM-DD", proc.stderr)


if __name__ == "__main__":
    unittest.main()
