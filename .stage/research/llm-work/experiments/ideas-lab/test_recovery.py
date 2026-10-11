"""복구와 작업 상태 시제품을 실제 임시 파일로 검사합니다."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from recovery import (
    TaskState,
    build_cases,
    inspect_recovery,
    recover,
    snapshot,
    transition,
)


class RecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "a.txt").write_text("old-a", encoding="utf-8")
        (self.root / "b.txt").write_text("old-b", encoding="utf-8")
        self.before = snapshot(self.root, ["a.txt", "b.txt"])
        self.desired = {"a.txt": "new-a", "b.txt": "new-b"}

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_partial_recovery_does_not_rewrite_completed_file(self) -> None:
        (self.root / "a.txt").write_text("new-a", encoding="utf-8")
        completed = snapshot(self.root, ["a.txt"])
        observation = inspect_recovery(self.root, self.before, self.desired)
        self.assertEqual(observation["action"], "recover")
        self.assertEqual(observation["targets"], ["b.txt"])
        result = recover(self.root, self.before, self.desired)
        self.assertEqual(result["action"], "complete")
        self.assertEqual(result["written"], ["b.txt"])
        self.assertEqual(snapshot(self.root, ["a.txt"]), completed)
        self.assertEqual((self.root / "b.txt").read_text(), "new-b")

    def test_success_can_be_read_after_lost_response(self) -> None:
        for name, content in self.desired.items():
            (self.root / name).write_text(content)
        result = recover(self.root, self.before, self.desired)
        self.assertEqual(result["action"], "complete")
        self.assertEqual(result["written"], [])

    def test_unexpected_change_blocks_all_writes(self) -> None:
        (self.root / "b.txt").write_text("human-change")
        unchanged = snapshot(self.root, ["a.txt", "b.txt"])
        result = recover(self.root, self.before, self.desired)
        self.assertEqual(result["action"], "conflict")
        self.assertEqual(result["targets"], ["b.txt"])
        self.assertEqual(result["written"], [])
        self.assertEqual(snapshot(self.root, ["a.txt", "b.txt"]), unchanged)

    def test_change_between_inspection_and_apply_blocks_all_writes(self) -> None:
        def competing_write() -> None:
            (self.root / "b.txt").write_text("changed-during-recovery")

        result = recover(self.root, self.before, self.desired, before_apply=competing_write)
        self.assertEqual(result["action"], "conflict")
        self.assertEqual(result["written"], [])
        self.assertEqual((self.root / "a.txt").read_text(), "old-a")
        self.assertEqual((self.root / "b.txt").read_text(), "changed-during-recovery")

    def test_original_contents_restored_by_other_writer_still_conflict(self) -> None:
        (self.root / "b.txt").unlink()
        (self.root / "b.txt").write_text("old-b")
        result = recover(self.root, self.before, self.desired)
        self.assertEqual(result["action"], "conflict")
        self.assertEqual(result["written"], [])

    def test_cooperative_lock_blocks_writes(self) -> None:
        (self.root / ".recovery-lock").mkdir()
        result = recover(self.root, self.before, self.desired)
        self.assertEqual(result["action"], "busy")
        self.assertEqual(result["written"], [])
        self.assertEqual((self.root / "a.txt").read_text(), "old-a")

    def test_unexpected_deletion_blocks_writes(self) -> None:
        (self.root / "b.txt").unlink()
        self.assertEqual(recover(self.root, self.before, self.desired)["action"], "conflict")
        self.assertEqual((self.root / "a.txt").read_text(), "old-a")

    def test_create_missing_file(self) -> None:
        before = snapshot(self.root, ["created.txt"])
        result = recover(self.root, before, {"created.txt": "new"})
        self.assertEqual(result["action"], "complete")
        self.assertEqual((self.root / "created.txt").read_text(), "new")

    def test_io_failure_after_first_write_can_resume_remaining_file(self) -> None:
        original_replace = Path.replace

        def interrupt_second(source: Path, target: Path) -> Path:
            if target.name == "b.txt":
                raise OSError("실험에서 두 번째 쓰기를 끊었습니다.")
            return original_replace(source, target)

        with patch.object(Path, "replace", interrupt_second):
            with self.assertRaises(OSError):
                recover(self.root, self.before, self.desired)
        self.assertEqual((self.root / "a.txt").read_text(), "new-a")
        self.assertEqual((self.root / "b.txt").read_text(), "old-b")
        self.assertFalse((self.root / ".recovery-lock").exists())
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["a.txt", "b.txt"])
        result = recover(self.root, self.before, self.desired)
        self.assertEqual(result["written"], ["b.txt"])
        self.assertEqual(result["action"], "complete")

    def test_aliases_cannot_name_same_file_twice(self) -> None:
        with self.assertRaises(ValueError):
            snapshot(self.root, ["a.txt", "./a.txt"])

    def test_rejects_escape_and_symlink_paths(self) -> None:
        with self.assertRaises(ValueError):
            snapshot(self.root, ["../escape"])
        try:
            (self.root / "alias").symlink_to(self.root / "a.txt")
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(ValueError):
            snapshot(self.root, ["alias"])


class TaskStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.active = TaskState("active", ("report", "analysis"), ("analysis",))

    def test_status_question_preserves_pending_work(self) -> None:
        result = transition(self.active, "status")
        self.assertEqual(result["action"], "report_and_continue")
        self.assertEqual(result["targets"], ["report"])
        self.assertEqual(result["state"]["status"], "active")

    def test_stop_overrides_active_work(self) -> None:
        result = transition(self.active, "stop")
        self.assertEqual(result["action"], "stop")
        self.assertEqual(result["targets"], [])
        self.assertEqual(result["state"]["status"], "stopped")

    def test_acknowledgement_does_not_resume_stopped_work(self) -> None:
        state = TaskState("stopped", ("report",), ())
        self.assertEqual(transition(state, "acknowledgement")["action"], "stay_stopped")

    def test_scope_change_requires_new_explicit_authorization(self) -> None:
        result = transition(self.active, "scope_change", proposed=("publish",))
        self.assertEqual(result["action"], "review_scope")
        self.assertEqual(result["targets"], [])
        self.assertEqual(result["state"]["authorized"], ["report", "analysis"])
        pending = TaskState(**{**result["state"], "status": "scope_pending"})
        self.assertEqual(transition(pending, "acknowledgement")["action"], "review_scope")

    def test_missing_required_information_blocks_continue(self) -> None:
        result = transition(self.active, "missing_info", missing=("recipient",))
        self.assertEqual(result["action"], "wait_for_info")
        self.assertEqual(result["targets"], ["recipient"])
        waiting = TaskState("waiting", ("report",), (), ("recipient",))
        self.assertEqual(transition(waiting, "acknowledgement")["action"], "wait_for_info")

    def test_unknown_instruction_does_not_run(self) -> None:
        result = transition(self.active, "ambiguous")
        self.assertEqual(result["action"], "clarify")
        self.assertEqual(result["targets"], [])

    def test_acknowledgement_only_continues_existing_scope(self) -> None:
        result = transition(self.active, "acknowledgement")
        self.assertEqual(result["action"], "continue")
        self.assertEqual(result["targets"], ["report"])

    def test_finished_task_stays_finished(self) -> None:
        state = TaskState("active", ("report",), ("report",))
        self.assertEqual(transition(state, "status")["action"], "report_complete")

    def test_invalid_completed_target_rejected(self) -> None:
        with self.assertRaises(ValueError):
            transition(TaskState("active", ("report",), ("publish",)), "status")

    def test_completed_state_cannot_hide_pending_work(self) -> None:
        with self.assertRaises(ValueError):
            transition(TaskState("completed", ("report",), ()), "status")

    def test_ambiguous_instruction_stays_blocked_after_acknowledgement(self) -> None:
        unclear = TaskState(**transition(self.active, "ambiguous")["state"])
        self.assertEqual(transition(unclear, "acknowledgement")["action"], "clarify")

    def test_case_contract_and_real_prototype_outputs(self) -> None:
        cases = build_cases()
        self.assertEqual(len(cases), 8)
        self.assertEqual(len({case["id"] for case in cases}), 8)
        self.assertEqual(sum(case["idea"] == "I03" for case in cases), 4)
        self.assertEqual(sum(case["idea"] == "I04" for case in cases), 4)
        json.dumps(cases, ensure_ascii=False)
        for case in cases:
            result = case["enhanced"]["prototype"]
            self.assertEqual(result["action"], case["expected"]["action"])
            self.assertEqual(sorted(result["targets"]), case["expected"]["targets"])


if __name__ == "__main__":
    unittest.main()
