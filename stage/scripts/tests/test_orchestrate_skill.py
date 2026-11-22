"""The stage-orchestrate skill owns the cloud session procedure; stage-handoff points to it."""

from __future__ import annotations

import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2] / "skills"


def read(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")


class OrchestrateSkillTest(unittest.TestCase):
    def test_the_skill_names_itself_and_both_generated_briefs(self) -> None:
        text = read("stage-orchestrate")

        self.assertTrue(text.startswith("---\nname: stage-orchestrate\ndescription: "))
        self.assertIn("subsession_brief.py --project-root . <W-id>", text)
        self.assertIn("--role verify", text)
        self.assertIn("## Take over from the records", text)
        self.assertIn("`list_sessions`", text)
        self.assertIn("waiting_confirmations:", text)

    def test_handoff_keeps_no_copy_of_the_sub_session_procedure(self) -> None:
        text = read("stage-handoff")

        self.assertIn("see `stage-orchestrate`", text)
        for moved in ("subsession_brief.py", "--reserve-for", "split_when", "start_work.py <W-id>"):
            self.assertNotIn(moved, text)

    def test_the_driver_skill_states_its_boundary_with_the_orchestrator(self) -> None:
        self.assertIn("`stage-orchestrate`", read("stage-drive"))


if __name__ == "__main__":
    unittest.main()
