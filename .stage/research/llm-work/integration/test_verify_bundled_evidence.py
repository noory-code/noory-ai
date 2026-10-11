"""Reject missing sender provenance or changes to the wrapper actually executed."""
from pathlib import Path
import shutil
import tempfile
import unittest

from verify_integration import verify


ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / "evidence/2026-10-06-contract"
BUNDLED = ROOT / "evidence/2026-10-07-handoff-bundled"


class BundledEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="bundled-evidence-")
        self.addCleanup(self.temporary.cleanup)
        self.evidence = Path(self.temporary.name) / "evidence"
        shutil.copytree(BUNDLED, self.evidence)

    def test_missing_reused_sender_manifest_fails(self) -> None:
        (self.evidence / "sender-claude/reuse.json").unlink()
        with self.assertRaisesRegex(ValueError, "reused sender manifest"):
            verify(CONTRACT, True, self.evidence)

    def test_changed_executed_wrapper_fails(self) -> None:
        wrapper = self.evidence / "fixture_avatar_batch.py"
        wrapper.write_bytes(wrapper.read_bytes() + b"\n# Changed after execution.\n")
        with self.assertRaisesRegex(ValueError, "recording wrapper"):
            verify(CONTRACT, True, self.evidence)


if __name__ == "__main__":
    unittest.main()
