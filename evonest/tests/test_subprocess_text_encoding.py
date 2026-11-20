"""Every text-mode subprocess call names its encoding.

Without `encoding=`, Python decodes child output with the host locale. On Windows in Korean
(cp949) the UTF-8 output of `claude`, `codex`, or `git` then raises `UnicodeDecodeError` or
turns into mojibake. English-locale CI (cp1252) decodes the same bytes without an error, so
only this check catches a new call that leaves the encoding out.
"""

from __future__ import annotations

import ast
from pathlib import Path

SOURCE_ROOT = Path(__file__).parent.parent / "src" / "evonest"
TEXT_MODE_KEYWORDS = {"text", "universal_newlines"}


def _text_mode_calls_without_encoding(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords}
        text_mode = any(
            isinstance(keywords.get(name), ast.Constant) and keywords[name].value is True
            for name in TEXT_MODE_KEYWORDS
        )
        if text_mode and "encoding" not in keywords:
            lines.append(node.lineno)
    return lines


def test_text_mode_subprocess_calls_name_their_encoding() -> None:
    missing = [
        f"{path.relative_to(SOURCE_ROOT).as_posix()}:{line}"
        for path in sorted(SOURCE_ROOT.rglob("*.py"))
        for line in _text_mode_calls_without_encoding(path)
    ]
    assert missing == [], f"text-mode calls without encoding=: {missing}"


def test_the_check_finds_a_call_without_encoding(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text(
        "import subprocess\n"
        'subprocess.run(["git"], text=True)\n'
        'subprocess.run(["git"], text=True, encoding="utf-8")\n',
        encoding="utf-8",
    )
    assert _text_mode_calls_without_encoding(sample) == [2]
