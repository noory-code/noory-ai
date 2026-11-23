# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
"""The record-derived index a session starts with, and the cap on its size (DE-00000100).

A session's top layer carries one line per record — never a body — so the session knows
which decisions and rule candidates exist and opens the body itself. Every line is derived
from the records when the layer is built; nothing here is stored. The SessionStart hook
(`stage_context.session_context`) and the cloud brief (`scripts/subsession_brief.py`) both
build their index through `stage_context.session_index`, which fits its blocks with
`fit_blocks` below.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import ACTIVE_TOPOLOGY_V4, active_topology  # noqa: E402
import stage_topology  # noqa: E402
from stage_record_paths import record_paths  # noqa: E402
from stage_work import parse_frontmatter  # noqa: E402

# The whole text a session receives at start. DE-00000100 chose the number from the size the
# text had then (6,484 characters), not from a measurement of what a session uses.
SESSION_CONTEXT_CHAR_LIMIT = 10_000
SESSION_CONTEXT_LINE_LIMIT = 160

# Decisions whose status is one of these are in force; any other status is shown on the line.
DECISION_SETTLED_STATUSES = frozenset({"decided", "promoted", "approved"})

# The consolidated rule-candidate list a consolidation session writes
# (`skills/stage-retrospective/rule-promotion.md`), relative to `.stage/`.
RULE_CANDIDATE_LIST = "state/rule-candidates.md"
# New retrospectives since the list's `through:` id that make a consolidation session due.
CONSOLIDATION_DUE_AFTER = 20
# What a bullet of that list says when the consolidation session proposes promoting it.
PROMOTE_PROPOSAL = "proposed: promote"

RULE_CANDIDATE_SECTION = re.compile(
    r"^## Rule candidate[ \t]*\r?\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
# What a retrospective writes in `## Rule candidate` to say it has none. A machine-written
# retrospective leaves a `driver-generated` placeholder for whoever merges the run.
NO_CANDIDATE_WORDS = frozenset({"없음", "없다", "none", "n/a", "nothing"})
NO_CANDIDATE_PREFIX = "driver-generated"


def id_sort_key(item_id: str) -> tuple[int, str]:
    """Numeric ID portion first: lexical order misranks variable-width IDs
    (Q-999 would outrank Q-1000)."""
    match = re.search(r"(\d+)", item_id)
    return (int(match.group(1)) if match else -1, item_id)


def bounded_record_line(
    item_id: str, title: str, suffix: str, limit: int = SESSION_CONTEXT_LINE_LIMIT
) -> str:
    """One bounded line per injected record — the budget caps size, not just
    count. Overlength truncates the TITLE while reserving the suffix: the
    `(blocks: ...)` / `(priority: ...)` linkage is the actionable part."""
    prefix = f"- {item_id} ".rstrip() + (" " if title or suffix else "")
    title = " ".join(title.split())
    room = max(8, limit - len(prefix) - len(suffix))
    if len(title) > room:
        title = title[: room - 1] + "…"
    return (prefix + title + suffix).rstrip()


def record_files(directory: Path) -> list[Path]:
    """Individual record files of an artifact family (skips readme/template files).

    `record_paths` owns which underscore files are records: it drops the
    templates at the family root and keeps the `_epic.md` and `_story.md`
    cards inside hierarchy folders.
    """
    try:
        files = record_paths(directory)
    except OSError:
        return []
    return [path for path in files if path.name.lower() != "readme.md"]


def record_title(path: Path, record_id: str = "") -> str:
    """A record's title: its `title:` field, else its first H1 without the leading id."""

    title = (parse_frontmatter(path).get("title") or "").strip()
    if title:
        return title
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r"^# +(.+?)[ \t]*$", text, re.MULTILINE)
    if match is None:
        return ""
    heading = match.group(1).strip()
    for prefix in (record_id, path.stem):
        if prefix and heading.startswith(prefix):
            return heading[len(prefix):].lstrip(" :—-").strip()
    return heading


