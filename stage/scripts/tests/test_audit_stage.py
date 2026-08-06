import importlib.util
import json
import shutil
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


def project_settings(root: Path) -> tuple[Path, dict]:
    settings_path, data, error = audit_stage.read_settings(root / ".stage")
    if error is not None:
        raise error
    if not isinstance(data, dict):
        raise AssertionError("test project settings must be an object")
    return settings_path, data


class StageAuditTest(unittest.TestCase):
    def init_stage(self, root: Path) -> None:
        init_stage.copy_templates(root, False)

    def init_v3_stage(self, root: Path) -> None:
        shutil.copytree(audit_stage.TEMPLATE_ROOT, root / ".stage")

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
        promotes: str = "",
        decision_refs: str = "",
        terminal_disposition: str = "",
    ) -> Path:
        if location == "present":
            base = root / ".stage" / "work" / "current"
        else:
            base = root / ".stage" / "official" / "work" / "archive" / "items"
        base.mkdir(parents=True, exist_ok=True)
        if parent:
            try:
                parent_path = self.find_work_item(root, parent)
            except AssertionError:
                parent_path = base / parent / "_epic.md"
            if parent_path.name == "_story.md" and parent_path.parent.parent == base:
                epic_path = parent_path.with_name("_epic.md")
                parent_path.replace(epic_path)
                parent_path = epic_path
            if parent_path.name == "_epic.md":
                path = parent_path.parent / item_id / "_story.md"
            elif parent_path.name == "_story.md":
                path = parent_path.parent / f"{item_id}.md"
            else:
                raise AssertionError(
                    f"action cannot parent another fixture: {parent_path}"
                )
        else:
            path = base / item_id / "_story.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        terminal_disposition_line = (
            f"terminal_disposition: {terminal_disposition}\n"
            if terminal_disposition
            else ""
        )
        path.write_text(
            (
                "---\n"
                f"id: {item_id}\n"
                "title: Test work\n"
                f"status: {status}\n"
                f"{terminal_disposition_line}"
                f"verification: {verification}\n"
                f"retrospective: {retrospective}\n"
                f"retrospective_ref: {retrospective_ref}\n"
                f"promotion: {promotion}\n"
                "scope:\n"
                f"promotes: {promotes}\n"
                f"decision_refs: {decision_refs}\n"
                "---\n"
                f"# {item_id} Test work\n"
                "\n## Purpose\n\nDeliver the requested outcome.\n"
                "\n## Success criteria\n\n- The user observes the requested outcome.\n"
            ),
            encoding="utf-8",
        )
        return path

    def find_work_item(self, root: Path, item_id: str) -> Path:
        for base in (
            root / ".stage/work/current",
            root / ".stage/work/planned",
            root / ".stage/official/work/archive/items",
        ):
            if not base.is_dir():
                continue
            for path in base.rglob("*.md"):
                if f"id: {item_id}\n" in path.read_text(encoding="utf-8"):
                    return path
        raise AssertionError(f"fixture work item not found: {item_id}")

    def write_archive_retrospective(self, root: Path, *, retro_id: str = "R-0001", work_item: str = "W-0001") -> Path:
        path = root / ".stage" / "official" / "work" / "archive" / "retrospectives" / f"{retro_id}.md"
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
        authorizes: str = "",
    ) -> Path:
        path = root / ".stage" / "decisions" / "pending" / f"{decision_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        authorizes_line = f"authorizes: {authorizes}\n" if authorizes else ""
        path.write_text(
            (
                f"---\nid: {decision_id}\nwork_item: {work_item}\nstatus: {status}\n"
                f"{authorizes_line}---\n"
                f"# {decision_id}\n\n## Question\n\nQ\n\n## Principles applied\n\n"
                f"{principles}\n\n## Chosen direction\n\nX\n"
            ),
            encoding="utf-8",
        )
        return path

    def write_backlog_item(self, root: Path, *, item_id: str = "W-0001", status: str = "captured", parent: str = "", frontmatter: bool = True) -> Path:
        base = root / ".stage" / "work" / "planned"
        if parent:
            try:
                parent_path = self.find_work_item(root, parent)
            except AssertionError:
                parent_path = base / parent / "_epic.md"
            if parent_path.name == "_story.md" and parent_path.parent.parent == base:
                epic_path = parent_path.with_name("_epic.md")
                parent_path.replace(epic_path)
                parent_path = epic_path
            if parent_path.name == "_epic.md":
                path = parent_path.parent / item_id / "_story.md"
            else:
                path = parent_path.parent / f"{item_id}.md"
        else:
            path = base / item_id / "_story.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if frontmatter:
            path.write_text(
                f"---\nid: {item_id}\ntitle: Test\nkind:\nstatus: {status}\npriority:\n---\n"
                f"# {item_id}\n\n## Purpose\n\nDeliver the requested outcome.\n\n"
                "## Success criteria\n\n- The user observes the requested outcome.\n",
                encoding="utf-8",
            )
        else:
            path.write_text(f"# {item_id} Legacy item\n\n## Status\n\n`captured`\n", encoding="utf-8")
        return path

    def test_audit_rejects_empty_purpose_on_current_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "## Purpose\n\nDeliver the requested outcome.\n",
                    "## Purpose\n\n",
                ),
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK028", finding_codes(findings))
        finding = next(finding for finding in findings if finding.code == "WORK028")
        self.assertIn("ask the human what they want to achieve", finding.message)

    def test_audit_rejects_empty_success_criteria_on_current_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "## Success criteria\n\n- The user observes the requested outcome.\n",
                    "## Success criteria\n\n",
                ),
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK029", finding_codes(findings))
        finding = next(finding for finding in findings if finding.code == "WORK029")
        self.assertIn("ask the human how they will know the work is done", finding.message)

    def test_audit_rejects_empty_outcomes_on_planned_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_backlog_item(root)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "## Purpose\n\nDeliver the requested outcome.\n",
                    "## Purpose\n\n",
                ).replace(
                    "## Success criteria\n\n- The user observes the requested outcome.\n",
                    "## Success criteria\n\n",
                ),
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG011", finding_codes(findings))
        self.assertIn("BACKLOG010", finding_codes(findings))

    def test_audit_warns_about_empty_outcomes_in_archived_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root, location="archive")
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "## Purpose\n\nDeliver the requested outcome.\n",
                    "## Purpose\n\n",
                ).replace(
                    "## Success criteria\n\n- The user observes the requested outcome.\n",
                    "## Success criteria\n\n",
                ),
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        outcome_findings = [
            finding
            for finding in findings
            if finding.code in {"WORK028", "WORK029"}
        ]
        self.assertEqual(
            [("warning", "WORK028"), ("warning", "WORK029")],
            [(finding.severity, finding.code) for finding in outcome_findings],
        )
        self.assertTrue(
            all(
                "do not invent a historical answer" in finding.message
                for finding in outcome_findings
            )
        )

    def write_retrospective(self, root: Path, *, retro_id: str = "R-0001", work_item: str = "W-0001") -> Path:
        path = root / ".stage" / "work" / "retrospectives" / f"{retro_id}.md"
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
        path = root / ".stage" / "work" / "active.md"
        target = self.find_work_item(root, item_id)
        link = target.relative_to(path.parent).as_posix()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"| {item_id} | test | active | ai | [item]({link}) |\n"
            )

    def append_review_index(self, root: Path, item_id: str, status: str = "review") -> None:
        path = root / ".stage" / "work" / "review.md"
        target = self.find_work_item(root, item_id)
        link = target.relative_to(path.parent).as_posix()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"| {item_id} | passed | completed | {status} | [item]({link}) |\n"
            )

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

    def test_completed_promoted_item_requires_declared_promotion_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="promoted",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK027", finding_codes(findings))

    def test_completed_promoted_item_requires_every_promoted_path_to_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="promoted",
                promotes=".stage/official/decisions/records/DE-0001.md",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK027", finding_codes(findings))

    def test_completed_approved_item_still_requires_promotion_when_paths_already_exist(self):
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
                promotes=".stage/official/decisions/index.md",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK027", finding_codes(findings))

    def test_completed_promoted_item_passes_when_every_promoted_path_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="promoted",
                promotes=".stage/official/decisions/index.md",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "promoted")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

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

    def test_archived_work_item_pending_intent_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                item_id="W-0001",
                status="archived",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="not_applicable",
                location="archive",
            )
            self.write_archive_retrospective(
                root,
                retro_id="R-0001",
                work_item="W-0001",
            )
            intents = root / ".stage/.runtime/intents"
            intents.mkdir(parents=True)
            archived_intent = intents / "W-0001--index.md-1111111111.json"
            archived_intent.write_text("{}\n", encoding="utf-8")
            active_intent = intents / "W-0002--index.md-2222222222.json"
            active_intent.write_text("{}\n", encoding="utf-8")

            findings = [
                finding
                for finding in audit_stage.Audit(root).run()
                if finding.code == "WORK025"
            ]

        self.assertEqual(1, len(findings))
        self.assertEqual("warning", findings[0].severity)
        self.assertIn("W-0001", findings[0].message)
        self.assertEqual(
            ".stage/.runtime/intents/W-0001--index.md-1111111111.json",
            findings[0].path,
        )

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
                promotion="not_applicable",
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
                promotion="not_applicable",
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
            retrospective = root / ".stage" / "work" / "retrospectives" / "R-0001.md"
            retrospective.write_text("# R-0001\n", encoding="utf-8")
            review = root / ".stage" / "work" / "review.md"
            with review.open("a", encoding="utf-8") as handle:
                handle.write("| W-0001 | pending | [R-0001](retrospectives/R-0001.md) | pending | [item](current/W-0001.md) |\n")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("INDEX002", finding_codes(findings))

    def test_active_prose_with_sha_like_text_is_not_treated_as_missing_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")
            active = root / ".stage" / "work" / "active.md"
            with active.open("a", encoding="utf-8") as handle:
                handle.write("\nA SHA-256 digest is not a work item ID.\n")
                handle.write("| W-0001 | test | active | ai | [item](current/W-0001.md) |\n")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("INDEX001", finding_codes(findings))

    def test_similar_item_id_link_does_not_satisfy_missing_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="active")
            active = root / ".stage" / "work" / "active.md"
            with active.open("a", encoding="utf-8") as handle:
                handle.write("| W-00012 | test | active | ai | [item](current/W-00012.md) |\n")

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
        message = next(
            finding.message for finding in findings if finding.code == "WORK017"
        )
        self.assertIn("no hierarchy location", message)
        self.assertNotIn("not found", message)

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
        message = next(
            finding.message for finding in findings if finding.code == "WORK019"
        )
        self.assertIn("finalized hierarchy location", message)

    def test_completed_parent_with_planned_child_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(
                root,
                item_id="W-0001",
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.append_review_index(root, "W-0001", "completed")
            self.write_backlog_item(
                root,
                item_id="W-0002",
                status="captured",
                parent="W-0001",
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("WORK024", finding_codes(findings))

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
            audit_stage.refresh_decision_index.refresh_index(root)

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def append_archive_index(self, root: Path, item_id: str, final: str) -> None:
        path = root / ".stage" / "official" / "work" / "archive" / "index.md"
        try:
            target = self.find_work_item(root, item_id)
            link = target.relative_to(path.parent).as_posix()
        except AssertionError:
            link = f"items/{item_id}/_story.md"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"| {item_id} | {final} | [item]({link}) |\n")

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

    def test_archived_hierarchy_requires_only_top_level_archive_index_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            records = (
                ("W-0001", "", "R-0001"),
                ("W-0002", "W-0001", "R-0002"),
                ("W-0003", "W-0002", "R-0003"),
            )
            for item_id, parent, retrospective_ref in records:
                self.write_work_item(
                    root,
                    item_id=item_id,
                    status="archived",
                    verification="passed",
                    retrospective="completed",
                    retrospective_ref=retrospective_ref,
                    promotion="promoted",
                    location="archive",
                    parent=parent,
                    terminal_disposition="accepted",
                )
                self.write_archive_retrospective(
                    root,
                    retro_id=retrospective_ref,
                    work_item=item_id,
                )
            self.append_archive_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_archive_index_allows_legacy_nested_hierarchy_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            records = (
                ("W-0001", "", "R-0001"),
                ("W-0002", "W-0001", "R-0002"),
            )
            for item_id, parent, retrospective_ref in records:
                self.write_work_item(
                    root,
                    item_id=item_id,
                    status="archived",
                    verification="passed",
                    retrospective="completed",
                    retrospective_ref=retrospective_ref,
                    promotion="promoted",
                    location="archive",
                    parent=parent,
                    terminal_disposition="accepted",
                )
                self.write_archive_retrospective(
                    root,
                    retro_id=retrospective_ref,
                    work_item=item_id,
                )
                self.append_archive_index(root, item_id, "completed")

            findings = audit_stage.Audit(root).run()

        self.assertEqual([], findings)

    def test_nested_archived_item_requires_terminal_disposition_without_index_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            records = (
                ("W-0001", "", "R-0001", "accepted"),
                ("W-0002", "W-0001", "R-0002", ""),
            )
            for item_id, parent, retrospective_ref, terminal_disposition in records:
                self.write_work_item(
                    root,
                    item_id=item_id,
                    status="archived",
                    verification="passed",
                    retrospective="completed",
                    retrospective_ref=retrospective_ref,
                    promotion="promoted",
                    location="archive",
                    parent=parent,
                    terminal_disposition=terminal_disposition,
                )
                self.write_archive_retrospective(
                    root,
                    retro_id=retrospective_ref,
                    work_item=item_id,
                )
            self.append_archive_index(root, "W-0001", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE002", finding_codes(findings))

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
                terminal_disposition="rejected",
            )
            self.append_archive_index(root, "W-0001", "rejected")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE003", finding_codes(findings))

    def test_archived_planned_rejection_needs_no_current_lifecycle_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            archived = (
                root
                / ".stage"
                / "official"
                / "work"
                / "archive"
                / "items"
                / "W-0001"
                / "_story.md"
            )
            archived.parent.mkdir(parents=True, exist_ok=True)
            archived.write_text(
                (
                    "---\n"
                    "id: W-0001\n"
                    "title: Rejected planned work\n"
                    "kind: fix\n"
                    "venue: codex\n"
                    "status: archived\n"
                    "terminal_disposition: rejected\n"
                    "review: not_required\n"
                    "---\n"
                    "# W-0001 Rejected planned work\n\n"
                    "Rejected before work started.\n"
                ),
                encoding="utf-8",
            )
            self.append_archive_index(root, "W-0001", "rejected")

            findings = audit_stage.Audit(root).run()

        unexpected_codes = {
            finding.code
            for finding in findings
            if finding.path.endswith(
                "official/work/archive/items/W-0001/_story.md"
            )
        } & {"ARCHIVE003", "WORK001", "WORK004", "WORK005", "WORK006"}
        self.assertEqual(set(), unexpected_codes)

    def test_archive_index_row_requires_existing_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_archive_index(root, "W-9999", "completed")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ARCHIVE004", finding_codes(findings))

    def test_record_archive_indexes_require_every_archived_record(self):
        fixtures = (
            (
                "official/decisions/archive/DE-0001.md",
                "---\nid: DE-0001\nwork_item: W-0001\nstatus: decided\n---\n# DE-0001\n",
            ),
            ("official/proposals/archive/P-0001.md", "# P-0001 Proposal\n"),
            (
                "official/state/archive/O-0001.md",
                "---\nid: O-0001\ntitle: Closed\nwork_items:\n---\n# O-0001 Closed\n",
            ),
        )
        for relative, content in fixtures:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.init_stage(root)
                path = root / ".stage" / relative
                path.write_text(content, encoding="utf-8")

                findings = audit_stage.Audit(root).run()

                self.assertIn("RECORD_ARCHIVE001", finding_codes(findings))

    def test_record_archive_indexes_reject_rows_without_records(self):
        indexes = (
            ("official/decisions/archive/index.md", "DE-9999"),
            ("official/proposals/archive/index.md", "P-9999"),
            ("official/state/archive/index.md", "O-9999"),
        )
        for relative, record_id in indexes:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.init_stage(root)
                self.append_index_row(root, relative, record_id)

                findings = audit_stage.Audit(root).run()

                self.assertIn("RECORD_ARCHIVE002", finding_codes(findings))

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
            self.append_index_row(root, "work/planned/index.md", "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("BACKLOG008", finding_codes(findings))
        self.assertNotIn("BACKLOG009", finding_codes(findings))

    def test_backlog_index_row_requires_existing_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "work/planned/index.md", "B-9999")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG009", finding_codes(findings))

    def test_milestone_missing_from_roadmap_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_heading_record(root, "roadmap/milestones/M-0001.md", "M-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ROADMAP001", finding_codes(findings))

    def test_roadmap_index_row_requires_existing_milestone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "roadmap/milestones/index.md", "M-9999")

            findings = audit_stage.Audit(root).run()

        self.assertIn("ROADMAP002", finding_codes(findings))

    def test_roadmap_theme_rows_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "roadmap/themes/index.md", "Foundations")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("ROADMAP002", finding_codes(findings))

    def test_proposal_missing_from_proposal_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_heading_record(root, "proposals/P-0001.md", "P-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("PROPOSAL001", finding_codes(findings))

    def test_proposal_index_row_requires_existing_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.append_index_row(root, "proposals/index.md", "P-9999")

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

    def test_audit_defaults_keep_missing_fields_empty(self):
        # Audit-side constructor policy: missing lifecycle fields stay empty
        # so every enum check fires (the gate-side policy is pinned in the
        # hooks suite).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            items = root / ".stage" / "work" / "current"
            (items / "W-0001.md").write_text(
                "---\nid: W-0001\ntitle: Sparse\nscope: src\n---\n# W-0001\n",
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        codes = finding_codes(findings)
        for code in ("WORK003", "WORK004", "WORK005", "WORK006"):
            self.assertIn(code, codes)

    def test_settings_without_schema_version_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings, data = project_settings(root)
            del data["schema_version"]
            settings.write_text(json.dumps(data), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("SCHEMA001", finding_codes(findings))

    def test_both_settings_names_are_reported_as_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            (root / ".stage" / "settings.json").write_text(
                '{"schema_version": 5}\n', encoding="utf-8"
            )

            findings = audit_stage.Audit(root).run()

        duplicate_findings = [
            finding
            for finding in findings
            if finding.severity == "error"
            and "settings.json" in finding.message
            and "settings.jsonc" in finding.message
        ]
        self.assertEqual(1, len(duplicate_findings))

    def test_settings_with_stale_schema_version_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings, data = project_settings(root)
            data["schema_version"] = 0
            settings.write_text(json.dumps(data), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("SCHEMA001", finding_codes(findings))

    def test_boolean_schema_version_is_flagged(self):
        # JSON `true` equals 1 in Python (bool is an int subclass) — the type
        # itself is part of the contract.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings, data = project_settings(root)
            data["schema_version"] = True
            settings.write_text(json.dumps(data), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("SCHEMA001", finding_codes(findings))

    def test_template_schema_version_matches_plugin_constant(self):
        _settings_path, template, error = audit_stage.read_settings(
            audit_stage.V4_TEMPLATE_ROOT
        )
        self.assertIsNone(error)
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

    def test_retrospective_id_collision_across_present_and_archive_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="active")
            self.write_work_item(root, item_id="W-0002", status="active")
            self.append_active_index(root, "W-0001")
            self.append_active_index(root, "W-0002")
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.write_archive_retrospective(
                root, retro_id="R-0001", work_item="W-0002"
            )

            findings = audit_stage.Audit(root).run()

        collisions = [finding for finding in findings if finding.code == "RETRO003"]
        self.assertEqual(len(collisions), 1)
        self.assertEqual(collisions[0].severity, "error")
        self.assertIn("R-0001", collisions[0].message)
        self.assertIn("W-0001", collisions[0].message)
        self.assertIn("W-0002", collisions[0].message)
        self.assertIn("official/work/archive/retrospectives/R-0001.md", collisions[0].path)
        self.assertNotIn("SSOT001", finding_codes(findings))

    def test_retrospective_id_may_not_repeat_for_same_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-0001", status="active")
            self.append_active_index(root, "W-0001")
            self.write_retrospective(root, retro_id="R-0001", work_item="W-0001")
            self.write_archive_retrospective(
                root, retro_id="R-0001", work_item="W-0001"
            )

            findings = audit_stage.Audit(root).run()

        self.assertIn("RETRO003", finding_codes(findings))

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
        message = next(
            finding.message for finding in findings if finding.code == "BACKLOG002"
        )
        self.assertIn("no hierarchy location", message)
        self.assertNotIn("not found", message)

    def test_backlog_parent_cycle_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, item_id="B-0001", parent="B-0002")
            self.write_backlog_item(root, item_id="B-0002", parent="B-0001")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG007", finding_codes(findings))

    def test_backlog_parent_chain_without_cycle_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, item_id="B-0001", parent="")
            self.write_backlog_item(root, item_id="B-0002", parent="B-0001")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("BACKLOG007", finding_codes(findings))

    def test_backlog_filename_must_start_with_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = root / ".stage" / "work" / "planned" / "misnamed-item.md"
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
            principles = root / ".stage" / "official" / "canon" / "principles.md"
            principles.write_text("# Principles\n\nProject-only principles.\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("CANON001", finding_codes(findings))

    def test_legacy_source_field_is_inert_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            path = self.write_work_item(root, status="active")
            path.write_text(path.read_text(encoding="utf-8").replace("title: Test work", "title: Test work\nsource: B-9999"), encoding="utf-8")
            self.append_active_index(root, "W-0001")

            findings = audit_stage.Audit(root).run()

        self.assertEqual(set(), finding_codes(findings) & {"WORK020", "WORK023"})

    def test_planned_card_may_be_selected_without_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, item_id="W-0042", status="selected")

            findings = audit_stage.Audit(root).run()

        self.assertEqual(
            set(),
            finding_codes(findings)
            & {"BACKLOG001", "BACKLOG004", "BACKLOG005", "WORK001"},
        )

    def test_open_status_in_backlog_column_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, item_id="W-0042", status="active")

            findings = audit_stage.Audit(root).run()

        self.assertIn("BACKLOG001", finding_codes(findings))

    def test_same_card_in_two_columns_is_ssot_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, status="active")
            self.append_active_index(root, "W-0001")
            self.write_backlog_item(root, item_id="W-0001", status="selected")

            findings = audit_stage.Audit(root).run()

        self.assertIn("SSOT001", finding_codes(findings))

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
            question = root / ".stage" / "state" / "questions" / "Q-0001.md"
            question.write_text("---\nid: Q-0001\ntitle: Q\nwork_items: W-9999\n---\n# Q-0001\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("STATE001", finding_codes(findings))

    def test_governance_allowlist_is_reported_as_narrowing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings, _data = project_settings(root)
            settings.write_text('{"governance": {"extensions": [".py"]}}', encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("GOV001", finding_codes(findings))

    def test_governance_excludes_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings, _data = project_settings(root)
            settings.write_text('{"governance": {"exclude_paths": ["notes"]}}', encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("GOV002", finding_codes(findings))

    def test_broken_governance_settings_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings, _data = project_settings(root)
            settings.write_text('{"governance": {', encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("GOV000", finding_codes(findings))

    def test_family_shape_violation_is_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            rogue = root / ".stage" / "work" / "retrospectives" / "notes.md"
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

    def test_english_guidance_in_korean_project_is_reported_as_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("state/current.md")
            target = root / ".stage" / relative
            target.write_bytes((init_stage.TEMPLATE_ROOT / relative).read_bytes())

            findings = audit_stage.Audit(root).run()

        stale = [finding for finding in findings if finding.code == "TEMPLATE004"]
        self.assertEqual(["warning"], [finding.severity for finding in stale])
        self.assertEqual([".stage/state/current.md"], [finding.path for finding in stale])
        self.assertIn("refresh_guidance.py", stale[0].message)

    def test_guidance_override_suppresses_stale_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("state/current.md")
            target = root / ".stage" / relative
            target.write_bytes((init_stage.TEMPLATE_ROOT / relative).read_bytes())
            settings_path, settings = project_settings(root)
            settings["guidance_overrides"] = [relative.as_posix()]
            settings_path.write_text(json.dumps(settings), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("TEMPLATE004", finding_codes(findings))

    def test_project_rows_in_template_empty_table_are_not_guidance_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            target = root / ".stage" / "work" / "active.md"
            lines = target.read_text(encoding="utf-8").splitlines()
            separator = next(
                index
                for index, line in enumerate(lines)
                if line.startswith("|---") or line.startswith("| ---")
            )
            lines.insert(
                separator + 1,
                "| W-00000001 | development | codex | Test | active | owner | [item](current/W-00000001.md) |",
            )
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertNotIn("TEMPLATE004", finding_codes(findings))

    def test_malformed_guidance_overrides_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            settings_path, settings = project_settings(root)
            settings["guidance_overrides"] = "state/current.md"
            settings_path.write_text(json.dumps(settings), encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        self.assertIn("TEMPLATE005", finding_codes(findings))


    def write_record(self, root: Path, relative: str, record_id: str, extra: str = "") -> Path:
        path = root / ".stage" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nid: {record_id}\ntitle: T\n{extra}---\n", encoding="utf-8")
        return path

    def test_record_outside_owning_location_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_record(root, "work/planned/Q-00000001.md", "Q-00000001")

            findings = audit_stage.Audit(root).run()

        own = [finding for finding in findings if finding.code == "OWN001"]
        self.assertEqual(len(own), 1)
        self.assertEqual(own[0].severity, "error")
        self.assertIn("state/questions", own[0].message)

    def test_closed_records_are_owned_by_their_archive_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            records = (
                ("official/decisions/archive/DE-00000001.md", "DE-00000001"),
                ("official/proposals/archive/P-00000001.md", "P-00000001"),
                ("official/state/archive/O-00000001.md", "O-00000001"),
                ("official/state/archive/Q-00000001.md", "Q-00000001"),
            )
            for relative, record_id in records:
                self.write_record(root, relative, record_id)

            findings = audit_stage.Audit(root).run()

        ownership_paths = {
            finding.path for finding in findings if finding.code == "OWN001"
        }
        for relative, _record_id in records:
            with self.subTest(relative=relative):
                self.assertNotIn(f".stage/{relative}", ownership_paths)

    def test_observation_question_and_proposal_require_status_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            records = (
                (
                    "state/observations/O-00000001.md",
                    "O-00000001",
                    "# O-00000001 Title\n\n## Observation\n\nValue.\n\n"
                    "## Evidence\n\nProof.\n\n## Impact\n\nImpact.\n\n"
                    "## Next action\n\nAct.\n",
                    "Status",
                ),
                (
                    "official/state/archive/O-00000002.md",
                    "O-00000002",
                    "# O-00000002 Title\n\n## Observation\n\nValue.\n\n"
                    "## Evidence\n\nProof.\n\n## Impact\n\nImpact.\n\n"
                    "## Next action\n\nAct.\n",
                    "Status",
                ),
                (
                    "state/questions/Q-00000001.md",
                    "Q-00000001",
                    "# Q-00000001 Title\n\n## Question\n\nWhy?\n\n"
                    "## Decision needed\n\nChoose.\n\n## Blocked work\n\nW.\n\n"
                    "## Answer owner\n\nOwner.\n",
                    "Status",
                ),
                (
                    "official/state/archive/Q-00000002.md",
                    "Q-00000002",
                    "# Q-00000002 Title\n\n## Question\n\nWhy?\n\n"
                    "## Decision needed\n\nChoose.\n\n## Blocked work\n\nW.\n\n"
                    "## Answer owner\n\nOwner.\n",
                    "Status",
                ),
                (
                    "proposals/P-00000001.md",
                    "P-00000001",
                    "# P-00000001 Title\n\n## Proposal\n\nChange.\n\n"
                    "## Purpose\n\nValue.\n\n## Alternatives\n\nNone.\n\n"
                    "## Cost\n\nLow.\n\n## Risks\n\nNone.\n\n"
                    "## Decision criteria\n\nCriteria.\n",
                    "Status",
                ),
                (
                    "official/proposals/archive/P-00000002.md",
                    "P-00000002",
                    "# P-00000002 Title\n\n## Proposal\n\nChange.\n\n"
                    "## Purpose\n\nValue.\n\n## Alternatives\n\nNone.\n\n"
                    "## Cost\n\nLow.\n\n## Risks\n\nNone.\n\n"
                    "## Decision criteria\n\nCriteria.\n",
                    "Status",
                ),
            )
            for relative, record_id, body, _missing in records:
                path = self.write_record(root, relative, record_id)
                path.write_text(
                    f"---\nid: {record_id}\ntitle: T\n---\n\n{body}",
                    encoding="utf-8",
                )

            findings = audit_stage.Audit(root).run()

        shape_findings = [finding for finding in findings if finding.code == "FAMILY002"]
        self.assertEqual(6, len(shape_findings))
        by_path = {finding.path: finding for finding in shape_findings}
        for relative, _record_id, _body, missing in records:
            with self.subTest(relative=relative):
                finding = by_path[f".stage/{relative}"]
                self.assertEqual("error", finding.severity)
                self.assertIn(f"`## {missing}`", finding.message)

    def test_duplicate_record_id_across_files_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_record(root, "work/planned/B-00000001.md", "B-00000001", "status: captured\n")
            self.write_record(root, "work/planned/B-00000001-copy.md", "B-00000001", "status: captured\n")

            findings = audit_stage.Audit(root).run()

        self.assertEqual(
            len([finding for finding in findings if finding.code == "SSOT001"]), 2
        )

    def test_same_decision_in_pending_and_archive_is_reported_as_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, decision_refs="DE-0001")
            self.append_active_index(root, "W-0001")
            source = self.write_decision(root, authorizes="venue_exception")
            audit_stage.refresh_decision_index.refresh_index(root)
            self.assertEqual([], audit_stage.Audit(root).run())

            destination = root / ".stage/official/decisions/archive" / source.name
            destination.write_bytes(source.read_bytes())
            archive_index = destination.parent / "index.md"
            with archive_index.open("a", encoding="utf-8") as handle:
                handle.write("| DE-0001 | venue exception consumed | [record](DE-0001.md) |\n")

            findings = audit_stage.Audit(root).run()

        duplicate_paths = {
            ".stage/decisions/pending/DE-0001.md",
            ".stage/official/decisions/archive/DE-0001.md",
        }
        duplicate_errors = [
            finding
            for finding in findings
            if finding.severity == "error"
            and finding.path in duplicate_paths
            and "DE-0001" in finding.message
        ]
        self.assertTrue(duplicate_errors)

    def test_work_item_duplicates_stay_with_work007(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root)
            source = self.find_work_item(root, "W-0001")
            copy = source.parent / "W-0001-copy.md"
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
                    line for line in text.splitlines() if "work/planned/" not in line
                )
                + "\n",
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        route = [finding for finding in findings if finding.code == "ROUTE001"]
        self.assertEqual(len(route), 1)
        self.assertEqual(route[0].severity, "warning")
        self.assertIn("work/planned", route[0].message)

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
            path = root / ".stage" / "work" / "planned" / "P-00000001.md"
            path.write_text("# P-00000001 Misplaced proposal\n\n## Proposal\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        own = [finding for finding in findings if finding.code == "OWN001"]
        self.assertEqual(len(own), 1)
        self.assertIn("proposals", own[0].message)

    def test_unrouted_non_prefixed_family_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            index_path = root / ".stage" / "index.md"
            text = index_path.read_text(encoding="utf-8")
            index_path.write_text(
                "\n".join(
                    line for line in text.splitlines() if "roadmap/themes/" not in line
                )
                + "\n",
                encoding="utf-8",
            )

            findings = audit_stage.Audit(root).run()

        route = [finding for finding in findings if finding.code == "ROUTE001"]
        self.assertEqual(len(route), 1)
        self.assertIn("roadmap/themes", route[0].message)


    def test_planned_card_parent_may_live_in_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, item_id="W-1", status="active")
            self.append_active_index(root, "W-1")
            self.write_backlog_item(root, item_id="W-2", status="captured", parent="W-1")

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertNotIn("BACKLOG002", codes)

    def test_planned_card_missing_parent_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_backlog_item(root, item_id="W-2", status="captured", parent="W-9999")

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("BACKLOG002", codes)

    def test_orphan_decision_and_retrospective_are_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_record(root, "work/retrospectives/R-9.md", "R-9", "work_item: W-999\n")
            (root / ".stage/decisions/pending/DE-9.md").write_text(
                "---\nid: DE-9\nwork_item: W-999\nstatus: impossible\n---\n"
                "# DE-9\n\n## Principles applied\n\n",
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("RETRO001", codes)
        self.assertIn("DECISION001", codes)
        self.assertIn("WORK016", codes)
        self.assertIn("WORK021", codes)

    def test_pending_decision_index_drift_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, decision_refs="DE-0001")
            self.append_active_index(root, "W-0001")
            self.write_decision(root)

            findings = audit_stage.Audit(root).run()

        drift = [finding for finding in findings if finding.code == "DECISION004"]
        self.assertEqual(["error"], [finding.severity for finding in drift])
        self.assertIn("refresh_decision_index.py", drift[0].message)

    def test_generated_pending_decision_index_passes_sync_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_work_item(root, decision_refs="DE-0001")
            self.append_active_index(root, "W-0001")
            self.write_decision(root)
            audit_stage.refresh_decision_index.refresh_index(root)

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertNotIn("DECISION004", codes)

    def test_unrecognized_pending_decision_index_shape_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            index = root / ".stage/decisions/index.md"
            index.write_text("# Custom\n\n| Name | Note |\n|---|---|\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        drift = [finding for finding in findings if finding.code == "DECISION004"]
        self.assertEqual(["error"], [finding.severity for finding in drift])
        self.assertIn("cannot be derived", drift[0].message)

    def test_directory_squatting_a_required_file_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            target = root / ".stage" / "operations" / "verification.md"
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
                "\n".join(
                    line.replace("`proposals/`", "proposals/")
                    for line in text.splitlines()
                    if "Proposal bodies" not in line
                )
                + "\n",
                encoding="utf-8",
            )

            route = [f for f in audit_stage.Audit(root).run() if f.code == "ROUTE001"]

        # proposals/ body route removed even though proposals/index.md remains.
        self.assertTrue(any("proposals" in f.message for f in route))


    def test_catalog_duplicate_prefix_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            # A project copy of the plugin-owned catalog takes precedence in
            # the sync check, so seed one from the plugin and mutate it.
            catalog = root / ".stage" / "operations" / "artifacts.md"
            text = (audit_stage.PLUGIN_ROOT / "operations" / "artifacts.md").read_text(
                encoding="utf-8"
            )
            catalog.write_text(
                text.replace(
                    "| `Q-` | Question | `state/questions/`",
                    "| `Q-` | Question | `state/wrong/` | Stale. |\n"
                    "| `Q-` | Question | `state/questions/`",
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
            text = (audit_stage.PLUGIN_ROOT / "operations" / "artifacts.md").read_text(
                encoding="utf-8"
            )
            catalog.write_text(
                text.replace(
                    "| `M-` | Milestone |",
                    "| `Z-` | Zeta | `zeta/` | New family. |\n| `M-` | Milestone |",
                ),
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("CATALOG001", codes)

    def test_catalog_representative_location_drift_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            catalog = root / ".stage" / "operations" / "artifacts.md"
            text = (audit_stage.PLUGIN_ROOT / "operations" / "artifacts.md").read_text(
                encoding="utf-8"
            )
            catalog.write_text(
                text.replace("`work/current/`", "`work/planned/`"),
                encoding="utf-8",
            )

            codes = finding_codes(audit_stage.Audit(root).run())

        self.assertIn("CATALOG001", codes)


class LanguageSettingAuditTest(unittest.TestCase):
    def init_stage(self, root: Path) -> None:
        init_stage.copy_templates(root, False)

    def set_language(self, root: Path, value) -> None:
        settings_path, data = project_settings(root)
        data["language"] = value
        settings_path.write_text(json.dumps(data), encoding="utf-8")

    def lang_findings(self, root: Path):
        return [f for f in audit_stage.Audit(root).run() if f.code == "LANG001"]

    def test_valid_and_missing_language_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.assertEqual([], self.lang_findings(root))
            self.set_language(root, "ko")
            self.assertEqual([], self.lang_findings(root))

    def test_malformed_language_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            for bad in ("KO", "", 3, True, ["ko"]):
                with self.subTest(value=bad):
                    self.set_language(root, bad)
                    findings = self.lang_findings(root)
                    self.assertEqual(["warning"], [f.severity for f in findings])


class InitLanguageTest(unittest.TestCase):
    def test_default_init_is_english_with_explicit_setting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False)
            _settings_path, settings = project_settings(root)
            index = (root / ".stage" / "index.md").read_text(encoding="utf-8")

        self.assertEqual("en", settings["language"])
        self.assertIn("# Stage Index", index)

    def test_korean_init_localizes_prose_and_keeps_machine_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            stage_root = root / ".stage"
            _settings_path, settings = project_settings(root)
            index = (stage_root / "index.md").read_text(encoding="utf-8")
            verification = (stage_root / "operations" / "verification.md").read_text(
                encoding="utf-8"
            )
            template = (stage_root / "work" / "current" / "_template.md").read_text(
                encoding="utf-8"
            )
            findings = audit_stage.Audit(root).run()

        self.assertEqual("ko", settings["language"])
        self.assertEqual(
            audit_stage.stage_guard.STAGE_SCHEMA_VERSION, settings["schema_version"]
        )
        self.assertIn("# Stage 인덱스", index)
        self.assertIn("`official/canon/principles.md`", index)
        # kind tokens stay language-neutral in the localized criteria table.
        self.assertIn("| planning |", verification)
        # Record skeletons are locale-invariant machine contracts.
        self.assertIn("## Purpose", template)
        self.assertEqual([], [f for f in findings if f.severity == "error"])
        self.assertEqual(set(), finding_codes(findings) & {"LANG001", "SCHEMA001"})

    def test_unbundled_locale_falls_back_to_english_but_keeps_setting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="fr")
            stage_root = root / ".stage"
            _settings_path, settings = project_settings(root)
            index = (stage_root / "index.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertEqual("fr", settings["language"])
        self.assertIn("# Stage Index", index)
        self.assertEqual([], [f for f in findings if f.severity == "error"])

    def test_file_sets_are_identical_across_languages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root_en = Path(tmp) / "en"
            root_ko = Path(tmp) / "ko"
            root_en.mkdir()
            root_ko.mkdir()
            init_stage.copy_templates(root_en, False)
            init_stage.copy_templates(root_ko, False, language="ko")
            files_en = sorted(
                p.relative_to(root_en).as_posix()
                for p in (root_en / ".stage").rglob("*")
                if p.is_file()
            )
            files_ko = sorted(
                p.relative_to(root_ko).as_posix()
                for p in (root_ko / ".stage").rglob("*")
                if p.is_file()
            )

        self.assertEqual([p.replace("en/", "ko/", 1) for p in files_en], files_ko)


class VenueRoutingAuditTest(unittest.TestCase):
    """DE-00000004: a declared kind -> venue role policy is audited; no policy
    means venue stays fully advisory with zero findings."""

    def init_stage(self, root: Path) -> None:
        init_stage.copy_templates(root, False)

    def declare_routing(self, root: Path, routing) -> None:
        settings_path, data = project_settings(root)
        data["venue_routing"] = routing
        settings_path.write_text(json.dumps(data), encoding="utf-8")

    def write_item(self, root: Path, *, kind: str, venue: str, decision_refs: str = "") -> Path:
        path = (
            root
            / ".stage"
            / "work"
            / "current"
            / "W-0001"
            / "_story.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                "---\n"
                "id: W-0001\n"
                "title: Test\n"
                f"kind: {kind}\n"
                f"venue: {venue}\n"
                "status: active\n"
                "verification: pending\n"
                "retrospective: pending\n"
                "promotion: pending\n"
                "scope: src\n"
                f"decision_refs: {decision_refs}\n"
                "---\n"
                "# W-0001 Test\n"
            ),
            encoding="utf-8",
        )
        return path

    def venue_codes(self, root: Path) -> set[str]:
        return {
            f.code for f in audit_stage.Audit(root).run() if f.code.startswith("VENUE")
        }

    ROUTING = {"design": "claude", "development": "codex"}

    def test_no_policy_reports_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_item(root, kind="design", venue="")
            self.assertEqual(set(), self.venue_codes(root))

    def test_missing_venue_on_routed_kind_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            self.write_item(root, kind="design", venue="")
            self.assertIn("VENUE001", self.venue_codes(root))

    def test_missing_venue_on_unrouted_kind_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            self.write_item(root, kind="chore", venue="")
            self.assertEqual(set(), self.venue_codes(root))

    def test_unknown_venue_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            self.write_item(root, kind="design", venue="cursor")
            self.assertIn("VENUE002", self.venue_codes(root))

    def write_exception_decision(
        self, root: Path, *, decision_id: str = "DE-0001", work_item: str = "W-0001",
        status: str = "decided", authorizes: str = "venue_exception",
    ) -> None:
        decisions = root / ".stage" / "decisions" / "pending"
        decisions.mkdir(parents=True, exist_ok=True)
        lines = ["---", f"id: {decision_id}", f"work_item: {work_item}", f"status: {status}"]
        if authorizes:
            lines.append(f"authorizes: {authorizes}")
        lines += [
            "---",
            f"# {decision_id} Exception",
            "",
            "## Principles applied",
            "",
            "- SSOT — one owner.",
            "",
        ]
        (decisions / f"{decision_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def test_policy_contradiction_without_decision_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            self.write_item(root, kind="development", venue="claude")
            findings = [f for f in audit_stage.Audit(root).run() if f.code == "VENUE003"]
        self.assertEqual(["error"], [f.severity for f in findings])

    def test_valid_exception_decision_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            self.write_exception_decision(root)
            self.write_item(root, kind="development", venue="claude", decision_refs="DE-0001")
            codes = self.venue_codes(root)
        self.assertNotIn("VENUE003", codes)

    def test_open_or_non_authorizing_decision_does_not_excuse(self):
        for kwargs in ({"status": "open"}, {"authorizes": ""}):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.init_stage(root)
                self.declare_routing(root, self.ROUTING)
                self.write_exception_decision(root, **kwargs)
                self.write_item(
                    root, kind="development", venue="claude", decision_refs="DE-0001"
                )
                with self.subTest(**kwargs):
                    self.assertIn("VENUE003", self.venue_codes(root))

    def test_split_kind_single_item_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, {"feature": "split", "design": "claude"})
            self.write_item(root, kind="feature", venue="claude")
            findings = [f for f in audit_stage.Audit(root).run() if f.code == "VENUE005"]
        self.assertEqual(["error"], [f.severity for f in findings])

    def test_split_kind_with_valid_exception_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, {"feature": "split", "design": "claude"})
            self.write_exception_decision(root)
            self.write_item(root, kind="feature", venue="claude", decision_refs="DE-0001")
            codes = self.venue_codes(root)
        self.assertNotIn("VENUE005", codes)

    def test_split_token_is_not_a_declared_venue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, {"feature": "split", "design": "claude"})
            self.write_item(root, kind="design", venue="split")
            self.assertIn("VENUE002", self.venue_codes(root))

    def test_matching_venue_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            self.write_item(root, kind="design", venue="claude")
            self.assertEqual(set(), self.venue_codes(root))

    def test_malformed_routing_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            for bad in (["design"], {"design": 3}, {"": "claude"}, "claude"):
                with self.subTest(value=bad):
                    self.declare_routing(root, bad)
                    findings = [
                        f for f in audit_stage.Audit(root).run() if f.code == "VENUE004"
                    ]
                    self.assertEqual(["error"], [f.severity for f in findings])

    def test_archived_items_are_not_judged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.declare_routing(root, self.ROUTING)
            path = root / ".stage" / "official" / "work" / "archive" / "items" / "W-0001.md"
            path.write_text(
                (
                    "---\n"
                    "id: W-0001\n"
                    "title: Old\n"
                    "kind: development\n"
                    "venue: claude\n"
                    "status: archived\n"
                    "verification: passed\n"
                    "retrospective: completed\n"
                    "retrospective_ref: R-0001\n"
                    "promotion: not_applicable\n"
                    "scope: src\n"
                    "---\n"
                    "# W-0001 Old\n"
                ),
                encoding="utf-8",
            )
            (root / ".stage" / "official" / "work" / "archive" / "retrospectives").mkdir(
                parents=True, exist_ok=True
            )
            (
                root / ".stage" / "official" / "work" / "archive" / "retrospectives" / "R-0001.md"
            ).write_text("---\nid: R-0001\nwork_item: W-0001\n---\n# R-0001\n", encoding="utf-8")

            self.assertEqual(set(), self.venue_codes(root))


class OpenDecisionCompletionTest(unittest.TestCase):
    """DE-00000005: finished work must not rest on undecided decisions."""

    def init_stage(self, root: Path) -> None:
        init_stage.copy_templates(root, False)

    def write_completed_item(self, root: Path, *, decision_refs: str) -> None:
        path = root / ".stage" / "work" / "current" / "W-0001.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                "---\n"
                "id: W-0001\n"
                "title: Done\n"
                "kind: chore\n"
                "status: completed\n"
                "verification: passed\n"
                "retrospective: completed\n"
                "retrospective_ref: R-0001\n"
                "promotion: not_applicable\n"
                "scope: src\n"
                f"decision_refs: {decision_refs}\n"
                "---\n"
                "# W-0001 Done\n"
            ),
            encoding="utf-8",
        )
        retro = root / ".stage" / "work" / "retrospectives" / "R-0001.md"
        retro.parent.mkdir(parents=True, exist_ok=True)
        retro.write_text("---\nid: R-0001\nwork_item: W-0001\n---\n# R-0001\n", encoding="utf-8")

    def write_decision(self, root: Path, *, status: str) -> None:
        path = root / ".stage" / "decisions" / "pending" / "DE-0001.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                "---\nid: DE-0001\nwork_item: W-0001\n"
                f"status: {status}\n---\n# DE-0001\n\n"
                "## Principles applied\n\n- SSOT — one owner.\n"
            ),
            encoding="utf-8",
        )

    def codes(self, root: Path) -> set[str]:
        return finding_codes(audit_stage.Audit(root).run())

    def test_completed_item_with_open_decision_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_decision(root, status="open")
            self.write_completed_item(root, decision_refs="DE-0001")
            findings = [f for f in audit_stage.Audit(root).run() if f.code == "DECISION003"]
        self.assertEqual(["error"], [f.severity for f in findings])

    def test_completed_item_with_decided_decision_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_decision(root, status="decided")
            self.write_completed_item(root, decision_refs="DE-0001")
            self.assertNotIn("DECISION003", self.codes(root))

    def test_open_decision_on_open_item_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.write_decision(root, status="open")
            path = root / ".stage" / "work" / "current" / "W-0001.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                (
                    "---\nid: W-0001\ntitle: Working\nkind: chore\nstatus: active\n"
                    "verification: pending\nretrospective: pending\npromotion: pending\n"
                    "scope: src\ndecision_refs: DE-0001\n---\n# W-0001 Working\n"
                ),
                encoding="utf-8",
            )
            self.assertNotIn("DECISION003", self.codes(root))


