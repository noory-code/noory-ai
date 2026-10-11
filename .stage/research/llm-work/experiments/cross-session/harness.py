"""고정한 과거 Stage 트리에서 읽기·문자열 교체·회귀 검사만 실행합니다."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "review-reuse"
SPEC = importlib.util.spec_from_file_location("frozen_prepare", PREVIOUS / "prepare-recorded.py")
assert SPEC and SPEC.loader
PREP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREP)
CASES = PREP.CASES
NOTE = "\n# User note: preserve this audit comment added between sessions.\n"


def digest(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def setup(root: Path, case: dict, source: str) -> dict:
    started = time.perf_counter()
    archive = PREP.git("archive", "--format=tar", case["commit"], "stage/")
    PREP.extract_stage(archive, root)
    (root / case["target"]).write_text(source, encoding="utf-8")
    return {"seconds": time.perf_counter() - started, "archive_sha256": hashlib.sha256(archive).hexdigest(),
            "source_sha256": digest(source), "commit": case["commit"]}


def test(root: Path, case: dict, *, full: bool = False) -> dict:
    name = case["test"].split(".")[0] if full else case["test"]
    command = [sys.executable, "-B", "-m", "unittest", name, "-q"]
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
    started = time.perf_counter()
    try:
        result = subprocess.run(command, cwd=root / "stage/scripts/tests", env=environment,
                                text=True, capture_output=True, timeout=120)
        return {"command": command, "returncode": result.returncode,
                "stdout": result.stdout.replace(str(root), "<experiment>"),
                "stderr": result.stderr.replace(str(root), "<experiment>"),
                "seconds": time.perf_counter() - started}
    except subprocess.TimeoutExpired:
        return {"command": command, "returncode": None, "error": "test timeout 120s",
                "seconds": time.perf_counter() - started}


def tool(root: Path, case: dict, answer: dict) -> dict:
    action, targets = answer["action"], answer["targets"]
    allowed_read = {case["target"], case["test_file"]}
    if action == "read" and len(targets) == 1 and targets[0] in allowed_read:
        text = (root / targets[0]).read_text(encoding="utf-8")
        # 검사 파일은 길 수 있으므로 해당 메서드와 소속 클래스 이름을 돌려줍니다.
        if targets[0] == case["test_file"]:
            import ast
            tree = ast.parse(text)
            method = case["test"].split(".")[-1]
            found = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == method]
            if len(found) != 1:
                return {"ok": False, "error": "test method not uniquely found"}
            node = found[0]
            lines = text.splitlines(keepends=True)
            text = "".join(lines[node.lineno - 1:node.end_lineno])
        return {"ok": True, "path": targets[0], "content": text, "sha256": digest(text)}
    if action == "replace" and len(targets) == 3 and targets[0] == case["target"]:
        path, old, new = root / targets[0], targets[1], targets[2]
        before = path.read_text(encoding="utf-8")
        if not old or before.count(old) != 1:
            return {"ok": False, "error": "old text must occur exactly once", "old_occurrences": before.count(old) if old else None}
        after = before.replace(old, new, 1)
        path.write_text(after, encoding="utf-8")
        return {"ok": True, "before_sha256": digest(before), "after_sha256": digest(after),
                "changed": after != before}
    if action == "test" and not targets:
        result = test(root, case)
        return {"ok": result["returncode"] == 0, **result}
    if action == "finish" and not targets:
        return {"ok": True, "declared_complete": True}
    return {"ok": False, "error": "invalid tool or arguments"}


def verify(root: Path, case: dict, initial_tree: dict[str, str], note_required: bool) -> dict:
    focused = test(root, case)
    full = test(root, case, full=True)
    final_tree = PREP.tree_manifest(root)
    changed = sorted(name for name in initial_tree.keys() | final_tree.keys()
                     if initial_tree.get(name) != final_tree.get(name))
    outside = [name for name in changed if name != case["target"]]
    note_kept = not note_required or NOTE in (root / case["target"]).read_text(encoding="utf-8")
    return {"focused": focused, "full_module": full, "changed_paths": changed,
            "outside_target_changes": outside, "note_preserved": note_kept,
            "passed": focused["returncode"] == 0 and full["returncode"] == 0 and not outside and note_kept}
