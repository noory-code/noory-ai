"""Check current Codex availability once and retain the complete response."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True, type=Path)
args = parser.parse_args()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=False)
with tempfile.TemporaryDirectory(prefix="criteria-codex-probe-") as temporary:
    argv = ["codex", "exec", "--ignore-user-config", "--model", "gpt-6-sol",
            "--sandbox", "read-only", "--skip-git-repo-check", "--ephemeral", "--json",
            "--cd", temporary, "Reply with exactly READY. Do not use tools or read or write files."]
    (out / "input.json").write_text(json.dumps({"argv": argv, "timeout_seconds": 60}, indent=2))
    started = time.monotonic()
    with (out / "stdout.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
        try:
            code = subprocess.run(argv, stdout=stdout, stderr=stderr, timeout=60).returncode
        except subprocess.TimeoutExpired:
            code = 124
    result = {"exit": code, "elapsed_seconds": time.monotonic() - started}
    (out / "result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    print((out / "stdout.jsonl").read_text()[-6000:])
