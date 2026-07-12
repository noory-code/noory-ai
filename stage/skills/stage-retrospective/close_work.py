#!/usr/bin/env python3
"""Close a Stage work item by RUNNING its verification checks.

`verification: passed` becomes a byproduct of executing the checks and observing
their output, not a hand-typed claim (the honesty gap behind commit 79c86ee9).

Honest scope: this runs the checks you give it and captures their evidence. It
does NOT judge whether those checks are sufficient for the item's kind — supply
the kind-appropriate checks (see operations/verification.md). A check that runs
nothing (e.g. `true`, or unittest over an empty dir) will pass; that is the
caller's responsibility.

Closing also requires what the completion gate and audit require: a completed
retrospective (with an existing retrospective_ref) and a FINAL promotion
decision — otherwise the item would audit-fail (WORK008) and block later commits.

Usage:
    close_work.py --project-root . W-00000008 \
        --check "python3 -m unittest discover -s stage/hooks/tests -q" \
        --check "python3 stage/scripts/audit_stage.py" \
        [--promotion not_applicable] [--timeout 900]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

OPEN_TO_CLOSE = {"active", "review"}
PROMOTION_FINAL = {"approved", "promoted", "deferred", "not_applicable", "rejected"}
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
MAX_LINES = 40
MAX_BYTES = 4000


def field(text: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def set_field(text: str, name: str, value: str) -> str:
    return re.sub(rf"^({re.escape(name)}:)[ \t]*.*$", rf"\g<1> {value}", text, count=1, flags=re.MULTILINE)


def set_section(text: str, heading: str, body: str) -> str:
    # Body goes through a replacement FUNCTION, never an `rf"...\g<1>..."` template:
    # the check output is arbitrary and would otherwise be read as regex escapes
    # (`\1`, `\U…`) — a crash or silent corruption. Tail is a lookahead so the
    # section may be the last heading (\Z) without swallowing the next one.
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    return re.sub(pattern, lambda m: f"{m.group(1)}\n{body}\n", text, count=1, flags=re.DOTALL)


def clip(output: str) -> str:
    cleaned = _CTRL_RE.sub("", output).replace("```", "``​`")  # don't break the evidence fence
    lines = cleaned.splitlines()
    clipped = lines[-MAX_LINES:]
    text = "\n".join(clipped)
    if len(text.encode("utf-8")) > MAX_BYTES:
        text = text.encode("utf-8")[-MAX_BYTES:].decode("utf-8", "ignore")
    prefix = "" if len(lines) <= MAX_LINES else f"... ({len(lines) - MAX_LINES} earlier lines omitted)\n"
    return prefix + text


def drop_row(text: str, item_id: str) -> str:
    kept = [ln for ln in text.splitlines() if not re.search(rf"\(items/{re.escape(item_id)}\.md\)", ln)]
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def ensure_review_row(review_path: Path, item_id: str, verification: str, retrospective: str, promotion: str) -> None:
    # Index membership is eventually-consistent: this read-modify-write can lose a
    # row if two windows update the index at once. The id allocation is the atomic
    # part; a dropped index row is self-detected by the audit (INDEX003) and
    # repaired by a re-run (which reconciles rather than duplicates).
    row = f"| {item_id} | {verification} | {retrospective} | {promotion} | [items/{item_id}.md](items/{item_id}.md) |"
    text = review_path.read_text(encoding="utf-8") if review_path.exists() else ""
    if re.search(rf"\(items/{re.escape(item_id)}\.md\)", text):
        return
    review_path.write_text(f"{text.rstrip(chr(10))}\n{row}\n", encoding="utf-8")


def run_check(command: str, timeout: int, cwd: Path) -> tuple[bool, str]:
    # cwd is the project root so a check's relative paths (`stage/hooks/tests`)
    # resolve the same way whatever directory close_work was launched from.
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout, cwd=str(cwd)
        )
    except subprocess.TimeoutExpired:
        return False, f"$ {command}\n[TIMED OUT after {timeout}s]"
    output = (proc.stdout or "") + (proc.stderr or "")
    header = f"$ {command}\n[exit {proc.returncode}]"
    return proc.returncode == 0, f"{header}\n{clip(output)}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Close a Stage work item by running its checks.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("item", help="Work item id, e.g. W-00000008.")
    parser.add_argument("--check", action="append", default=[], help="A verification command (repeatable). Runs in the platform shell.")
    parser.add_argument("--promotion", default=None, help=f"Set the promotion decision; must be one of {sorted(PROMOTION_FINAL)}.")
    parser.add_argument("--timeout", type=int, default=900, help="Per-check timeout in seconds.")
    args = parser.parse_args()

    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    item_path = stage_root / "present" / "work" / "items" / f"{args.item}.md"
    active_path = stage_root / "present" / "work" / "active.md"
    review_path = stage_root / "present" / "work" / "review.md"
    if not item_path.exists():
        print(f"{args.item}: no present item file at {item_path}", file=sys.stderr)
        return 2

    text = item_path.read_text(encoding="utf-8")
    status = field(text, "status")

    # Reconcile a re-run: an already-completed item must sit in review.md, not active.md.
    if status == "completed":
        item_path.write_text(text, encoding="utf-8")
        active_path.write_text(drop_row(active_path.read_text(encoding="utf-8"), args.item), encoding="utf-8") if active_path.exists() else None
        ensure_review_row(review_path, args.item, field(text, "verification"), field(text, "retrospective"), field(text, "promotion"))
        print(f"{args.item}: already completed; index reconciled")
        return 0
    if status not in OPEN_TO_CLOSE:
        print(f"{args.item}: status `{status}` is not active/review; refusing to close", file=sys.stderr)
        return 1

    if field(text, "retrospective") != "completed":
        print(f"{args.item}: retrospective is not completed — write it first (Completion principle)", file=sys.stderr)
        return 1
    ref = field(text, "retrospective_ref")
    if not ref or not (stage_root / "present" / "work" / "retrospectives" / f"{ref}.md").exists():
        print(f"{args.item}: retrospective_ref `{ref or 'empty'}` has no file", file=sys.stderr)
        return 1

    promotion = args.promotion if args.promotion is not None else field(text, "promotion")
    if promotion not in PROMOTION_FINAL:
        print(f"{args.item}: promotion `{promotion}` is not final {sorted(PROMOTION_FINAL)} — pass --promotion", file=sys.stderr)
        return 1

    if not args.check:
        print(f"{args.item}: no --check given; closing must run the verification checks (no silent pass)", file=sys.stderr)
        return 1

    if "## Verification\n" not in text:
        print(f"{args.item}: no '## Verification' section to record evidence into; refusing", file=sys.stderr)
        return 1

    project_root = stage_root.parent
    blocks: list[str] = []
    for command in args.check:
        ok, block = run_check(command, args.timeout, project_root)
        blocks.append(block)
        if not ok:
            print(f"{args.item}: check failed, nothing changed:\n{block}", file=sys.stderr)
            return 1
        if re.search(r"Ran 0 tests", block):
            print(f"{args.item}: WARNING a check reported 'Ran 0 tests' — it may verify nothing", file=sys.stderr)

    evidence = "Executed this session:\n\n```\n" + "\n\n".join(blocks) + "\n```"
    updated = set_section(text, "Verification", evidence)
    updated = set_field(updated, "verification", "passed")
    updated = set_field(updated, "promotion", promotion)
    updated = set_field(updated, "status", "completed")
    item_path.write_text(updated, encoding="utf-8")

    # Index last, derived from the new status, so a re-run always converges.
    if active_path.exists():
        active_path.write_text(drop_row(active_path.read_text(encoding="utf-8"), args.item), encoding="utf-8")
    ensure_review_row(review_path, args.item, "passed", "completed", promotion)
    print(f"{args.item}: closed (verification passed on {len(args.check)} check(s), status completed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
