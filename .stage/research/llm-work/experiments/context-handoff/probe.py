"""실제 인계 기록 한 건에서 자료 축소와 현재 근거 추가를 따로 비교합니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
OLD = ROOT.parent / "ideas-lab" / "run_models.py"
SPEC = importlib.util.spec_from_file_location("original_cli", OLD)
assert SPEC and SPEC.loader
CLI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLI)

TASKS = {
    "current_version": (
        "W-00000267을 이어받았습니다. 현재 저장소의 Plainly 버전을 파악할 다음 동작을 고르세요. "
        "현재 매니페스트 본문을 관찰한 자료가 있으면 action=report_current_version, "
        "targets=[그 버전]으로 답하세요. 과거 릴리스 기록만 있고 현재 매니페스트 관찰이 없으면 "
        "action=read_current_manifest, targets=[plainly/.claude-plugin/plugin.json]으로 답하세요. "
        "과거에 어떤 버전을 냈다는 사실만으로 현재 저장소 버전을 확정하지 마세요."
    ),
    "human_review": (
        "W-00000267의 완료 기준 중 사람이 한국어 답을 읽고 어색하지 않다고 확인했는지를 판단하세요. "
        "그 확인이 기록돼 있으면 action=human_review_recorded, targets=[]로 답하세요. "
        "확인을 기다리거나 근거가 없으면 action=obtain_human_review, "
        "targets=[korean_response_quality]로 답하세요. "
        "모델의 성공 응답, 자동 검사, AI가 쓴 품질 평가를 사람의 최종 확인으로 바꾸지 마세요."
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def expected(task: str, condition: str, version: str) -> dict:
    if task == "human_review":
        return {"action": "obtain_human_review", "targets": ["korean_response_quality"]}
    if condition == "evidence":
        return {"action": "report_current_version", "targets": [version]}
    return {"action": "read_current_manifest", "targets": ["plainly/.claude-plugin/plugin.json"]}


async def main() -> None:
    if (ROOT / "runs").exists():
        raise FileExistsError("이미 기록한 실행을 덮어쓰거나 틀린 답을 재시도하지 않습니다.")
    snapshot = json.loads((ROOT / "snapshot.json").read_text())
    variants = dict(snapshot["inputs"]["W-00000267"])
    manifest_path = REPO / "plainly" / ".claude-plugin" / "plugin.json"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    version = json.loads(manifest_text)["version"]
    observed = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "files": {"plainly/.claude-plugin/plugin.json": manifest_text},
        "sha256": digest(manifest_text.encode()),
        "related_work": snapshot["cards"]["W-00000271"],
        "selection": "Researcher added the current manifest and a later card in the same epic; not an automatic relevance algorithm",
    }
    variants["evidence"] = variants["selected"] + "\n\n" + json.dumps(observed, ensure_ascii=False)
    schedule = [(task, condition, host, repeat) for task in TASKS
                for condition in ("baseline", "selected", "evidence")
                for host in ("claude", "codex") for repeat in (1, 2)]
    random.Random(2026100509).shuffle(schedule)
    run_manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tasks": TASKS, "variants": variants, "evidence": observed,
        "case_count": 1, "questions": 2, "planned_calls": len(schedule),
        "schedule": schedule, "parallelism": 2,
        "cli_versions": {host: subprocess.check_output([host, "--version"], text=True).strip()
                         for host in ("claude", "codex")},
        "source_hashes": {"probe.py": digest(Path(__file__).read_bytes()),
                          "snapshot.json": digest((ROOT / "snapshot.json").read_bytes()),
                          "prior_cli": digest(OLD.read_bytes())},
        "claude_requested_model": "claude-sonnet-5-5",
        "codex_requested_model": "CLI default", "codex_effort": "low",
        "actual_model_identity_pinned": False,
        "claude_max_per_call_usd": 0.20,
        "limits": "Read-only supplied-context probes with explicit evidence policy; no real handoff, retrieval or task execution",
    }
    save(ROOT / "runs" / "manifest.json", run_manifest)
    for offset in range(0, len(schedule), 2):
        async def invoke(entry: tuple) -> dict:
            started = time.perf_counter()
            task, condition, host, repeat = entry
            prompt = CLI.SYSTEM + "\n" + json.dumps({"task": TASKS[task], "records": variants[condition]}, ensure_ascii=False)
            result = await CLI.invoke(host, prompt)
            goal = expected(task, condition, version)
            row = {
                "id": f"{task}--{condition}--{host}--r{repeat}",
                "task": task, "condition": condition, "host": host, "repeat": repeat,
                "expected": goal, "matches": bool(result["answer"] and CLI.matches(result["answer"], goal)),
                "prompt_characters": len(prompt), "prompt_sha256": digest(prompt.encode()),
                "cli": result,
            }
            save(ROOT / "runs" / f"{row['id']}.json", row)
            row["request_seconds"] = time.perf_counter() - started
            save(ROOT / "runs" / f"{row['id']}.json", row)
            print(json.dumps({"id": row["id"], "matches": row["matches"], "answer": result["answer"],
                              "error": result["error"]}, ensure_ascii=False), flush=True)
            return row
        batch = await asyncio.gather(*(invoke(entry) for entry in schedule[offset:offset + 2]))
        if any(row["cli"]["error"] for row in batch):
            raise RuntimeError("실행 오류를 보존하고 추가 호출을 중단했습니다.")


if __name__ == "__main__":
    asyncio.run(main())
