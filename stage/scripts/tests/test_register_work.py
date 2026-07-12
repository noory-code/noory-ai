from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-work" / "register_work.py"

ACTIVE = (
    "# Active Work\n\n"
    "| Work | Kind | Venue | Purpose | Status | Owner | Item |\n"
    "|---|---|---|---|---|---|---|\n"
)

BACKLOG_WITH_TRAILING_SECTION = (
    "# Backlog Index\n\n"
    "## Current backlog\n\n"
    "| ID | Title | Kind | Status | Priority | Parent | Item |\n"
    "|---|---|---|---|---|---|---|\n"
    "| W-00000001 | Existing | chore | captured | low |  | "
    "[items/W-00000001.md](items/W-00000001.md) |\n\n"
    "## Status values\n\n"
    "- `captured`: captured but not yet organized.\n"
)


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args], capture_output=True, text=True
    )


class RegisterWorkTest(unittest.TestCase):
    def make(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/present/work/items").mkdir(parents=True)
        (root / ".stage/past/work/archive/items").mkdir(parents=True)
        (root / ".stage/present/work/active.md").write_text(ACTIVE, encoding="utf-8")
        return tmp, root

    def declare_routing(self, root: Path) -> None:
        (root / ".stage/settings.json").write_text(
            '{"schema_version": 2, "venue_routing": '
            '{"design": "claude", "development": "codex", "feature": "split"}}',
            encoding="utf-8",
        )

    def write_decision(
        self, root: Path, *, decision_id: str = "DE-0009", status: str = "decided",
        authorizes: str = "venue_exception",
    ) -> None:
        decisions = root / ".stage/present/work/decisions"
        decisions.mkdir(parents=True, exist_ok=True)
        lines = [f"---", f"id: {decision_id}", "work_item: W-00000001", f"status: {status}"]
        if authorizes:
            lines.append(f"authorizes: {authorizes}")
        lines += ["---", f"# {decision_id} Exception", ""]
        (decisions / f"{decision_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def test_venue_derived_from_declared_routing(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(root, "--title", "T", "--kind", "design", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("venue derived from venue_routing: design -> claude", result.stdout)
            item = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")

        self.assertIn("venue: claude", item)
        self.assertIn("| claude |", active)

    def test_unrouted_kind_keeps_empty_venue(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(root, "--title", "T", "--kind", "chore", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)

        self.assertNotIn("derived", result.stdout)
        self.assertNotIn("policy exception", result.stdout)

    def test_contradicting_venue_without_decision_is_refused(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude",
            )
            created = (root / ".stage/present/work/items/W-00000001.md").exists()

        self.assertEqual(1, result.returncode)
        self.assertIn("--decision", result.stderr)
        self.assertFalse(created)

    def test_contradicting_venue_with_valid_decision_registers(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            self.write_decision(root)
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            item = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")

        self.assertIn("venue: claude", item)
        self.assertIn("decision_refs: DE-0009", item)

    def test_open_or_non_authorizing_decision_is_refused(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            self.write_decision(root, status="open")
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(1, result.returncode)

            self.write_decision(root, authorizes="")
            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(1, result.returncode)

            result = run(
                root, "--title", "T", "--kind", "development", "--scope", "src",
                "--venue", "claude", "--decision", "DE-9999",
            )
            self.assertEqual(1, result.returncode)

    def test_split_kind_single_item_is_refused_with_resolution(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            result = run(root, "--title", "T", "--kind", "feature", "--scope", "src")
            created = (root / ".stage/present/work/items/W-00000001.md").exists()

        self.assertEqual(1, result.returncode)
        self.assertIn("split", result.stderr)
        self.assertIn("parent", result.stderr)
        self.assertFalse(created)

    def test_split_kind_with_valid_decision_registers_single_item(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root)
            self.write_decision(root)
            result = run(
                root, "--title", "T", "--kind", "feature", "--scope", "src",
                "--venue", "claude", "--decision", "DE-0009",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            item = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")

        self.assertIn("decision_refs: DE-0009", item)

    def test_no_policy_keeps_current_behavior(self):
        tmp, root = self.make()
        with tmp:
            result = run(root, "--title", "T", "--kind", "design", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)

        self.assertNotIn("derived", result.stdout)
        self.assertNotIn("policy exception", result.stdout)

    def test_auto_id_and_link_row(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "--title", "Do a thing", "--kind", "feature", "--scope", "stage/x", "--venue", "claude")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = root / ".stage/present/work/items/W-00000001.md"
            self.assertTrue(item.exists())
            body = item.read_text(encoding="utf-8")
            self.assertIn("id: W-00000001", body)
            self.assertIn("kind: feature", body)
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")
            self.assertIn("[items/W-00000001.md](items/W-00000001.md)", active)

    def test_increments_past_max_including_archive(self):
        tmp, root = self.make()
        with tmp:
            (root / ".stage/past/work/archive/items/W-00000005.md").write_text("---\nid: W-00000005\n---\n", encoding="utf-8")
            run(root, "--title", "A", "--kind", "chore", "--scope", "x")
            self.assertTrue((root / ".stage/present/work/items/W-00000006.md").exists())

    def test_reruns_reconcile_index_not_duplicate(self):
        tmp, root = self.make()
        with tmp:
            run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000001")
            # Drop the row, then a re-run with same id must re-add exactly one.
            (root / ".stage/present/work/active.md").write_text(ACTIVE, encoding="utf-8")
            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000001")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")
            self.assertEqual(active.count("[items/W-00000001.md]"), 1)

    def test_active_row_is_inserted_before_trailing_sections(self):
        tmp, root = self.make()
        with tmp:
            active_path = root / ".stage/present/work/active.md"
            active_path.write_text(
                ACTIVE + "\n## Status values\n\n- `active`: work in progress.\n",
                encoding="utf-8",
            )

            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            active = active_path.read_text(encoding="utf-8")

        self.assertLess(active.index("| W-00000001 |"), active.index("## Status values"))

    def test_backlog_row_is_inserted_after_empty_table_header(self):
        tmp, root = self.make()
        with tmp:
            backlog = root / ".stage/future/backlog"
            (backlog / "items").mkdir(parents=True)
            empty_index = BACKLOG_WITH_TRAILING_SECTION.replace(
                "| W-00000001 | Existing | chore | captured | low |  | "
                "[items/W-00000001.md](items/W-00000001.md) |\n",
                "",
            )
            index_path = backlog / "index.md"
            index_path.write_text(empty_index, encoding="utf-8")

            proc = run(
                root,
                "--backlog",
                "--title",
                "First work",
                "--kind",
                "fix",
                "--scope",
                "",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            index = index_path.read_text(encoding="utf-8")

        separator = index.index("|---|---|---|---|---|---|---|")
        new_row = index.index("| W-00000001 | First work |")
        trailing_section = index.index("## Status values")
        self.assertLess(separator, new_row)
        self.assertLess(new_row, trailing_section)

    def test_backlog_row_is_inserted_before_trailing_sections(self):
        tmp, root = self.make()
        with tmp:
            backlog = root / ".stage/future/backlog"
            (backlog / "items").mkdir(parents=True)
            (backlog / "items/W-00000001.md").write_text(
                "---\nid: W-00000001\n---\n", encoding="utf-8"
            )
            index_path = backlog / "index.md"
            index_path.write_text(BACKLOG_WITH_TRAILING_SECTION, encoding="utf-8")

            proc = run(
                root,
                "--backlog",
                "--title",
                "New work",
                "--kind",
                "fix",
                "--scope",
                "",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            index = index_path.read_text(encoding="utf-8")

        existing_row = index.index("| W-00000001 | Existing |")
        new_row = index.index("| W-00000002 | New work |")
        trailing_section = index.index("## Status values")
        self.assertLess(existing_row, new_row)
        self.assertLess(new_row, trailing_section)

    def test_refuses_archived_id(self):
        tmp, root = self.make()
        with tmp:
            (root / ".stage/past/work/archive/items/W-00000003.md").write_text("---\nid: W-00000003\n---\n", encoding="utf-8")
            proc = run(root, "--title", "A", "--kind", "chore", "--scope", "x", "--id", "W-00000003")
            self.assertEqual(proc.returncode, 1)
            self.assertFalse((root / ".stage/present/work/items/W-00000003.md").exists())


if __name__ == "__main__":
    unittest.main()
