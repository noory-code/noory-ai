"""The plugins that promise Python 3.9 keep testing it on every OS in CI."""

from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[3] / ".github" / "workflows"
SHARD_SCRIPT = WORKFLOWS.parent / "scripts" / "unittest_shard.py"
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


def matrix_entries(block: str, section: str) -> list[dict[str, str]]:
    found = re.search(rf"^        {section}:\n((?:          .*\n)+)", block, re.MULTILINE)
    if not found:
        return []
    entries: list[dict[str, str]] = []
    for line in found.group(1).splitlines():
        if line.lstrip().startswith("#"):
            continue
        key_value = re.match(r"^          (- |  )(\w+): (.+)$", line)
        assert key_value, f"unparsed matrix line: {line!r}"
        if key_value.group(1) == "- ":
            entries.append({})
        entries[-1][key_value.group(2)] = key_value.group(3).strip().strip('"')
    return entries


def expand_matrix(block: str) -> list[dict[str, str]]:
    """Expand a matrix of list-valued keys with its exclude and include entries."""

    axes: dict[str, list[str]] = {}
    for key, values in re.findall(r"(?m)^        (\w+): \[(.*)\]$", block):
        axes[key] = [value.strip().strip('"') for value in values.split(",")]
    jobs: list[dict[str, str]] = [{}]
    for key, values in axes.items():
        jobs = [{**job, key: value} for job in jobs for value in values]
    excluded = matrix_entries(block, "exclude")
    jobs = [
        job
        for job in jobs
        if not any(all(job.get(k) == v for k, v in entry.items()) for entry in excluded)
    ]
    # Every include entry in these workflows names a combination the axes do not
    # produce, so GitHub adds each one as a job of its own.
    return jobs + matrix_entries(block, "include")


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

    def test_push_runs_on_main_only_so_a_pull_request_branch_runs_once(self):
        # A workflow that runs on every push and on pull_request runs twice for each push to
        # a branch with an open pull request.
        workflows = sorted(WORKFLOWS.glob("*.yml"))
        self.assertTrue(workflows)
        for workflow in workflows:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding="utf-8")

                self.assertRegex(text, r"(?m)^  pull_request:\n    paths:\n")
                self.assertRegex(text, r"(?m)^  push:\n    branches: \[main\]\n    paths:\n")


    def test_stage_matrix_runs_every_shard_number_up_to_each_os_total(self):
        # A shard number the matrix drops never runs, and its tests vanish without a failure.
        # Windows splits into more shards than the other OSes, so the guarantee holds per OS.
        text = (WORKFLOWS / "stage.yml").read_text(encoding="utf-8")
        totals = dict(re.findall(r"(?m)^  (SHARD_TOTAL|WINDOWS_SHARD_TOTAL): (\d+)$", text))
        assert set(totals) == {"SHARD_TOTAL", "WINDOWS_SHARD_TOTAL"}, totals
        total_argument = (
            "--total ${{ matrix.os == 'windows-latest' && env.WINDOWS_SHARD_TOTAL "
            "|| env.SHARD_TOTAL }}"
        )
        self.assertEqual(2, text.count(total_argument))
        self.assertNotRegex(text, r"--total \$\{\{ env\.SHARD_TOTAL \}\}")

        shards_by_job: dict[tuple[str, str], set[int]] = {}
        for job in expand_matrix(matrix_block(text)):
            shards_by_job.setdefault((job["os"], job["python"]), set()).add(int(job["shard"]))
        self.assertEqual(6, len(shards_by_job))
        for (os_name, python), shards in sorted(shards_by_job.items()):
            with self.subTest(os=os_name, python=python):
                name = "WINDOWS_SHARD_TOTAL" if os_name == "windows-latest" else "SHARD_TOTAL"
                self.assertEqual(set(range(1, int(totals[name]) + 1)), shards)

    def test_shards_together_run_every_test_exactly_once(self):
        spec = importlib.util.spec_from_file_location("unittest_shard", SHARD_SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class Sample(unittest.TestCase):
            pass

        for index in range(7):
            setattr(Sample, f"test_{index}", lambda self: None)
        tests = list(unittest.TestLoader().loadTestsFromTestCase(Sample))
        everything = sorted(test.id() for test in tests)
        for total in (1, 2, 3, 4, 6, 8):
            with self.subTest(total=total):
                picked = [
                    test.id()
                    for shard in range(1, total + 1)
                    for test in module.shard_tests(tests, shard, total)
                ]
                self.assertEqual(everything, sorted(picked))


if __name__ == "__main__":
    unittest.main()
