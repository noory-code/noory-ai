"""Test explicit comparison targets using fixed synthetic records only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Any

from split_profile_lab import (
    COMMON, MODES, ROOT, SPLIT_SCHEMA, encoded, fingerprint, preserve_records, validate_split,
)

TARGETS = {"requested_answer", "user_wording", "requested_action", "none"}
PROPERTIES = {
    "owner_id": {"type": "string"}, "language": {"enum": ["ko"]},
    "status": {"enum": ["compare", "insufficient"]}, "target": {"enum": sorted(TARGETS)},
    "relation": {"enum": ["same", "different", "none"]},
    "evidence_ids": {"type": "array", "maxItems": 2, "items": {"type": "string"}},
    "question": {"type": "string", "maxLength": 180},
}
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": PROPERTIES, "required": list(PROPERTIES)}
SHARED = """If there is insufficient direct user evidence to connect two records, do not force a
portrait. State that there is not enough evidence. Quoted speakers and unknown authors do not
establish the user's own style or requests. A user's message can itself contain someone else's
quotation: speaker=user does not make every quoted phrase the user's view or wording.
"""
TYPED = """Return a structured comparison, not a narrative interpretation.
Choose two distinct direct user records and one target: requested_answer (what answers the user asks
the AI to produce), user_wording (how the user actually speaks), or requested_action (what the user
asks the AI to do or not do). Mark whether this target is same or different in the selected records.
Do not turn a request into a completed action, a prohibition into a delay, or an output-length
request into the user's own verbosity. The application will show the COMPLETE original text and
context for the two selected IDs; do not copy or paraphrase it. Ask one short, optional question
about an external condition that could clarify this particular comparison. Do not presume hidden
feelings or motives. A question must not assert the conclusion it is meant to test.
If a useful comparison is unsupported, use status=insufficient, target=none, relation=none,
evidence_ids=[] and question="". Otherwise status=compare, with exactly two evidence IDs, a target
other than none, relation=same or different, and a question. Use polite Korean for the question.
"""


def validate_typed(card: Any, bundle: dict[str, Any]) -> list[str]:
    records = preserve_records(bundle)
    if not isinstance(card, dict) or set(card) != set(PROPERTIES):
        return ["Unexpected or missing fields."]
    errors: list[str] = []
    if card["owner_id"] != bundle["owner_id"] or card["language"] != "ko":
        errors.append("Owner or language mismatch.")
    question = card["question"]
    if not isinstance(question, str) or len(question) > 180:
        errors.append("Invalid question.")
    if card["status"] == "insufficient":
        if (card["target"] != "none" or card["relation"] != "none"
                or card["evidence_ids"] != [] or question != ""):
            errors.append("Abstention cannot contain a comparison or a leading question.")
        return errors
    if (card["status"] != "compare" or card["target"] not in TARGETS - {"none"}
            or card["relation"] not in {"same", "different"}):
        errors.append("Invalid comparison target or relation.")
    if isinstance(question, str) and not question.strip():
        errors.append("A comparison needs a question.")
    refs = card["evidence_ids"]
    if (not isinstance(refs, list) or len(refs) != 2
            or any(not isinstance(ref, str) for ref in refs)):
        return errors + ["A comparison needs exactly two source IDs."]
    if len(set(refs)) != 2:
        errors.append("A comparison cannot repeat one record.")
    by_id = {record["id"]: record for record in records}
    for ref in refs:
        if ref not in by_id or by_id[ref]["speaker"] != "user":
            errors.append("A source is missing or is not a direct user record.")
    return errors


def render_typed(card: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """Preserve source text; this renderer does not validate the model's interpretation."""
    errors = validate_typed(card, bundle)
    if errors:
        raise ValueError("; ".join(errors))
    by_id = {record["id"]: record for record in preserve_records(bundle)}
    labels = {"requested_answer": "AI에게 요청한 답", "user_wording": "사용자가 실제로 쓴 말",
              "requested_action": "AI에게 요청한 행동", "none": "비교할 근거가 부족해요"}
    return {"target_label": labels[card["target"]],
            "model_selection": {"same": "모델은 두 기록을 같게 읽었어요",
                                "different": "모델은 두 기록을 다르게 읽었어요",
                                "none": "판단을 보류했어요"}[card["relation"]],
            "records": [by_id[ref] for ref in card["evidence_ids"]],
            "question": card["question"], "confirmed_personal_rule": False}


