"""Fetch current criteria through public CLI arguments, without a shell."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

from handoff_sources import PacketError


def validate_config(config: object) -> dict:
    if not isinstance(config, dict) or set(config) - {"distill", "avatar"}:
        raise PacketError("E_PRODUCERS_INVALID: expected distill and/or avatar settings")
    for name, item in config.items():
        if not isinstance(item, dict):
            raise PacketError("E_PRODUCERS_INVALID: each producer must be an object")
        argv = item.get("argv")
        if (not isinstance(argv, list) or not argv
                or not all(isinstance(arg, str) and arg and "\0" not in arg for arg in argv)
                or not Path(argv[0]).is_absolute()):
            raise PacketError("E_PRODUCERS_INVALID: argv must start with an absolute executable")
        location = "db" if name == "distill" else "home"
        if location in item and (not isinstance(item[location], str) or not item[location].strip()):
            raise PacketError(f"E_PRODUCERS_INVALID: {location} must be a non-empty path")
    return config


def command(name: str, config: dict, project: str, refs: list[str] | None = None) -> list[str]:
    argv = list(config["argv"])
    if name == "distill":
        argv += ["criteria", "current" if refs is None else "check", "--project", project]
        if refs is not None:
            argv += ["--refs", ",".join(refs)]
        if "db" in config:
            argv += ["--db", config["db"]]
    else:
        if "home" in config:
            argv += ["--home", config["home"]]
        argv += ["export"] if refs is None else ["check", "--refs", ",".join(refs)]
    return argv


def invoke(argv: list[str], root: Path) -> dict:
    result = subprocess.run(argv, cwd=root, capture_output=True, text=True, encoding="utf-8",
                            shell=False, timeout=30)
    if result.returncode:
        raise ValueError(f"producer exited {result.returncode}")
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise ValueError("producer returned a non-object")
    return data


def snapshot(name: str, config: dict, project: str, root: Path) -> dict:
    try:
        data = invoke(command(name, config, project), root)
        if data.get("schema") != "criteria-snapshot/1" or data.get("producer") != name:
            raise ValueError("unknown snapshot schema or producer")
        expected = {"kind": "project", "key": project} if name == "distill" else {"kind": "personal", "key": "personal"}
        if data.get("scope") != expected:
            raise PacketError("E_SCOPE_MISMATCH: snapshot belongs to another scope")
        if (not isinstance(data.get("generation"), int) or isinstance(data["generation"], bool)
                or data["generation"] < 0 or not isinstance(data.get("checked_at"), str)
                or not isinstance(data.get("criteria"), list) or not isinstance(data.get("retired"), list)):
            raise ValueError("incomplete snapshot metadata")
        ids = set()
        for item in data["criteria"]:
            prefix = "CR" if name == "distill" else "PC"
            match = re.fullmatch(rf"{name}:({prefix}-[0-9a-f]{{12}})@([1-9][0-9]*)", item.get("ref", ""))
            if match is None:
                raise ValueError("invalid criterion ref")
            if match.group(1) in ids:
                raise PacketError("E_VERSION_CONFLICT: multiple current versions of one criterion")
            ids.add(match.group(1))
            if not isinstance(item.get("origin"), dict) or not isinstance(item.get("statement"), str):
                raise ValueError("criterion has no statement or source")
            allowed = "user_stated" if name == "distill" else "user_confirmed"
            if item.get("confirmation") != allowed or item["origin"].get("actor") != "user":
                raise ValueError("snapshot contains an unconfirmed criterion")
        return data
    except PacketError:
        raise
    except (OSError, ValueError, TypeError, AttributeError, UnicodeError, subprocess.TimeoutExpired) as error:
        return {"error": str(error)}


def check_refs(name: str, config: dict, project: str, root: Path, refs: list[str]) -> dict:
    try:
        data = invoke(command(name, config, project, refs), root)
        statuses = {item["ref"]: item["status"] for item in data["results"]}
        return {ref: statuses.get(ref, "unknown") for ref in refs}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, subprocess.TimeoutExpired):
        return {ref: "unknown (producer check failed)" for ref in refs}
