"""자료가 빠졌던 목적 문제와 모호한 기억 범위를 보완해 따로 실행합니다."""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
from pathlib import Path

import run_followup as runner

ROOT = Path(__file__).resolve().parents[1]


async def main() -> None:
    original = json.loads((ROOT / "followup-cases.json").read_text(encoding="utf-8"))
    rubric = json.loads((ROOT / "followup-rubric.json").read_text(encoding="utf-8"))
    materials = {
        "clear_report": "분석할 코드는 def total(xs): return sum([x for x in xs]) 입니다. 출력은 채팅 보고서입니다.",
        "clear_edit": "대상 /lab/notice.txt 내용은 '안녕하새요'입니다. '안녕하세요'로 고치는 오타 한 개입니다.",
        "clear_draft": "모임은 10월 10일 오후 3시 회의실 A에서 합니다. 목적은 분기 회고이며 참석 대상은 팀원입니다.",
        "clear_missing": "비교할 문서는 여전히 특정되지 않았습니다.",
        "example_cafe": "승인 절차 자료: 초안 작성 10분, 담당자 대기 2일, 검토 30분, 최종 승인 대기 3일입니다. 이 자료를 기준으로 조사 보고서를 쓰면 됩니다.",
        "example_archive": "자료는 보고서 100개와 회의록 50개입니다. 현재 연도와 팀 이름만 폴더로 구분돼 있고 검색어로 제목을 찾습니다. 이 조건에서 정리 방법을 비교해주세요.",
        "example_post": "모임 내용: 10월 10일 오후 3시 회의실 A, 팀원 대상 분기 회고. 회사 공지처럼 정중하고 간결하게 작성합니다.",
        "example_edit": "대상 /lab/title.md 제목은 '이번 달에 진행할 정기 회의에 관한 안내'입니다. 예시 제목은 '정기 회의 안내'입니다. 본문은 '월요일 오후 3시에 모입니다.'입니다.",
        "revised_report": "대상 /lab/calc.py의 코드는 def total(xs): return sum([x for x in xs]) 입니다. 최신 요구대로 분석할 자료가 모두 있습니다.",
        "revised_edit": "승인한 수정은 /lab/notice.txt의 '안녕하새요'를 '안녕하세요'로 바꾸는 것입니다. 대상 파일과 내용이 제공됐습니다.",
        "revised_draft": "공지 내용은 10월 10일 오후 3시 회의실 A에서 팀 회고를 한다는 안내입니다. 초안에 필요한 정보는 모두 제공됐습니다.",
        "revised_continue": "남은 연구자료와 보고서 목차는 이미 제공됐습니다. 외부 승인이나 추가 정보 없이 조사를 계속할 수 있는 상태입니다.",
    }
    cases = []
    expected = {}
    for case in original:
        if case["family"] not in ("H01", "H05"):
            continue
        item = json.loads(json.dumps(case))
        if item["family"] == "H01":
            for condition in item["variants"]:
                item["variants"][condition] += "\n제공된 자료: " + materials[item["id"]]
        else:
            item["variants"]["conclusion_only"] += " 저장 기록의 적용 버전 필드는 미기록 상태입니다."
        item["id"] = "repaired_" + item["id"]
        cases.append(item)
        expected[item["id"]] = rubric[case["id"]]
    data_files = {"repaired-cases.json": cases, "repaired-rubric.json": expected}
    for filename, data in data_files.items():
        path = ROOT / filename
        if path.exists() and json.loads(path.read_text(encoding="utf-8")) != data:
            raise ValueError("이미 고정한 보완 문제와 다릅니다.")
        runner.save(path, data)
    runner.OUT = ROOT / "runs" / "2026-10-05-repaired"
    runner.OUT.mkdir(parents=True, exist_ok=True)
    schedule = [(c, v, r) for c in cases for v in c["variants"] for r in range(1, 4)]
    random.Random(2026100503).shuffle(schedule)
    manifest = {
        "purpose": "앞선 결과를 읽은 뒤 평가 자료를 보완했습니다. 독립된 최종 시험은 아닙니다.",
        "base_runner_sha256": hashlib.sha256(Path(runner.__file__).read_bytes()).hexdigest(),
        "repair_runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_hashes": {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
                          for n in data_files},
        "same_runtime_as": "2026-10-05-followup/manifest.json",
        "schedule": [{"case": c["id"], "condition": v, "repeat": r}
                     for c, v, r in schedule],
        "remaining_reported_budget_usd": 3.8,
    }
    runner.save(runner.OUT / "manifest.json", manifest)
    spent = 0.0
    for offset in range(0, len(schedule), 2):
        if spent + 0.30 > 3.8:
            raise RuntimeError("후속 실험 전체 한도를 지키기 위해 멈춥니다.")
        records = await asyncio.gather(*(runner.execute(*entry)
                                        for entry in schedule[offset:offset + 2]))
        for record in records:
            result = record.get("result") or {}
            spent += result.get("total_cost_usd") or 0
            print(json.dumps({"run_id": record["run_id"], "error": record["error"],
                              "is_error": result.get("is_error"),
                              "cumulative_reported_usd": round(spent, 6)}), flush=True)
        if any(r["error"] or not r["result"] or r["result"].get("is_error") for r in records):
            raise RuntimeError("오류를 보관하고 다음 실행을 멈춥니다.")


if __name__ == "__main__":
    asyncio.run(main())
