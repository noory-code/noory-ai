"""모델을 다시 부르지 않고 실제 리뷰 결과와 캐시의 출처를 대조합니다."""

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from statistics import mean

from run import CLI, ROOT, prompt_for, save


def main() -> None:
    manifest = json.loads((ROOT / "runs" / "manifest.json").read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in json.loads(
        (ROOT / "fixtures.json").read_text(encoding="utf-8"))}
    records = {path.stem: json.loads(path.read_text(encoding="utf-8"))
               for path in (ROOT / "runs").glob("*--*.json")}
    errors = []
    for name, expected in manifest["source_hashes"].items():
        actual = hashlib.sha256((ROOT.parent / name).read_bytes()).hexdigest()
        if expected != actual:
            errors.append(f"source changed: {name}")
    expected_ids = {
        f"{case_id}--{host}--r{repeat}--{condition}--s{step}"
        for case_id in cases for host in ("claude", "codex") for repeat in (1, 2)
        for condition in ("baseline", "reuse") for step in range(1, 5)
    }
    rows = []
    groups = defaultdict(list)
    for run_id, record in sorted(records.items()):
        case = cases[record["case"]]
        prompt_hash = hashlib.sha256(prompt_for(case, record["version"]).encode()).hexdigest()
        if prompt_hash != record["prompt_sha256"]:
            errors.append(f"prompt changed: {run_id}")
        if record["cache_hit"]:
            origin = records.get(record["origin"])
            if (not origin or origin["cache_hit"] or origin["key"] != record["key"]
                    or origin["answer"] != record["answer"] or record["cli"] is not None):
                errors.append(f"invalid reuse: {run_id}")
        expected = {"action": "revise", "targets": [record["case"]]} if (
            record["version"] == "before") else {"action": "approve", "targets": []}
        correct = bool(record["answer"] and not record["error"] and
                       CLI.matches(record["answer"], expected))
        if record["matches"] != correct or record["expected"] != expected:
            errors.append(f"scoring changed: {run_id}")
        row = {key: value for key, value in record.items() if key != "cli"}
        rows.append(row)
        groups[(record["host"], record["condition"])].append(row)
    grouped = []
    for (host, condition), values in sorted(groups.items()):
        grouped.append({
            "host": host, "condition": condition, "requests": len(values),
            "cli_calls": sum(not row["cache_hit"] for row in values),
            "cache_hits": sum(row["cache_hit"] for row in values),
            "matches": sum(row["matches"] for row in values),
            "errors": sum(bool(row["error"]) for row in values),
            "end_to_end_total_s": sum(row["end_to_end_s"] for row in values),
            "end_to_end_mean_s": mean(row["end_to_end_s"] for row in values),
            "reported_input_tokens": sum(row["reported_tokens"]["input"] or 0 for row in values),
            "reported_output_tokens": sum(row["reported_tokens"]["output"] or 0 for row in values),
            "reported_cost_usd": sum(row["reported_cost_usd"] or 0 for row in values)
            if host == "claude" else None,
        })
    summary = {
        "planned_requests": len(expected_ids), "observed_requests": len(records),
        "missing": sorted(expected_ids - records.keys()),
        "unexpected": sorted(records.keys() - expected_ids),
        "validation_errors": errors, "groups": grouped, "rows": rows,
        "total_cli_calls": sum(not row["cache_hit"] for row in rows),
        "total_cache_hits": sum(row["cache_hit"] for row in rows),
        "real_world_repeat_rate": None,
    }
    save(ROOT / "summary.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, indent=2))
    if errors or summary["missing"] or summary["unexpected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
