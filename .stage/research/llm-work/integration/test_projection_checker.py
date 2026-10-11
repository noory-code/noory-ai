"""A nonempty history from another criterion or project is insufficient."""
import unittest

from verify_integration import projections_include_refs


class ProjectionCheckerTest(unittest.TestCase):
    def test_applied_ref_and_project_must_match(self):
        ref = "distill:CR-aaaaaaaaaaaa@2"
        projection = {"producer": "distill", "history": {
            "project": "test/demo-app", "versions": [{"ref": ref}]}}
        self.assertTrue(projections_include_refs([projection], [ref]))
        self.assertFalse(projections_include_refs([projection], ["distill:CR-bbbbbbbbbbbb@2"]))
        projection["history"]["project"] = "other/project"
        self.assertFalse(projections_include_refs([projection], [ref]))


if __name__ == "__main__":
    unittest.main()
