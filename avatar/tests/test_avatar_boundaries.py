from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import unittest

import test_avatar_cli as cli


def history(identifier: str, generation: int = 1) -> dict:
    ref = f"distill:{identifier}@1"
    return {
        "schema": "criteria-history/1", "producer": "distill", "producer_version": "1.10.0",
        "id": identifier, "project": "test/app", "generation": generation,
        "versions": [{"ref": ref, "statement": "Keep errors explicit.", "origin": cli.origin()}],
        "events": [{"event": "recorded", "ref": ref, "generation": generation}],
    }


class AvatarBoundaryTest(unittest.TestCase):
    setUp = cli.AvatarCliTest.setUp
    tearDown = cli.AvatarCliTest.tearDown
    run_avatar = cli.AvatarCliTest.run_avatar
    write_payload = cli.AvatarCliTest.write_payload
    propose = cli.AvatarCliTest.propose

    def attach(self, payload: dict, key: str, expected_exit: int = 0) -> dict:
        path = self.write_payload(f"{key}.json", payload)
        return self.run_avatar("source", "attach", "--file", str(path),
                               "--idempotency-key", key, home=self.home,
                               expected_exit=expected_exit)

    def mutate(self, action: str, identifier: str, key: str, payload: dict,
               expected_exit: int = 0) -> dict:
        path = self.write_payload(f"{key}-{identifier}.json", payload)
        args = ["criterion", action, identifier]
        if action == "confirm":
            args += ["--version", "1"]
        return self.run_avatar(*args, "--payload-file", str(path), "--idempotency-key", key,
                               home=self.home, expected_exit=expected_exit)

    def test_each_distill_criterion_keeps_its_own_history(self) -> None:
        first = history("CR-aaaaaaaaaaaa")
        second = history("CR-bbbbbbbbbbbb")
        self.attach(first, "first")
        self.attach(second, "second")
        newer = copy.deepcopy(second)
        newer["generation"] = 2
        newer["events"].append({"event": "revoked", "ref": second["versions"][0]["ref"]})
        self.attach(newer, "newer")
        shown = self.run_avatar("show", "--json", home=self.home)
        projections = {(p["history"]["id"], p["generation"]): p for p in shown["projections"]}
        self.assertFalse(projections[(first["id"], 1)]["newer_projection_exists"])
        self.assertTrue(projections[(second["id"], 1)]["newer_projection_exists"])
        self.assertFalse(projections[(second["id"], 2)]["newer_projection_exists"])

    def test_payload_cannot_hide_a_different_mutation_target(self) -> None:
        for action in ("confirm", "revise", "revoke"):
            with self.subTest(action=action):
                first = self.propose(f"propose:{action}-a")
                second = self.propose(f"propose:{action}-b")
                payload = {"id": "shadow-target", "origin": cli.origin(),
                           "base_version": 1, "reason": "A user change."}
                self.mutate(action, first["id"], action, payload)
                error = self.mutate(action, second["id"], action, payload, expected_exit=2)
                self.assertEqual(error["error"], "E_IDEMPOTENCY_CONFLICT")

    def test_directory_at_database_path_is_a_storage_error(self) -> None:
        (self.home / "avatar.db").mkdir(parents=True)
        for arguments in (("export",), ("show", "--json"),
                          ("check", "--refs", "avatar:PC-aaaaaaaaaaaa@1")):
            with self.subTest(arguments=arguments):
                result = self.run_avatar(*arguments, home=self.home, expected_exit=3)
                self.assertEqual(result["error"], "E_STORE_UNAVAILABLE")

    def test_file_at_home_path_returns_a_json_storage_error(self) -> None:
        self.home.write_text("not a directory")
        payload = self.write_payload("proposal.json", {"statement": "Use clear errors."})
        result = self.run_avatar("criterion", "propose", "--payload-file", str(payload),
                                 "--idempotency-key", "blocked", home=self.home, expected_exit=3)
        self.assertEqual(result["error"], "E_STORE_UNAVAILABLE")

    def test_invalid_conditions_do_not_create_a_store(self) -> None:
        for path in ("../secret", "/etc", "C:/outside", "C:outside", "app/*", "   "):
            with self.subTest(path=path):
                payload = self.write_payload("invalid.json", {
                    "statement": "Use explicit errors.",
                    "applies_when": [{"kind": "path", "any": [path]}],
                })
                result = self.run_avatar("criterion", "propose", "--payload-file", str(payload),
                                         "--idempotency-key", "invalid", home=self.home,
                                         expected_exit=2)
                self.assertEqual(result["error"], "E_INVALID_CONDITION")
                self.assertFalse((self.home / "avatar.db").exists())

    def test_confirmation_has_a_quote_digest_and_replays_without_a_new_timestamp(self) -> None:
        first = self.propose()
        payload = {"origin": cli.origin()}
        result = self.mutate("confirm", first["id"], "confirmation", payload)
        replay = self.mutate("confirm", first["id"], "confirmation", payload)
        self.assertEqual(replay, {**result, "replayed": True})
        exported = self.run_avatar("export", home=self.home)
        origin = exported["criteria"][0]["origin"]
        self.assertEqual(origin["quote_sha256"], hashlib.sha256(origin["quote"].encode()).hexdigest())
        self.assertTrue(origin["captured_at"])

    def test_revocation_reason_and_source_can_be_read_in_both_formats(self) -> None:
        first = self.propose()
        payload = {"base_version": 1, "origin": cli.origin("I no longer want this."),
                   "reason": "The old preference no longer applies."}
        self.mutate("revoke", first["id"], "revoke", payload)
        shown = self.run_avatar("show", "--criterion", first["id"], "--json", home=self.home)
        event = shown["criteria"][0]["events"][-1]
        self.assertEqual(event["reason"], payload["reason"])
        self.assertEqual(event["origin"]["quote"], payload["origin"]["quote"])
        result = subprocess.run([sys.executable, str(cli.SCRIPT), "--home", str(self.home), "show"],
                                capture_output=True, text=True, check=True)
        self.assertIn(payload["reason"], result.stdout)
        self.assertIn(payload["origin"]["quote"], result.stdout)
        self.assertIn(payload["origin"]["source_ref"], result.stdout)

    def test_older_history_cannot_introduce_a_conflicting_event(self) -> None:
        newer = history("CR-aaaaaaaaaaaa", 2)
        self.attach(newer, "newer")
        older = copy.deepcopy(newer)
        older["generation"] = 1
        older["events"] = [{"event": "revoked", "ref": newer["versions"][0]["ref"]}]
        error = self.attach(older, "older", expected_exit=2)
        self.assertEqual(error["error"], "E_PROJECTION_CONFLICT")

    def test_newer_history_cannot_drop_a_version(self) -> None:
        first = history("CR-aaaaaaaaaaaa")
        second = copy.deepcopy(first["versions"][0])
        second["ref"] = "distill:CR-aaaaaaaaaaaa@2"
        first["versions"].append(second)
        first["events"][0]["ref"] = second["ref"]
        self.attach(first, "first")
        shortened = copy.deepcopy(first)
        shortened["generation"] = 2
        shortened["versions"] = [second]
        error = self.attach(shortened, "shortened", expected_exit=2)
        self.assertEqual(error["error"], "E_PROJECTION_CONFLICT")

    def test_projection_rejects_duplicate_or_mixed_criterion_refs(self) -> None:
        first = history("CR-aaaaaaaaaaaa")
        for ref in (first["versions"][0]["ref"], "distill:CR-bbbbbbbbbbbb@1"):
            with self.subTest(ref=ref):
                invalid = copy.deepcopy(first)
                invalid["versions"].append({**invalid["versions"][0], "ref": ref})
                error = self.attach(invalid, "invalid", expected_exit=2)
                self.assertEqual(error["error"], "E_SOURCE_INVALID")


if __name__ == "__main__":
    unittest.main()
