"""quality_gate_cli adapter regression (TS-003 A-002 — invoke checks, record, minimal failure action, stdlib unittest).

Target: quality_gate_cli.cmd_run — no-op / pass / required failure / non-required failure / checks record.
Portability: check commands use `sys.executable -c "..."` (common to POSIX/Windows). shell=False verification.
Run: cd flow/hooks && python3 -m unittest tests.test_quality_gate
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as w  # noqa: E402
import quality_gate_cli as qg  # noqa: E402

PY = sys.executable
PASS = f'"{PY}" -c "import sys; sys.exit(0)"'
FAIL = f'"{PY}" -c "import sys; sys.exit(1)"'


def _settings(ws: str, commands: dict) -> None:
    d = os.path.join(ws, ".flow")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "settings.json"), "w", encoding="utf-8") as f:
        json.dump({"commands": commands}, f)


def _audit_records(ws: str) -> list:
    path = os.path.join(w.runtime_dir(ws), w.AUDIT_FILE)
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


class TestQualityGateRun(unittest.TestCase):
    def test_no_commands_noop_pass(self):
        with tempfile.TemporaryDirectory() as ws:
            self.assertEqual(qg.cmd_run(ws), 0)  # unset → no-op pass
            self.assertEqual(_audit_records(ws), [])  # no records

    def test_all_pass_no_required(self):
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": PASS, "lint": PASS})  # no required_checks
            self.assertEqual(qg.cmd_run(ws), 0)
            checks = [r for r in _audit_records(ws) if r.get("check")]
            self.assertEqual(len(checks), 2)
            self.assertTrue(all(r["passed"] for r in checks))

    def test_required_pass(self):
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": PASS, "required_checks": ["test"]})
            self.assertEqual(qg.cmd_run(ws), 0)

    def test_required_fail_blocks(self):
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": FAIL, "required_checks": ["test"]})
            self.assertEqual(qg.cmd_run(ws), 1)  # minimal failure action — non-zero
            check = [r for r in _audit_records(ws) if r.get("check") == "test"][0]
            self.assertFalse(check["passed"])
            self.assertEqual(check["returncode"], 1)

    def test_non_required_fail_passes(self):
        with tempfile.TemporaryDirectory() as ws:
            # analyze fails but is not required → not blocked
            _settings(ws, {"test": PASS, "analyze": FAIL, "required_checks": ["test"]})
            self.assertEqual(qg.cmd_run(ws), 0)

    def test_check_record_shape(self):
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": PASS, "required_checks": ["test"]})
            qg.cmd_run(ws)
            check = [r for r in _audit_records(ws) if r.get("check")][0]
            for key in ("ts", "check", "cmd", "returncode", "passed"):
                self.assertIn(key, check)

    def test_missing_executable_records_fail(self):
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": "nonexistent_cmd_xyz --run", "required_checks": ["test"]})
            self.assertEqual(qg.cmd_run(ws), 1)  # run failure = required fail → block
            check = [r for r in _audit_records(ws) if r.get("check") == "test"][0]
            self.assertFalse(check["passed"])


class TestWindowsSafeParsing(unittest.TestCase):
    """M-1 — allow command argv list + OS-aware shlex.split (preserve Windows path backslash)."""

    def test_argv_list_passthrough(self):
        self.assertEqual(qg._to_argv(["python", "-c", "pass"]), ["python", "-c", "pass"])

    def test_argv_list_preserves_windows_path(self):
        argv = [r"C:\Program Files\Python311\python.exe", "-m", "pytest"]
        self.assertEqual(qg._to_argv(argv), argv)  # backslash path intact (OS-independent recommended path)

    def test_str_posix_split_on_unix(self):
        self.assertEqual(qg._to_argv('"x y" -c z'), ["x y", "-c", "z"])

    def test_str_nt_preserves_backslash(self):
        # Windows (os.name='nt') → posix=False → preserve backslash (avoids the fixed-POSIX-split defect)
        with mock.patch.object(qg.os, "name", "nt"):
            self.assertIn(r"C:\Python\python.exe", qg._to_argv(r"C:\Python\python.exe -m pytest"))

    def test_argv_list_command_runs(self):
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": [PY, "-c", "import sys; sys.exit(0)"], "required_checks": ["test"]})
            self.assertEqual(qg.cmd_run(ws), 0)
            self.assertTrue([r for r in _audit_records(ws) if r.get("check") == "test"][0]["passed"])


class TestMisconfiguredRequired(unittest.TestCase):
    """M-2 — required but command undeclared = config error (distinct from check failure)."""

    def test_misconfigured_required_is_config_error(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": PASS, "required_checks": ["test", "lint"]})  # lint undeclared
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = qg.cmd_run(ws)
            self.assertEqual(rc, 1)
            msg = err.getvalue()
            self.assertIn("config error", msg)
            self.assertIn("lint", msg)
            self.assertEqual([r for r in _audit_records(ws) if r.get("check") == "lint"], [])  # not run

    def test_check_fail_vs_config_error_distinct(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as ws:
            _settings(ws, {"test": FAIL, "required_checks": ["test", "lint"]})
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = qg.cmd_run(ws)
            self.assertEqual(rc, 1)
            msg = err.getvalue()
            self.assertIn("config error", msg)         # lint (undeclared)
            self.assertIn("required check failed", msg)  # test (run failure)


if __name__ == "__main__":
    unittest.main()
