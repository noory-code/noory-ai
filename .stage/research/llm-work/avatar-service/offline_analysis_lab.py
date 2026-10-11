"""Test one installed local model on authored fictional conversation cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any
from urllib.request import ProxyHandler, Request, build_opener


ROOT = Path(__file__).resolve().parent
FIXTURES = {
    "v1": ROOT / "offline-analysis-fixtures.json",
    "v2": ROOT / "offline-analysis-fixtures-v2.json",
}
API = "http://127.0.0.1:11434/api/chat"
KINDS = (
    "task_constraint", "assistant_constraint_miss", "user_correction",
    "evidence_request", "unverified_outcome", "reported_third_party_requirement",
    "reported_ai_claim", "task_format_request",
)
SCHEMA = {
    "type": "object",
    "properties": {
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": list(KINDS)},
                    "evidence_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["kind", "evidence_ids"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["observations"],
    "additionalProperties": False,
}
SYSTEM = """Read only the fictional messages provided. Return observable interaction events.
Do not infer stable personality, motive, emotion, a verified test, or a personal rule.
Use only the listed kinds and message IDs. Return no prose. Empty observations is valid.
task_constraint: a user's constraint for this task, not a lifelong preference.
assistant_constraint_miss: assistant explicitly contradicts a prior user constraint.
user_correction: user explicitly corrects the assistant after a mistake.
evidence_request: user asks for a test result, source, or other evidence.
unverified_outcome: the user asks for verification but the assistant gives only an impression.
reported_third_party_requirement: user reports another person's requirement.
reported_ai_claim: user reports a claim that AI made; do not adopt it as fact.
task_format_request: user asks for a length or style for this response only.
For a relation between messages, include every message ID needed to support it.
Do not label a quoted claim as the user's own belief. A question alone proves none of these.
"""
SYSTEM_V2 = """Read only the fictional messages provided. Return every supported
interaction observation. One message can support two different kinds. Do not infer a
stable trait, feeling, motive, verified outcome, or personal rule. Return only the
listed kinds and source IDs; no prose. Empty observations is valid.

task_constraint: a user states a content or feature constraint for this task.
Do not use it for response length or writing style.
task_format_request: a user requests a length or style for this answer only.
assistant_constraint_miss: assistant explicitly contradicts an earlier user constraint.
Include BOTH the earlier user message ID and the assistant message ID.
user_correction: user explicitly corrects an assistant error. Include the correcting user ID.
evidence_request: user asks for test results, sources, or original wording. If the
request occurs twice, return two observations.
unverified_outcome: user asks for verification and assistant gives only an impression.
Include BOTH the request ID and the assistant response ID. Do not invent a later result.
reported_third_party_requirement: user reports another person's requirement.
reported_ai_claim: user reports a claim made by AI. Do not treat it as the user's claim.

