#!/usr/bin/env python3
"""Find record numbers already used in this checkout or on any known branch.

Parallel sessions work on different branches, and a number picked from one
checkout alone can already belong to a record on another branch: W-00000286 and
DE-00000076 collided that way. This counts one prefix (`W`, `DE`, `O`, ...)
across the working tree's `.stage/` and every local and remote-tracking branch,
and names the next free id.

Branches a session has not fetched stay invisible to that count, so the id is
also reserved on the remote (DE-00000092): a create-only push of
`refs/stage-ids/<id>` succeeds for exactly one session, and a rejected push moves
on to the next number. Ids already reserved there are counted too. When there is
no remote, it cannot be reached, or it refuses the push, the id is chosen as
before and one line on stderr says it was not reserved.

A main session that hands a started card to a sub-session can also hand it a
block of numbers (DE-00000094): `--reserve-for <W-id> --count N` picks N free ids
and writes them to that card's `reserved_ids:` frontmatter, which every other
session counts as used once the card is pushed and fetched. The sub-session then
takes its next unused id from the block with `--from-card <W-id>`, so it never
picks a number of its own.

Usage:
    python3 stage/scripts/stage_record_ids.py --project-root . DE
    python3 stage/scripts/stage_record_ids.py --project-root . --no-reserve DE
    python3 stage/scripts/stage_record_ids.py --project-root . --reserve-for W-00000001 --count 2 DE
    python3 stage/scripts/stage_record_ids.py --project-root . --from-card W-00000001 DE
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
from stage_record_paths import record_paths  # noqa: E402

PREFIX_RE = re.compile(r"^[A-Z]{1,3}$")
RUNTIME_PART = ".runtime"
RESERVE_REF_ROOT = "refs/stage-ids"
RESERVED_FIELD = "reserved_ids"
RESERVE_TIMEOUT_SECONDS = 30


def id_line_re(prefix: str) -> re.Pattern[str]:
    """Match a record's id, whether in a frontmatter `id:` line or its title heading.

    Proposals and other body-only records name their id only in the heading
    (`# P-00000004 Title`), as `stage_records.py` accepts; counting `id:` lines
    alone offered their numbers as free.
    """

    return re.compile(
        rf"^(?:id:[ \t]*|#[ \t]+){re.escape(prefix)}-(\d{{8}})(?![\d])", re.MULTILINE
    )


def local_record_numbers(stage_root: Path, prefix: str) -> set[int]:
    """Numbers named by ids in the working tree's `.stage/` records."""

    pattern = id_line_re(prefix)
    numbers: set[int] = set()
    if not stage_root.is_dir():
        return numbers
    for path in record_paths(stage_root):
        if RUNTIME_PART in path.relative_to(stage_root).parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        numbers.update(int(number) for number in pattern.findall(text))
        numbers.update(reserved_numbers(text, prefix))
    numbers.discard(0)  # templates carry the all-zero placeholder id
    return numbers


def reserved_numbers(text: str, prefix: str) -> set[int]:
    """Numbers a card's `reserved_ids:` line holds back for a sub-session."""

    id_re = re.compile(rf"\b{re.escape(prefix)}-(\d{{8}})(?![\d])")
    numbers: set[int] = set()
    for line in re.findall(rf"^{RESERVED_FIELD}:[ \t]*(.*)$", text, re.MULTILINE):
        numbers.update(int(number) for number in id_re.findall(line))
    return numbers


def record_numbers_only(stage_root: Path, prefix: str) -> set[int]:
    """Numbers that already name a record, leaving out numbers only reserved."""

    pattern = id_line_re(prefix)
    numbers: set[int] = set()
    if not stage_root.is_dir():
        return numbers
    for path in record_paths(stage_root):
        if RUNTIME_PART in path.relative_to(stage_root).parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        numbers.update(int(number) for number in pattern.findall(text))
    numbers.discard(0)
    return numbers


def git_output(
    project_root: Path, *args: str, timeout: int = 60, env: dict[str, str] | None = None
) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(project_root),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return -1, ""
    return proc.returncode, os.fsdecode(proc.stdout)


