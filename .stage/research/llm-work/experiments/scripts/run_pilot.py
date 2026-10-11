"""공개 SDK와 설치된 CLI로 작은 연구 실험을 실행합니다."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict, is_dataclass
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
from claude_agent_sdk.types import (
    AssistantMessage,
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


async def execute(
    run_id: str, prompt: str, args: argparse.Namespace, workspace: Path,
    system: str, probe: str | None = None,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    record: dict[str, Any] = {
        "run_id": run_id, "requested_model": args.model, "started_at": now(),
        "prompt": prompt, "system_prompt": system,
        "input_sha256": hashlib.sha256((system + "\n" + prompt).encode()).hexdigest(),
        "events": events, "result": None, "error": None,
    }
    start = time.monotonic()

    def event(kind: str, data: Any) -> None:
        events.append({"kind": kind, "elapsed_s": time.monotonic() - start, "data": data})

    async def hook(data: dict[str, Any], tool_id: str | None, _: Any) -> dict[str, Any]:
        selected = {key: data[key] for key in (
            "hook_event_name", "tool_name", "tool_input", "tool_response", "tool_use_id"
        ) if key in data}
        event("hook", selected)
        if data.get("hook_event_name") == "PreToolUse":
            path = data.get("tool_input", {}).get("file_path", "")
            if data.get("tool_name") != "Read" or Path(path).resolve() != workspace / "fixture.txt":
                return {"hookSpecificOutput": {
                    "hookEventName": "PreToolUse", "permissionDecision": "deny",
                    "permissionDecisionReason": "이 실험에서는 지정한 시험 파일만 읽습니다.",
                }}
            if probe == "ask_callback":
                return {"hookSpecificOutput": {
                    "hookEventName": "PreToolUse", "permissionDecision": "ask",
                }}
        return {}

    async def permission(name: str, data: dict[str, Any], context: Any) -> Any:
        event("permission_callback", {"tool_name": name, "input": data,
                                      "tool_use_id": context.tool_use_id})
        if name == "Read" and Path(data.get("file_path", "")).resolve() == workspace / "fixture.txt":
            return PermissionResultAllow(updated_input=data)
        return PermissionResultDeny(message="실험 범위를 벗어난 호출입니다.")

    options = ClaudeAgentOptions(
        model=args.model, cli_path=args.cli, cwd=workspace,
        system_prompt=system, tools=["Read"] if probe else [],
        allowed_tools=["Read"] if probe == "allowed_read" else [],
        permission_mode="default", max_turns=4, max_budget_usd=0.50,
        setting_sources=[], strict_mcp_config=True, mcp_servers={},
        extra_args={"restricted": None, "disable-slash-commands": None,
                    "no-session-persistence": None},
        hooks={name: [HookMatcher(matcher="Read", hooks=[hook])]
               for name in ("PreToolUse", "PostToolUse", "PostToolUseFailure")} if probe else None,
        can_use_tool=permission if probe else None,
        include_hook_events=bool(probe),
    )
    record["configuration"] = {
        "tools": options.tools, "allowed_tools": options.allowed_tools,
        "setting_sources": [], "strict_mcp_config": True,
        "permission_mode": "default", "max_turns": 4, "max_budget_usd": 0.50,
        "extra_args": options.extra_args, "timeout_s": 120,
        "reasoning_configuration": "CLI와 모델의 기본값을 사용합니다. 별도로 지정하지 않았습니다.",
    }

    async def collect() -> None:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    blocks = []
                    for block in message.content:
                        if isinstance(block, (TextBlock, ToolUseBlock)):
                            blocks.append(asdict(block))
                        else:
                            blocks.append({"omitted_block_type": type(block).__name__})
                    event("assistant", {"model": message.model, "blocks": blocks})
                elif isinstance(message, ResultMessage):
                    record["result"] = asdict(message)
                    event("result", record["result"])
                elif isinstance(message, SystemMessage):
                    event("system", {"subtype": message.subtype,
                                     "model": message.data.get("model"),
                                     "tools": message.data.get("tools")})
                elif isinstance(message, UserMessage):
                    event("user_or_tool_result", {"content": asdict(message)["content"]})
                elif is_dataclass(message):
                    event("other_message", {"type": type(message).__name__})

    try:
        await asyncio.wait_for(collect(), timeout=120)
    except Exception as error:
        record["error"] = {"type": type(error).__name__, "message": str(error)}
    record["finished_at"] = now()
    record["wall_time_s"] = time.monotonic() - start
    save(args.output / f"{run_id}.json", record)
    result = record["result"] or {}
    print(json.dumps({"run_id": run_id, "error": record["error"],
                      "is_error": result.get("is_error"),
                      "wall_time_s": round(record["wall_time_s"], 2),
                      "cost_usd_reported": result.get("total_cost_usd")}), flush=True)
    return record


async def main(args: argparse.Namespace) -> None:
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.glob("*.json")):
        raise ValueError("기존 실행 결과가 있는 폴더에는 덮어쓰지 않습니다.")
    metadata = {
        "sdk_version": importlib.metadata.version("claude-agent-sdk"),
        "cli_version": subprocess.check_output([args.cli, "--version"], text=True).strip(),
        "requested_model": args.model, "created_at": now(), "suite": args.suite,
        "sdk_revision": args.sdk_revision,
    }
    save(args.output / "environment.json", metadata)
    with tempfile.TemporaryDirectory(prefix="llm-work-pilot-") as directory:
        workspace = Path(directory).resolve()
        (workspace / "fixture.txt").write_text("RESEARCH_MARKER=orchid-731\n", encoding="utf-8")
        if args.suite == "hooks":
            for condition in ("allowed_read", "ask_callback"):
                record = await execute(condition,
                    f"Read 도구로 {workspace / 'fixture.txt'} 파일을 한 번 읽고, "
                    "RESEARCH_MARKER 값을 그대로 답해주세요. 다른 파일은 읽지 마세요.",
                    args, workspace, "지정한 시험 파일을 읽는 실험입니다. 요청대로 수행하세요.",
                    probe=condition)
                if record["error"] or (record["result"] or {}).get("is_error"):
                    break
        else:
            cases = json.loads(args.cases.read_text())
            schedule = [(case, condition) for case in cases
                        for condition in ("baseline", "evidence_check")]
            random.Random(20261005).shuffle(schedule)
            save(args.output / "schedule.json", [{"case": c["id"], "condition": v}
                                                  for c, v in schedule])
            base = (
                "제공한 자료만 사용해 사용자의 질문에 한국어로 답하세요. "
                "답은 JSON 객체 하나로 작성하세요. status는 supported, insufficient, conflicting "
                "중 하나를 사용하고, answer에는 짧은 설명을, sources에는 근거 문서 ID 배열을 넣으세요."
            )
            for case, condition in schedule:
                system = base
                if condition == "evidence_check":
                    system += (
                        " 답을 쓰기 전에 자료의 주제 관련성, 주장을 뒷받침하는 내용, "
                        "버전과 조건의 일치, 자료 사이의 충돌, 답에 필요한 증거가 충분한지를 "
                        "각각 확인하세요. 확인 과정은 출력하지 않아도 됩니다."
                    )
                record = await execute(f'{case["id"]}-{condition}',
                    json.dumps({"question": case["question"], "documents": case["documents"]},
                               ensure_ascii=False), args, workspace, system)
                if record["error"] or (record["result"] or {}).get("is_error"):
                    break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=["hooks", "evidence"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--cli", default=shutil.which("claude"))
    parser.add_argument("--sdk-revision", required=True)
    arguments = parser.parse_args()
    if not arguments.cli:
        parser.error("claude 실행 파일이 필요합니다.")
    if arguments.suite == "evidence" and arguments.cases is None:
        parser.error("evidence 실험에는 --cases가 필요합니다.")
    asyncio.run(main(arguments))
