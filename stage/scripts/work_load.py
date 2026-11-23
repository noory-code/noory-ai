#!/usr/bin/env python3
"""Count what a card cost to land, and keep that count on the card.

Whether a control carries load shows in how many attempts, rejected reviews, and
driver failures a card needed. Those events live in the shared work log, which is
not committed, so a session without that log (a cloud session, for one) cannot
count them afterwards. `close_work.py` therefore writes one `- Load at close` line
into the card's `## Verification` from the work log and the card as they stand at
close. This module owns that line: counting, rendering, parsing, and the table
over closed cards.

Usage:
    python3 stage/scripts/work_load.py --project-root . [--closed-since YYYY-MM-DD] [W-id ...]

Prints one Markdown table row per closed card and a totals row. A card closed
before the line existed shows its rejected reviews, which were already recorded,
and `not recorded` elsewhere.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from stage_work import load_all_work_items  # noqa: E402

NOT_RECORDED = "not recorded"
UNKNOWN = "unknown"
MAX_REASON_CHARS = 200

_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_SECTION_RE = re.compile(r"(?m)^### [^\r\n]*\r?$")
_DISPOSITIONS_RE = re.compile(r"(?m)^Review dispositions \(JSON\):[ \t]*\r?\n([^\r\n]+)$")
_REVIEW_LINE_RE = re.compile(
    r"(?m)^- Review at close (\d{4}-\d{2}-\d{2}) by [^:\r\n]+: (approved|rejected)\b"
)
_CHECKS_LINE_RE = re.compile(r"(?m)^- Checks at close (\d{4}-\d{2}-\d{2}):")
_LOAD_LINE_RE = re.compile(
    r"(?m)^- Load at close (\d{4}-\d{2}-\d{2}): attempts (\d+), review FAIL rounds (\d+), "
    r"repeated findings (\d+|unknown), driver rounds (\d+), "
    r"driver failures (\d+) \(timed out (\d+)\)[ \t]*\r?$"
)


@dataclass(frozen=True)
class Load:
    """What one card took to close. `repeated_findings` is None when it cannot be counted."""

    attempts: int
    review_fail_rounds: int
    repeated_findings: Optional[int]
    driver_rounds: int
    driver_failures: int
    timeouts: int
    failure_reasons: tuple[str, ...] = ()


def _sections(log_text: str, heading: str) -> list[str]:
    """Bodies of every `### <heading>` section of a work log, in order."""

    marks = list(_SECTION_RE.finditer(log_text))
    bodies = []
    for index, mark in enumerate(marks):
        if mark.group(0).strip() != f"### {heading}":
            continue
        end = marks[index + 1].start() if index + 1 < len(marks) else len(log_text)
        bodies.append(log_text[mark.end() : end])
    return bodies


def _line_field(body: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(label)}:[ \t]*([^\r\n]*)$", body)
    return " ".join(_CTRL_RE.sub("", match.group(1)).split()) if match else ""


def _disposition_findings(report_body: str) -> Optional[list[str]]:
    """Findings one executor report answered; None when it answered no review."""

    match = _DISPOSITIONS_RE.search(report_body)
    if not match:
        return None
    try:
        entries = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    if not isinstance(entries, list) or not entries:
        return None
    return [
        entry["finding"]
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("finding"), str)
    ]


def rejected_reviews(card_text: str) -> int:
    """Close reviews on the card that sent the work back."""

    return sum(1 for match in _REVIEW_LINE_RE.finditer(card_text) if match.group(2) == "rejected")


def count_load(log_text: str, card_text: str) -> Load:
    """Count a card's load from its work log (may be empty) and its own text.

    The driver and a hand-run close record a failed review in different places:
    the driver's next executor report answers it with `Review dispositions (JSON)`
    in the work log, and `close_work.py` leaves a `rejected` line on the card. One
    round can appear in both, so the larger count is taken, not the sum.
    """

    reports = _sections(log_text, "Executor report")
    answered = [findings for findings in map(_disposition_findings, reports) if findings]
    fail_rounds = max(len(answered), rejected_reviews(card_text))
    # A round's findings can only be compared with the next round's when the log
    # holds every answered round; a fresh log in a cloud session does not.
    repeated: Optional[int] = None
    if len(answered) >= fail_rounds:
        repeated = sum(
            1
            for earlier, later in zip(answered, answered[1:])
            if set(earlier) & set(later)
        )
    failures = _sections(log_text, "Driver failure")
    reasons = []
    for body in failures:
        reason = _line_field(body, "Reason") or "(no reason)"
        role = _line_field(body, "Role") or "driver"
        reasons.append(f"{role} — {reason}"[:MAX_REASON_CHARS])
    return Load(
        # Each rejected review is followed by one more attempt, and the closing
        # attempt counts even when no executor reported it.
        attempts=max(len(reports), fail_rounds + 1),
        review_fail_rounds=fail_rounds,
        repeated_findings=repeated,
        driver_rounds=len(_sections(log_text, "Driver commands")),
        driver_failures=len(failures),
        timeouts=sum(1 for reason in reasons if "timed out" in reason),
        failure_reasons=tuple(reasons),
    )


def load_record_lines(load: Load, day: str) -> str:
    """The card's committed record of its load: one count line, one line per driver failure."""

    repeated = UNKNOWN if load.repeated_findings is None else str(load.repeated_findings)
    lines = [
        f"- Load at close {day}: attempts {load.attempts}, "
        f"review FAIL rounds {load.review_fail_rounds}, repeated findings {repeated}, "
        f"driver rounds {load.driver_rounds}, "
        f"driver failures {load.driver_failures} (timed out {load.timeouts})"
    ]
    lines += [f"  - Driver failure: {reason}" for reason in load.failure_reasons]
    return "\n".join(lines)


