#!/usr/bin/env python3
"""Run one shard of a unittest discovery suite, so CI can split a slow suite across jobs.

Every discovered test is sorted by id and dealt round-robin to the shards, so the
shards together run each test exactly once and slow test modules spread evenly.
A module that fails to import becomes a failing test in one shard, never a silent
gap. Runs on Python 3.9, the oldest version the plugins test against.

Usage:
    python unittest_shard.py --start-dir scripts/tests --shard 1 --total 3
"""

from __future__ import annotations

import argparse
import sys
import unittest
from collections.abc import Iterator
from pathlib import Path


def iter_tests(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from iter_tests(test)
        else:
            yield test


def shard_tests(
    tests: list[unittest.TestCase], shard: int, total: int
) -> list[unittest.TestCase]:
    ordered = sorted(tests, key=lambda test: test.id())
    return [test for index, test in enumerate(ordered) if index % total == shard - 1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start-dir", required=True)
    parser.add_argument("--shard", type=int, required=True, help="1-based shard number.")
    parser.add_argument("--total", type=int, required=True, help="Number of shards.")
    args = parser.parse_args(argv)
    if args.total < 1 or not 1 <= args.shard <= args.total:
        parser.error(f"--shard must be in 1..{args.total}, got {args.shard}")

    # `python -m unittest` puts the working directory first on sys.path; match it.
    sys.path.insert(0, str(Path.cwd()))
    discovered = list(iter_tests(unittest.TestLoader().discover(args.start_dir)))
    picked = shard_tests(discovered, args.shard, args.total)
    print(
        f"{args.start_dir}: shard {args.shard}/{args.total} runs "
        f"{len(picked)} of {len(discovered)} tests",
        flush=True,
    )
    result = unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(picked))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