def branch_record_numbers(project_root: Path, prefix: str) -> dict[int, set[str]]:
    """Map each number used on a local or remote-tracking branch to those branches."""

    code, refs_text = git_output(
        project_root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"
    )
    if code != 0:
        return {}
    refs = [ref for ref in refs_text.split() if ref and not ref.endswith("/HEAD")]
    pattern = id_line_re(prefix)
    found: dict[int, set[str]] = {}
    for ref in refs:
        code, matches = git_output(
            project_root,
            "grep",
            "-h",
            "-I",
            "-E",
            rf"^((id:[[:space:]]*|#[[:space:]]+){prefix}-[0-9]{{8}}|{RESERVED_FIELD}:.*{prefix}-[0-9]{{8}})",
            ref,
            "--",
            ".stage",
        )
        if code not in (0, 1):  # 1 means no match on this branch
            continue
        numbers = {int(number) for number in pattern.findall(matches)}
        numbers |= reserved_numbers(matches, prefix)
        for number in numbers:
            if number:
                found.setdefault(number, set()).add(ref)
    return found


def default_remote(project_root: Path) -> str | None:
    """The remote this checkout pushes to, read from git config.

    The current branch's `branch.<name>.remote` wins; otherwise `origin`, or the
    only remote when there is exactly one. Stage keeps no setting of its own.
    """

    code, remotes_text = git_output(project_root, "remote")
    if code != 0:
        return None
    remotes = remotes_text.split()
    code, branch = git_output(project_root, "symbolic-ref", "--short", "-q", "HEAD")
    if code == 0 and branch.strip():
        code, configured = git_output(
            project_root, "config", "--get", f"branch.{branch.strip()}.remote"
        )
        if code == 0 and configured.strip() in remotes:
            return configured.strip()
    if "origin" in remotes:
        return "origin"
    return remotes[0] if len(remotes) == 1 else None


def _network_env() -> dict[str, str]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"  # never wait on a credential prompt
    env["GCM_INTERACTIVE"] = "never"
    return env


class IdReserver:
    """Reserve ids on the project's remote as `refs/stage-ids/<id>`.

    A failure to reach the remote or to push there turns reservation off for the
    rest of the run; ids are then chosen from what this checkout can see, and
    `unreserved_note` explains why.
    """

    def __init__(self, project_root: Path, remote: str | None = None) -> None:
        self.project_root = project_root
        self.remote = remote if remote is not None else default_remote(project_root)
        self.reason = "" if self.remote else "no git remote"
        self.reserved: set[str] = set()
        self._remote_ids: set[str] | None = None

    @property
    def available(self) -> bool:
        return not self.reason

    def _disable(self, reason: str) -> None:
        if not self.reason:
            self.reason = reason

    def remote_ids(self) -> set[str]:
        """Every id reserved on the remote; empty once reservation is off."""

        if self._remote_ids is not None or not self.available:
            return self._remote_ids or set()
        code, text = git_output(
            self.project_root,
            "ls-remote",
            "--refs",
            str(self.remote),
            f"{RESERVE_REF_ROOT}/*",
            timeout=RESERVE_TIMEOUT_SECONDS,
            env=_network_env(),
        )
        if code != 0:
            self._disable(f"remote {self.remote} could not be read")
            return set()
        prefix = f"{RESERVE_REF_ROOT}/"
        self._remote_ids = {
            fields[1][len(prefix):]
            for fields in (line.split() for line in text.splitlines())
            if len(fields) == 2 and fields[1].startswith(prefix)
        }
        return self._remote_ids

    def remote_numbers(self, prefix: str) -> set[int]:
        pattern = re.compile(rf"{re.escape(prefix)}-(\d{{8}})")
        return {
            int(match.group(1))
            for match in map(pattern.fullmatch, self.remote_ids())
            if match and int(match.group(1))
        }

    def _marker_commit(self, record_id: str) -> str:
        """A one-commit object naming the id, so the push never uploads branch work."""

        code, tree = git_output(self.project_root, "hash-object", "-t", "tree", "-w", "--stdin")
        if code != 0 or not tree.strip():
            return ""
        env = dict(os.environ)
        for role in ("AUTHOR", "COMMITTER"):
            env.setdefault(f"GIT_{role}_NAME", "Stage")
            env.setdefault(f"GIT_{role}_EMAIL", "stage@localhost")
        code, commit = git_output(
            self.project_root,
            "commit-tree",
            tree.strip(),
            "-m",
            # The nonce keeps two sessions from building the same commit in the
            # same second; an identical object would make the second push a no-op
            # that reports success.
            f"stage-id {record_id}\n\nnonce: {uuid.uuid4().hex}",
            env=env,
        )
        return commit.strip() if code == 0 else ""

    def claim(self, record_id: str) -> bool:
        """Return False only when the remote already holds this id.

        True means the id was reserved now, or reservation is off and the caller
        proceeds as it did before reservation existed.
        """

        if not self.available:
            return True
        if record_id in self.remote_ids():
            return False
        if not self.available:
            return True
        commit = self._marker_commit(record_id)
        if not commit:
            self._disable("could not write the reservation commit")
            return True
        ref = f"{RESERVE_REF_ROOT}/{record_id}"
        code, _ = git_output(
            self.project_root,
            "push",
            "--quiet",
            "--no-verify",
            f"--force-with-lease={ref}:",
            str(self.remote),
            f"{commit}:{ref}",
            timeout=RESERVE_TIMEOUT_SECONDS,
            env=_network_env(),
        )
        if code == 0:
            self.reserved.add(record_id)
            return True
        # A rejected lease and an unreachable remote both exit non-zero; only
        # the ref now existing on the remote says another session holds it.
        code, text = git_output(
            self.project_root,
            "ls-remote",
            "--refs",
            str(self.remote),
            ref,
            timeout=RESERVE_TIMEOUT_SECONDS,
            env=_network_env(),
        )
        if code == 0 and text.strip():
            if self._remote_ids is not None:
                self._remote_ids.add(record_id)
            return False
        self._disable(f"remote {self.remote} refused the push to {RESERVE_REF_ROOT}/")
        return True

    def unreserved_note(self, record_id: str) -> str:
        """One line for stderr when `record_id` was not reserved, else empty."""

        if record_id in self.reserved:
            return ""
        return (
            f"{record_id}: not reserved on the remote ({self.reason or 'reservation off'}); "
            "fetch before registering and push the record right after"
        )


