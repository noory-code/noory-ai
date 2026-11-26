"""An epic that closes with a review hands that review to its stories (W-00000432)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from python_shell_command import python_command

import test_close_work_record as close_base

STAGE = Path(__file__).resolve().parents[2]
REGISTER = STAGE / "skills" / "stage-work" / "register_work.py"
START = STAGE / "scripts" / "start_work.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"

EPIC = "W-00000001"
STORY = "W-00000002"
NO_REVIEW_AT_CLOSE = "this card runs no review at close"


def run(script: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def card_args(title: str, kind: str, scale: str) -> tuple[str, ...]:
    return (
        "--title",
        title,
        "--kind",
        kind,
        "--scale",
        scale,
        "--scope",
        "src/",
        "--purpose",
        "Deliver the requested outcome.",
        "--success-criterion",
        "The user can observe the requested outcome",
    )


def frontmatter(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines[1 : lines.index("---", 1)]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def approving_reviewer(marker: Path) -> str:
    """A reviewer that leaves `marker` to show it ran, then approves."""

    verdict = json.dumps(
        {
            "criteria": [
                {"criterion": "c", "verdict": "PASS", "method": "ran", "reason": "r"}
            ],
            "approved": True,
        }
    )
    return python_command(
        "import os\n"
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('ran', encoding='utf-8')\n"
        f"Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text({verdict!r}, encoding='utf-8')\n"
    )


class EpicStoryReviewFixture(unittest.TestCase):
    def setUp(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        self.marker = Path(outside.name) / "reviewer-ran"
        project = tempfile.TemporaryDirectory()
        self.addCleanup(project.cleanup)
        self.root = Path(project.name)
        self.stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, self.stage)
        (self.stage / "settings.jsonc").unlink()
        settings = {
            "schema_version": 5,
            "venue_routing": {"fix": "codex", "documentation": "claude"},
            "environment_venues": {"cloud": "claude", "lab": "codex"},
            "review": {
                "strengths": {"standard": approving_reviewer(self.marker)},
                "stages": {"implementation": "standard"},
            },
        }
        (self.stage / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

    def register(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run(REGISTER, self.root, *args)

    def plan_epic_with_story(self, story_kind: str = "fix") -> None:
        epic = self.register(*card_args("Epic", "documentation", "epic"), "--backlog")
        self.assertEqual(0, epic.returncode, epic.stderr)
        story = self.register(
            *card_args("Story", story_kind, "story"), "--backlog", "--parent", EPIC
        )
        self.assertEqual(0, story.returncode, story.stderr)

    def start_epic(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run(START, self.root, EPIC, "--scope", "src/", *args)

    def planned_story(self) -> Path:
        return self.stage / "work/planned" / EPIC / STORY / "_story.md"

    def story(self, item: str = STORY) -> Path:
        return self.stage / "work/current" / EPIC / item / "_story.md"

    def set_planned_story_field(self, key: str, value: str) -> None:
        path = self.planned_story()
        lines = path.read_text(encoding="utf-8").splitlines()
        end = lines.index("---", 1)
        for index in range(1, end):
            if lines[index].partition(":")[0].strip() == key:
                lines[index] = f"{key}: {value}"
                break
        else:
            lines.insert(end, f"{key}: {value}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class StartHandsTheReviewToStoriesTest(EpicStoryReviewFixture):
    def test_a_story_takes_the_review_the_environment_and_its_venue(self):
        self.plan_epic_with_story(story_kind="fix")

        proc = self.start_epic("--environment", "cloud", "--review")

        self.assertEqual(0, proc.returncode, proc.stderr)
        story = frontmatter(self.story())
        self.assertEqual("pending", story["review"])
        self.assertEqual("cloud", story["environment"])
        self.assertEqual("claude", story["venue"])
        text = self.story().read_text(encoding="utf-8")
        self.assertIn("venue: claude\nenvironment: cloud\n", text)

    def test_review_alone_leaves_the_routed_venue_and_adds_no_environment(self):
        self.plan_epic_with_story(story_kind="fix")

        proc = self.start_epic("--review")

        self.assertEqual(0, proc.returncode, proc.stderr)
        story = frontmatter(self.story())
        self.assertEqual("pending", story["review"])
        self.assertEqual("codex", story["venue"])
        self.assertNotIn("environment", story)

    def test_an_epic_without_a_review_leaves_its_stories_without_one(self):
        self.plan_epic_with_story()

        proc = self.start_epic()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("not_required", frontmatter(self.story())["review"])

    def test_a_review_already_on_the_planned_epic_is_handed_over_too(self):
        self.plan_epic_with_story()
        epic = self.stage / "work/planned" / EPIC / "_epic.md"
        text = epic.read_text(encoding="utf-8")
        self.assertIn("review: not_required\n", text)
        epic.write_text(
            text.replace("review: not_required\n", "review: pending\n"), encoding="utf-8"
        )

        proc = self.start_epic()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("pending", frontmatter(self.story())["review"])

    def test_an_action_under_a_story_is_left_as_it_is(self):
        self.plan_epic_with_story()
        action = self.register(
            *card_args("Action", "fix", "action"), "--backlog", "--parent", STORY
        )
        self.assertEqual(0, action.returncode, action.stderr)

        proc = self.start_epic("--environment", "cloud", "--review")

        self.assertEqual(0, proc.returncode, proc.stderr)
        fields = frontmatter(self.stage / "work/current" / EPIC / STORY / "W-00000003.md")
        self.assertEqual("not_required", fields["review"])
        self.assertNotIn("environment", fields)

    def test_a_story_that_names_another_venue_refuses_the_start(self):
        self.plan_epic_with_story()
        self.set_planned_story_field("venue", "codex")

        proc = self.start_epic("--environment", "cloud", "--review")

        self.assertEqual(1, proc.returncode, proc.stdout)
        self.assertIn(f"refusing: {STORY}: the story names venue `codex`", proc.stderr)
        self.assertIn("environment `cloud` runs venue `claude`", proc.stderr)
        self.assertTrue(self.planned_story().exists())
        self.assertFalse((self.stage / "work/current" / EPIC).exists())
        self.assertEqual("codex", frontmatter(self.planned_story())["venue"])

    def test_a_story_that_names_another_environment_refuses_the_start(self):
        self.plan_epic_with_story()
        self.set_planned_story_field("environment", "lab")

        proc = self.start_epic("--environment", "cloud", "--review")

        self.assertEqual(1, proc.returncode, proc.stdout)
        self.assertIn(f"refusing: {STORY}: the story names environment `lab`", proc.stderr)
        self.assertFalse((self.stage / "work/current" / EPIC).exists())

    def test_a_rejected_story_is_not_given_a_review(self):
        self.plan_epic_with_story()
        self.set_planned_story_field("status", "rejected")
        self.set_planned_story_field("venue", "codex")

        proc = self.start_epic("--environment", "cloud", "--review")

        self.assertEqual(0, proc.returncode, proc.stderr)
        story = frontmatter(self.story())
        self.assertEqual("rejected", story["status"])
        self.assertEqual("not_required", story["review"])
        self.assertNotIn("environment", story)


class RegisterHandsTheReviewToANewStoryTest(EpicStoryReviewFixture):
    def start_epic_alone(self, *args: str) -> None:
        epic = self.register(*card_args("Epic", "documentation", "epic"), "--backlog")
        self.assertEqual(0, epic.returncode, epic.stderr)
        proc = self.start_epic(*args)
        self.assertEqual(0, proc.returncode, proc.stderr)

    def register_story(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self.register(*card_args("Story", "fix", "story"), "--parent", EPIC, *args)

    def test_a_story_added_to_a_started_epic_takes_the_same_three(self):
        self.start_epic_alone("--environment", "cloud", "--review")

        proc = self.register_story()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(f"review: pending inherited from the epic {EPIC}", proc.stdout)
        story = frontmatter(self.story())
        self.assertEqual("pending", story["review"])
        self.assertEqual("cloud", story["environment"])
        self.assertEqual("claude", story["venue"])

    def test_review_alone_gives_the_new_story_the_review_and_the_routed_venue(self):
        self.start_epic_alone("--review")

        proc = self.register_story()

        self.assertEqual(0, proc.returncode, proc.stderr)
        story = frontmatter(self.story())
        self.assertEqual("pending", story["review"])
        self.assertEqual("codex", story["venue"])
        self.assertNotIn("environment", story)

    def test_an_epic_without_a_review_gives_the_new_story_none(self):
        self.start_epic_alone()

        proc = self.register_story()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("not_required", frontmatter(self.story())["review"])

    def test_a_venue_or_an_environment_that_differs_from_the_epic_is_refused(self):
        self.start_epic_alone("--environment", "cloud", "--review")
        cases = {
            "venue": (("--venue", "codex"), "--venue `codex` differs from the venue `claude`"),
            "environment": (
                ("--environment", "lab", "--review"),
                "--environment `lab` differs from the environment `cloud`",
            ),
        }

        for label, (extra, expected) in cases.items():
            with self.subTest(case=label):
                proc = self.register_story(*extra)

                self.assertEqual(1, proc.returncode, proc.stdout)
                self.assertIn(expected, proc.stderr)
                self.assertFalse(self.story().exists())


class TheStoryClosesWithItsReviewTest(EpicStoryReviewFixture):
    def test_review_commit_is_accepted_and_the_reviewer_runs(self):
        self.plan_epic_with_story(story_kind="fix")
        started = self.start_epic("--environment", "cloud", "--review")
        self.assertEqual(0, started.returncode, started.stderr)
        card = self.story()
        text = card.read_text(encoding="utf-8")
        text = text.replace("retrospective: pending\n", "retrospective: completed\n")
        text = text.replace("retrospective_ref:\n", "retrospective_ref: R-00000002\n")
        card.write_text(text, encoding="utf-8")
        retrospectives = self.stage / "work/retrospectives"
        retrospectives.mkdir(parents=True, exist_ok=True)
        (retrospectives / "R-00000002.md").write_text(
            f"---\nid: R-00000002\nwork_item: {STORY}\n---\n", encoding="utf-8"
        )
        (self.root / "src").mkdir()
        (self.root / "src/app.py").write_text("VALUE = 1\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "add", "-A", "-f"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Stage Test",
                "-c",
                "user.email=stage-test@example.com",
                "commit",
                "-q",
                "-m",
                "test: the story's code",
            ],
            cwd=self.root,
            check=True,
        )

        proc = close_base.run(
            self.root,
            STORY,
            "--check",
            python_command("print('ok')"),
            "--promotion",
            "not_applicable",
            "--review-commit",
            "HEAD",
        )

        self.assertNotIn(NO_REVIEW_AT_CLOSE, proc.stderr)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue(self.marker.exists(), "the configured reviewer did not run")
        closed = frontmatter(card)
        self.assertEqual("completed", closed["status"])
        self.assertEqual("passed", closed["review"])


if __name__ == "__main__":
    unittest.main()
