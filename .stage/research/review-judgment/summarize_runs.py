#!/usr/bin/env python3
"""Print the reviewer runs of `measure_reviewer.py` as Markdown tables (W-00000414).

A run's outcome is `approved` or `rejected` when the verdict file was valid, and
`no verdict` otherwise; `close_work.py` fails the close review on all but `approved`.
The expected outcome of a case comes from `cases.json`. Whether a rejection named
the recorded defect is not decided here: a person reads the reasons for that.

Usage (from the project root):
    python3 .stage/research/review-judgment/summarize_runs.py
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def outcome(run: dict[str, object]) -> str:
    verdict = run.get("verdict")
    if run.get("verdict_error") or not isinstance(verdict, dict):
        return "no verdict"
    return "approved" if verdict.get("approved") is True else "rejected"


def marks(run: dict[str, object]) -> str:
    verdict = run.get("verdict")
    if not isinstance(verdict, dict):
        return str(run.get("verdict_error") or "")
    return ", ".join(
        f"{number} {entry['verdict']} {entry['method']}"
        for number, entry in enumerate(verdict["criteria"], 1)
    )


def main() -> int:
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"]
    runs: dict[str, list[dict[str, object]]] = {}
    for path in sorted((HERE / "runs").glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        runs.setdefault(str(run["case"]), []).append(run)

    print("| case | commit | expected | run | outcome | criteria | seconds | shell commands |"
          " output tokens | tree changed |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    counts: dict[tuple[str, str], int] = {}
    seconds: list[int] = []
    for case in cases:
        for run in sorted(runs.get(case["id"], []), key=lambda item: int(str(item["run"]))):
            result = outcome(run)
            counts[(case["expected"], result)] = counts.get((case["expected"], result), 0) + 1
            seconds.append(int(str(run["seconds"])))
            tokens = run["tokens"]
            assert isinstance(tokens, dict)
            commands = run["shell_commands"]
            assert isinstance(commands, list)
            print(
                f"| {case['id']} | `{case['commit']}` | {case['expected']} | {run['run']} |"
                f" {result} | {marks(run)} | {run['seconds']} | {len(commands)} |"
                f" {tokens['output']} | {'yes' if run['tree_changed_by_review'] else 'no'} |"
            )

    print()
    print("| expected | approved | rejected | no verdict |")
    print("|---|---|---|---|")
    for expected in ("rejected", "approved"):
        row = [counts.get((expected, result), 0) for result in ("approved", "rejected", "no verdict")]
        print(f"| {expected} | {row[0]} | {row[1]} | {row[2]} |")
    if seconds:
        ordered = sorted(seconds)
        print()
        print(
            f"runs {len(ordered)}, seconds: min {ordered[0]}, median {ordered[len(ordered) // 2]},"
            f" max {ordered[-1]}, total {sum(ordered)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
