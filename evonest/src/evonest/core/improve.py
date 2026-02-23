"""Improve engine — select a proposal and apply it (Execute + Verify + commit).

This module is the core of the `evonest improve` mode:
1. Select a proposal from .evonest/proposals/ (auto or explicit)
2. Use the proposal content as the plan
3. Run Execute + Verify
4. Commit/PR on success, revert on failure
5. Mark proposal as done
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

from evonest.core.config import EvonestConfig
from evonest.core.lock import EvonestLock
from evonest.core.orchestrator import (
    _git_commit,
    _git_commit_pr,
    _git_revert,
    _git_stash,
    _git_stash_drop,
)
from evonest.core.phases import run_execute, run_verify
from evonest.core.state import ProjectState

logger = logging.getLogger("evonest")

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def select_proposal(state: ProjectState, proposal_id: str | None = None) -> Path | None:
    """Select a proposal file to implement.

    Priority ordering:
      1. If proposal_id is given, look up that exact file.
      2. Otherwise: sort by priority (high > medium > low),
         then by filename (oldest timestamp first within same priority).

    Returns the Path to the selected proposal file, or None if nothing available.

    Raises:
        FileNotFoundError: If proposal_id is given but file does not exist.
    """
    if proposal_id:
        name = Path(proposal_id).name
        candidate = state.proposals_dir / name
        if not candidate.exists():
            raise FileNotFoundError(f"Proposal not found: {candidate}")
        return candidate

    proposals = state.list_proposals()
    if not proposals:
        return None

    def _sort_key(p: Path) -> tuple[int, str]:
        # Read first 10 lines to find priority value (always English: high/medium/low)
        try:
            text = p.read_text(encoding="utf-8")
            for line in text.splitlines()[:10]:
                lower = line.lower()
                if "priority" in lower or "우선순위" in lower:
                    for prio in ("high", "medium", "low"):
                        if prio in lower:
                            return (_PRIORITY_ORDER.get(prio, 1), p.name)
        except OSError:
            pass
        return (1, p.name)  # default: medium priority, then filename (oldest first)

    proposals.sort(key=_sort_key)
    return proposals[0]


def _commit_message_from_proposal(proposal_content: str) -> str | None:
    """Extract a commit message from a proposal's title line."""
    for line in proposal_content.splitlines():
        if line.startswith("# Proposal:") or line.startswith("# 제안:"):
            title = line.split(":", 1)[-1].strip()
            # Convert to lowercase, replace whitespace
            slug = re.sub(r"\s+", " ", title).strip().lower()
            return f"improve: {slug}"
    return None


async def run_improve(
    project: str,
    proposal_id: str | None = None,
) -> str:
    """Select a proposal from proposals/ and execute it.

    Steps:
      1. Select proposal (by proposal_id or auto by priority+age)
      2. Load proposal content as the "plan"
      3. Write it to .evonest/plan.md (so run_execute() can read it)
      4. Run Execute + Verify
      5. Commit or PR on success, revert on failure
      6. Mark proposal as done

    Returns a summary string.
    """
    config = EvonestConfig.load(project)
    state = ProjectState(project)
    state.ensure_dirs()

    with EvonestLock(state.lock_path):
        try:
            proposal_path = select_proposal(state, proposal_id)
        except FileNotFoundError as e:
            return f"Error: {e}"

        if proposal_path is None:
            return "No pending proposals. Run `evonest analyze` first."

        proposal_content = proposal_path.read_text(encoding="utf-8")

        # Extract title and priority for logging
        _title = "(no title)"
        _priority = ""
        for _line in proposal_content.splitlines()[:15]:
            if _line.startswith("# Proposal:") or _line.startswith("# 제안:"):
                _title = _line.split(":", 1)[-1].strip()
            if "priority" in _line.lower() or "우선순위" in _line.lower():
                for _p in ("critical", "high", "medium", "low"):
                    if _p in _line.lower():
                        _priority = _p
                        break
        state.log(f"  [Improve] Selected proposal: {proposal_path.name}")
        state.log(f"  [Improve] Title: {_title} [{_priority}]")

        # Write proposal content as plan so run_execute() can read it
        state.write_text(state.plan_path, proposal_content)

        cycle_start = time.time()

        _git_stash(state.project)

        execute_result = run_execute(state, config, "")
        state.log(f"  [Improve] Execute complete ({len(execute_result.output)} bytes)")

        verify = run_verify(state, config, cycle_num=0)

        # Use proposal title as commit message if available
        commit_msg = _commit_message_from_proposal(proposal_content) or verify.commit_message

        if verify.overall and verify.changed_files:
            state.log(f"  [Improve] PASS: {commit_msg}")
            if config.code_output == "pr":
                branch = f"evonest/improve-{proposal_path.stem}"
                _git_commit_pr(state.project, commit_msg, branch, state, mutation=None)
            else:
                _git_commit(state.project, commit_msg)
            _git_stash_drop(state.project)

            dest = state.mark_proposal_done(proposal_path.name)
            state.log(f"  [Improve] Proposal archived to: {dest}")

            duration = int(time.time() - cycle_start)
            return (
                f"Improve complete: {commit_msg}\n"
                f"Changed files: {', '.join(verify.changed_files)}\n"
                f"Proposal archived: {dest.name}\n"
                f"Duration: {duration}s"
            )

        elif verify.overall and not verify.changed_files:
            _git_stash_drop(state.project)
            dest = state.mark_proposal_done(proposal_path.name)
            state.log(f"  [Improve] Proposal archived (no changes needed): {dest}")
            return "Improve skipped: Execute succeeded but no files were changed."

        else:
            _git_revert(state.project)
            return f"Improve failed: {verify.notes}. Changes reverted."
