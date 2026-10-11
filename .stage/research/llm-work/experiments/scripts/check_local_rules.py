"""정해진 입력의 분기와 완료 조건을 모델 없이 검사합니다."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_followup import route


def may_finish(checks: dict[str, bool]) -> bool:
    return bool(checks) and all(value is True for value in checks.values())


def main() -> None:
    examples: list[tuple[dict[str, Any], str]] = [
        ({"schema": 1, "type": "read"}, "execute"),
        ({"schema": 1, "type": "write", "approved": True}, "execute"),
        ({"schema": 1, "type": "write", "approved": False}, "ask"),
        ({"schema": 1, "type": "write"}, "fallback"),
        ({"schema": 1, "type": "write", "approved": "true"}, "fallback"),
        ({"schema": 1, "type": "write", "approved": 1}, "fallback"),
        ({"schema": 1, "type": "delete", "approved": True}, "fallback"),
        ({"schema": 2, "type": "read"}, "fallback"),
        ({"schema": True, "type": "read"}, "fallback"),
        ({"schema": "1", "type": "read"}, "fallback"),
        ({"schema": 1.0, "type": "read"}, "fallback"),
        ({"schema": 1, "type": "READ"}, "fallback"),
        ({"schema": 1, "type": "read and write"}, "fallback"),
        ({"text": "먼저 읽고 필요하면 수정"}, "fallback"),
        ({}, "fallback"),
    ]
    rows = [{"input": data, "expected": expected, "actual": route(data)}
            for data, expected in examples]
    completion = [
        ({}, False),
        ({"report_saved": True, "results_verified": False}, False),
        ({"report_saved": True, "results_verified": True}, True),
    ]
    finish_rows = [{"checks": checks, "expected": expected, "actual": may_finish(checks)}
                   for checks, expected in completion]
    assert all(r["actual"] == r["expected"] for r in [*rows, *finish_rows])
    output = {"routing": rows, "completion": finish_rows, "passed": 18,
              "model_calls": 0,
              "limit": "모의 계약을 검사했습니다. 실제 서비스 통합이나 목적 해석은 시험하지 않았습니다."}
    path = Path(__file__).resolve().parents[1] / "runs" / "2026-10-05-local-rules.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": 18, "model_calls": 0}))


if __name__ == "__main__":
    main()
