"""Run a bounded synthetic experiment; never load a personal Avatar store or transcript."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parent
TEXT = {"type": "string", "minLength": 1, "maxLength": 240}
CLAIM = {
    "type": "object", "additionalProperties": False,
    "properties": {"text": TEXT, "evidence_ids": {
        "type": "array", "minItems": 1, "maxItems": 5, "items": {"type": "string"}}},
    "required": ["text", "evidence_ids"],
}
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "owner_id": {"type": "string"}, "language": {"enum": ["ko", "en"]},
        "headline": {**CLAIM, "properties": {**CLAIM["properties"],
                     "text": {"type": "string", "minLength": 1, "maxLength": 70}}},
        "observations": {"type": "array", "minItems": 2, "maxItems": 3, "items": CLAIM},
        "interpretation": CLAIM, "alternative": TEXT, "limitation": TEXT,
    },
    "required": ["owner_id", "language", "headline", "observations", "interpretation",
                 "alternative", "limitation"],
}


def validate(card: Any, bundle: dict[str, Any], language: str) -> list[str]:
    """Check structure and references only; semantic accuracy requires a separate review."""
    errors: list[str] = []
    if not isinstance(card, dict):
        return ["The card is not an object."]
    if card.get("owner_id") != bundle["owner_id"] or card.get("language") != language:
        errors.append("The owner or requested language does not match.")
    observations = card.get("observations")
    if not isinstance(observations, list) or not 2 <= len(observations) <= 3:
        return errors + ["The observation count is invalid."]
    ids = {record["id"] for record in bundle["records"]}
    for claim in [card.get("headline"), *observations, card.get("interpretation")]:
        if not isinstance(claim, dict):
            errors.append("A claim is missing.")
            continue
        value = claim.get("text")
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 240:
            errors.append("A claim has invalid text.")
        refs = claim.get("evidence_ids")
        if (not isinstance(refs, list) or not refs
                or not all(isinstance(ref, str) and ref in ids for ref in refs)):
            errors.append("A claim references another owner or an unknown source.")
    for name in ("alternative", "limitation"):
        value = card.get(name)
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 240:
            errors.append(f"The {name} is invalid.")
    visible = [card.get("alternative"), card.get("limitation")]
    visible += [claim.get("text") for claim in
                [card.get("headline"), *observations, card.get("interpretation")]
                if isinstance(claim, dict)]
    if any(isinstance(value, str) and value.strip().casefold() in
           {"placeholder", "todo", "tbd", "n/a", "..."} for value in visible):
        errors.append("A visible field contains a placeholder instead of a claim.")
    if isinstance(card.get("headline"), dict):
        value = card["headline"].get("text")
        if isinstance(value, str) and len(value) > 70:
            errors.append("The headline is too long.")
    return errors


def run_one(out: Path, bundle: dict[str, Any], language: str, repeat: int,
            system: str) -> bool:
    run_id = f"{bundle['bundle_id']}-{language}-{repeat}"
    folder = out / run_id
    prompt = json.dumps({"requested_language": language, "bundle": bundle}, ensure_ascii=False)
    digest = hashlib.sha256((system + prompt + json.dumps(SCHEMA)).encode()).hexdigest()
    if folder.exists():
        metadata_path = folder / "process.json"
        if not metadata_path.exists():
            raise SystemExit(f"Unfinished evidence exists: {folder}. Inspect it before retrying.")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("input_sha256") != digest:
            raise SystemExit("Input changed. Choose a new batch to preserve previous evidence.")
        if metadata.get("status") != "generated":
            raise SystemExit(f"Previous run failed: {run_id}. Inspect it before retrying.")
        print(f"{run_id}: already generated; semantic review is separate", flush=True)
        return True
    folder.mkdir(parents=True)
    (folder / "input.json").write_text(prompt + "\n", encoding="utf-8")
    (folder / "system.txt").write_text(system, encoding="utf-8")
    (folder / "schema.json").write_text(json.dumps(SCHEMA, indent=2) + "\n", encoding="utf-8")
    args = [
        "claude", "-p", "--model", "sonnet", "--effort", "low", "--safe-mode",
        "--tools", "", "--disable-slash-commands", "--no-session-persistence",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--output-format", "json", "--json-schema", json.dumps(SCHEMA),
        "--system-prompt", system,
    ]
    metadata: dict[str, Any] = {
        "run_id": run_id, "input_sha256": digest, "requested_model": "sonnet",
        "effort": "low", "synthetic_only": True,
        "started_at": datetime.now(timezone.utc).isoformat(), "status": "failed",
        "semantic_review": "pending",
    }
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="avatar-synthetic-") as cwd:
            with (folder / "raw.json").open("w", encoding="utf-8") as stdout:
                with (folder / "stderr.txt").open("w", encoding="utf-8") as stderr:
                    result = subprocess.run(args, input=prompt, text=True, encoding="utf-8",
                                            stdout=stdout, stderr=stderr, cwd=cwd, timeout=120)
        metadata["exit"] = result.returncode
        if result.returncode != 0:
            raise ValueError("Claude returned a nonzero exit status.")
        envelope = json.loads((folder / "raw.json").read_text(encoding="utf-8"))
        metadata["is_error"] = envelope.get("is_error")
        metadata["model_usage"] = envelope.get("modelUsage", {})
        metadata["reported_list_cost_usd"] = envelope.get("total_cost_usd")
        if envelope.get("is_error"):
            raise ValueError("Claude reported an error.")
        card = envelope.get("structured_output")
        if card is None:
            card = json.loads(envelope.get("result", ""))
        errors = validate(card, bundle, language)
        (folder / "card.json").write_text(
            json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        metadata["structural_errors"] = errors
        if errors:
            raise ValueError("Structural checks failed: " + "; ".join(errors))
        metadata["status"] = "generated"
    except (OSError, ValueError, TypeError, AttributeError, subprocess.TimeoutExpired) as error:
        metadata["error"] = str(error)
    finally:
        metadata["seconds"] = round(time.monotonic() - started, 2)
        metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
        (folder / "process.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{run_id}: {metadata['status']} ({metadata['seconds']}s)", flush=True)
    return metadata["status"] == "generated"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--prompt-version", choices=("v1", "v2"), default="v1")
    parser.add_argument("--limit", type=int, default=16, choices=range(1, 17))
    options = parser.parse_args()
    if not options.batch.replace("-", "").isalnum():
        parser.error("The batch name must contain only letters, digits, and hyphens.")
    fixtures = json.loads((ROOT / "profile-fixtures.json").read_text(encoding="utf-8"))
    if fixtures.get("synthetic") is not True:
        raise SystemExit("Only the fixed synthetic fixture is supported.")
    prompt_file = "profile-lab-prompt.txt" if options.prompt_version == "v1" else "profile-lab-prompt-v2.txt"
    system = (ROOT / prompt_file).read_text(encoding="utf-8")
    out = ROOT / "evidence" / options.batch
    count = 0
    for repeat in range(1, 5):
        for language in ("ko", "en"):
            for bundle in fixtures["bundles"]:
                if count >= options.limit:
                    return
                if not run_one(out, bundle, language, repeat, system):
                    raise SystemExit("Stopped after a failed run. Inspect saved evidence.")
                count += 1


if __name__ == "__main__":
    main()
