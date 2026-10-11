"""Retain stricter checks separately after independent QA found missed failures."""
import hashlib
import json
from pathlib import Path
import shutil

from check_host_result import check_case

root = Path(__file__).parent / "evidence/2026-10-07-handoff"
prior = root / "host-runs-after-prefix-fix.json"
if prior.exists():
    raise SystemExit("The QA audit already exists; do not overwrite it.")
shutil.copyfile(root / "host-runs.json", prior)
runs = json.loads(prior.read_text())
for run in runs:
    case = root / run["case_root"]
    frozen = json.loads((root / run["frozen_input"]).read_text())
    sender = (root / run["sender_raw"]).parent.parent
    frozen["sender_card_text"] = (sender / "project" / frozen["card"]).read_text()
    frozen["require_next_action_update"] = True
    checked = check_case(case, frozen)
    (case / "qa-check-input.json").write_text(json.dumps(frozen, indent=2))
    (case / "qa-file-checks.json").write_text(json.dumps(checked, indent=2))
    run["prior_frozen_input"] = run["frozen_input"]
    run["prior_file_checks"] = run["file_checks"]
    run["frozen_input"] = str(case.relative_to(root) / "qa-check-input.json")
    run["file_checks"] = str(case.relative_to(root) / "qa-file-checks.json")
    run["file_checks_passed"] = checked["passed"]
    print(json.dumps({"case": run["case_root"], **checked}))
shutil.copyfile(Path(__file__).parent / "check_host_result.py", root / "check_host_result-after-qa.py")
(root / "qa-checker-correction.json").write_text(json.dumps({
    "reason": "Check newly added applied records, unsupported superseded claims, and stale Next action.",
    "baseline_source": "Each preserved sender card; original model output and input stay unchanged.",
    "model_reruns": 0, "product_changes": 0, "new_checks": True,
    "checker_sha256": hashlib.sha256((root / "check_host_result-after-qa.py").read_bytes()).hexdigest(),
    "review": "qa-review.json", "tests": ["qa-checker-red.log", "qa-checker-green.log"]}, indent=2))
(root / "host-runs.json").write_text(json.dumps(runs, indent=2))
