"""Ordered pin for the audit's record-link finding surface.

One kitchen-sink project triggers a representative violation for every
link-check group (dangling id/path refs, back-pointer mismatch, symmetry,
cycles, indexes, orphans, state refs). The test asserts the EXACT ordered
code sequence, so the record-graph rewrite (P31) cannot change what is
reported, where, or in which order.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit_stage = load_module("audit_stage_link_pin", SCRIPT_ROOT / "audit_stage.py")
init_stage = load_module("init_stage_link_pin", SCRIPT_ROOT / "init_stage.py")


class LinkFindingOrderPinTest(unittest.TestCase):
    maxDiff = None

    def write_item(self, root: Path, filename: str, **fields: str) -> Path:
        base = root / ".stage" / "present" / "work" / "items"
        base.mkdir(parents=True, exist_ok=True)
        defaults = {
            "id": filename,
            "title": "Test work",
            "status": "active",
            "verification": "pending",
            "retrospective": "pending",
            "promotion": "pending",
            "scope": "",
        }
        defaults.update(fields)
        body = "".join(f"{key}: {value}\n" for key, value in defaults.items())
        path = base / f"{filename}.md"
        path.write_text(f"---\n{body}---\n# {defaults['id']} Test work\n", encoding="utf-8")
        return path

    def write_retro(self, root: Path, retro_id: str, work_item: str) -> Path:
        path = root / ".stage" / "present" / "work" / "retrospectives" / f"{retro_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {retro_id}\nwork_item: {work_item}\n---\n# {retro_id}\n", encoding="utf-8"
        )
        return path

    def write_decision(
        self,
        root: Path,
        decision_id: str,
        work_item: str,
        status: str = "decided",
        principles: str = "SSOT — one owning location for this rule.",
    ) -> Path:
        path = root / ".stage" / "present" / "work" / "decisions" / f"{decision_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                f"---\nid: {decision_id}\nwork_item: {work_item}\nstatus: {status}\n---\n"
                f"# {decision_id}\n\n## Principles applied\n\n{principles}\n"
            ),
            encoding="utf-8",
        )
        return path

    def write_backlog(self, root: Path, filename: str, **fields: str) -> Path:
        base = root / ".stage" / "future" / "backlog" / "items"
        base.mkdir(parents=True, exist_ok=True)
        defaults = {"id": filename, "title": "Test", "parent": "", "status": "captured"}
        defaults.update(fields)
        body = "".join(f"{key}: {value}\n" for key, value in defaults.items())
        path = base / f"{filename}.md"
        path.write_text(f"---\n{body}---\n# {defaults['id']}\n", encoding="utf-8")
        return path

    def append_index(self, root: Path, index_name: str, item_id: str) -> None:
        path = root / ".stage" / "present" / "work" / index_name
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {item_id} | test | x | ai | [item](items/{item_id}.md) |\n")

    def test_link_finding_codes_pin_exact_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False)

            # Per-item field/ref findings, in filename scan order.
            self.write_item(root, "W-0001", retrospective="completed")  # WORK011
            self.write_item(root, "W-0002", retrospective="completed", retrospective_ref="R-9999")  # WORK012
            self.write_item(root, "W-0003", retrospective="completed", retrospective_ref="R-0003")  # WORK013
            self.write_item(root, "W-0004", decision_refs="DE-9999")  # WORK014
            self.write_item(root, "W-0005", decision_refs="DE-0005")  # WORK015
            self.write_item(root, "W-0006", parent="W-9999")  # WORK017
            self.write_item(root, "W-0007", parent="W-0008")  # WORK018 (cycle)
            self.write_item(root, "W-0008", parent="W-0007")  # WORK018 (cycle)
            self.write_item(root, "W-0009", parent="W-0010")  # WORK019 (finalized parent)
            self.write_item(
                root,
                "W-0010",
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0010",
                promotion="approved",
            )
            self.write_item(root, "W-0011", source="B-9999")  # WORK020
            self.write_item(root, "W-0012", source="B-0001")  # WORK023 (one-sided)
            self.write_item(root, "W-0013")  # target of B-0001.realized_by, source empty
            self.write_item(root, "W-0014", id="W-0001")  # WORK002 + WORK007 x2

            self.write_retro(root, "R-0003", "W-9999")  # WORK013 above + RETRO001
            self.write_retro(root, "R-0010", "W-0010")
            self.write_decision(root, "DE-0005", "W-0001")  # WORK015 above
            self.write_decision(root, "DE-0007", "")  # DECISION001
            self.write_decision(root, "DE-0008", "W-0001", status="weird")  # WORK016
            self.write_decision(root, "DE-0009", "W-0001", principles="")  # WORK021
            self.write_decision(root, "DE-0010", "W-0001", principles="Just vibes.")  # WORK022

            self.write_backlog(root, "B-0001", status="selected", realized_by="W-0013")  # BACKLOG006
            self.write_backlog(root, "B-0002", status="bogus")  # BACKLOG001
            self.write_backlog(root, "B-0003", parent="B-9999")  # BACKLOG002
            self.write_backlog(root, "B-0004", realized_by="W-9999")  # BACKLOG005
            self.write_backlog(root, "B-0005", id="B-5555")  # BACKLOG003
            self.write_backlog(root, "B-0006", status="selected")  # BACKLOG004

            question = root / ".stage" / "present" / "state" / "questions" / "Q-0001.md"
            question.write_text(
                "---\nid: Q-0001\ntitle: Q\nwork_items: W-9999\n---\n# Q-0001\n", encoding="utf-8"
            )  # STATE001

            for item_id in [f"W-{index:04d}" for index in range(1, 10)] + ["W-0011", "W-0012", "W-0013"]:
                self.append_index(root, "active.md", item_id)
            self.append_index(root, "active.md", "W-8888")  # INDEX001
            self.append_index(root, "review.md", "W-0010")
            self.append_index(root, "review.md", "W-7777")  # INDEX002

            findings = audit_stage.Audit(root).run()

        self.assertEqual(
            [
                "WORK011",
                "WORK012",
                "WORK013",
                "WORK014",
                "WORK015",
                "WORK002",
                "WORK007",
                "WORK007",
                "WORK017",
                "WORK019",
                "WORK018",
                "WORK018",
                "INDEX001",
                "INDEX002",
                "BACKLOG001",
                "BACKLOG005",
                "BACKLOG003",
                "BACKLOG004",
                "BACKLOG002",
                "WORK020",
                "WORK023",
                "BACKLOG006",
                "DECISION001",
                "WORK016",
                "WORK021",
                "WORK022",
                "RETRO001",
                "STATE001",
            ],
            [finding.code for finding in findings],
        )


if __name__ == "__main__":
    unittest.main()
