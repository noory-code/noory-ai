"""Run one fresh host session and retain its raw response and timing."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time


def run_host(host: str, project: Path, output: Path, prompt: str) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    if host == "codex":
        argv = ["codex", "exec", "--ignore-user-config", "--model", "gpt-6-sol",
                "-c", 'model_reasoning_effort="high"', "--sandbox", "workspace-write",
                "--skip-git-repo-check", "--ephemeral", "--json", "--cd", str(project), "-"]
    else:
        argv = ["claude", "-p", "--model", "opus[1m]", "--tools", "Read,Write,Edit,Bash",
                "--allowedTools", "Read,Write,Edit,Bash", "--setting-sources", "",
                "--settings", '{"disableAllHooks":true}', "--strict-mcp-config", "--mcp-config",
                '{"mcpServers":{}}', "--output-format", "stream-json", "--verbose"]
    (output / "prompt.txt").write_text(prompt, encoding="utf-8")
    (output / "input.json").write_text(json.dumps({"host": host, "argv": argv,
        "cwd": str(project), "timeout_seconds": 180}, indent=2), encoding="utf-8")
    started = time.monotonic()
    with (output / "stdout.jsonl").open("w") as out, (output / "stderr.txt").open("w") as err:
        try:
            result = subprocess.run(argv, input=prompt, text=True, encoding="utf-8",
                                    cwd=project, stdout=out, stderr=err, timeout=180)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    events = []
    for line in (output / "stdout.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    finals, usage, models, session_ids = [], [], set(), set()
    for event in events:
        if event.get("session_id") or event.get("thread_id"):
            session_ids.add(event.get("session_id", event.get("thread_id")))
        if host == "codex":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                finals.append(item.get("text", ""))
            if event.get("type") == "turn.completed":
                usage.append(event.get("usage"))
        elif event.get("type") == "result":
            finals.append(event.get("result", ""))
            usage.append({"usage": event.get("usage"), "reported_cost_usd": event.get("total_cost_usd")})
        model = event.get("message", {}).get("model")
        if model:
            models.add(model)
    summary = {"host": host, "exit": code, "elapsed_seconds": time.monotonic() - started,
               "session_ids": sorted(session_ids), "reported_models": sorted(models),
               "usage": usage, "assistant_text": "\n".join(finals)}
    (output / "result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
