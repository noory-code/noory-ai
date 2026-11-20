"""run_review.py runs a reviewer, records its output, and needs no shell syntax."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "scripts" / "run_review.py"
CLOSE_WORK = PLUGIN_ROOT / "skills" / "stage-retrospective" / "close_work.py"
KOREAN = "한국어 판정"

# Records what the reviewer received, prints UTF-8 text, and exits with the given status.
REVIEWER = (
    "import json, os, sys\n"
    "sys.stdout.reconfigure(encoding='utf-8')\n"
    "sys.stderr.reconfigure(encoding='utf-8')\n"
    "seen = {'argv': sys.argv[2:], 'model': os.environ.get('REVIEW_MODEL')}\n"
    "open(os.environ['SEEN_FILE'], 'w', encoding='utf-8').write(json.dumps(seen))\n"
    f"print('{KOREAN} stdout')\n"
    "print('stderr line', file=sys.stderr)\n"
    "sys.exit(int(sys.argv[1]))\n"
)


def load(path: Path, name: str):
    # close_work imports its neighbours by bare name.
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_review = load(SCRIPT, "run_review_under_test")


class ExpandStageVariablesTest(unittest.TestCase):
    def test_set_variables_expand_in_both_spellings(self):
        environ = {"STAGE_WORK_ITEM_PATH": "C:\\work dir\\카드.md", "STAGE_X_1": "one"}

        text = run_review.expand_stage_variables(
            "Read $STAGE_WORK_ITEM_PATH, then ${STAGE_X_1}.", environ
        )

        self.assertEqual("Read C:\\work dir\\카드.md, then one.", text)

    def test_an_unset_stage_variable_expands_to_nothing_like_a_posix_shell(self):
        self.assertEqual(
            "If  is set", run_review.expand_stage_variables("If $STAGE_PREVIOUS is set", {})
        )

    def test_other_dollar_text_is_left_alone(self):
        text = "costs $5, $HOME, $stage_lower, and STAGE_PLAIN"

        self.assertEqual(text, run_review.expand_stage_variables(text, {"HOME": "/home/x"}))


class ReviewerCommandTest(unittest.TestCase):
    def test_python_names_run_with_this_interpreter(self):
        for name in ("python3", "python"):
            with self.subTest(name=name):
                self.assertEqual(
                    [sys.executable, "x.py"], run_review.reviewer_command([name, "x.py"], {})
                )

    def test_another_executable_is_kept(self):
        self.assertEqual(["node", "x.mjs"], run_review.reviewer_command(["node", "x.mjs"], {}))

    def test_an_empty_command_is_refused(self):
        with self.assertRaises(ValueError):
            run_review.reviewer_command([], {})

    def test_env_assignments_need_a_name_and_an_equals_sign(self):
        self.assertEqual({"A": "b=c", "E": ""}, run_review.parse_assignments(["A=b=c", "E="]))
        for bad in ("novalue", "=value"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                run_review.parse_assignments([bad])


class RunReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "프로젝트 dir"
        self.root.mkdir()
        self.reviewer = self.root / "reviewer.py"
        self.reviewer.write_text(REVIEWER, encoding="utf-8")
        self.log = self.root / "log.md"
        self.log.write_bytes(b"# Log\n")
        self.seen = self.root / "seen.json"
        self.card = self.root / "card.md"

    def environment(self, **extra: str) -> dict[str, str]:
        env = {
            **os.environ,
            "SEEN_FILE": str(self.seen),
            "STAGE_WORK_LOG_PATH": str(self.log),
            "STAGE_WORK_ITEM_PATH": str(self.card),
        }
        env.pop("STAGE_PREVIOUS_REVIEW_VERDICT_FILE", None)
        env.update(extra)
        return env

    def run_script(self, *arguments: str, env: dict[str, str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=str(self.root),
        )

    def test_output_goes_to_the_log_and_stdout_and_the_status_is_the_reviewers(self):
        result = self.run_script(
            "--label", "probe", "--env", "REVIEW_MODEL=opus[1m]", "--",
            "python3", str(self.reviewer), "3", "Read $STAGE_WORK_ITEM_PATH now",
            env=self.environment(),
        )  # fmt: skip

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"{KOREAN} stdout", result.stdout)
        self.assertIn("stderr line", result.stdout)
        log = self.log.read_text(encoding="utf-8")
        self.assertTrue(log.startswith("# Log\n\n### Reviewer report\n"), log)
        self.assertIn(f"{KOREAN} stdout", log)
        self.assertIn("stderr line", log)
        seen = json.loads(self.seen.read_text(encoding="utf-8"))
        self.assertEqual([f"Read {self.card} now"], seen["argv"])
        self.assertEqual("opus[1m]", seen["model"])

    def test_a_missing_work_log_variable_blocks_before_the_reviewer_runs(self):
        env = self.environment()
        del env["STAGE_WORK_LOG_PATH"]

        result = self.run_script("--", "python3", str(self.reviewer), "0", env=env)

        self.assertEqual(1, result.returncode)
        self.assertIn("BLOCK: STAGE_WORK_LOG_PATH is not set", result.stdout)
        self.assertFalse(self.seen.exists())

    def test_a_log_that_cannot_be_written_blocks_even_when_the_reviewer_passed(self):
        env = self.environment(STAGE_WORK_LOG_PATH=str(self.root / "missing" / "log.md"))

        result = self.run_script(
            "--label", "probe", "--", "python3", str(self.reviewer), "0", env=env
        )  # fmt: skip

        self.assertEqual(1, result.returncode)
        self.assertIn("BLOCK: cannot append probe review to work log", result.stdout)

    def test_a_reviewer_that_cannot_start_is_recorded_and_fails(self):
        result = self.run_script("--", "no-such-reviewer-binary", env=self.environment())

        self.assertEqual(127, result.returncode)
        self.assertIn("cannot run no-such-reviewer-binary", self.log.read_text(encoding="utf-8"))

    def test_a_command_string_in_the_settings_shape_runs_in_the_platform_shell(self):
        # close_work hands a configured command to the platform shell: `sh` on macOS
        # and Linux, `cmd.exe` on Windows. The same string has to work in both.
        close_work = load(CLOSE_WORK, "close_work_for_run_review")
        command = (
            f'"{sys.executable}" "{SCRIPT}" --label probe --env "REVIEW_MODEL=opus[1m]" -- '
            f'python3 "{self.reviewer}" 0 '
            '"Read $STAGE_WORK_ITEM_PATH; if $STAGE_PREVIOUS_REVIEW_VERDICT_FILE is set, read it."'
        )

        ok, evidence, raw = close_work.run_check(
            command, timeout=120, cwd=self.root, env=self.environment()
        )

        self.assertTrue(ok, evidence)
        self.assertIn(f"{KOREAN} stdout", raw)
        seen = json.loads(self.seen.read_text(encoding="utf-8"))
        self.assertEqual([f"Read {self.card}; if  is set, read it."], seen["argv"])
        self.assertEqual("opus[1m]", seen["model"])
        self.assertIn("### Reviewer report", self.log.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
