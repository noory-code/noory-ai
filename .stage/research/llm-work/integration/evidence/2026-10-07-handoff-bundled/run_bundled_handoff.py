"""Reuse observed sender outputs and test a single synthetic-recording command."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from run_real_handoff import Experiment, PERSONAL, write_json


class BundledExperiment(Experiment):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.sender_evidence = args.sender_evidence.resolve()
        if json.loads((self.sender_evidence / "sources.json").read_text()) != self.sources:
            raise ValueError("Reused senders used different product sources.")
        for name in ("run_bundled_handoff.py", "fixture_avatar_batch.py", "bundled-recording-plan.md",
                     "verify_integration.py", "test_fixture_avatar_batch.py"):
            shutil.copyfile(Path(__file__).parent / name, self.out / name)

    def sender(self, host: str) -> dict:
        label = "sender-" + host
        prior = self.sender_evidence / label
        output = self.out / label
        source = json.loads((prior / "sender-result.json").read_text())
        result = json.loads((prior / "model/result.json").read_text())
        if source["passed"] is not True or result["exit"] != 0 or result["host"] != host:
            raise ValueError("The original sender did not finish successfully.")
        shutil.copytree(prior, output)
        restored = []
        for entry in json.loads((self.sender_evidence / "fixture-paths.json").read_text()):
            if not entry["original"].startswith(label + "/"):
                continue
            stored = self.out / entry["stored"]
            if hashlib.sha256(stored.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("A reused sender card changed.")
            stored.rename(self.out / entry["original"])
            restored.append(entry)
        manifest = {str(path.relative_to(prior)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in prior.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
        write_json(output / "reuse.json", {"original": str(prior), "new_model_call": False,
                                          "source_files": manifest, "restored_cards": restored})
        project = output / "project"
        print(json.dumps({"phase": label, "reused": True, "new_model_calls": 0}), flush=True)
        return {"host": host, "ok": True, "project": project, "ref": source["ref"], "output": output}

    def avatar_instructions(self, host: str, project: Path, label: str) -> str:
        write_json(project / ".data/recording-fixture.json", {
            "synthetic_only": True, "label": label, "project_key": "test/demo-app",
            "statement": PERSONAL, "avatar_argv": self.avatar, "distill_argv": self.distill})
        command = [sys.executable, str(self.out / "fixture_avatar_batch.py"),
                   "--project-root", str(project), "--chosen", "<actual choice>", "--refs", "<applied refs or none>"]
        return f"""
After H, record the same synthetic Avatar fixtures with this prepared public-CLI wrapper:
{json.dumps(command)}
Replace <actual choice> with ConfigError, None, or other, matching YOUR implementation.
Replace <applied refs or none> with the comma-separated refs YOU applied, or none.
This wrapper only copies explicit fixture data and runs choice add, criterion propose, criterion
confirm using the exact supplied confirmation, history/source attach when refs exist, and show.
It preserves every public CLI response in .data/batch-calls.jsonl and writes .data/avatar-show.json.
It does not choose the error contract, implement or test code, query criteria before your decision,
or update the Stage card. Those remain your responsibility above. Do not edit the wrapper or its fixture.
You do not need to reconstruct those Avatar payloads individually. Report the returned choice ID
and confirmed ref. If the wrapper exits nonzero, inspect its recorded error; do not bypass it.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--distill-python", required=True, type=Path)
    parser.add_argument("--avatar-root", required=True, type=Path)
    parser.add_argument("--stage-root", required=True, type=Path)
    parser.add_argument("--source-manifest", type=Path, default=Path(__file__).parent / "evidence/2026-10-06-contract/sources.json")
    parser.add_argument("--sender-evidence", type=Path, default=Path(__file__).parent / "evidence/2026-10-07-handoff-followup")
    return BundledExperiment(parser.parse_args()).execute()


if __name__ == "__main__":
    raise SystemExit(main())
