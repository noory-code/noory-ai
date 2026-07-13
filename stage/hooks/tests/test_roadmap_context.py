"""Schema-v4 active-milestone session view."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_context  # noqa: E402


V3_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "project-stage"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"


class ActiveMilestoneContextTest(unittest.TestCase):
    def make_fixture(self, template_root: Path):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(template_root, root / ".stage")
        return tmp, root

    def test_v4_session_renders_active_milestone_from_chain(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            (stage_root / "roadmap/themes/TH-00000001.md").write_text(
                "---\nid: TH-00000001\ndecision_refs:\n---\n"
                "# TH-00000001 Delivery reliability\n",
                encoding="utf-8",
            )
            (stage_root / "roadmap/milestones/M-00000002.md").write_text(
                "---\nid: M-00000002\ntheme: TH-00000001\n"
                "decision_refs: DE-00000001\n---\n"
                "# M-00000002 Stable release\n",
                encoding="utf-8",
            )
            (stage_root / "decisions/pending/DE-00000001.md").write_text(
                "---\nid: DE-00000001\nroadmap_item: M-00000002\n"
                "status: decided\ntransition: pursuit\npredecessor:\nsupersedes:\n---\n"
                "# DE-00000001 Pursue stable release\n",
                encoding="utf-8",
            )

            context = stage_context.session_context(root)

        self.assertIn("### Active milestones (decision-derived)", context)
        self.assertIn("| Milestone | Theme | Title |", context)
        self.assertIn(
            "| [M-00000002](roadmap/milestones/M-00000002.md) | "
            "TH-00000001 | Stable release |",
            context,
        )
        self.assertNotIn("Open cards", context)

    def test_v4_empty_active_milestone_table_is_explicit(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            context = stage_context.session_context(root)

        self.assertIn("### Active milestones (decision-derived)", context)
        self.assertIn("| — | — | None |", context)

    def test_v3_session_has_no_active_milestone_table(self):
        tmp, root = self.make_fixture(V3_TEMPLATE_ROOT)
        with tmp:
            context = stage_context.session_context(root)

        self.assertNotIn("Active milestones (decision-derived)", context)


if __name__ == "__main__":
    unittest.main()
