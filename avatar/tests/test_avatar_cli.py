from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "avatar.py"


def origin(quote: str = "I confirm this preference.") -> dict[str, object]:
    return {
        "kind": "user_statement",
        "source_ref": "session:claude/session-1/msg-1",
        "quote": quote,
        "actor": "user",
        "recorded_by": {
            "host": "claude",
            "session_id": "session-1",
            "via": "cli",
        },
    }


class AvatarCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary_directory.name) / "avatar home"
        self.payloads = Path(self.temporary_directory.name) / "payloads"
        self.payloads.mkdir()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_avatar(
        self,
        *arguments: str,
        expected_exit: int = 0,
        home: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        command = [sys.executable, str(SCRIPT)]
        if home is not None:
            command.extend(["--home", str(home)])
        command.extend(arguments)
        completed = subprocess.run(
            command,
            cwd=PLUGIN_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            expected_exit,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return json.loads(completed.stdout)

    def write_payload(self, name: str, payload: dict[str, object]) -> Path:
        path = self.payloads / name
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def propose(self, key: str = "claude:session-1:1") -> dict[str, Any]:
        payload = self.write_payload(
            f"propose-{key.rsplit(':', 1)[-1]}.json",
            {
                "statement": "Prefer explicit errors at public boundaries.",
                "applies_when": [{"kind": "path", "any": ["app/"]}],
                "exceptions": [],
                "notes": [],
                "overrides": [],
                "ai_confidence": 0.8,
                "from_choices": [],
            },
        )
        return self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "propose",
            "--idempotency-key",
            key,
            "--payload-file",
            str(payload),
        )

    def test_confirm_requires_user_quote_and_preserves_confirmation_origin(self) -> None:
        proposed = self.propose()
        criterion_id = proposed["id"]

        missing_quote = self.write_payload(
            "confirm-missing-quote.json",
            {"origin": {**origin(), "quote": ""}},
        )
        error = self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "confirm",
            criterion_id,
            "--version",
            "1",
            "--idempotency-key",
            "claude:session-1:2",
            "--payload-file",
            str(missing_quote),
            expected_exit=2,
        )
        self.assertEqual(error["error"], "E_QUOTE_REQUIRED")

        confirmation = self.write_payload(
            "confirm.json",
            {"origin": origin("Yes, make that my personal criterion.")},
        )
        confirmed = self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "confirm",
            criterion_id,
            "--version",
            "1",
            "--idempotency-key",
            "claude:session-1:3",
            "--payload-file",
            str(confirmation),
        )
        self.assertEqual(confirmed["ref"], f"avatar:{criterion_id}@2")

        shown = self.run_avatar(
            "--home",
            str(self.home),
            "show",
            "--criterion",
            criterion_id,
            "--json",
        )
        current = shown["criteria"][0]["versions"][-1]
        self.assertEqual(current["confirmation"], "user_confirmed")
        self.assertEqual(current["origin"]["recorded_by"]["host"], "claude")

        checked = self.run_avatar(
            "--home",
            str(self.home),
            "check",
            "--refs",
            f"avatar:{criterion_id}@1,avatar:{criterion_id}@2",
        )
        self.assertEqual(
            [item["status"] for item in checked["results"]],
            ["superseded", "eligible_current"],
        )

        exported = self.run_avatar("--home", str(self.home), "export")
        self.assertEqual(exported["schema"], "criteria-snapshot/1")
        self.assertEqual(exported["scope"], {"kind": "personal", "key": "personal"})
        self.assertEqual([item["ref"] for item in exported["criteria"]], [confirmed["ref"]])
        self.assertEqual(exported["retired"][0]["status"], "superseded")

    def test_revise_stays_proposed_until_confirmed_and_revoke_is_historical(self) -> None:
        proposed = self.propose()
        criterion_id = proposed["id"]
        confirmation = self.write_payload("confirm-v1.json", {"origin": origin()})
        self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "confirm",
            criterion_id,
            "--version",
            "1",
            "--idempotency-key",
            "claude:session-1:2",
            "--payload-file",
            str(confirmation),
        )

        revision = self.write_payload(
            "revise.json",
            {
                "base_version": 2,
                "statement": "Prefer result values at internal boundaries.",
                "reason": "Internal callers already branch on missing values.",
            },
        )
        revised = self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "revise",
            criterion_id,
            "--idempotency-key",
            "claude:session-1:3",
            "--payload-file",
            str(revision),
        )
        self.assertEqual(revised["ref"], f"avatar:{criterion_id}@3")
        checked = self.run_avatar(
            "--home",
            str(self.home),
            "check",
            "--refs",
            revised["ref"],
        )
        self.assertEqual(checked["results"][0]["status"], "proposed")
        self.assertEqual(self.run_avatar("--home", str(self.home), "export")["criteria"], [])

        confirmation_v2 = self.write_payload(
            "confirm-v2.json", {"origin": origin("Yes, use the revised wording.")}
        )
        confirmed = self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "confirm",
            criterion_id,
            "--version",
            "3",
            "--idempotency-key",
            "claude:session-1:4",
            "--payload-file",
            str(confirmation_v2),
        )
        revocation = self.write_payload(
            "revoke.json",
            {
                "base_version": 4,
                "origin": origin("I no longer want this as a personal criterion."),
                "reason": "The preference was too broad.",
            },
        )
        self.run_avatar(
            "--home",
            str(self.home),
            "criterion",
            "revoke",
            criterion_id,
            "--idempotency-key",
            "claude:session-1:5",
            "--payload-file",
            str(revocation),
        )
        checked = self.run_avatar(
            "--home",
            str(self.home),
            "check",
            "--refs",
            confirmed["ref"],
        )
        self.assertEqual(checked["results"][0]["status"], "revoked")
        self.assertEqual(self.run_avatar("--home", str(self.home), "export")["criteria"], [])

    def test_choice_idempotency_and_condition_differences(self) -> None:
        first_payload = {
            "question": "How should invalid ports be handled?",
            "options": ["raise", "return-none"],
            "chosen": "return-none",
            "reason_quote": "The caller already handles None.",
            "context": {
                "project_key": "test/demo-app",
                "conditions": [{"kind": "path", "any": ["app/"]}],
            },
            "origin": origin("Return None in the application code."),
            "source_refs": ["distill:CR-123456789abc@2"],
        }
        first_path = self.write_payload("choice-1.json", first_payload)
        first = self.run_avatar(
            "--home",
            str(self.home),
            "choice",
            "add",
            "--idempotency-key",
            "claude:session-1:10",
            "--payload-file",
            str(first_path),
        )
        replayed = self.run_avatar(
            "--home",
            str(self.home),
            "choice",
            "add",
            "--idempotency-key",
            "claude:session-1:10",
            "--payload-file",
            str(first_path),
        )
        self.assertEqual(replayed["id"], first["id"])
        self.assertTrue(replayed["replayed"])

        conflicting_path = self.write_payload(
            "choice-conflict.json", {**first_payload, "options": ["return-none", "ignore"]}
        )
        conflict = self.run_avatar(
            "--home",
            str(self.home),
            "choice",
            "add",
            "--idempotency-key",
            "claude:session-1:10",
            "--payload-file",
            str(conflicting_path),
            expected_exit=2,
        )
        self.assertEqual(conflict["error"], "E_IDEMPOTENCY_CONFLICT")

        second_path = self.write_payload(
            "choice-2.json",
            {
                **first_payload,
                "chosen": "raise",
                "reason_quote": "Tests should fail loudly.",
                "context": {
                    "project_key": "test/demo-app",
                    "conditions": [{"kind": "path", "any": ["tests/"]}],
                },
                "origin": origin("Raise in tests."),
            },
        )
        self.run_avatar(
            "--home",
            str(self.home),
            "choice",
            "add",
            "--idempotency-key",
            "claude:session-1:11",
            "--payload-file",
            str(second_path),
        )
        shown = self.run_avatar("--home", str(self.home), "show", "--json")
        self.assertEqual(len(shown["review_candidates"]), 1)
        self.assertTrue(shown["review_candidates"][0]["conditions_differ"])

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--home", str(self.home), "show"],
            cwd=PLUGIN_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Conditions differ", completed.stdout)
        self.assertNotIn("contradiction", completed.stdout.lower())

    def test_projection_history_is_append_only(self) -> None:
        version = {
            "ref": "distill:CR-123456789abc@1",
            "statement": "Raise ConfigError for invalid input.",
            "applies_when": [{"kind": "path", "any": ["app/"]}],
            "exceptions": [],
            "notes": [],
            "overrides": [],
            "confirmation": "user_stated",
            "ai_confidence": None,
            "origin": origin("Raise ConfigError for invalid input."),
            "reason": "Initial statement.",
            "supersedes": None,
            "recorded_at": "2026-10-05T12:00:00Z",
        }
        first_envelope = {
            "schema": "criteria-history/1",
            "producer": "distill",
            "generation": 1,
            "versions": [version],
            "events": [{"kind": "recorded", "ref": version["ref"], "generation": 1}],
        }
        first_path = self.write_payload("history-1.json", first_envelope)
        attached = self.run_avatar(
            "--home",
            str(self.home),
            "source",
            "attach",
            "--idempotency-key",
            "claude:session-1:20",
            "--file",
            str(first_path),
        )
        self.assertFalse(attached["duplicate"])
        duplicate = self.run_avatar(
            "--home",
            str(self.home),
            "source",
            "attach",
            "--idempotency-key",
            "claude:session-1:21",
            "--file",
            str(first_path),
        )
        self.assertTrue(duplicate["duplicate"])

        changed_version = {**version, "statement": "Return None for invalid input."}
        changed_path = self.write_payload(
            "history-changed.json",
            {
                **first_envelope,
                "generation": 2,
                "versions": [changed_version],
                "events": [
                    *first_envelope["events"],
                    {"kind": "revised", "ref": version["ref"], "generation": 2},
                ],
            },
        )
        conflict = self.run_avatar(
            "--home",
            str(self.home),
            "source",
            "attach",
            "--idempotency-key",
            "claude:session-1:22",
            "--file",
            str(changed_path),
            expected_exit=2,
        )
        self.assertEqual(conflict["error"], "E_PROJECTION_CONFLICT")

        revoked_event = {"kind": "revoked", "ref": version["ref"], "generation": 2}
        second_path = self.write_payload(
            "history-2.json",
            {
                **first_envelope,
                "generation": 2,
                "events": [*first_envelope["events"], revoked_event],
            },
        )
        accepted = self.run_avatar(
            "--home",
            str(self.home),
            "source",
            "attach",
            "--idempotency-key",
            "claude:session-1:23",
            "--file",
            str(second_path),
        )
        self.assertEqual(accepted["generation"], 2)

        missing_event_path = self.write_payload(
            "history-missing-event.json",
            {
                **first_envelope,
                "generation": 3,
                "events": [
                    *first_envelope["events"],
                    {"kind": "reviewed", "ref": version["ref"], "generation": 3},
                ],
            },
        )
        conflict = self.run_avatar(
            "--home",
            str(self.home),
            "source",
            "attach",
            "--idempotency-key",
            "claude:session-1:24",
            "--file",
            str(missing_event_path),
            expected_exit=2,
        )
        self.assertEqual(conflict["error"], "E_PROJECTION_CONFLICT")

        historical_path = self.write_payload(
            "history-0.json",
            {**first_envelope, "generation": 0, "events": []},
        )
        historical = self.run_avatar(
            "--home",
            str(self.home),
            "source",
            "attach",
            "--idempotency-key",
            "claude:session-1:25",
            "--file",
            str(historical_path),
        )
        self.assertTrue(historical["newer_projection_exists"])
        shown = self.run_avatar("--home", str(self.home), "show", "--json")
        self.assertEqual(shown["projections"][0]["generation"], 2)
        self.assertTrue(shown["projections"][-1]["newer_projection_exists"])

    def test_unknown_and_non_personal_refs_are_not_current(self) -> None:
        checked = self.run_avatar(
            "--home",
            str(self.home),
            "check",
            "--refs",
            "distill:CR-123456789abc@1,avatar:PC-000000000000@1",
        )
        self.assertEqual(
            [item["status"] for item in checked["results"]],
            ["scope_mismatch", "unknown"],
        )

    def test_avatar_home_environment_variable_is_used(self) -> None:
        environment = os.environ.copy()
        environment["AVATAR_HOME"] = str(self.home)
        default_home = self.home.parent / "unused home"
        environment["HOME"] = str(default_home)
        environment["USERPROFILE"] = str(default_home)
        exported = self.run_avatar("export", env=environment)
        self.assertEqual(exported["store"], "absent")
        self.assertFalse((default_home / ".avatar" / "avatar.db").exists())

    def test_concurrent_writes_do_not_lose_choices(self) -> None:
        def add_choice(number: int) -> dict[str, Any]:
            payload = self.write_payload(
                f"concurrent-{number}.json",
                {
                    "question": f"Question {number}",
                    "options": ["a", "b"],
                    "chosen": "a",
                    "reason_quote": f"Reason {number}",
                    "context": {"project_key": "test/demo", "conditions": []},
                    "origin": origin(f"Choice {number}"),
                    "source_refs": [],
                },
            )
            return self.run_avatar(
                "--home",
                str(self.home),
                "choice",
                "add",
                "--idempotency-key",
                f"codex:concurrent:{number}",
                "--payload-file",
                str(payload),
            )

        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(add_choice, range(12)))
        self.assertEqual(len({result["id"] for result in results}), 12)
        shown = self.run_avatar("--home", str(self.home), "show", "--json")
        self.assertEqual(len(shown["choices"]), 12)


if __name__ == "__main__":
    unittest.main()
