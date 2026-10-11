"""Count observable tool calls without treating one trial as a causal estimate."""
import argparse
import json
from pathlib import Path


def tool_calls(path: Path, host: str) -> dict:
    seen = {}
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if host == "codex":
            item = event.get("item", {})
            if item.get("type") in {"command_execution", "file_change", "mcp_tool_call", "web_search"}:
                seen[item["id"]] = item["type"]
        else:
            for block in event.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    seen[block["id"]] = block["name"]
    return {"total": len(seen), "by_type": {kind: list(seen.values()).count(kind) for kind in sorted(set(seen.values()))}}


def rows(root: Path) -> dict:
    result = {}
    for row in json.loads((root / "summary.json").read_text())["cases"]:
        case = row["direction"] + "-" + row["condition"]
        model = root / case / "model"
        result[case] = {name: row[name] for name in ("exit", "seconds", "input_tokens", "cached_input_tokens", "output_tokens", "reported_cost_usd")}
        result[case]["tools"] = tool_calls(model / "stdout.jsonl", row["direction"].split("-to-")[1])
        batch = root / case / "project/.data/batch-calls.jsonl"
        result[case]["batch_public_cli_calls"] = len(batch.read_text().splitlines()) if batch.exists() else None
    return result


parser = argparse.ArgumentParser()
parser.add_argument("before", type=Path)
parser.add_argument("after", type=Path)
args = parser.parse_args()
before, after = rows(args.before), rows(args.after)
comparison = {"before": str(args.before), "after": str(args.after), "cases": [
    {"case": case, "before": before[case], "after": after[case]} for case in sorted(after)],
    "limits": ["One run per condition; order, cache, and prompt were not controlled.",
               "Tool IDs count attempted tool actions; they are not individual model/API requests.",
               "A wrapper still executes the public CLIs; fewer AI tool calls do not mean fewer store operations.",
               "Timeout usage is unknown. Missing values do not mean zero."]}
(args.after / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
for row in comparison["cases"]:
    print(json.dumps(row))
