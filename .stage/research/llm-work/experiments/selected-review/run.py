"""원문과 선택한 코드를 같은 정책으로 검토하고 모든 응답을 남깁니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

from selector import select_source

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "ideas-lab/run_models.py"
SPEC = importlib.util.spec_from_file_location("original_cli", OLD)
CLI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLI)
POLICY = (
    "제공한 Python 코드가 명시한 기준 하나를 만족하는지 검토하세요. "
    "전체 파일 또는 같은 모듈에서 선택한 함수가 제공됩니다. 외부 모듈과 환경은 기준에 적힌 전제를 따릅니다. "
    "기준을 만족하면 action=approve, targets=[]로 답하세요. "
    "위반하면 action=revise, targets=[기준 id]로 답하세요. "
    "판단할 코드가 없거나 연결된 동작의 근거가 부족하면 action=uncertain, targets=[기준 id]로 답하세요. "
    "다른 기능이나 일반적인 코드 품질은 평가하지 마세요. reason에는 코드에서 확인한 근거를 적으세요."
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_prompt(case: dict, condition: str) -> tuple[str, dict]:
    files, selections = {}, {}
    for name, source in case["files"].items():
        selected = select_source(source, case["entry"]) if condition == "selected" else {
            "source": source, "mode": "full", "reason": "requested_full", "symbols": []}
        files[name] = selected["source"]
        selections[name] = {key: selected[key] for key in ("mode", "reason", "symbols")}
    payload = {"instruction": POLICY,
               "criterion": {"id": case["criterion_id"], "text": case["criterion"]},
               "files": files}
    return CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False), selections


def schedule_for(host: str, cases: list[dict]) -> list[dict]:
    schedule = []
    for repeat in (1, 2):
        for index, case in enumerate(cases):
            if case["kind"] == "missing_source" and repeat == 2:
                continue
            conditions = ["full", "selected"]
            if (repeat + index + (host == "codex")) % 2:
                conditions.reverse()
            for condition in conditions:
                schedule.append({"host": host, "case": case["id"],
                                 "condition": condition, "repeat": repeat})
    return schedule


async def lane(host: str, schedule: list[dict]) -> dict:
    calls = 0
    cost = 0.0
    for entry in schedule:
        started = time.perf_counter()
        cases = json.loads((ROOT / "fixtures.json").read_text())
        case = next(row for row in cases if row["id"] == entry["case"])
        prompt, selections = build_prompt(case, entry["condition"])
        prompt_hash = digest(prompt.encode())
        preparation_seconds = time.perf_counter() - started
        cli = await CLI.invoke(host, prompt)
        record = {**entry, "kind": case["kind"], "prompt_sha256": prompt_hash,
                  "prompt_characters": len(prompt), "selections": selections,
                  "preparation_seconds": preparation_seconds, "cli": cli,
                  "expected": case["expected"],
                  "matches": bool(not cli["error"] and cli["answer"]
                                  and CLI.matches(cli["answer"], case["expected"]))}
        run_id = f"{entry['case']}--{host}--{entry['condition']}--r{entry['repeat']}"
        path = ROOT / "runs" / f"{run_id}.json"
        if path.exists():
            raise FileExistsError(path)
        save(path, record)
        record["request_seconds"] = time.perf_counter() - started
        save(path, record)
        calls += 1
        cost += (cli["result"] or {}).get("total_cost_usd", 0) or 0
        print(json.dumps({"id": run_id, "matches": record["matches"], "error": cli["error"],
                          "seconds": round(record["request_seconds"], 3)}, ensure_ascii=False), flush=True)
        if cli["error"]:
            return {"host": host, "calls": calls, "stopped_on_error": run_id,
                    "reported_cost_usd": cost if host == "claude" else None}
    return {"host": host, "calls": calls, "stopped_on_error": None,
            "reported_cost_usd": cost if host == "claude" else None}


async def main() -> None:
    if (ROOT / "runs").exists():
        raise FileExistsError("기존 실행을 덮어쓰거나 실패한 답을 재시도하지 않습니다.")
    cases = json.loads((ROOT / "fixtures.json").read_text())
    schedules = {host: schedule_for(host, cases) for host in ("claude", "codex")}
    source_paths = list(ROOT.glob("*.py")) + [ROOT / "fixtures.json", ROOT / "regression-results.json", ROOT / "README.md", OLD]
    manifest = {"started_at": datetime.now(timezone.utc).isoformat(),
                "planned_calls": sum(len(entries) for entries in schedules.values()),
                "historical_defects": 2, "schedules": schedules,
                "sources": {path.relative_to(ROOT.parent).as_posix(): digest(path.read_bytes())
                            for path in source_paths},
                "cli_versions": {host: subprocess.check_output([host, "--version"], text=True).strip()
                                 for host in schedules},
                "claude_requested_model": "claude-sonnet-5-5", "codex_requested_model": "CLI default",
                "codex_effort": "low", "actual_model_identity_pinned": False,
                "claude_max_reported_cost_usd": 3.60,
                "policy": POLICY, "parallelism": 2,
                "note": "두 과제는 앞선 연구에서 사용했습니다. 결과를 본 뒤 시작점이나 선택 규칙을 바꾸지 않습니다."}
    save(ROOT / "runs/manifest.json", manifest)
    results = await asyncio.gather(*(lane(host, schedule) for host, schedule in schedules.items()))
    save(ROOT / "runs/status.json", {"hosts": results,
         "ended_at": datetime.now(timezone.utc).isoformat()})
    if any(row["stopped_on_error"] for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
