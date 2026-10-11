"""Run the frozen two-host, three-condition experiment on isolated projects."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from check_host_result import check_case
from host_process import run_host

PERSONAL = "Choose an explicit error contract that callers can predict."
CARD = ".stage/work/current/W-00000001/W-00000002/_story.md"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def origin(host: str, session: str, quote: str) -> dict:
    return {"kind": "user_statement", "source_ref": f"session:{host}/{session}/fixture-1",
            "quote": "[Synthetic test statement] " + quote, "actor": "user",
            "recorded_by": {"host": host, "session_id": session, "via": "cli"}}


class Experiment:
    def __init__(self, args: argparse.Namespace):
        self.out = args.out.resolve()
        self.out.mkdir(parents=True, exist_ok=False)
        self.scratch = Path(tempfile.mkdtemp(prefix="criteria-real-handoff-"))
        self.distill = [str(args.distill_python.absolute()), "-m", "distill", "criteria"]
        self.avatar = [sys.executable, str(args.avatar_root.resolve() / "scripts/avatar.py")]
        self.stage = [sys.executable, str(args.stage_root.resolve() / "scripts/handoff_packet.py")]
        self.sources = json.loads(args.source_manifest.read_text())
        changed = [path for path, sha in self.sources.items()
                   if hashlib.sha256(Path(path).read_bytes()).hexdigest() != sha]
        if changed:
            raise ValueError("Reviewed product source changed: " + ", ".join(changed))
        write_json(self.out / "sources.json", self.sources)
        for name in ("real-host-plan.md", "run_real_handoff.py", "host_process.py", "check_host_result.py"):
            shutil.copyfile(Path(__file__).parent / name, self.out / name)
        write_json(self.out / "environment.json", {"scratch": str(self.scratch), "python": sys.version,
            "codex": subprocess.check_output(["codex", "--version"], text=True).strip(),
            "claude": subprocess.check_output(["claude", "--version"], text=True).strip(),
            "requested_models": {"codex": "gpt-6-sol", "claude": "opus[1m]"},
            "real_user_data": False, "product_cli_contract": str(args.source_manifest.resolve())})

    def cli(self, output: Path, label: str, argv: list[str], cwd: Path, as_json: bool = True):
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=30)
        write_json(output / f"{label}.json", {"argv": argv, "exit": result.returncode,
                                             "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise ValueError(f"{label}: {result.stderr} {result.stdout}")
        return json.loads(result.stdout) if as_json else result.stdout

    def configure(self, project: Path) -> dict:
        config = {"distill": {"argv": self.distill[:-1], "db": str(project / ".data/distill.db")},
                  "avatar": {"argv": self.avatar, "home": str(project / ".data/avatar")}}
        write_json(project / ".data/producers.json", config)
        return config

    def shared_prompt(self, host: str, project: Path, label: str) -> str:
        return f"""This is a synthetic validation project. The quoted user statements are fixtures,
not evidence about the real user's personal preferences. Work only inside {project}.
Do not commit, use other agents, access personal stores, install packages, or edit plugin source.
Use the provided public CLI argv arrays; do not import plugin internals or open their databases.
Your host label is {host}; your synthetic session label is {label}, not a native session ID.
All JSON payloads are UTF-8. Run argv arrays without a shell using Python subprocess, or quote each
argument correctly in a shell. Preserve CLI JSON output in the receipt files requested below.
If information blocks completion, say what is missing. Do not invent user preferences.
Distill base argv: {json.dumps(self.distill + ['--db', str(project / '.data/distill.db')])}
The --db option belongs AFTER the subcommand, e.g. criteria current --db PATH --project test/demo-app.
Avatar base argv: {json.dumps(self.avatar + ['--home', str(project / '.data/avatar')])}
Stage packet argv: {json.dumps(self.stage + ['--project-root', str(project), 'W-00000002', '--project-key', 'test/demo-app', '--producers', str(project / '.data/producers.json')])}
"""

    def sender(self, host: str) -> dict:
        label = "sender-" + host
        output = self.out / label
        output.mkdir()
        project = self.scratch / label
        (project / "app").mkdir(parents=True)
        (project / "app/__init__.py").write_text("")
        (project / "app/errors.py").write_text("class ConfigError(ValueError):\n    pass\n")
        card = project / CARD
        card.parent.mkdir(parents=True)
        (card.parent.parent / "_epic.md").write_text("---\nid: W-00000001\nkind: planning\n---\n## Purpose\nMake configuration parsing predictable for callers.\n")
        card.write_text("---\nid: W-00000002\nkind: development\nscope: app/\n---\n## Purpose\nImplement configuration parsing in two steps.\n## Progress\n\n## Success criteria\n- Valid ports and hosts are parsed.\n## Next action\nImplement parse_port, then leave parse_host for the next session.\n")
        self.configure(project)
        payload = {"project": "test/demo-app", "statement": "Invalid configuration input raises ConfigError.",
                   "applies_when": [{"kind": "path", "any": ["app/"]}], "exceptions": [], "notes": [],
                   "overrides": [], "confirmation": "user_stated",
                   "origin": origin(host, label, "Invalid configuration input raises ConfigError.")}
        write_json(project / ".data/criterion-v1.json", payload)
        record = self.distill + ["record", "--db", str(project / ".data/distill.db"),
                   "--payload-file", str(project / ".data/criterion-v1.json"), "--idempotency-key", label + ":record"]
        prompt = self.shared_prompt(host, project, label) + f"""
