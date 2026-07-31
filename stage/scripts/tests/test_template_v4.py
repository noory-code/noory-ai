"""Active schema-v4 template tree contract."""

import importlib.util
import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
PROJECT_SETTINGS = PLUGIN_ROOT.parent / ".stage" / "settings.json"
V3_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
V4_ROOT = PLUGIN_ROOT / "templates" / "v4" / "project-stage"
V4_LOCALE_ROOT = PLUGIN_ROOT / "templates" / "v4" / "locales" / "ko"

EXTRA_V4_FILES = {
    Path("decisions/index.md"),
    Path("official/work/archive/items/_epic.md"),
    Path("official/work/archive/items/_story.md"),
    Path("roadmap/milestones/index.md"),
    Path("roadmap/themes/index.md"),
    Path("work/current/_epic.md"),
    Path("work/current/_story.md"),
    Path("work/planned/_epic.md"),
    Path("work/planned/_story.md"),
}

_INIT_SPEC = importlib.util.spec_from_file_location(
    "template_v4_init_stage", PLUGIN_ROOT / "scripts" / "init_stage.py"
)
assert _INIT_SPEC is not None and _INIT_SPEC.loader is not None
init_stage = importlib.util.module_from_spec(_INIT_SPEC)
_INIT_SPEC.loader.exec_module(init_stage)


def v4_path(relative: Path) -> Path:
    """Map one schema-v3 template path to its schema-v4 destination."""
    value = relative.as_posix()
    if value == "settings.json":
        return Path("settings.jsonc")
    relocations = (
        ("past/canon", "official/canon"),
        ("past/model", "official/model"),
        ("past/decisions", "official/decisions"),
        ("past/work/archive", "official/work/archive"),
        ("present/work/items", "work/current"),
        ("present/work/decisions", "decisions/pending"),
        ("present/work/retrospectives", "work/retrospectives"),
        ("present/work/active.md", "work/active.md"),
        ("present/work/review.md", "work/review.md"),
        ("present/state", "state"),
        ("future/backlog/items", "work/planned"),
        ("future/backlog/index.md", "work/planned/index.md"),
        ("future/backlog/views", "work/views"),
        ("future/proposals", "proposals"),
        ("future/roadmap", "roadmap"),
    )
    for source, destination in relocations:
        if value == source or value.startswith(f"{source}/"):
            return Path(f"{destination}{value[len(source):]}")
    return relative


