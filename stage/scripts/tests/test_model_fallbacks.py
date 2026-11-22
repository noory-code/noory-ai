"""Tests for `model_fallbacks` / `usage_limit_patterns` (docs/SCHEMA_V5.md → Model fallbacks)."""

from __future__ import annotations

import io
import json
import contextlib
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
STAGE_ROOT = SCRIPTS_DIR.parent
for import_dir in (
    STAGE_ROOT / "hooks",
    SCRIPTS_DIR,
    Path(__file__).resolve().parent,
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

import driver_model_fallback  # noqa: E402
import stage_model_tiers  # noqa: E402
import test_drive_unattended as unattended_fixture  # noqa: E402
from python_shell_command import python_command  # noqa: E402
from test_drive import (  # noqa: E402
    PASS_COMMAND,
    approving_reviewer_command,
    initialize_git,
    reporting_python_command,
)
from test_driver_model_tier import make_project, run_drive  # noqa: E402

AGY_LIMIT = (
    "RESOURCE_EXHAUSTED (code 429): Individual quota reached for claude-sonnet-5-5-high. "
    "Resets in 69h26m36s"
)
FALLBACKS = {"codex": [["m1", "m1-mini"], ["m2"], ["m3"]]}
PATTERNS = {"codex": ["RESOURCE_EXHAUSTED", r"code 429"]}


# `python_command` encodes its code, so a test command names $STAGE_MODEL in a trailing
# comment (POSIX shell) or an ignored argument (cmd.exe) to let the driver switch model.
READS_MODEL = " # $STAGE_MODEL"


def limited_unless(allowed: str, then: str) -> str:
    """Python code that stops on the agy limit unless STAGE_MODEL is `allowed`."""

    return (
        "import os, sys\n"
        f"if os.environ.get('STAGE_MODEL') != {allowed!r}:\n"
        f"    print({AGY_LIMIT!r}); sys.exit(1)\n"
        f"{then}\n"
    )


def add_settings(stage_root: Path, **values: object) -> None:
    path = stage_root / "settings.json"
    settings = json.loads(path.read_text(encoding="utf-8"))
    settings.update(values)
    path.write_text(json.dumps(settings), encoding="utf-8")


class FallbackConfigTest(unittest.TestCase):
    def test_absent_settings_declare_nothing(self):
        config = stage_model_tiers.parse_fallback_config({"schema_version": 5})
        self.assertEqual([], config.errors)
        self.assertFalse(config.declares("codex"))
        self.assertEqual("", config.next_model("codex", ["m1"]))

    def test_next_model_skips_every_group_that_shares_a_limited_model(self):
        config = stage_model_tiers.parse_fallback_config(
            {"model_fallbacks": FALLBACKS, "usage_limit_patterns": PATTERNS}
        )
        self.assertEqual([], config.errors)
        # The tier's model is in no group: the list starts from its first group.
        self.assertEqual("m1", config.next_model("codex", ["tier-model"]))
        self.assertEqual("m1", config.next_model("CODEX", [""]))
        # m1-mini shares m1's limit, so the whole first group is spent.
        self.assertEqual("m2", config.next_model("codex", ["m1-mini"]))
        self.assertEqual("m1", config.next_model("codex", ["m3"]))
        self.assertEqual("", config.next_model("codex", ["m1", "m2", "m3"]))

    def test_usage_limit_match_names_the_pattern(self):
        config = stage_model_tiers.parse_fallback_config({"usage_limit_patterns": PATTERNS})
        self.assertEqual("RESOURCE_EXHAUSTED", config.usage_limit_match("codex", AGY_LIMIT))
        self.assertEqual("", config.usage_limit_match("codex", "tests failed"))
        self.assertEqual("", config.usage_limit_match("claude", AGY_LIMIT))

    def test_malformed_settings_are_inert_and_say_why(self):
        for settings in (
            {"model_fallbacks": ["m1"]},
            {"model_fallbacks": {"codex": []}},
            {"model_fallbacks": {"codex": ["m1"]}},
            {"model_fallbacks": {"codex": [[]]}},
            {"model_fallbacks": {"codex": [["m1", 3]]}},
            {"model_fallbacks": {"codex": [["m1"], ["M1"]]}},
            {"model_fallbacks": {"*": [["m1"]]}},
            {"usage_limit_patterns": {"codex": "RESOURCE_EXHAUSTED"}},
            {"usage_limit_patterns": {"codex": ["("]}},
            {"usage_limit_patterns": {"codex": [""]}},
        ):
            with self.subTest(settings=settings):
                config = stage_model_tiers.parse_fallback_config(settings)
                self.assertTrue(config.errors)
                self.assertFalse(config.declares("codex"))


class RunWithFallbacksTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.stage_root = Path(tmp.name) / ".stage"
        self.stage_root.mkdir()
        self.log = Path(tmp.name) / "log.md"
        self.log.write_text("# log\n", encoding="utf-8")
        self.write({"model_fallbacks": FALLBACKS, "usage_limit_patterns": PATTERNS})

    def write(self, settings: dict) -> None:
        (self.stage_root / "settings.json").write_text(
            json.dumps({"schema_version": 5, **settings}), encoding="utf-8"
        )

    def run_turn(self, allowed: set[str], command: str = 'tool --model "$STAGE_MODEL"'):
        seen: list[str] = []

        def run(env: dict[str, str]) -> tuple[bool, str, str]:
            model = env.get("STAGE_MODEL", "")
            seen.append(model)
            if model in allowed:
                return True, "done", "done"
            return False, AGY_LIMIT, AGY_LIMIT

        retries: list[str] = []
        with contextlib.redirect_stdout(io.StringIO()):
            result = driver_model_fallback.run_with_model_fallbacks(
                run,
                stage_root=self.stage_root,
                venue="codex",
                role="executor",
                command=command,
                env={"STAGE_MODEL": "tier-model"},
                log_path=self.log,
                before_retry=lambda: retries.append("x"),
            )
        return result, seen, retries, self.log.read_text(encoding="utf-8")

    def test_a_usage_limit_reruns_on_the_next_group_and_logs_each_model(self):
        result, seen, retries, log = self.run_turn({"m2"})

        self.assertTrue(result.ok)
        self.assertFalse(result.exhausted)
        self.assertEqual(["tier-model", "m1", "m2"], seen)
        self.assertEqual(2, len(retries))
        self.assertEqual(3, log.count("Model run: executor on codex with model"))
        self.assertIn('Model run: executor on codex with model "m2"', log)
        self.assertEqual(2, log.count("hit a usage limit"))
        self.assertIn('rerunning with "m1"; the rerun is not an attempt', log)
        self.assertIn('(matched "RESOURCE_EXHAUSTED")', log)

    def test_every_group_spent_reports_exhaustion(self):
        result, seen, _retries, log = self.run_turn(set())

        self.assertFalse(result.ok)
        self.assertTrue(result.exhausted)
        self.assertEqual(["tier-model", "m1", "m2", "m3"], seen)
        self.assertTrue(driver_model_fallback.usage_limits_exhausted(result.evidence))
        self.assertIn("every model group in model_fallbacks is spent", log)

    def test_a_command_without_stage_model_cannot_fall_back(self):
        result, seen, _retries, log = self.run_turn({"m1"}, command="tool --model fixed")

        self.assertTrue(result.exhausted)
        self.assertEqual(["tier-model"], seen)
        self.assertIn("does not read $STAGE_MODEL", log)

    def test_patterns_without_fallbacks_stop_on_the_first_limit(self):
        self.write({"usage_limit_patterns": PATTERNS})
        result, seen, _retries, _log = self.run_turn(set())

        self.assertTrue(result.exhausted)
        self.assertEqual(["tier-model"], seen)

    def test_an_ordinary_failure_is_not_a_usage_limit(self):
        def run(_env):
            return False, "tests failed", "tests failed"

        result = driver_model_fallback.run_with_model_fallbacks(
            run,
            stage_root=self.stage_root,
            venue="codex",
            role="executor",
            command='tool --model "$STAGE_MODEL"',
            env={},
            log_path=self.log,
        )
        self.assertFalse(result.ok)
        self.assertFalse(result.exhausted)
        self.assertEqual(1, self.log.read_text(encoding="utf-8").count("Model run:"))

    def test_an_undeclared_venue_runs_once_and_logs_nothing(self):
        self.write({})
        result, seen, _retries, log = self.run_turn(set())

        self.assertFalse(result.ok)
        self.assertFalse(result.exhausted)
        self.assertEqual(["tier-model"], seen)
        self.assertEqual("# log\n", log)


class SupervisedFallbackTest(unittest.TestCase):
    def project(self, root: Path, executor: str, reviewer: str) -> Path:
        stage_root = make_project(root, executor=executor, reviewer=reviewer, tiers=None)
        add_settings(
            stage_root,
            model_fallbacks={**FALLBACKS, "claude": [["r1"], ["r2"]]},
            usage_limit_patterns={**PATTERNS, "claude": ["RESOURCE_EXHAUSTED"]},
        )
        initialize_git(root)
        return stage_root

    def test_executor_and_reviewer_move_to_the_next_model_without_spending_attempts(self):
        executor = reporting_python_command(
            "exec(" + repr(limited_unless("m2", "pass")) + "); "
            "from pathlib import Path; "
            "Path('executor-work.txt').write_text('done', encoding='utf-8')",
            ["executor-work.txt"],
        ) + READS_MODEL
        reviewer = approving_reviewer_command(limited_unless("r2", "pass")) + READS_MODEL
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.project(root, executor, reviewer)
            result = run_drive(root)
            log = (stage_root / ".runtime/driver/logs/W-00000002.md").read_text(
                encoding="utf-8"
            )
            state = json.loads(
                (stage_root / ".runtime/driver/W-00000001.json").read_text(encoding="utf-8")
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('Model run: executor on codex with model "m2"', log)
        self.assertIn('Model run: reviewer on claude with model "r2"', log)
        self.assertIn('reviewer model "r1" on claude hit a usage limit', log)
        self.assertEqual(1, state["items"]["W-00000002"]["attempt_count"])

    def test_exhausted_executor_stops_and_spends_no_attempt(self):
        executor = python_command(limited_unless("never", "pass"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.project(root, executor + READS_MODEL, PASS_COMMAND)
            result = run_drive(root)
            state = json.loads(
                (stage_root / ".runtime/driver/W-00000001.json").read_text(encoding="utf-8")
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("every model group hit its usage limit", result.stdout)
        self.assertIn("Outcome: blocked", result.stdout)
        self.assertEqual(0, state["items"]["W-00000002"]["attempt_count"])


class CloseReviewFallbackTest(unittest.TestCase):
    def test_close_review_reruns_on_the_next_reviewer_model(self):
        reviewer = approving_reviewer_command(limited_unless("r2", "pass")) + READS_MODEL
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_project(root, executor=PASS_COMMAND, reviewer=reviewer, tiers=None)
            add_settings(
                stage_root,
                model_fallbacks={"claude": [["r1"], ["r2"]]},
                usage_limit_patterns={"claude": ["RESOURCE_EXHAUSTED"]},
            )
            initialize_git(root)
            import close_work

            card = next(
                path
                for path in (stage_root / "work/current").rglob("*.md")
                if "id: W-00000002\n" in path.read_text(encoding="utf-8")
            )
            with contextlib.redirect_stdout(io.StringIO()):
                ok, detail = close_work.run_close_review(
                    root, card, "W-00000002", reviewer, 30, 60
                )
            log = (stage_root / ".runtime/driver/logs/W-00000002.md").read_text(
                encoding="utf-8"
            )

        self.assertTrue(ok, detail)
        self.assertIn('Model run: reviewer on claude with model "r1"', log)
        self.assertIn('Model run: reviewer on claude with model "r2"', log)


class UnattendedFallbackTest(unittest.TestCase):
    def fixture(self) -> unattended_fixture.UnattendedTest:
        fixture = unattended_fixture.UnattendedTest("test_refuses_without_limits")
        self.addCleanup(fixture.doCleanups)
        return fixture

    def limits(self) -> dict[str, int]:
        return {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}

    def test_exhausted_executor_stops_the_run_without_escalating_the_card(self):
        fixture = self.fixture()
        executor = python_command(limited_unless("never", "pass")) + READS_MODEL
        root, stage_root = fixture.make(limits=self.limits(), executor=executor)
        add_settings(stage_root, model_fallbacks=FALLBACKS, usage_limit_patterns=PATTERNS)
        fixture.card(stage_root, "W-00000001")
        fixture.commit_all(root)
        drive = unattended_fixture.load_module()
        calls: list = []
        fixture.install_stubs(drive, calls)

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = drive.run_unattended(
                fixture.args(root, "W-00000001"), root, stage_root, time.time()
            )
        log = (stage_root / ".runtime/driver/logs/W-00000001.md").read_text(encoding="utf-8")

        self.assertEqual(1, rc)
        self.assertIn("every model group of venue codex hit its usage limit", out.getvalue())
        self.assertEqual([], [call for call in calls if call[0] == "escalate"])
        self.assertEqual(4, log.count("Model run: executor on codex"))

    def test_exhausted_close_review_stops_and_restores_the_card(self):
        fixture = self.fixture()
        root, stage_root = fixture.make(limits=self.limits())
        fixture.card(stage_root, "W-00000001")
        fixture.commit_all(root)
        drive = unattended_fixture.load_module()
        calls: list = []
        fixture.install_stubs(drive, calls)

        def exhausted_close(project_root, item_id, *_args, **_kwargs):
            calls.append(("close", item_id))
            return False, f"[{driver_model_fallback.USAGE_LIMITS_EXHAUSTED_MARKER}] reviewer"

        drive.unattended.close_via_close_work = exhausted_close
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = drive.run_unattended(
                fixture.args(root, "W-00000001"), root, stage_root, time.time()
            )
        card = fixture.card_path(stage_root, "W-00000001").read_text(encoding="utf-8")

        self.assertEqual(1, rc)
        self.assertEqual(1, len([call for call in calls if call[0] == "close"]))
        self.assertIn("reviewer venue hit its usage limit", out.getvalue())
        self.assertIn("status: active", card)
        self.assertIn("retrospective: pending", card)


if __name__ == "__main__":
    unittest.main()
