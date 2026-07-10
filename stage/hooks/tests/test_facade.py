# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from pathlib import Path


HOOK_PATH = Path(__file__).resolve().parents[1] / "stage_guard.py"
SPEC = importlib.util.spec_from_file_location("stage_guard", HOOK_PATH)
stage_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["stage_guard"] = stage_guard
SPEC.loader.exec_module(stage_guard)

STAGE_ROOT = HOOK_PATH.parents[1]  # stage/
# Every file that imports the guard module and reaches into it by attribute.
CONSUMERS = [
    STAGE_ROOT / "scripts" / "audit_stage.py",
    STAGE_ROOT / "scripts" / "promote_intent.py",
    STAGE_ROOT / "hooks" / "tests" / "test_stage_guard.py",
    STAGE_ROOT / "scripts" / "tests" / "test_audit_stage.py",
    STAGE_ROOT / "scripts" / "tests" / "test_promote_intent.py",
]


def _referenced_attrs(pyfile: Path) -> set[str]:
    """Every `stage_guard.<attr>` accessed in the file."""
    tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    attrs: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "stage_guard"
        ):
            attrs.add(node.attr)
    return attrs


class FacadeCoverageTest(unittest.TestCase):
    def test_every_referenced_symbol_is_exported(self):
        # P33 module-split guard: the public facade `stage_guard` must expose
        # every symbol its consumers reference. Pins the export surface so that
        # extracting modules cannot silently drop one (the main deferral risk).
        missing: list[str] = []
        for consumer in CONSUMERS:
            if not consumer.exists():
                continue
            for attr in _referenced_attrs(consumer):
                if not hasattr(stage_guard, attr):
                    missing.append(f"{consumer.name}: stage_guard.{attr}")
        self.assertEqual(sorted(missing), [], f"facade missing symbols: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
