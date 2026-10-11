"""고정한 입력과 모든 CLI 응답을 대조하고 같은 조건끼리 집계합니다."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from run import CLI, ROOT, build_prompt, digest, save


def usage(cli: dict) -> dict:
    result = cli.get("result") or {}
    values = result.get("usage")
    if not isinstance(values, dict):
        return {"input_tokens": None, "cached_input_tokens": None,
                "cache_creation_input_tokens": None, "output_tokens": None,
                "reported_cost_usd": result.get("total_cost_usd")}
    inputs = values.get("input_tokens")
    if cli["host"] == "claude":
        inputs += values.get("cache_creation_input_tokens", 0) + values.get("cache_read_input_tokens", 0)
        cached = values.get("cache_read_input_tokens", 0)
        created = values.get("cache_creation_input_tokens", 0)
    else:
        cached = values.get("cached_input_tokens")
        created = values.get("cache_write_input_tokens")
    return {"input_tokens": inputs, "cached_input_tokens": cached,
            "cache_creation_input_tokens": created, "output_tokens": values.get("output_tokens"),
            "reported_cost_usd": result.get("total_cost_usd")}


def aggregate(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    result = []
    for values, selected in sorted(groups.items()):
        group = {**dict(zip(keys, values)), "calls": len(selected),
                 "matches": sum(row["matches"] for row in selected),
                 "cli_errors": sum(bool(row["error"]) for row in selected)}
        for key in ("input_tokens", "cached_input_tokens", "cache_creation_input_tokens",
                    "output_tokens", "reported_cost_usd", "request_seconds", "cli_seconds",
                    "preparation_seconds", "other_seconds", "prompt_characters"):
            known = [row[key] for row in selected if row[key] is not None]
            group[key] = sum(known) if known else None
            group[f"{key}_missing"] = len(selected) - len(known)
        result.append(group)
    return result


def main() -> None:
    errors = []
    manifest = json.loads((ROOT / "runs/manifest.json").read_text())
    cases = {row["id"]: row for row in json.loads((ROOT / "fixtures.json").read_text())}
    for name, expected in manifest["sources"].items():
        if digest((ROOT.parent / name).read_bytes()) != expected:
            errors.append(f"고정한 소스 변경: {name}")
    preparation = json.loads((ROOT / "preparation.json").read_text())
    if digest((ROOT / "prepare-recorded.py").read_bytes()) != preparation["source_sha256"]:
        errors.append("준비할 때 실행한 원본 코드 해시가 다릅니다.")
    expected_ids = {
        f"{r['case']}--{r['host']}--{r['condition']}--r{r['repeat']}"
        for entries in manifest["schedules"].values() for r in entries}
    rows, originals, actual_ids = [], {}, set()
    models = {"claude": set(), "codex": set()}
    for path in sorted((ROOT / "runs").glob("*--*.json")):
        record = json.loads(path.read_text())
        case = cases[record["case"]]
        cli = record["cli"]
        prompt, selections = build_prompt(case, record["condition"])
        if prompt != cli["prompt"] or digest(prompt.encode()) != record["prompt_sha256"]:
            errors.append(f"입력 불일치: {path.name}")
        if cli["input_sha256"] != record["prompt_sha256"] or selections != record["selections"]:
            errors.append(f"선택·해시 불일치: {path.name}")
        correct = bool(not cli["error"] and cli["answer"] and CLI.matches(cli["answer"], case["expected"]))
        if record["expected"] != case["expected"] or record["matches"] != correct:
            errors.append(f"기대값·채점 불일치: {path.name}")
        other = record["request_seconds"] - record["preparation_seconds"] - cli["wall_time_s"]
        if other < -0.00001:
            errors.append(f"시간 구간이 겹칩니다: {path.name}")
        row = {key: record[key] for key in (
            "case", "kind", "host", "condition", "repeat", "matches", "prompt_characters",
            "preparation_seconds", "request_seconds", "prompt_sha256", "selections")}
        row.update({"source": f"runs/{path.name}", "source_sha256": digest(path.read_bytes()),
                    "criterion_id": case["criterion_id"],
                    "error": cli["error"], "answer": cli["answer"], "cli_seconds": cli["wall_time_s"],
                    "other_seconds": other, **usage(cli)})
        rows.append(row)
        originals[(record["case"], record["host"], record["repeat"], record["condition"])] = row
        actual_ids.add(path.stem)
        models[record["host"]].update((cli.get("result") or {}).get("modelUsage", {}))
        models[record["host"]].update(line for line in cli.get("diagnostic_lines", [])
                                      if line.startswith("model:"))
    pairs = []
    for case, host, repeat in sorted({key[:3] for key in originals}):
        a = originals.get((case, host, repeat, "full"))
        b = originals.get((case, host, repeat, "selected"))
        if a is None or b is None:
            continue
        pairs.append({"case": case, "host": host, "repeat": repeat,
                      "same_prompt": a["prompt_sha256"] == b["prompt_sha256"],
                      "both_match": a["matches"] and b["matches"],
                      "action_same": (a["answer"] or {}).get("action") == (b["answer"] or {}).get("action"),
                      "selected_minus_full_seconds": b["request_seconds"] - a["request_seconds"]})
    normal = [r for r in rows if r["kind"] == "historical"]
    check_sources = [ROOT / "runs/manifest.json", ROOT / "fixtures.json", Path(__file__)]
    summary = {
        "validation_errors": errors, "planned_calls": len(expected_ids), "observed_calls": len(rows),
        "missing": sorted(expected_ids - actual_ids), "unexpected": sorted(actual_ids - expected_ids),
        "matches": sum(r["matches"] for r in rows), "cli_errors": sum(bool(r["error"]) for r in rows),
        "source_hashes": {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in check_sources},
        "reported_model_ids": {host: sorted(values) for host, values in models.items()},
        "groups": aggregate(normal, ("host", "condition")),
        "case_groups": aggregate(normal, ("case", "host", "condition")),
        "task_groups": aggregate(normal, ("criterion_id", "host", "condition")),
        "missing_source_groups": aggregate([r for r in rows if r["kind"] == "missing_source"],
                                           ("host", "condition")),
        "pairs": pairs, "rows": rows,
        "limits": ["앞선 연구에서 쓴 결함 두 개를 다시 사용했습니다.",
                   "두 조건의 입력이 동일한 비교도 포함합니다.",
                   "시작 함수는 연구자가 지정했습니다.",
                   "외부 모듈과 상태 전체를 자동으로 추적하지 않습니다."]}
    save(ROOT / "summary.json", summary)
    print(json.dumps({key: summary[key] for key in (
        "validation_errors", "planned_calls", "observed_calls", "missing", "unexpected", "matches",
        "cli_errors", "reported_model_ids", "groups", "task_groups")}, ensure_ascii=False, indent=2))
    if errors or summary["missing"] or summary["unexpected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
