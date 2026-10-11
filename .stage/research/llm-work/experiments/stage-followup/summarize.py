"""실제 CLI 인계와 기준 적용 시험의 결과를 원본과 대조합니다."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate(rows: list[dict]) -> list[dict]:
    groups = []
    for host, condition in sorted({(row["host"], row["condition"]) for row in rows}):
        values = [row for row in rows if (row["host"], row["condition"]) == (host, condition)]
        groups.append({"host": host, "condition": condition, "calls": len(values),
                       "matches": sum(row.get("matches", False) for row in values) if "matches" in values[0] else None,
                       "actions": dict(Counter((row["answer"] or {}).get("action") for row in values)),
                       **{key: sum(row["usage"][key] or 0 for row in values)
                          for key in ("input_tokens", "output_tokens", "claude_reported_cost_usd", "seconds")}})
    return groups


def usage(cli: dict) -> dict:
    result = cli.get("result") or {}
    data = result.get("usage") or {}
    available = isinstance(result.get("usage"), dict)
    inputs = data.get("input_tokens", 0) or 0
    if cli["host"] == "claude":
        inputs += (data.get("cache_creation_input_tokens", 0) or 0) + (data.get("cache_read_input_tokens", 0) or 0)
    return {"reported_usage_available": available,
            "input_tokens": inputs if available else None,
            "output_tokens": (data.get("output_tokens", 0) or 0) if available else None,
            "claude_reported_cost_usd": result.get("total_cost_usd", 0) or 0,
            "seconds": cli.get("seconds", cli.get("wall_time_s"))}


def native_results(errors: list[str]) -> dict:
    out = ROOT / "runs"
    manifest = read(out / "manifest.json")
    for name, expected in manifest["source_hashes"].items():
        if digest(ROOT / name) != expected:
            errors.append(f"changed source: {name}")
    rows = []
    for path in sorted(out.glob("*/*/result.json")):
        result, cli = read(path), read(path.parent / "cli.json")
        if hashlib.sha256(cli["prompt"].encode()).hexdigest() != cli["input_sha256"]:
            errors.append(f"prompt mismatch: {result['id']}")
        changes = sorted(name for name in result["initial_manifest"].keys() | result["final_manifest"].keys()
                         if result["initial_manifest"].get(name) != result["final_manifest"].get(name))
        if changes != result["changed_paths"]:
            errors.append(f"changed paths mismatch: {result['id']}")
        target = next(case["target"] for case in manifest["cases"] if case["id"] == result["case"])
        setup = read(path.parent.parent / "setup.json")
        if result["initial_manifest"][target] != setup["target_sha256"]:
            errors.append(f"initial target mismatch: {result['id']}")
        if hashlib.sha256(result["final_source"].encode()).hexdigest() != result["final_manifest"][target]:
            errors.append(f"final source mismatch: {result['id']}")
        actual = result["verification"]["returncode"] == 0 and not result["outside_target_changes"] and result["note_preserved"]
        if actual != result["verified"]:
            errors.append(f"verifier mismatch: {result['id']}")
        tools = Counter()
        commands = []
        failed_commands = 0
        explicit_observation_reads = 0
        for event in cli["events"]:
            if cli["host"] == "claude" and event["type"] == "assistant":
                for block in event["content"]:
                    if block["type"] == "tool_use":
                        tools[block["name"]] += 1
                        if "handoff-observation.json" in json.dumps(block.get("input", {})):
                            explicit_observation_reads += 1
                        if block["name"] == "Bash":
                            commands.append(block["input"].get("command", ""))
            elif cli["host"] == "codex" and event.get("type") == "item.completed":
                item = event.get("item", {})
                if item.get("type") in {"command_execution", "file_change", "mcp_tool_call", "web_search"}:
                    tools[item["type"]] += 1
                if item.get("type") == "command_execution":
                    commands.append(item.get("command", ""))
                    if "handoff-observation.json" in item.get("command", ""):
                        explicit_observation_reads += 1
                    failed_commands += item.get("exit_code") not in (0, None)
        rows.append({key: result[key] for key in ("id", "case", "receiver", "condition", "verified", "success",
                    "declared_complete", "outside_target_changes", "note_preserved", "seconds_including_verification")}
                    | {"cli_error": cli["error"], "tools": dict(tools), "tool_count": sum(tools.values()),
                       "failed_codex_commands": failed_commands, "commands": commands,
                       "explicit_observation_read_calls": explicit_observation_reads,
                       "verification_seconds": result["verification"]["seconds"],
                       "test_stderr": result["verification"]["stderr"], "usage": usage(cli),
                       "permission_denials": (cli["result"] or {}).get("permission_denials", [])})
    groups = []
    for host in ("claude", "codex"):
        for condition in manifest["conditions"]:
            selected = [row for row in rows if row["receiver"] == host and row["condition"] == condition]
            groups.append({"receiver": host, "condition": condition, "runs": len(selected),
                           "successes": sum(row["success"] for row in selected),
                           "tool_count": sum(row["tool_count"] for row in selected),
                           "missing_usage_runs": sum(not row["usage"]["reported_usage_available"] for row in selected),
                           "total_seconds": sum(row["seconds_including_verification"] for row in selected),
                           **{key: sum(row["usage"][key] or 0 for row in selected)
                              for key in ("input_tokens", "output_tokens", "claude_reported_cost_usd")}})
    return {"planned_runs": manifest["planned_runs"], "completed_runs": len(rows), "rows": rows, "groups": groups,
            "all_planned_runs_recorded": len(rows) == manifest["planned_runs"]}


def criteria_results(errors: list[str]) -> dict | None:
    out = ROOT / "criteria-runs"
    if not out.exists():
        return None
    manifest = read(out / "manifest.json")
    if digest(ROOT / "criteria.py") != manifest["source_sha256"]:
        errors.append("changed criteria script")
    cases = {case["id"]: case for case in manifest["cases"]}
    rows = []
    for path in sorted(out.glob("*--*--*.json")):
        row = read(path)
        cli = row["cli"]
        if hashlib.sha256(cli["prompt"].encode()).hexdigest() != cli["input_sha256"]:
            errors.append(f"criteria prompt mismatch: {path.name}")
        answer, expected = cli["answer"] or {}, cases[row["case"]]["expected"]
        matches = answer.get("action") == expected["action"] and sorted(answer.get("targets", [])) == sorted(expected["targets"])
        if matches != row["matches"]:
            errors.append(f"criteria score mismatch: {path.name}")
        rows.append({key: row[key] for key in ("host", "case", "condition", "matches")}
                    | {"answer": answer, "error": cli["error"], "usage": usage(cli)})
    extractions = {host: read(out / f"extraction-check--{host}.json")
                   for host in ("claude", "codex") if (out / f"extraction-check--{host}.json").exists()}
    return {"planned_decisions": 24, "completed_decisions": len(rows), "extractions": extractions, "rows": rows,
            "groups": aggregate(rows),
            "extraction_attempts": {host: {"error": read(path)["error"], "usage": usage(read(path))}
                                    for host in ("claude", "codex")
                                    if (path := out / f"extract--{host}.json").exists()}}


def freshness_results(errors: list[str]) -> dict | None:
    out = ROOT / "freshness-runs"
    if not out.exists():
        return None
    manifest = read(out / "manifest.json")
    if digest(ROOT / "freshness.py") != manifest["script_sha256"]:
        errors.append("changed freshness script")
    if digest(ROOT.parent / manifest["source_record"]) != manifest["source_record_sha256"]:
        errors.append("changed original freshness input")
    rows = []
    for path in sorted(out.glob("*--*--*.json")):
        row = read(path)
        cli = row["cli"]
        if cli["prompt"] != manifest["prompts"][row["condition"]]:
            errors.append(f"freshness prompt mismatch: {path.name}")
        rows.append({key: row[key] for key in ("host", "condition", "repeat")}
                    | {"answer": cli["answer"], "error": cli["error"], "usage": usage(cli)})
    return {"original_both_host_plan": manifest["original_both_host_plan"],
            "selected_host_plan": manifest["planned_calls"], "completed_calls": len(rows), "rows": rows,
            "groups": aggregate(rows)}


def main() -> None:
    errors = []
    native = native_results(errors)
    criteria = criteria_results(errors)
    freshness = freshness_results(errors)
    summary = {"validation_errors": errors, "native_handoff": native, "criteria": criteria, "freshness": freshness,
               "reuse_audit": read(ROOT / "reuse-audit.json"),
               "limits": ["Two historical defects and no repetitions within each native condition.",
                          "Observed tool counts are not counts of model inference requests.",
                          "Uses Stage registration and handoff records, not every plugin hook or driver lifecycle.",
                          "Synthetic criterion transfer does not establish personal-preference learning.",
                          "Historical logs do not provide complete input provenance for a real reuse rate."]}
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"validation_errors": errors, "native_runs": native["completed_runs"],
                      "native_groups": native["groups"],
                      "criteria_runs": criteria["completed_decisions"] if criteria else None,
                      "freshness_runs": freshness["completed_calls"] if freshness else None}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
