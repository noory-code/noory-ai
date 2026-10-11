"""재시도 원본을 대조하고 실패와 별도 조건을 구별해 집계합니다."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import criteria as C
import native
import prepare as P
import summarize as S

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "retry-1"


def aggregate(rows: list[dict]) -> list[dict]:
    groups = S.aggregate(rows)
    for group in groups:
        selected = [row for row in rows if row["host"] == group["host"]
                    and row["condition"] == group["condition"]]
        known = [row for row in selected if row["usage"]["reported_usage_available"]]
        group["missing_usage_calls"] = len(selected) - len(known)
        for key in ("input_tokens", "output_tokens"):
            group[key] = sum(row["usage"][key] for row in known) if known else None
        if group["host"] != "claude":
            group["claude_reported_cost_usd"] = None
    return groups


def prompt_check(cli: dict, expected: str, errors: list[str], label: str) -> None:
    if cli["prompt"] != expected or native.digest(cli["prompt"]) != cli["input_sha256"]:
        errors.append(f"입력이 다릅니다: {label}")


def extraction_check(cli: dict) -> dict:
    accepted, errors = [], []
    answer = cli["answer"] or {}
    if answer.get("action") != "extract_rules" or not answer.get("targets"):
        errors.append({"message": "기준 추출 응답이 아니거나 기준이 없습니다."})
    notes = {note["id"]: note["text"] for note in C.NOTES}
    for index, item in enumerate(answer.get("targets", [])):
        try:
            rule = json.loads(item)
            if set(rule) != {"rule", "project", "status", "source", "quote"}:
                raise ValueError("기준 필드가 다릅니다.")
            if rule["source"] not in notes:
                raise ValueError(f"단일 원문 ID가 아닙니다: {rule['source']}")
            if not rule["quote"] or rule["quote"] not in notes[rule["source"]]:
                raise ValueError("연속된 원문 인용이 아닙니다.")
            if rule["status"] not in {"confirmed", "unconfirmed"}:
                raise ValueError("허용된 상태가 아닙니다.")
            accepted.append(rule)
        except (ValueError, KeyError, TypeError) as error:
            errors.append({"index": index, "message": str(error)})
    return {"rules": accepted, "errors": errors}


def native_row(path: Path, errors: list[str]) -> dict:
    result, cli = S.read(path), S.read(path.parent / "cli.json")
    prompt = native.RULES + "\n작업 카드를 읽고 이 임시 프로젝트의 일을 이어서 끝내세요: " + P.CARD
    prompt_check(cli, prompt, errors, result["id"])
    case = next(case for case in P.H.CASES if case["id"] == result["case"])
    before, after = result["initial_manifest"], result["final_manifest"]
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    outside = [name for name in changed if name != case["target"]]
    setup = S.read(path.parent.parent / "setup.json")
    seed_path = ROOT.parent / setup["seed"]
    seed_source = S.read(seed_path)["source_after"] + P.H.NOTE
    note = P.H.NOTE in result["final_source"]
    verified = result["verification"]["returncode"] == 0 and not outside and note
    checks = [changed == result["changed_paths"], outside == result["outside_target_changes"],
              S.digest(seed_path) == setup["seed_sha256"],
              native.digest(seed_source) == setup["target_sha256"],
              before[case["target"]] == setup["target_sha256"],
              native.digest(result["final_source"]) == after[case["target"]],
              result["note_preserved"] == note, result["verified"] == verified,
              result["success"] == (verified and (cli["answer"] or {}).get("complete") is True)]
    if not all(checks):
        errors.append(f"인계 결과를 다시 계산한 값이 다릅니다: {result['id']}")
    commands, tool_inputs = [], []
    for event in cli["events"]:
        if cli["host"] == "claude" and event["type"] == "assistant":
            for block in event["content"]:
                if block["type"] == "tool_use":
                    tool_inputs.append(block.get("input", {}))
                    if block["name"] == "Bash":
                        commands.append(block["input"].get("command", ""))
        elif cli["host"] == "codex" and event["type"] == "item.completed":
            item = event.get("item", {})
            if item.get("type") in {"command_execution", "file_change", "mcp_tool_call", "web_search"}:
                tool_inputs.append({key: value for key, value in item.items()
                                    if key not in {"aggregated_output", "text"}})
            if item.get("type") == "command_execution":
                commands.append(item.get("command", ""))
    return ({key: result[key] for key in (
        "id", "case", "receiver", "condition", "verified", "success", "declared_complete",
        "outside_target_changes", "note_preserved", "seconds_including_verification")}
        | {"cli_error": cli["error"], "usage": S.usage(cli), "commands": commands,
           "tool_count": len(tool_inputs),
           "explicit_observation_read_calls": sum(
               "handoff-observation.json" in json.dumps(value) for value in tool_inputs),
           "test_stderr": result["verification"]["stderr"],
           "permission_denials": (cli["result"] or {}).get("permission_denials", []),
           "retries_failed_attempt": result["retries_failed_attempt"]})


def main() -> None:
    errors, calls = [], []
    manifest = S.read(OUT / "manifest.json")
    for relative, value in manifest["source_hashes"].items():
        if S.digest(P.REPO / relative) != value:
            errors.append(f"실행기가 달라졌습니다: {relative}")
    previous_calls = []
    for relative, value in manifest["original_record_hashes"].items():
        if S.digest(ROOT / relative) != value:
            errors.append(f"이전 원본이 달라졌습니다: {relative}")
        data = S.read(ROOT / relative)
        if isinstance(data, dict):
            if "cli" in data:
                previous_calls.append(data["cli"])
            elif "input_sha256" in data and "host" in data:
                previous_calls.append(data)
    continuation = S.read(OUT / "continuation-manifest.json")
    for name, value in (("retry_continue.py", continuation["source_sha256"]),
                        ("retry.py", continuation["retry_runner_sha256"])):
        if S.digest(ROOT / name) != value:
            errors.append(f"후속 실행기가 달라졌습니다: {name}")
    if S.digest(OUT / "manifest.json") != continuation["parent_manifest_sha256"]:
        errors.append("재시도 계획이 달라졌습니다.")
    if S.digest(OUT / "criteria-runs/extract--codex.json") != continuation["original_extraction_sha256"]:
        errors.append("후속 시험의 원인이 된 추출 결과가 달라졌습니다.")
    claude_manifest = OUT / "claude-continuation-manifest.json"
    if claude_manifest.exists():
        data = S.read(claude_manifest)
        if S.digest(ROOT / "retry_claude.py") != data["source_sha256"]:
            errors.append("Claude 후속 실행기가 달라졌습니다.")
        if S.digest(OUT / "manifest.json") != data["parent_manifest_sha256"]:
            errors.append("Claude 후속 계획의 상위 기록이 달라졌습니다.")
    extractions, decision_sets = {}, {}
    for folder in ("criteria-runs", "criteria-single-source"):
        path = OUT / folder / "extract--codex.json"
        if not path.exists():
            continue
        cli = S.read(path)
        calls.append(cli)
        expected = (S.read(ROOT / "criteria-runs/extract--codex.json")["prompt"]
                    if folder == "criteria-runs" else continuation["amended_extraction_prompt"])
        prompt_check(cli, expected, errors, folder)
        checked = extraction_check(cli)
        saved_check_path = OUT / folder / "extraction-check--codex.json"
        if saved_check_path.exists():
            saved_check = S.read(saved_check_path)
            if saved_check["rules"] != checked["rules"] or bool(saved_check["errors"]) != bool(checked["errors"]):
                errors.append(f"추출 검사를 다시 계산한 결과가 다릅니다: {folder}")
        extractions[folder] = {"cli_error": cli["error"], "contract_passed": not checked["errors"],
                               "usage": S.usage(cli), **checked}
        rows = []
        for path in sorted((OUT / folder).glob("*--codex--*.json")):
            row = S.read(path)
            cli = row["cli"]
            calls.append(cli)
            case = next(case for case in C.CASES if case["id"] == row["case"])
            payload = {"policy": C.POLICY, "task": case["task"],
                       "allowed_actions_and_targets": case["actions"],
                       "records": C.NOTES if row["condition"] == "raw_notes" else checked["rules"]}
            prompt_check(cli, C.CLI.SYSTEM + "\n" + json.dumps(payload, ensure_ascii=False), errors, path.name)
            actual = bool(cli["answer"] and C.CLI.matches(cli["answer"], case["expected"]))
            if row["matches"] != actual:
                errors.append(f"채점이 다릅니다: {path.name}")
            rows.append({key: row[key] for key in ("host", "case", "condition", "matches")}
                        | {"answer": cli["answer"], "error": cli["error"], "usage": S.usage(cli)})
        decision_sets[folder] = {"rows": rows, "groups": aggregate(rows)}
    freshness = []
    for path in sorted((OUT / "freshness-runs").glob("*--*--*.json")):
        row = S.read(path)
        cli = row["cli"]
        calls.append(cli)
        prompt_check(cli, manifest["freshness_manifest"]["prompts"][row["condition"]], errors, path.name)
        freshness.append({key: row[key] for key in ("host", "condition", "repeat")}
                         | {"answer": cli["answer"], "error": cli["error"], "usage": S.usage(cli)})
    native_rows = []
    for path in sorted((OUT / "runs").glob("*/*/result.json")):
        native_rows.append(native_row(path, errors))
        calls.append(S.read(path.parent / "cli.json"))
    old = S.read(ROOT / "summary.json")
    amounts = [S.usage(cli) for cli in calls if cli["host"] == "claude"]
    summary = {
        "validation_errors": errors,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "original_json_files_unchanged": len(manifest["original_record_hashes"]),
        "cli_versions": manifest["cli_versions"],
        "cli_versions_unchanged": manifest["cli_versions"] == manifest["previous_cli_versions"],
        "retry_calls": len(calls), "cli_errors": sum(bool(cli["error"]) for cli in calls),
        "missing_usage_calls": sum(not S.usage(cli)["reported_usage_available"] for cli in calls),
        "retry_claude_reported_cost_usd": sum(row["claude_reported_cost_usd"] for row in amounts),
        "all_calls_including_originals": len(previous_calls) + len(calls),
        "all_cli_errors_including_originals": sum(bool(cli["error"]) for cli in previous_calls + calls),
        "all_claude_reported_cost_usd": sum(S.usage(cli)["claude_reported_cost_usd"]
                                            for cli in previous_calls + calls if cli["host"] == "claude"),
        "codex_cost_usd": None,
        "extractions": extractions, "criteria": decision_sets,
        "freshness": {"rows": freshness, "groups": aggregate(freshness)},
        "native_handoff": native_rows,
        "native_all_attempts": old["native_handoff"]["rows"] + native_rows,
        "freshness_all_runs": old["freshness"]["rows"] + freshness,
        "interpretation_limits": [
            "원래 기준 추출은 계약을 통과하지 못했습니다. 원래 조건의 후속 판단은 실행하지 않았습니다.",
            "출처 형식을 더 명확히 하는 계획은 별도 조건이며 앞선 Claude 조건과 동일하지 않습니다.",
            "이전 서버 오류와 이번 계약 실패를 성공한 실행으로 대체하지 않습니다.",
            "Codex 기본 모델 설정은 같지만 모델 식별자를 명시적으로 고정하지 않았습니다."]}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in (
        "validation_errors", "original_json_files_unchanged", "cli_versions_unchanged",
        "retry_calls", "cli_errors", "retry_claude_reported_cost_usd")}, ensure_ascii=False, indent=2))
    print(json.dumps({"native": [{key: row[key] for key in (
        "condition", "success", "seconds_including_verification", "tool_count",
        "explicit_observation_read_calls", "usage")} for row in native_rows],
        "all_calls": summary["all_calls_including_originals"],
        "all_cli_errors": summary["all_cli_errors_including_originals"],
        "all_claude_reported_cost_usd": summary["all_claude_reported_cost_usd"]},
        ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
