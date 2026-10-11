"""Record pre-authorized synthetic fixtures through public CLIs; never decide for the AI."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import time


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object: " + str(path))
    return value


def run_batch(project: Path, chosen: str, refs: list[str]) -> dict:
    project = project.resolve()
    data = (project / ".data").resolve()
    data.relative_to(project)
    config = load(data / "recording-fixture.json")
    choice_origin = load(data / "choice-origin.json")
    confirmation = load(data / "confirm-personal.json")
    statement = config.get("statement")
    confirm_origin = confirmation.get("origin", {})
    if config.get("synthetic_only") is not True or not isinstance(statement, str) or not statement:
        raise ValueError("This command only accepts a declared synthetic fixture.")
    required_quote = "[Synthetic test statement] I confirm this synthetic personal criterion: " + statement
    if confirm_origin.get("actor") != "user" or confirm_origin.get("quote") != required_quote:
        raise ValueError("The supplied fixture must confirm this exact statement before any write.")
    if (choice_origin.get("actor") != "user"
            or not choice_origin.get("quote", "").startswith("[Synthetic test statement] ")):
        raise ValueError("The choice origin must be explicitly synthetic.")
    if chosen not in {"ConfigError", "None", "other"}:
        raise ValueError("The AI must supply one of the fixture's choices.")
    if len(refs) != len(set(refs)) or any(not re.fullmatch(r"distill:CR-[a-f0-9]{12}@[1-9]\d*", ref) for ref in refs):
        raise ValueError("Expected distinct Distill version refs.")
    if refs:
        receipt = load(data / "receiver-check.json")
        eligible = {row.get("ref") for row in receipt.get("results", [])
                    if row.get("status") == "eligible_current"}
        if not set(refs).issubset(eligible):
            raise ValueError("An applied ref lacks an eligible-current receipt from the AI's check.")
    avatar = list(config["avatar_argv"]) + ["--home", str(data / "avatar")]
    distill = list(config["distill_argv"])
    prefix = config["label"] + ":batch"
    sequence = 0

    def invoke(label: str, argv: list[str], payload: dict | None = None) -> dict:
        nonlocal sequence
        sequence += 1
        started = time.monotonic()
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            result = subprocess.run(argv, cwd=project, capture_output=True, text=True,
                                    encoding="utf-8", timeout=30)
        except subprocess.TimeoutExpired as error:
            def partial(value: str | bytes | None) -> str:
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
            result = subprocess.CompletedProcess(argv, 124, partial(error.stdout), partial(error.stderr))
        record = {"label": label, "sequence": sequence, "started_at": timestamp,
                  "seconds": time.monotonic() - started, "argv": argv, "payload": payload,
                  "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        with (data / "batch-calls.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        if result.returncode:
            raise ValueError(f"{label} failed; earlier writes remain recorded: {result.stdout} {result.stderr}")
        response = json.loads(result.stdout)
        (data / f"batch-{label}.json").write_text(result.stdout, encoding="utf-8")
        return response

    def mutation(label: str, command: list[str], payload: dict) -> dict:
        path = data / f"batch-{label}-payload.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return invoke(label, avatar + command + ["--idempotency-key", prefix + ":" + label,
                                                "--payload-file", str(path)], payload)

    choice = mutation("choice", ["choice", "add"], {
        "question": "How should invalid host input be reported?",
        "options": ["ConfigError", "None", "other"], "chosen": chosen,
        "reason_quote": choice_origin["quote"], "origin": choice_origin,
        "context": {"project_key": config["project_key"],
                    "conditions": [{"kind": "path", "any": ["app/"]}]}, "source_refs": refs})
    proposal = mutation("propose", ["criterion", "propose"], {
        "statement": statement, "from_choices": [choice["id"]]})
    version = proposal["ref"].rsplit("@", 1)[1]
    confirmed = mutation("confirm", ["criterion", "confirm", proposal["id"],
                                     "--version", version], confirmation)
    for index, ref in enumerate(refs):
        identifier = ref.split(":", 1)[1].split("@", 1)[0]
        label = f"history-{index}"
        invoke(label, distill + ["history", identifier, "--db", str(data / "distill.db")])
        history_file = data / f"batch-{label}.json"
        invoke(f"attach-{index}", avatar + ["source", "attach", "--idempotency-key",
               prefix + f":attach-{index}", "--file", str(history_file)], load(history_file))
    invoke("show", avatar + ["show", "--json"])
    (data / "avatar-show.json").write_bytes((data / "batch-show.json").read_bytes())
    result = {"choice_id": choice["id"], "confirmed_ref": confirmed["ref"], "applied_refs": refs}
    (data / "batch-result.json").write_text(json.dumps(result), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--chosen", required=True, choices=["ConfigError", "None", "other"])
    parser.add_argument("--refs", required=True, help="Comma-separated applied refs, or none.")
    args = parser.parse_args()
    refs = [] if args.refs == "none" else args.refs.split(",")
    try:
        print(json.dumps(run_batch(args.project_root, args.chosen, refs)))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
