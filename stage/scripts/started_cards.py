#!/usr/bin/env python3
"""List the cards in progress across fetched branches, and the questions waiting in records.

A PO session that takes over reads this instead of walking branches by hand
(DE-00000099, DE-00000103). A card is in progress when a record for it sits under the started
cards of HEAD, of the default branch, or of a fetched branch the default branch
has not merged, and the default branch has not archived it. A branch merged by
squash still looks unmerged to git; its cards are archived on the default branch
and drop out for that reason.

A card can sit on several branches (a PM session's branch and the
PO session's copy). The branch whose last commit touched the card's record most
recently is listed first and is the one to read: after a card starts, only the
PO session edits its record. Planned cards are not in progress and are not
listed. This reads fetched refs and the checkout's records; it never touches the
network and changes nothing.

Two more lists serve a take-over with no open PM session (W-00000406). Open
observations are listed because they wait for a card or a decision. Sessions whose
commits changed a card record are listed newest first: registering, starting,
closing, and archiving a card are the PO session's commits, so the newest
session there that is not the reader is the earlier PO session. A commit names its
session only when the host writes
the session id into the commit message (Claude Code cloud sessions add a
`Claude-Session:` trailer); elsewhere the list is empty.

Usage:
    python3 stage/scripts/started_cards.py --project-root . [--base origin/main]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS.parent / "hooks"))
sys.path.insert(0, str(SCRIPTS))
from lifecycle_paths import v4_lifecycle_paths  # noqa: E402
from stage_paths import ACTIVE_TOPOLOGY_V4, active_topology  # noqa: E402
from stage_context import observation_root  # noqa: E402
from stage_record_ids import default_remote  # noqa: E402
from stage_record_paths import record_paths  # noqa: E402
from stage_work import DECISION_FINAL_STATUSES, parse_frontmatter  # noqa: E402

WORK_ID_RE = re.compile(r"W-\d{8}")
WAITING_PREFIX = "Waiting on user:"
SESSION_ID_RE = re.compile(r"\bsession_[0-9A-Za-z]{8,}\b")
SESSION_COMMIT_LIMIT = 300
SESSION_LIST_LIMIT = 5
SHOWN_FIELDS = ("status", "verification", "review")
# Session tags (DE-00000103). The earlier pair marks sessions created before that decision;
# a PO session that takes over still finds them in the session list.
ROLE_TAGS_LINE = (
    "Role tags: stage-role:po on the PO session; stage-role:<plan|pm|verify|research> and "
    "stage-po:<PO session id> on each session it creates"
)
EARLIER_TAGS_LINE = (
    "Earlier tags: stage-orchestrator (a PO session), stage-main-session:<id> (a session "
    "under the PO session <id>)"
)


def git_text(project_root: Path, *args: str) -> str | None:
    """Run one git command and return its output as UTF-8 text, or None on failure."""

    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(project_root), capture_output=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="replace")


def git_lines(project_root: Path, *args: str) -> list[str] | None:
    """Run one git command; return its NUL- or newline-separated output, or None on failure."""

    text = git_text(project_root, *args)
    if text is None:
        return None
    separator = "\0" if "\0" in text else "\n"
    return [line for line in text.split(separator) if line]


def unmerged_refs(project_root: Path, base: str) -> list[str]:
    """Fetched local and remote-tracking branches that `base` has not merged."""

    refs = git_lines(
        project_root,
        "for-each-ref",
        f"--no-merged={base}",
        "--format=%(refname:short)",
        "refs/heads",
        "refs/remotes",
    )
    return [ref for ref in refs or () if not ref.endswith("/HEAD")]


def ref_paths(project_root: Path, ref: str, roots: list[str]) -> list[str]:
    """Every file path a ref holds under the given project-relative roots."""

    return git_lines(project_root, "ls-tree", "-r", "-z", "--name-only", ref, "--", *roots) or []


def record_sessions(project_root: Path, refs: list[str]) -> list[str]:
    """Sessions named in commits that changed a planned, started, or archived card.

    One line per session: its id, and the date and subject of its newest such
    commit. Only the last `SESSION_COMMIT_LIMIT` commits are read, and at most
    `SESSION_LIST_LIMIT` sessions are returned.
    """

    text = git_text(
        project_root,
        "log",
        f"--max-count={SESSION_COMMIT_LIMIT}",
        "--date-order",
        "--format=%x1e%cs%x1f%s%x1f%B",
        *refs,
        "--",
        *[(Path(".stage") / root).as_posix() for root in lifecycle_roots(project_root / ".stage")],
    )
    found: dict[str, str] = {}
    for entry in (text or "").split("\x1e"):
        day, _, rest = entry.partition("\x1f")
        subject, _, body = rest.partition("\x1f")
        for session_id in SESSION_ID_RE.findall(body):
            found.setdefault(session_id, f"{session_id}: {day} {subject.strip()}")
    return list(found.values())[:SESSION_LIST_LIMIT]


def lifecycle_roots(stage_root: Path) -> tuple[str, str, str]:
    """The planned, started, and archived card roots, relative to `.stage`."""

    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        return paths.planned_cards, paths.current_cards, paths.archive_cards
    return (
        Path("future", "backlog", "items").as_posix(),
        Path("present", "work", "items").as_posix(),
        Path("past", "work", "archive", "items").as_posix(),
    )


def default_base(project_root: Path) -> str | None:
    """The default branch as a fetched ref: the remote's HEAD, else main or master."""

    remote = default_remote(project_root)
    candidates: list[str] = []
    if remote:
        head = git_text(project_root, "symbolic-ref", "-q", "--short", f"refs/remotes/{remote}/HEAD")
        if head and head.strip():
            candidates.append(head.strip())
        candidates += [f"{remote}/main", f"{remote}/master"]
    candidates += ["main", "master"]
    for candidate in candidates:
        if git_text(project_root, "rev-parse", "-q", "--verify", f"{candidate}^{{commit}}"):
            return candidate
    return None


