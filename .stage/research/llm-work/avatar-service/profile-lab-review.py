"""Request an independent critique of fixed synthetic inputs and generated cards."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def load_evidence(batch: Path) -> tuple[list[dict], str, list[dict]]:
    """Read the exact saved inputs; reject edits or mixed prompts before another model call."""
    cards: list[dict] = []
    bundles: dict[str, dict] = {}
    systems: set[str] = set()
    for file in sorted(batch.glob("*/card.json")):
        folder = file.parent
        metadata = json.loads((folder / "process.json").read_text(encoding="utf-8"))
        if metadata.get("status") != "generated":
            raise ValueError(f"A failed run needs inspection: {folder.name}")
        raw_input = (folder / "input.json").read_text(encoding="utf-8").removesuffix("\n")
        system = (folder / "system.txt").read_text(encoding="utf-8")
        schema = json.loads((folder / "schema.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256((system + raw_input + json.dumps(schema)).encode()).hexdigest()
        if digest != metadata.get("input_sha256"):
            raise ValueError(f"Saved input digest mismatch: {folder.name}")
        bundle = json.loads(raw_input)["bundle"]
        owner = bundle["owner_id"]
        if owner in bundles and bundles[owner] != bundle:
            raise ValueError(f"Mixed fixtures for owner: {owner}")
        bundles[owner] = bundle
        systems.add(system)
        cards.append({"run_id": folder.name,
                      "card": json.loads(file.read_text(encoding="utf-8"))})
    if len(systems) != 1:
        raise ValueError("Expected one saved prompt per batch.")
    return list(bundles.values()), systems.pop(), cards


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--review", default="review-1")
    args = parser.parse_args()
    for value in (args.batch, args.review):
        if not value.replace("-", "").isalnum():
            parser.error("Names may contain only letters, digits, and hyphens.")
    batch = ROOT / "evidence" / args.batch
    bundles, system, cards = load_evidence(batch)
    if len(cards) != 16:
        raise SystemExit(f"Expected 16 cards, found {len(cards)}. No review requested.")
    out = batch / args.review
    out.mkdir(exist_ok=False)
    prompt = """Independently review this synthetic Avatar experiment. Return JSON, without fences.
You only have supplied material. Do not use tools, private data, or an imagined transcript.
All 16 cards were generated in separate fresh CLI calls, using sonnet at low effort. These examples
were discussed before the prompt was written: this is a development check, NOT a held-out evaluation,
product accuracy estimate, clinical validation, user study, or evidence of repeat usage.
The product should connect contextual clues into useful self-understanding, with readable short text.
Audit EVERY visible field: headline, observations, interpretation, alternative, limitation. Check
owner attribution, cited support, counts, scope, implicit causation, hidden motives/emotion, requests
versus actual behavior, and assistant repairs versus the user's normal style. A tentative alternative
is allowed but must not quietly invent event ordering or an actual missing event. A cautious body
cannot rescue an unqualified headline. A source summary cannot become a verbatim quote. K5 is a story
character, never the owner's tone. J3 and J4 are not known to be independent incidents.
Do not hunt for errors merely to be adversarial. Explain reasonable disagreements. Check Korean for
natural everyday wording, especially literal translations and noun strings. Semantic severity and
wording quality are separate. Do not mark an English card invalid merely because Korean sounds odd.
For each of the 16 run IDs give verdict (acceptable_for_synthetic_demo or revise), exact field paths,
quoted problem text, reasoning tied to source IDs, and short suggested replacements. No problem may
be claimed without quoting the actual output. Return keys: cards (array of per-card objects),
experiment_limits (array), recommendations (array). Write explanations in Korean. Keep replacements
in the original card language. Max 4500 words. No blanket endorsement or unsupported rates.
FIXED INPUTS:
""" + json.dumps(bundles, ensure_ascii=False)
    prompt += "\nGENERATION PROMPT:\n" + system
    prompt += "\nOUTPUTS:\n" + json.dumps(cards, ensure_ascii=False)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    command = [
        "claude", "-p", "--model", "opus", "--effort", "high", "--safe-mode",
        "--tools", "", "--disable-slash-commands", "--no-session-persistence",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--output-format", "json", "--system-prompt",
        "You independently check supplied synthetic evidence. Do not treat model agreement as proof.",
    ]
    metadata = {"started_at": datetime.now(timezone.utc).isoformat(), "status": "failed"}
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="avatar-lab-review-") as cwd:
            with (out / "raw.json").open("w", encoding="utf-8") as stdout:
                with (out / "stderr.txt").open("w", encoding="utf-8") as stderr:
                    completed = subprocess.run(command, input=prompt, text=True, encoding="utf-8",
                                               stdout=stdout, stderr=stderr, cwd=cwd, timeout=240)
        metadata["exit"] = completed.returncode
        if completed.returncode != 0:
            raise ValueError("Claude returned a nonzero exit status.")
        envelope = json.loads((out / "raw.json").read_text(encoding="utf-8"))
        metadata["is_error"] = envelope.get("is_error")
        metadata["model_usage"] = envelope.get("modelUsage", {})
        metadata["reported_list_cost_usd"] = envelope.get("total_cost_usd")
        if envelope.get("is_error") or not isinstance(envelope.get("result"), str):
            raise ValueError("Claude did not return a review.")
        body = envelope["result"]
        (out / "response.txt").write_text(body + "\n", encoding="utf-8")
        if body.startswith("```json\n") and body.rstrip().endswith("```"):
            body = body.removeprefix("```json\n").rstrip().removesuffix("```")
        result = json.loads(body)
        if not isinstance(result, dict) or not isinstance(result.get("cards"), list):
            raise ValueError("Review structure is incomplete.")
        requested = {card["run_id"] for card in cards}
        received = [card.get("run_id") for card in result["cards"] if isinstance(card, dict)]
        if len(received) != 16 or set(received) != requested:
            raise ValueError("Review does not cover each requested run exactly once.")
        (out / "review.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        metadata["status"] = "review_returned"
    except (OSError, ValueError, TypeError, AttributeError, subprocess.TimeoutExpired) as error:
        metadata["error"] = str(error)
    finally:
        metadata["seconds"] = round(time.monotonic() - started, 2)
        metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
        (out / "process.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False), flush=True)
    if metadata["status"] != "review_returned":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
