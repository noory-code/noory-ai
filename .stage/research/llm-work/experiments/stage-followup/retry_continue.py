"""추출 계약을 명확히 한 별도 비교와 독립된 나머지 시험을 수행합니다."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path

import criteria as C
import retry as R


async def clarified_criteria(prompt: str) -> None:
    out = R.OUT / "criteria-single-source"
    result = await C.CLI.invoke("codex", prompt)
    R.save(out / "extract--codex.json", result)
    print(json.dumps({"single_source_extraction": "codex", "error": result["error"]}), flush=True)
    if result["error"]:
        raise RuntimeError("출처 형식을 명시한 추출 호출 오류를 보존했습니다.")
    rules, errors = [], []
    answer = result["answer"]
    if answer["action"] != "extract_rules" or not answer["targets"]:
        errors.append("기준 추출 응답이 아니거나 기준이 없습니다.")
    for index, item in enumerate(answer["targets"]):
        try:
            rule = json.loads(item)
            if set(rule) != {"rule", "project", "status", "source", "quote"}:
                raise ValueError("기준 필드 오류")
            notes = {note["id"]: note["text"] for note in C.NOTES}
            if rule["source"] not in notes:
                raise ValueError("한 개의 원문 ID와 대응하지 않습니다.")
            if not rule["quote"] or rule["quote"] not in notes[rule["source"]]:
                raise ValueError("해당 원문에 그대로 들어 있는 인용이 아닙니다.")
            if rule["status"] not in {"confirmed", "unconfirmed"}:
                raise ValueError("상태 오류")
            rules.append(rule)
        except (ValueError, KeyError, TypeError) as error:
            errors.append({"index": index, "message": str(error)})
    R.save(out / "extraction-check--codex.json", {"rules": rules, "errors": errors})
    if errors:
        raise RuntimeError("명시한 계약도 충족하지 못했습니다. 추가로 고쳐 재시도하지 않습니다.")
    for index, case in enumerate(C.CASES):
        conditions = ["raw_notes", "extracted_rules"]
        if (index + 1) % 2:
            conditions.reverse()
        for condition in conditions:
            payload = {"policy": C.POLICY, "task": case["task"],
                       "allowed_actions_and_targets": case["actions"],
                       "records": C.NOTES if condition == "raw_notes" else rules}
            result = await C.CLI.invoke(
                "codex", C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False))
            row = {"host": "codex", "case": case["id"], "condition": condition, "cli": result,
                   "matches": bool(result["answer"] and C.CLI.matches(result["answer"], case["expected"]))}
            R.save(out / f"{case['id']}--codex--{condition}.json", row)
            print(json.dumps({"criteria": case["id"], "condition": condition,
                              "matches": row["matches"], "error": result["error"]}), flush=True)
            if result["error"]:
                raise RuntimeError("별도 기준 비교 호출 오류를 보존했습니다.")


async def main() -> None:
    path = R.OUT / "continuation-manifest.json"
    if path.exists():
        raise FileExistsError("기존 후속 시험 기록을 덮어쓰지 않습니다.")
    manifest = R.read(R.OUT / "manifest.json")
    first = R.read(R.OUT / "criteria-runs/extract--codex.json")
    check = R.read(R.OUT / "criteria-runs/extraction-check--codex.json")
    if first["error"] or not check["errors"]:
        raise ValueError("이 후속 실행은 추출 형식이 맞지 않았을 때만 사용합니다.")
    prefix, payload = first["prompt"].rsplit("\n", 1)
    task = json.loads(payload)
    clarification = (
        " 각 객체의 source에는 N1부터 N5 중 원문 ID를 정확히 한 개만 적으세요. "
        "quote에는 그 source의 원문에 연속해서 들어 있는 문자열만 적으세요. "
        "두 원문을 합쳐야 하면 객체를 나누세요. 여러 출처나 인용을 쉼표 또는 슬래시로 합치지 마세요.")
    task["task"] += clarification
    prompt = prefix + "\n" + json.dumps(task, ensure_ascii=False)
    R.save(path, {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": R.digest(Path(__file__)),
        "retry_runner_sha256": R.digest(R.ROOT / "retry.py"),
        "parent_manifest_sha256": R.digest(R.OUT / "manifest.json"),
        "original_extraction_sha256": R.digest(R.OUT / "criteria-runs/extract--codex.json"),
        "reason": "CLI는 정상 종료했지만 N2와 N3를 한 출처와 인용으로 합쳐 추출 계약을 통과하지 못했습니다.",
        "amendment": clarification, "amended_extraction_prompt": prompt,
        "planned_calls": {"freshness": 6, "native_handoff": 4,
                          "clarified_extraction": 1, "clarified_criteria_decisions": 12},
        "scope": "원래 추출 실패는 그대로 두며, 수정한 요청의 성공으로 원래 점수를 바꾸지 않습니다."})
    status = {"completed_phases": [], "error": None}
    try:
        for phase, task in (("freshness", lambda: R.freshness(manifest)),
                            ("native_handoff", R.handoff),
                            ("criteria_single_source", lambda: clarified_criteria(prompt))):
            status["phase"] = phase
            await task()
            status["completed_phases"].append(phase)
            R.save(R.OUT / "continuation-status.json", status)
    except Exception as error:
        status["error"] = str(error)
        raise
    finally:
        status["stopped_at"] = datetime.now(timezone.utc).isoformat()
        R.save(R.OUT / "continuation-status.json", status)


if __name__ == "__main__":
    asyncio.run(main())
