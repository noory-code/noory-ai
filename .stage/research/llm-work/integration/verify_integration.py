"""Validate saved observations; never infer a real host run from CLI fixtures."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from check_host_result import card_snapshot, check_case, contained


def projections_include_refs(projections: list, refs: list[str]) -> bool:
    recorded = {version.get("ref") for projection in projections
                if projection.get("producer") == "distill"
                and projection.get("history", {}).get("project") == "test/demo-app"
                for version in projection.get("history", {}).get("versions", [])}
    return set(refs).issubset(recorded)


def verify(path: Path, require_real_hosts: bool, host_path: Path | None = None) -> dict:
    calls = json.loads((path / "calls.json").read_text())
    by_label = {record["label"]: record for record in calls}
    if len(by_label) != len(calls):
        raise ValueError("Duplicate command labels")
    if any(record["exit"] != 0 for record in calls):
        raise ValueError("A public CLI command failed")

    def data(label):
        return json.loads(by_label[label]["stdout"])

    first, revised = data("record-v1"), data("revise-v2")
    if data("replay-v1") != {**first, "replayed": True}:
        raise ValueError("Replay did not preserve the first result")
    packet = by_label["packet-v2"]["stdout"]
    current_section = packet.split("## Criteria as of check", 1)[1].split("## Prior result evidence", 1)[0]
    if revised["ref"] not in current_section or first["ref"] in current_section:
        raise ValueError("Current criteria section contains the wrong version")
    if first["ref"] + ": superseded" not in packet:
        raise ValueError("The earlier applied criterion was not marked superseded")
    if [r["status"] for r in data("check-exclusions")["results"]] != ["unconfirmed", "scope_mismatch"]:
        raise ValueError("Ineligible criteria were not excluded")
    if data("avatar-proposed-export")["criteria"]:
        raise ValueError("Avatar exported an unconfirmed proposal")
    confirmed = data("avatar-confirm")["ref"]
    if [c["ref"] for c in data("avatar-confirmed-export")["criteria"]] != [confirmed]:
        raise ValueError("Avatar export lost the confirmed version")
    if not data("attach-older")["newer_projection_exists"]:
        raise ValueError("Old history was not identified as historical")
    if data("check-revoked")["results"][0]["status"] != "revoked":
        raise ValueError("The revoked version remains eligible")
    if len(data("avatar-show")["projections"]) != 4:
        raise ValueError("Projection histories were lost or merged")
    if confirmed not in by_label["packet-with-avatar"]["stdout"]:
        raise ValueError("Stage did not carry Avatar's actual export")
    for label, status in (("packet-changed", "changed"), ("packet-missing", "missing")):
        if f'"status": "{status}"' not in by_label[label]["stdout"]:
            raise ValueError("File evidence was not rechecked")
    sources = json.loads((path / "sources.json").read_text())
    changed = [name for name, digest in sources.items()
               if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest]
    if changed:
        raise ValueError("Source changed after this run: " + ", ".join(changed))
    if require_real_hosts:
        host_path = (host_path or path).resolve()
        host_file = host_path / "host-runs.json"
        if not host_file.is_file():
            raise ValueError("Real Claude/Codex handoff evidence is missing; CLI contract checks do not substitute for it")
        bundled = (host_path / "bundled-recording-plan.md").is_file()
        if bundled:
            executed_wrapper = host_path / "fixture_avatar_batch.py"
            reviewed_wrapper = Path(__file__).parent / "fixture_avatar_batch.py"
            if (not executed_wrapper.is_file()
                    or hashlib.sha256(executed_wrapper.read_bytes()).digest()
                    != hashlib.sha256(reviewed_wrapper.read_bytes()).digest()):
                raise ValueError("The executed recording wrapper differs from the reviewed source")
        runs = json.loads(host_file.read_text())
        archived = host_path / "fixture-paths.json"
        if archived.exists():
            for entry in json.loads(archived.read_text()):
                saved = contained(host_path, entry["stored"])
                if hashlib.sha256(saved.read_bytes()).hexdigest() != entry["sha256"]:
                    raise ValueError("An archived fixture card changed")
        required = {(direction, condition) for direction in ("claude-to-codex", "codex-to-claude")
                    for condition in ("C0", "C1", "C2")}
        observed = {(r["direction"], r["condition"]) for r in runs if r.get("real_cli") is True}
        if observed != required or len(runs) != len(required):
            raise ValueError("Real host matrix is incomplete")
        if json.loads((host_path / "sources.json").read_text()) != sources:
            raise ValueError("The CLI and real-host runs used different product sources")
        for run in runs:
            for field in ("sender_raw", "receiver_raw", "file_checks", "frozen_input"):
                target = contained(host_path, run[field])
                if not target.is_file() or not target.stat().st_size:
                    raise ValueError("Missing host evidence: " + field)
            if run.get("exit") != 0 or run.get("file_checks_passed") is not True:
                raise ValueError("A real host case did not pass")
            for field, host in zip(("sender_raw", "receiver_raw"), run["direction"].split("-to-")):
                target = contained(host_path, run[field])
                events = [json.loads(line) for line in target.read_text().splitlines() if line.strip()]
                completed = (any(e.get("type") == "turn.completed" for e in events) if host == "codex"
                             else any(e.get("type") == "result" and not e.get("is_error") for e in events))
                metadata = json.loads((target.parent / "result.json").read_text())
                if not completed or metadata["exit"] != 0 or metadata["host"] != host or not metadata["session_ids"]:
                    raise ValueError("Host completion evidence is invalid: " + field)
            frozen = json.loads(contained(host_path, run["frozen_input"]).read_text())
            if frozen["condition"] != run["condition"]:
                raise ValueError("Frozen condition differs from the recorded run")
            if "sender_card_text" not in frozen:
                raise ValueError("The sender card baseline is required to check receiver records")
            sender_project = contained(host_path, run["sender_raw"]).parent.parent / "project"
            reuse = sender_project.parent / "reuse.json"
            if bundled and not reuse.is_file():
                raise ValueError("A bundled run requires each reused sender manifest")
            if reuse.exists():
                manifest = json.loads(reuse.read_text())
                if manifest.get("new_model_call") is not False:
                    raise ValueError("A reused sender must not be counted as a new model call")
                for relative, digest in manifest["source_files"].items():
                    saved = contained(sender_project.parent, relative)
                    if not saved.exists() and relative.endswith(".md.txt"):
                        saved = contained(sender_project.parent, relative[:-4])
                    if hashlib.sha256(saved.read_bytes()).hexdigest() != digest:
                        raise ValueError("A reused sender artifact changed: " + relative)
            if frozen["sender_card_text"] != card_snapshot(sender_project, frozen["card"]).read_text():
                raise ValueError("The baseline does not match the preserved sender card")
            checked = check_case(contained(host_path, run["case_root"]), frozen)
            if not checked["passed"]:
                raise ValueError("Independent file check failed: " + json.dumps(checked))
            case = contained(host_path, run["case_root"])
            if (host_path / "real-host-followup-plan.md").is_file():
                if not any('"path": "app/port.py"' in line and '"status": "matches"' in line
                           for line in (case / "packet.md").read_text().splitlines()):
                    raise ValueError("Stage did not report matching prior file evidence")
            if frozen["condition"] != "C0":
                receipt = json.loads((case / "project/.data/receiver-check.json").read_text())
                if not any(r.get("ref") == frozen["expected_applied_ref"] and r.get("status") == "eligible_current"
                           for r in receipt.get("results", [])):
                    raise ValueError("The receiving session did not save a current-criterion check")
                raw = contained(host_path, run["receiver_raw"]).read_text()
                events = [json.loads(line) for line in raw.splitlines() if line.strip()]
                commands = [e.get("item", {}).get("command", "") for e in events]
                commands += [block.get("input", {}).get("command", "") for e in events
                             for block in e.get("message", {}).get("content", [])
                             if isinstance(block, dict) and block.get("name") == "Bash"]
                if not any("criteria" in command and "check" in command for command in commands):
                    raise ValueError("The raw tool trace does not show a criteria check command")
            shown = json.loads(json.loads((case / "avatar-observation.json").read_text())["stdout"])
            exported = json.loads(json.loads((case / "avatar-export.json").read_text())["stdout"])
            invalid = checked["observed"]["invalid"]
            choice = ("None" if invalid == {"returned": None} else
                      "ConfigError" if invalid == {"raised": "ConfigError"} else "other")
            refs = [] if frozen["condition"] == "C0" else [frozen["expected_applied_ref"]]
            if not any(c.get("chosen") == choice and c.get("source_refs") == refs
                       and c.get("origin", {}).get("actor") == "user" for c in shown["choices"]):
                raise ValueError("Avatar does not record the observed choice and applied refs")
            if not any(c.get("confirmation") == "user_confirmed" and c.get("ref", "").endswith("@2")
                       for c in exported["criteria"]):
                raise ValueError("Avatar confirmation evidence is missing")
            if not projections_include_refs(shown["projections"], refs):
                raise ValueError("Avatar history does not include the applied Distill ref")
    return {"cli_contract": "passed", "commands": len(calls),
            "real_hosts": "required evidence checked" if require_real_hosts else "not verified"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=Path(__file__).parent / "evidence/2026-10-06-contract")
    parser.add_argument("--require-real-hosts", action="store_true")
    parser.add_argument("--host-evidence", type=Path, default=Path(__file__).parent / "evidence/2026-10-07-handoff-bundled")
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.evidence, args.require_real_hosts, args.host_evidence)))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"passed": False, "error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