Task P: first record the supplied synthetic user criterion with this exact public command:
{json.dumps(record)}
Save its actual JSON response to .data/record-result.json. Build and read the Stage packet.
Run criteria current and check the returned ref before applying it; save check output to .data/check-result.json.
Implement app/port.py with parse_port(value). Accept only digit strings representing 1..65535;
return the integer. Invalid values include 'bad', '', '0', '65536' and non-string inputs.
Use app.errors.ConfigError and follow the stored criterion for invalid values. Do not create host.py yet.
Record Applied criteria: <returned ref> in the card's Progress. Add file hash Evidence for app/port.py.
Set Next action to implement parse_host. Test the port behavior. Report changed files and remaining work.
"""
        result = run_host(host, project, output / "model", prompt)
        shutil.copytree(project, output / "project")
        if result["exit"] != 0:
            return {"host": host, "ok": False, "result": result}
        receipt = json.loads((project / ".data/record-result.json").read_text())
        check = self.cli(output, "check-v1", self.distill + ["check", "--db", str(project / ".data/distill.db"),
                         "--project", "test/demo-app", "--refs", receipt["ref"]], project)
        program = "from app.port import parse_port\nfrom app.errors import ConfigError\nassert parse_port('443') == 443\nfor v in ['bad', '', '0', '65536', None]:\n try: parse_port(v)\n except ConfigError: pass\n else: raise AssertionError(v)\nprint('port checks passed')\n"
        port_test = subprocess.run([sys.executable, "-c", program], cwd=project, capture_output=True, text=True, timeout=10)
        write_json(output / "port-check.json", {"exit": port_test.returncode, "stdout": port_test.stdout, "stderr": port_test.stderr})
        ok = port_test.returncode == 0 and check["results"][0]["status"] == "eligible_current"
        write_json(output / "sender-result.json", {"passed": ok, "ref": receipt["ref"]})
        print(json.dumps({"phase": label, "passed": ok, "seconds": result["elapsed_seconds"]}), flush=True)
        return {"host": host, "ok": ok, "project": project, "ref": receipt["ref"], "output": output}

    def receiver(self, sender: dict, condition: str) -> dict:
        host = "codex" if sender["host"] == "claude" else "claude"
        direction = sender["host"] + "-to-" + host
        label = direction + "-" + condition
        output = self.out / label
        output.mkdir()
        project = self.scratch / label
        shutil.copytree(sender["project"], project)
        for path in (project / ".data").glob("*.json"):
            path.unlink()
        self.configure(project)
        ref = sender["ref"]
        if condition == "C0":
            for path in (project / ".data").glob("distill.db*"):
                path.unlink()
        elif condition == "C2":
            payload = {"base_version": 1, "statement": "Invalid configuration input returns None.",
                       "reason": "Synthetic change: callers now handle absence.",
                       "origin": origin("fixture", label, "Invalid configuration input returns None.")}
            payload_path = output / "revision.json"
            write_json(payload_path, payload)
            changed = self.cli(output, "revision", self.distill + ["revise", ref.split(":")[1].split("@")[0],
                "--db", str(project / ".data/distill.db"), "--payload-file", str(payload_path),
                "--idempotency-key", label + ":revise"], project)
            ref = changed["ref"]
        packet_args = self.stage + ["--project-root", str(project), "W-00000002", "--project-key", "test/demo-app"]
        if condition != "C0":
            packet_args += ["--producers", str(project / ".data/producers.json")]
        packet = self.cli(output, "packet", packet_args, project, False)
        (output / "packet.md").write_text(packet, encoding="utf-8")
        frozen = {"condition": condition, "project_dir": "project", "card": CARD,
                  "sender_port_sha256": hashlib.sha256((project / "app/port.py").read_bytes()).hexdigest(),
                  "expected_applied_ref": "none" if condition == "C0" else ref,
                  "stale_ref": sender["ref"] if condition == "C2" else None}
        write_json(output / "frozen-input.json", frozen)
        choice_origin = origin(host, label, "Callers should be able to predict how errors are handled.")
        write_json(project / ".data/choice-origin.json", choice_origin)
        write_json(project / ".data/confirm-personal.json", {"origin": origin(host, label, "I confirm this synthetic personal criterion: " + PERSONAL)})
        prompt = self.shared_prompt(host, project, label) + f"""
