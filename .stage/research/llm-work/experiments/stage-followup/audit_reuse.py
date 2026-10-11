"""실제 Stage 로그에서 판단 재사용 비율을 계산할 근거가 남았는지 조사합니다."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]


def main() -> None:
    output = ROOT / "reuse-audit.json"
    if output.exists():
        raise FileExistsError("이 시점의 조사 기록을 덮어쓰지 않습니다.")
    runtime = REPO / ".stage/.runtime/driver"
    logs, verdicts = [], []
    for path in sorted((runtime / "logs").glob("*.md")):
        text = path.read_text()
        logs.append({"path": str(path.relative_to(REPO)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "review_report_headings": len(re.findall(r"(?m)^### Reviewer report\s*$", text)),
                     "executor_report_headings": len(re.findall(r"(?m)^### Executor report\s*$", text)),
                     "fingerprint_word_present": bool(re.search(r"sha256|fingerprint|input_hash", text))})
    keys = Counter()
    fingerprint_keys = {"input_sha256", "input_hash", "request_hash", "source_hashes", "evidence_hashes",
                        "criteria_hash", "criteria_version", "model_settings_hash", "dependency_hashes"}
    for path in sorted((runtime / "verdicts").glob("*.json")):
        value = json.loads(path.read_text())
        names = set()

        def collect(item: object) -> None:
            if isinstance(item, dict):
                names.update(item)
                for child in item.values():
                    collect(child)
            elif isinstance(item, list):
                for child in item:
                    collect(child)

        collect(value)
        keys.update(names)
        verdicts.append({"path": str(path.relative_to(REPO)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "keys": sorted(names), "fingerprint_fields": sorted(names & fingerprint_keys),
                         "criterion_count": len(value.get("criteria", []))})
    result = {"observed_at": datetime.now(timezone.utc).isoformat(), "log_count": len(logs),
              "verdict_count": len(verdicts),
              "review_heading_count": sum(row["review_report_headings"] for row in logs),
              "logs_with_multiple_review_headings": sum(row["review_report_headings"] > 1 for row in logs),
              "verdict_key_counts": dict(keys),
              "verdicts_with_candidate_fingerprint_fields": sum(bool(row["fingerprint_fields"]) for row in verdicts),
              "reusable_request_rate": None, "logs": logs, "verdicts": verdicts,
              "limits": ["A report heading is not a model invocation ID.",
                         "Fingerprint words in prose are not captured review inputs.",
                         "This scans the present driver log and verdict directories only.",
                         "Missing provenance cannot establish a zero or positive reuse rate."]}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in {"logs", "verdicts"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