def decision_roots(stage_root: Path) -> tuple[str, ...]:
    """Folders, relative to `.stage/`, whose decisions bind work: pending first, then official.

    The decision archive is left out: it holds closed records that no longer bind
    (spent venue exceptions). Empty outside the current topology, whose index this is.
    """
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return ()
    return tuple(
        path.rsplit("/", 1)[0]
        for path in stage_topology.resolve_artifact_reference("DE-00000000").candidate_paths[:2]
    )


def decision_title_lines(stage_root: Path) -> list[str]:
    """Every binding decision as `- <id> <title>`, newest first, one bounded line each."""

    records: dict[str, tuple[str, str]] = {}
    for root in decision_roots(stage_root):
        for path in record_files(stage_root / root):
            if path.name.lower() == "index.md":
                continue
            fields = parse_frontmatter(path)
            record_id = (fields.get("id") or path.stem).strip()
            if re.fullmatch(r"DE?-\d{3,}", record_id) is None or record_id in records:
                continue
            status = (fields.get("status") or "").strip().lower()
            suffix = "" if not status or status in DECISION_SETTLED_STATUSES else f" ({status})"
            records[record_id] = (record_title(path, record_id), suffix)
    return [
        bounded_record_line(record_id, *records[record_id])
        for record_id in sorted(records, key=id_sort_key, reverse=True)
    ]


def retrospective_roots(stage_root: Path) -> tuple[str, ...]:
    """Folders, relative to `.stage/`, that hold retrospectives: current first, then archived."""

    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return ()
    return tuple(stage_topology.retrospective_locations())


def _retrospectives(stage_root: Path) -> list[tuple[str, Path]]:
    found: dict[str, Path] = {}
    for root in retrospective_roots(stage_root):
        for path in record_files(stage_root / root):
            if re.fullmatch(r"R-\d{3,}", path.stem):
                found.setdefault(path.stem, path)
    return sorted(found.items(), key=lambda entry: id_sort_key(entry[0]))


