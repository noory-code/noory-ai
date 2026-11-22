"""How run_bounded reads a command's output (W-00000394)."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_process import decode_output, run_bounded  # noqa: E402

KOREAN = "'true'은(는) 내부 또는 외부 명령이 아닙니다."


class DecodeOutputTest(unittest.TestCase):
    def test_utf_8_output_is_read_as_utf_8(self) -> None:
        self.assertEqual(KOREAN, decode_output(KOREAN.encode("utf-8"), fallback="cp949"))

    def test_output_that_is_not_utf_8_is_read_in_the_fallback_code_page(self) -> None:
        self.assertEqual(KOREAN, decode_output(KOREAN.encode("cp949"), fallback="cp949"))

    def test_empty_output_is_an_empty_string(self) -> None:
        self.assertEqual("", decode_output(b""))
        self.assertEqual("", decode_output(None))

    def test_run_bounded_reads_a_child_that_writes_utf_8(self) -> None:
        code = "import sys; sys.stdout.buffer.write('한국어 출력'.encode('utf-8'))"

        result = run_bounded([sys.executable, "-c", code], timeout=30)

        self.assertEqual("한국어 출력", result.stdout)

    @unittest.skipUnless(sys.platform == "win32", "cmd.exe writes in the Windows OEM code page")
    def test_a_cmd_exe_error_reads_without_replacement_characters(self) -> None:
        result = run_bounded("stage_no_such_command_w394", shell=True, timeout=30)

        self.assertNotEqual(0, result.returncode)
        self.assertTrue(result.stderr.strip())
        self.assertNotIn("�", result.stderr)


if __name__ == "__main__":
    unittest.main()