Task H: continue the prior completed port task by implementing app/host.py with parse_host(value).
For this small test, a valid host is a nonempty string containing a dot with no whitespace; return
it unchanged. 'example.com' is valid and 'bad' is invalid. Use app.errors.ConfigError if an exception
contract applies. Decide how invalid input is reported from the current project criterion in the
packet below. If no current criterion is provided, choose a contract and explain your choice.
Work on H; the prior P implementation is already complete. Read its evidence. Run any required
current-criterion check immediately before the choice and save its actual output to .data/receiver-check.json.
In the card's Progress, add Applied criteria: <ref> or Applied criteria: none. If a prior judgment
is superseded, add Stale judgment: <old ref> superseded. Do not rewrite earlier Progress records.
After H, use Avatar's public CLI to record these synthetic fixtures in the supplied isolated home:
1. choice add: question 'How should invalid host input be reported?', options ['ConfigError','None','other'],
   chosen = the actual implementation's choice, reason_quote = the exact quote from .data/choice-origin.json,
   origin = that object, context.project_key='test/demo-app', context.conditions=[{{"kind":"path","any":["app/"]}}],
   source_refs = refs actually applied, or [] for none. Use an idempotency key starting with {label}.
2. criterion propose: statement={json.dumps(PERSONAL)}, from_choices=[the returned choice ID].
   This is a fixture requested by the test, not an inferred trait of the real user.
3. criterion confirm the proposed ID/version using .data/confirm-personal.json as payload. That fixture
   is explicit confirmation for the exact synthetic statement. Use the returned new ref afterward.
4. If you used a Distill ref, obtain its criteria history JSON and source attach it to Avatar. Then show --json.
Never read the DB directly. Save the final Avatar show JSON to .data/avatar-show.json.
Report tests, the decision and any question that blocked you. Do not claim a general cost improvement.

The actual Stage handoff packet follows:
{packet}
"""
        result = run_host(host, project, output / "model", prompt)
        shutil.copytree(project, output / "project")
        try:
            checked = check_case(output, frozen)
        except Exception as error:
            checked = {"passed": False, "error": str(error)}
        avatar = self.cli(output, "avatar-observation", self.avatar + ["--home", str(project / ".data/avatar"), "show", "--json"], project)
        exported = self.cli(output, "avatar-export", self.avatar + ["--home", str(project / ".data/avatar"), "export"], project)
        avatar_ok = bool(avatar["choices"]) and any(c["statement"] == PERSONAL for c in exported["criteria"])
        checked["avatar_flow"] = avatar_ok
        checked["passed"] = checked["passed"] and avatar_ok
        write_json(output / "file-checks.json", checked)
        run = {"direction": direction, "condition": condition, "real_cli": True, "exit": result["exit"],
               "file_checks_passed": checked["passed"], "case_root": label,
               "sender_raw": str(sender["output"].relative_to(self.out) / "model/stdout.jsonl"),
               "receiver_raw": label + "/model/stdout.jsonl", "file_checks": label + "/file-checks.json",
               "frozen_input": label + "/frozen-input.json", "seconds": result["elapsed_seconds"]}
        write_json(output / "run.json", run)
        print(json.dumps({"phase": label, "passed": checked["passed"], "exit": result["exit"],
                          "seconds": result["elapsed_seconds"]}), flush=True)
        return run

    def execute(self) -> int:
        with ThreadPoolExecutor(max_workers=2) as pool:
            senders = list(pool.map(self.sender, ("claude", "codex")))
        if not all(sender["ok"] for sender in senders):
            write_json(self.out / "blocked.json", {"reason": "A sender failed. No receiver cases were fabricated."})
            return 1
        cases = [(sender, condition) for sender in senders for condition in ("C0", "C1", "C2")]
        runs = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            for result in pool.map(lambda pair: self.receiver(*pair), cases):
                runs.append(result)
                write_json(self.out / "host-runs.json", runs)
        return 0 if all(run["exit"] == 0 and run["file_checks_passed"] for run in runs) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--distill-python", required=True, type=Path)
    parser.add_argument("--avatar-root", required=True, type=Path)
    parser.add_argument("--stage-root", required=True, type=Path)
    parser.add_argument("--source-manifest", type=Path, default=Path(__file__).parent / "evidence/2026-10-06-contract/sources.json")
    return Experiment(parser.parse_args()).execute()


if __name__ == "__main__":
    raise SystemExit(main())
