"""실제 변경·독립 검사·호출 기록을 대조하고 인계 조건별 결과를 집계합니다."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import mean

import harness as H

ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calls(directory: Path) -> list[dict]:
    return [json.loads(path.read_text()) for path in sorted(directory.glob("call-*.json"))]


def totals(records: list[dict]) -> dict:
    inputs, outputs, cost = 0, 0, 0.0
    for record in records:
        result = record["result"] or {}
        usage = result.get("usage") or {}
        if record["host"] == "claude":
            inputs += sum(usage.get(key, 0) or 0 for key in (
                "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        else:
            inputs += usage.get("input_tokens", 0) or 0
        outputs += usage.get("output_tokens", 0) or 0
        cost += result.get("total_cost_usd", 0) or 0
    return {"calls": len(records), "reported_input_tokens": inputs, "reported_output_tokens": outputs,
            "claude_reported_cost_usd": round(cost, 8),
            "codex_cost_usd": None,
            "cli_seconds": sum(record["wall_time_s"] for record in records)}


def replay(source: str, events: list[dict], target: str, directory: Path,
           errors: list[str]) -> str:
    """저장한 호출과 도구 결과를 대조하며 파일 내용이 어떻게 바뀌었는지 복원합니다."""
    for event in events:
        record = json.loads((directory / event["cli_record"]).read_text())
        answer, observed = event["answer"], event["tool_result"]
        if record["answer"] != answer:
            errors.append(f"answer/event mismatch: {directory.name}/{event['step']}")
        if answer["action"] == "read" and answer["targets"] == [target]:
            if observed.get("content") != source or observed.get("sha256") != H.digest(source):
                errors.append(f"read/source mismatch: {directory.name}/{event['step']}")
        if answer["action"] == "replace" and observed.get("ok"):
            path, old, new = answer["targets"]
            if path != target or not old or source.count(old) != 1:
                errors.append(f"invalid recorded replacement: {directory.name}/{event['step']}")
                continue
            after = source.replace(old, new, 1)
            if (observed["before_sha256"] != H.digest(source)
                    or observed["after_sha256"] != H.digest(after)
                    or observed["changed"] != (source != after)):
                errors.append(f"replacement/hash mismatch: {directory.name}/{event['step']}")
            source = after
    return source


def main() -> None:
    out = ROOT / "runs"
    manifest = json.loads((out / "manifest.json").read_text())
    sources = {"run.py": ROOT / "run.py", "harness.py": ROOT / "harness.py",
               "prior_cli": ROOT.parent / "ideas-lab" / "run_models.py",
               "fixtures": ROOT.parent / "review-reuse" / "fixtures.json",
               "prepare": ROOT.parent / "review-reuse" / "prepare-recorded.py"}
    errors = [f"source hash mismatch: {name}" for name, path in sources.items()
              if sha(path) != manifest["source_hashes"][name]]
    fixtures = {row["id"]: row for row in json.loads(sources["fixtures"].read_text())}
    cases = {row["id"]: row for row in manifest["cases"]}
    all_calls = []
    for path in out.glob("*/*/call-*.json"):
        record = json.loads(path.read_text())
        all_calls.append(record)
        if hashlib.sha256(record["prompt"].encode()).hexdigest() != record["input_sha256"]:
            errors.append(f"prompt hash mismatch: {path.relative_to(ROOT)}")
        if record["error"]:
            errors.append(f"CLI error: {path.relative_to(ROOT)}: {record['error']}")
    rows = []
    seed_rows = []
    continuation_calls = []
    for directory in sorted(path for path in out.iterdir() if path.is_dir()):
        seed_file = directory / "seed" / "seed.json"
        if not seed_file.exists():
            errors.append(f"missing successful seed: {directory.name}")
            continue
        seed = json.loads(seed_file.read_text())
        case_id = directory.name.split("--")[0]
        target = cases[case_id]["target"]
        source_before = fixtures[case_id]["versions"]["before"]["files"][target]
        if replay(source_before, seed["events"], target, seed_file.parent, errors) != seed["source_after"]:
            errors.append(f"seed source mismatch: {directory.name}")
        start_source = seed["source_after"] + (H.NOTE if case_id == "retrospective_owner_conflict" else "")
        seed_rows.append({"lane": directory.name, "host": seed["host"], "seconds": seed["seconds"],
                          **totals(calls(directory / "seed"))})
        for condition in manifest["conditions"]:
            path = directory / condition / "result.json"
            if not path.exists():
                errors.append(f"missing continuation: {directory.name}/{condition}")
                continue
            row = json.loads(path.read_text())
            handoff = json.loads((path.parent / "handoff.json").read_text())["data"]
            if condition == "transcript":
                if handoff["prior_history"] != seed["history"]:
                    errors.append(f"transcript mismatch: {row['id']}")
            else:
                observed = handoff["current_files"][target]
                if observed != {"content": start_source, "sha256": H.digest(start_source)}:
                    errors.append(f"handoff source mismatch: {row['id']}")
            if replay(start_source, row["events"], target, path.parent, errors) != row["final_source"]:
                errors.append(f"final source mismatch: {row['id']}")
            records = calls(path.parent)
            continuation_calls.extend((condition, record) for record in records)
            if len(records) != len(row["events"]):
                errors.append(f"call/event count mismatch: {row['id']}")
            independently_passed = (
                row["verification"]["focused"]["returncode"] == 0
                and row["verification"]["full_module"]["returncode"] == 0
                and not row["verification"]["outside_target_changes"]
                and row["verification"]["note_preserved"])
            if row["success"] != (row["declared_complete"] and independently_passed):
                errors.append(f"completion mismatch: {row['id']}")
            fields = ("id", "case", "starter", "receiver", "condition", "success", "false_completion",
                      "preparation_file_reads", "model_file_reads", "model_test_requests",
                      "repeated_last_patch_requests", "rejected_patch_requests", "no_change_writes",
                      "clone_seconds", "preparation_seconds", "resume_seconds_including_verification")
            compact = {field: row[field] for field in fields}
            compact["focused_passed"] = row["verification"]["focused"]["returncode"] == 0
            compact["full_module_passed"] = row["verification"]["full_module"]["returncode"] == 0
            compact["note_preserved"] = row["verification"]["note_preserved"]
            compact["outside_target_changes"] = row["verification"]["outside_target_changes"]
            compact.update(totals(records))
            compact["verification_seconds"] = (row["verification"]["focused"]["seconds"]
                                                + row["verification"]["full_module"]["seconds"])
            compact["full_module_stderr"] = row["verification"]["full_module"]["stderr"]
            rows.append(compact)
    if len(seed_rows) != manifest["planned_seeds"] or len(rows) != manifest["planned_continuations"]:
        errors.append("planned run count not reached")
    groups = []
    for condition in manifest["conditions"]:
        values = [row for row in rows if row["condition"] == condition]
        if not values:
            continue
        summed = ("calls", "model_file_reads", "preparation_file_reads", "model_test_requests",
                  "repeated_last_patch_requests", "rejected_patch_requests", "no_change_writes",
                  "reported_input_tokens", "reported_output_tokens", "claude_reported_cost_usd",
                  "resume_seconds_including_verification", "verification_seconds", "cli_seconds")
        groups.append({"condition": condition, "runs": len(values),
                       "successes": sum(row["success"] for row in values),
                       "focused_passes": sum(row["focused_passed"] for row in values),
                       "full_module_passes": sum(row["full_module_passed"] for row in values),
                       "false_completions": sum(row["false_completion"] for row in values),
                       **{name: sum(row[name] for row in values) for name in summed},
                       "mean_resume_seconds": mean(row["resume_seconds_including_verification"] for row in values)})
    pairs = []
    for seed in seed_rows:
        values = {row["condition"]: row for row in rows if row["id"].startswith(seed["lane"] + "--")}
        if len(values) == 2:
            pairs.append({"lane": seed["lane"],
                          "state_packet_minus_transcript_calls": values["state_packet"]["calls"] - values["transcript"]["calls"],
                          "state_packet_minus_transcript_seconds": values["state_packet"]["resume_seconds_including_verification"] - values["transcript"]["resume_seconds_including_verification"],
                          "both_successful": all(row["success"] for row in values.values())})
    summary = {"validation_errors": errors, "case_count": len(manifest["cases"]),
               "seed_count": len(seed_rows), "continuation_count": len(rows),
               "whole_experiment_model_usage": totals(all_calls), "seeds": seed_rows,
               "usage_by_receiver_and_condition": [
                   {"receiver": host, "condition": condition,
                    **totals([record for name, record in continuation_calls
                              if name == condition and record["host"] == host])}
                   for host in ("claude", "codex") for condition in manifest["conditions"]],
               "continuations": rows, "groups": groups, "paired_results": pairs,
               "limits": ["Two historical defects, two handoff directions, one run per condition.",
                          "This is a constrained model-action loop, not a full Stage/host integration.",
                          "Fresh observation and context packaging change together.",
                          "Per-request CLI processes add startup cost; native persistent sessions may differ.",
                          "Independent checks use historical tests; this is not general code-quality proof.",
                          "The retrospective full-module gate includes a new API outside the model goal; false_completion is a gate mismatch, not proof of dishonest reporting. See diagnostics.json.",
                          "A lost response is simulated; process death and external side effects were not tested."]}
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("validation_errors", "seed_count", "continuation_count",
                                                  "whole_experiment_model_usage", "groups", "paired_results")}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