def next_record_id(
    project_root: Path, prefix: str, reserver: IdReserver | None = None
) -> str:
    used = local_record_numbers(project_root / ".stage", prefix) | set(
        branch_record_numbers(project_root, prefix)
    )
    if reserver is not None:
        used |= reserver.remote_numbers(prefix)
    number = (max(used) + 1) if used else 1
    for _ in range(1000):
        candidate = f"{prefix}-{number:08d}"
        if reserver is None or reserver.claim(candidate):
            return candidate
        number += 1
    raise RuntimeError(f"could not reserve a free {prefix} id on the remote")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--no-reserve",
        action="store_true",
        help="Only name the next id from what this checkout sees; touch no remote.",
    )
    parser.add_argument(
        "--reserve-for",
        metavar="W-ID",
        help="Main session: hold a block of ids on this started card for its sub-session.",
    )
    parser.add_argument(
        "--count", type=int, default=1, help="How many ids --reserve-for holds (default 1)."
    )
    parser.add_argument(
        "--from-card",
        metavar="W-ID",
        help="Sub-session: name the next unused id from this card's reserved block.",
    )
    parser.add_argument("prefix", help="Record id prefix, e.g. W, DE, or O.")
    args = parser.parse_args()
    if not PREFIX_RE.fullmatch(args.prefix):
        print(f"prefix must be 1-3 capital letters, got {args.prefix!r}", file=sys.stderr)
        return 2
    if args.reserve_for and args.from_card:
        print("--reserve-for and --from-card cannot be combined", file=sys.stderr)
        return 2
    project_root = Path(args.project_root).expanduser().resolve()
    card_id = args.reserve_for or args.from_card
    if card_id:
        from stage_id_blocks import (
            CURRENT_CARDS,
            current_card_path,
            next_from_card,
            reserve_block,
        )

        card = current_card_path(project_root / ".stage", card_id)
        if card is None:
            print(f"{card_id}: no started card in .stage/{CURRENT_CARDS.as_posix()}", file=sys.stderr)
            return 1
        if args.from_card:
            record_id = next_from_card(project_root, args.prefix, card)
            if record_id is None:
                print(
                    f"{card_id}: no unused {args.prefix} id left in its reserved_ids; "
                    "ask the main session for more",
                    file=sys.stderr,
                )
                return 1
            print(record_id)
            return 0
        if args.count < 1:
            print("--count must be at least 1", file=sys.stderr)
            return 2
        block_reserver = None if args.no_reserve else IdReserver(project_root)
        block = reserve_block(project_root, args.prefix, args.count, card, block_reserver)
        if block_reserver is not None:
            notes = [block_reserver.unreserved_note(record_id) for record_id in block]
            if any(notes):
                print(notes[0], file=sys.stderr)
        print(" ".join(block))
        return 0
    reserver = None if args.no_reserve else IdReserver(project_root)
    record_id = next_record_id(project_root, args.prefix, reserver)
    if reserver is not None and reserver.unreserved_note(record_id):
        print(reserver.unreserved_note(record_id), file=sys.stderr)
    print(record_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
