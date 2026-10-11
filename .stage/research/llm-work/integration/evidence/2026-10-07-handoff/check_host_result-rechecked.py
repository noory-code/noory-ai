"""Check a receiver's files independently of its own completion claim."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PROBE = """import importlib, json
module = importlib.import_module('app.host')
def observe(value):
    try:
        return {'returned': module.parse_host(value)}
    except Exception as error:
        return {'raised': type(error).__name__}
print(json.dumps({'valid': observe('example.com'), 'invalid': observe('bad')}))
"""


def contained(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    path.relative_to(root.resolve())
    return path


def check_case(case_root: Path, frozen: dict) -> dict:
    project = contained(case_root, frozen["project_dir"])
    port = contained(project, "app/port.py")
    host = contained(project, "app/host.py")
    card = contained(project, frozen["card"])
    if not host.is_file():
        raise ValueError("The receiver did not create app/host.py")
    port_sha = hashlib.sha256(port.read_bytes()).hexdigest()
    unchanged = port_sha == frozen["sender_port_sha256"]
    probe = subprocess.run([sys.executable, "-c", PROBE], cwd=project,
                           capture_output=True, text=True, encoding="utf-8", timeout=10)
    if probe.returncode:
        raise ValueError("The receiver's file could not run: " + probe.stderr)
    observed = json.loads(probe.stdout)
    valid = observed["valid"] == {"returned": "example.com"}
    condition = frozen["condition"]
    if condition not in {"C0", "C1", "C2"}:
        raise ValueError("Unknown condition")
    expected = {"C1": {"raised": "ConfigError"}, "C2": {"returned": None}}
    contract = condition == "C0" or observed["invalid"] == expected[condition]
    body = card.read_text(encoding="utf-8")
    applied_lines = re.findall(
        r"(?m)^\s*(?:[-*]\s+)?(?:\d{4}-\d{2}-\d{2}:\s*)?Applied criteria:\s*([^\n]+)$", body)
    refs = {ref.strip() for line in applied_lines for ref in line.split(",")}
    applied = frozen["expected_applied_ref"] in refs
    stale_ref = frozen.get("stale_ref")
    stale = stale_ref is None or f"Stale judgment: {stale_ref} superseded" in body
    return {"passed": unchanged and valid and contract and applied and stale,
            "condition": condition, "port_unchanged": unchanged, "port_sha256": port_sha,
            "valid_host": valid, "invalid_contract": contract, "observed": observed,
            "applied_ref_recorded": applied, "stale_judgment_recorded": stale,
            "limits": ["C0 has no required invalid-input contract; its outcome is observational.",
                       "This checks files and records, not whether an AI CLI produced them."]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-root", required=True, type=Path)
    parser.add_argument("--frozen-input", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = check_case(args.case_root.resolve(), json.loads(args.frozen_input.read_text()))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        result = {"passed": False, "error": str(error)}
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
