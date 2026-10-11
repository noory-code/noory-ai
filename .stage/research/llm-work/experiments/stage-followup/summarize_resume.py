"""이어간 비교의 입력과 결과를 원본에 대조합니다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import criteria as C
import prepare as P
import summarize as S
import summarize_retry as V

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="retry-2")
    args = parser.parse_args()
    out = ROOT / args.output
    manifest = S.read(out / "manifest.json")
    errors, previous_calls, calls = [], [], []
    for name, expected in manifest["source_hashes"].items():
        if S.digest(P.REPO / name) != expected:
            errors.append(f"실행기가 달라졌습니다: {name}")
    for name, expected in manifest["original_record_hashes"].items():
        if S.digest(ROOT / name) != expected:
            errors.append(f"이전 기록이 달라졌습니다: {name}")
        data = S.read(ROOT / name)
        if isinstance(data, dict):
            if "cli" in data:
                previous_calls.append(data["cli"])
            elif "host" in data and "input_sha256" in data:
                previous_calls.append(data)
    extraction, decisions = None, []
    path = out / "criteria-single-source/extract--codex.json"
    if path.exists():
        cli = S.read(path)
        calls.append(cli)
        V.prompt_check(cli, manifest["amended_extraction_prompt"], errors, "extract")
        checked = V.extraction_check(cli)
        check_path = path.with_name("extraction-check--codex.json")
        if check_path.exists():
            saved = S.read(check_path)
            if saved["rules"] != checked["rules"] or bool(saved["errors"]) != bool(checked["errors"]):
                errors.append("추출 검사 결과가 다릅니다.")
        extraction = {"cli_error": cli["error"], "contract_passed": not checked["errors"],
                      "usage": S.usage(cli), **checked}
        for path in sorted((out / "criteria-single-source").glob("*--codex--*.json")):
            row = S.read(path)
            cli = row["cli"]
            calls.append(cli)
            case = next(case for case in C.CASES if case["id"] == row["case"])
            payload = {"policy": C.POLICY, "task": case["task"],
                       "allowed_actions_and_targets": case["actions"],
                       "records": C.NOTES if row["condition"] == "raw_notes" else checked["rules"]}
            V.prompt_check(cli, C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False),
                           errors, path.name)
            actual = bool(cli["answer"] and C.CLI.matches(cli["answer"], case["expected"]))
            if actual != row["matches"]:
                errors.append(f"채점 결과가 다릅니다: {path.name}")
            decisions.append({key: row[key] for key in ("host", "case", "condition", "matches")}
                             | {"answer": cli["answer"], "error": cli["error"], "usage": S.usage(cli)})
    freshness, handoffs = [], []
    for path in sorted((out / "freshness-runs").glob("*--*--*.json")):
        row = S.read(path)
        cli = row["cli"]
        calls.append(cli)
        V.prompt_check(cli, manifest["freshness_manifest"]["prompts"][row["condition"]],
                       errors, path.name)
        freshness.append({key: row[key] for key in ("host", "condition", "repeat")}
                         | {"answer": cli["answer"], "error": cli["error"], "usage": S.usage(cli)})
    for path in sorted((out / "runs").glob("*/*/result.json")):
        handoffs.append(V.native_row(path, errors))
        calls.append(S.read(path.parent / "cli.json"))
    all_calls = previous_calls + calls
    old = S.read(ROOT / "retry-1/summary.json")
    all_handoffs = old["native_all_attempts"] + handoffs
    covered = {(row["case"], row["receiver"], row["condition"])
               for row in all_handoffs if row["success"]}
    done = (bool(extraction and extraction["contract_passed"])
            and len(decisions) == 12 and len(freshness) == 6 and len(handoffs) == 2
            and all(row["success"] for row in handoffs)
            and not any(cli["error"] for cli in calls))
    summary = {
        "validation_errors": errors, "source_sha256": S.digest(Path(__file__)),
        "validation_helper_sha256": S.digest(ROOT / "summarize_retry.py"),
        "previous_records_unchanged": len(manifest["original_record_hashes"]),
        "cli_versions_unchanged": manifest["cli_versions"] == manifest["previous_cli_versions"],
        "this_calls": len(calls), "this_cli_errors": sum(bool(cli["error"]) for cli in calls),
        "all_calls": len(all_calls), "all_cli_errors": sum(bool(cli["error"]) for cli in all_calls),
        "all_claude_reported_cost_usd": sum(S.usage(cli)["claude_reported_cost_usd"]
                                            for cli in all_calls if cli["host"] == "claude"),
        "codex_cost_usd": None, "extraction": extraction,
        "criteria": {"rows": decisions, "groups": V.aggregate(decisions)},
        "freshness": {"rows": freshness, "groups": V.aggregate(freshness)},
        "native_handoff": handoffs, "native_all_attempts": all_handoffs,
        "native_successful_unique_conditions": len(covered),
        "native_total_attempts": len(all_handoffs),
        "pending_comparisons_completed": done,
        "limits": ["원래 추출 요청과 출처 단위를 명시한 요청의 결과를 구별합니다.",
                   "같은 CLI 설정을 유지했지만 모델 ID를 명시적으로 고정하지 않았습니다.",
                   "시점이 다른 탐색 실험이며 전체 Stage 운영 과정과 실무 절감률을 증명하지 않습니다."]}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in (
        "validation_errors", "previous_records_unchanged", "cli_versions_unchanged",
        "this_calls", "this_cli_errors", "all_calls", "all_cli_errors",
        "native_successful_unique_conditions", "pending_comparisons_completed")},
        ensure_ascii=False, indent=2))
    print(json.dumps({"criteria": summary["criteria"]["groups"],
                      "freshness": summary["freshness"]["groups"],
                      "native": [{key: row[key] for key in (
                          "condition", "success", "seconds_including_verification",
                          "tool_count", "explicit_observation_read_calls", "usage")}
                          for row in handoffs]}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
