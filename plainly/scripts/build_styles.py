"""Compose the shipped output styles from their single sources.

Claude Code reads a plugin's `output-styles/*.md` as static files, so the baseline, the profile
delta, and the fixed rules cannot be joined at load time. This script joins them and writes the
result, which is committed. `--check` reports whether the committed files still match their
sources, so a source edit that never reached the shipped files fails the test suite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
STYLES = PLUGIN_ROOT / "styles"
OUTPUT_STYLES = PLUGIN_ROOT / "output-styles"

# Claude Code drops its default coding instructions for any output style that does not ask to keep
# them. Plainly governs how a sentence reads and says nothing about how code is written, so every
# shipped style keeps them. An unknown key here is discarded in silence, so the spelling matters.
KEEP_CODING_INSTRUCTIONS = "keep-coding-instructions"


def read_registry() -> dict[str, object]:
    return json.loads((STYLES / "profiles.json").read_text(encoding="utf-8"))


def read(name: str) -> str:
    return (STYLES / name).read_text(encoding="utf-8").strip()


def compose(profile: str, entry: dict[str, str], baseline_name: str) -> str:
    body = read("baseline.md")
    if profile != baseline_name:
        body = f"{body}\n\n{read(entry['file'])}"
    fixed = read("fixed-rules.md")
    label = entry["label"]
    description = entry["description"]
    return (
        "---\n"
        f"name: {label}\n"
        f"description: {description}\n"
        f"{KEEP_CODING_INSTRUCTIONS}: true\n"
        "---\n"
        "\n"
        f"{body}\n"
        "\n"
        f"{fixed}\n"
    )


def build() -> dict[Path, str]:
    registry = read_registry()
    baseline_name = str(registry["baseline"])
    profiles: dict[str, dict[str, str]] = registry["profiles"]  # type: ignore[assignment]
    return {
        OUTPUT_STYLES / f"{profile}.md": compose(profile, entry, baseline_name)
        for profile, entry in profiles.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report drift instead of writing; exit 1 when a committed file differs.",
    )
    args = parser.parse_args()

    composed = build()
    if args.check:
        drifted = [
            path
            for path, text in composed.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        for path in drifted:
            print(f"stale: {path.relative_to(PLUGIN_ROOT)}")
        if drifted:
            print("Run `python3 plainly/scripts/build_styles.py` and commit the result.")
            return 1
        print(f"{len(composed)} output styles match their sources.")
        return 0

    OUTPUT_STYLES.mkdir(exist_ok=True)
    for path, text in composed.items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(PLUGIN_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
