"""합성 시험의 원본 응답을 보존하고 조건별·문제별로 집계합니다."""

from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import json
from pathlib import Path
import statistics
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def main(repaired: bool = False) -> None:
    suite = "repaired" if repaired else "followup"
    folder = ROOT / "runs" / f"2026-10-05-{suite}"
    rubric = json.loads((ROOT / f"{suite}-rubric.json").read_text(encoding="utf-8"))
    manifest = json.loads((folder / "manifest.json").read_text())
    rows: list[dict[str, Any]] = []
    for path in sorted(folder.glob("*--*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        result = data.get("result") or {}
        raw = result.get("result") or ""
        clean = raw.strip()
        if clean.startswith("```") and clean.endswith("```"):
            clean = "\n".join(clean.splitlines()[1:-1])
        try:
            answer = json.loads(clean)
            if not isinstance(answer, dict):
                raise ValueError("JSON 객체가 아닙니다.")
            parse_error = None
        except (ValueError, TypeError) as error:
            answer, parse_error = {}, str(error)
        expected = rubric[data["case"]]["expected"][data["condition"]]
        usage = result.get("usage") or {}
        input_tokens = sum(usage.get(key, 0) for key in (
            "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        rows.append({
            "id": data["run_id"], "case": data["case"], "family": data["family"],
            "condition": data["condition"], "repeat": data["repeat"],
            "answer": answer, "parse_error": parse_error, "raw_output": raw,
            "execution_error": data["error"] or result.get("is_error") or not result,
            "matches_preregistered_label": answer.get("decision") in expected,
            "false_complete": rubric[data["case"]].get("actual_state") == "incomplete"
                              and answer.get("decision") == "complete",
            "wall_time_s": data["wall_time_s"],
            "reported_cost_usd": result.get("total_cost_usd") or 0,
            "reported_input_tokens_including_cache": input_tokens,
            "reported_output_tokens": usage.get("output_tokens", 0),
            "reported_thinking_tokens": usage.get("output_tokens_details", {}).get("thinking_tokens"),
            "model_usage": result.get("model_usage"),
        })
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    cases: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["family"], row["condition"]].append(row)
        cases[row["case"], row["condition"]].append(row)
    aggregate = []
    for (family, condition), items in sorted(groups.items()):
        aggregate.append({
            "family": family, "condition": condition, "trials": len(items),
            "cases": len({r["case"] for r in items}),
            "label_matches": sum(r["matches_preregistered_label"] for r in items),
            "false_complete": sum(r["false_complete"] for r in items),
            "decisions": dict(Counter(r["answer"].get("decision") for r in items)),
            "reported_cost_usd": sum(r["reported_cost_usd"] for r in items),
            "mean_wall_time_s": statistics.mean(r["wall_time_s"] for r in items),
            "mean_input_tokens": statistics.mean(
                r["reported_input_tokens_including_cache"] for r in items),
            "mean_output_tokens": statistics.mean(r["reported_output_tokens"] for r in items),
        })
    case_counts = [{"case": key[0], "condition": key[1], "trials": len(items),
                    "label_matches": sum(r["matches_preregistered_label"] for r in items),
                    "decisions": dict(Counter(r["answer"].get("decision") for r in items))}
                   for key, items in sorted(cases.items())]
    output = {
        "planned": len(manifest["schedule"]), "observed": len(rows),
        "all_scheduled_records_present": len(rows) == len(manifest["schedule"]),
        "errors": sum(bool(r["execution_error"] or r["parse_error"]) for r in rows),
        "reported_cost_usd": sum(r["reported_cost_usd"] for r in rows),
        "groups": aggregate, "cases": case_counts, "rows": rows,
        "warning": "사전 기준과의 일치만 집계합니다. 모호한 문제와 정보 차이는 보고서를 보세요.",
    }
    (ROOT / "runs" / f"2026-10-05-{suite}-summary.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k not in ("rows", "cases")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repaired", action="store_true")
    main(parser.parse_args().repaired)
