from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-work" / "register_work.py"
SKILL = CLI.parent / "SKILL.md"
START_CLI = Path(__file__).resolve().parents[1] / "start_work.py"

ACTIVE = (
    "# Active Work\n\n"
    "| Work | Kind | Venue | Purpose | Status | Owner | Item |\n"
    "|---|---|---|---|---|---|---|\n"
)

BACKLOG_WITH_TRAILING_SECTION = (
    "# Backlog Index\n\n"
    "## Current backlog\n\n"
    "| ID | Title | Kind | Status | Priority | Parent | Item |\n"
    "|---|---|---|---|---|---|---|\n"
    "| W-00000001 | Existing | chore | captured | low |  | "
    "[W-00000001.md](W-00000001.md) |\n\n"
    "## Status values\n\n"
    "- `captured`: captured but not yet organized.\n"
)


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    if "--scale" not in args and "--count-open-milestones" not in args:
        args = ("--scale", "story", *args)
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args], capture_output=True, text=True
    )


def run_start(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(START_CLI), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def work_path(
    root: Path,
    lifecycle: str,
    item_id: str,
    scale: str,
    parent_id: str = "",
) -> Path:
    lifecycle_root = root / ".stage" / "work" / lifecycle
    if scale == "epic":
        return lifecycle_root / item_id / "_epic.md"
    if scale == "story":
        return lifecycle_root / item_id / "_story.md"
    if scale == "action" and parent_id:
        return lifecycle_root / parent_id / f"{item_id}.md"
    raise ValueError(f"unsupported work hierarchy: scale={scale!r}, parent={parent_id!r}")


def story_path(root: Path, lifecycle: str, item_id: str) -> Path:
    return work_path(root, lifecycle, item_id, "story")


def question_headings(text: str) -> tuple[str, ...]:
    return tuple(
        line
        for line in text.splitlines()
        if line.startswith("## ") or line.startswith("### ")
    )


def frontmatter_keys(text: str) -> tuple[str, ...]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return ()
    end = lines.index("---", 1)
    return tuple(line.partition(":")[0] for line in lines[1:end] if not line.startswith(" "))


class RegisterWorkTest(unittest.TestCase):
    def make(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/work/current").mkdir(parents=True)
        (root / ".stage/work/planned").mkdir(parents=True)
        (root / ".stage/official/work/archive/items").mkdir(parents=True)
        (root / ".stage/work/active.md").write_text(ACTIVE, encoding="utf-8")
        (root / ".stage/settings.json").write_text(
            '{"schema_version": 5}\n', encoding="utf-8"
        )
        return tmp, root

    def declare_routing(self, root: Path) -> None:
        (root / ".stage/settings.json").write_text(
            '{"schema_version": 5, "venue_routing": '
            '{"design": "claude", "development": "codex", "feature": "split"}}',
            encoding="utf-8",
        )

    def write_decision(
        self, root: Path, *, decision_id: str = "DE-0009", status: str = "decided",
        authorizes: str = "venue_exception",
    ) -> None:
        decisions = root / ".stage/decisions/pending"
        decisions.mkdir(parents=True, exist_ok=True)
        lines = [f"---", f"id: {decision_id}", "work_item: W-00000001", f"status: {status}"]
        if authorizes:
            lines.append(f"authorizes: {authorizes}")
        lines += ["---", f"# {decision_id} Exception", ""]
        (decisions / f"{decision_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def test_venue_derived_from_declared_routing(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(root, "--title", "T", "--kind", "design", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("venue derived from venue_routing: design -> claude", result.stdout)
            item = story_path(root, "current", "W-00000001").read_text(encoding="utf-8")
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")

        self.assertIn("venue: claude", item)
        self.assertIn("| claude |", active)

    def test_unrouted_kind_keeps_empty_venue(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(root, "--title", "T", "--kind", "chore", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)

        self.assertNotIn("derived", result.stdout)
        self.assertNotIn("policy exception", result.stdout)

    def test_contradicting_venue_without_decision_is_refused(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude",
            )
            created = story_path(root, "current", "W-00000001").exists()

        self.assertEqual(1, result.returncode)
        self.assertIn("--decision", result.stderr)
        self.assertFalse(created)

    def test_contradicting_venue_with_valid_decision_registers(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            self.write_decision(root)
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            item = story_path(root, "current", "W-00000001").read_text(encoding="utf-8")

        self.assertIn("venue: claude", item)
        self.assertIn("decision_refs: DE-0009", item)

    def test_open_or_non_authorizing_decision_is_refused(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            self.write_decision(root, status="open")
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(1, result.returncode)

            self.write_decision(root, authorizes="")
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(1, result.returncode)

            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-9999",
            )
            self.assertEqual(1, result.returncode)

    def test_split_kind_single_item_is_refused_with_resolution(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(root, "--title", "T", "--kind", "feature", "--scope", "src")
            created = story_path(root, "current", "W-00000001").exists()

        self.assertEqual(1, result.returncode)
        self.assertIn("split", result.stderr)
        self.assertIn("hierarchy", result.stderr)
        self.assertFalse(created)

    def test_split_kind_with_valid_decision_registers_single_item(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            self.write_decision(root)
            result = run(
                root, "--title", "T", "--kind", "feature", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            item = story_path(root, "current", "W-00000001").read_text(encoding="utf-8")

        self.assertIn("decision_refs: DE-0009", item)

    def test_no_policy_keeps_current_behavior(self):
        tmp, root = self.make()
        with tmp:
            result = run(root, "--title", "T", "--kind", "design", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)

        self.assertNotIn("derived", result.stdout)
        self.assertNotIn("policy exception", result.stdout)

    def test_auto_id_and_link_row(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "--title", "Do a thing", "--kind", "feature", "--scope", "stage/x", "--venue", "claude")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = story_path(root, "current", "W-00000001")
            self.assertTrue(item.exists())
            body = item.read_text(encoding="utf-8")
            self.assertIn("id: W-00000001", body)
            self.assertIn("kind: feature", body)
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")
            self.assertIn(
                "[current/W-00000001/_story.md](current/W-00000001/_story.md)",
                active,
            )

    def test_top_level_action_is_refused_with_story_first_guidance(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                root,
                "--scale",
                "action",
                "--title",
                "Do a thing",
                "--kind",
                "chore",
                "--scope",
                "stage/x",
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("story", proc.stderr.lower())
        self.assertIn("first", proc.stderr.lower())
        self.assertEqual([], list((root / ".stage/work/current").glob("W-*")))

    def test_registration_without_scale_is_refused(self):
        tmp, root = self.make()
        with tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--project-root",
                    str(root),
                    "--title",
                    "Do a thing",
                    "--kind",
                    "chore",
                    "--scope",
                    "stage/x",
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(0, proc.returncode)
        self.assertIn("--scale", proc.stderr)
        self.assertEqual([], list((root / ".stage/work/current").glob("W-*")))

    def test_planned_story_can_be_registered_below_planned_epic(self):
        tmp, root = self.make()
        with tmp:
            epic = run(
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Reliable driver",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000001",
            )
            story = run(
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--title",
                "Review evidence",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000002",
            )
            story_path = (
                root / ".stage/work/planned/W-00000001/W-00000002/_story.md"
            )
            body = story_path.read_text(encoding="utf-8")

        self.assertEqual(0, epic.returncode, epic.stderr)
        self.assertEqual(0, story.returncode, story.stderr)
        self.assertNotIn("\nparent:", body)

    def test_nested_work_cannot_claim_a_milestone(self):
        tmp, root = self.make()
        with tmp:
            epic = run(
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Reliable driver",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000001",
            )
            story = run(
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--milestone",
                "M-00000001",
                "--title",
                "Review evidence",
                "--kind",
                "development",
                "--scope",
                "",
            )

        self.assertEqual(0, epic.returncode, epic.stderr)
        self.assertEqual(1, story.returncode)
        self.assertIn("top-level", story.stderr)

    def test_autonomous_registration_requires_acceptance(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                root,
                "--title",
                "Autonomous",
                "--kind",
                "chore",
                "--scope",
                "src",
                "--autonomous",
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("autonomous", proc.stderr)
        self.assertIn("acceptance", proc.stderr)
        self.assertFalse(story_path(root, "current", "W-00000001").exists())

    def test_current_registration_refuses_more_than_one_purpose_sentence(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                root,
                "--title",
                "Focused purpose",
                "--kind",
                "chore",
                "--scope",
                "src",
                "--purpose",
                "Deliver one outcome. Repeat the parent outcome.",
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("purpose must be one sentence", proc.stderr)
        self.assertFalse(story_path(root, "current", "W-00000001").exists())

    def test_planned_registration_refuses_more_than_one_purpose_sentence(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                root,
                "--backlog",
                "--title",
                "Focused purpose",
                "--kind",
                "chore",
                "--scope",
                "src",
                "--purpose",
                "Deliver one outcome! Repeat the parent outcome.",
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("purpose must be one sentence", proc.stderr)
        self.assertFalse(story_path(root, "planned", "W-00000001").exists())

    def test_registration_accepts_one_purpose_sentence_without_terminal_punctuation(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                root,
                "--title",
                "Focused purpose",
                "--kind",
                "chore",
                "--scope",
                "src",
                "--purpose",
                "Deliver one outcome",
            )
            body = story_path(root, "current", "W-00000001").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("## Purpose\n\nDeliver one outcome\n", body)

    def test_registration_writes_autonomous_acceptance_sequence(self):
        tmp, root = self.make()
        with tmp:
            proc = run(
                root,
                "--title",
                "Autonomous",
                "--kind",
                "chore",
                "--scope",
                "src",
                "--autonomous",
                "--acceptance",
                'python3 -c "print(1)"',
                "--acceptance",
                "python3 stage/scripts/audit_stage.py",
            )
            body = story_path(root, "current", "W-00000001").read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("autonomous: true", body)
        self.assertIn("acceptance:\n", body)
        self.assertIn('  - "python3 -c \\"print(1)\\""', body)
        self.assertIn('  - "python3 stage/scripts/audit_stage.py"', body)

    def test_skill_requires_a_clean_audit_after_hierarchy_registration(self):
        skill = SKILL.read_text(encoding="utf-8")

        self.assertNotIn("Current audit boundary", skill)
        self.assertNotIn("BACKLOG003", skill)
        self.assertNotIn("WORK002", skill)
        self.assertNotIn("INDEX003", skill)
        self.assertNotIn("INDEX004", skill)
        self.assertIn("expect errors=0", skill)

    def test_skill_counts_affected_places_before_registration_confirmation(self):
        skill = SKILL.read_text(encoding="utf-8")

        count_step = skill.index("## Count affected places before drafting")
        confirm_step = skill.index("## Confirm, then register")

        self.assertLess(count_step, confirm_step)
        for check in (
            "Entry paths and actors",
            "Lifecycle and state changes",
            "Replaced or removed responsibilities",
            "Results, failures, and durable evidence",
        ):
            self.assertIn(f"| {check} |", skill)
        self.assertIn("record the count", skill)
        self.assertIn("name what was checked", skill)
        self.assertIn("Show the human the affected-place count", skill)

    def test_increments_past_max_including_archive(self):
        tmp, root = self.make()
        with tmp:
            (root / ".stage/official/work/archive/items/W-00000005.md").write_text("---\nid: W-00000005\n---\n", encoding="utf-8")
            run(root, "--title", "A", "--kind", "chore", "--scope", "x")
            self.assertTrue(story_path(root, "current", "W-00000006").exists())

    def test_reruns_reconcile_index_not_duplicate(self):
        tmp, root = self.make()
        with tmp:
            run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000001")
            # Drop the row, then a re-run with same id must re-add exactly one.
            (root / ".stage/work/active.md").write_text(ACTIVE, encoding="utf-8")
            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000001")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")
            self.assertEqual(active.count("[current/W-00000001/_story.md]"), 1)

    def test_active_row_is_inserted_before_trailing_sections(self):
        tmp, root = self.make()
        with tmp:
            active_path = root / ".stage/work/active.md"
            active_path.write_text(
                ACTIVE + "\n## Status values\n\n- `active`: work in progress.\n",
                encoding="utf-8",
            )

            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            active = active_path.read_text(encoding="utf-8")

        self.assertLess(active.index("| W-00000001 |"), active.index("## Status values"))

    def test_backlog_row_is_inserted_after_empty_table_header(self):
        tmp, root = self.make()
        with tmp:
            backlog = root / ".stage/work/planned"
            backlog.mkdir(parents=True, exist_ok=True)
            empty_index = BACKLOG_WITH_TRAILING_SECTION.replace(
                "| W-00000001 | Existing | chore | captured | low |  | "
                "[W-00000001.md](W-00000001.md) |\n",
                "",
            )
            index_path = backlog / "index.md"
            index_path.write_text(empty_index, encoding="utf-8")

            proc = run(
                root,
                "--backlog",
                "--title",
                "First work",
                "--kind",
                "fix",
                "--scope",
                "",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            index = index_path.read_text(encoding="utf-8")

        separator = index.index("|---|---|---|---|---|---|---|")
        new_row = index.index("| W-00000001 | First work |")
        trailing_section = index.index("## Status values")
        self.assertLess(separator, new_row)
        self.assertLess(new_row, trailing_section)

    def test_backlog_row_is_inserted_before_trailing_sections(self):
        tmp, root = self.make()
        with tmp:
            backlog = root / ".stage/work/planned"
            backlog.mkdir(parents=True, exist_ok=True)
            (backlog / "W-00000001.md").write_text(
                "---\nid: W-00000001\n---\n", encoding="utf-8"
            )
            index_path = backlog / "index.md"
            index_path.write_text(BACKLOG_WITH_TRAILING_SECTION, encoding="utf-8")

            proc = run(
                root,
                "--backlog",
                "--title",
                "New work",
                "--kind",
                "fix",
                "--scope",
                "",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            index = index_path.read_text(encoding="utf-8")

        existing_row = index.index("| W-00000001 | Existing |")
        new_row = index.index("| W-00000002 | New work |")
        trailing_section = index.index("## Status values")
        self.assertLess(existing_row, new_row)
        self.assertLess(new_row, trailing_section)

    def test_starting_legacy_planned_card_adds_review_field(self):
        tmp, root = self.make()
        with tmp:
            planned = root / ".stage/work/planned/W-00000001.md"
            planned.write_text(
                """---
id: W-00000001
title: Planned fix
kind: fix
venue: codex
parent:
milestone: M-00000001
priority:
autonomous: false
acceptance: []
status: captured
---

# W-00000001 Planned fix

## Purpose
""",
                encoding="utf-8",
            )

            proc = run_start(root, "W-00000001", "--scope", "stage/x")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("review: not_required", item)
        self.assertNotIn("\nparent:", item)
        self.assertNotIn("\npriority:", item)
        self.assertLess(item.index("venue:"), item.index("milestone:"))
        self.assertLess(item.index("milestone:"), item.index("autonomous:"))

    def test_starting_legacy_child_preserves_valued_parent(self):
        tmp, root = self.make()
        with tmp:
            planned = root / ".stage/work/planned/W-00000002.md"
            planned.write_text(
                """---
id: W-00000002
title: Planned child
kind: fix
venue: codex
parent: W-00000001
priority:
autonomous: false
acceptance: []
status: captured
---

# W-00000002 Planned child

## Purpose
""",
                encoding="utf-8",
            )

            proc = run_start(root, "W-00000002", "--scope", "stage/x")
            item = (root / ".stage/work/current/W-00000002.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("\nparent: W-00000001\n", item)

    def test_planned_and_direct_current_registration_ask_the_same_questions(self):
        for scale in ("epic", "story", "action"):
            with self.subTest(scale=scale):
                tmp, root = self.make()
                with tmp:
                    parent_id = ""
                    if scale == "action":
                        parent_id = "W-00000001"
                        parent = run(
                            root,
                            "--backlog",
                            "--scale",
                            "story",
                            "--title",
                            "Planned parent",
                            "--kind",
                            "chore",
                            "--scope",
                            "stage/x",
                            "--id",
                            parent_id,
                        )
                        self.assertEqual(0, parent.returncode, parent.stderr)

                    planned_id = "W-00000002" if parent_id else "W-00000001"
                    direct_id = "W-00000003" if parent_id else "W-00000002"
                    parent_args = ("--parent", parent_id) if parent_id else ()
                    planned = run(
                        root,
                        "--backlog",
                        "--scale",
                        scale,
                        *parent_args,
                        "--title",
                        "Planned path",
                        "--kind",
                        "chore",
                        "--scope",
                        "stage/x",
                        "--id",
                        planned_id,
                    )
                    self.assertEqual(0, planned.returncode, planned.stderr)
                    start_id = parent_id or planned_id
                    started = run_start(root, start_id, "--scope", "stage/x")
                    self.assertEqual(0, started.returncode, started.stderr)
                    direct = run(
                        root,
                        "--scale",
                        scale,
                        *parent_args,
                        "--title",
                        "Direct path",
                        "--kind",
                        "chore",
                        "--scope",
                        "stage/x",
                        "--id",
                        direct_id,
                    )
                    self.assertEqual(0, direct.returncode, direct.stderr)

                    started_text = work_path(
                        root, "current", planned_id, scale, parent_id
                    ).read_text(encoding="utf-8")
                    direct_text = work_path(
                        root, "current", direct_id, scale, parent_id
                    ).read_text(encoding="utf-8")

                self.assertEqual(
                    question_headings(direct_text), question_headings(started_text)
                )
                self.assertEqual(
                    frontmatter_keys(direct_text), frontmatter_keys(started_text)
                )
                self.assertIn("## Related truth", question_headings(started_text))
                self.assertIn("### Included", question_headings(direct_text))
                self.assertIn("### Excluded", question_headings(direct_text))

    def test_planned_hierarchy_records_keep_their_declared_scopes_when_started(self):
        tmp, root = self.make()
        with tmp:
            epic = run(
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Release",
                "--kind",
                "development",
                "--scope",
                "epic-owned",
                "--id",
                "W-00000001",
            )
            story = run(
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--title",
                "Driver",
                "--kind",
                "development",
                "--scope",
                "story-owned",
                "--id",
                "W-00000002",
            )
            action = run(
                root,
                "--backlog",
                "--scale",
                "action",
                "--parent",
                "W-00000002",
                "--title",
                "Selection",
                "--kind",
                "development",
                "--scope",
                "action-owned",
                "--id",
                "W-00000003",
            )
            self.assertEqual(0, epic.returncode, epic.stderr)
            self.assertEqual(0, story.returncode, story.stderr)
            self.assertEqual(0, action.returncode, action.stderr)

            started = run_start(
                root,
                "W-00000001",
                "--scope",
                "epic-start-scope",
            )
            current = root / ".stage/work/current/W-00000001"
            epic_text = (current / "_epic.md").read_text(encoding="utf-8")
            story_text = (
                current / "W-00000002/_story.md"
            ).read_text(encoding="utf-8")
            action_text = (
                current / "W-00000002/W-00000003.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, started.returncode, started.stderr)
        self.assertIn("scope: epic-start-scope", epic_text)
        self.assertIn("scope: story-owned", story_text)
        self.assertIn("scope: action-owned", action_text)

    def test_starting_hierarchy_refuses_to_silently_activate_deferred_descendant(self):
        tmp, root = self.make()
        with tmp:
            run(
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Release",
                "--kind",
                "development",
                "--scope",
                "epic-owned",
                "--id",
                "W-00000001",
            )
            run(
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--title",
                "Deferred story",
                "--kind",
                "development",
                "--scope",
                "story-owned",
                "--id",
                "W-00000002",
            )
            story = root / ".stage/work/planned/W-00000001/W-00000002/_story.md"
            story.write_text(
                story.read_text(encoding="utf-8").replace(
                    "status: captured", "status: deferred"
                ),
                encoding="utf-8",
            )

            started = run_start(
                root,
                "W-00000001",
                "--scope",
                "epic-owned",
            )
            deferred_still_planned = (
                root / ".stage/work/planned/W-00000001/W-00000002/_story.md"
            ).is_file()
            current_created = (
                root / ".stage/work/current/W-00000001"
            ).exists()

        self.assertEqual(1, started.returncode)
        self.assertIn("deferred", started.stderr)
        self.assertTrue(deferred_still_planned)
        self.assertFalse(current_created)

    def test_rejected_story_keeps_its_actions_rejected_when_tree_starts(self):
        tmp, root = self.make()
        with tmp:
            run(
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Release",
                "--kind",
                "development",
                "--scope",
                "epic-owned",
                "--id",
                "W-00000001",
            )
            run(
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--title",
                "Rejected story",
                "--kind",
                "development",
                "--scope",
                "story-owned",
                "--id",
                "W-00000002",
            )
            run(
                root,
                "--backlog",
                "--scale",
                "action",
                "--parent",
                "W-00000002",
                "--title",
                "Old action",
                "--kind",
                "development",
                "--scope",
                "action-owned",
                "--id",
                "W-00000003",
            )
            story = root / ".stage/work/planned/W-00000001/W-00000002/_story.md"
            story.write_text(
                story.read_text(encoding="utf-8").replace(
                    "status: captured", "status: rejected"
                ),
                encoding="utf-8",
            )

            started = run_start(
                root,
                "W-00000001",
                "--scope",
                "epic-owned",
            )
            current = root / ".stage/work/current/W-00000001/W-00000002"
            story_text = (current / "_story.md").read_text(encoding="utf-8")
            action_text = (current / "W-00000003.md").read_text(encoding="utf-8")

        self.assertEqual(0, started.returncode, started.stderr)
        self.assertIn("status: rejected", story_text)
        self.assertIn("status: rejected", action_text)

    def test_refuses_archived_id(self):
        tmp, root = self.make()
        with tmp:
            (root / ".stage/official/work/archive/items/W-00000003.md").write_text("---\nid: W-00000003\n---\n", encoding="utf-8")
            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000003")
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(story_path(root, "current", "W-00000003").exists())


if __name__ == "__main__":
    unittest.main()