def parse_load_record(card_text: str) -> Optional[tuple[str, Load]]:
    """The last `- Load at close` line of a card as (date, Load), or None when it has none."""

    matches = list(_LOAD_LINE_RE.finditer(card_text))
    if not matches:
        return None
    day, attempts, fail_rounds, repeated, rounds, failures, timeouts = matches[-1].groups()
    return day, Load(
        attempts=int(attempts),
        review_fail_rounds=int(fail_rounds),
        repeated_findings=None if repeated == UNKNOWN else int(repeated),
        driver_rounds=int(rounds),
        driver_failures=int(failures),
        timeouts=int(timeouts),
    )


def close_date(card_text: str) -> str:
    """The day the card's checks passed at close, or '' when it carries no close record."""

    days = [match.group(1) for match in _CHECKS_LINE_RE.finditer(card_text)]
    return days[-1] if days else ""


COLUMNS = (
    "Card",
    "Closed",
    "Attempts",
    "Review FAIL rounds",
    "Repeated findings",
    "Driver rounds",
    "Driver failures",
    "Timed out",
)


def card_row(item_id: str, card_text: str) -> list[str]:
    recorded = parse_load_record(card_text)
    day = close_date(card_text)
    if recorded is None:
        return [item_id, day, NOT_RECORDED, str(rejected_reviews(card_text))] + [NOT_RECORDED] * 4
    _day, load = recorded
    repeated = UNKNOWN if load.repeated_findings is None else str(load.repeated_findings)
    return [
        item_id,
        day,
        str(load.attempts),
        str(load.review_fail_rounds),
        repeated,
        str(load.driver_rounds),
        str(load.driver_failures),
        str(load.timeouts),
    ]


def totals_row(rows: list[list[str]]) -> list[str]:
    """Sum each column over the cards that recorded it, as `<sum> (<cards counted>)`."""

    cells = [f"Total ({len(rows)} cards)", ""]
    for column in range(2, len(COLUMNS)):
        values = [int(row[column]) for row in rows if row[column].isdigit()]
        cells.append(f"{sum(values)} ({len(values)})" if values else NOT_RECORDED)
    return cells


def load_table(stage_root: Path, item_ids: list[str], closed_since: str) -> str:
    """A Markdown table of the load of closed cards, oldest close first."""

    wanted = set(item_ids)
    rows = []
    for item in load_all_work_items(stage_root):
        if wanted and item.item_id not in wanted:
            continue
        text = item.path.read_text(encoding="utf-8")
        day = close_date(text)
        if not day or (closed_since and day < closed_since):
            continue
        rows.append(card_row(item.item_id, text))
    rows.sort(key=lambda row: (row[1], row[0]))
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    lines += ["| " + " | ".join(row) + " |" for row in [*rows, totals_row(rows)]]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--closed-since",
        default="",
        metavar="YYYY-MM-DD",
        help="Only cards whose checks passed at close on or after this day.",
    )
    parser.add_argument("items", nargs="*", help="Work item ids; default: every closed card.")
    args = parser.parse_args()
    if args.closed_since and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.closed_since):
        print(f"--closed-since `{args.closed_since}` is not YYYY-MM-DD", file=sys.stderr)
        return 2
    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    print(load_table(stage_root, args.items, args.closed_since))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
