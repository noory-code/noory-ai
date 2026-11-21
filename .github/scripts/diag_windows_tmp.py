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
    def one_repo(cfg_env, steps):
        env = dict(os.environ)
        env.pop("GIT_CONFIG_GLOBAL", None)
        env.update(cfg_env)
        d = Path(tempfile.mkdtemp())
        t = {}
        s = time.perf_counter(); subprocess.run(["git", "init", "-q"], cwd=d, env=env, capture_output=True); t["init"] = time.perf_counter() - s
        (d / "x").write_text("x", encoding="utf-8")
        s = time.perf_counter(); subprocess.run(["git", "add", "-A"], cwd=d, env=env, capture_output=True); t["add"] = time.perf_counter() - s
        s = time.perf_counter(); subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-q", "-m", "x"], cwd=d, env=env, capture_output=True); t["commit"] = time.perf_counter() - s
        s = time.perf_counter(); subprocess.run(["git", "config", "user.name", "a"], cwd=d, env=env, capture_output=True); t["config"] = time.perf_counter() - s
        s = time.perf_counter(); c = Path(tempfile.mkdtemp()) / "copy"; shutil.copytree(d / ".git", c / ".git"); t["copytree .git"] = time.perf_counter() - s
        s = time.perf_counter(); shutil.rmtree(d, ignore_errors=True); t["rmtree"] = time.perf_counter() - s
        shutil.rmtree(c.parent, ignore_errors=True)
        for k, v in t.items():
            steps[k].append(v)

    sys.path.insert(0, str(Path("scripts/tests").resolve()))
    from git_test_config import isolate_git_config
    saved = os.environ.get("GIT_CONFIG_GLOBAL")
    cfg = str(isolate_git_config())
    if saved is None:
        os.environ.pop("GIT_CONFIG_GLOBAL", None)
    for name, env in (("default", {}), ("isolated", {"GIT_CONFIG_GLOBAL": cfg})):
        steps = defaultdict(list)
        for _ in range(15):
            one_repo(env, steps)
        for k, v in steps.items():
            print(f"BENCH {name:9s} {k:15s} {sum(v) / len(v) * 1000:8.1f} ms", flush=True)
    bench("git --version", lambda: run(["git", "--version"]), 30)
    bench("python -c pass", lambda: run([sys.executable, "-c", "pass"]), 20)
    bench("python -c import stage_work", lambda: run([sys.executable, "-c", "import sys; sys.path.insert(0, 'hooks'); import stage_work"]), 10)
    bench("python close_work.py --help", lambda: run([sys.executable, "skills/stage-retrospective/close_work.py", "--help"]), 10)


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