def project_tag(project_root: Path) -> str:
    """The session tag of this project: `stage-project:<owner>/<name>` from the remote's URL.

    Without a remote the project folder's name stands in. A PO session copies
    this line instead of spelling the repository itself, because a session whose
    tag is spelled differently silently drops out of the take-over list.
    """

    remote = default_remote(project_root)
    url = (git_text(project_root, "remote", "get-url", remote) or "").strip() if remote else ""
    parts = [part for part in re.split(r"[/:\\]", url[:-4] if url.endswith(".git") else url) if part]
    name = "/".join(parts[-2:]) if len(parts) >= 2 else project_root.name
    return f"stage-project:{name}"


def is_waiting(line: str) -> bool:
    return line.lstrip("-* ").startswith(WAITING_PREFIX)


def frontmatter_scalars(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines() if end != -1 else ():
        match = re.match(r"^([A-Za-z_]+):[ \t]*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def next_action(text: str) -> list[str]:
    match = re.search(r"(?ms)^## Next action[ \t]*\n(.*?)(?=^## |\Z)", text)
    return [line.strip() for line in (match.group(1) if match else "").splitlines() if line.strip()]


def is_card_record(path: str, root: str) -> bool:
    relative = Path(path).relative_to(root)
    if relative.suffix != ".md":
        return False
    return len(relative.parts) > 1 or not (
        relative.name.startswith("_") or relative.name == "README.md"
    )


def read_refs(project_root: Path, base: str) -> list[str]:
    """HEAD, the base, and each unmerged fetched branch, one ref per distinct commit."""

    refs: list[str] = []
    seen_commits: set[str] = set()
    for ref in ["HEAD", base, *sorted(unmerged_refs(project_root, base))]:
        commit = (git_text(project_root, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}") or "").strip()
        if commit and commit not in seen_commits:
            seen_commits.add(commit)
            refs.append(ref)
    return refs


def started_cards(project_root: Path, base: str) -> list[dict[str, object]]:
    """Cards in progress, each with the refs that hold it, the most recently edited first."""

    _, current, archive = lifecycle_roots(project_root / ".stage")
    current_root = (Path(".stage") / current).as_posix()
    archive_root = (Path(".stage") / archive).as_posix()
    archived = {
        match
        for path in ref_paths(project_root, base, [archive_root])
        for match in WORK_ID_RE.findall(path)
    }
    refs = read_refs(project_root, base)

    cards: dict[str, dict[str, object]] = {}
    for ref in refs:
        for path in ref_paths(project_root, ref, [current_root]):
            if not is_card_record(path, current_root):
                continue
            if archived.intersection(WORK_ID_RE.findall(path)):
                continue
            text = git_text(project_root, "show", f"{ref}:{path}") or ""
            fields = frontmatter_scalars(text)
            item_id = fields.get("id", "")
            if not WORK_ID_RE.fullmatch(item_id) or item_id in archived:
                continue
            stamp = (git_text(project_root, "log", "-1", "--format=%ct", ref, "--", path) or "0").strip()
            copy = {
                "ref": ref,
                "path": path,
                "edited": int(stamp or 0),
                "fields": fields,
                "next_action": next_action(text),
            }
            card = cards.setdefault(item_id, {"id": item_id, "copies": []})
            card["copies"].append(copy)  # type: ignore[union-attr]
    for card in cards.values():
        card["copies"].sort(key=lambda copy: -copy["edited"])  # type: ignore[union-attr]
    return [cards[item_id] for item_id in sorted(cards)]


def open_decisions(stage_root: Path) -> list[str]:
    root = stage_root / "decisions" / "pending"
    found = []
    for path in record_paths(root) if root.is_dir() else ():
        fields = parse_frontmatter(path)
        record_id = (fields.get("id") or "").strip()
        status = (fields.get("status") or "").strip()
        if re.fullmatch(r"DE?-\d{8}", record_id) and status not in DECISION_FINAL_STATUSES:
            found.append(f"{record_id} ({status or 'no status'}): {path.relative_to(stage_root.parent).as_posix()}")
    return found


def open_questions(stage_root: Path) -> list[str]:
    root = stage_root / "state" / "questions"
    found = []
    for path in record_paths(root) if root.is_dir() else ():
        fields = parse_frontmatter(path)
        record_id = (fields.get("id") or "").strip()
        if re.fullmatch(r"Q-\d{8}", record_id) and path.stem == record_id:
            title = (fields.get("title") or "").strip()
            found.append(f"{record_id} {title}: {path.relative_to(stage_root.parent).as_posix()}")
    return found


def open_observations(stage_root: Path) -> list[str]:
    """Every observation in the live folder; a closed one leaves it for the archive."""

    root = observation_root(stage_root)
    found = []
    for path in record_paths(root) if root.is_dir() else ():
        fields = parse_frontmatter(path)
        record_id = (fields.get("id") or "").strip()
        if re.fullmatch(r"O-\d{8}", record_id) and path.stem == record_id:
            title = (fields.get("title") or "").strip()
            found.append(f"{record_id} {title}: {path.relative_to(stage_root.parent).as_posix()}")
    return found


def render(project_root: Path, base: str) -> str:
    cards = started_cards(project_root, base)
    lines = [
        f"Base: {base}",
        f"Project tag: {project_tag(project_root)}",
        ROLE_TAGS_LINE,
        EARLIER_TAGS_LINE,
        "",
        f"## Cards in progress: {len(cards)}",
        "",
    ]
    waiting: list[str] = []
    for card in cards:
        copies = card["copies"]
        first = copies[0]  # type: ignore[index]
        fields = first["fields"]
        state = ", ".join(f"{key}: {fields.get(key) or '-'}" for key in SHOWN_FIELDS)
        lines.append(f"- {card['id']} {fields.get('title', '')}".rstrip())
        lines.append(f"  - {state}")
        lines.append(f"  - read: `{first['path']}` on `{first['ref']}`")
        others = [copy["ref"] for copy in copies[1:]]  # type: ignore[index]
        if others:
            lines.append(f"  - other copies: {', '.join(f'`{ref}`' for ref in others)}")
        every_line = first["next_action"]
        actions = [line for line in every_line if not is_waiting(line)]  # type: ignore[union-attr]
        empty = "(waiting on user, listed below)" if every_line else "(empty)"
        lines.append(f"  - next action: {' / '.join(actions) if actions else empty}")
        if fields.get("status") == "blocked":
            waiting.append(f"{card['id']} is `blocked`: {' / '.join(actions) or '(no next action)'}")
        waiting += [
            f"{card['id']}: {line.lstrip('-* ').strip()}"
            for line in every_line  # type: ignore[union-attr]
            if is_waiting(line)
        ]
    stage_root = project_root / ".stage"
    waiting += [f"decision {entry}" for entry in open_decisions(stage_root)]
    waiting += [f"question {entry}" for entry in open_questions(stage_root)]
    lines += ["", f"## Waiting in the records: {len(waiting)}", "", *[f"- {entry}" for entry in waiting]]
    observations = open_observations(stage_root)
    lines += ["", f"## Open observations: {len(observations)}", "", *[f"- {entry}" for entry in observations]]
    sessions = record_sessions(project_root, read_refs(project_root, base))
    lines += [
        "",
        f"## Sessions that committed card records: {len(sessions)}",
        "",
        *[f"- {entry}" for entry in sessions],
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--base",
        default="",
        help="The default branch as a fetched ref. Default: the remote's HEAD, else main or master.",
    )
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    base = args.base or default_base(project_root) or ""
    if not base or not git_text(project_root, "rev-parse", "-q", "--verify", f"{base}^{{commit}}"):
        print(
            f"no default branch ref found ({args.base or 'tried the remote HEAD, main, master'}); "
            "fetch it, then pass --base <ref>",
            file=sys.stderr,
        )
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(render(project_root, base))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
