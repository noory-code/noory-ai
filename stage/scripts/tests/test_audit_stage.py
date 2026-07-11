import importlib.util
import json
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


audit_stage = load_module("audit_stage", SCRIPT_ROOT / "audit_stage.py")
init_stage = load_module("init_stage", SCRIPT_ROOT / "init_stage.py")


def finding_codes(findings):
    return {finding.code for finding in findings}


class StageAuditTest(unittest.TestCase):
    def init_stage(self, root: Path) -> None:
        init_stage.copy_templates(root, False)

    def write_work_item(
        self,
        root: Path,
        *,
        item_id: str = "W-0001",
        status: str = "active",
        verification: str = "pending",
        retrospective: str = "pending",
        retrospective_ref: str = "",
        promotion: str = "pending",
        location: str = "present",
        parent: str = "",
        decision_refs: str = "",
    ) -> Path:
        if location == "present":
            base = root / ".stage" / "present" / "work" / "items"
        else:
            base = root / ".stage" / "past" / "work" / "archive" / "items"
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"{item_id}.md"
        path.write_text(
            (
                "---\n"
                f"id: {item_id}\n"
                "title: Test work\n"
                f"parent: {parent}\n"
                f"status: {status}\n"
                f"verification: {verification}\n"
                f"retrospective: {retrospective}\n"
                f"retrospective_ref: {retrospective_ref}\n"
                f"promotion: {promotion}\n"
                "scope:\n"
                f"decision_refs: {decision_refs}\n"
                "---\n"
                f"# {item_id} Test work\n"
            ),
            encoding="utf-8",
        )
        return path

    def write_archive_retrospective(self, root: Path, *, retro_id: str = "R-0001", work_item: str = "W-0001") -> Path:
        path = root / ".stage" / "past" / "work" / "archive" / "retrospectives" / f"{retro_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {retro_id}\nwork_item: {work_item}\n---\n# {retro_id}\n",
            encoding="utf-8",
        )
        return path

    def write_decision(
        self,
        root: Path,
        *,
        decision_id: str = "DE-0001",
        work_item: str = "W-0001",
        status: str = "decided",
        principles: str = "SSOT — one owning location for this rule.",
    ) -> Path:
        path = root / ".stage" / "present" / "work" / "decisions" / f"{decision_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                f"---\nid: {decision_id}\nwork_item: {work_item}\nstatus: {status}\n---\n"
                f"# {decision_id}\n\n## Question\n\nQ\n\n## Principles applied\n\n{principles}\n\n## Chosen direction\n\nX\n"
            ),
            encoding="utf-8",
        )
        return path

    def write_backlog_item(self, root: Path, *, item_id: str = "B-0001", status: str = "captured", parent: str = "", frontmatter: bool = True) -> Path:
        path = root / ".stage" / "future" / "backlog" / "items" / f"{item_id}-test.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            path.write_text(
                f"---\nid: {item_id}\ntitle: Test\nkind:\nparent: {parent}\nstatus: {status}\npriority:\n---\n# {item_id}\n",
                encoding="utf-8",
            )
        else:
            path.write_text(f"# {item_id} Legacy item\n\n## Status\n\n`captured`\n", encoding="utf-8")
        return path

    def write_retrospective(self, root: Path, *, retro_id: str = "R-0001", work_item: str = "W-0001") -> Path:
        path = root / ".stage" / "present" / "work" / "retrospectives" / f"{retro_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                "---\n"
                f"id: {retro_id}\n"
                f"work_item: {work_item}\n"
                "---\n"
                f"# {retro_id} Retrospective\n"
            ),
            encoding="utf-8",
        )
        return path

    def append_active_index(self, root: Path, item_id: str) -> None:
        path = root / ".stage" / "present" / "work" / "active.md"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {item_id} | test | active | ai | [item](items/{item_id}.md) |\n")

    def append_review_index(self, root: Path, item_id: str, status: str = "review") -> None:
        path = root / ".stage" / "present" / "work" / "review.md"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {item_id} | passed | completed | {status} | [item](items/{item_id}.md) |\n")

    def test_initialized_stage_passes_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_invalid_work_status_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="done")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK003", finding_codes(findings))

    def test_completed_item_requires_closed_completion_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="completed", verification="passed", retrospective="pending", promotion="approved")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK008", finding_codes(findings))

    def test_completed_retrospective_requires_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
            )
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK011", finding_codes(findings))

    def test_completed_retrospective_reference_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK012", finding_codes(findings))

    def test_completed_retrospective_reference_must_link_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-9999")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK013", finding_codes(findings))

    def test_completed_retrospective_reference_passes_with_backlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_completed_retrospective_reference_accepts_retrospectives_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="retrospectives/R-0001.md",
                promotion="approved",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_archived_item_must_move_out_of_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="archived",
                verification="passed",
                retrospective="completed",
                promotion="not_applicable",
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK009", finding_codes(findings))

    def test_archive_location_requires_archived_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="completed", location="archive")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK010", finding_codes(findings))

    def test_active_item_must_be_indexed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")

            findings = audit_stage.Audit(root).run()

        self.assertIn("INDEX003", finding_codes(findings))

    def test_active_item_with_matching_index_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_review_retrospective_link_is_not_treated_as_missing_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="review")
            retrospective = root / ".stage" / "present" / "work" / "retrospectives" / "R-0001.md"
            retrospective.write_text("# R-0001\n", encoding="utf-8")
            review = root / ".stage" / "present" / "work" / "review.md"
            with review.open("a", encoding="utf-8") as handle:
                handle.write("| W-0001 | pending | [R-0001](retrospectives/R-0001.md) | pending | [item](items/W-0001.md) |\n")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("INDEX002", finding_codes(findings))

    def test_active_prose_with_sha_like_text_is_not_treated_as_missing_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")
            active = root / ".stage" / "present" / "work" / "active.md"
            with active.open("a", encoding="utf-8") as handle:
                handle.write("\nA SHA-256 digest is not a work item ID.\n")
                handle.write("| W-0001 | test | active | ai | [item](items/W-0001.md) |\n")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("INDEX001", finding_codes(findings))

    def test_similar_item_id_link_does_not_satisfy_missing_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="active")
            active = root / ".stage" / "present" / "work" / "active.md"
            with active.open("a", encoding="utf-8") as handle:
                handle.write("| W-00012 | test | active | ai | [item](items/W-00012.md) |\n")

            findings = audit_stage.Audit(root).run()

        self.assertIn("INDEX003", finding_codes(findings))

    def test_parent_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", parent="W-9999")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK017", finding_codes(findings))

    def test_parent_cycle_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="active", parent="W-0002")
            self.write_work_item(root, item_id="W-0002", status="active", parent="W-0001")
            self.append_active_index(root, "W-0001")
            self.append_active_index(root, "W-0002")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK018", finding_codes(findings))

    def test_open_child_with_finalized_parent_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="rejected")
            self.write_work_item(root, item_id="W-0002", status="active", parent="W-0001")
            self.append_review_index(root, "W-0001", "rejected")
            self.append_active_index(root, "W-0002")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK019", finding_codes(findings))

    def test_valid_parent_hierarchy_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="active")
            self.write_work_item(root, item_id="W-0002", status="active", parent="W-0001")
            self.append_active_index(root, "W-0001")
            self.append_active_index(root, "W-0002")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_decision_ref_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK014", finding_codes(findings))

    def test_decision_ref_must_link_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-9999")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK015", finding_codes(findings))

    def test_decision_status_must_be_known(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-0001", status="maybe")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK016", finding_codes(findings))

    def test_valid_decision_ref_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-0001")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def append_archive_index(self, root: Path, item_id: str, final: str) -> None:
        path = root / ".stage" / "past" / "work" / "archive" / "index.md"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {item_id} | {final} | [item](items/{item_id}.md) |\n")

    def archived_item(self, root: Path, **overrides) -> None:
        fields = dict(
            status="archived",
            verification="passed",
            retrospective="completed",
            retrospective_ref="R-0001",
            promotion="promoted",
            location="archive",
        )
        fields.update(overrides)
        self.write_work_item(root, **fields)
        self.write_archive_retrospective(root, retro_id="R-0001", work_item="W-0001")

    def test_archived_item_retrospective_resolves_in_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.archived_item(root)
            self.append_archive_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_archived_item_missing_from_archive_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.archived_item(root)

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE001", finding_codes(findings))

    def test_archive_index_final_status_must_be_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.archived_item(root)
            self.append_archive_index(root, "W-0001", "archived")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE002", finding_codes(findings))

    def test_archived_completed_item_requires_closed_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.archived_item(root, verification="pending")
            self.append_archive_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE003", finding_codes(findings))

    def test_archived_rejected_item_requires_completed_retrospective(self):
        # Rejection reasons are learning assets: rejected items archive with a
        # completed retrospective, like completed ones.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="archived",
                verification="pending",
                retrospective="pending",
                promotion="rejected",
                location="archive",
            )
            self.append_archive_index(root, "W-0001", "rejected")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE003", finding_codes(findings))

    def test_archive_index_row_requires_existing_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_archive_index(root, "W-9999", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE004", finding_codes(findings))

    def append_index_row(self, root: Path, relative: str, first_cell: str) -> None:
        path = root / ".stage" / relative
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {first_cell} | x | x | x | x |\n")

    def write_heading_record(self, root: Path, relative: str, record_id: str) -> Path:
        path = root / ".stage" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {record_id} Title\n\n## Purpose\n\nx\n", encoding="utf-8")
        return path

    def test_backlog_item_missing_from_backlog_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root)

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG008", finding_codes(findings))

    def test_indexed_backlog_item_has_no_index_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root)
            self.append_index_row(root, "future/backlog/index.md", "B-0001")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("BACKLOG008", finding_codes(findings))
        self.assertNotIn("BACKLOG009", finding_codes(findings))

    def test_backlog_index_row_requires_existing_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "future/backlog/index.md", "B-9999")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG009", finding_codes(findings))

    def test_milestone_missing_from_roadmap_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_heading_record(root, "future/roadmap/milestones/M-0001.md", "M-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ROADMAP001", finding_codes(findings))

    def test_roadmap_index_row_requires_existing_milestone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "future/roadmap/index.md", "M-9999")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ROADMAP002", finding_codes(findings))

    def test_roadmap_theme_rows_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "future/roadmap/index.md", "Foundations")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("ROADMAP002", finding_codes(findings))

    def test_proposal_missing_from_proposal_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_heading_record(root, "future/proposals/P-0001.md", "P-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("PROPOSAL001", finding_codes(findings))

    def test_proposal_index_row_requires_existing_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "future/proposals/index.md", "P-9999")

            findings = audit_stage.Audit(root).run()

        self.assertIn("PROPOSAL002", finding_codes(findings))

    def test_archived_item_retrospective_left_in_present_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="archived",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="promoted",
                location="archive",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK012", finding_codes(findings))

    def test_settings_without_schema_version_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings = root / ".stage" / "settings.json"
            data = json.loads(settings.read_text(encoding="utf-8"))
            del data["schema_version"]
            settings.write_text(json.dumps(data), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("SCHEMA001", finding_codes(findings))

    def test_settings_with_stale_schema_version_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings = root / ".stage" / "settings.json"
            data = json.loads(settings.read_text(encoding="utf-8"))
            data["schema_version"] = 0
            settings.write_text(json.dumps(data), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("SCHEMA001", finding_codes(findings))

    def test_template_schema_version_matches_plugin_constant(self):
        template = json.loads(
            (audit_stage.TEMPLATE_ROOT / "settings.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            audit_stage.stage_guard.STAGE_SCHEMA_VERSION, template.get("schema_version")
        )

    def test_decision_not_linked_back_is_reported(self):
        # decisions/README.md: `decision_refs` is optional, but a recorded
        # decision must link back.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")
            self.append_active_index(root, "W-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("DECISION002", finding_codes(findings))

    def test_decision_linked_back_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.append_active_index(root, "W-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("DECISION002", finding_codes(findings))

    def test_second_retrospective_claiming_completed_item_is_reported(self):
        # A completed item's retrospective_ref is THE binding: another R
        # claiming the same item is a silent contradiction.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.append_review_index(root, "W-0001", "completed")
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.write_retrospective(root, retro_id="R-0002", work_item="W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("RETRO002", finding_codes(findings))

    def test_retrospective_for_in_progress_item_is_allowed(self):
        # An R drafted before the item completes is a normal intermediate
        # state, not a contradiction.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")
            self.append_active_index(root, "W-0001")
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("RETRO002", finding_codes(findings))

    def test_backlog_status_must_be_known(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, status="someday")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG001", finding_codes(findings))

    def test_backlog_parent_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, item_id="B-0001", parent="B-9999")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG002", finding_codes(findings))

    def test_backlog_filename_must_start_with_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = root / ".stage" / "future" / "backlog" / "items" / "misnamed-item.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "---\nid: B-0001\ntitle: Test\nkind:\nparent:\nstatus: captured\npriority:\n---\n# B-0001\n",
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG003", finding_codes(findings))

    def test_legacy_backlog_item_without_frontmatter_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, frontmatter=False)

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_unknown_kind_without_criterion_is_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root, status="active")
            path.write_text(path.read_text(encoding="utf-8").replace("title: Test work", "title: Test work\nkind: marketing"), encoding="utf-8")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("KIND001", finding_codes(findings))

    def test_declared_kind_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root, status="active")
            path.write_text(path.read_text(encoding="utf-8").replace("title: Test work", "title: Test work\nkind: design"), encoding="utf-8")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("KIND001", finding_codes(findings))

    def test_removed_core_principles_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            principles = root / ".stage" / "past" / "canon" / "principles.md"
            principles.write_text("# Principles\n\nProject-only principles.\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("CANON001", finding_codes(findings))

    def test_work_source_must_reference_existing_backlog_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root, status="active")
            path.write_text(path.read_text(encoding="utf-8").replace("title: Test work", "title: Test work\nsource: B-9999"), encoding="utf-8")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK020", finding_codes(findings))

    def test_selected_backlog_without_realization_is_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, status="selected")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG004", finding_codes(findings))

    def test_backlog_realized_by_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_backlog_item(root, status="selected")
            path.write_text(path.read_text(encoding="utf-8").replace("realized_by:", "realized_by: W-9999") if "realized_by:" in path.read_text(encoding="utf-8") else path.read_text(encoding="utf-8").replace("priority:", "priority:\nrealized_by: W-9999"), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG005", finding_codes(findings))

    def test_decision_with_empty_principles_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-0001", principles="")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK021", finding_codes(findings))

    def test_decision_citing_no_known_principle_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active", decision_refs="DE-0001")
            self.write_decision(root, decision_id="DE-0001", work_item="W-0001", principles="Just vibes.")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK022", finding_codes(findings))

    def test_state_record_work_items_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            question = root / ".stage" / "present" / "state" / "questions" / "Q-0001.md"
            question.write_text("---\nid: Q-0001\ntitle: Q\nwork_items: W-9999\n---\n# Q-0001\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("STATE001", finding_codes(findings))

    def test_governance_allowlist_is_reported_as_narrowing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings = root / ".stage" / "settings.json"
            settings.write_text('{"governance": {"extensions": [".py"]}}', encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("GOV001", finding_codes(findings))

    def test_governance_excludes_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings = root / ".stage" / "settings.json"
            settings.write_text('{"governance": {"exclude_paths": ["notes"]}}', encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("GOV002", finding_codes(findings))

    def test_broken_governance_settings_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings = root / ".stage" / "settings.json"
            settings.write_text('{"governance": {', encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("GOV000", finding_codes(findings))

    def test_family_shape_violation_is_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            rogue = root / ".stage" / "present" / "work" / "retrospectives" / "notes.md"
            rogue.write_text("# free-form notes without frontmatter\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("FAMILY001", finding_codes(findings))

    def test_missing_template_file_is_warning_not_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            target = root / ".stage" / "operations" / "verification.md"
            target.unlink()

            findings = audit_stage.Audit(root).run()

        self.assertIn("TEMPLATE002", finding_codes(findings))
        self.assertEqual(["warning"], [finding.severity for finding in findings if finding.code == "TEMPLATE002"])


    def write_record(self, root: Path, relative: str, record_id: str, extra: str = "") -> Path:
        path = root / ".stage" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nid: {record_id}\ntitle: T\n{extra}---\n", encoding="utf-8")
        return path

    def test_record_outside_owning_location_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_record(root, "future/backlog/items/Q-00000001.md", "Q-00000001")

            findings = audit_stage.Audit(root).run()

        own = [finding for finding in findings if finding.code == "OWN001"]
        self.assertEqual(len(own), 1)
        self.assertEqual(own[0].severity, "error")
        self.assertIn("present/state/questions", own[0].message)

    def test_duplicate_record_id_across_files_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_record(root, "future/backlog/items/B-00000001.md", "B-00000001", "status: captured\n")
            self.write_record(root, "future/backlog/items/B-00000001-copy.md", "B-00000001", "status: captured\n")

            findings = audit_stage.Audit(root).run()

        self.assertEqual(
            len([finding for finding in findings if finding.code == "SSOT001"]), 2
        )

    def test_work_item_duplicates_stay_with_work007(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root)
            source = root / ".stage" / "present" / "work" / "items" / "W-0001.md"
            copy = root / ".stage" / "present" / "work" / "items" / "W-0001-copy.md"
            copy.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        codes = finding_codes(findings)
        self.assertIn("WORK007", codes)
        self.assertNotIn("SSOT001", codes)

    def test_unrouted_record_location_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            index_path = root / ".stage" / "index.md"
            text = index_path.read_text(encoding="utf-8")
            index_path.write_text(
                "\n".join(
                    line for line in text.splitlines() if "future/backlog/items/" not in line
                )
                + "\n",
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        route = [finding for finding in findings if finding.code == "ROUTE001"]
        self.assertEqual(len(route), 1)
        self.assertEqual(route[0].severity, "warning")
        self.assertIn("future/backlog/items", route[0].message)

    def test_unrouted_operations_document_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            extra = root / ".stage" / "operations" / "custom.md"
            extra.write_text("# Custom rules\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ROUTE002", finding_codes(findings))


    def test_body_only_record_id_is_audited_via_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = root / ".stage" / "future" / "backlog" / "items" / "P-00000001.md"
            path.write_text("# P-00000001 Misplaced proposal\n\n## Proposal\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        own = [finding for finding in findings if finding.code == "OWN001"]
        self.assertEqual(len(own), 1)
        self.assertIn("future/proposals", own[0].message)

    def test_unrouted_non_prefixed_family_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            index_path = root / ".stage" / "index.md"
            text = index_path.read_text(encoding="utf-8")
            index_path.write_text(
                "\n".join(
                    line for line in text.splitlines() if "future/roadmap/themes/" not in line
                )
                + "\n",
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        route = [finding for finding in findings if finding.code == "ROUTE001"]
        self.assertEqual(len(route), 1)
        self.assertIn("future/roadmap/themes", route[0].message)


    def test_one_sided_lineage_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-1")
            (root / ".stage/present/work/items/W-1.md").write_text(
                "---\nid: W-1\ntitle: t\nstatus: active\nverification: pending\n"
                "retrospective: pending\npromotion: pending\nscope:\nsource: B-1\n---\n# W-1\n",
                encoding="utf-8",
            )
            self.write_record(root, "future/backlog/items/B-1.md", "B-1",
                              "status: selected\nrealized_by: W-2\n")
            self.write_work_item(root, item_id="W-2")

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("WORK023", codes)
        self.assertIn("BACKLOG006", codes)

    def test_orphan_decision_and_retrospective_are_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_record(root, "present/work/retrospectives/R-9.md", "R-9", "work_item: W-999\n")
            (root / ".stage/present/work/decisions/DE-9.md").write_text(
                "---\nid: DE-9\nwork_item: W-999\nstatus: impossible\n---\n"
                "# DE-9\n\n## Principles applied\n\n",
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("RETRO001", codes)
        self.assertIn("DECISION001", codes)
        self.assertIn("WORK016", codes)
        self.assertIn("WORK021", codes)

    def test_directory_squatting_a_required_file_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            target = root / ".stage" / "operations" / "output.md"
            target.unlink()
            target.mkdir()

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("TEMPLATE003", codes)

    def test_routing_requires_exact_row_not_substring(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            index_path = root / ".stage" / "index.md"
            text = index_path.read_text(encoding="utf-8")
            index_path.write_text(
                "\n".join(line for line in text.splitlines() if "Proposal bodies" not in line) + "\n",
                encoding="utf-8",
            )

            route = [f for f in audit_stage.Audit(root).run() if f.code == "ROUTE001"]

        # future/proposals/ body route removed even though future/proposals/index.md remains.
        self.assertTrue(any("future/proposals" in f.message for f in route))


    def test_catalog_duplicate_prefix_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            catalog = root / ".stage" / "operations" / "artifacts.md"
            text = catalog.read_text(encoding="utf-8")
            catalog.write_text(
                text.replace(
                    "| `Q-` | Question | `present/state/questions/`",
                    "| `Q-` | Question | `present/state/wrong/` | Stale. |\n"
                    "| `Q-` | Question | `present/state/questions/`",
                ),
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("CATALOG001", codes)

    def test_catalog_extra_prefix_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            catalog = root / ".stage" / "operations" / "artifacts.md"
            text = catalog.read_text(encoding="utf-8")
            catalog.write_text(
                text.replace(
                    "| `M-` | Milestone |",
                    "| `Z-` | Zeta | `future/zeta/` | New family. |\n| `M-` | Milestone |",
                ),
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("CATALOG001", codes)

    def test_catalog_location_drift_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            catalog = root / ".stage" / "operations" / "artifacts.md"
            text = catalog.read_text(encoding="utf-8")
            catalog.write_text(
                text.replace("`present/state/questions/`", "`present/state/wrong/`"),
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("CATALOG001", codes)


if __name__ == "__main__":
    unittest.main()
