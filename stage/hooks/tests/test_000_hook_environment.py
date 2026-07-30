from __future__ import annotations

import os
import unittest

from hook_test_environment import (
    sanitize_current_hook_environment,
    sanitized_hook_environment,
)


sanitize_current_hook_environment()


class HookTestEnvironmentTest(unittest.TestCase):
    def test_bootstrap_sanitizes_the_current_test_process(self):
        self.assertNotIn("CLAUDE_PROJECT_DIR", os.environ)
        self.assertNotIn("PROJECT_ROOT", os.environ)
        self.assertFalse(any(key.startswith("STAGE_WORK_") for key in os.environ))

    def test_removes_host_project_and_stage_work_bindings(self):
        source = {
            "CLAUDE_PROJECT_DIR": "/wrong/claude-project",
            "PROJECT_ROOT": "/wrong/project-root",
            "STAGE_WORK_ITEM": "W-wrong",
            "STAGE_WORK_ITEM_PATH": "/wrong/item.md",
            "STAGE_WORK_ITEM_ANCESTOR_PATHS": '["/wrong/ancestor.md"]',
            "STAGE_WORK_LOG_PATH": "/wrong/log.md",
            "STAGE_PROJECT_ROOT": "/fixture/project",
            "PATH": "/usr/bin",
        }

        self.assertEqual(
            {
                "STAGE_PROJECT_ROOT": "/fixture/project",
                "PATH": "/usr/bin",
            },
            sanitized_hook_environment(source),
        )


if __name__ == "__main__":
    unittest.main()
