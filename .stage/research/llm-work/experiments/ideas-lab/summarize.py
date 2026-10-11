"""고정한 기준과 공개 응답을 비교하고 오답과 미실행도 남깁니다."""

from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

from run_models import digest, make_prompt, matches, save

ROOT = Path(__file__).resolve().parent


def main() -> None:
    cases = {case["id"]: case for case in json.loads((ROOT / "cases.json").read_text())}
    directory = ROOT / "runs" / "comparison"
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["cases_sha256"] != digest((ROOT / "cases.json").read_bytes()):
        raise ValueError("비교 자료가 실행할 때와 다릅니다.")
    rows = []
    grouped = defaultdict(list)
    validation = []
    for filename, expected in manifest["source_hashes"].items():
        if digest((ROOT / filename).read_bytes()) != expected:
            validation.append(f"source changed: {filename}")
    for path in sorted(directory.glob("*--*.json")):
        record = json.loads(path.read_text())
        case = cases[record["case"]]
        condition = record["condition"]
        if record["input_sha256"] != digest(make_prompt(case, condition).encode()):
            validation.append(f"input changed: {record['id']}")
        result = record.get("result") or {}
        usage = result.get("usage") or {}
        if record["host"] == "claude":
            input_tokens = sum(usage.get(key, 0) or 0 for key in (
                "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            thinking = (usage.get("output_tokens_details") or {}).get("thinking_tokens")
        else:
            input_tokens = usage.get("input_tokens")
            thinking = usage.get("reasoning_output_tokens")
        answer = record.get("answer")
        row = {"id": record["id"], "idea": case["idea"], "host": record["host"],
               "condition": condition, "expected": case["expected"], "answer": answer,
               "matches": matches(answer, case["expected"]) if answer else False,
               "error": record.get("error"), "wall_time_s": record["wall_time_s"],
               "reported_input_tokens": input_tokens,
               "reported_output_tokens": usage.get("output_tokens"),
               "reported_thinking_tokens": thinking,
               "reported_cost_usd": result.get("total_cost_usd"),
               "prompt_characters": len(record["prompt"]), "scoring_note": case["scoring_note"]}
        rows.append(row)
        grouped[(row["idea"], row["host"], condition)].append(row)
    groups = []
    for (idea, host, condition), group in sorted(grouped.items()):
        groups.append({"idea": idea, "host": host, "condition": condition,
                       "runs": len(group), "matches": sum(row["matches"] for row in group),
                       "errors": sum(bool(row["error"]) for row in group),
                       "mean_wall_time_s": mean(row["wall_time_s"] for row in group),
                       "mean_prompt_characters": mean(row["prompt_characters"] for row in group),
                       "mean_reported_output_tokens": mean(row["reported_output_tokens"] or 0 for row in group)})
    expected_ids = {f"{row['case']}--{row['condition']}--{row['host']}--{row['repeat']}"
                    for row in manifest["schedule"]}
    observed_ids = {row["id"] for row in rows}
    summary = {"planned": len(expected_ids), "observed": len(rows),
               "missing": sorted(expected_ids - observed_ids),
               "unexpected": sorted(observed_ids - expected_ids),
               "validation_errors": validation,
               "errors": sum(bool(row["error"]) for row in rows),
               "claude_reported_cost_usd": sum(row["reported_cost_usd"] or 0 for row in rows),
               "codex_reported_cost_usd": None,
               "groups": groups, "rows": rows}
    save(ROOT / "summary.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
