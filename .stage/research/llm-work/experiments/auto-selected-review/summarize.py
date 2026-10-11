"""함수 선택과 검토 비용을 합치고 고정한 원본과 응답을 대조합니다."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from common import CLI, ROOT, choose_source, digest, save, usage
from run import cases, locate_prompt, review_prompt


def aggregate(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    results = []
    for key, values in sorted(grouped.items()):
        result = {**dict(zip(keys, key)), "count": len(values)}
        for metric in ("input_tokens", "cached_input_tokens", "output_tokens", "reported_cost_usd",
                       "seconds", "cli_seconds", "local_seconds"):
            available = [row.get(metric) for row in values if row.get(metric) is not None]
            result[metric] = sum(available) if available else None
            result[f"{metric}_missing"] = len(values) - len(available)
        if "matches" in values[0]:
            result["matches"] = sum(row["matches"] for row in values)
        result["errors"] = sum(bool(row.get("error")) for row in values)
        results.append(result)
    return results


def all_known_sum(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows]
    return sum(values) if values and all(value is not None for value in values) else None


def main() -> None:
    manifest = json.loads((ROOT / "runs/manifest.json").read_text())
    catalog = {case["id"]: case for case in cases()}
    errors = []
    for name, expected in manifest["source_hashes"].items():
        if digest((ROOT.parent / name).read_bytes()) != expected:
            errors.append(f"고정한 소스 변경: {name}")
    planned = {f"{r['case']}--{r['host']}--{r['condition']}--r{r['repeat']}"
               for entries in manifest["schedules"].values() for r in entries}
    request_rows, call_rows, source_hashes = [], [], {}
    seen = set()
    for path in sorted((ROOT / "runs").glob("*/request.json")):
        record = json.loads(path.read_text())
        source_hashes[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())
        case = catalog[record["case"]]
        actual_calls = []
        chosen_files = case["files"]
        selection = {}
        for filename in record["calls"]:
            call_path = path.parent / filename
            cli = json.loads(call_path.read_text())
            source_hashes[call_path.relative_to(ROOT).as_posix()] = digest(call_path.read_bytes())
            phase = call_path.stem
            prompt = locate_prompt(case) if phase == "locate" else review_prompt(case, chosen_files)
            if prompt != cli["prompt"] or digest(prompt.encode()) != cli["input_sha256"]:
                errors.append(f"입력·해시 불일치: {call_path.relative_to(ROOT)}")
            row = {"request_id": record["id"], "case": case["id"],
                   "criterion_id": case["criterion_id"], "host": record["host"],
                   "condition": record["condition"], "repeat": record["repeat"], "phase": phase,
                   "error": cli["error"], "seconds": cli["wall_time_s"], **usage(cli)}
            actual_calls.append(row)
            call_rows.append(row)
            if phase == "locate" and not cli["error"]:
                chosen = {name: choose_source(source, cli["answer"])
                          for name, source in case["files"].items()}
                chosen_files = {name: item["source"] for name, item in chosen.items()}
                selection = {name: {k: v for k, v in item.items() if k != "source"}
                             for name, item in chosen.items()}
            elif phase == "review":
                correct = bool(not cli["error"] and cli["answer"]
                               and CLI.matches(cli["answer"], case["expected"]))
                if correct != record["matches"] or cli["answer"] != record["answer"]:
                    errors.append(f"응답·채점 불일치: {record['id']}")
        if selection != record["selection"] or record["expected"] != case["expected"]:
            errors.append(f"선택·기대값 불일치: {record['id']}")
        if not record["error"]:
            expected_calls = ["locate.json", "review.json"] if record["condition"] == "auto" else ["review.json"]
            if record["calls"] != expected_calls:
                errors.append(f"호출 순서 불일치: {record['id']}")
        cli_seconds = sum(row["seconds"] for row in actual_calls)
        local_seconds = record["request_seconds"] - cli_seconds
        if local_seconds < -0.00001:
            errors.append(f"시간 구간 불일치: {record['id']}")
        request_rows.append({**{key: record[key] for key in (
            "id", "case", "criterion_id", "host", "condition", "repeat", "matches", "error", "selection")},
            "cli_calls": len(actual_calls), "seconds": record["request_seconds"],
            "cli_seconds": cli_seconds, "local_seconds": local_seconds,
            **{key: all_known_sum(actual_calls, key) for key in (
                "input_tokens", "cached_input_tokens", "output_tokens", "reported_cost_usd")},
            "review_prompt_matches_full": review_prompt(case, chosen_files) == review_prompt(case, case["files"])})
        seen.add(record["id"])
    summary = {
        "planned_requests": manifest["planned_requests"], "observed_requests": len(request_rows),
        "planned_cli_calls": manifest["planned_cli_calls"], "observed_cli_calls": len(call_rows),
        "missing": sorted(planned - seen), "unexpected": sorted(seen - planned),
        "validation_errors": errors, "matches": sum(row["matches"] for row in request_rows),
        "cli_errors": sum(bool(row["error"]) for row in call_rows),
        "groups": aggregate(request_rows, ("host", "condition")),
        "task_groups": aggregate(request_rows, ("criterion_id", "host", "condition")),
        "phase_groups": aggregate(call_rows, ("criterion_id", "host", "condition", "phase")),
        "request_rows": request_rows, "call_rows": call_rows, "source_hashes": source_hashes,
        "summarizer_sha256": digest(Path(__file__).read_bytes()),
        "limits": ["대상 파일을 찾는 비용은 측정하지 않았습니다.",
                   "기존 과거 결함 두 개를 다시 사용했습니다.",
                   "외부 의존 파일과 실제 업무 전체의 결과는 확인하지 않았습니다.",
                   "금액은 Claude CLI 보고값이며 Codex 금액은 확인하지 못했습니다."]}
    save(ROOT / "summary.json", summary)
    print(json.dumps({key: summary[key] for key in (
        "planned_requests", "observed_requests", "observed_cli_calls", "matches", "cli_errors",
        "missing", "unexpected", "validation_errors", "task_groups", "phase_groups")},
        ensure_ascii=False, indent=2))
    if errors or summary["missing"] or summary["unexpected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
