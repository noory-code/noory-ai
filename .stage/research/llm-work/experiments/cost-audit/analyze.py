"""기존 실험 원본에서 비용과 누락을 다시 계산합니다. 모델은 호출하지 않습니다."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPERIMENTS = ROOT.parent
SOURCES: dict[str, str] = {}
ERRORS: list[str] = []


def read(path: Path) -> dict:
    raw = path.read_bytes()
    SOURCES[path.relative_to(EXPERIMENTS).as_posix()] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def check(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


def equal(actual: float, expected: float, label: str) -> None:
    check(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9), label)


def normalize(cli: dict, path: Path, experiment: str, phase: str, condition: str) -> dict:
    result = cli.get("result") or {}
    usage = result.get("usage")
    host = cli["host"]
    check(host in {"claude", "codex"}, f"알 수 없는 host: {path}")
    prompt = cli.get("prompt")
    if prompt is not None:
        check(hashlib.sha256(prompt.encode()).hexdigest() == cli["input_sha256"],
              f"입력 해시 불일치: {path}")
    seconds = cli.get("seconds", cli.get("wall_time_s"))
    check(isinstance(seconds, (int, float)) and seconds >= 0, f"시간 누락: {path}")
    total = cached = uncached = created = output = None
    if isinstance(usage, dict):
        if host == "claude":
            uncached = usage.get("input_tokens", 0)
            created = usage.get("cache_creation_input_tokens", 0)
            cached = usage.get("cache_read_input_tokens", 0)
            total = uncached + created + cached
        else:
            total = usage.get("input_tokens")
            cached = usage.get("cached_input_tokens")
            if total is not None and cached is not None:
                uncached = total - cached
                check(uncached >= 0, f"캐시 입력이 전체 입력보다 큽니다: {path}")
        output = usage.get("output_tokens")
    return {
        "source": path.relative_to(EXPERIMENTS).as_posix(),
        "experiment": experiment, "phase": phase, "condition": condition, "host": host,
        "cli_error": cli.get("error"), "seconds": seconds,
        "input_tokens": total, "cached_input_tokens": cached,
        "new_or_non_cached_input_tokens": uncached, "cache_creation_input_tokens": created,
        "output_tokens": output, "reported_cost_usd": result.get("total_cost_usd"),
    }


def totals(rows: list[dict]) -> dict:
    result = {"calls": len(rows), "cli_errors": sum(bool(r["cli_error"]) for r in rows)}
    for key in ("seconds", "input_tokens", "cached_input_tokens", "output_tokens",
                "new_or_non_cached_input_tokens", "cache_creation_input_tokens", "reported_cost_usd"):
        known = [r[key] for r in rows if r[key] is not None]
        result[key] = sum(known) if known else None
        result[f"{key}_missing_calls"] = len(rows) - len(known)
    return result


def grouped(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    return [{**dict(zip(keys, values)), **totals(group)}
            for values, group in sorted(groups.items())]


def stage_followup() -> tuple[list[dict], list[dict]]:
    base = EXPERIMENTS / "stage-followup"
    rows, native = [], []
    for folder in ("runs", "criteria-runs", "freshness-runs", "retry-1", "retry-2",
                   "retry-3", "after-update"):
        for path in sorted((base / folder).rglob("*.json")):
            data = read(path)
            if not isinstance(data, dict):
                continue
            cli = data.get("cli")
            if cli is None and "host" in data and "input_sha256" in data:
                cli = data
            if not isinstance(cli, dict):
                continue
            if path.name == "cli.json":
                phase = "native_handoff"
                condition = path.parent.name
            elif path.name.startswith("extract--"):
                phase, condition = "criteria_extraction", path.parent.name
            elif data.get("kind") == "criteria" or ("case" in data and "matches" in data):
                phase, condition = "criteria_decision", data["condition"]
            elif data.get("kind") == "freshness" or data.get("condition") in {"original", "time_explicit"}:
                phase, condition = "freshness_decision", data["condition"]
            else:
                ERRORS.append(f"호출 분류를 확인해야 합니다: {path}")
                continue
            row = normalize(cli, path, "stage-followup", phase, condition)
            rows.append(row)
            if phase == "criteria_extraction":
                saved_check = path.with_name(path.name.replace("extract--", "extraction-check--"))
                row["extraction_contract_passed"] = (
                    not bool(read(saved_check)["errors"]) if saved_check.exists() else None)
            if phase == "native_handoff":
                outcome = read(path.parent / "result.json")
                total = outcome["seconds_including_verification"]
                verify = outcome["verification"]["seconds"]
                remaining = total - row["seconds"] - verify
                check(remaining >= -0.01, f"서로 겹치는 시간 구간: {path}")
                native.append({**row, "case": outcome["case"], "success": outcome["success"],
                               "total_seconds": total, "independent_test_seconds": verify,
                               "preparation_and_other_seconds": remaining,
                               "cloning_seconds_excluded": outcome["clone_seconds"]})
    previous = read(base / "after-update/summary.json")
    check(len(rows) == previous["all_calls"], "후속 실험 호출 수가 기존 집계와 다릅니다.")
    check(sum(bool(r["cli_error"]) for r in rows) == previous["all_cli_errors"],
          "후속 실험 오류 수가 기존 집계와 다릅니다.")
    equal(totals([r for r in rows if r["host"] == "claude"])["reported_cost_usd"],
          previous["claude_reported_cost_usd"], "Claude 보고 금액이 기존 집계와 다릅니다.")
    check(len(native) == len(previous["native_handoff"]["all_attempts"]), "인계 시도 수 불일치")
    return rows, native


def review_reuse() -> tuple[list[dict], list[dict]]:
    base = EXPERIMENTS / "review-reuse"
    rows, requests = [], []
    for path in sorted((base / "runs").glob("*--*.json")):
        data = read(path)
        requests.append({key: data[key] for key in (
            "host", "condition", "cache_hit", "end_to_end_s", "matches", "origin")})
        if data["cache_hit"]:
            check(data["cli"] is None, f"캐시 응답에 모델 호출이 있습니다: {path}")
        else:
            rows.append(normalize(data["cli"], path, "review-reuse", "review", data["condition"]))
    previous = read(base / "summary.json")
    check(len(rows) == previous["total_cli_calls"], "리뷰 호출 수 불일치")
    check(len(requests) == previous["observed_requests"], "리뷰 요청 수 불일치")
    for saved in previous["groups"]:
        selected = [r for r in rows if (r["host"], r["condition"]) == (saved["host"], saved["condition"])]
        computed = totals(selected)
        for field in ("input_tokens", "output_tokens"):
            equal(computed[field], saved[f"reported_{field}"], f"리뷰 {field} 불일치")
        if saved["reported_cost_usd"] is not None:
            equal(computed["reported_cost_usd"], saved["reported_cost_usd"], "리뷰 보고 금액 불일치")
    return rows, requests


def context_handoff() -> list[dict]:
    base = EXPERIMENTS / "context-handoff"
    rows = []
    for path in sorted((base / "runs").glob("*--*.json")):
        data = read(path)
        rows.append(normalize(data["cli"], path, "context-handoff", "handoff_decision", data["condition"]))
    check(len(rows) == 24, "문맥 실험 원본 호출 수 불일치")
    for saved in read(base / "summary.json")["groups"]:
        selected = [r for r in rows if (r["host"], r["condition"]) == (saved["host"], saved["condition"])]
        computed = totals(selected)
        for field in ("input_tokens", "output_tokens"):
            equal(computed[field], saved[f"reported_{field}"], f"문맥 {field} 불일치")
        equal(computed["seconds"] / len(selected), saved["mean_cli_seconds"], "문맥 시간 불일치")
        if saved["reported_cost_usd"] is not None:
            equal(computed["reported_cost_usd"], saved["reported_cost_usd"], "문맥 보고 금액 불일치")
    return rows


def derived_metrics(stage: list[dict], native: list[dict], review: list[dict],
                    requests: list[dict]) -> dict:
    claude = [r for r in stage if r["host"] == "claude"]
    claude_cost = totals(claude)["reported_cost_usd"]
    phase_costs = [{**r, "share_of_claude_reported_cost": r["reported_cost_usd"] / claude_cost}
                   for r in grouped(claude, ("phase",))]
    native_total = sum(r["total_seconds"] for r in native)
    cli_total = sum(r["seconds"] for r in native)
    test_total = sum(r["independent_test_seconds"] for r in native)
    failures = totals([r for r in stage if r["cli_error"]])
    decisions = [r for r in claude if r["phase"] == "criteria_decision"]
    raw = totals([r for r in decisions if r["condition"] == "raw_notes"])
    extracted = totals([r for r in claude if r["phase"] == "criteria_extraction"
                        or (r["phase"] == "criteria_decision" and r["condition"] == "extracted_rules")])
    reuse_groups = []
    for host in ("claude", "codex"):
        for condition in ("baseline", "reuse"):
            selected = [r for r in requests if (r["host"], r["condition"]) == (host, condition)]
            calls = [r for r in review if (r["host"], r["condition"]) == (host, condition)]
            request_seconds = sum(r["end_to_end_s"] for r in selected)
            cli_seconds = sum(r["seconds"] for r in calls)
            check(request_seconds >= cli_seconds, "리뷰 요청 시간이 내부 CLI 시간보다 짧습니다.")
            reuse_groups.append({"host": host, "condition": condition, "requests": len(selected),
                                 "calls": len(calls), "request_seconds": request_seconds,
                                 "cli_seconds": cli_seconds,
                                 "local_wrapper_seconds": request_seconds - cli_seconds})
    return {
        "claude_stage_costs": phase_costs,
        "native_time": {"attempts": len(native), "completed": sum(r["success"] for r in native),
                        "total_seconds": native_total, "cli_seconds": cli_total,
                        "independent_test_seconds": test_total,
                        "other_seconds": native_total - cli_total - test_total,
                        "cli_share": cli_total / native_total,
                        "independent_test_share": test_total / native_total},
        "failed_cli_calls": failures,
        "claude_criteria_including_extraction": {"raw": raw, "extracted": extracted},
        "review_request_times": reuse_groups,
    }


def main() -> None:
    stage, native = stage_followup()
    review, requests = review_reuse()
    context = context_handoff()
    rows = stage + review + context
    check(len({r["source"] for r in rows}) == len(rows), "원본 호출을 중복 집계했습니다.")
    before_write = dict(SOURCES)
    for relative, expected in before_write.items():
        check(hashlib.sha256((EXPERIMENTS / relative).read_bytes()).hexdigest() == expected,
              f"집계 중 원본이 달라졌습니다: {relative}")
    report = {
        "schema": "research-cost-audit/1", "validation_errors": ERRORS,
        "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "raw_cli_records": len(rows), "source_hashes": SOURCES,
        "groups": grouped(rows, ("experiment", "host", "phase", "condition")),
        "stage_phase_totals": grouped(stage, ("host", "phase")),
        "stage_error_totals": grouped([r for r in stage if r["cli_error"]], ("host", "phase")),
        "native_handoff": native, "review_requests": requests, "rows": rows,
        "derived": derived_metrics(stage, native, review, requests),
        "limits": ["실험 단계의 합계이며 일반 업무의 비용 순위가 아닙니다.",
                   "요청의 경과 시간을 합쳤습니다. 병렬 실행의 전체 경과 시간이 아닙니다.",
                   "CLI 시간에는 모델 응답 대기와 도구 실행이 함께 들어 있습니다.",
                   "사용량 누락은 0으로 바꾸지 않습니다. 알려진 합계와 누락 수를 함께 기록합니다.",
                   "실제 청구액과 사람의 작업 시간, 재시도 사이의 대기 시간은 확인하지 않았습니다."]}
    (ROOT / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"validation_errors": ERRORS, "raw_cli_records": len(rows),
                      "source_files_checked": len(SOURCES), "derived": report["derived"]},
                     ensure_ascii=False, indent=2))
    if ERRORS:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
