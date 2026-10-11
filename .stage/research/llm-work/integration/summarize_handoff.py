"""Summarize observations without turning missing measurements into zeroes."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
rows = []
index = args.evidence / "host-runs.json"
runs = (json.loads(index.read_text()) if index.exists() else
        [json.loads(path.read_text()) for path in sorted(args.evidence.glob("*-to-*/run.json"))])
for run in sorted(runs, key=lambda r: (r["direction"], r["condition"])):
    path = args.evidence / run["case_root"] / "run.json"
    result = json.loads((path.parent / "model/result.json").read_text())
    checks = json.loads((args.evidence / run["file_checks"]).read_text())
    records = result.get("usage", [])
    usage = [record.get("usage", record) for record in records]
    cost = [record["reported_cost_usd"] for record in records if record.get("reported_cost_usd") is not None]
    rows.append({"direction": run["direction"], "condition": run["condition"],
                 "exit": run["exit"], "passed": checks["passed"], "checks": checks,
                 "seconds": result["elapsed_seconds"],
                 "input_tokens": sum(u.get("input_tokens", 0) for u in usage) if usage else None,
                 "cached_input_tokens": sum(u.get("cached_input_tokens", u.get("cache_read_input_tokens", 0)) for u in usage) if usage else None,
                 "cache_creation_tokens": sum(u.get("cache_creation_input_tokens", u.get("cache_write_input_tokens", 0)) for u in usage) if usage else None,
                 "output_tokens": sum(u.get("output_tokens", 0) for u in usage) if usage else None,
                 "reported_cost_usd": sum(cost) if cost else None,
                 "session_ids": result["session_ids"], "assistant_text": result["assistant_text"],
                 "prompt_bytes": (path.parent / "model/prompt.txt").stat().st_size})
summary = {"cases": rows, "complete_matrix": len(rows) == 6,
           "passed_cases": sum(row["passed"] and row["exit"] == 0 for row in rows),
           "file_checks_passed_cases": sum(row["passed"] for row in rows),
           "normally_completed_cases": sum(row["exit"] == 0 for row in rows),
           "limits": ["CLI sessions, not individual API requests, are counted as cases.",
                      "Input and cache fields follow each provider's reporting and are not directly comparable.",
                      "Null price means no observed price; it does not mean free.",
                      "Question requests need transcript review; no automatic zero is assumed."]}
(args.evidence / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
for row in rows:
    print(json.dumps({k: v for k, v in row.items() if k not in {"assistant_text", "checks"}}, ensure_ascii=False))
    print(row["checks"])
    print(row["assistant_text"])