def run_one(out: Path, bundle: dict[str, Any], mode: str, repeat: int, phase: str) -> bool:
    records = preserve_records(bundle)
    schema = SCHEMA if mode == "typed" else SPLIT_SCHEMA
    system = COMMON + SHARED + (TYPED if mode == "typed" else MODES["split"])
    source = {"requested_language": "ko", "bundle": bundle}
    digest = fingerprint({"input": source, "system": system, "schema": schema})
    run_id = f"{bundle['bundle_id']}-{mode}-{repeat}"
    folder = out / run_id
    # A batch is run once; explicit new evidence is required after any interruption.
    folder.mkdir()
    for name, value in (("input.json", source), ("schema.json", schema)):
        (folder / name).write_text(encoded(value), encoding="utf-8")
    (folder / "system.txt").write_text(system, encoding="utf-8")
    metadata: dict[str, Any] = {
        "run_id": run_id, "mode": mode, "phase": phase, "input_sha256": digest,
        "status": "failed", "semantic_review": "pending", "synthetic_only": True,
        "requested_model": "sonnet", "effort": "low",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    args = ["claude", "-p", "--model", "sonnet", "--effort", "low", "--safe-mode",
            "--tools", "", "--disable-slash-commands", "--no-session-persistence",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--output-format", "json", "--json-schema", json.dumps(schema),
            "--system-prompt", system]
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="avatar-comparison-") as cwd:
            with (folder / "raw.json").open("w", encoding="utf-8") as stdout:
                with (folder / "stderr.txt").open("w", encoding="utf-8") as stderr:
                    result = subprocess.run(args, input=encoded(source), text=True,
                                            stdout=stdout, stderr=stderr, cwd=cwd, timeout=120)
        metadata["exit"] = result.returncode
        if result.returncode != 0:
            raise ValueError("Claude returned a nonzero exit status.")
        envelope = json.loads((folder / "raw.json").read_text())
        metadata["model_usage"] = envelope.get("modelUsage", {})
        metadata["reported_list_cost_usd"] = envelope.get("total_cost_usd")
        metadata["num_turns"] = envelope.get("num_turns")
        if envelope.get("is_error"):
            raise ValueError("Claude reported an error.")
        card = envelope.get("structured_output")
        if card is None:
            card = json.loads(envelope.get("result", ""))
        (folder / "card.json").write_text(encoded(card), encoding="utf-8")
        errors = validate_typed(card, bundle) if mode == "typed" else validate_split(card, bundle)
        metadata["validation_errors"] = errors
        metadata["status"] = "rejected" if errors else "accepted_structure"
        if not errors:
            display = (render_typed(card, bundle) if mode == "typed"
                       else {"records": records, "generated": card})
            (folder / "display.json").write_text(encoded(display), encoding="utf-8")
    except (OSError, ValueError, TypeError, AttributeError, subprocess.TimeoutExpired) as error:
        metadata["error"] = str(error)
    finally:
        metadata["seconds"] = round(time.monotonic() - started, 2)
        metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
        (folder / "process.json").write_text(encoded(metadata), encoding="utf-8")
    print(f"{run_id}: {metadata['status']} ({metadata['seconds']}s)", flush=True)
    return metadata["status"] != "failed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    options = parser.parse_args()
    if not options.batch.replace("-", "").isalnum():
        parser.error("Invalid batch name.")
    development = json.loads((ROOT / "split-fixtures.json").read_text())
    fresh = json.loads((ROOT / "comparison-fixtures.json").read_text())
    if any(data.get("synthetic") is not True for data in (development, fresh)):
        raise SystemExit("Only fixed synthetic fixtures are supported.")
    jobs = [(bundle, "typed", repeat, "development") for repeat in (1, 2)
            for bundle in development["bundles"] if bundle["bundle_id"] in {"M", "P"}]
    for index, bundle in enumerate(fresh["bundles"]):
        for mode in (("free", "typed") if index % 2 == 0 else ("typed", "free")):
            jobs.append((bundle, mode, 1, "fresh"))
    out = ROOT / "evidence" / options.batch
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "plan": (ROOT / "comparison-lab-plan.md").read_text(),
        "jobs": [{"bundle": bundle, "mode": mode, "repeat": repeat, "phase": phase}
                 for bundle, mode, repeat, phase in jobs],
        "sources": {name: (ROOT / name).read_text() for name in
                    ("comparison_lab.py", "split_profile_lab.py", "synthetic_profile_lab.py")},
    }
    (out / "preregistered.json").write_text(encoded(manifest), encoding="utf-8")
    for job in jobs:
        if not run_one(out, *job):
            raise SystemExit("Stopped after a tool or parsing failure; inspect saved evidence.")


if __name__ == "__main__":
    main()
