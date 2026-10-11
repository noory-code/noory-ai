"""입력 해시와 실행 수를 확인한 뒤 비교 결과를 집계합니다."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    manifest = json.loads((ROOT / "runs" / "manifest.json").read_text())
    records = [json.loads(path.read_text()) for path in sorted((ROOT / "runs").glob("*.json"))
               if path.name != "manifest.json"]
    errors = []
    expected_ids = {f"{task}--{condition}--{host}--r{repeat}"
                    for task, condition, host, repeat in manifest["schedule"]}
    if len(records) != len(expected_ids) or {row["id"] for row in records} != expected_ids:
        errors.append("실행 목록이 계획과 다릅니다.")
    for name, path in (("probe.py", ROOT / "probe.py"), ("snapshot.json", ROOT / "snapshot.json"),
                       ("prior_cli", ROOT.parent / "ideas-lab" / "run_models.py")):
        if digest(path.read_bytes()) != manifest["source_hashes"][name]:
            errors.append(f"실행 입력 또는 스크립트가 바뀌었습니다: {name}")
    for row in records:
        cli = row["cli"]
        if digest(cli["prompt"].encode()) != row["prompt_sha256"] or row["prompt_sha256"] != cli["input_sha256"]:
            errors.append(f"입력 해시가 다릅니다: {row['id']}")
        if cli["error"]:
            errors.append(f"CLI 오류: {row['id']}: {cli['error']}")
        answer = cli["answer"] or {}
        actual_match = (answer.get("action") == row["expected"]["action"]
                        and sorted(answer.get("targets", [])) == sorted(row["expected"]["targets"]))
        if actual_match != row["matches"]:
            errors.append(f"판정 집계가 다릅니다: {row['id']}")

    groups = []
    for host in ("claude", "codex"):
        for condition in ("baseline", "selected", "evidence"):
            rows = [row for row in records if row["host"] == host and row["condition"] == condition]
            if not rows:
                continue
            inputs, outputs, costs = [], [], []
            for row in rows:
                result = row["cli"]["result"] or {}
                usage = result.get("usage") or {}
                value = (sum(usage.get(key, 0) or 0 for key in (
                    "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
                         if host == "claude" else usage.get("input_tokens"))
                inputs.append(value)
                outputs.append(usage.get("output_tokens"))
                costs.append(result.get("total_cost_usd"))
            groups.append({
                "host": host, "condition": condition, "calls": len(rows),
                "matches": sum(row["matches"] for row in rows),
                "mean_prompt_characters": mean(row["prompt_characters"] for row in rows),
                "mean_request_seconds": mean(row["request_seconds"] for row in rows),
                "mean_cli_seconds": mean(row["cli"]["wall_time_s"] for row in rows),
                "reported_input_tokens": sum(inputs) if all(v is not None for v in inputs) else None,
                "reported_output_tokens": sum(outputs) if all(v is not None for v in outputs) else None,
                "reported_cost_usd": round(sum(costs), 8) if all(v is not None for v in costs) else None,
            })
    summary = {
        "independent_work_cases": 1, "questions_per_case": 2, "calls": len(records),
        "matches": sum(row["matches"] for row in records), "validation_errors": errors,
        "groups": groups,
        "mismatches": [{"id": row["id"], "expected": row["expected"], "answer": row["cli"]["answer"]}
                       for row in records if not row["matches"]],
        "limits": ["All correctness checks concern supplied records and explicit evidence policy.",
                   "The evidence condition has extra information and different expected version action.",
                   "Manual evidence selection cost is excluded; evidence retrieval was not tested.",
                   "Two repetitions per question are not independent work cases.",
                   "CLI timings include startup and service variance; no full task cost claim.",
                   "Reported cost is not a verified invoice; Codex monetary cost is unavailable."],
    }
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
