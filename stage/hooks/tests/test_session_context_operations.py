"""Session-start inventory of project-owned operation files."""

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


V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"


class ProjectOperationsContextTest(unittest.TestCase):
    def make_fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")
        operations = root / ".stage" / "operations"
        for entry in operations.iterdir():
            if entry.is_file():
                entry.unlink()
        return tmp, root, operations

    def test_session_lists_every_operation_file_without_copying_bodies(self):
        tmp, root, operations = self.make_fixture()
        with tmp:
            (operations / "alpha.md").write_text(
                "ALPHA BODY MUST NOT ENTER THE SESSION\n", encoding="utf-8"
            )
            (operations / "middle.md").write_text(
                "MIDDLE BODY MUST NOT ENTER THE SESSION\n", encoding="utf-8"
            )

            before = stage_context.session_context(root)

            self.assertIn("### Project operations (project-defined)", before)
            self.assertIn("- `.stage/operations/alpha.md`", before)
            self.assertIn("- `.stage/operations/middle.md`", before)
            self.assertNotIn("ALPHA BODY MUST NOT ENTER THE SESSION", before)
            self.assertNotIn("MIDDLE BODY MUST NOT ENTER THE SESSION", before)

            (operations / "z-last.md").write_text(
                "NEW BODY MUST NOT ENTER THE SESSION\n", encoding="utf-8"
            )
            after = stage_context.session_context(root)

        added_line = "\n- `.stage/operations/z-last.md`"
        self.assertIn(added_line, after)
        self.assertNotIn("NEW BODY MUST NOT ENTER THE SESSION", after)
        self.assertEqual(after.replace(added_line, ""), before)


if __name__ == "__main__":
    unittest.main()
