"""Observe a real Skill invocation without writing to a user's Avatar store."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--avatar-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    prompt = """This is an isolated plugin-loading test, not a real personal record.
Invoke the Skill tool with skill avatar:avatar now. Read its instructions. Do not write files,
record choices, propose criteria or invoke other skills. You have only Skill and Read tools.
After the tool returns, state which command shows records, which command exports current criteria,
and whether confirmation preserves the proposal version. Do not claim you executed those commands.
"""
    argv = ["claude", "-p", "--model", "opus[1m]", "--plugin-dir", str(args.avatar_root.resolve()),
            "--tools", "Skill,Read", "--allowedTools", "Skill,Read", "--setting-sources", "",
            "--settings", '{"disableAllHooks":true}', "--strict-mcp-config", "--mcp-config",
            '{"mcpServers":{}}', "--output-format", "stream-json", "--verbose", "--", prompt]
    (out / "input.json").write_text(json.dumps({"argv": argv, "prompt": prompt,
        "expected_skill": "avatar:avatar", "hooks": "disabled for this invocation",
        "limit_seconds": 180}, indent=2), encoding="utf-8")
    started = time.monotonic()
    with (out / "stdout.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
        try:
            result = subprocess.run(argv, cwd=out, stdout=stdout, stderr=stderr, timeout=180)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    events = [json.loads(line) for line in (out / "stdout.jsonl").read_text().splitlines() if line.strip()]
    calls = [block for event in events for block in event.get("message", {}).get("content", [])
             if isinstance(block, dict) and block.get("type") == "tool_use"]
    skill_calls = [call for call in calls if call.get("name") == "Skill"
                   and call.get("input", {}).get("skill") == "avatar:avatar"]
    results = [block for event in events for block in event.get("message", {}).get("content", [])
               if isinstance(block, dict) and block.get("type") == "tool_result"]
    confirmed = any(not result.get("is_error") and result.get("tool_use_id") == call["id"]
                    for call in skill_calls for result in results)
    report = {"exit": code, "elapsed_seconds": time.monotonic() - started,
              "skill_calls": len(skill_calls), "successful_skill_result": confirmed,
              "passed": code == 0 and confirmed, "real_handoff": False}
    (out / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
