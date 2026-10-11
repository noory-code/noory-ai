"""업데이트 전후의 결과를 구별하고 남은 비교가 끝났는지 확인합니다."""

from __future__ import annotations

import json
from pathlib import Path

import criteria as C
import prepare as P
import summarize as S
import summarize_retry as V

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "after-update"


def group_by_version(rows: list[dict]) -> list[dict]:
    result = []
    for version in sorted({row["cli_version"] for row in rows}):
        values = [row for row in rows if row["cli_version"] == version and not row["error"]]
        for group in V.aggregate(values):
            result.append({"cli_version": version, **group})
    return result


def main() -> None:
    manifest = S.read(OUT / "manifest.json")
    errors = []
    for name, expected in manifest["source_hashes"].items():
        if S.digest(P.REPO / name) != expected:
            errors.append(f"실행기가 달라졌습니다: {name}")
    for name, expected in manifest["previous_record_hashes"].items():
        if S.digest(ROOT / name) != expected:
            errors.append(f"이전 기록이 달라졌습니다: {name}")
    previous = S.read(ROOT / "retry-3/summary.json")
    criteria_rows = previous["criteria"]["all_attempts"]
    freshness_rows = previous["freshness"]["all_attempts"]
    native_rows = previous["native_handoff"]["all_attempts"]
    for row in criteria_rows + freshness_rows:
        row["cli_version"] = manifest["previous_cli_versions"][row["host"]]
    for row in native_rows:
        row["cli_version"] = manifest["previous_cli_versions"][row["receiver"]]
    requests = {entry["id"]: entry for entry in manifest["requests"]}
    calls, seen, fresh_native = [], set(), []
    checked = V.extraction_check(S.read(ROOT / manifest["source_extraction"]))
    if checked["errors"]:
        errors.append("재사용한 기준이 출처 검사를 통과하지 못했습니다.")
    for path in sorted((OUT / "choices").glob("*/*.json")):
        row = S.read(path)
        entry = requests[row["id"]]
        cli = row["cli"]
        calls.append(cli)
        V.prompt_check(cli, entry["prompt"], errors, str(path.relative_to(ROOT)))
        record = {key: row[key] for key in ("host", "condition")}
        record.update({"answer": cli["answer"], "error": cli["error"], "usage": S.usage(cli),
                       "record": str(path.relative_to(ROOT)),
                       "cli_version": manifest["cli_versions"][row["host"]]})
        if row["kind"] == "criteria":
            case = next(case for case in C.CASES if case["id"] == row["case"])
            payload = {"policy": C.POLICY, "task": case["task"],
                       "allowed_actions_and_targets": case["actions"],
                       "records": C.NOTES if row["condition"] == "raw_notes" else checked["rules"]}
            V.prompt_check(cli, C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False),
                           errors, row["id"])
            matches = C.CLI.matches(cli["answer"], case["expected"]) if not cli["error"] else None
            if matches != row["matches"]:
                errors.append(f"판단 채점이 다릅니다: {row['id']}")
            criteria_rows.append({**record, "case": row["case"], "matches": matches})
        else:
            freshness_rows.append({**record, "repeat": row["repeat"]})
        if not cli["error"]:
            seen.add(row["id"])
    for path in sorted((OUT / "runs").glob("*/*/result.json")):
        row = V.native_row(path, errors)
        row["cli_version"] = manifest["cli_versions"][row["receiver"]]
        fresh_native.append(row)
        native_rows.append(row)
        calls.append(S.read(path.parent / "cli.json"))
    criteria_success = [row for row in criteria_rows if not row["error"]]
    freshness_success = [row for row in freshness_rows if not row["error"]]
    native_completed = [row for row in native_rows
                        if not row["cli_error"] and isinstance(row["declared_complete"], bool)]
    criteria_keys = {(row["case"], row["condition"]) for row in criteria_success}
    freshness_keys = {(row["host"], row["condition"], row["repeat"]) for row in freshness_success}
    native_keys = {(row["case"], row["receiver"], row["condition"]) for row in native_completed}
    if len(criteria_keys) != len(criteria_success) or len(freshness_keys) != len(freshness_success):
        errors.append("같은 조건의 성공을 두 번 세었습니다.")
    completed = len(criteria_keys) == 12 and len(freshness_keys) == 12 and len(native_keys) == 8
    summary = {
        "validation_errors": errors, "source_sha256": S.digest(Path(__file__)),
        "previous_records_unchanged": len(manifest["previous_record_hashes"]),
        "previous_cli_versions": manifest["previous_cli_versions"],
        "cli_versions": manifest["cli_versions"],
        "new_calls": len(calls), "new_cli_errors": sum(bool(cli["error"]) for cli in calls),
        "all_calls": previous["all_cli_calls"] + len(calls),
        "all_cli_errors": previous["all_cli_errors"] + sum(bool(cli["error"]) for cli in calls),
        "claude_reported_cost_usd": previous["all_claude_reported_cost_usd"],
        "codex_cost_usd": None,
        "criteria": {"all_attempts": criteria_rows, "successful_conditions": len(criteria_keys),
                     "matching_answers": sum(row["matches"] for row in criteria_success),
                     "groups_by_version": group_by_version(criteria_rows)},
        "freshness": {"all_attempts": freshness_rows, "successful_conditions": len(freshness_keys),
                      "groups_by_version": group_by_version(freshness_rows)},
        "native_handoff": {"all_attempts": native_rows, "completed_conditions": len(native_keys),
                           "verified_and_declared_complete": sum(row["success"] for row in native_completed)},
        "new_successful_choice_requests": len(seen),
        "planned_comparisons_have_results": completed,
        "limits": ["CLI 업데이트 전후의 시간과 토큰을 같은 환경의 반복처럼 비교하지 않습니다.",
                   "과거 실패를 유지하며 출처 단위를 명시한 추출은 별도 조건으로 다룹니다.",
                   "전체 Stage 운영 검증과 실무 재사용률 관측은 포함하지 않습니다."]}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in (
        "validation_errors", "previous_records_unchanged", "new_calls", "new_cli_errors",
        "all_calls", "all_cli_errors", "planned_comparisons_have_results")},
        ensure_ascii=False, indent=2))
    print(json.dumps({"criteria": summary["criteria"]["groups_by_version"],
                      "freshness": summary["freshness"]["groups_by_version"],
                      "native": [{key: row[key] for key in (
                          "condition", "success", "seconds_including_verification",
                          "tool_count", "explicit_observation_read_calls", "usage")}
                          for row in fresh_native]}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
