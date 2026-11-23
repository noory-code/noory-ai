"""Audit checks for the evidence a close leaves and the review commands that produce it.

Codes:
- WORK030 (warning): a closed card has no `- Load at close` line although it closed on a
  later day than the first card of this project that carries the line.
- REVIEW003 (warning): a review command in `settings.json` does not tell the reviewer to
  name how it judged each criterion (`method`: `ran`, `read`, `unable`).

Both describe a project that runs an older Stage, or settings written for one: `close_work.py`
writes the load line on every close (`scripts/work_load.py`) and rejects a verdict whose
criteria carry no `method` (`operations/review.md`, "How the reviewer judges").

The cut-off for WORK030 is taken from the project's own records, not from a date or a card id
of the repository where the line was introduced: another project's ids and upgrade day differ.
The earliest `- Load at close` day among the project's cards is the day its Stage began to
write the line. Cards closed on that same day are not judged, because the day alone cannot
say which of them closed before the upgrade. A project with no such line gets no finding.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Iterable, Union

# Evaluated at import time, so no `X | Y` syntax: Stage runs on Python 3.9.
Report = Callable[[str, str, Union[Path, str]], None]

_CHECKS_DAY_RE = re.compile(r"(?m)^- Checks at close (\d{4}-\d{2}-\d{2}):")
_LOAD_DAY_RE = re.compile(r"(?m)^- Load at close (\d{4}-\d{2}-\d{2}):")
# A command "says method" when it names the key and all three of its values as words.
METHOD_WORDS = ("method", "ran", "read", "unable")
REVIEW_COMMAND_GROUPS = ("reviewers", "strengths")


def _last_day(pattern: "re.Pattern[str]", text: str) -> str:
    days = pattern.findall(text)
    return days[-1] if days else ""


def audit_load_lines(card_paths: Iterable[Path], warn: Report) -> None:
    """WORK030: closed cards without a load line, judged from the project's first one on."""

    closed: list[tuple[Path, str, str]] = []
    for path in card_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        closed_day = _last_day(_CHECKS_DAY_RE, text)
        if closed_day:
            closed.append((path, closed_day, _last_day(_LOAD_DAY_RE, text)))
    load_days = [load_day for _path, _closed_day, load_day in closed if load_day]
    if not load_days:
        return
    first_load_day = min(load_days)
    for path, closed_day, load_day in closed:
        if not load_day and closed_day > first_load_day:
            warn(
                "WORK030",
                f"Closed on {closed_day} with no `- Load at close` line, although this "
                f"project's cards carry the line since {first_load_day}. The card was closed "
                "by an older Stage or completed by hand, so its attempts and review rounds "
                "were not counted. Do not write the line by hand: confirm which Stage version "
                "the closing session ran (a stale plugin cache is the usual cause) and close "
                "later cards with `close_work.py` of the current version.",
                path,
            )


def says_method(command: str) -> bool:
    return all(re.search(rf"\b{word}\b", command) for word in METHOD_WORDS)


def review_commands(review: Any) -> list[tuple[str, str]]:
    """Every non-empty review command of the `review` block as (settings key, command)."""

    if not isinstance(review, dict):
        return []
    found = []
    for group in REVIEW_COMMAND_GROUPS:
        commands = review.get(group)
        if not isinstance(commands, dict):
            continue
        for name, command in commands.items():
            if isinstance(command, str) and command.strip():
                found.append((f"review.{group}.{name}", command))
    return found


def audit_review_methods(review: Any, settings_path: Path, warn: Report) -> None:
    """REVIEW003: review commands that do not ask for each criterion's `method`."""

    for key, command in review_commands(review):
        if says_method(command):
            continue
        missing = ", ".join(
            f"`{word}`" for word in METHOD_WORDS if not re.search(rf"\b{word}\b", command)
        )
        warn(
            "REVIEW003",
            f"{key} does not tell the reviewer to name how it judged each criterion (missing "
            f"the word(s) {missing}). `close_work.py` rejects a verdict whose criteria carry no "
            "`method`, so a close review through this command fails. Add the `method` "
            "sentences from the `review` comment of the plugin's "
            "`templates/v4/project-stage/settings.jsonc` (`operations/review.md`, \"How the "
            "reviewer judges\"). A command that keeps its prompt in another file is reported "
            "too: state the method in that file and name `method`, `ran`, `read`, `unable` in "
            "the command.",
            settings_path,
        )