For a message that both reports someone else's words and requests an action, return
both observations. A quoted instruction is never a standing personal rule.
"""


def load_cases(version: str) -> list[dict[str, Any]]:
    payload = json.loads(FIXTURES[version].read_text(encoding="utf-8"))
    expected_format = "avatar-offline-analysis-lab/" + version.removeprefix("v")
    if payload.get("format") != expected_format:
        raise ValueError("Unexpected fictional fixture format")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise ValueError("Expected six fictional cases")
    for case in cases:
        if set(case) != {
            "id", "messages", "required_kinds", "required_ids", "forbidden_kinds"
        }:
            raise ValueError("Unexpected case fields")
        if not re.fullmatch(r"[A-F]", case["id"]):
            raise ValueError("Unexpected case ID")
        messages = case["messages"]
        if not isinstance(messages, list) or not 1 <= len(messages) <= 5:
            raise ValueError("Unexpected message list")
        ids = [message["id"] for message in messages]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate message ID")
        for message in messages:
            if set(message) != {"id", "role", "text"}:
                raise ValueError("Unexpected message fields")
            if message["role"] not in {"user", "assistant"}:
                raise ValueError("Unexpected speaker")
            if not isinstance(message["text"], str) or len(message["text"]) > 1000:
                raise ValueError("Unexpected message text")
    return cases


def validate_reply(response: object, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
    if not isinstance(response, dict) or set(response) != {"observations"}:
        raise ValueError("Unexpected response fields")
    observations = response["observations"]
    if not isinstance(observations, list) or len(observations) > 12:
        raise ValueError("Unexpected observation list")
    roles = {message["id"]: message["role"] for message in messages}
    for observation in observations:
        if not isinstance(observation, dict) or set(observation) != {"kind", "evidence_ids"}:
            raise ValueError("Unexpected observation fields")
        kind = observation["kind"]
        ids = observation["evidence_ids"]
        if kind not in KINDS or not isinstance(ids, list) or not 1 <= len(ids) <= 5:
            raise ValueError("Unexpected kind or evidence IDs")
        if any(not isinstance(item, str) or item not in roles for item in ids):
            raise ValueError("Unknown evidence ID")
        if len(ids) != len(set(ids)):
            raise ValueError("Repeated evidence ID")
        selected_roles = {roles[item] for item in ids}
        if kind in {"assistant_constraint_miss", "unverified_outcome"}:
            if selected_roles != {"user", "assistant"}:
                raise ValueError("Relational observation needs both speakers")
        elif "user" not in selected_roles:
            raise ValueError("User action needs a user message")
    return observations


def assess(case: dict[str, Any], observations: list[dict[str, Any]]) -> dict[str, Any]:
    found = {item["kind"] for item in observations}
    evidence = {kind: set() for kind in KINDS}
    for item in observations:
        evidence[item["kind"]].update(item["evidence_ids"])
    missing = sorted(set(case["required_kinds"]) - found)
    forbidden = sorted(set(case["forbidden_kinds"]) & found)
    missing_ids = {
        kind: sorted(set(ids) - evidence[kind])
        for kind, ids in case["required_ids"].items()
        if set(ids) - evidence[kind]
    }
    return {"missing_kinds": missing, "forbidden_kinds": forbidden,
            "missing_evidence_ids": missing_ids}


def run_case(case: dict[str, Any], prompt_version: str) -> dict[str, Any]:
    request_body = {
        "model": "gemma4:latest",
        "messages": [
            {"role": "system", "content": SYSTEM if prompt_version == "v1" else SYSTEM_V2},
            {"role": "user", "content": json.dumps(case["messages"], ensure_ascii=False)},
        ],
        "stream": False,
        "format": SCHEMA,
        "options": {"temperature": 0},
        "keep_alive": "5m",
    }
    request = Request(API, data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    opener = build_opener(ProxyHandler({}))
    with opener.open(request, timeout=180) as reply:
        envelope = json.load(reply)
    answer = envelope.get("message", {}).get("content")
    if not isinstance(answer, str):
        raise ValueError("Local model returned no text")
    result = {"case": case["id"], "raw_response": answer,
            "model": envelope.get("model"),
            "total_duration_ns": envelope.get("total_duration"),
            "prompt_eval_count": envelope.get("prompt_eval_count"),
            "eval_count": envelope.get("eval_count"),
            "done": envelope.get("done")}
    try:
        parsed = json.loads(answer)
        observations = validate_reply(parsed, case["messages"])
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        result["validation_error"] = str(error)
    else:
        result["observations"] = observations
        result["assessment"] = assess(case, observations)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-name", required=True)
    parser.add_argument("--case", choices=list("ABCDEF"))
    parser.add_argument("--version", choices=["v1", "v2"], default="v1")
    options = parser.parse_args()
    if not re.fullmatch(r"2026-10-09-offline-v[1-9][0-9]*", options.output_name):
        raise SystemExit("Use a new, dated offline research output name")
    output = ROOT / "evidence" / options.output_name
    cases = load_cases(options.version)
    if options.case:
        cases = [case for case in cases if case["id"] == options.case]
    output.mkdir(parents=True, exist_ok=False)
    for case in cases:
        try:
            result = run_case(case, options.version)
        except Exception as error:
            result = {"case": case["id"], "error": type(error).__name__, "detail": str(error)}
        (output / f"{case['id']}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(case["id"] + ": " + json.dumps(result.get("assessment", result.get(
            "validation_error", result)),
                                             ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