def _has_rule_candidate(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    match = RULE_CANDIDATE_SECTION.search(text)
    if match is None:
        return False
    body = HTML_COMMENT.sub("", match.group("body")).strip()
    said = body.lstrip("-* ").rstrip(". ").lower()
    if not said or said in NO_CANDIDATE_WORDS:
        return False
    return not said.startswith(NO_CANDIDATE_PREFIX)


def candidate_bullets(list_text: str) -> list[tuple[str, bool]]:
    """Each top-level bullet of the list as (its bounded first line, whether it proposes promotion).

    A wrapped bullet states `proposed: promote` on an indented line, so the proposal is read
    from the whole bullet while only its first line is shown.
    """
    bullets: list[list[str]] = []
    open_bullet = False
    for line in list_text.splitlines():
        if line.startswith("- "):
            bullets.append([line[2:]])
            open_bullet = True
        elif open_bullet and line[:1] in (" ", "\t") and line.strip():
            bullets[-1].append(line)
        elif line.strip():
            open_bullet = False
    found = []
    for parts in bullets:
        body = " ".join(parts[0].split())
        if len(body) > SESSION_CONTEXT_LINE_LIMIT - 2:
            body = body[: SESSION_CONTEXT_LINE_LIMIT - 3] + "…"
        whole = " ".join(" ".join(parts).split()).lower()
        found.append((f"- {body}", PROMOTE_PROPOSAL in whole))
    return found


def promote_first(bullets: list[tuple[str, bool]]) -> list[str]:
    """Candidate lines with the `proposed: promote` ones first, each group in the list's order.

    The index gives up candidates from the end (`fit_blocks`), so the ones a person is asked
    to decide on are the last to go.
    """
    return [line for line, promote in bullets if promote] + [
        line for line, promote in bullets if not promote
    ]


def rule_candidate_lines(stage_root: Path) -> tuple[list[str], list[str]]:
    """The open rule candidates, and the fixed lines that say how current they are.

    Returns `(candidates, status)`. `candidates` are the top-level bullets of the
    consolidated list, one bounded line each: the `proposed: promote` ones first, then the
    rest, each group in the list's order. `status` says how many
    retrospectives are newer than the list and whether a consolidation session is due; with
    no list it says how many retrospectives carry a candidate and where they are.
    """
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return [], []
    list_relative = RULE_CANDIDATE_LIST
    list_path = stage_root / list_relative
    retrospectives = _retrospectives(stage_root)
    if not list_path.is_file():
        carrying = sum(1 for _record_id, path in retrospectives if _has_rule_candidate(path))
        if not carrying:
            return [], []
        return [], [
            f"- No consolidated list yet (`.stage/{list_relative}`). {carrying} retrospectives "
            "state a candidate under `## Rule candidate`; search "
            + " and ".join(f"`.stage/{root}/`" for root in retrospective_roots(stage_root))
            + " for that heading."
        ]
    through = (parse_frontmatter(list_path).get("through") or "").strip()
    try:
        text = list_path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    candidates = promote_first(candidate_bullets(text))
    if re.fullmatch(r"R-\d{3,}", through):
        covered = id_sort_key(through)
        newer = sum(1 for record_id, _path in retrospectives if id_sort_key(record_id) > covered)
        status = (
            f"- `.stage/{list_relative}` covers retrospectives through {through}; "
            f"{newer} are newer."
        )
        if newer >= CONSOLIDATION_DUE_AFTER:
            status += (
                f" A consolidation session is due ({CONSOLIDATION_DUE_AFTER} or more): "
                "`skills/stage-retrospective/rule-promotion.md` in the installed Stage plugin."
            )
    else:
        status = (
            f"- `.stage/{list_relative}` declares no `through: R-<id>`, so how many "
            "retrospectives are newer than it is unknown."
        )
    return candidates, [status]


def find_lines(stage_root: Path) -> list[str]:
    """How a session gets from a line of the index, or from a word, to a record body."""

    roots = decision_roots(stage_root)
    if not roots:
        return []
    pending, official = roots
    retrospectives = retrospective_roots(stage_root)[-1]
    return [
        "- Every line below names a record, not its content. Open the body before relying on "
        "it: a title says the topic, not what was chosen.",
        f"- A decision body is `.stage/{pending}/<id>.md` or `.stage/{official}/<id>.md`.",
        "- By topic: search `.stage/` for the word with your search tool, in the project's "
        f"document language too; retrospectives are in `.stage/{retrospectives}/`.",
    ]


@dataclass
class Block:
    """One block of the session index.

    `shed` is 0 for a block that is never shortened (what the session is doing now) and
    otherwise the order in which blocks give up lines when the text is over its limit:
    the lowest number first, and within a block the last line first. `noun` and `read_at`
    make the one line that says how many lines were left out and where to read them.
    """

    heading: str
    lines: list[str] = field(default_factory=list)
    tail: list[str] = field(default_factory=list)
    shed: int = 0
    noun: str = "lines"
    read_at: str = ""
    separator: str = "\n"
    dropped: int = 0

    def render(self) -> str:
        if not self.lines and not self.tail and not self.dropped:
            return ""
        body = self.separator.join(self.lines)
        parts = [f"\n{self.heading}"] if self.heading else []
        if body:
            parts.append(body)
        if self.dropped:
            parts.append(f"- …{self.dropped} {self.noun} not shown — read {self.read_at}")
        parts.extend(self.tail)
        return "\n".join(parts)


def render_blocks(blocks: list[Block]) -> str:
    return "\n".join(text for text in (block.render() for block in blocks) if text)


def fit_blocks(blocks: list[Block], limit: int) -> str:
    """Render `blocks` in at most `limit` characters.

    Lines are dropped one at a time from the sheddable block with the lowest `shed` number
    that still has lines. When every sheddable line is gone and the text is still too long,
    the end is cut and the last line says so: the limit holds whatever the records contain.
    """
    text = render_blocks(blocks)
    for block in sorted((block for block in blocks if block.shed), key=lambda block: block.shed):
        while len(text) > limit and block.lines:
            block.lines.pop()
            block.dropped += 1
            text = render_blocks(blocks)
        if len(text) <= limit:
            return text
    if len(text) <= limit:
        return text
    marker = f"\n…cut at {max(limit, 0)} characters — read `.stage/index.md` for the rest"
    return (text[: max(limit - len(marker), 0)].rstrip() + marker)[: max(limit, 0)]
