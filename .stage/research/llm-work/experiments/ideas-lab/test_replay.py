"""실제 임시 파일로 두 아이디어의 동작과 실패 경계를 확인합니다."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any
import unittest

from replay import (
    MANIFEST_PATHS,
    build_cases,
    check_manifest_versions,
    compare_fixture,
    record_observation,
    replay_once,
)


class ReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "output.txt").write_text("part", encoding="utf-8")
        self.input = {"target": "output.txt", "expected": "complete"}
        self.response = {"success": True}
        self.record = record_observation(
            self.root, self.input, self.response, ["output.txt"]
        )

    def test_record_hashes_actual_bytes_and_does_not_alias_inputs(self) -> None:
        self.assertEqual(
            self.record["files"]["output.txt"]["sha256"],
            hashlib.sha256(b"part").hexdigest(),
        )
        self.input["target"] = "changed.txt"
        self.response["success"] = False
        self.assertEqual(self.record["input"]["target"], "output.txt")
        self.assertTrue(self.record["tool_response"]["success"])

    def test_one_file_change_runs_in_copy_and_preserves_original(self) -> None:
        roots = []

        def observe(
            root: Path, request: dict[str, Any], response: dict[str, Any]
        ) -> dict[str, Any]:
            roots.append(root)
            actual = (root / request["target"]).read_text(encoding="utf-8")
            return {"complete": actual == request["expected"]}

        original = copy.deepcopy(self.record)
        result = replay_once(
            self.record,
            {"file_state": {"output.txt": "complete"}},
            observe,
        )
        self.assertFalse(result["before"]["complete"])
        self.assertTrue(result["after"]["complete"])
        self.assertEqual(result["changed_factors"], ["file_state"])
        self.assertEqual(self.record, original)
        self.assertEqual((self.root / "output.txt").read_text(), "part")
        self.assertEqual(len(roots), 2)
        self.assertTrue(all(path != self.root for path in roots))
        self.assertTrue(all(not path.exists() for path in roots))
        self.assertEqual(
            result["before_hashes"]["input"], result["after_hashes"]["input"]
        )
        self.assertEqual(
            result["before_hashes"]["tool_response"],
            result["after_hashes"]["tool_response"],
        )

    def test_zero_two_unknown_or_unchanged_factors_do_not_run(self) -> None:
        changes = [
            {},
            {"input": {}, "tool_response": {}},
            {"hidden_server_state": {}},
            {"tool_response": self.record["tool_response"]},
        ]
        for change in changes:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    replay_once(self.record, change, self.fail_if_called)

    @staticmethod
    def fail_if_called(*args: Any) -> dict[str, Any]:
        raise AssertionError("잘못된 시험은 관찰 함수를 실행하면 안 됩니다.")

    def test_tampered_record_is_rejected(self) -> None:
        self.record["tool_response"]["success"] = False
        with self.assertRaises(ValueError):
            replay_once(self.record, {"tool_response": {}}, self.fail_if_called)

    def test_observer_cannot_silently_change_a_second_factor(self) -> None:
        def mutating_observer(
            root: Path, request: dict[str, Any], response: dict[str, Any]
        ) -> dict[str, Any]:
            (root / "output.txt").write_text("unexpected", encoding="utf-8")
            return {"complete": True}

        with self.assertRaises(ValueError):
            replay_once(self.record, {"tool_response": {"success": False}}, mutating_observer)
        self.assertEqual((self.root / "output.txt").read_text(), "part")

    def test_paths_cannot_escape_fixture(self) -> None:
        for path in ["../outside.txt", str(self.root / "output.txt")]:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    record_observation(self.root, {}, {}, [path])
        with self.assertRaises(ValueError):
            replay_once(
                self.record,
                {"file_state": {"../outside.txt": "oops"}},
                self.fail_if_called,
            )

    def test_restored_exception_can_support_the_requested_region(self) -> None:
        policy = {"default": "unsupported", "exceptions": {"island": "supported"}}
        (self.root / "policy.json").write_text(json.dumps(policy), encoding="utf-8")
        request = {"kind": "policy", "region": "island", "evidence": {"default": "unsupported"}}
        record = record_observation(
            self.root, request, {"documents": ["policy.json"]}, ["policy.json"]
        )
        changed = {"kind": "policy", "region": "island", "evidence": policy}
        result = compare_fixture(record, {"input": changed})
        self.assertEqual(result["comparison"]["before"], {"status": "unknown"})
        self.assertEqual(result["comparison"]["after"], {"status": "supported"})
        self.assertEqual(result["action"], "restore_exception")
        self.assertEqual(result["targets"], ["input.evidence.exceptions"])


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for path in MANIFEST_PATHS:
            self.write(path, {"name": "sample-plugin", "version": "1.2.3"})

    def write(self, relative: str, value: Any) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_matching_versions_are_accepted_without_changing_files(self) -> None:
        before = {path: (self.root / path).read_bytes() for path in MANIFEST_PATHS}
        result = check_manifest_versions(self.root)
        self.assertEqual(result["action"], "accept")
        self.assertEqual(result["targets"], [])
        self.assertEqual(result["versions"], {path: "1.2.3" for path in MANIFEST_PATHS})
        self.assertEqual(before, {path: (self.root / path).read_bytes() for path in MANIFEST_PATHS})

    def test_mismatch_identifies_both_files_without_choosing_a_release_version(self) -> None:
        self.write(MANIFEST_PATHS[1], {"name": "sample-plugin", "version": "1.2.4"})
        result = check_manifest_versions(self.root)
        self.assertEqual(result["action"], "align_versions")
        self.assertEqual(result["targets"], sorted(MANIFEST_PATHS))
        self.assertNotIn("selected_version", result)

    def test_invalid_schema_or_values_fall_back(self) -> None:
        invalid = [
            [],
            {"name": "sample-plugin"},
            {"name": "sample-plugin", "version": 123},
            {"name": "sample-plugin", "version": True},
            {"name": "sample-plugin", "version": "01.2.3"},
            {"name": "sample-plugin", "version": "1.2.3-beta"},
            {"name": "sample-plugin", "version": "1.2.3２"},
            {"name": "sample-plugin", "version": "1.2.3", "unknown": 1},
            {"name": "Bad Name", "version": "1.2.3"},
        ]
        for value in invalid:
            with self.subTest(value=value):
                self.write(MANIFEST_PATHS[0], value)
                result = check_manifest_versions(self.root)
                self.assertEqual(result["action"], "fallback")
                self.assertEqual(result["targets"], [MANIFEST_PATHS[0]])

    def test_missing_or_invalid_json_falls_back(self) -> None:
        path = self.root / MANIFEST_PATHS[1]
        path.unlink()
        result = check_manifest_versions(self.root)
        self.assertEqual(result["action"], "fallback")
        self.assertEqual(result["targets"], [MANIFEST_PATHS[1]])
        self.assertNotIn(str(self.root), json.dumps(result))
        path.write_text("{broken", encoding="utf-8")
        self.assertEqual(check_manifest_versions(self.root)["action"], "fallback")

    def test_different_plugin_names_are_not_compared(self) -> None:
        self.write(MANIFEST_PATHS[1], {"name": "another-plugin", "version": "1.2.3"})
        result = check_manifest_versions(self.root)
        self.assertEqual(result["action"], "fallback")
        self.assertEqual(result["targets"], sorted(MANIFEST_PATHS))


class CaseTests(unittest.TestCase):
    def test_eight_cases_are_serializable_and_match_the_stated_expectations(self) -> None:
        cases = build_cases()
        self.assertEqual(len(cases), 8)
        self.assertEqual(len({case["id"] for case in cases}), 8)
        self.assertEqual(sum(case["idea"] == "I05" for case in cases), 4)
        self.assertEqual(sum(case["idea"] == "I06" for case in cases), 4)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIn("action", case["task"])
                self.assertIn("targets", case["task"])
                self.assertIn("baseline", case)
                self.assertIn("scoring_note", case)
                expected = case["expected"]
                self.assertEqual(case["enhanced"]["action"], expected["action"])
                self.assertEqual(case["enhanced"]["targets"], expected["targets"])
                self.assertEqual(expected["targets"], sorted(expected["targets"]))
        json.dumps(cases, ensure_ascii=False, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
