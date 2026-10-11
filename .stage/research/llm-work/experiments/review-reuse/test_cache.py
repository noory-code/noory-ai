"""리뷰 입력이 바뀌면 재사용을 막고 저장한 결과를 보존하는지 검사합니다."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cache import fingerprint, lookup, store


class FingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = {"src/main.py": b"print('hello')\n", "rules.txt": b"strict\n"}
        self.criteria = "오류와 누락을 검토합니다."
        self.policy = "read-only; check-all-listed-files"
        self.reviewer = "model=example; reasoning=high; prompt_revision=1"

    def key(self, **updates: object) -> str:
        values: dict[str, object] = {
            "files": self.files, "criteria": self.criteria,
            "policy": self.policy, "reviewer": self.reviewer,
        }
        values.update(updates)
        return fingerprint(**values)

    def test_equal_contents_have_equal_keys_regardless_of_mapping_order(self) -> None:
        reversed_files = dict(reversed(list(self.files.items())))
        self.assertEqual(self.key(), self.key(files=reversed_files))
        self.assertRegex(self.key(), r"\A[a-f0-9]{64}\Z")

    def test_each_file_byte_change_changes_key(self) -> None:
        baseline = self.key()
        for path in self.files:
            with self.subTest(path=path):
                changed = dict(self.files)
                changed[path] += b"\x00"
                self.assertNotEqual(baseline, self.key(files=changed))

    def test_added_deleted_and_renamed_files_change_key(self) -> None:
        baseline = self.key()
        added = {**self.files, "empty.txt": b""}
        deleted = {"src/main.py": self.files["src/main.py"]}
        renamed = {"src/other.py": self.files["src/main.py"], "rules.txt": b"strict\n"}
        for files in (added, deleted, renamed):
            with self.subTest(files=files):
                self.assertNotEqual(baseline, self.key(files=files))

    def test_criteria_policy_and_reviewer_each_change_key(self) -> None:
        for field in ("criteria", "policy", "reviewer"):
            with self.subTest(field=field):
                changed = self.key(**{field: getattr(self, field) + " revised"})
                self.assertNotEqual(self.key(), changed)

    def test_field_boundaries_are_unambiguous(self) -> None:
        left = self.key(criteria="ab", policy="c")
        right = self.key(criteria="a", policy="bc")
        self.assertNotEqual(left, right)
        self.assertNotEqual(self.key(files={"a": b"bc"}), self.key(files={"ab": b"c"}))

    def test_paths_cannot_escape_or_have_ambiguous_spellings(self) -> None:
        for path in ("", "../outside", "/absolute", "./a", "a//b", "a\\b", "C:/file"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.key(files={path: b"data"})

    def test_file_contents_must_be_bytes(self) -> None:
        with self.assertRaises(ValueError):
            self.key(files={"file.txt": "text"})


class CacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "cache"
        self.key = fingerprint({"main.py": b"pass\n"}, "review", "read-only", "example")
        self.result = {"summary": "검토를 마쳤습니다.", "findings": [{"line": 1, "ok": True}]}

    def test_miss_does_not_create_directory(self) -> None:
        self.assertIsNone(lookup(self.directory, self.key))
        self.assertFalse(self.directory.exists())

    def test_roundtrip_and_replacement_preserve_complete_results(self) -> None:
        store(self.directory, self.key, self.result)
        self.assertEqual(lookup(self.directory, self.key), self.result)
        second = {"summary": "다시 검토했습니다.", "findings": []}
        store(self.directory, self.key, second)
        self.assertEqual(lookup(self.directory, self.key), second)

    def test_mutating_input_or_returned_result_does_not_change_cache(self) -> None:
        store(self.directory, self.key, self.result)
        self.result["findings"][0]["ok"] = False
        first = lookup(self.directory, self.key)
        self.assertTrue(first["findings"][0]["ok"])
        first["findings"].clear()
        self.assertEqual(len(lookup(self.directory, self.key)["findings"]), 1)

    def test_truncated_json_and_invalid_utf8_are_misses(self) -> None:
        store(self.directory, self.key, self.result)
        path = self.directory / f"{self.key}.json"
        for content in (b'{"partial":', b"\xff", b"null", b"[]"):
            with self.subTest(content=content):
                path.write_bytes(content)
                self.assertIsNone(lookup(self.directory, self.key))

    def test_changed_result_is_a_miss_even_if_json_still_parses(self) -> None:
        store(self.directory, self.key, self.result)
        path = self.directory / f"{self.key}.json"
        path.write_text(path.read_text(encoding="utf-8").replace("검토를", "평가를"), encoding="utf-8")
        self.assertIsNone(lookup(self.directory, self.key))

    def test_entry_from_another_key_is_a_miss(self) -> None:
        store(self.directory, self.key, self.result)
        other = fingerprint({"main.py": b"changed\n"}, "review", "read-only", "example")
        original = self.directory / f"{self.key}.json"
        (self.directory / f"{other}.json").write_bytes(original.read_bytes())
        self.assertIsNone(lookup(self.directory, other))

    def test_invalid_key_does_not_touch_disk(self) -> None:
        for key in ("../outside", "f" * 63, "F" * 64, "f" * 64 + "/child", ""):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    store(self.directory, key, self.result)
                with self.assertRaises(ValueError):
                    lookup(self.directory, key)
        self.assertFalse(self.directory.exists())

    def test_non_json_results_do_not_replace_an_existing_entry(self) -> None:
        store(self.directory, self.key, self.result)
        invalid = [[], {"bad": float("nan")}, {"bad": b"bytes"}, {1: "key"}, {"bad": (1, 2)}]
        circular: dict[str, object] = {}
        circular["self"] = circular
        for value in invalid + [circular]:
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ValueError):
                store(self.directory, self.key, value)
            self.assertEqual(lookup(self.directory, self.key), self.result)

    def test_failed_atomic_replace_preserves_old_result_and_cleans_temporary_file(self) -> None:
        store(self.directory, self.key, self.result)
        with patch("cache.os.replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                store(self.directory, self.key, {"summary": "new"})
        self.assertEqual(lookup(self.directory, self.key), self.result)
        self.assertEqual([path.name for path in self.directory.iterdir()], [f"{self.key}.json"])

    def test_duplicate_json_fields_are_a_miss(self) -> None:
        store(self.directory, self.key, self.result)
        path = self.directory / f"{self.key}.json"
        text = path.read_text(encoding="utf-8")
        path.write_text('{"version": 1,' + text[1:], encoding="utf-8")
        self.assertIsNone(lookup(self.directory, self.key))


if __name__ == "__main__":
    unittest.main()
