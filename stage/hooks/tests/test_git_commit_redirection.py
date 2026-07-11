# A shell redirection after `git commit` (`2>&1`, `> out`, a piped `| tail`) must
# not be read as a commit pathspec — that once produced false registration-gate
# denials on ordinary commit invocations. Real pathspecs must still be caught.
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

_HOOKS = Path(__file__).resolve().parents[1]
for _name in ("stage_paths", "stage_shell", "stage_git"):
    _spec = importlib.util.spec_from_file_location(_name, _HOOKS / f"{_name}.py")
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_name] = _mod
    assert _spec.loader is not None
    _spec.loader.exec_module(_mod)
stage_git = sys.modules["stage_git"]

WS = Path(".").resolve()


class GitCommitRedirectionTest(unittest.TestCase):
    def paths(self, command: str) -> list[str]:
        return stage_git.git_commit_pathspec_files(command, WS)

    def test_redirection_is_not_a_pathspec(self):
        self.assertEqual(self.paths("git commit -F /tmp/msg.txt 2>&1 | tail -5"), [])
        self.assertEqual(self.paths("git commit -m \"msg\" 2>&1"), [])
        self.assertEqual(self.paths("git commit -am \"x\" > out.log"), [])

    def test_real_pathspec_still_detected(self):
        self.assertEqual(self.paths("git commit -- a.py b.py"), ["a.py", "b.py"])

    def test_redirect_target_after_pathspec_excluded(self):
        # The pathspec before the redirect is kept; the redirect target is not.
        self.assertEqual(self.paths("git commit -- a.py > out.txt"), ["a.py"])


if __name__ == "__main__":
    unittest.main()
