"""Cross-platform regressions that can also run without a Windows host."""
import os
import subprocess
import sys
import unittest
from pathlib import Path, PureWindowsPath
from unittest import mock

from test_audit_stage import audit_stage
from test_close_work import python_command


class WindowsContractsTest(unittest.TestCase):
    def test_audit_paths_use_forward_slashes_on_windows(self):
        audit = audit_stage.Audit.__new__(audit_stage.Audit)
        audit.project_root = PureWindowsPath('C:/project')
        with mock.patch.object(audit_stage, 'Path', PureWindowsPath):
            self.assertEqual('.stage/work/current.md', audit.display_path(
                PureWindowsPath('C:/project/.stage/work/current.md')))

    def test_multiline_fixture_is_one_windows_shell_command(self):
        with mock.patch('os.name', 'nt'):
            command = python_command("for value in [1]:\n    print('hello')\n")
        self.assertNotIn('\n', command)

    def test_escalation_survives_an_ascii_output_pipe(self):
        scripts = Path(__file__).resolve().parents[1]
        code = ('import sys; sys.path.insert(0, ' + repr(str(scripts)) + '); '
                'from driver_worklog import print_escalation; print_escalation("stopped")')
        result = subprocess.run([sys.executable, '-c', code], capture_output=True,
                                env={**os.environ, 'PYTHONIOENCODING': 'ascii'})
        self.assertEqual(0, result.returncode, result.stderr.decode('utf-8'))
        self.assertIn('→ escalate_work', result.stdout.decode('utf-8'))
