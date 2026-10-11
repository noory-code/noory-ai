"""Guard concrete failures observed in the synthetic research workflow."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from synthetic_profile_lab import validate

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("review", ROOT / "profile-lab-review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class LabTests(unittest.TestCase):
    def test_placeholder_is_not_a_completed_limitation(self) -> None:
        saved = ROOT / "evidence/2026-10-07-profile-lab-v1/K-ko-4"
        card = json.loads((saved / "card.json").read_text())
        bundle = json.loads((saved / "input.json").read_text())["bundle"]
        self.assertTrue(any("placeholder" in error.lower() for error in validate(card, bundle, "ko")))

    def test_saved_evidence_is_used_without_current_fixture(self) -> None:
        bundles, system, cards = review.load_evidence(ROOT / "evidence/2026-10-07-profile-lab-v1")
        self.assertEqual(len(bundles), 2)
        self.assertEqual(len(cards), 16)
        self.assertIn("fictional-J", {bundle["owner_id"] for bundle in bundles})
        self.assertIn("You write a small Avatar card", system)

    def test_modified_saved_input_is_rejected(self) -> None:
        source = ROOT / "evidence/2026-10-07-profile-lab-v1/J-ko-1"
        with tempfile.TemporaryDirectory() as temporary:
            batch = Path(temporary)
            folder = batch / "J-ko-1"
            folder.mkdir()
            for name in ("input.json", "schema.json", "system.txt", "process.json", "card.json"):
                (folder / name).write_bytes((source / name).read_bytes())
            data = json.loads((folder / "input.json").read_text())
            data["bundle"]["owner_id"] = "another-person"
            (folder / "input.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "digest"):
                review.load_evidence(batch)


if __name__ == "__main__":
    unittest.main()
