"""TEMPORARY W-00000380 diagnostic: measure process and filesystem costs on the runner."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from collections import defaultdict
from pathlib import Path


def bench(label, fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    per = (time.perf_counter() - start) / n * 1000
    print(f"BENCH {label:45s} {per:8.1f} ms", flush=True)


def run(args, cwd=None, shell=False):
    subprocess.run(args, cwd=cwd, shell=shell, capture_output=True, check=False)


def micro():
    repo = Path(tempfile.mkdtemp())
    run(["git", "init", "-q"], cwd=repo)
    (repo / "a.txt").write_text("a", encoding="utf-8")
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-q", "-m", "x"], cwd=repo)
    bench("git --version", lambda: run(["git", "--version"]), 40)
    bench("git rev-parse --git-path index", lambda: run(["git", "rev-parse", "--git-path", "index"], cwd=repo), 40)
    bench("git ls-files --others", lambda: run(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=repo), 40)
    bench("git status --porcelain", lambda: run(["git", "status", "--porcelain"], cwd=repo), 40)
    bench("python -c pass", lambda: run([sys.executable, "-c", "pass"]), 20)
    bench("python -S -c pass", lambda: run([sys.executable, "-S", "-c", "pass"]), 20)
    bench("shell=True python -c pass", lambda: run(f'"{sys.executable}" -c pass', shell=True), 20)
    drive = Path("scripts/drive.py").resolve()
    bench("python drive.py --help", lambda: run([sys.executable, str(drive), "--help"]), 10)

    def init_repo():
        d = tempfile.mkdtemp()
        run(["git", "init", "-q"], cwd=d)
        shutil.rmtree(d, ignore_errors=True)
    bench("mkdtemp + git init + rmtree", init_repo, 20)

    def commit_repo():
        d = Path(tempfile.mkdtemp())
        run(["git", "init", "-q"], cwd=d)
        (d / "x").write_text("x", encoding="utf-8")
        run(["git", "add", "-A"], cwd=d)
        run(["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-q", "-m", "x"], cwd=d)
        shutil.rmtree(d, ignore_errors=True)
    bench("init+add+commit+rmtree", commit_repo, 20)

    def tree_io():
        d = Path(tempfile.mkdtemp())
        for i in range(30):
            (d / f"f{i}").write_text("x", encoding="utf-8")
        shutil.rmtree(d)
    bench("mkdtemp + 30 files + rmtree", tree_io, 20)


class R(unittest.TextTestResult):
    def startTest(self, test):
        self._t = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        TIMES.append((time.perf_counter() - self._t, test.id()))


TIMES: list[tuple[float, str]] = []


def suite(start_dir, shard, total):
    sys.path.insert(0, str(Path.cwd()))
    loader = unittest.TestLoader()
    tests = []

    def flat(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                flat(t)
            else:
                tests.append(t)
    flat(loader.discover(start_dir))
    tests.sort(key=lambda t: t.id())
    picked = [t for i, t in enumerate(tests) if i % total == shard - 1]
    unittest.TextTestRunner(resultclass=R, verbosity=0, stream=open(os.devnull, "w")).run(unittest.TestSuite(picked))
    mods = defaultdict(float)
    for d, i in TIMES:
        mods[i.split(".")[0]] += d
    print(f"TOTAL {sum(d for d, _ in TIMES):.1f}s over {len(TIMES)} tests")
    for m, d in sorted(mods.items(), key=lambda x: -x[1])[:20]:
        print(f"MOD {d:7.1f} {m}")
    for d, i in sorted(TIMES, reverse=True)[:40]:
        print(f"TEST {d:6.2f} {i}")


if __name__ == "__main__":
    micro()
    suite("scripts/tests", int(sys.argv[1]), int(sys.argv[2]))
