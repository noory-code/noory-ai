#!/usr/bin/env python3
"""Hold blocks of record ids on a started card for the PM session that works it.

A PO session hands a started card to a cloud PM session (DE-00000094, DE-00000103).
The PM session cannot reserve ids on the remote (the session proxy refuses pushes
outside its own branch), so the PO session picks the ids it may need before
handing the card over and writes them to the card's `reserved_ids:` frontmatter.
`stage_record_ids.py` counts those numbers as used here and on every fetched
branch, so no other session picks them; the PM session takes its next unused id
from the block. The command-line entry points live in `stage_record_ids.py`.
"""

from __future__ import annotations

import re
from pathlib import Path

from stage_record_ids import (
    RESERVED_FIELD,
    IdReserver,
    git_output,
    id_line_re,
    record_numbers_only,
    record_paths,
    reserved_numbers,
    used_numbers,
)

CURRENT_CARDS = Path("work", "current")


def current_card_path(stage_root: Path, item_id: str) -> Path | None:
    """The started card's own record file, or None when the card is not started."""

    root = stage_root / CURRENT_CARDS
    for path in record_paths(root) if root.is_dir() else ():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if re.search(rf"^id:[ \t]*{re.escape(item_id)}[ \t]*$", text, re.MULTILINE):
            return path
    return None


def card_reserved_ids(card: Path, prefix: str) -> list[str]:
    text = card.read_text(encoding="utf-8")
    return [f"{prefix}-{number:08d}" for number in sorted(reserved_numbers(text, prefix))]


def write_reserved_ids(card: Path, record_ids: list[str]) -> None:
    """Add ids to the card's `reserved_ids:` frontmatter line, keeping ones already there."""

    text = card.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{card} has no frontmatter")
    end = text.index("\n---", 3)
    frontmatter, rest = text[: end + 1], text[end + 1 :]
    line_re = re.compile(rf"^{RESERVED_FIELD}:[ \t]*(.*)$", re.MULTILINE)
    match = line_re.search(frontmatter)
    existing = [value.strip() for value in match.group(1).split(",")] if match else []
    merged = [value for value in existing if value]
    merged += [record_id for record_id in record_ids if record_id not in merged]
    line = f"{RESERVED_FIELD}: {', '.join(merged)}"
    if match:
        frontmatter = frontmatter[: match.start()] + line + frontmatter[match.end() :]
    else:
        frontmatter += line + "\n"
    card.write_text(frontmatter + rest, encoding="utf-8")


def reserve_block(
    project_root: Path,
    prefix: str,
    count: int,
    card: Path,
    reserver: IdReserver | None = None,
) -> list[str]:
    """Pick `count` free ids after every used one and hold them on the card."""

    used = used_numbers(project_root, prefix, reserver)
    number = (max(used) + 1) if used else 1
    block: list[str] = []
    for _ in range(count + 1000):
        if len(block) == count:
            break
        candidate = f"{prefix}-{number:08d}"
        if reserver is None or reserver.claim(candidate):
            block.append(candidate)
        number += 1
    if len(block) < count:
        raise RuntimeError(f"could not reserve {count} free {prefix} ids on the remote")
    write_reserved_ids(card, block)
    return block


def next_from_card(project_root: Path, prefix: str, card: Path) -> str | None:
    """The card's first reserved id that no record uses yet, here or on a fetched branch."""

    named = record_numbers_only(project_root / ".stage", prefix)
    code, refs_text = git_output(
        project_root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"
    )
    pattern = id_line_re(prefix)
    for ref in refs_text.split() if code == 0 else ():
        if ref.endswith("/HEAD"):
            continue
        code, matches = git_output(
            project_root,
            "grep",
            "-h",
            "-I",
            "-E",
            rf"^(id:[[:space:]]*|#[[:space:]]+){prefix}-[0-9]{{8}}",
            ref,
            "--",
            ".stage",
        )
        if code == 0:
            named.update(int(number) for number in pattern.findall(matches))
    for record_id in card_reserved_ids(card, prefix):
        if int(record_id.split("-")[1]) not in named:
            return record_id
    return None
