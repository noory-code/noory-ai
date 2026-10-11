"""고정한 문제를 반복 실행합니다. 제품 파일과 사용자 자료에는 접근하지 않습니다."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import time
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "2026-10-05-followup"
MODEL = "claude-sonnet-5-5"


def save(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def execute(case: dict[str, Any], condition: str, repeat: int) -> dict[str, Any]:
    run_id = f'{case["id"]}--{condition}--{repeat}'
    output = OUT / (run_id + ".json")
    if output.exists():
        return json.loads(output.read_text(encoding="utf-8"))
    system = (
        "주어진 요청과 자료를 보고 판단하세요. 실제 외부 작업은 수행하지 않습니다. "
        "JSON 객체 하나로 답하세요. decision은 제공한 choices 중 하나이며 reason은 한 문장입니다. "
        "report는 분석 보고서 작성, edit는 파일 수정, draft는 발송하지 않을 초안 작성, "
        "ask는 필요한 정보 질문, continue는 맡은 일 계속 수행을 뜻합니다. "
        "그 외 choices는 문맥에 따라 지원 여부, 완료 여부, 규칙에 따른 처리 여부를 뜻합니다."
    )
    if condition == "purpose_check":
        system += " 행동을 고르기 전에 사용자의 목적, 제약, 미확인 사항을 각각 짧게 적고 purpose 필드에 담으세요."
    prompt = json.dumps({"request": case["variants"][condition], "choices": case["choices"]},
                        ensure_ascii=False)
    record: dict[str, Any] = {
        "run_id": run_id, "case": case["id"], "family": case["family"],
        "condition": condition, "repeat": repeat,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt, "system_prompt": system,
        "input_sha256": hashlib.sha256((system + "\n" + prompt).encode()).hexdigest(),
        "messages": [], "result": None, "error": None,
    }
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="llm-followup-") as directory:
        options = ClaudeAgentOptions(
            model=MODEL, cli_path=shutil.which("claude"), cwd=Path(directory),
            system_prompt=system, tools=[], setting_sources=[], mcp_servers={},
            strict_mcp_config=True, permission_mode="default", max_turns=1,
            max_budget_usd=0.15, thinking={"type": "disabled"},
            extra_args={"restricted": None, "disable-slash-commands": None,
                        "no-session-persistence": None},
        )

        async def collect() -> None:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        record["messages"].append({"model": message.model, "text":
                            [b.text for b in message.content if isinstance(b, TextBlock)]})
                    elif isinstance(message, ResultMessage):
                        record["result"] = asdict(message)
        try:
            await asyncio.wait_for(collect(), timeout=90)
        except Exception as error:
            record["error"] = {"type": type(error).__name__, "message": str(error)}
    record["wall_time_s"] = time.monotonic() - start
    save(output, record)
    return record


async def main() -> None:
    cases = json.loads((ROOT / "followup-cases.json").read_text(encoding="utf-8"))
    hashes = json.loads((ROOT / "followup-input-hashes.json").read_text())
    for filename, expected in hashes.items():
        if hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f"실행 전에 고정한 파일이 달라졌습니다: {filename}")
    OUT.mkdir(parents=True, exist_ok=True)
    schedule = [(case, condition, repeat) for case in cases
                for condition in case["variants"] for repeat in range(1, 4)]
    random.Random(2026100502).shuffle(schedule)
    manifest = {
        "model": MODEL, "sdk": importlib.metadata.version("claude-agent-sdk"),
        "cli": subprocess.check_output([shutil.which("claude"), "--version"], text=True).strip(),
        "thinking_requested": {"type": "disabled"}, "max_turns": 1,
        "max_budget_usd_per_run": 0.15, "total_reported_budget_usd": 5,
        "parallel_calls": 2, "timeout_s": 90, "source_hashes": hashes,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "schedule": [{"case": c["id"], "condition": v, "repeat": r}
                     for c, v, r in schedule],
    }
    path = OUT / "manifest.json"
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError("기존 실행의 설정이 다릅니다. 덮어쓰지 않습니다.")
    save(path, manifest)
    spent = 0.0
    for offset in range(0, len(schedule), 2):
        if spent + 0.30 > 5:
            raise RuntimeError("남은 비용 한도가 두 실행의 최대값보다 적어 멈춥니다.")
        records = await asyncio.gather(*(execute(*entry) for entry in schedule[offset:offset + 2]))
        for record in records:
            result = record.get("result") or {}
            spent += result.get("total_cost_usd") or 0
            print(json.dumps({"run_id": record["run_id"], "error": record["error"],
                              "is_error": result.get("is_error"),
                              "cumulative_reported_usd": round(spent, 6)}), flush=True)
        if any(r["error"] or not r["result"] or r["result"].get("is_error") for r in records):
            raise RuntimeError("오류가 생겼습니다. 원본을 보관하고 다음 실행을 멈춥니다.")


if __name__ == "__main__":
    asyncio.run(main())
