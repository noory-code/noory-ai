"""Observe every saved case even when the strict completion gate stops at a timeout."""
import argparse
import json
from pathlib import Path

from check_host_result import check_case
from verify_integration import projections_include_refs

parser = argparse.ArgumentParser()
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
root = args.evidence
rows = []
for run in json.loads((root / "host-runs.json").read_text()):
    case = root / run["case_root"]
    frozen = json.loads((root / run["frozen_input"]).read_text())
    checked = check_case(case, frozen)
    shown = json.loads(json.loads((case / "avatar-observation.json").read_text())["stdout"])
    exported = json.loads(json.loads((case / "avatar-export.json").read_text())["stdout"])
    refs = [] if frozen["condition"] == "C0" else [frozen["expected_applied_ref"]]
    invalid = checked["observed"]["invalid"]
    choice = "None" if invalid == {"returned": None} else "ConfigError" if invalid == {"raised": "ConfigError"} else "other"
    choices_match = any(c.get("chosen") == choice and c.get("source_refs") == refs
                        and c.get("origin", {}).get("actor") == "user" for c in shown["choices"])
    confirmed = any(c.get("confirmation") == "user_confirmed" and c.get("ref", "").endswith("@2")
                    for c in exported["criteria"])
    rows.append({"case": run["case_root"], "exit": run["exit"], "file_checks": checked,
                 "avatar_choices_match": choices_match, "avatar_confirmation": confirmed,
                 "avatar_applied_history": projections_include_refs(shown["projections"], refs)})
(root / "saved-case-observations.json").write_text(json.dumps(rows, indent=2))
for row in rows:
    print(json.dumps({**row, "file_checks": row["file_checks"]["passed"]}))
