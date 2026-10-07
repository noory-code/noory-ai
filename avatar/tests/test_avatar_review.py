from __future__ import annotations

import copy
import json
import os
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_avatar_cli as cli
from test_avatar_boundaries import history

sys.path.insert(0, str(cli.PLUGIN_ROOT / "scripts"))
import avatar_view
from avatar_store import AvatarStore


class AvatarReviewTest(unittest.TestCase):
    setUp = cli.AvatarCliTest.setUp
    tearDown = cli.AvatarCliTest.tearDown
    run_avatar = cli.AvatarCliTest.run_avatar
    write_payload = cli.AvatarCliTest.write_payload
    propose = cli.AvatarCliTest.propose

    def test_revision_does_not_claim_an_earlier_user_confirmation(self) -> None:
        store = AvatarStore(self.home)
        first = store.propose("first", {"statement": "Prefer errors."})
        store.confirm(first["id"], 1, "confirm", {"origin": cli.origin()})
        store.revise(first["id"], "revise", {"base_version": 2, "statement": "Prefer None.", "reason": "A proposal."})
        shown = store.show(criterion_id=first["id"])["criteria"][0]
        self.assertIsNone(shown["versions"][-1]["origin"])
        self.assertIsNone(shown["events"][-1]["origin"])
        self.assertEqual(shown["versions"][-2]["origin"]["quote"], cli.origin()["quote"])

    def test_invalid_projection_cannot_break_future_human_show(self) -> None:
        for origin in ("text", ["bad"], 1):
            with self.subTest(origin=origin):
                value = history("CR-aaaaaaaaaaaa")
                value["versions"][0]["origin"] = origin
                path = self.write_payload("history.json", value)
                result = self.run_avatar("source", "attach", "--idempotency-key", "invalid",
                                         "--file", str(path), home=self.home, expected_exit=2)
                self.assertEqual(result["error"], "E_SOURCE_INVALID")

    def test_wrong_json_types_return_input_errors(self) -> None:
        first = self.propose()
        for field in ("actor", "kind", "quote_sha256"):
            for value in ([], {}):
                with self.subTest(field=field, value=value):
                    payload = {"origin": {**cli.origin(), field: value}}
                    path = self.write_payload("invalid.json", payload)
                    result = self.run_avatar("criterion", "confirm", first["id"], "--version", "1",
                                             "--idempotency-key", "invalid", "--payload-file", str(path),
                                             home=self.home, expected_exit=2)
                    self.assertIn("error", result)

    def test_bad_text_encoding_returns_input_error(self) -> None:
        for content in (b"\xff", json.dumps({"origin": cli.origin("\ud800")}).encode()):
            with self.subTest(content=content):
                path = self.payloads / "bad.json"
                path.write_bytes(content)
                first = self.propose()
                result = self.run_avatar("criterion", "confirm", first["id"], "--version", "1",
                                         "--idempotency-key", "bad-text", "--payload-file", str(path),
                                         home=self.home, expected_exit=2)
                self.assertIn("error", result)

    def test_korean_output_survives_an_ascii_pipe(self) -> None:
        store = AvatarStore(self.home)
        first = store.propose("first", {"statement": "잘못된 입력은 알려 주세요."})
        store.confirm(first["id"], 1, "confirm", {"origin": cli.origin("이 기준을 확인합니다.")})
        environment = {**os.environ, "PYTHONIOENCODING": "ascii"}
        result = self.run_avatar("export", home=self.home, env=environment)
        self.assertEqual(result["criteria"][0]["statement"], "잘못된 입력은 알려 주세요.")

    def test_reads_keep_one_generation_during_a_concurrent_revision(self) -> None:
        store = AvatarStore(self.home)
        first = store.propose("first", {"statement": "Prefer errors."})
        store.confirm(first["id"], 1, "confirm", {"origin": cli.origin()})
        with sqlite3.connect(store.path) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("UPDATE meta SET value = value WHERE key = 'generation'")
        original_connect = avatar_view.connect

        class InterleavedConnection:
            def __init__(self, connection):
                self.connection = connection
                self.fired = False

            def execute(self, sql, *args):
                if sql.startswith("SELECT id, current_version") and not self.fired:
                    self.fired = True
                    store.revise(first["id"], "revise", {"base_version": 2, "reason": "Changed."})
                return self.connection.execute(sql, *args)

            def close(self):
                self.connection.close()

        with patch("avatar_view.connect", side_effect=lambda path: InterleavedConnection(original_connect(path))):
            result = store.export("0.1.0")
        self.assertEqual(result["generation"], 2)
        self.assertEqual([v["ref"] for v in result["criteria"]], [f"avatar:{first['id']}@2"])
        self.assertEqual(store.export("0.1.0")["generation"], 3)

    def test_missing_selected_record_reports_not_found(self) -> None:
        result = self.run_avatar("show", "--criterion", "PC-aaaaaaaaaaaa", "--json",
                                 home=self.home, expected_exit=2)
        self.assertEqual(result["error"], "E_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
