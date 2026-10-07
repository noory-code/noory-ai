from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path, PureWindowsPath
from typing import Any, Optional, Sequence

from avatar_common import AvatarError
from avatar_projection import validate as validate_projection
from avatar_store import AvatarStore


VERSION = json.loads(
    (Path(__file__).resolve().parents[1] / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
)["version"]
JsonObject = dict[str, Any]


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(
        prog="avatar", description="Review recorded choices and confirmed personal criteria."
    )
    command_parser.add_argument("--home", type=Path)
    commands = command_parser.add_subparsers(dest="command", required=True)

    choice = commands.add_parser("choice")
    choice_commands = choice.add_subparsers(dest="choice_command", required=True)
    choice_add = choice_commands.add_parser("add")
    add_write_arguments(choice_add)

    criterion = commands.add_parser("criterion")
    criterion_commands = criterion.add_subparsers(dest="criterion_command", required=True)
    propose = criterion_commands.add_parser("propose")
    add_write_arguments(propose)
    confirm = criterion_commands.add_parser("confirm")
    confirm.add_argument("id")
    confirm.add_argument("--version", required=True, type=int)
    add_write_arguments(confirm)
    revise = criterion_commands.add_parser("revise")
    revise.add_argument("id")
    add_write_arguments(revise)
    revoke = criterion_commands.add_parser("revoke")
    revoke.add_argument("id")
    add_write_arguments(revoke)

    source = commands.add_parser("source")
    source_commands = source.add_subparsers(dest="source_command", required=True)
    attach = source_commands.add_parser("attach")
    attach.add_argument("--idempotency-key", required=True)
    attach.add_argument("--file", required=True, type=Path)

    show = commands.add_parser("show")
    show.add_argument("--choice")
    show.add_argument("--criterion")
    show.add_argument("--json", action="store_true")

    commands.add_parser("export")
    check = commands.add_parser("check")
    check.add_argument("--refs", required=True)
    return command_parser


def add_write_arguments(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument("--idempotency-key", required=True)
    command_parser.add_argument("--payload-file", required=True, type=Path)


def read_object(path: Path, error_code: str = "E_INPUT_INVALID") -> JsonObject:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        json.dumps(value, ensure_ascii=False).encode("utf-8")
    except (OSError, ValueError) as error:
        raise AvatarError(error_code, f"Cannot read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise AvatarError(error_code, "JSON input must be an object.")
    return value


def require_text(payload: JsonObject, field: str, code: str = "E_INPUT_INVALID") -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise AvatarError(code, f"{field} must be a non-empty string.")
    return value


def validate_origin(origin: object, require_user: bool = True) -> JsonObject:
    if not isinstance(origin, dict):
        raise AvatarError("E_QUOTE_REQUIRED", "A user origin with a quote is required.")
    quote = origin.get("quote")
    source_ref = origin.get("source_ref")
    actor = origin.get("actor")
    recorded_by = origin.get("recorded_by")
    if not isinstance(quote, str) or not quote.strip() or len(quote) > 2000:
        raise AvatarError("E_QUOTE_REQUIRED", "A non-empty quote of at most 2000 characters is required.")
    if not isinstance(source_ref, str) or not source_ref.strip():
        raise AvatarError("E_QUOTE_REQUIRED", "The quote source_ref is required.")
    if require_user and actor != "user":
        raise AvatarError("E_QUOTE_REQUIRED", "The confirming origin actor must be user.")
    if actor not in ("user", "ai") or not isinstance(recorded_by, dict):
        raise AvatarError("E_QUOTE_REQUIRED", "The origin actor and recorded_by fields are required.")
    if origin.get("kind") not in ("user_statement", "stage_card", "stage_decision"):
        raise AvatarError("E_QUOTE_REQUIRED", "The origin kind is invalid.")
    expected = hashlib.sha256(quote.encode("utf-8")).hexdigest()
    if origin.get("quote_sha256") not in (None, expected):
        raise AvatarError("E_QUOTE_REQUIRED", "quote_sha256 does not match the quote.")
    for field in ("host", "session_id", "via"):
        if not isinstance(recorded_by.get(field), str) or not recorded_by[field].strip():
            raise AvatarError("E_QUOTE_REQUIRED", f"origin.recorded_by.{field} is required.")
    return origin


def validate_conditions(value: object) -> list[JsonObject]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise AvatarError("E_INVALID_CONDITION", "Conditions must be a list.")
    result: list[JsonObject] = []
    for condition in value:
        if not isinstance(condition, dict) or condition.get("kind") not in ("path", "work_kind"):
            raise AvatarError("E_INVALID_CONDITION", "Condition kind must be path or work_kind.")
        alternatives = condition.get("any")
        if (
            not isinstance(alternatives, list)
            or not alternatives
            or not all(isinstance(item, str) and item.strip() for item in alternatives)
        ):
            raise AvatarError("E_INVALID_CONDITION", "Condition any must contain strings.")
        if condition["kind"] == "path":
            for path in alternatives:
                parts = path.replace("\\", "/").split("/")
                if (path.startswith(("/", "\\")) or PureWindowsPath(path).drive
                        or ".." in parts or any(mark in path for mark in "*?[")):
                    raise AvatarError("E_INVALID_CONDITION", "Paths must be relative and cannot use globs.")
        result.append(condition)
    return result


def validate_string_list(payload: JsonObject, field: str) -> list[str]:
    value = payload.get(field, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise AvatarError("E_INPUT_INVALID", f"{field} must be a list of strings.")
    return value


def validate_choice(payload: JsonObject) -> None:
    require_text(payload, "question")
    require_text(payload, "chosen")
    require_text(payload, "reason_quote", "E_QUOTE_REQUIRED")
    options = validate_string_list(payload, "options")
    if not options or payload["chosen"] not in options:
        raise AvatarError("E_INPUT_INVALID", "chosen must be one of the options.")
    validate_string_list(payload, "source_refs")
    validate_origin(payload.get("origin"))
    context = payload.get("context")
    if not isinstance(context, dict) or not isinstance(context.get("project_key"), str):
        raise AvatarError("E_INPUT_INVALID", "context.project_key is required.")
    validate_conditions(context.get("conditions", []))


def validate_proposal(payload: JsonObject) -> None:
    require_text(payload, "statement")
    payload["applies_when"] = validate_conditions(payload.get("applies_when", []))
    payload["exceptions"] = validate_conditions(payload.get("exceptions", []))
    validate_string_list(payload, "notes")
    validate_string_list(payload, "overrides")
    validate_string_list(payload, "from_choices")
    if "origin" in payload or payload.get("overrides"):
        validate_origin(payload.get("origin"), require_user=bool(payload.get("overrides")))
    confidence = payload.get("ai_confidence")
    if confidence is not None and (
        not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1
    ):
        raise AvatarError("E_INPUT_INVALID", "ai_confidence must be between 0 and 1.")


def validate_revision(payload: JsonObject) -> None:
    base_version = payload.get("base_version")
    if not isinstance(base_version, int) or isinstance(base_version, bool) or base_version < 1:
        raise AvatarError("E_INPUT_INVALID", "base_version must be a positive integer.")
    require_text(payload, "reason")
    if "statement" in payload:
        require_text(payload, "statement")
    for field in ("applies_when", "exceptions"):
        if field in payload:
            payload[field] = validate_conditions(payload[field])
    for field in ("notes", "overrides"):
        if field in payload:
            validate_string_list(payload, field)
    if "origin" in payload or payload.get("overrides"):
        validate_origin(payload.get("origin"), require_user=bool(payload.get("overrides")))
    confidence = payload.get("ai_confidence")
    if confidence is not None and (
        not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1
    ):
        raise AvatarError("E_INPUT_INVALID", "ai_confidence must be between 0 and 1.")


def validate_revocation(payload: JsonObject) -> None:
    base_version = payload.get("base_version")
    if not isinstance(base_version, int) or isinstance(base_version, bool) or base_version < 1:
        raise AvatarError("E_INPUT_INVALID", "base_version must be a positive integer.")
    require_text(payload, "reason")
    validate_origin(payload.get("origin"))


def home_path(argument: Optional[Path]) -> Path:
    if argument is not None:
        return argument.expanduser()
    configured = os.environ.get("AVATAR_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".avatar"


def human_show(data: JsonObject) -> str:
    lines = ["Avatar local record", ""]
    lines.append(f"Choices: {len(data['choices'])}")
    for choice in data["choices"]:
        lines.append(f"- {choice['id']}: {choice['chosen']} — {choice['reason_quote']}")
        lines.append(f"  Question: {choice['question']}")
        lines.append(f"  Source: {choice['origin']['source_ref']}")
        lines.append(f"  Conditions: {json.dumps(choice['context'], ensure_ascii=False)}")
    lines.append(f"Personal criteria: {len(data['criteria'])}")
    for criterion in data["criteria"]:
        state = "revoked" if criterion["revoked"] else "current"
        lines.append(f"- {criterion['id']} ({state})")
        for version in criterion["versions"]:
            lines.append(
                f"  - {version['ref']}: {version['statement']} [{version['confirmation']}]"
            )
            lines.append(f"    Reason: {version['reason']}")
            if version.get("origin"):
                lines.append(f"    Source: {version['origin']['source_ref']}")
                lines.append(f"    Quote: {version['origin']['quote']}")
        for event in criterion["events"]:
            lines.append(f"  - {event['kind']} at {event['recorded_at']}: {event['reason']}")
            if event.get("origin"):
                lines.append(f"    Source: {event['origin']['source_ref']}")
                lines.append(f"    Quote: {event['origin']['quote']}")
    lines.append(f"Source projections: {len(data['projections'])}")
    for projection in data["projections"]:
        note = "; newer projection exists" if projection["newer_projection_exists"] else ""
        lines.append(
            f"- {projection['producer']} generation {projection['generation']} fetched at "
            f"{projection['fetched_at']}; current status unverified{note}"
        )
        for version in projection["history"]["versions"]:
            lines.append(f"  - {version['ref']}: {version.get('statement', '')}")
            lines.append(f"    Reason: {version.get('reason', '')}")
            if version.get("origin"):
                lines.append(f"    Source: {version['origin'].get('source_ref', '')}")
                lines.append(f"    Quote: {version['origin'].get('quote', '')}")
        for event in projection["history"]["events"]:
            lines.append(f"  - {event.get('event', event.get('kind', 'event'))}: {event.get('reason', '')}")
    for candidate in data["review_candidates"]:
        condition_note = " Conditions differ." if candidate["conditions_differ"] else ""
        lines.append(
            f"Review candidate: {' and '.join(candidate['choice_ids'])}.{condition_note}"
        )
    return "\n".join(lines) + "\n"


def execute(arguments: argparse.Namespace) -> tuple[object, bool]:
    store = AvatarStore(home_path(arguments.home))
    if arguments.command == "choice":
        payload = read_object(arguments.payload_file)
        validate_choice(payload)
        return store.add_choice(arguments.idempotency_key, payload), True
    if arguments.command == "criterion":
        payload = read_object(arguments.payload_file)
        if arguments.criterion_command == "propose":
            validate_proposal(payload)
            return store.propose(arguments.idempotency_key, payload), True
        if arguments.criterion_command == "confirm":
            validate_origin(payload.get("origin"))
            if "reason" in payload:
                require_text(payload, "reason")
            return store.confirm(
                arguments.id, arguments.version, arguments.idempotency_key, payload
            ), True
        if arguments.criterion_command == "revise":
            validate_revision(payload)
            return store.revise(arguments.id, arguments.idempotency_key, payload), True
        validate_revocation(payload)
        return store.revoke(arguments.id, arguments.idempotency_key, payload), True
    if arguments.command == "source":
        payload = read_object(arguments.file, "E_SOURCE_INVALID")
        validate_projection(payload)
        return store.attach_projection(arguments.idempotency_key, payload), True
    if arguments.command == "show":
        shown = store.show(arguments.choice, arguments.criterion)
        return (shown, True) if arguments.json else (human_show(shown), False)
    if arguments.command == "export":
        return store.export(VERSION), True
    refs = [ref.strip() for ref in arguments.refs.split(",") if ref.strip()]
    if not refs:
        raise AvatarError("E_INPUT_INVALID", "At least one ref is required.")
    return store.check(refs), True


def main(argv: Optional[Sequence[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        arguments = parser().parse_args(argv)
        result, as_json = execute(arguments)
        if as_json:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print(result, end="")
        return 0
    except AvatarError as error:
        print(json.dumps({"error": error.code, "message": error.message}, ensure_ascii=False))
        return 2
    except (sqlite3.Error, OSError) as error:
        print(
            json.dumps(
                {"error": "E_STORE_UNAVAILABLE", "message": str(error)}, ensure_ascii=False
            )
        )
        return 3


if __name__ == "__main__":
    sys.exit(main())
