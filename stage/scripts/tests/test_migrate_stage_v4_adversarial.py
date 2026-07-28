"""Adversarial external-project QA for the schema-v3 to schema-v4 migration."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
SCRIPT_ROOT = STAGE_ROOT / "scripts"
V3_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "project-stage"
V3_LOCALE_ROOT = STAGE_ROOT / "templates" / "locales"
ROADMAP = STAGE_ROOT / "skills" / "stage-roadmap" / "manage_roadmap.py"
REGISTER = STAGE_ROOT / "skills" / "stage-work" / "register_work.py"
START = SCRIPT_ROOT / "start_work.py"
CLOSE = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ARCHIVE = STAGE_ROOT / "skills" / "stage-archive" / "archive_work.py"
AUDIT = SCRIPT_ROOT / "audit_stage.py"
for import_root in (HOOK_ROOT, SCRIPT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


migrate_stage = load_module(
    "migrate_stage_v4_adversarial", SCRIPT_ROOT / "migrate_stage.py"
)
import stage_guard  # noqa: E402
import stage_records  # noqa: E402


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    )


def make_v3_project(root: Path, *, language: str = "en") -> Path:
    shutil.copytree(V3_TEMPLATE_ROOT, root / ".stage")
    stage_root = root / ".stage"
    locale_root = V3_LOCALE_ROOT / language
    if language != "en" and locale_root.is_dir():
        for source in locale_root.rglob("*"):
            if not source.is_file():
                continue
            target = stage_root / source.relative_to(locale_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    settings_path = stage_root / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    settings["schema_version"] = 3
    settings["language"] = language
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "config", "user.email", "stage-test@example.com")
    git(root, "config", "user.name", "Stage Test")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "v3 adversarial fixture")
    return stage_root


def commit_all(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)


def stage_tree(stage_root: Path) -> dict[str, tuple[str, bytes | str]]:
    entries: dict[str, tuple[str, bytes | str]] = {}
    for path in sorted(stage_root.rglob("*")):
        relative = path.relative_to(stage_root).as_posix()
        if path.is_symlink():
            entries[relative] = ("symlink", os.readlink(path))
        elif path.is_file():
            entries[relative] = ("file", path.read_bytes())
        elif path.is_dir():
            entries[relative] = ("directory", "")
    return entries


def run_migrate(
    root: Path, *, dry_run: bool = False, abort: bool = False
) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output):
        code = migrate_stage.abort(root) if abort else migrate_stage.migrate(root, dry_run)
    return code, output.getvalue()


def run_tool(cli: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    if cli == REGISTER and "--scale" not in args:
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


class MigrationAdversarialFixture(unittest.TestCase):
    def assert_audit_errors(
        self,
        root: Path,
        expected: list[tuple[str, str]],
    ) -> None:
        result = run_tool(AUDIT, root, "--format", "json")
        payload = json.loads(result.stdout)
        actual = [
            (finding["code"], finding["path"])
            for finding in payload["findings"]
            if finding["code"] != "TEMPLATE004"
        ]
        self.assertEqual(expected, actual)

    def assert_audit_clean(self, root: Path) -> None:
        result = run_tool(AUDIT, root, "--format", "json")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        unexpected = [
            finding
            for finding in payload["findings"]
            if finding["code"] != "TEMPLATE004"
        ]
        self.assertEqual([], unexpected)

    def migrate_successfully(self, root: Path, *, commit: bool = False) -> str:
        code, output = run_migrate(root)
        self.assertEqual(0, code, output)
        if commit:
            git(root, "commit", "-qm", "migrate fixture to schema v4")
        self.assert_audit_clean(root)
        return output

    def write_active_work(self, stage_root: Path, decision_refs: str) -> Path:
        path = stage_root / "present/work/items/W-00000001.md"
        path.write_text(
            "---\n"
            "id: W-00000001\n"
            "title: Contract X migration fixture\n"
            "kind: development\n"
            "venue: codex\n"
            "parent:\n"
            "source:\n"
            "status: active\n"
            "verification: pending\n"
            "retrospective: pending\n"
            "retrospective_ref:\n"
            "promotion: pending\n"
            "review: not_required\n"
            "scope: src\n"
            "promotes:\n"
            f"decision_refs: {decision_refs}\n"
            "---\n\n"
            "# W-00000001 Contract X migration fixture\n\n"
            "## Purpose\n\nPreserve legacy and stable decision identity.\n\n"
            "## Scope\n\n\n## Success criteria\n\n\n## Related truth\n\n"
            "## Progress\n\n\n## Verification\n\n\n## Retrospective\n\n"
            "## Promotion decision\n",
            encoding="utf-8",
        )
        active = stage_root / "present/work/active.md"
        active.write_text(
            active.read_text(encoding="utf-8")
            + "| W-00000001 | development | codex | Contract X | active | codex | "
            "[item](items/W-00000001.md) |\n",
            encoding="utf-8",
        )
        return path


class MigrationPreflightAdversarialTest(MigrationAdversarialFixture):
    def test_runtime_dirt_is_exempt_but_pending_intents_reach_the_specific_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_v3_project(root)
            cache = stage_root / ".runtime/cache/session.txt"
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text("ephemeral\n", encoding="utf-8")

            code, output = run_migrate(root, dry_run=True)
            self.assertEqual(0, code, output)
            self.assertEqual("ephemeral\n", cache.read_text(encoding="utf-8"))

            intent = stage_root / ".runtime/intents/W-00000001.json"
            intent.parent.mkdir(parents=True, exist_ok=True)
            intent.write_text("{}\n", encoding="utf-8")
            code, output = run_migrate(root, dry_run=True)

        self.assertEqual(1, code)
        self.assertIn("pending promotion machinery", output.lower())
        self.assertNotIn("dirty git working tree", output.lower())


class MigrationAbortAdversarialTest(MigrationAdversarialFixture):
    def test_abort_after_mid_relocation_failure_restores_exact_committed_v3_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_v3_project(root)
            runtime_cache = stage_root / ".runtime/cache/session.txt"
            runtime_cache.parent.mkdir(parents=True, exist_ok=True)
            runtime_cache.write_text("preserve external runtime state\n", encoding="utf-8")
            (stage_root / ".runtime/existing-empty").mkdir()
            before = stage_tree(stage_root)
            before_status = git(root, "status", "--porcelain").stdout
            with patch.object(
                migrate_stage.v4_migration,
                "rewrite_moved_markdown",
                side_effect=migrate_stage.v4_migration.MigrationError(
                    "injected interruption after relocation"
                ),
            ):
                code, output = run_migrate(root)

            self.assertEqual(1, code)
            self.assertIn("injected interruption", output)
            self.assertTrue(
                (stage_root / ".runtime/schema-v4-maintenance.json").is_file()
            )
            self.assertTrue((stage_root / "official").is_dir())

            abort_code, abort_output = run_migrate(root, abort=True)
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )

            self.assertEqual(0, abort_code, abort_output)
            self.assertEqual(before, stage_tree(stage_root))
            self.assertEqual(3, settings["schema_version"])
            self.assertTrue((stage_root / "past").is_dir())
            self.assertTrue((stage_root / "present").is_dir())
            self.assertTrue((stage_root / "future").is_dir())
            for retired in ("official", "work", "decisions", "state", "proposals", "roadmap"):
                self.assertFalse((stage_root / retired).exists(), retired)
            self.assertFalse(
                (stage_root / ".runtime/schema-v4-maintenance.json").exists()
            )
            self.assertFalse(
                (stage_root / ".runtime/schema-v4-migration-journal.json").exists()
            )
            self.assertEqual(before_status, git(root, "status", "--porcelain").stdout)


class MigrationContentAdversarialTest(MigrationAdversarialFixture):
    def test_hand_edited_operations_doc_and_custom_governed_file_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_v3_project(root)
            operations = stage_root / "operations/verification.md"
            operations.write_text(
                operations.read_text(encoding="utf-8")
                + "\n## Project-specific evidence\n\n"
                "Keep this owner-authored verification policy byte-for-byte.\n",
                encoding="utf-8",
            )
            custom = stage_root / "future/proposals/customer-runbook.md"
            custom_content = (
                "# Customer runbook\n\n외부 프로젝트의 사용자 정의 내용.\n"
            )
            custom.write_bytes(custom_content.encode("utf-8"))
            expected_operations = operations.read_bytes()
            expected_custom = custom.read_bytes()
            commit_all(root, "add hand-edited governed content")

            self.migrate_successfully(root)

            self.assertEqual(expected_operations, operations.read_bytes())
            self.assertEqual(
                expected_custom,
                (stage_root / "proposals/customer-runbook.md").read_bytes(),
            )
            self.assertFalse((stage_root / "future/proposals/customer-runbook.md").exists())

    def test_korean_locale_migrates_with_korean_prose_and_indexes_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_v3_project(root, language="ko")
            original_principles = (stage_root / "past/canon/principles.md").read_text(
                encoding="utf-8"
            )

            self.migrate_successfully(root)

            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            migrated_principles = (
                stage_root / "official/canon/principles.md"
            ).read_text(encoding="utf-8")
            decisions_index = (stage_root / "decisions/index.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual("ko", settings["language"])
            self.assertIn("이 문서는 이 프로젝트의 안정적 원칙", original_principles)
            self.assertIn("이 문서는 이 프로젝트의 안정적 원칙", migrated_principles)
            self.assertIn("대기 중 결정", decisions_index)
            self.assertIn("## 수명주기", (stage_root / "index.md").read_text(encoding="utf-8"))

    def test_contract_x_legacy_d_and_stable_de_references_survive_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_v3_project(root)
            legacy_id = "D-00000001"
            stable_id = "DE-00000002"
            work = self.write_active_work(
                stage_root,
                f".stage/past/decisions/records/{legacy_id}.md, "
                f".stage/present/work/decisions/{stable_id}.md",
            )
            legacy = stage_root / f"past/decisions/records/{legacy_id}.md"
            legacy.write_text(
                "---\n"
                f"id: {legacy_id}\n"
                "work_item: W-00000001\n"
                "status: promoted\n"
                "predecessor:\n"
                "supersedes:\n"
                "---\n\n"
                f"# {legacy_id} Legacy promoted decision\n\n"
                "## Principles applied\n\n- SSOT — preserve the original identity.\n",
                encoding="utf-8",
            )
            stable = stage_root / f"present/work/decisions/{stable_id}.md"
            stable.write_text(
                "---\n"
                f"id: {stable_id}\n"
                "work_item: W-00000001\n"
                "status: decided\n"
                f"predecessor: {legacy_id}\n"
                f"supersedes: {legacy_id}\n"
                "---\n\n"
                f"# {stable_id} Stable successor decision\n\n"
                "## Principles applied\n\n- SSOT — keep the DE identity stable.\n",
                encoding="utf-8",
            )
            commit_all(root, "add Contract X decision fixture")

            self.migrate_successfully(root)

            migrated_work = stage_root / "work/current/W-00000001.md"
            work_text = migrated_work.read_text(encoding="utf-8")
            resolved_legacy = stage_records.resolve_decision_ref(
                root, stage_root, legacy_id
            )
            resolved_stable = stage_records.resolve_decision_ref(
                root, stage_root, stable_id
            )
            stable_fields = stage_guard.parse_frontmatter(resolved_stable)
            self.assertFalse(work.exists())
            self.assertIn(
                f".stage/official/decisions/records/{legacy_id}.md", work_text
            )
            self.assertIn(f".stage/decisions/pending/{stable_id}.md", work_text)
            self.assertEqual(
                stage_root / f"official/decisions/records/{legacy_id}.md",
                resolved_legacy,
            )
            self.assertEqual(
                stage_root / f"decisions/pending/{stable_id}.md", resolved_stable
            )
            self.assertEqual(legacy_id, stable_fields["predecessor"])
            self.assertEqual(legacy_id, stable_fields["supersedes"])


class MigratedProjectLifecycleAdversarialTest(MigrationAdversarialFixture):
    def add_retrospective(
        self, stage_root: Path, card: Path, item_id: str, retrospective_id: str
    ) -> None:
        set_field(card, "retrospective", "completed")
        set_field(card, "retrospective_ref", retrospective_id)
        (stage_root / f"work/retrospectives/{retrospective_id}.md").write_text(
            "---\n"
            f"id: {retrospective_id}\n"
            f"work_item: {item_id}\n"
            "---\n\n"
            f"# {retrospective_id} Migrated lifecycle retrospective\n\n"
            "## Principles applied\n\n- SSOT — the migrated registry owned every path.\n",
            encoding="utf-8",
        )

    def close_work(
        self, root: Path, item_id: str, *, promotion: str
    ) -> subprocess.CompletedProcess[str]:
        check = (
            subprocess.list2cmdline(
                [sys.executable, "-c", "print('migrated lifecycle check passed')"]
            )
            if sys.platform == "win32"
            else shlex.join(
                [sys.executable, "-c", "print('migrated lifecycle check passed')"]
            )
        )
        return run_tool(
            CLOSE,
            root,
            item_id,
            "--promotion",
            promotion,
            "--check",
            check,
        )

    def test_full_lifecycle_closure_promotion_and_reattribution_on_migrated_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = make_v3_project(root)
            self.migrate_successfully(root, commit=True)

            theme = run_tool(
                ROADMAP,
                root,
                "create-theme",
                "--title",
                "Migrated delivery",
                "--intent",
                "Prove external projects retain the full lifecycle",
            )
            self.assertEqual(0, theme.returncode, theme.stderr)
            self.assert_audit_clean(root)

            milestone = run_tool(
                ROADMAP,
                root,
                "create-milestone",
                "--theme",
                "TH-00000001",
                "--title",
                "Migration confidence",
                "--purpose",
                "Exercise every v4 transition after migration",
                "--completion-criteria",
                "The migrated lifecycle and strict audit both pass",
            )
            self.assertEqual(0, milestone.returncode, milestone.stderr)
            self.assert_audit_clean(root)

            pursuit = run_tool(ROADMAP, root, "open-pursuit", "M-00000001")
            self.assertEqual(0, pursuit.returncode, pursuit.stderr)
            self.assertIn("DE-00000001", pursuit.stdout)
            self.assert_audit_clean(root)

            registered = run_tool(
                REGISTER,
                root,
                "--backlog",
                "--title",
                "Migrated end-to-end work",
                "--kind",
                "development",
                "--scope",
                "",
                "--priority",
                "high",
                "--milestone",
                "M-00000001",
            )
            self.assertEqual(0, registered.returncode, registered.stderr)
            planned = stage_root / "work/planned/W-00000001/_story.md"
            self.assertTrue(planned.is_file())
            self.assert_audit_clean(root)

            started = run_tool(
                START,
                root,
                "W-00000001",
                "--scope",
                "src",
                "--venue",
                "codex",
                "--owner",
                "Codex",
            )
            self.assertEqual(0, started.returncode, started.stderr)
            card = stage_root / "work/current/W-00000001/_story.md"
            self.assertTrue(card.is_file())
            self.assertFalse(planned.exists())
            self.assertIn("milestone: M-00000001", card.read_text(encoding="utf-8"))
            self.assert_audit_clean(root)

            self.add_retrospective(stage_root, card, "W-00000001", "R-00000001")
            closed_work = self.close_work(
                root, "W-00000001", promotion="not_applicable"
            )
            self.assertEqual(0, closed_work.returncode, closed_work.stderr)
            self.assertIn("status: completed", card.read_text(encoding="utf-8"))
            # W-00000109 owns close_work's hierarchy move: it still computes the
            # flat active-index link and therefore cannot remove this exact row.
            self.assert_audit_errors(
                root,
                [
                    (
                        "INDEX005",
                        ".stage/work/current/W-00000001/_story.md",
                    )
                ],
            )

            archived = run_tool(ARCHIVE, root, "W-00000001")
            self.assertEqual(0, archived.returncode, archived.stdout + archived.stderr)
            archived_card = stage_root / "official/work/archive/items/W-00000001.md"
            self.assertIn(
                "terminal_disposition: accepted",
                archived_card.read_text(encoding="utf-8"),
            )
            # W-00000109 also owns archive_work's hierarchy move. Until then,
            # the exact nested active row becomes dangling after archival.
            self.assert_audit_errors(
                root,
                [("INDEX001", "work/active.md")],
            )

            closed_milestone = run_tool(
                ROADMAP,
                root,
                "close-milestone",
                "M-00000001",
                "--attestation",
                "The migrated lifecycle and strict audit both passed.",
            )
            self.assertEqual(0, closed_milestone.returncode, closed_milestone.stderr)
            closure_id = "DE-00000002"
            pending = stage_root / f"decisions/pending/{closure_id}.md"
            self.assertIn(
                "| W-00000001 | accepted |", pending.read_text(encoding="utf-8")
            )
            self.assert_audit_errors(
                root,
                [("INDEX001", "work/active.md")],
            )

            promoter = run_tool(
                REGISTER,
                root,
                "--title",
                "Promote migrated closure",
                "--kind",
                "development",
                "--scope",
                "promotion-fixture",
                "--venue",
                "codex",
            )
            self.assertEqual(0, promoter.returncode, promoter.stderr)
            promoter_card = stage_root / "work/current/W-00000002/_story.md"
            official_relative = f".stage/official/decisions/records/{closure_id}.md"
            set_field(promoter_card, "promotes", official_relative)
            self.add_retrospective(
                stage_root, promoter_card, "W-00000002", "R-00000002"
            )
            closed_promoter = self.close_work(
                root, "W-00000002", promotion="approved"
            )
            self.assertEqual(0, closed_promoter.returncode, closed_promoter.stderr)
            # W-00000109 removes this exact close-owned stale hierarchy row.
            self.assert_audit_errors(
                root,
                [
                    ("INDEX001", "work/active.md"),
                    (
                        "INDEX005",
                        ".stage/work/current/W-00000002/_story.md",
                    )
                ],
            )

            intent = stage_guard.write_intent_file(
                stage_root,
                {"type": "promotion", "work_item": "W-00000002"},
                official_relative,
            )
            self.assertIsNotNone(intent)
            promotion_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "session_id": "migrated-lifecycle",
                "tool_input": {
                    "command": (
                        f"mv .stage/decisions/pending/{closure_id}.md "
                        f"{official_relative}"
                    )
                },
            }

            set_field(archived_card, "terminal_disposition", "rejected")
            denied_promotion = stage_guard.handle_event(
                "pre-tool-use", promotion_payload
            )
            denial_reason = denied_promotion["hookSpecificOutput"][
                "permissionDecisionReason"
            ]
            self.assertEqual(
                "deny",
                denied_promotion["hookSpecificOutput"]["permissionDecision"],
            )
            self.assertIn("promotion revalidation", denial_reason.lower())
            self.assertIn("expected terminal_disposition `accepted`", denial_reason)

            set_field(archived_card, "terminal_disposition", "accepted")
            allowed_promotion = stage_guard.handle_event(
                "pre-tool-use", promotion_payload
            )
            self.assertEqual({}, allowed_promotion)
            set_field(pending, "status", "promoted")
            official = stage_root / f"official/decisions/records/{closure_id}.md"
            pending.replace(official)
            stage_guard.handle_event("post-tool-use", promotion_payload)
            set_field(promoter_card, "promotion", "promoted")
            self.assert_audit_errors(
                root,
                [
                    ("INDEX001", "work/active.md"),
                    (
                        "INDEX005",
                        ".stage/work/current/W-00000002/_story.md",
                    )
                ],
            )

            reattribution_payload = {
                "tool_name": "Edit",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/official/work/archive/items/W-00000001.md",
                    "old_string": "milestone: M-00000001",
                    "new_string": "milestone: M-00000077",
                },
            }
            denied_reattribution = stage_guard.handle_event(
                "pre-tool-use", reattribution_payload
            )
            reattribution_reason = denied_reattribution["hookSpecificOutput"][
                "permissionDecisionReason"
            ]
            self.assertEqual(
                "deny",
                denied_reattribution["hookSpecificOutput"]["permissionDecision"],
            )
            self.assertIn(closure_id, reattribution_reason)
            self.assertIn("re-attribution", reattribution_reason.lower())
            self.assert_audit_errors(
                root,
                [
                    ("INDEX001", "work/active.md"),
                    (
                        "INDEX005",
                        ".stage/work/current/W-00000002/_story.md",
                    )
                ],
            )

            archived_promoter = run_tool(ARCHIVE, root, "W-00000002")
            self.assertEqual(
                0,
                archived_promoter.returncode,
                archived_promoter.stdout + archived_promoter.stderr,
            )
            self.assert_audit_errors(
                root,
                [
                    ("INDEX001", "work/active.md"),
                    ("INDEX001", "work/active.md"),
                ],
            )


if __name__ == "__main__":
    unittest.main()
