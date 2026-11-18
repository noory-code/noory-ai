from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
STAGE_ROOT = SCRIPTS_DIR.parent
for import_dir in (STAGE_ROOT / "hooks", SCRIPTS_DIR, Path(__file__).resolve().parent):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from test_drive import (  # noqa: E402
    PASS_COMMAND,
    approving_reviewer_command,
    initialize_git,
    reporting_python_command,
    write_card,
)
import driver_environment  # noqa: E402
import driver_worklog  # noqa: E402
from stage_work import load_all_work_items  # noqa: E402

DRIVE = SCRIPTS_DIR / "drive.py"
CLOSE_WORK = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
TIERS = {
    "scout": {
        "claude": {"model": "haiku", "effort": "low"},
        "codex": {"model": "codex-small"},
    },
    "standard": {
        "claude": {"model": "sonnet", "effort": "medium"},
        "codex": {"model": "codex-large", "effort": "medium"},
    },
}
MODEL_TIER_LINE = re.compile(r"^Model tier \(JSON\): (.+)$", re.MULTILINE)


def set_card_tier(stage_root: Path, item_id: str, tier: str) -> Path:
    for path in (stage_root / "work/current").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if f"id: {item_id}\n" in text:
            path.write_text(
                text.replace(f"id: {item_id}\n", f"id: {item_id}\ntier: {tier}\n", 1),
                encoding="utf-8",
            )
            return path
    raise AssertionError(f"no card {item_id}")


