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
        base = root / ".stage" / "work" / "current"
        base.mkdir(parents=True, exist_ok=True)
        parent = fields.pop("parent", "")
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
        if parent:
            path = base / parent / filename / "_story.md"
        elif (base / filename).is_dir():
            path = base / filename / "_epic.md"
        else:
            path = base / filename / "_story.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\n{body}---\n# {defaults['id']} Test work\n\n"
            "## Purpose\n\nDeliver the requested outcome.\n\n"
            "## Success criteria\n\n- The user observes the requested outcome.\n",
            encoding="utf-8",
        )
        return path

    def write_retro(self, root: Path, retro_id: str, work_item: str) -> Path:
        path = root / ".stage" / "work" / "retrospectives" / f"{retro_id}.md"
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
        path = root / ".stage" / "decisions" / "pending" / f"{decision_id}.md"
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
        base = root / ".stage" / "work" / "planned"
        base.mkdir(parents=True, exist_ok=True)
        parent = fields.pop("parent", "")
        defaults = {"id": filename, "title": "Test", "status": "captured"}
        defaults.update(fields)
        body = "".join(f"{key}: {value}\n" for key, value in defaults.items())
        if parent:
            path = base / parent / filename / "_story.md"
        elif (base / filename).is_dir():
            path = base / filename / "_epic.md"
        else:
            path = base / filename / "_story.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\n{body}---\n# {defaults['id']}\n\n"
            "## Purpose\n\nDeliver the requested outcome.\n\n"
            "## Success criteria\n\n- The user observes the requested outcome.\n",
            encoding="utf-8",
        )
        return path

    def append_index(self, root: Path, index_name: str, item_id: str) -> None:
        path = root / ".stage" / "work" / index_name
        target = next(
            (
                candidate
                for candidate in (root / ".stage/work").rglob("*.md")
                if f"id: {item_id}\n" in candidate.read_text(encoding="utf-8")
            ),
            root / ".stage/work/current" / item_id / "_story.md",
        )
        link = target.relative_to(path.parent).as_posix()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {item_id} | test | x | ai | [item]({link}) |\n")

    def test_link_finding_codes_pin_exact_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False)

            # Per-item field/ref findings, in filename scan order. W-0001
            # links back every decision that names it (DECISION002 otherwise).
            self.write_item(
                root,
                "W-0001",
                retrospective="completed",  # WORK011
                decision_refs="DE-0005, DE-0008, DE-0009, DE-0010",
            )
            self.write_item(root, "W-0002", retrospective="completed", retrospective_ref="R-9999")  # WORK012
            self.write_item(root, "W-0003", retrospective="completed", retrospective_ref="R-0003")  # WORK013
            self.write_item(root, "W-0004", decision_refs="DE-9999")  # WORK014
            self.write_item(root, "W-0005", decision_refs="DE-0005")  # WORK015
            self.write_item(root, "W-0006", parent="W-9999")  # WORK017
            self.write_item(root, "W-0007")
            self.write_item(root, "W-0008")
            self.write_item(root, "W-0009", parent="W-0010")  # WORK019 (finalized parent)
            self.write_item(
                root,
                "W-0010",
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0010",
                promotion="not_applicable",
            )
            self.write_item(root, "W-0011", source="B-9999")  # legacy source: inert history
            self.write_item(root, "W-0012", source="B-0001")  # legacy source: inert history
            self.write_item(root, "W-0013")
            self.write_item(root, "W-0014", id="W-0001")  # WORK002 + WORK007 x2

            self.write_retro(root, "R-0003", "W-9999")  # WORK013 above + RETRO001
            self.write_retro(root, "R-0010", "W-0010")
            self.write_decision(root, "DE-0005", "W-0001")  # WORK015 above
            self.write_decision(root, "DE-0007", "")  # DECISION001
            self.write_decision(root, "DE-0008", "W-0001", status="weird")  # WORK016
            self.write_decision(root, "DE-0009", "W-0001", principles="")  # WORK021
            self.write_decision(root, "DE-0010", "W-0001", principles="Just vibes.")  # WORK022
            self.write_decision(root, "DE-0011", "W-0001")  # DECISION002 (not linked back)
            self.write_retro(root, "R-0012", "W-0010")  # RETRO002 (W-0010 binds R-0010)

            # Planned cards (DE-00000007): realization links retired; selected
            # cards and legacy realized_by fields produce no findings.
            self.write_backlog(root, "W-0101", status="selected", realized_by="W-0013")
            self.write_backlog(root, "W-0102", status="bogus")  # BACKLOG001
            self.write_backlog(root, "W-0103", parent="W-9999")  # BACKLOG002
            self.write_backlog(root, "W-0104", realized_by="W-9999")
            self.write_backlog(root, "W-0105", id="W-0555")  # BACKLOG003
            self.write_backlog(root, "W-0106", status="selected")

            question = root / ".stage" / "state" / "questions" / "Q-0001.md"
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
                "WORK024",
                "WORK019",
                "WORK017",
                "INDEX001",
                "INDEX001",
                "INDEX002",
                "INDEX003",
                "INDEX003",
                "BACKLOG001",
                "BACKLOG003",
                "BACKLOG002",
                "DECISION001",
                "WORK016",
                "WORK021",
                "WORK022",
                "DECISION002",
                "RETRO001",
                "RETRO002",
                "DECISION004",
                "STATE001",
                # Family-index membership (X4): every backlog record in the
                # fixture is deliberately unindexed.
                "BACKLOG008",
                "BACKLOG008",
                "BACKLOG008",
                "BACKLOG008",
                "BACKLOG008",
                "BACKLOG008",
                "FAMILY002",
            ],
            [finding.code for finding in findings],
        )


if __name__ == "__main__":
    unittest.main()