def frontmatter_keys(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return []
    keys = []
    for line in lines[1:]:
        if line == "---":
            break
        keys.append(line.split(":", 1)[0])
    return keys


class TemplateV4Test(unittest.TestCase):
    def files_under(self, root: Path) -> set[Path]:
        return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}

    def test_v4_tree_mirrors_v3_file_set_under_renamed_roots(self):
        expected = {v4_path(path) for path in self.files_under(V3_ROOT)} | EXTRA_V4_FILES
        self.assertEqual(expected, self.files_under(V4_ROOT))

    def test_v4_tree_is_active_and_v3_operations_are_verbatim(self):
        self.assertEqual(V4_ROOT, init_stage.TEMPLATE_ROOT)
        self.assertNotEqual(V3_ROOT, init_stage.TEMPLATE_ROOT)
        self.assertEqual(
            (V3_ROOT / "operations/verification.md").read_bytes(),
            (V4_ROOT / "operations/verification.md").read_bytes(),
        )

    def test_v4_settings_marker_is_bundled_and_init_is_cut_over(self):
        settings_text = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")
        self.assertIn('"schema_version": 5', settings_text)
        self.assertIn("//", settings_text)
        v3_settings = json.loads((V3_ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(3, v3_settings["schema_version"])
        self.assertEqual(V4_ROOT, init_stage.TEMPLATE_ROOT)

    def test_v4_settings_documents_hierarchy_executor_and_subtree_limit_contracts(self):
        settings_text = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")

        self.assertIn("STAGE_WORK_ITEM_ANCESTOR_PATHS", settings_text)
        self.assertIn('"preflights"', settings_text)
        self.assertIn("null", settings_text)
        self.assertIn('"max_attempts_per_item"', settings_text)
        self.assertIn('"max_iterations"', settings_text)
        self.assertIn('"max_wall_clock_seconds"', settings_text)

    def test_project_declares_preflight_policy_for_every_executor_venue(self):
        settings = json.loads(PROJECT_SETTINGS.read_text(encoding="utf-8"))

        self.assertEqual(set(settings["executors"]), set(settings["preflights"]))

    def test_project_pins_the_current_model_in_all_eight_driver_commands(self):
        settings = json.loads(PROJECT_SETTINGS.read_text(encoding="utf-8"))
        commands = {
            "executor.claude": settings["executors"]["claude"],
            "executor.codex": settings["executors"]["codex"],
            "reviewer.claude": settings["review"]["reviewers"]["claude"],
            "reviewer.codex": settings["review"]["reviewers"]["codex"],
            **{
                f"strength.{name}": command
                for name, command in settings["review"]["strengths"].items()
                if command is not None
            },
        }

        self.assertEqual(8, len(commands))
        for name, command in commands.items():
            with self.subTest(name=name):
                expected_model = (
                    "--model 'opus[1m]'"
                    if name in {"executor.claude", "reviewer.claude"}
                    else "--model gpt-5.6-sol"
                )
                self.assertIn(expected_model, command)

    def test_v4_settings_template_exposes_all_eight_model_pinning_positions(self):
        settings_text = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")
        settings = json.loads(
            "\n".join(
                line
                for line in settings_text.splitlines()
                if not line.lstrip().startswith("//")
            )
        )
        commands = list(settings["executors"].values())
        commands += list(settings["review"]["reviewers"].values())
        commands += [
            command
            for command in settings["review"]["strengths"].values()
            if command is not None
        ]

        self.assertEqual(8, len(commands))
        self.assertIn("--model", settings_text)

    def test_executor_prompts_share_ancestor_and_cumulative_reporting_instructions(self):
        ancestor_instruction = (
            "Read the selected card at $STAGE_WORK_ITEM_PATH and every ancestor card "
            "listed in $STAGE_WORK_ITEM_ANCESTOR_PATHS before acting; together they "
            "are the whole instruction."
        )
        reporting_instruction = (
            "Changed paths (JSON) must contain every repository-relative path changed "
            "for this card across all attempts."
        )
        template_settings = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")

        self.assertIn(ancestor_instruction, template_settings)
        self.assertIn(reporting_instruction, template_settings)

    def test_executor_prompts_share_autonomy_and_reporting_contract(self):
        settings = json.loads(PROJECT_SETTINGS.read_text(encoding="utf-8"))
        template_settings = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")
        required_fragments = (
            "Within the card's declared scope, do work needed for its purpose and report "
            "every decision you make.",
            "When needed work is outside scope, do not act; report what is needed.",
            "Skip work the purpose does not need without reporting it.",
            "Decisions made:",
            "Work not done:",
            "Use None when there is nothing to report for a field.",
        )

        self.assertEqual({"claude", "codex"}, set(settings["executors"]))
        for command in (*settings["executors"].values(), template_settings):
            with self.subTest(command=command):
                for fragment in required_fragments:
                    self.assertIn(fragment, command)

    def test_review_prompts_require_reading_executor_judgment_fields(self):
        settings = json.loads(PROJECT_SETTINGS.read_text(encoding="utf-8"))
        review = settings["review"]
        commands = list(review["reviewers"].values()) + [
            command
            for command in review["strengths"].values()
            if command is not None
        ]
        instruction = (
            "Read the non-empty Decisions made: and Work not done: fields in the latest "
            "executor report and judge whether the declared-scope contract was followed."
        )
        template_settings = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")

        self.assertEqual(6, len(commands))
        for command in (*commands, template_settings):
            with self.subTest(command=command):
                self.assertIn(instruction, command)

    def test_v4_settings_template_documents_review_verdict_file_contract(self):
        template_settings = (V4_ROOT / "settings.jsonc").read_text(encoding="utf-8")

        self.assertIn("STAGE_REVIEW_VERDICT_FILE", template_settings)
        self.assertIn("STAGE_REVIEW_MODE", template_settings)
        self.assertIn("STAGE_PREVIOUS_REVIEW_VERDICT_FILE", template_settings)
        self.assertIn("STAGE_REVIEW_FAILED_CRITERIA_FILE", template_settings)
        self.assertIn("reviewed_in_round", template_settings)
        self.assertIn('"criteria"', template_settings)
        self.assertIn('"criterion"', template_settings)
        self.assertIn('"verdict"', template_settings)
        self.assertIn('"reason"', template_settings)
        self.assertIn('"approved"', template_settings)

    def test_project_review_prompts_share_every_verdict_validation_condition(self):
        settings = json.loads(PROJECT_SETTINGS.read_text(encoding="utf-8"))
        review = settings["review"]
        commands = list(review["reviewers"].values()) + [
            command
            for command in review["strengths"].values()
            if command is not None
        ]
        required_fragments = (
            "$STAGE_REVIEW_VERDICT_FILE",
            "exactly the keys criteria and approved",
            "objects with exactly the keys criterion, verdict, and reason",
            "criterion and reason are non-empty one-line strings",
            "criterion values are unique",
            "approved is true exactly when every criterion passes",
            "$STAGE_PREVIOUS_REVIEW_VERDICT_FILE",
            "$STAGE_REVIEW_FAILED_CRITERIA_FILE",
            "judge only those failed criteria plus any previously passing criterion "
            "affected by the paths in $STAGE_CHANGED_PATHS_FILE",
            "write only criteria judged in this round because the driver merges them",
            "Otherwise, judge every ## Success criteria item",
        )

        self.assertEqual(6, len(commands))
        for command in commands:
            with self.subTest(command=command):
                for fragment in required_fragments:
                    self.assertIn(fragment, command)

    def test_project_executor_prompts_limit_empty_claim_to_all_reasoned_rejections(self):
        settings = json.loads(PROJECT_SETTINGS.read_text(encoding="utf-8"))
        executors = settings["executors"]
        instruction = (
            "Only when every failed criterion is declined or deferred with a reason "
            "may Changed paths (JSON) be empty."
        )

        self.assertEqual({"claude", "codex"}, set(executors))
        for command in executors.values():
            with self.subTest(command=command):
                self.assertIn(instruction, command)
                self.assertNotIn(
                    "A reasoned decline or defer may claim an empty Changed paths array.",
                    command,
                )

    def test_close_work_comments_do_not_describe_removed_block_scanning(self):
        source = (
            PLUGIN_ROOT / "skills" / "stage-retrospective" / "close_work.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("verdict scan", source)
        self.assertNotIn("`BLOCK:` verdict line", source)

    def test_driver_source_has_no_dead_base_repository_paths_field(self):
        source = (PLUGIN_ROOT / "scripts/drive.py").read_text(encoding="utf-8")

        self.assertNotIn("base_repository_paths", source)

    def test_roadmap_templates_have_computed_status_contract(self):
        theme = V4_ROOT / "roadmap/themes/_template.md"
        milestone = V4_ROOT / "roadmap/milestones/_template.md"
        self.assertEqual(["id", "decision_refs"], frontmatter_keys(theme))
        self.assertEqual(["id", "theme", "decision_refs"], frontmatter_keys(milestone))
        self.assertIn("id: TH-00000000", theme.read_text(encoding="utf-8"))
        self.assertIn("id: M-00000000", milestone.read_text(encoding="utf-8"))
        for template in (theme, milestone):
            text = template.read_text(encoding="utf-8")
            self.assertNotIn("status:", text.lower())
            self.assertNotIn("## Status", text)

    def test_roadmap_families_and_pending_decisions_have_indexes(self):
        for relative in {
            Path("decisions/index.md"),
            Path("roadmap/milestones/index.md"),
            Path("roadmap/themes/index.md"),
        }:
            with self.subTest(file=str(relative)):
                self.assertTrue((V4_ROOT / relative).is_file())
                self.assertTrue((V4_LOCALE_ROOT / relative).is_file())

    def test_work_hierarchy_templates_have_no_parent_field(self):
        work_templates = (
            Path("work/planned/_epic.md"),
            Path("work/planned/_story.md"),
            Path("work/planned/_template.md"),
            Path("work/current/_epic.md"),
            Path("work/current/_story.md"),
            Path("work/current/_template.md"),
            Path("official/work/archive/items/_epic.md"),
            Path("official/work/archive/items/_story.md"),
            Path("official/work/archive/items/_template.md"),
        )
        for relative in work_templates:
            with self.subTest(file=str(relative)):
                self.assertNotIn("parent", frontmatter_keys(V4_ROOT / relative))
        for relative in work_templates:
            if relative.name == "_template.md":
                continue
            with self.subTest(locale="ko", file=str(relative)):
                self.assertTrue((V4_LOCALE_ROOT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
