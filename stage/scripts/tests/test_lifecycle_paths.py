import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import lifecycle_paths


class LifecyclePathsTests(unittest.TestCase):
    def test_work_template_contract_names_each_hierarchy_scale(self):
        paths = lifecycle_paths.v4_lifecycle_paths()
        self.assertEqual(
            "project-stage/work/planned/_epic.md",
            paths.planned_epic_template,
        )
        self.assertEqual(
            "project-stage/work/planned/_story.md",
            paths.planned_story_template,
        )
        self.assertEqual(
            "project-stage/work/planned/_template.md",
            paths.planned_action_template,
        )
        self.assertEqual(
            "project-stage/work/current/_epic.md",
            paths.current_epic_template,
        )
        self.assertEqual(
            "project-stage/work/current/_story.md",
            paths.current_story_template,
        )
        self.assertEqual(
            "project-stage/work/current/_template.md",
            paths.current_action_template,
        )
        self.assertEqual(
            "project-stage/official/work/archive/items/_epic.md",
            paths.archive_epic_template,
        )
        self.assertEqual(
            "project-stage/official/work/archive/items/_story.md",
            paths.archive_story_template,
        )
        self.assertEqual(
            "project-stage/official/work/archive/items/_template.md",
            paths.archive_action_template,
        )


if __name__ == "__main__":
    unittest.main()
