from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import handoff_packet as packet
from handoff_conditions import classify
from handoff_sources import source_status


def criterion() -> dict:
    return {"ref": "distill:CR-aaaaaaaaaaaa@2", "statement": "Return None for invalid input.",
            "applies_when": [{"kind": "path", "any": ["app/"]}], "exceptions": [],
            "notes": [], "confirmation": "user_stated", "ai_confidence": None,
            "origin": {"kind": "user_statement", "source_ref": "session:codex/test/1",
                       "quote": "Return None.", "actor": "user"}}


def snapshot() -> dict:
    return {"schema": "criteria-snapshot/1", "producer": "distill", "producer_version": "1.10.0",
            "generation": 2, "checked_at": "2026-10-06T00:00:00Z",
            "scope": {"kind": "project", "key": "test/app"}, "criteria": [criterion()],
            "retired": [{"ref": "distill:CR-aaaaaaaaaaaa@1", "status": "superseded",
                         "by": "distill:CR-aaaaaaaaaaaa@2"}]}


class HandoffPacketTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project with spaces"
        self.root.mkdir()
        (self.root / "app/api").mkdir(parents=True)
        for name in ("config.py", "host.py", "api/x.py"):
            (self.root / "app" / name).write_text("# Fixture file.\n")
        self.work = self.root / ".stage/work/current/W-00000001"
        self.work.mkdir(parents=True)
        (self.work / "_epic.md").write_text(
            "---\nid: W-00000001\nkind: planning\n---\n## Purpose\nKeep parsing predictable.\n")
        child = self.work / "W-00000002"
        child.mkdir()
        self.card = child / "_story.md"
        self.card.write_text(
            "---\nid: W-00000002\nkind: development\nscope: app/\n---\n"
            "## Purpose\nSupport host parsing.\n## Progress\n"
            "Applied criteria: distill:CR-aaaaaaaaaaaa@1\n"
            "Condition judgment: distill:CR-aaaaaaaaaaaa@1 path=app/config.py -> applies\n"
            "## Success criteria\n- Invalid hosts return None.\n"
            "## Next action\nImplement parse_host.\n")
        self.config = {"distill": {"argv": [sys.executable, "producer with spaces.py"],
                                    "db": str(self.root / "criteria.db")}}

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self, data: dict | None = None) -> str:
        def run(argv, **kwargs):
            self.assertFalse(kwargs["shell"])
            self.assertEqual(kwargs["timeout"], 30)
            if "check" in argv:
                value = {"results": [{"ref": "distill:CR-aaaaaaaaaaaa@1", "status": "superseded"}]}
            else:
                value = data if data is not None else snapshot()
            return subprocess.CompletedProcess(argv, 0, json.dumps(value), "")
        with patch("handoff_producers.subprocess.run", side_effect=run):
            return packet.build_packet(self.root, "W-00000002", "test/app", self.config)

    def test_packet_carries_purpose_current_criteria_evidence_and_recheck_argv(self) -> None:
        text = self.build()
        self.assertLess(text.index("Keep parsing predictable."), text.index("Support host parsing."))
        self.assertIn("generation: 2", text)
        self.assertIn("Return None for invalid input.", text)
        self.assertIn("No recorded evidence", text)
        self.assertIn("superseded", text)
        self.assertIn("Condition judgment:", text)
        self.assertIn('"criteria", "check", "--project", "test/app"', text)
        self.assertIn('"--refs", "distill:CR-aaaaaaaaaaaa@2"', text)
        self.assertIn("Implement parse_host.", text)
        self.assertIn("avatar: Criteria were not queried", text)

    def test_scope_mismatch_and_duplicate_versions_stop_the_packet(self) -> None:
        bad = snapshot()
        bad["scope"]["key"] = "other/project"
        with self.assertRaisesRegex(packet.PacketError, "E_SCOPE_MISMATCH"):
            self.build(bad)
        bad = snapshot()
        bad["criteria"].append({**criterion(), "ref": "distill:CR-aaaaaaaaaaaa@3"})
        with self.assertRaisesRegex(packet.PacketError, "E_VERSION_CONFLICT"):
            self.build(bad)

    def test_unavailable_or_malformed_producer_never_means_empty_criteria(self) -> None:
        for result in (subprocess.CompletedProcess([], 3, "[]", "broken"),
                       subprocess.CompletedProcess([], 0, "invalid json", "")):
            with self.subTest(result=result), patch("handoff_producers.subprocess.run", return_value=result):
                text = packet.build_packet(self.root, "W-00000002", "test/app", self.config)
                self.assertIn("Could not check distill criteria", text)
                self.assertNotIn("Return None for invalid input.", text)
        with patch("handoff_producers.subprocess.run", side_effect=subprocess.TimeoutExpired([], 30)):
            text = packet.build_packet(self.root, "W-00000002", "test/app", self.config)
            self.assertIn("Could not check distill criteria", text)

    def test_invalid_producer_configuration_cannot_launch_a_command(self) -> None:
        for argv in ("python producer.py", ["python", "producer.py"], [], [42]):
            with self.subTest(argv=argv), patch("handoff_producers.subprocess.run") as run:
                with self.assertRaisesRegex(packet.PacketError, "E_PRODUCERS_INVALID"):
                    packet.build_packet(self.root, "W-00000002", "test/app", {"distill": {"argv": argv}})
                run.assert_not_called()

    def test_file_evidence_is_rehashed_and_checks_are_not_run(self) -> None:
        path = self.root / "app/config.py"
        path.parent.mkdir(exist_ok=True)
        path.write_text("before")
        evidence = [
            {"kind": "file", "path": "app/config.py", "sha256": hashlib.sha256(b"before").hexdigest()},
            {"kind": "check", "command": "DO_NOT_RUN_THIS", "exit": 0, "result": "3 passed"},
        ]
        body = self.card.read_text().replace("## Progress\n", "## Progress\n" + "\n".join(
            "Evidence: " + json.dumps(e) for e in evidence) + "\n")
        self.card.write_text(body)
        text = packet.build_packet(self.root, "W-00000002", "test/app", {})
        self.assertIn("matches", text)
        self.assertIn("not rerun by this packet", text)
        path.write_text("after")
        text = packet.build_packet(self.root, "W-00000002", "test/app", {})
        self.assertIn("changed", text)

    def test_no_producer_is_required_for_existing_stage_work(self) -> None:
        text = packet.build_packet(self.root, "W-00000002", "test/app", {})
        self.assertIn("Support host parsing.", text)
        self.assertIn("Criteria were not queried", text)

    def test_condition_and_or_exceptions_and_partial_scope(self) -> None:
        base = criterion()
        self.assertEqual(classify(base, ["app/config.py"], "development", self.root)["status"], "applies")
        self.assertEqual(classify(base, ["other.py"], "development", self.root)["status"], "not_applicable")
        base["applies_when"].append({"kind": "path", "any": ["tests/"]})
        self.assertEqual(classify(base, ["app/", "tests/"], "development", self.root)["status"], "not_applicable")
        base = criterion()
        base["applies_when"] = [{"kind": "path", "any": ["app/config.py", "app/host.py"]}]
        result = classify(base, ["app/"], "development", self.root)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["targets"], ["app/config.py", "app/host.py"])
        base["exceptions"] = [{"kind": "path", "any": ["app/config.py"]}]
        result = classify(base, ["app/"], "development", self.root)
        self.assertEqual(result["targets"], ["app/host.py"])
        base["notes"] = ["Public interfaces only."]
        self.assertEqual(classify(base, ["app/host.py"], "development", self.root)["status"], "needs_judgment")

    def test_unknown_conditions_and_unsafe_scope_remain_unresolved(self) -> None:
        for scope in ([], ["../outside"], ["C:/outside"]):
            self.assertEqual(classify(criterion(), scope, "development", self.root)["status"], "unresolved")
        base = criterion()
        base["applies_when"] = [{"kind": "language", "any": ["Python"]}]
        self.assertEqual(classify(base, ["app/"], "development", self.root)["status"], "unresolved")

    def test_changed_stage_source_is_unresolved_and_excluded_from_check(self) -> None:
        data = snapshot()
        data["criteria"][0]["origin"] = {
            "kind": "stage_card", "source_ref": "stage:test/app/" + self.card.relative_to(self.root).as_posix() + "#Purpose",
            "source_sha256": "old", "quote": "A past purpose.", "actor": "user",
        }
        text = self.build(data)
        self.assertIn("source_status: changed", text)
        self.assertIn("### unresolved", text)
        self.assertNotIn('"--refs", "distill:CR-aaaaaaaaaaaa@2"', text)

    def test_stage_source_ref_checks_project_before_path_and_rejects_escape(self) -> None:
        origin = {"kind": "stage_card", "source_ref": "stage:other/project/../secret#Purpose"}
        self.assertEqual(source_status(origin, self.root, "test/app"), "not_checkable")
        for path in ("../secret", "/secret", "C:/secret"):
            origin["source_ref"] = "stage:test/app/" + path + "#Purpose"
            self.assertEqual(source_status(origin, self.root, "test/app"), "rejected_ref")
        origin["source_ref"] = "stage:test/app/" + self.card.relative_to(self.root).as_posix() + "#Purpose"
        origin["source_sha256"] = hashlib.sha256(b"Support host parsing.").hexdigest()
        self.assertEqual(source_status(origin, self.root, "test/app"), "matches")
        outside = self.root.parent / "outside.md"
        outside.write_text("## Purpose\nsecret\n")
        try:
            (self.root / "link.md").symlink_to(outside)
        except OSError:
            self.skipTest("This host cannot create symlinks.")
        origin["source_ref"] = "stage:test/app/link.md#Purpose"
        self.assertEqual(source_status(origin, self.root, "test/app"), "rejected_ref")

    def test_stage_scopes_without_slashes_and_wildcard_keep_descendants(self) -> None:
        base = criterion()
        base["applies_when"] = [{"kind": "path", "any": ["app/config.py"]}]
        for scope in (["app"], ["*"]):
            with self.subTest(scope=scope):
                result = classify(base, scope, "development", self.root)
                self.assertEqual(result["status"], "partial")
                self.assertEqual(result["targets"], ["app/config.py"])
        self.assertEqual(classify(base, ["app/config.py"], "development", self.root)["status"], "applies")

    def test_nested_and_conditions_and_missing_file_and_section(self) -> None:
        base = criterion()
        base["applies_when"].append({"kind": "path", "any": ["app/api/"]})
        result = classify(base, ["app/"], "development", self.root)
        self.assertEqual(result, {"status": "partial", "targets": ["app/api/"], "excluded": []})
        self.assertEqual(classify(base, ["app/api/x.py"], "development", self.root)["status"], "applies")
        self.card.write_text(self.card.read_text().replace("## Progress\n", '## Progress\nEvidence: {"kind":"file","path":"app/gone.py","sha256":"old"}\n'))
        text = packet.build_packet(self.root, "W-00000002", "test/app", {})
        self.assertIn('"status": "missing"', text)
        data = snapshot()
        data["criteria"][0]["origin"] = {"kind": "stage_card", "actor": "user", "quote": "Past text.",
            "source_ref": "stage:test/app/" + self.card.relative_to(self.root).as_posix() + "#Removed"}
        self.assertIn("source_status: missing", self.build(data))
        self.assertIn("### unresolved", self.build(data))

    def test_dated_and_bulleted_records_are_visible_and_none_is_explicit(self) -> None:
        self.card.write_text(self.card.read_text().replace("Applied criteria:", "- 2026-10-06: Applied criteria:"))
        self.assertIn("superseded", self.build())
        self.card.write_text(self.card.read_text().replace("distill:CR-aaaaaaaaaaaa@1", "none"))
        self.assertIn("Explicitly applied no criteria", self.build())

    def test_live_producer_argv_and_korean_packet_work_through_a_pipe(self) -> None:
        producer = self.root / "producer with spaces.py"
        data = snapshot()
        data["criteria"][0]["statement"] = "잘못된 입력은 None을 돌려주세요."
        recorder = self.root / "received.jsonl"
        producer.write_text(
            "import json, sys\nfrom pathlib import Path\n"
            + f"with Path({str(recorder)!r}).open('a') as f: f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            + f"print({json.dumps(data)!r} if 'current' in sys.argv else '{{\"results\":[]}}')\n"
        )
        config = self.root / "producers.json"
        db = "a path with spaces\\database.db"
        config.write_text(json.dumps({"distill": {"argv": [sys.executable, str(producer)], "db": db}}))
        args = [sys.executable, str(SCRIPTS / "handoff_packet.py"), "--project-root", str(self.root),
                "W-00000002", "--project-key", "test/app", "--producers", str(config)]
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONIOENCODING": "ascii"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("잘못된 입력", result.stdout)
        absent = snapshot()
        absent.update({"criteria": [], "retired": [], "generation": 0, "store": "absent"})
        self.assertIn("store: absent", self.build(absent))
        received = [json.loads(line) for line in recorder.read_text().splitlines()]
        self.assertEqual(received[0], ["criteria", "current", "--project", "test/app", "--db", db])
        line = next(line for line in result.stdout.splitlines() if line.startswith("distill: ["))
        check = json.loads(line.split(": ", 1)[1])
        self.assertEqual(check[-2:], ["--db", db])
        self.assertEqual(subprocess.run(check, capture_output=True).returncode, 0)
        config.write_text("broken")
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("E_PRODUCERS_INVALID", result.stderr)

    def test_ambiguous_condition_directories_never_expand_or_exclude_scope(self) -> None:
        for field in ("applies_when", "exceptions"):
            base = criterion()
            base[field] = [{"kind": "path", "any": ["app"]}]
            for scope in (["app"], ["app/config.py"]):
                with self.subTest(field=field, scope=scope):
                    self.assertEqual(classify(base, scope, "development", self.root)["status"], "unresolved")
        base = criterion()
        base["applies_when"] = [{"kind": "path", "any": ["future"]}]
        self.assertEqual(classify(base, ["future/"], "development", self.root)["status"], "unresolved")

    def test_file_targets_keep_file_shape_and_dot_scope_is_not_project_scope(self) -> None:
        result = classify(criterion(), ["app/config.py"], "development", self.root)
        self.assertEqual(result["targets"], ["app/config.py"])
        self.assertEqual(classify(criterion(), ["."], "development", self.root)["status"], "unresolved")

    def test_new_descendants_and_directory_marked_files_are_unresolved(self) -> None:
        for field in ("applies_when", "exceptions"):
            for path, scope in (("app/newdir", "app/newdir/x.py"),
                                ("app/config.py/", "app/config.py")):
                base = criterion()
                base[field] = [{"kind": "path", "any": [path]}]
                with self.subTest(field=field, path=path):
                    self.assertEqual(classify(base, [scope], "development", self.root)["status"], "unresolved")
        base = criterion()
        base["applies_when"] = [{"kind": "path", "any": ["future/x.py"]}]
        base["exceptions"] = [{"kind": "path", "any": ["future"]}]
        self.assertEqual(classify(base, ["*"], "development", self.root)["status"], "unresolved")

    def test_malformed_applied_refs_are_visible_and_none_ignores_outer_space(self) -> None:
        self.card.write_text(self.card.read_text().replace("Applied criteria: distill:CR-aaaaaaaaaaaa@1",
                                                       "Applied criteria: distill:CR-ZZZ@1"))
        text = self.build()
        self.assertIn("Unparsed record: Applied criteria: distill:CR-ZZZ@1", text)
        self.assertNotIn("No applied-criteria record.", text)
        self.card.write_text(self.card.read_text().replace("Applied criteria: distill:CR-ZZZ@1",
                                                       "Applied criteria: none  "))
        self.assertIn("Explicitly applied no criteria.", self.build())


if __name__ == "__main__":
    unittest.main()
