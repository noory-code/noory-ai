"""Child-process output is read as UTF-8 whatever the host locale is.

Without an explicit `encoding`, a text-mode `subprocess` call decodes with the
locale encoding. On Windows in Korean that is cp949, so a check that prints
UTF-8 Korean made close_work's reader thread raise UnicodeDecodeError and the
check's output was lost (W-00000352).
"""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import locale
import subprocess
import sys
import threading
import unittest
from collections.abc import Generator
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from python_shell_command import python_command  # noqa: E402

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIRS = ("hooks", "scripts", "skills")
SUBPROCESS_CALLS = {"run", "Popen", "check_output", "check_call", "call"}
CLOSE_WORK = PLUGIN_ROOT / "skills" / "stage-retrospective" / "close_work.py"

# "한국어" in UTF-8 (it starts with 0xEC... the byte cp949 rejected first in the
# reported crash), then a byte that is valid in no encoding Stage reads.
KOREAN = "한국어"
CHILD_CODE = (
    "import sys\n"
    "sys.stdout.buffer.write('" + KOREAN + "'.encode('utf-8') + b' ok \\xff\\n')\n"
    "sys.stdout.buffer.flush()\n"
)


def plugin_sources() -> list[Path]:
    paths: list[Path] = []
    for directory in SOURCE_DIRS:
        for path in sorted((PLUGIN_ROOT / directory).rglob("*.py")):
            if "tests" not in path.relative_to(PLUGIN_ROOT).parts:
                paths.append(path)
    return paths


def _is_constant(node: ast.expr | None, value: object) -> bool:
    return isinstance(node, ast.Constant) and node.value == value


def text_mode_calls(source: str, filename: str) -> tuple[int, list[str]]:
    """Count text-mode subprocess calls and list those not decoding UTF-8 with replace."""

    tree = ast.parse(source, filename=filename)
    imported = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "subprocess"
        for alias in node.names
        if alias.name in SUBPROCESS_CALLS
    }
    count = 0
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_subprocess_call = (
            isinstance(func, ast.Attribute)
            and func.attr in SUBPROCESS_CALLS
            and isinstance(func.value, ast.Name)
            and func.value.id == "subprocess"
        ) or (isinstance(func, ast.Name) and func.id in imported)
        if not is_subprocess_call:
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg}
        text_mode = (
            _is_constant(keywords.get("text"), True)
            or _is_constant(keywords.get("universal_newlines"), True)
            or "encoding" in keywords
            or "errors" in keywords
        )
        if not text_mode:
            continue
        count += 1
        if not (
            _is_constant(keywords.get("encoding"), "utf-8")
            and _is_constant(keywords.get("errors"), "replace")
        ):
            violations.append(f"{filename}:{node.lineno}")
    return count, violations


@contextlib.contextmanager
def locale_encoding(name: str) -> Generator[None, None, None]:
    """Make text-mode subprocess calls without `encoding` default to `name`.

    Python 3.11+ asks `subprocess._text_encoding()` (UTF-8 mode short-circuits
    it); 3.9 and 3.10 ask `locale.getpreferredencoding(False)`. Patching the one
    this interpreter uses gives a non-UTF-8 default on macOS and Linux too.
    """

    if hasattr(subprocess, "_text_encoding"):
        with mock.patch.object(subprocess, "_text_encoding", return_value=name):
            yield
    else:
        with mock.patch.object(locale, "getpreferredencoding", return_value=name):
            yield


def load_close_work():
    if str(CLOSE_WORK.parent) not in sys.path:
        sys.path.insert(0, str(CLOSE_WORK.parent))
    spec = importlib.util.spec_from_file_location("stage_close_work_encoding", CLOSE_WORK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SubprocessTextEncodingGuardTest(unittest.TestCase):
    def test_every_text_mode_subprocess_call_decodes_utf8_with_replace(self):
        total = 0
        violations: list[str] = []
        for path in plugin_sources():
            count, found = text_mode_calls(
                path.read_text(encoding="utf-8"),
                path.relative_to(PLUGIN_ROOT).as_posix(),
            )
            total += count
            violations.extend(found)

        self.assertGreater(total, 0, "the guard found no text-mode subprocess calls to check")
        self.assertEqual(
            [],
            violations,
            'text-mode subprocess calls must pass encoding="utf-8", errors="replace"',
        )

    def test_guard_flags_text_mode_without_utf8_and_replace(self):
        cases = {
            "subprocess.run(['x'], text=True)": 1,
            "subprocess.run(['x'], universal_newlines=True)": 1,
            "subprocess.Popen(['x'], text=True, encoding='utf-8')": 1,
            "subprocess.check_output(['x'], encoding='cp949', errors='replace')": 1,
            "from subprocess import run as go\ngo(['x'], text=True)": 1,
            "subprocess.run(['x'], text=True, encoding='utf-8', errors='replace')": 0,
            "subprocess.run(['x'], capture_output=True)": 0,
            "tempfile.mkstemp(text=True)": 0,
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                _, violations = text_mode_calls(source, "case.py")
                self.assertEqual(expected, len(violations))


class SubprocessTextEncodingBehaviourTest(unittest.TestCase):
    def test_locale_default_loses_utf8_output(self):
        # Control: the simulated locale really breaks an undeclared decode, so
        # the close_work test below would fail without the fix.
        output = ""
        with locale_encoding("cp949"), mock.patch.object(threading, "excepthook"):
            try:
                proc = subprocess.run(
                    python_command(CHILD_CODE), shell=True, capture_output=True, text=True
                )
                output = proc.stdout or ""
            except UnicodeDecodeError:
                output = ""
        self.assertNotIn(KOREAN, output)

    def test_close_work_check_keeps_utf8_output_under_a_cp949_locale(self):
        close_work = load_close_work()

        with locale_encoding("cp949"):
            ok, evidence, raw = close_work.run_check(
                python_command(CHILD_CODE), timeout=60, cwd=PLUGIN_ROOT
            )

        self.assertTrue(ok, evidence)
        self.assertIn(f"{KOREAN} ok �", raw)
        self.assertIn(f"{KOREAN} ok", evidence)


if __name__ == "__main__":
    unittest.main()
