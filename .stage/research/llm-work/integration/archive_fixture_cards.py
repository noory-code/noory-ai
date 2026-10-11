"""Store synthetic cards as byte-identical text, outside Stage's live Markdown records."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("evidence", type=Path)
args = parser.parse_args()
root = args.evidence.resolve()
manifest = root / "fixture-paths.json"
if manifest.exists():
    raise SystemExit("Fixture cards were already archived; do not replace the manifest.")
entries = []
for path in sorted(root.glob("*/project/.stage/**/*.md")):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    stored = path.with_name(path.name + ".txt")
    if stored.exists():
        raise SystemExit("The destination already exists: " + str(stored))
    path.rename(stored)
    assert hashlib.sha256(stored.read_bytes()).hexdigest() == digest
    entries.append({"original": str(path.relative_to(root)), "stored": str(stored.relative_to(root)),
                    "sha256": digest})
manifest.write_text(json.dumps(entries, indent=2), encoding="utf-8")
print(json.dumps({"cards_archived": len(entries), "content_changes": 0}))
