"""모든 시도를 남기고 정상 응답을 얻은 비교를 별도로 집계합니다."""

from __future__ import annotations

import json
from pathlib import Path

import criteria as C
import prepare as P
import summarize as S
import summarize_retry as V

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "retry-3"


def main() -> None:
    manifest = S.read(OUT / "manifest.json")
    errors = []
    for name, value in manifest["source_hashes"].items():
        if S.digest(P.REPO / name) != value:
            errors.append(f"실행기가 달라졌습니다: {name}")
    for name, value in manifest["previous_record_hashes"].items():
        if S.digest(ROOT / name) != value:
            errors.append(f"이전 기록이 달라졌습니다: {name}")
    extraction = S.read(ROOT / manifest["source_extraction"])
    checked = V.extraction_check(extraction)
    if checked["errors"]:
        errors.append("이어 쓴 기준이 추출 검사를 통과하지 못했습니다.")
    criteria_rows, freshness_rows, all_calls = [], [], []
    for folder in ("runs", "criteria-runs", "freshness-runs", "retry-1", "retry-2", "retry-3"):
        for path in sorted((ROOT / folder).rglob("*.json")):
            data = S.read(path)
            if not isinstance(data, dict):
                continue
            cli = data.get("cli")
            if cli is None and "host" in data and "input_sha256" in data:
                cli = data
            if cli is None:
                continue
            all_calls.append(cli)
            if cli["input_sha256"] != C.CLI.digest(cli["prompt"].encode()):
                errors.append(f"입력 해시가 다릅니다: {path.relative_to(ROOT)}")
            if data.get("kind") == "criteria" or (
                "case" in data and "matches" in data and "cli" in data
            ):
                if folder in {"criteria-runs", "retry-1"}:
                    continue
                case = next(case for case in C.CASES if case["id"] == data["case"])
                payload = {"policy": C.POLICY, "task": case["task"],
                           "allowed_actions_and_targets": case["actions"],
                           "records": C.NOTES if data["condition"] == "raw_notes" else checked["rules"]}
                V.prompt_check(cli, C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False),
                               errors, str(path.relative_to(ROOT)))
                matches = C.CLI.matches(cli["answer"], case["expected"]) if not cli["error"] else None
                if not cli["error"] and matches != data["matches"]:
                    errors.append(f"판단 채점이 다릅니다: {path.relative_to(ROOT)}")
                criteria_rows.append({"host": "codex", "case": data["case"],
                                      "condition": data["condition"], "matches": matches,
                                      "answer": cli["answer"], "error": cli["error"],
                                      "record": str(path.relative_to(ROOT)), "usage": S.usage(cli)})
            elif data.get("kind") == "freshness" or (
                "repeat" in data and "cli" in data and data.get("condition") in {"original", "time_explicit"}
            ):
                original = S.read(ROOT / "freshness-runs/manifest.json")
                V.prompt_check(cli, original["prompts"][data["condition"]], errors,
                               str(path.relative_to(ROOT)))
                freshness_rows.append({key: data[key] for key in ("host", "condition", "repeat")}
                                      | {"answer": cli["answer"], "error": cli["error"],
                                         "record": str(path.relative_to(ROOT)), "usage": S.usage(cli)})
    requests = {entry["id"]: entry for entry in manifest["requests"]}
    for path in sorted((OUT / "choices").glob("*/*.json")):
        row = S.read(path)
        V.prompt_check(row["cli"], requests[row["id"]]["prompt"], errors, str(path.relative_to(ROOT)))
    native_rows = []
    for path in sorted((OUT / "runs").glob("*/*/result.json")):
        native_rows.append(V.native_row(path, errors))
    all_native = S.read(ROOT / "retry-1/summary.json")["native_all_attempts"] + native_rows
    criteria_success = [row for row in criteria_rows if not row["error"]]
    freshness_success = [row for row in freshness_rows if not row["error"]]
    criteria_keys = {(row["case"], row["condition"]) for row in criteria_success}
    freshness_keys = {(row["host"], row["condition"], row["repeat"]) for row in freshness_success}
    native_keys = {(row["case"], row["receiver"], row["condition"])
                   for row in all_native if row["success"]}
    if len(criteria_keys) != len(criteria_success) or len(freshness_keys) != len(freshness_success):
        errors.append("성공한 같은 조건을 두 번 세었습니다.")
    complete = len(criteria_keys) == 12 and len(freshness_keys) == 12 and len(native_keys) == 8
    status_path = OUT / "status.json"
    status = S.read(status_path) if status_path.exists() else None
    summary = {
        "validation_errors": errors, "source_sha256": S.digest(Path(__file__)),
        "previous_records_unchanged": len(manifest["previous_record_hashes"]),
        "all_cli_calls": len(all_calls),
        "all_cli_errors": sum(bool(cli["error"]) for cli in all_calls),
        "all_claude_reported_cost_usd": sum(S.usage(cli)["claude_reported_cost_usd"]
                                            for cli in all_calls if cli["host"] == "claude"),
        "codex_cost_usd": None,
        "clarified_extraction": {"usage": S.usage(extraction), **checked},
        "criteria": {"all_attempts": criteria_rows,
                     "successful_groups": V.aggregate(criteria_success),
                     "successful_unique_conditions": len(criteria_keys)},
        "freshness": {"all_attempts": freshness_rows,
                      "successful_groups": V.aggregate(freshness_success),
                      "successful_unique_conditions": len(freshness_keys)},
        "native_handoff": {"all_attempts": all_native,
                           "successful_unique_conditions": len(native_keys)},
        "recovery": {"status": status, "capacity_retry_delay_seconds": 30,
                     "seconds_between_choice_calls": 5},
        "planned_comparisons_completed": complete,
        "limits": ["실패한 시도를 남기고 정상 응답을 얻은 비교도 따로 보여 줍니다.",
                   "출처 단위를 명시한 Codex 추출은 원래 Claude 요청과 다릅니다.",
                   "전체 Stage 운영 검증과 실무 재사용률 관측은 포함하지 않습니다."]}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in (
        "validation_errors", "previous_records_unchanged", "all_cli_calls", "all_cli_errors",
        "all_claude_reported_cost_usd", "planned_comparisons_completed")}, ensure_ascii=False, indent=2))
    print(json.dumps({"criteria": summary["criteria"]["successful_groups"],
                      "freshness": summary["freshness"]["successful_groups"],
                      "native": [{key: row[key] for key in (
                          "condition", "success", "seconds_including_verification",
                          "tool_count", "explicit_observation_read_calls", "usage")}
                          for row in native_rows]}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
