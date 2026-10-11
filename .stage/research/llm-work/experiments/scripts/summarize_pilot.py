"""저장한 실행 기록을 집계합니다. 답변의 의미는 별도로 검토합니다."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    rubric = load(root / "evidence-rubric.json")["criteria"]
    rows: list[dict[str, Any]] = []
    for suite in ("hooks", "evidence"):
        folder = root / "runs" / f"2026-10-05-{suite}"
        for path in sorted(folder.glob("*.json")):
            data = load(path)
            if not isinstance(data, dict) or "run_id" not in data:
                continue
            result = data["result"]
            counts = Counter(
                event["data"]["hook_event_name"] if event["kind"] == "hook"
                else event["kind"] for event in data["events"]
            )
            row: dict[str, Any] = {
                "suite": suite, "run_id": data["run_id"],
                "record": str(path.relative_to(root)),
                "error": data["error"], "is_error": result["is_error"],
                "reported_cost_usd": result["total_cost_usd"],
                "wall_time_s": data["wall_time_s"],
                "reported_model_usage": result["model_usage"],
                "event_counts": dict(counts),
            }
            if suite == "evidence":
                answer = json.loads(result["result"])
                case_id, condition = data["run_id"].split("-", 1)
                row.update({
                    "case": case_id, "condition": condition, "answer": answer,
                    "status_matches_rubric":
                        answer["status"] in rubric[case_id]["acceptable_status"],
                })
            rows.append(row)
    artifacts = [root / "scripts" / "run_pilot.py", root / "evidence-cases.json",
                 root / "evidence-rubric.json"]
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hashes_recorded_after_execution": True,
        "summary_python": platform.python_version(),
        "artifact_sha256": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in artifacts
        },
        "review_scope": "status만 자동 대조했습니다. 본문의 의미 검토는 분석 보고서에 남깁니다.",
        "cost_basis": "SDK가 보고한 값입니다. 실제 청구액을 조회하지 않았습니다.",
        "total_reported_cost_usd": sum(r["reported_cost_usd"] for r in rows),
        "rows": rows,
    }
    destination = root / "runs" / "2026-10-05-summary.json"
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"runs": len(rows), "total_reported_cost_usd":
                      output["total_reported_cost_usd"], "summary": str(destination)}))


if __name__ == "__main__":
    main()
