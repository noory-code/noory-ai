"""The plugins that promise Python 3.9 keep testing it on every OS in CI."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[3] / ".github" / "workflows"
PYTHON_39_PLUGINS = ("stage", "avatar", "plainly")


def matrix_block(text: str) -> str:
    match = re.search(r"^      matrix:\n((?:        .*\n)+)", text, re.MULTILINE)
    assert match, "workflow has no strategy matrix"
    return match.group(1)


def combinations(block: str) -> set[tuple[str, str]]:
    """Expand a matrix of os x python with its exclude and include entries."""

    oses = re.search(r"^        os: \[(.*)\]$", block, re.MULTILINE)
    pythons = re.search(r"^        python: \[(.*)\]$", block, re.MULTILINE)
    assert oses and pythons, "matrix must list os and python"
    os_values = [value.strip() for value in oses.group(1).split(",")]
    python_values = [value.strip().strip('"') for value in pythons.group(1).split(",")]
    result = {(os_name, python) for os_name in os_values for python in python_values}

    def entries(section: str) -> set[tuple[str, str]]:
        found = re.search(
            rf"^        {section}:\n((?:          .*\n)+)", block, re.MULTILINE
        )
        if not found:
            return set()
        pairs = re.findall(
            r"- os: (\S+)\n\s+python: \"([^\"]+)\"", found.group(1)
        )
        return set(pairs)

    return (result - entries("exclude")) | entries("include")


class CiWorkflowsTest(unittest.TestCase):
    def test_python_39_runs_on_every_os_with_ubuntu_on_the_previous_lts(self):
        for plugin in PYTHON_39_PLUGINS:
            with self.subTest(plugin=plugin):
                text = (WORKFLOWS / f"{plugin}.yml").read_text(encoding="utf-8")

                self.assertEqual(
                    {
                        ("ubuntu-24.04", "3.9"),
                        ("ubuntu-latest", "3.12"),
                        ("macos-latest", "3.9"),
                        ("macos-latest", "3.12"),
                        ("windows-latest", "3.9"),
                        ("windows-latest", "3.12"),
                    },
                    combinations(matrix_block(text)),
                )


if __name__ == "__main__":
    unittest.main()