def make_project(
    root: Path,
    *,
    executor: str,
    reviewer: str,
    tiers: dict | None = TIERS,
) -> Path:
    stage_root = root / ".stage"
    stage_root.mkdir()
    settings: dict[str, object] = {
        "schema_version": 5,
        "executors": {"codex": executor},
        "review": {"reviewers": {"codex": "echo SELF", "claude": reviewer}},
    }
    if tiers is not None:
        settings["model_tiers"] = tiers
    (stage_root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    write_card(stage_root, "W-00000001")
    write_card(stage_root, "W-00000002", parent="W-00000001", acceptance=(PASS_COMMAND,))
    return stage_root


def capture_environment_code(target: Path) -> str:
    return (
        "import json, os; from pathlib import Path; "
        f"Path({str(target)!r}).write_text(json.dumps({{"
        "'model': os.environ.get('STAGE_MODEL'), "
        "'effort': os.environ.get('STAGE_EFFORT')}), encoding='utf-8')"
    )


def run_drive(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DRIVE), "--project-root", str(root), "--execute", "W-00000001"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class TierEnvironmentTest(unittest.TestCase):
    def items(self, root: Path, *, tier: str = "", tiers: dict | None = TIERS):
        stage_root = make_project(root, executor=PASS_COMMAND, reviewer=PASS_COMMAND, tiers=tiers)
        if tier:
            set_card_tier(stage_root, "W-00000002", tier)
        items = load_all_work_items(stage_root)
        return stage_root, items, next(i for i in items if i.item_id == "W-00000002")

    def executor_env(self, root: Path, item, items, stage_root: Path) -> dict[str, str]:
        return driver_environment.executor_environment(
            item,
            root,
            stage_root / ".runtime/driver/logs/W-00000002.md",
            stage_root / ".runtime/driver/verdicts/W-00000002.json",
            items=items,
        )

    def test_executor_receives_its_venue_values_for_the_card_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root, items, item = self.items(root, tier="standard")
            env = self.executor_env(root, item, items, stage_root)

        self.assertEqual("codex-large", env["STAGE_MODEL"])
        self.assertEqual("medium", env["STAGE_EFFORT"])

    def test_an_omitted_value_is_not_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root, items, item = self.items(root, tier="scout")
            env = self.executor_env(root, item, items, stage_root)

        self.assertEqual("codex-small", env["STAGE_MODEL"])
        self.assertNotIn("STAGE_EFFORT", env)

    def test_reviewer_gets_its_own_venue_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stage_root, _items, item = self.items(root, tier="scout")
            env = driver_environment.model_tier_environment(root, item, "claude")

        self.assertEqual({"STAGE_MODEL": "haiku", "STAGE_EFFORT": "low"}, env)

    def test_no_tier_or_no_model_tiers_exports_nothing_even_when_inherited(self):
        inherited = {"STAGE_MODEL": "leaked", "STAGE_EFFORT": "leaked"}
        for tier, tiers in (("", TIERS), ("standard", None)):
            with self.subTest(tier=tier, tiers=tiers is not None):
                with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(
                    os.environ, inherited
                ):
                    root = Path(tmp)
                    stage_root, items, item = self.items(root, tier=tier, tiers=tiers)
                    env = self.executor_env(root, item, items, stage_root)
                    reviewer_env = driver_environment.project_environment(root)
                    reviewer_env.update(
                        driver_environment.model_tier_environment(root, item, "claude")
                    )

                self.assertNotIn("STAGE_MODEL", env)
                self.assertNotIn("STAGE_EFFORT", env)
                self.assertNotIn("STAGE_MODEL", reviewer_env)
                self.assertNotIn("STAGE_EFFORT", reviewer_env)

    def test_record_says_whether_each_command_reads_the_variables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stage_root, _items, item = self.items(root, tier="standard")
            record = driver_environment.model_tier_record(
                root,
                item,
                executor_venue="codex",
                executor_command='tool --model "$STAGE_MODEL" --effort "$STAGE_EFFORT"',
                reviewer_venue="claude",
                reviewer_command="tool --model opus",
            )

        self.assertEqual(
            {
                "tier": "standard",
                "executor": {
                    "venue": "codex",
                    "model": "codex-large",
                    "effort": "medium",
                    "command_uses_model_env": True,
                    "command_uses_effort_env": True,
                },
                "reviewer": {
                    "venue": "claude",
                    "model": "sonnet",
                    "effort": "medium",
                    "command_uses_model_env": False,
                    "command_uses_effort_env": False,
                },
            },
            record,
        )

    def test_record_is_absent_without_a_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stage_root, _items, item = self.items(root)
            record = driver_environment.model_tier_record(
                root,
                item,
                executor_venue="codex",
                executor_command="tool",
                reviewer_venue="claude",
                reviewer_command="tool",
            )

        self.assertIsNone(record)

    def test_work_log_line_carries_the_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "log.md"
            log.write_text("# log\n", encoding="utf-8")
            record = {"tier": "scout", "executor": {}, "reviewer": {}}
            driver_worklog.append_driver_commands_to_work_log(
                log, executor_command="e", reviewer_command="r", model_tier=record
            )
            driver_worklog.append_driver_commands_to_work_log(
                log, executor_command="e", reviewer_command="r"
            )
            text = log.read_text(encoding="utf-8")

        self.assertEqual([record], [json.loads(m) for m in MODEL_TIER_LINE.findall(text)])
        self.assertEqual(2, text.count("### Driver commands"))


class DriverRunTest(unittest.TestCase):
    def run_round(self, root: Path, *, tier: str, tiers: dict | None, shell_prefix: str = ""):
        executor_seen = root.parent / f"{root.name}-executor.json"
        reviewer_seen = root.parent / f"{root.name}-reviewer.json"
        executor = shell_prefix + reporting_python_command(
            capture_environment_code(executor_seen)
            + "; Path('executor-work.txt').write_text('done', encoding='utf-8')",
            ["executor-work.txt"],
        )
        reviewer = approving_reviewer_command(capture_environment_code(reviewer_seen))
        stage_root = make_project(root, executor=executor, reviewer=reviewer, tiers=tiers)
        if tier:
            set_card_tier(stage_root, "W-00000002", tier)
        initialize_git(root)
        result = run_drive(root)
        log = (stage_root / ".runtime/driver/logs/W-00000002.md").read_text(encoding="utf-8")
        return (
            result,
            json.loads(executor_seen.read_text(encoding="utf-8")),
            json.loads(reviewer_seen.read_text(encoding="utf-8")),
            log,
        )

    def test_supervised_round_passes_both_roles_their_venue_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            result, executor_seen, reviewer_seen, log = self.run_round(
                root, tier="standard", tiers=TIERS
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual({"model": "codex-large", "effort": "medium"}, executor_seen)
        self.assertEqual({"model": "sonnet", "effort": "medium"}, reviewer_seen)
        records = [json.loads(match) for match in MODEL_TIER_LINE.findall(log)]
        self.assertEqual(1, len(records))
        self.assertEqual("standard", records[0]["tier"])
        self.assertEqual("codex-large", records[0]["executor"]["model"])
        self.assertEqual("claude", records[0]["reviewer"]["venue"])
        self.assertFalse(records[0]["executor"]["command_uses_model_env"])

    @unittest.skipIf(os.name == "nt", "POSIX shell expansion of $STAGE_MODEL")
    def test_a_command_that_references_the_variable_runs_with_its_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            expanded = Path(tmp) / "expanded.txt"
            prefix = f'printf "%s/%s" "$STAGE_MODEL" "$STAGE_EFFORT" > "{expanded}" && '
            result, _executor_seen, _reviewer_seen, log = self.run_round(
                root, tier="standard", tiers=TIERS, shell_prefix=prefix
            )
            written = expanded.read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("codex-large/medium", written)
        record = json.loads(MODEL_TIER_LINE.findall(log)[0])
        self.assertTrue(record["executor"]["command_uses_model_env"])
        self.assertTrue(record["executor"]["command_uses_effort_env"])

    def test_without_model_tiers_the_round_exports_and_logs_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            result, executor_seen, reviewer_seen, log = self.run_round(
                root, tier="standard", tiers=None
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual({"model": None, "effort": None}, executor_seen)
        self.assertEqual({"model": None, "effort": None}, reviewer_seen)
        self.assertNotIn("Model tier (JSON)", log)


class CloseReviewTierTest(unittest.TestCase):
    def test_close_review_environment_carries_the_reviewer_venue_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_project(root, executor=PASS_COMMAND, reviewer=PASS_COMMAND)
            card = set_card_tier(stage_root, "W-00000002", "scout")
            initialize_git(root)
            sys.path.insert(0, str(CLOSE_WORK.parent))
            import close_work

            env = close_work.close_review_environment(
                root, card, "W-00000002", Path(tmp) / "changed.json", 30
            )

        self.assertEqual("haiku", env["STAGE_MODEL"])
        self.assertEqual("low", env["STAGE_EFFORT"])


if __name__ == "__main__":
    unittest.main()