class OperationsOwnershipTest(unittest.TestCase):
    """DE-00000002: common operations docs are plugin-owned; the project
    carries only its policy surface plus declared overrides."""

    def init_stage(self, root: Path) -> None:
        init_stage.copy_templates(root, False)

    def set_settings(self, root: Path, **updates):
        settings_path, data = project_settings(root)
        data.update(updates)
        settings_path.write_text(json.dumps(data), encoding="utf-8")

    def ops_codes(self, root: Path) -> set[str]:
        return {
            finding.code
            for finding in audit_stage.Audit(root).run()
            if finding.code.startswith("OPS")
        }

    def test_fresh_init_copies_no_common_docs_and_audits_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            operations = sorted(
                path.name for path in (root / ".stage" / "operations").glob("*.md")
            )
            findings = audit_stage.Audit(root).run()

        self.assertEqual(["verification.md"], operations)
        self.assertEqual(set(), {f.code for f in findings if f.severity == "error"})
        self.assertEqual(set(), finding_codes(findings) & {"OPS001", "OPS002", "SCHEMA001"})

    def test_identical_shadow_copy_is_stale_duplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            plugin_doc = audit_stage.PLUGIN_ROOT / "operations" / "during.md"
            shadow = root / ".stage" / "operations" / "during.md"
            shadow.write_bytes(plugin_doc.read_bytes())

            findings = audit_stage.Audit(root).run()

        ops1 = [f for f in findings if f.code == "OPS001"]
        self.assertEqual(["warning"], [f.severity for f in ops1])
        self.assertNotIn("OPS002", finding_codes(findings))

    def test_undeclared_differing_shadow_is_ownership_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            shadow = root / ".stage" / "operations" / "during.md"
            shadow.write_text("# During\n\nProject-edited body.\n", encoding="utf-8")

            findings = audit_stage.Audit(root).run()

        ops2 = [f for f in findings if f.code == "OPS002"]
        self.assertEqual(["error"], [f.severity for f in ops2])

    def test_declared_override_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            shadow = root / ".stage" / "operations" / "during.md"
            shadow.write_text("# During\n\nProject-edited body.\n", encoding="utf-8")
            self.set_settings(root, operations_overrides=["during.md"])

            self.assertEqual(set(), self.ops_codes(root))

    def test_declared_override_without_file_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.set_settings(root, operations_overrides=["during.md"])

            self.assertIn("OPS003", self.ops_codes(root))

    def test_malformed_and_unknown_overrides_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            self.set_settings(root, operations_overrides="during.md")
            self.assertIn("OPS004", self.ops_codes(root))

            self.set_settings(root, operations_overrides=["nonexistent.md"])
            self.assertIn("OPS004", self.ops_codes(root))

            # verification.md is the project policy surface, not an override.
            self.set_settings(root, operations_overrides=["verification.md"])
            self.assertIn("OPS004", self.ops_codes(root))

    def test_v1_layout_gets_schema_warning_but_no_drift_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_stage(root)
            for name, path in audit_stage.Audit(root).plugin_common_docs().items():
                (root / ".stage" / "operations" / name).write_bytes(path.read_bytes())
            self.set_settings(root, schema_version=1)

            findings = audit_stage.Audit(root).run()

        self.assertIn("SCHEMA001", finding_codes(findings))
        self.assertEqual(set(), finding_codes(findings) & {"OPS001", "OPS002"})


if __name__ == "__main__":
    unittest.main()
