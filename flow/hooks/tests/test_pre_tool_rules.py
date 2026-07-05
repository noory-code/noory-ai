#!/usr/bin/env python3
"""PreToolUse rule pure-helper regression test (stdlib unittest, 0 dependencies).

Targets:
- Rule 5 no-shared-branch-merge: targets_shared_branch — catches the shared branch even when a flag
  (-f/--force/--no-ff) or refspec (HEAD:main) sits between push/merge and the branch, while
  partial-match false positives like feature-main/main-x pass.
- Rule 2 no-commit-without-retro: uses_no_verify — detects both --no-verify and the shorthand -n
  (including combined -nm/-an).

Run: cd flow/hooks && python3 -m unittest tests.test_pre_tool_rules
"""
from __future__ import annotations

import os
import sys
import unittest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402


class TestSharedBranch(unittest.TestCase):
    """Rule 5 — detect push/merge to a shared branch (develop/main/master/release/*)."""

    SHARED = [
        "git push origin main",
        "git push -f origin main",            # force (regression for the old regex missing it)
        "git push --force origin main",
        "git push origin HEAD:main",          # refspec
        "git push origin feature:main",       # feature → main
        "git merge --no-ff develop",
        "git merge develop",
        "git push origin release/1.2",
        "git push origin feature && git push origin main",  # main within a chain
    ]

    NOT_SHARED = [
        "git push origin feature-main",       # no partial-match false positive
        "git push origin main-feature",
        "git push origin my-develop-branch",
        "git push origin feat/login",
        "git commit -m main",                 # not push/merge
        "git push origin feature && echo main",  # main is not a git push argument
    ]

    def test_shared_detected(self):
        for cmd in self.SHARED:
            with self.subTest(cmd=cmd):
                self.assertTrue(pre.targets_shared_branch(cmd), cmd)

    def test_non_shared_passes(self):
        for cmd in self.NOT_SHARED:
            with self.subTest(cmd=cmd):
                self.assertFalse(pre.targets_shared_branch(cmd), cmd)


class TestNoVerify(unittest.TestCase):
    """Rule 2 — detect verify-skip flags (--no-verify / -n)."""

    USES = [
        "git commit -m x --no-verify",
        "git commit -nm x",                   # combined shorthand (regression for the old substring missing it)
        "git commit -n -m x",
        "git commit --no-verify",
    ]

    CLEAN = [
        "git commit -m x",
        "git commit -am x",                   # -am has no n
        "git commit -m 'add main feature'",
    ]

    def test_no_verify_detected(self):
        for cmd in self.USES:
            with self.subTest(cmd=cmd):
                self.assertTrue(pre.uses_no_verify(cmd), cmd)

    def test_clean_passes(self):
        for cmd in self.CLEAN:
            with self.subTest(cmd=cmd):
                self.assertFalse(pre.uses_no_verify(cmd), cmd)


if __name__ == "__main__":
    unittest.main()
