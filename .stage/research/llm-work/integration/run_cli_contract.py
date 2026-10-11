"""Exercise the three public CLIs against synthetic, isolated records."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distill-python", required=True, type=Path)
    parser.add_argument("--distill-root", required=True, type=Path)
    parser.add_argument("--avatar-root", required=True, type=Path)
    parser.add_argument("--stage-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    project = out / "synthetic project"
    project.mkdir()
    db = out / "distill.db"
    avatar_home = out / "avatar data"
    distill = [str(args.distill_python.absolute()), "-m", "distill", "criteria"]
    avatar = [sys.executable, str(args.avatar_root.resolve() / "scripts/avatar.py"), "--home", str(avatar_home)]
    stage = [sys.executable, str(args.stage_root.resolve() / "scripts/handoff_packet.py"),
             "--project-root", str(project), "W-00000002", "--project-key", "test/demo-app"]
    calls = []

    def run(label: str, argv: list[str], as_json: bool = True):
        started = time.monotonic()
        result = subprocess.run(argv, cwd=project, capture_output=True, text=True, encoding="utf-8", timeout=30)
        record = {"label": label, "argv": argv, "exit": result.returncode,
                  "elapsed_seconds": time.monotonic() - started,
                  "stdout": result.stdout, "stderr": result.stderr}
        calls.append(record)
        (out / "calls.json").write_text(json.dumps(calls, ensure_ascii=False, indent=2))
        if result.returncode:
            raise RuntimeError(f"{label} exited {result.returncode}: {result.stderr} {result.stdout}")
        return json.loads(result.stdout) if as_json else result.stdout

    def payload(label: str, value: dict) -> str:
        path = out / f"{label}.json"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2))
        return str(path)

    def origin(message: str, actor: str = "user") -> dict:
        return {"kind": "user_statement", "source_ref": "session:fixture/contract/" + message,
                "quote": "Synthetic test statement: " + message, "actor": actor,
                "recorded_by": {"host": "fixture", "session_id": "contract", "via": "cli"}}

    roots = {"distill": args.distill_root.resolve(), "avatar": args.avatar_root.resolve(),
             "stage": args.stage_root.resolve()}
    sources = {}
    for name, root in roots.items():
        relative_paths = (root / "src").rglob("*.py") if name == "distill" else (root / "scripts").glob("*.py")
        for path in relative_paths:
            sources[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / "sources.json").write_text(json.dumps(sources, indent=2))
    record = {"project": "test/demo-app", "statement": "Invalid input raises ConfigError.",
              "applies_when": [{"kind": "path", "any": ["app/"]}], "exceptions": [], "notes": [],
              "overrides": [], "confirmation": "user_stated", "origin": origin("v1")}
    first_args = [*distill, "record", "--db", str(db), "--idempotency-key", "fixture:1",
                  "--payload-file", payload("criterion-v1", record)]
    first = run("record-v1", first_args)
    replay = run("replay-v1", first_args)
    assert replay == {**first, "replayed": True}
    identifier = first["ref"].split(":", 1)[1].split("@", 1)[0]
    work = project / ".stage/work/current/W-00000001"
    work.mkdir(parents=True)
    (work / "_epic.md").write_text("---\nid: W-00000001\nkind: planning\n---\n## Purpose\nMake parsing predictable.\n")
    child = work / "W-00000002"
    child.mkdir()
    card = child / "_story.md"
    source = project / "app/port.py"
    source.parent.mkdir()
    source.write_text("# Synthetic prior result\ndef parse_port(value):\n    return int(value)\n")
    evidence = {"kind": "file", "path": "app/port.py", "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "observed_at": "2026-10-06T00:00:00Z"}
    card.write_text("---\nid: W-00000002\nkind: development\nscope: app/\n---\n"
                    "## Purpose\nContinue with host parsing.\n## Progress\nApplied criteria: " + first["ref"]
                    + "\nEvidence: " + json.dumps(evidence) + "\n## Success criteria\n- Parse valid hosts.\n"
                    "## Next action\nImplement parse_host.\n")
    producers = payload("producers", {"distill": {"argv": distill[:-1], "db": str(db)},
                                     "avatar": {"argv": avatar[:-2], "home": str(avatar_home)}})
    packet_v1 = run("packet-v1", [*stage, "--producers", producers], False)
    assert first["ref"] in packet_v1 and "### applies" in packet_v1
    before_history = run("history-v1", [*distill, "history", identifier, "--db", str(db)])
    revision = {"base_version": 1, "statement": "Invalid input returns None.",
                "origin": origin("v2"), "reason": "Synthetic change: callers handle absence."}
    second = run("revise-v2", [*distill, "revise", identifier, "--db", str(db),
                 "--idempotency-key", "fixture:2", "--payload-file", payload("revision-v2", revision)])
    packet_v2 = run("packet-v2", [*stage, "--producers", producers], False)
    assert "Invalid input raises ConfigError." not in packet_v2
    assert second["ref"] in packet_v2 and "superseded" in packet_v2
    for line in packet_v2.splitlines():
        if line.startswith("distill: ["):
            checked = run("packet-check", json.loads(line.split(": ", 1)[1]))
            assert checked["results"][0]["status"] == "eligible_current"
    unconfirmed = {**record, "statement": "A synthetic AI guess.", "confirmation": "none",
                   "ai_confidence": 0.99, "origin": origin("ai-guess", "ai")}
    guess = run("record-unconfirmed", [*distill, "record", "--db", str(db), "--idempotency-key", "fixture:3",
                "--payload-file", payload("unconfirmed", unconfirmed)])
    foreign = run("record-other-project", [*distill, "record", "--db", str(db), "--idempotency-key", "fixture:4",
                  "--payload-file", payload("foreign", {**record, "project": "test/other"})])
    check = run("check-exclusions", [*distill, "check", "--db", str(db), "--project", "test/demo-app",
                "--refs", ",".join([guess["ref"], foreign["ref"]])])
    assert [r["status"] for r in check["results"]] == ["unconfirmed", "scope_mismatch"]
    personal = run("avatar-propose", [*avatar, "criterion", "propose", "--idempotency-key", "fixture:5",
                   "--payload-file", payload("personal", {"statement": "Prefer explicit error contracts.", "from_choices": []})])
    assert run("avatar-proposed-export", [*avatar, "export"])["criteria"] == []
    confirmed = run("avatar-confirm", [*avatar, "criterion", "confirm", personal["id"], "--version", "1",
                    "--idempotency-key", "fixture:6", "--payload-file", payload("confirmation", {"origin": origin("personal-confirm")})])
    assert confirmed["ref"].endswith("@2")
    assert [c["ref"] for c in run("avatar-confirmed-export", [*avatar, "export"])["criteria"]] == [confirmed["ref"]]
    for key, criterion_id in (("own", identifier), ("foreign", foreign["ref"].split(":")[1].split("@")[0])):
        history = run(f"history-{key}", [*distill, "history", criterion_id, "--db", str(db)])
        run(f"attach-{key}", [*avatar, "source", "attach", "--idempotency-key", "attach:" + key,
                             "--file", payload("history-" + key, history)])
    run("revoke-v2", [*distill, "revoke", identifier, "--db", str(db), "--idempotency-key", "fixture:7",
                      "--payload-file", payload("revocation", {"base_version": 2, "origin": origin("revoke"), "reason": "Synthetic retirement."})])
    revoked = run("check-revoked", [*distill, "check", "--db", str(db), "--project", "test/demo-app",
                                    "--refs", second["ref"]])
    assert revoked["results"][0]["status"] == "revoked"
    revoked_history = run("history-revoked", [*distill, "history", identifier, "--db", str(db)])
    run("attach-revoked", [*avatar, "source", "attach", "--idempotency-key", "attach:revoked",
                           "--file", payload("history-revoked", revoked_history)])
    older = run("attach-older", [*avatar, "source", "attach", "--idempotency-key", "attach:older",
                                 "--file", payload("history-older", before_history)])
    assert older["newer_projection_exists"]
    shown = run("avatar-show", [*avatar, "show", "--json"])
    assert len(shown["projections"]) == 4
    combined = run("packet-with-avatar", [*stage, "--producers", producers], False)
    assert confirmed["ref"] in combined and first["ref"] + ": superseded" in combined
    assert "Invalid input returns None." not in combined
    source.write_text("changed after evidence")
    changed = run("packet-changed", stage, False)
    assert '"status": "changed"' in changed and "Criteria were not queried" in changed
    source.unlink()
    missing = run("packet-missing", stage, False)
    assert '"status": "missing"' in missing
    report = {"schema": "criteria-cli-contract/1", "passed": True, "call_count": len(calls),
              "real_hosts": [], "limitations": ["No real AI handoff or cost comparison in this run."]}
    (out / "result.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
