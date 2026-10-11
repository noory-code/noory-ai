"""실제 임시 파일을 읽고 변경 범위와 적용 조건을 검사합니다."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evidence import build_cases, extract_evidence, plan_review, snapshot


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def write(self, name: str, value: str) -> None:
        (self.root / name).write_text(value, encoding="utf-8")

    def document(self, name: str, **updates: object) -> None:
        record: dict[str, object] = {
            "id": name,
            "topic": "export",
            "version": "2",
            "answer": "supported",
            "exceptions": [],
            "source": f"manual/{name}",
        }
        record.update(updates)
        self.write(f"{name}.json", json.dumps(record))

    def test_real_change_reaches_transitive_dependents_only(self) -> None:
        self.write("policy.txt", "limit=3")
        self.write("format.txt", "indent=2")
        before = snapshot(self.root, ["policy.txt", "format.txt"])
        self.write("policy.txt", "limit=4")
        after = snapshot(self.root, ["policy.txt", "format.txt"])
        result = plan_review(before, after, {
            "approve": {"files": ["policy.txt"], "decisions": []},
            "publish": {"files": [], "decisions": ["approve"]},
            "format": {"files": ["format.txt"], "decisions": []},
        })
        self.assertEqual(result["action"], "review")
        self.assertEqual(result["targets"], ["approve", "publish"])

    def test_unchanged_files_do_not_request_review(self) -> None:
        self.write("policy.txt", "limit=3")
        state = snapshot(self.root, ["policy.txt"])
        result = plan_review(state, state, {
            "approve": {"files": ["policy.txt"], "decisions": []},
        })
        self.assertEqual((result["action"], result["targets"]), ("keep", []))

    def test_deleted_source_requires_review(self) -> None:
        self.write("policy.txt", "limit=3")
        before = snapshot(self.root, ["policy.txt"])
        (self.root / "policy.txt").unlink()
        result = plan_review(before, snapshot(self.root, ["policy.txt"]), {
            "approve": {"files": ["policy.txt"], "decisions": []},
        })
        self.assertEqual((result["action"], result["targets"]), ("review", ["approve"]))

    def test_unknown_dependency_blocks_it_and_its_dependent(self) -> None:
        result = plan_review({}, {}, {
            "audit": None,
            "publish": {"files": [], "decisions": ["audit"]},
        })
        self.assertEqual(result["action"], "clarify")
        self.assertEqual(result["targets"], ["audit", "publish"])

    def test_unrecorded_source_is_not_treated_as_unchanged(self) -> None:
        result = plan_review({}, {}, {
            "audit": {"files": ["unknown.txt"], "decisions": []},
        })
        self.assertEqual((result["action"], result["targets"]), ("clarify", ["audit"]))

    def test_cycle_and_unknown_decision_require_clarification(self) -> None:
        result = plan_review({}, {}, {
            "a": {"files": [], "decisions": ["b"]},
            "b": {"files": [], "decisions": ["a"]},
            "c": {"files": [], "decisions": ["missing"]},
        })
        self.assertEqual((result["action"], result["targets"]), ("clarify", ["a", "b", "c"]))

    def test_snapshot_rejects_path_outside_root(self) -> None:
        with self.assertRaises(ValueError):
            snapshot(self.root, ["../outside.txt"])

    def test_version_selection_keeps_source_and_exceptions(self) -> None:
        self.document("old", version="1", answer="unsupported")
        self.document("current")
        result = extract_evidence(self.root, ["old.json", "current.json"], {
            "topic": "export", "version": "2", "context": {},
        })
        self.assertEqual((result["action"], result["targets"]), ("supported", ["current"]))
        self.assertEqual(result["selected"][0]["source"], "manual/current")
        self.assertEqual(result["selected"][0]["exceptions"], [])

    def test_matching_exception_overrides_general_answer(self) -> None:
        self.document("policy", exceptions=[{
            "when": {"region": "EU"}, "answer": "unsupported",
        }])
        result = extract_evidence(self.root, ["policy.json"], {
            "topic": "export", "version": "2", "context": {"region": "EU"},
        })
        self.assertEqual((result["action"], result["targets"]), ("unsupported", ["policy"]))

    def test_unknown_exception_condition_requires_clarification(self) -> None:
        self.document("policy", exceptions=[{
            "when": {"region": "EU"}, "answer": "unsupported",
        }])
        result = extract_evidence(self.root, ["policy.json"], {
            "topic": "export", "version": "2", "context": {},
        })
        self.assertEqual((result["action"], result["targets"]), ("clarify", ["policy"]))

    def test_disagreeing_sources_require_clarification(self) -> None:
        self.document("a")
        self.document("b", answer="unsupported")
        result = extract_evidence(self.root, ["a.json", "b.json"], {
            "topic": "export", "version": "2", "context": {},
        })
        self.assertEqual((result["action"], result["targets"]), ("clarify", ["a", "b"]))

    def test_missing_metadata_is_not_silently_filled(self) -> None:
        self.write("partial.json", json.dumps({
            "id": "partial", "topic": "export", "version": "2", "answer": "supported",
        }))
        result = extract_evidence(self.root, ["partial.json"], {
            "topic": "export", "version": "2", "context": {},
        })
        self.assertEqual((result["action"], result["targets"]), ("clarify", ["partial"]))

    def test_duplicate_identifiers_and_broken_files_require_clarification(self) -> None:
        self.document("a")
        self.document("b", id="a")
        self.write("broken.json", "{")
        result = extract_evidence(self.root, ["a.json", "b.json", "broken.json"], {
            "topic": "export", "version": "2", "context": {},
        })
        self.assertEqual(result["action"], "clarify")
        self.assertTrue(result["issues"])

    def test_eight_cases_use_computed_results_and_are_serializable(self) -> None:
        cases = build_cases()
        self.assertEqual(len(cases), 8)
        self.assertEqual(len({case["id"] for case in cases}), 8)
        self.assertEqual(sum(case["idea"] == "I01" for case in cases), 4)
        self.assertEqual(sum(case["idea"] == "I02" for case in cases), 4)
        json.dumps(cases, ensure_ascii=False)
        for case in cases:
            computed = case["enhanced"]["computed"]
            self.assertEqual(computed["action"], case["expected"]["action"])
            self.assertEqual(computed["targets"], case["expected"]["targets"])
            self.assertNotIn("expected", case["baseline"])


if __name__ == "__main__":
    unittest.main()
