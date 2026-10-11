"""Recheck preserved files after a documented checker fix; never rerun an AI."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from check_host_result import check_case

parser = argparse.ArgumentParser()
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
root = args.evidence.resolve()
original = root / "host-runs-initial.json"
if original.exists():
    raise SystemExit("This evidence was already rechecked; retain another explicit revision instead of overwriting it.")
shutil.copyfile(root / "host-runs.json", original)
runs = json.loads(original.read_text())
for run in runs:
    case = root / run["case_root"]
    frozen = json.loads((case / "frozen-input.json").read_text())
    initial = json.loads((root / run["file_checks"]).read_text())
    checked = check_case(case, frozen)
    checked["avatar_flow"] = initial["avatar_flow"]
    checked["passed"] = checked["passed"] and checked["avatar_flow"]
    (case / "file-checks-rechecked.json").write_text(json.dumps(checked, indent=2))
    run["initial_file_checks"] = run["file_checks"]
    run["initial_file_checks_passed"] = run["file_checks_passed"]
    run["file_checks"] = str(case.relative_to(root) / "file-checks-rechecked.json")
    run["file_checks_passed"] = checked["passed"]
    print(json.dumps({"case": run["case_root"], "initial": initial["passed"], "rechecked": checked["passed"]}))
new_checker = Path(__file__).parent / "check_host_result.py"
shutil.copyfile(new_checker, root / "check_host_result-rechecked.py")
correction = {"reason": "The initial checker rejected bulleted Applied criteria records that Stage already accepts.",
              "old_checker_sha256": hashlib.sha256((root / "check_host_result.py").read_bytes()).hexdigest(),
              "new_checker_sha256": hashlib.sha256(new_checker.read_bytes()).hexdigest(),
              "model_reruns": 0, "product_changes": 0, "raw_output_changes": 0,
              "expectations_changed": False, "tests": {"red": "checker-red.log", "green": "checker-green.log"}}
(root / "checker-correction.json").write_text(json.dumps(correction, indent=2))
(root / "host-runs.json").write_text(json.dumps(runs, indent=2))
