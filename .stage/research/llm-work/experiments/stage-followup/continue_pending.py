"""성공한 추출과 판단은 재사용하고 일시적인 서버 오류만 제한해서 재시도합니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path

import criteria as C
import resume
import retry as R
import summarize_retry as V

ROOT = Path(__file__).resolve().parent


def plan() -> tuple[dict, list[dict]]:
    base = R.read(ROOT / "retry-2/manifest.json")
    extract_path = ROOT / "retry-2/criteria-single-source/extract--codex.json"
    extract = R.read(extract_path)
    check = V.extraction_check(extract)
    if extract["error"] or check["errors"]:
        raise ValueError("검증된 추출 결과가 없습니다.")
    requests, retained = [], []
    for index, case in enumerate(C.CASES):
        conditions = ["raw_notes", "extracted_rules"]
        if (index + 1) % 2:
            conditions.reverse()
        for condition in conditions:
            previous = ROOT / "retry-2/criteria-single-source" / f"{case['id']}--codex--{condition}.json"
            payload = {"policy": C.POLICY, "task": case["task"],
                       "allowed_actions_and_targets": case["actions"],
                       "records": C.NOTES if condition == "raw_notes" else check["rules"]}
            prompt = C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False)
            if previous.exists() and not R.read(previous)["cli"]["error"]:
                prior = R.read(previous)["cli"]
                if prior["prompt"] != prompt:
                    raise ValueError("보존할 성공 기록의 입력이 다릅니다.")
                retained.append(str(previous.relative_to(ROOT)))
                continue
            requests.append({"kind": "criteria", "case": case["id"], "condition": condition,
                             "id": f"criteria--{case['id']}--{condition}", "prompt": prompt,
                             "expected": case["expected"]})
    for host, condition, repeat in base["freshness_schedule"]:
        requests.append({"kind": "freshness", "host": host, "condition": condition,
                         "repeat": repeat, "id": f"freshness--{condition}--r{repeat}",
                         "prompt": base["freshness_manifest"]["prompts"][condition]})
    previous_files = sorted(path for folder in (
        "runs", "criteria-runs", "freshness-runs", "retry-1", "retry-2")
        for path in (ROOT / folder).rglob("*.json"))
    sources = dict(base["source_hashes"])
    for name, expected in sources.items():
        if R.digest(R.P.REPO / name) != expected:
            raise ValueError(f"실행기가 달라졌습니다: {name}")
    sources.update({str(path.relative_to(R.P.REPO)): R.digest(path)
                    for path in (Path(__file__), ROOT / "summarize_retry.py")})
    manifest = {"started_at": datetime.now(timezone.utc).isoformat(),
                "source_hashes": sources,
                "previous_record_hashes": {str(path.relative_to(ROOT)): R.digest(path)
                                           for path in previous_files},
                "source_extraction": str(extract_path.relative_to(ROOT)),
                "retained_successes": retained, "requests": requests,
                "planned_choice_requests": len(requests), "planned_native_requests": 2,
                "parallelism": 1, "seconds_between_choice_calls": 5,
                "capacity_retry_delay_seconds": 30, "max_attempts_per_choice_request": 2,
                "max_new_capacity_errors": 6,
                "reason": "성공한 추출과 두 판단은 재사용하고 남은 입력을 그대로 실행합니다.",
                "limits": ["재시도와 대기 시간도 별도로 기록합니다.",
                           "원래 실패를 지우거나 성공으로 바꾸지 않습니다.",
                           "서버 오류와 기대 답이 다른 판단을 구별합니다."]}
    return manifest, requests


async def main() -> None:
    R.OUT = ROOT / "retry-3"
    if R.OUT.exists():
        raise FileExistsError("이전 이어가기 기록을 덮어쓰지 않습니다.")
    manifest, requests = plan()
    R.save(R.OUT / "manifest.json", manifest)
    status = {"completed_requests": [], "capacity_errors": 0, "error": None}
    try:
        for entry in requests:
            status["request"] = entry["id"]
            for attempt in range(1, 3):
                result = await C.CLI.invoke("codex", entry["prompt"])
                matches = (bool(result["answer"] and C.CLI.matches(result["answer"], entry["expected"]))
                           if entry["kind"] == "criteria" and not result["error"] else None)
                row = {key: value for key, value in entry.items() if key not in {"prompt", "expected"}}
                row.update({"host": "codex", "attempt": attempt, "cli": result, "matches": matches})
                R.save(R.OUT / "choices" / entry["id"] / f"attempt-{attempt}.json", row)
                print(json.dumps({"id": entry["id"], "attempt": attempt,
                                  "matches": matches, "error": result["error"]}), flush=True)
                if not result["error"]:
                    status["completed_requests"].append(entry["id"])
                    break
                capacity = "Selected model is at capacity" in json.dumps(result["events"])
                if capacity:
                    status["capacity_errors"] += 1
                if not capacity or attempt == 2 or status["capacity_errors"] >= 6:
                    raise RuntimeError("정한 재시도 한도에서 응답을 받지 못했습니다.")
                R.save(R.OUT / "status.json", status)
                print("서버 혼잡 뒤 30초를 기다립니다.", flush=True)
                await asyncio.sleep(30)
            R.save(R.OUT / "status.json", status)
            await asyncio.sleep(5)
        status["phase"] = "native_handoff"
        R.save(R.OUT / "status.json", status)
        await resume.handoff()
        status["completed_requests"].extend(["native--stage_card", "native--stage_card_observation"])
    except Exception as error:
        status["error"] = str(error)
        raise
    finally:
        status["stopped_at"] = datetime.now(timezone.utc).isoformat()
        R.save(R.OUT / "status.json", status)


if __name__ == "__main__":
    asyncio.run(main())
