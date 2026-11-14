# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parents[1]
STAGE_ROOT = HOOKS_DIR.parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

import stage_model_tiers  # noqa: E402
import stage_work  # noqa: E402
from stage_paths import strip_json_comments  # noqa: E402

REGISTER_CLI = STAGE_ROOT / "skills" / "stage-work" / "register_work.py"
START_CLI = STAGE_ROOT / "scripts" / "start_work.py"

TIERS = {
    "scout": {
        "claude": {"model": "haiku", "effort": "low"},
        "codex": {"model": "codex-small", "effort": "low"},
    },
    "standard": {
        "claude": {"model": "sonnet", "effort": "medium"},
        "codex": {"model": "codex-large", "effort": "medium"},
    },
    "strong": {
        "claude": {"model": "opus[1m]", "effort": "high"},
        "codex": {"model": "codex-large"},
    },
    "lead": {"claude": {"model": "fable", "effort": "high"}},
}
ROUTING = {
    "*": "standard",
    "chore": "scout",
    "development": {"action": "strong", "*": "standard"},
}
ACTIVE = (
    "# Active Work\n\n"
    "| Work | Kind | Venue | Purpose | Status | Owner | Item |\n"
    "|---|---|---|---|---|---|---|\n"
)


def make_stage(settings: dict | str | None) -> Path:
    root = Path(tempfile.mkdtemp())
    stage_root = root / ".stage"
    stage_root.mkdir()
    if settings is not None:
        (stage_root / "settings.json").write_text(
            settings if isinstance(settings, str) else json.dumps(settings),
            encoding="utf-8",
        )
    return stage_root


class TierConfigTest(unittest.TestCase):
    def test_absent_model_tiers_is_inert(self):
        stage_root = make_stage({"schema_version": 5})
        config = stage_model_tiers.load_tier_config(stage_root)
        self.assertIsNone(config.tiers)
        self.assertEqual([], config.errors)
        self.assertEqual("", stage_model_tiers.registration_tier(stage_root, "chore", "story"))

    def test_unreadable_settings_is_inert(self):
        stage_root = make_stage("{not json")
        config = stage_model_tiers.load_tier_config(stage_root)
        self.assertIsNone(config.tiers)

    def test_declaration_order_is_cost_order(self):
        config = stage_model_tiers.load_tier_config(
            make_stage({"model_tiers": TIERS, "tier_routing": ROUTING})
        )
        self.assertEqual(["scout", "standard", "strong", "lead"], list(config.tiers))
        self.assertLess(config.rank("scout"), config.rank("standard"))
        self.assertLess(config.rank("strong"), config.rank("lead"))
        self.assertIsNone(config.rank("missing"))

    def test_venue_values_are_returned_in_their_native_shape(self):
        config = stage_model_tiers.load_tier_config(make_stage({"model_tiers": TIERS}))
        self.assertEqual(
            stage_model_tiers.VenueTier(model="opus[1m]", effort="high"),
            config.values("strong", "claude"),
        )
        self.assertEqual(
            stage_model_tiers.VenueTier(model="codex-large", effort=""),
            config.values("strong", "codex"),
        )
        self.assertIsNone(config.values("lead", "codex"))
        self.assertIsNone(config.values("missing", "claude"))

    def test_routing_uses_kind_then_scale_then_wildcards(self):
        config = stage_model_tiers.load_tier_config(
            make_stage({"model_tiers": TIERS, "tier_routing": ROUTING})
        )
        self.assertEqual("scout", config.route("chore", "action"))
        self.assertEqual("strong", config.route("development", "action"))
        self.assertEqual("standard", config.route("development", "story"))
        self.assertEqual("standard", config.route("documentation", "epic"))
        self.assertEqual("standard", config.route("Development", "Story"))

    def test_routing_without_match_selects_no_tier(self):
        config = stage_model_tiers.load_tier_config(
            make_stage({"model_tiers": TIERS, "tier_routing": {"chore": "scout"}})
        )
        self.assertEqual("", config.route("design", "story"))
        no_routing = stage_model_tiers.load_tier_config(make_stage({"model_tiers": TIERS}))
        self.assertEqual("", no_routing.route("chore", "story"))

    def test_malformed_tables_report_errors(self):
        cases = [
            {"model_tiers": ["scout"]},
            {"model_tiers": {}},
            {"model_tiers": {"scout": "haiku"}},
            {"model_tiers": {"scout": {"claude": "haiku"}}},
            {"model_tiers": {"scout": {"claude": {"model": 3}}}},
            {"model_tiers": {"scout": {"claude": {"temperature": "low"}}}},
            {"model_tiers": TIERS, "tier_routing": ["scout"]},
            {"model_tiers": TIERS, "tier_routing": {"chore": "cheap"}},
            {"model_tiers": TIERS, "tier_routing": {"chore": {"story": "cheap"}}},
            {"model_tiers": TIERS, "tier_routing": {"chore": 3}},
            {"tier_routing": {"chore": "scout"}},
        ]
        for settings in cases:
            with self.subTest(settings=settings):
                config = stage_model_tiers.load_tier_config(make_stage(settings))
                self.assertNotEqual([], config.errors)
                self.assertIsNone(config.tiers)

    def test_model_alias_matches_actual_model_id(self):
        matches = stage_model_tiers.model_matches
        self.assertTrue(matches("haiku", "claude-haiku-5-5"))
        self.assertTrue(matches("opus[1m]", "claude-opus-5-5"))
        self.assertTrue(matches("opus[1m]", "opus"))
        self.assertTrue(matches("codex-large", "codex-large"))
        self.assertFalse(matches("haiku", "claude-sonnet-5-5"))
        self.assertFalse(matches("", "claude-sonnet-5-5"))
        self.assertFalse(matches("sonnet", ""))

    def test_model_rank_is_the_cheapest_tier_using_that_model(self):
        config = stage_model_tiers.load_tier_config(make_stage({"model_tiers": TIERS}))
        self.assertEqual(config.rank("scout"), config.model_rank("claude", "haiku"))
        self.assertEqual(config.rank("strong"), config.model_rank("claude", "opus"))
        self.assertEqual(config.rank("lead"), config.model_rank("claude", "fable"))
        self.assertEqual(config.rank("standard"), config.model_rank("codex", "codex-large"))
        self.assertIsNone(config.model_rank("claude", "mystery"))


