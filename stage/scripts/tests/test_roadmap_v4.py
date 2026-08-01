"""Schema-v4 roadmap creation, chain integrity, and audit contracts."""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
SCRIPT_ROOT = STAGE_ROOT / "scripts"
ROADMAP = STAGE_ROOT / "skills" / "stage-roadmap" / "manage_roadmap.py"
REGISTER = STAGE_ROOT / "skills" / "stage-work" / "register_work.py"
AUDIT = SCRIPT_ROOT / "audit_stage.py"
REFRESH_DECISIONS = SCRIPT_ROOT / "refresh_decision_index.py"
V3_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "project-stage"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"
for import_root in (HOOK_ROOT, SCRIPT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import stage_roadmap  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit_stage = load_module("roadmap_v4_audit_stage", AUDIT)


def run_cli(cli: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    if cli == REGISTER and "--scale" not in args and "--count-open-milestones" not in args:
        args = ("--scale", "story", *args)
    return subprocess.run(
        [sys.executable, str(cli), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def set_field(path: Path, field: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        rf"^({re.escape(field)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise AssertionError(f"missing field {field} in {path}")
    path.write_text(updated, encoding="utf-8")


class RoadmapFixture(unittest.TestCase):
    def make_fixture(self, template_root: Path = V4_TEMPLATE_ROOT):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(template_root, root / ".stage")
        return tmp, root

    def create_theme_and_milestone(self, root: Path) -> tuple[str, str]:
        theme = run_cli(
            ROADMAP,
            root,
            "create-theme",
            "--title",
            "Delivery reliability",
            "--intent",
            "Make delivery predictable",
        )
        milestone = run_cli(
            ROADMAP,
            root,
            "create-milestone",
            "--theme",
            "TH-00000001",
            "--title",
            "Stable release",
            "--purpose",
            "Ship safely",
            "--period",
            "2026 Q3",
            "--completion-criteria",
            "All checks pass",
        )
        self.assertEqual(0, theme.returncode, theme.stderr)
        self.assertEqual(0, milestone.returncode, milestone.stderr)
        return "TH-00000001", "M-00000001"

    def write_decision(
        self,
        root: Path,
        decision_id: str,
        milestone_id: str,
        *,
        predecessor: str = "",
        supersedes: str = "",
        transition: str = "pursuit",
        status: str = "decided",
    ) -> Path:
        path = root / ".stage" / "decisions" / "pending" / f"{decision_id}.md"
        path.write_text(
            (
                "---\n"
                f"id: {decision_id}\n"
                f"roadmap_item: {milestone_id}\n"
                f"status: {status}\n"
                f"transition: {transition}\n"
                f"predecessor: {predecessor}\n"
                f"supersedes: {supersedes}\n"
                "---\n\n"
                f"# {decision_id} Roadmap transition\n\n"
                "## Principles applied\n\n- SSOT\n- Honesty\n"
            ),
            encoding="utf-8",
        )
        return path

    def set_chain(self, root: Path, milestone_id: str, *decision_ids: str) -> Path:
        milestone = (
            root / ".stage" / "roadmap" / "milestones" / f"{milestone_id}.md"
        )
        set_field(milestone, "decision_refs", ", ".join(decision_ids))
        return milestone

    def findings(self, root: Path):
        return audit_stage.Audit(root).run()

    def codes(self, root: Path) -> list[str]:
        return [finding.code for finding in self.findings(root)]

    def assert_audit_clean(self, root: Path) -> None:
        refreshed = run_cli(REFRESH_DECISIONS, root)
        self.assertEqual(0, refreshed.returncode, refreshed.stdout + refreshed.stderr)
        findings = self.findings(root)
        self.assertEqual([], findings, [finding.to_dict() for finding in findings])


class RoadmapCliTest(RoadmapFixture):
    def test_creation_uses_per_type_counters_and_syncs_indexes(self):
        tmp, root = self.make_fixture()
        with tmp:
            theme_id, milestone_id = self.create_theme_and_milestone(root)
            stage_root = root / ".stage"
            theme = stage_root / "roadmap" / "themes" / f"{theme_id}.md"
            milestone = stage_root / "roadmap" / "milestones" / f"{milestone_id}.md"
            theme_index = (stage_root / "roadmap/themes/index.md").read_text(
                encoding="utf-8"
            )
            milestone_index = (stage_root / "roadmap/milestones/index.md").read_text(
                encoding="utf-8"
            )

            self.assertTrue(theme.is_file())
            self.assertTrue(milestone.is_file())
            self.assertIn("id: TH-00000001", theme.read_text(encoding="utf-8"))
            self.assertNotIn("status:", theme.read_text(encoding="utf-8"))
            self.assertIn("theme: TH-00000001", milestone.read_text(encoding="utf-8"))
            self.assertNotIn("status:", milestone.read_text(encoding="utf-8"))
            self.assertIn("| TH-00000001 | Delivery reliability |", theme_index)
            self.assertIn(
                "| M-00000001 | TH-00000001 | Stable release | 2026 Q3 |",
                milestone_index,
            )
            self.assert_audit_clean(root)

    def test_end_to_end_pursuit_registration_audit_and_list(self):
        tmp, root = self.make_fixture()
        with tmp:
            _theme_id, milestone_id = self.create_theme_and_milestone(root)
            pursuit = run_cli(ROADMAP, root, "open-pursuit", milestone_id)
            decision_index = (root / ".stage/decisions/index.md").read_text(
                encoding="utf-8"
            )
            refreshed = run_cli(REFRESH_DECISIONS, root)
            refreshed_index = (root / ".stage/decisions/index.md").read_text(
                encoding="utf-8"
            )
            registered = run_cli(
                REGISTER,
                root,
                "--title",
                "Implement stable release",
                "--kind",
                "development",
                "--scope",
                "src",
                "--venue",
                "codex",
                "--milestone",
                milestone_id,
            )
            audited = run_cli(AUDIT, root)
            listing = run_cli(ROADMAP, root, "list")
            open_count = run_cli(REGISTER, root, "--count-open-milestones")

            self.assertEqual(0, pursuit.returncode, pursuit.stderr)
            self.assertIn("DE-00000001", pursuit.stdout)
            self.assertNotIn("DE-00000001", decision_index)
            self.assertEqual(0, refreshed.returncode, refreshed.stdout + refreshed.stderr)
            self.assertIn(
                "[M-00000001](../roadmap/milestones/M-00000001.md) | active | active |",
                refreshed_index,
            )
            self.assertEqual(0, registered.returncode, registered.stderr)
            self.assertEqual(0, audited.returncode, audited.stdout + audited.stderr)
            self.assertIn("Summary: errors=0, warnings=0", audited.stdout)
            self.assertEqual(0, listing.returncode, listing.stderr)
            self.assertRegex(
                listing.stdout,
                r"\| M-00000001 \| TH-00000001 \| Stable release \| active \|",
            )
            self.assertEqual("1", open_count.stdout.strip())

    def test_v3_refuses_without_writing(self):
        tmp, root = self.make_fixture(V3_TEMPLATE_ROOT)
        with tmp:
            before = set((root / ".stage/future/roadmap").rglob("*"))
            result = run_cli(
                ROADMAP, root, "create-theme", "--title", "Must stay dormant"
            )
            after = set((root / ".stage/future/roadmap").rglob("*"))

        self.assertEqual(2, result.returncode)
        self.assertIn("plugin requires v5", result.stderr)
        self.assertIn("stage-migrate", result.stderr)
        self.assertEqual(before, after)


class DecisionChainTest(RoadmapFixture):
    def test_dangling_predecessor_and_supersedes_are_rejected_then_repaired(self):
        for field in ("predecessor", "supersedes"):
            with self.subTest(field=field):
                tmp, root = self.make_fixture()
                with tmp:
                    _theme_id, milestone_id = self.create_theme_and_milestone(root)
                    values = {field: "DE-99999999"}
                    decision = self.write_decision(root, "DE-00000001", milestone_id, **values)
                    self.set_chain(root, milestone_id, "DE-00000001")
                    self.assertIn("CHAIN001", self.codes(root))

                    set_field(decision, field, "")
                    self.assert_audit_clean(root)

    def test_cycle_is_rejected_then_repaired(self):
        tmp, root = self.make_fixture()
        with tmp:
            _theme_id, milestone_id = self.create_theme_and_milestone(root)
            first = self.write_decision(
                root, "DE-00000001", milestone_id, predecessor="DE-00000002"
            )
            self.write_decision(
                root, "DE-00000002", milestone_id, predecessor="DE-00000001"
            )
            self.set_chain(root, milestone_id, "DE-00000001", "DE-00000002")
            self.assertIn("CHAIN002", self.codes(root))

            set_field(first, "predecessor", "")
            self.assert_audit_clean(root)

    def test_fork_is_rejected_then_repaired(self):
        tmp, root = self.make_fixture()
        with tmp:
            _theme_id, milestone_id = self.create_theme_and_milestone(root)
            self.write_decision(root, "DE-00000001", milestone_id)
            self.write_decision(
                root, "DE-00000002", milestone_id, predecessor="DE-00000001"
            )
            third = self.write_decision(
                root, "DE-00000003", milestone_id, predecessor="DE-00000001"
            )
            self.set_chain(
                root,
                milestone_id,
                "DE-00000001",
                "DE-00000002",
                "DE-00000003",
            )
            self.assertIn("CHAIN003", self.codes(root))

            set_field(third, "supersedes", "DE-00000002")
            self.assert_audit_clean(root)

    def test_multiple_heads_are_rejected_then_repaired(self):
        tmp, root = self.make_fixture()
        with tmp:
            _theme_id, milestone_id = self.create_theme_and_milestone(root)
            self.write_decision(root, "DE-00000001", milestone_id)
            second = self.write_decision(root, "DE-00000002", milestone_id)
            self.set_chain(root, milestone_id, "DE-00000001", "DE-00000002")
            self.assertIn("CHAIN004", self.codes(root))

            set_field(second, "predecessor", "DE-00000001")
            self.assert_audit_clean(root)

    def test_computed_status_follows_structural_head(self):
        tmp, root = self.make_fixture()
        with tmp:
            _theme_id, milestone_id = self.create_theme_and_milestone(root)
            milestone = self.set_chain(root, milestone_id)
            self.assertEqual(
                "planned",
                stage_roadmap.roadmap_record_state(root / ".stage", milestone).status,
            )

            self.write_decision(root, "DE-00000002", milestone_id)
            self.set_chain(root, milestone_id, "DE-00000002")
            self.assertEqual(
                "active",
                stage_roadmap.roadmap_record_state(root / ".stage", milestone).status,
            )

            self.write_decision(
                root,
                "DE-00000001",
                milestone_id,
                predecessor="DE-00000002",
                transition="closure",
            )
            self.set_chain(root, milestone_id, "DE-00000002", "DE-00000001")
            state = stage_roadmap.roadmap_record_state(root / ".stage", milestone)
            self.assertEqual("closed", state.status)
            self.assertEqual("DE-00000001", state.effective_head)

    def test_theme_status_is_also_computed_from_its_chain(self):
        tmp, root = self.make_fixture()
        with tmp:
            theme_id, _milestone_id = self.create_theme_and_milestone(root)
            theme = root / f".stage/roadmap/themes/{theme_id}.md"
            self.assertEqual(
                "planned",
                stage_roadmap.roadmap_record_state(root / ".stage", theme).status,
            )

            self.write_decision(root, "DE-00000002", theme_id)
            set_field(theme, "decision_refs", "DE-00000002")
            self.assertEqual(
                "active",
                stage_roadmap.roadmap_record_state(root / ".stage", theme).status,
            )


class RoadmapAuditTest(RoadmapFixture):
    def test_dangling_work_milestone_is_rejected_then_repaired(self):
        tmp, root = self.make_fixture()
        with tmp:
            _theme_id, milestone_id = self.create_theme_and_milestone(root)
            registered = run_cli(
                REGISTER,
                root,
                "--title",
                "Dangling attribution",
                "--kind",
                "development",
                "--scope",
                "src",
                "--venue",
                "codex",
                "--milestone",
                "M-99999999",
            )
            self.assertEqual(0, registered.returncode, registered.stderr)
            card = root / ".stage/work/current/W-00000001/_story.md"
            self.assertIn("ROADMAP005", self.codes(root))

            set_field(card, "milestone", milestone_id)
            self.assertEqual([], self.codes(root))

    def test_dangling_milestone_theme_is_rejected_then_repaired(self):
        tmp, root = self.make_fixture()
        with tmp:
            theme_id, milestone_id = self.create_theme_and_milestone(root)
            milestone = root / f".stage/roadmap/milestones/{milestone_id}.md"
            index = root / ".stage/roadmap/milestones/index.md"
            set_field(milestone, "theme", "TH-99999999")
            index.write_text(
                index.read_text(encoding="utf-8").replace(theme_id, "TH-99999999"),
                encoding="utf-8",
            )
            self.assertIn("ROADMAP006", self.codes(root))

            set_field(milestone, "theme", theme_id)
            index.write_text(
                index.read_text(encoding="utf-8").replace("TH-99999999", theme_id),
                encoding="utf-8",
            )
            self.assert_audit_clean(root)

    def test_theme_and_milestone_index_mismatches_are_rejected(self):
        tmp, root = self.make_fixture()
        with tmp:
            theme_id, milestone_id = self.create_theme_and_milestone(root)
            stage_root = root / ".stage"
            theme_index = stage_root / "roadmap/themes/index.md"
            milestone_index = stage_root / "roadmap/milestones/index.md"
            original_theme = theme_index.read_text(encoding="utf-8")
            theme_index.write_text(
                "\n".join(
                    line for line in original_theme.splitlines() if theme_id not in line
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertIn("ROADMAP003", self.codes(root))

            theme_index.write_text(original_theme, encoding="utf-8")
            original_milestone = milestone_index.read_text(encoding="utf-8")
            milestone_index.write_text(
                original_milestone.replace("Stable release", "Wrong title"),
                encoding="utf-8",
            )
            self.assertIn("ROADMAP007", self.codes(root))

            milestone_index.write_text(original_milestone, encoding="utf-8")
            self.assert_audit_clean(root)


if __name__ == "__main__":
    unittest.main()
