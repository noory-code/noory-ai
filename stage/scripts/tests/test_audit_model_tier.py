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
REGISTER = STAGE / "skills" / "stage-work" / "register_work.py"
AUDIT = STAGE / "scripts" / "audit_stage.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"
TIERS = {
    "scout": {"claude": {"model": "haiku", "effort": "low"}, "codex": {"model": "cx-small", "effort": "low"}},
    "standard": {
        "claude": {"model": "sonnet", "effort": "medium"},
        "codex": {"model": "cx-large", "effort": "medium"},
    },
    "strong": {"claude": {"model": "opus", "effort": "high"}, "codex": {"model": "cx-large", "effort": "high"}},
    "lead": {"claude": {"model": "fable", "effort": "high"}},
}
SETTINGS = {
    "schema_version": 5,
    "venue_routing": {"development": "codex"},
    "model_tiers": TIERS,
    "tier_routing": {"*": "standard"},
}
TIER_LINE = re.compile(r"^(ERROR|WARNING) (TIER\d{3}) \[([^\]]*)\]: (.*)$", re.MULTILINE)


def run(script: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class AuditModelTierTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, self.stage)
        (self.stage / "settings.jsonc").unlink()
        self.write_settings(SETTINGS)
        proc = run(
            REGISTER,
            self.root,
            "--title", "Build it", "--kind", "development", "--scale", "story",
            "--scope", "src/", "--purpose", "Deliver the requested outcome.",
            "--success-criterion", "The user can observe the requested outcome",
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.card = self.stage / "work/current/W-00000001/_story.md"
        self.assertIn("tier: standard", self.card.read_text(encoding="utf-8"))

    def write_settings(self, settings: dict) -> None:
        (self.stage / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

    def set_card_tier(self, tier: str) -> None:
        text = self.card.read_text(encoding="utf-8")
        self.card.write_text(re.sub(r"^tier: .*$", f"tier: {tier}", text, flags=re.M), encoding="utf-8")

    def findings(self) -> list[tuple[str, str, str, str]]:
        return TIER_LINE.findall(run(AUDIT, self.root).stdout)

    def codes(self) -> list[str]:
        return [code for _level, code, _path, _message in self.findings()]

    def driver_log(self, record: dict) -> None:
        log = self.stage / ".runtime/driver/logs/W-00000001.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(
            "# Work log\n\n### Driver commands\n"
            'Executor command: "x"\nReviewer command: "y"\n'
            f"Model tier (JSON): {json.dumps(record)}\n",
            encoding="utf-8",
        )

    def driver_record(self, **overrides) -> dict:
        record = {
            "tier": "standard",
            "executor": {
                "venue": "codex", "model": "cx-large", "effort": "medium",
                "command_uses_model_env": True, "command_uses_effort_env": True,
            },
            "reviewer": {
                "venue": "claude", "model": "sonnet", "effort": "medium",
                "command_uses_model_env": True, "command_uses_effort_env": True,
            },
        }
        record.update(overrides)
        return record

    def usage(self, *records: dict, raw: str = "") -> None:
        folder = self.stage / ".runtime/model-usage"
        folder.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(record) for record in records]
        if raw:
            lines.append(raw)
        (folder / "session-1.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def finished(self, model: str, effort: str, **overrides) -> dict:
        record = {
            "event": "agent_finished", "session_id": "session-1", "agent_id": "a1",
            "cards": ["W-00000001"], "tier": "standard", "ceiling": "standard",
            "model": model, "effort": effort,
        }
        record.update(overrides)
        return record

    def test_matching_records_raise_nothing(self):
        self.driver_log(self.driver_record())
        self.usage(self.finished("claude-sonnet-5-5", "medium"))

        self.assertEqual([], self.codes())

    def test_a_driver_round_on_another_tier_is_reported(self):
        self.driver_log(self.driver_record())
        self.set_card_tier("strong")
        findings = [f for f in self.findings() if f[1] == "TIER003"]

        self.assertTrue(findings)
        self.assertTrue(all(level == "WARNING" for level, *_ in findings))
        message = " ".join(f[3] for f in findings)
        self.assertIn("W-00000001", message)
        self.assertIn("standard", message)
        self.assertIn("strong", message)

    def test_a_command_that_ignores_the_variables_is_reported(self):
        record = self.driver_record()
        record["executor"]["command_uses_model_env"] = False
        self.driver_log(record)
        message = " ".join(f[3] for f in self.findings() if f[1] == "TIER003")

        self.assertIn("STAGE_MODEL", message)
        self.assertIn("executor", message)
        self.assertIn("cx-large", message)

    def test_a_subagent_on_another_model_is_reported_with_its_reason(self):
        self.usage(
            {"event": "agent_requested", "agent_id": "a1", "cards": ["W-00000001"],
             "tier": "standard", "over_tier_reason": "needs the deepest model"},
            self.finished("claude-fable-5-2", "medium"),
        )
        findings = [f for f in self.findings() if f[1] == "TIER004"]

        self.assertEqual(1, len(findings))
        level, _code, _path, message = findings[0]
        self.assertEqual("WARNING", level)
        self.assertIn("W-00000001", message)
        self.assertIn("sonnet", message)
        self.assertIn("claude-fable-5-2", message)
        self.assertIn("needs the deepest model", message)

    def test_a_subagent_on_another_effort_is_reported(self):
        self.usage(self.finished("claude-sonnet-5-5", "high"))
        message = " ".join(f[3] for f in self.findings() if f[1] == "TIER004")

        self.assertIn("medium", message)
        self.assertIn("high", message)

    def test_records_for_cards_that_are_not_current_are_ignored(self):
        self.usage(self.finished("claude-fable-5-2", "high", cards=["W-00000999"]))

        self.assertEqual([], self.codes())

    def test_an_unreadable_record_line_is_reported_and_the_rest_still_checked(self):
        self.usage(self.finished("claude-fable-5-2", "medium"), raw="{not json")

        codes = self.codes()
        self.assertIn("TIER005", codes)
        self.assertIn("TIER004", codes)

    def test_without_model_tiers_nothing_is_checked(self):
        self.driver_log(self.driver_record(tier="scout"))
        self.usage(self.finished("claude-fable-5-2", "high"))
        self.write_settings({k: v for k, v in SETTINGS.items() if k not in ("model_tiers", "tier_routing")})
        self.set_card_tier("standard")
        text = self.card.read_text(encoding="utf-8")
        self.card.write_text(text.replace("tier: standard\n", ""), encoding="utf-8")

        self.assertEqual([], self.codes())

    def test_invalid_settings_and_undeclared_card_tiers_are_errors(self):
        self.write_settings({**SETTINGS, "tier_routing": {"*": "cheap"}})
        self.assertIn(("ERROR", "TIER001"), [(f[0], f[1]) for f in self.findings()])

        self.write_settings(SETTINGS)
        self.set_card_tier("cheap")
        findings = [f for f in self.findings() if f[1] == "TIER002"]
        self.assertEqual(1, len(findings))
        self.assertEqual("ERROR", findings[0][0])
        self.assertIn("cheap", findings[0][3])

    def test_a_card_tier_without_model_tiers_is_an_error(self):
        self.write_settings({k: v for k, v in SETTINGS.items() if k not in ("model_tiers", "tier_routing")})

        self.assertIn("TIER002", self.codes())


if __name__ == "__main__":
    unittest.main()
