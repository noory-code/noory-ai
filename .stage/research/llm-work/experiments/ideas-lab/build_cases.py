"""시제품을 실행해 비교 자료를 저장하며 기존 입력은 덮어쓰지 않습니다."""

from collections import Counter
import json
from pathlib import Path

import evidence
import recovery
import replay
from run_models import digest, save

ROOT = Path(__file__).resolve().parent


def main() -> None:
    destination = ROOT / "cases.json"
    if destination.exists():
        raise SystemExit("입력 파일이 이미 있습니다. 기존 입력을 보존합니다.")
    cases = [case for module in (evidence, recovery, replay) for case in module.build_cases()]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("중복된 사례 ID가 있습니다.")
    counts = Counter(case["idea"] for case in cases)
    if counts != Counter({f"I{number:02d}": 4 for number in range(1, 7)}):
        raise ValueError(f"아이디어별 사례 수가 다릅니다: {counts}")
    for case in cases:
        if not {"id", "idea", "task", "baseline", "enhanced", "expected", "scoring_note"} <= set(case):
            raise ValueError(f"필드 누락: {case['id']}")
        if set(case["expected"]) != {"action", "targets"}:
            raise ValueError(f"기대값 형식 오류: {case['id']}")
        if case["baseline"] == case["enhanced"]:
            raise ValueError(f"조건 차이가 없습니다: {case['id']}")
    save(destination, cases)
    save(ROOT / "input-manifest.json", {
        "cases_sha256": digest(destination.read_bytes()),
        "counts": counts,
        "source_hashes": {name: digest((ROOT / name).read_bytes()) for name in
                          ("evidence.py", "recovery.py", "replay.py", "build_cases.py")},
    })
    print(json.dumps({"cases": len(cases), "counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
