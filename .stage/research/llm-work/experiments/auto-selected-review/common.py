"""기존 검토와 CLI를 재사용하고 함수 목록과 선택 결과를 다룹니다."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "selected-review"
sys.path.insert(0, str(PREVIOUS))
SPEC = importlib.util.spec_from_file_location("previous_selected_run", PREVIOUS / "run.py")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
sys.path.remove(str(PREVIOUS))
CLI = BASE.CLI
digest, save = BASE.digest, BASE.save


def function_index(source: str) -> list[dict]:
    tree = ast.parse(source)
    functions = [node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    names = {node.name for node in functions}
    return [{"name": node.name, "arguments": ast.unparse(node.args),
             "description": ast.get_docstring(node) or "",
             "same_file_references": sorted({n.id for n in ast.walk(node)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} & names)}
            for node in functions]


def choose_source(source: str, answer: dict | None) -> dict:
    answer = answer if isinstance(answer, dict) else {}
    targets = answer.get("targets")
    fallback = {"source": source, "entry": None, "mode": "full",
                "reason": "invalid_selection", "selection_valid": False}
    if answer.get("action") == "use_full" and targets == []:
        return {**fallback, "reason": "requested_full", "selection_valid": True}
    if (answer.get("action") != "select_entry" or not isinstance(targets, list)
            or len(targets) != 1 or not isinstance(targets[0], str)):
        return fallback
    try:
        names = {row["name"] for row in function_index(source)}
    except SyntaxError:
        return {**fallback, "reason": "invalid_source"}
    if targets[0] not in names:
        return fallback
    return {**BASE.select_source(source, targets[0]), "entry": targets[0], "selection_valid": True}


def usage(cli: dict) -> dict:
    result = cli.get("result") or {}
    values = result.get("usage")
    if not isinstance(values, dict):
        return {"input_tokens": None, "cached_input_tokens": None,
                "output_tokens": None, "reported_cost_usd": result.get("total_cost_usd")}
    inputs = values.get("input_tokens")
    if cli["host"] == "claude":
        inputs += values.get("cache_creation_input_tokens", 0) + values.get("cache_read_input_tokens", 0)
        cached = values.get("cache_read_input_tokens", 0)
    else:
        cached = values.get("cached_input_tokens")
    return {"input_tokens": inputs, "cached_input_tokens": cached,
            "output_tokens": values.get("output_tokens"),
            "reported_cost_usd": result.get("total_cost_usd")}