class WorkItemTierTest(unittest.TestCase):
    def test_work_item_reads_tier_field(self):
        stage_root = make_stage({"schema_version": 5})
        card = stage_root / "card.md"
        card.write_text(
            "---\nid: W-00000001\ntitle: T\nkind: chore\nvenue: codex\ntier: Scout\n---\n",
            encoding="utf-8",
        )
        item = stage_work.item_from_fields(
            card,
            stage_work.parse_frontmatter(card),
            {
                "status": "active",
                "verification": "pending",
                "retrospective": "pending",
                "promotion": "pending",
            },
        )
        self.assertEqual("scout", item.tier)


def run_register(root: Path, *args: str) -> subprocess.CompletedProcess:
    base = (
        "--purpose",
        "Deliver the requested outcome",
        "--success-criterion",
        "The user can observe the requested outcome",
    )
    return subprocess.run(
        [sys.executable, str(REGISTER_CLI), "--project-root", str(root), *args, *base],
        capture_output=True,
        text=True,
    )


def run_start(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(START_CLI), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def frontmatter(path: Path) -> dict:
    return stage_work.parse_frontmatter(path)


class RegistrationTierTest(unittest.TestCase):
    def make_project(self, settings: dict) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/work/current").mkdir(parents=True)
        (root / ".stage/work/planned").mkdir(parents=True)
        (root / ".stage/official/work/archive/items").mkdir(parents=True)
        (root / ".stage/work/active.md").write_text(ACTIVE, encoding="utf-8")
        (root / ".stage/settings.json").write_text(
            json.dumps({"schema_version": 5, **settings}), encoding="utf-8"
        )
        return tmp, root

    def test_registration_writes_the_routed_tier_after_venue(self):
        tmp, root = self.make_project({"model_tiers": TIERS, "tier_routing": ROUTING})
        with tmp:
            story = run_register(
                root, "--scale", "story", "--title", "S", "--kind", "development",
                "--venue", "codex", "--scope", "src", "--id", "W-00000001",
            )
            action = run_register(
                root, "--scale", "action", "--parent", "W-00000001", "--title", "A",
                "--kind", "development", "--venue", "codex", "--scope", "src",
                "--id", "W-00000002",
            )
            story_text = (root / ".stage/work/current/W-00000001/_story.md").read_text(
                encoding="utf-8"
            )
            action_fields = frontmatter(root / ".stage/work/current/W-00000001/W-00000002.md")

        self.assertEqual(0, story.returncode, story.stderr)
        self.assertEqual(0, action.returncode, action.stderr)
        self.assertIn("\nvenue: codex\ntier: standard\n", story_text)
        self.assertEqual("strong", action_fields["tier"])

    def test_tier_follows_environment_when_both_are_present(self):
        settings = {
            "model_tiers": TIERS,
            "tier_routing": ROUTING,
            "environment_venues": {"cloud": "claude"},
        }
        tmp, root = self.make_project(settings)
        with tmp:
            result = run_register(
                root, "--scale", "story", "--title", "S", "--kind", "chore",
                "--environment", "cloud", "--review", "--scope", "src",
            )
            text = (root / ".stage/work/current/W-00000001/_story.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("\nvenue: claude\nenvironment: cloud\ntier: scout\n", text)

    def test_explicit_tier_overrides_routing(self):
        tmp, root = self.make_project({"model_tiers": TIERS, "tier_routing": ROUTING})
        with tmp:
            result = run_register(
                root, "--scale", "story", "--title", "S", "--kind", "chore",
                "--scope", "src", "--tier", "Strong",
            )
            fields = frontmatter(root / ".stage/work/current/W-00000001/_story.md")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("strong", fields["tier"])

    def test_unknown_tier_name_is_refused(self):
        tmp, root = self.make_project({"model_tiers": TIERS, "tier_routing": ROUTING})
        with tmp:
            result = run_register(
                root, "--scale", "story", "--title", "S", "--kind", "chore",
                "--scope", "src", "--tier", "cheap",
            )
            created = list((root / ".stage/work/current").glob("W-*"))

        self.assertNotEqual(0, result.returncode)
        self.assertIn("cheap", result.stderr)
        self.assertEqual([], created)

    def test_routing_to_unknown_tier_is_refused(self):
        tmp, root = self.make_project(
            {"model_tiers": TIERS, "tier_routing": {"chore": "cheap"}}
        )
        with tmp:
            result = run_register(
                root, "--scale", "story", "--title", "S", "--kind", "chore", "--scope", "src",
            )
            created = list((root / ".stage/work/current").glob("W-*"))

        self.assertNotEqual(0, result.returncode)
        self.assertIn("cheap", result.stderr)
        self.assertEqual([], created)

    def test_without_model_tiers_no_tier_line_and_tier_flag_is_refused(self):
        tmp, root = self.make_project({})
        with tmp:
            plain = run_register(
                root, "--scale", "story", "--title", "S", "--kind", "chore", "--scope", "src",
            )
            text = (root / ".stage/work/current/W-00000001/_story.md").read_text(
                encoding="utf-8"
            )
            flagged = run_register(
                root, "--scale", "story", "--title", "S2", "--kind", "chore",
                "--scope", "src", "--tier", "scout",
            )

        self.assertEqual(0, plain.returncode, plain.stderr)
        self.assertNotIn("tier:", text)
        self.assertNotEqual(0, flagged.returncode)
        self.assertIn("model_tiers", flagged.stderr)

    def test_captured_card_records_tier_and_start_keeps_it(self):
        tmp, root = self.make_project({"model_tiers": TIERS, "tier_routing": ROUTING})
        with tmp:
            captured = run_register(
                root, "--backlog", "--scale", "story", "--title", "S", "--kind", "chore",
                "--scope", "src", "--id", "W-00000001",
            )
            planned = root / ".stage/work/planned/W-00000001/_story.md"
            planned_tier = frontmatter(planned)["tier"]
            planned.write_text(
                planned.read_text(encoding="utf-8").replace("tier: scout", "tier: strong"),
                encoding="utf-8",
            )
            started = run_start(root, "W-00000001", "--scope", "src")
            fields = frontmatter(root / ".stage/work/current/W-00000001/_story.md")

        self.assertEqual(0, captured.returncode, captured.stderr)
        self.assertEqual("scout", planned_tier)
        self.assertEqual(0, started.returncode, started.stderr)
        self.assertEqual("strong", fields["tier"])

    def test_start_fills_a_missing_tier_for_the_whole_unit(self):
        tmp, root = self.make_project({})
        with tmp:
            epic = run_register(
                root, "--backlog", "--scale", "epic", "--title", "E", "--kind", "chore",
                "--scope", "src", "--id", "W-00000001",
            )
            story = run_register(
                root, "--backlog", "--scale", "story", "--parent", "W-00000001",
                "--title", "S", "--kind", "development", "--scope", "src",
                "--id", "W-00000002",
            )
            (root / ".stage/settings.json").write_text(
                json.dumps(
                    {"schema_version": 5, "model_tiers": TIERS, "tier_routing": ROUTING}
                ),
                encoding="utf-8",
            )
            started = run_start(root, "W-00000001", "--scope", "src")
            epic_fields = frontmatter(root / ".stage/work/current/W-00000001/_epic.md")
            story_fields = frontmatter(
                root / ".stage/work/current/W-00000001/W-00000002/_story.md"
            )

        self.assertEqual(0, epic.returncode, epic.stderr)
        self.assertEqual(0, story.returncode, story.stderr)
        self.assertEqual(0, started.returncode, started.stderr)
        self.assertEqual("scout", epic_fields["tier"])
        self.assertEqual("standard", story_fields["tier"])

    def test_start_without_model_tiers_writes_no_tier(self):
        tmp, root = self.make_project({})
        with tmp:
            run_register(
                root, "--backlog", "--scale", "story", "--title", "S", "--kind", "chore",
                "--scope", "src", "--id", "W-00000001",
            )
            started = run_start(root, "W-00000001", "--scope", "src")
            text = (root / ".stage/work/current/W-00000001/_story.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, started.returncode, started.stderr)
        self.assertNotIn("tier:", text)


class TemplateTiersTest(unittest.TestCase):
    def test_project_template_ships_claude_tiers_and_routing(self):
        template = STAGE_ROOT / "templates" / "v4" / "project-stage" / "settings.jsonc"
        data = json.loads(strip_json_comments(template.read_text(encoding="utf-8")))
        tiers = data["model_tiers"]
        self.assertEqual(["scout", "standard", "strong", "lead"], list(tiers))
        for name, venues in tiers.items():
            self.assertEqual(["claude"], list(venues), name)
        self.assertEqual("standard", data["tier_routing"]["*"])
        config = stage_model_tiers.parse_tier_config(data)
        self.assertEqual([], config.errors)


if __name__ == "__main__":
    unittest.main()
