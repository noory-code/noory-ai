"""관찰한 전체 검사 실패가 수정 전 복사본에도 있었는지 추가로 확인합니다."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

import harness as H

ROOT = Path(__file__).resolve().parent


def main() -> None:
    output = ROOT / "diagnostics.json"
    if output.exists():
        raise FileExistsError("기존 진단을 덮어쓰지 않습니다.")
    case = next(row for row in H.CASES if row["id"] == "retrospective_owner_conflict")
    fixtures = json.loads((H.PREVIOUS / "fixtures.json").read_text())
    fixture = next(row for row in fixtures if row["id"] == case["id"])
    source = fixture["versions"]["before"]["files"][case["target"]]
    with tempfile.TemporaryDirectory(prefix="cross-session-diagnosis-") as directory:
        root = Path(directory)
        setup = H.setup(root, case, source)
        baseline = H.test(root, case, full=True)
    differences = H.PREP.git("diff", case["commit"] + "^", case["commit"], "--",
                             case["target"], case["test_file"]).decode()
    results = [json.loads(path.read_text()) for path in sorted(
        (ROOT / "runs").glob("retrospective_owner_conflict--*/*/result.json"))]
    H.save(output, {
        "timing": "Post hoc diagnosis after the planned model runs; no model calls or retries.",
        "case": case["id"], "setup": setup, "full_module_before_any_model_edit": baseline,
        "historical_commit_diff": differences,
        "model_visible_criterion": case["criterion"],
        "continuations": [{"id": row["id"],
                           "focused_returncode": row["verification"]["focused"]["returncode"],
                           "full_module_returncode": row["verification"]["full_module"]["returncode"],
                           "full_module_stderr": row["verification"]["full_module"]["stderr"]}
                          for row in results],
    })
    print(json.dumps({"case": case["id"], "baseline": baseline, "runs": len(results)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
