#!/usr/bin/env python3
"""PreToolUse Hook: Validate flow rules before tool execution.

Enforces Hook-backed rules:
1. no-action-without-doc: on apps/packages/plugins edits, verify an in-progress A-NNN.md exists
2. no-commit-without-retro: on git commit, check the retrospective section (block placeholder/too-short retro)
3. no-push-workspace: on git push, check whether .flow/workspace/ is included
5. no-shared-branch-merge: on merge/push to develop/main/master/release/*,
   verify an explicit user-request keyword (shared-branch protection rule — CRITICAL)
6. no-story-without-action-doc: block edits to non-SSOT files when the active Story has 0 A-*.md
7. no-merge-without-review: on Story-finish (all Actions ✅), require a deliverable review & evaluation
   record in _story.md (isomorphic to the retro gate — the concrete review is delegated to a project skill/agent)
8. no-work-without-playbook: when editing code/SSOT in the execution stage (Action docs exist), require a
   **playbook** (work type) field in the active Epic's _epic.md (Φ4 — no planning, no work).
   The Planning window (0 Action docs) is exempt (the playbook is chosen during Planning).
9. no-node-without-purpose: on new creation (Write/full-replace) of a workspace node SSOT
   (_initiative/_epic/_story/A-NNN.md), require an **Ultimate purpose** restatement — propagates the purpose-anchoring chain
   (a precondition for runtime purpose-anchoring derivation: the purpose must be embedded in the node so it can be read and derived).
   Independent of whether an epic exists (includes _epic/_initiative creation time). Edit (partial edit) is excluded to avoid false positives.
10. no-shell-node-write: block creating a workspace node via shell redirection (>/>>/tee)
   (prevents bypassing the node gate — best-effort).
11. no-finish-without-archive: right before PR creation (gh pr create)/shared-branch merge, block if a
   completed (✅) work item has not been migrated into .flow/archives/. Prevents skipping the archive step (epic-independent).
   Enforcement = only whether it was migrated into archives / preserving or deleting the workspace is up to the user.
12. no-action-without-depends-on: on new creation (Write/full-replace) of A-NNN.md, block if the **depends_on**
   field is missing. The dependency graph = a precondition for the fan-out attempt (D3) — always enforced regardless of AT.
   Edit (partial edit) is excluded to avoid false positives (consistent with the Rule 9 pattern).
13. fan-out-attempt-mandatory: with AT env on, on the first code edit of an in-progress Story, block if there is no
   spawn-attempt trace (Flow/Agent/Task) in the transcript. Limited to parallelizable Stories
   (A-NNN.md ≥2 + `depends_on: []` ≥2). AT off / silent fallback (attempted then
   failed — a trace remains) / serial Story / teammate (subagent) session (agent_id present — fan-out
   is the main session's responsibility) all pass (consistent with D4 — user intentionally disabled).

The path check (Rule 1/6) is performed on a path relative to workspace_root → even if the repo clone location
contains '/apps/' etc. (e.g. /Users/x/workspace/apps/myrepo), there is no false-positive workspace block.

Input (stdin): JSON with tool_name, tool_input, common fields
Output (stdout): JSON with hookSpecificOutput.permissionDecision

Tool name compatibility:
- File-write tools: Write, Edit, MultiEdit, NotebookEdit (+ compatible aliases such as create_file/apply_patch)
- Shell-exec tools: Bash (+ compatible aliases such as run_in_terminal)
"""

import json
import os
import re
import sys
import glob
import time

# Document self-status determination — the SSOT that blocks whole-substring contamination of the completed/in-progress verdict.
# (fix for the defect where a child Step's ✅ was misread as the epic/story's own status)
# resolve_workspace_root: shared SSOT across the 4 hooks — CLAUDE_PROJECT_DIR takes priority (cwd can change via cd).
from datetime import datetime, timezone

from _flow_state import self_status, is_completed, resolve_workspace_root, FOUR_WAY_BRIEF, runtime_dir, completed_unarchived, read_retrospective_settings, append_audit, active_unit_id, nfc

PATCH_TOOLS = frozenset({"apply_patch"})

# Extract the rule name from a block/warn reason — the first kebab identifier inside parentheses. Every deny/ask reason
# carries the rule name as `(rule-name)` near the front (convention). The `\(` anchor means argument parens like
# "(--no-verify / -n)" do not match because they do not start with [a-z] (false-positive blocking). Reasons without one are
# regression-guarded by the H3 test against real validate() output. TS-001 capture: on deny/ask, record which rule blocked.
BLOCKED_RULE_RE = re.compile(r"\(([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\)")

FILE_WRITE_TOOLS = frozenset({
    "create_file", "replace_string_in_file", "multi_replace_string_in_file",
    "edit_notebook_file", "editFiles", "edit_files",
    "Write", "Edit", "MultiEdit", "NotebookEdit",
}) | PATCH_TOOLS

SHELL_TOOLS = frozenset({"run_in_terminal", "Bash"})

# New-creation/full-replace tools (subject to no-node-without-purpose — partial-edit Edit excluded)
WRITE_NEW_TOOLS = frozenset({"Write", "create_file"})

# Hard-to-undo high-stakes tools (subject to fail-safe deny on internal hook exception — A-001).
# Write/edit/patch/shell. Read-type tools allow on exception (prevents a hook bug from halting all work).
HIGH_STAKES_TOOLS = FILE_WRITE_TOOLS | SHELL_TOOLS

# ⚠️ Sync obligation (A-002): the PreToolUse "matcher" in hooks.json must cover the full set of tools
# this hook actually checks = FILE_WRITE_TOOLS ∪ SHELL_TOOLS ∪ {"AskUserQuestion"}.
# If you add a tool to this set, you MUST also update the hooks.json matcher — if you miss it, Claude Code
# does not fire the hook for that tool and the rule silently dies (matcher not covering = silent gap).
# (Claude Code = scopes by matcher / VS Code = ignores the matcher, fires for everything, then branches internally on tool_name.)

# Workspace root (project-independent standard path)
WORKSPACE_SUBDIR = (".flow", "workspace")


def workspace_dir(workspace_root: str) -> str:
    """The .flow/workspace path under workspace_root."""
    return os.path.join(workspace_root, *WORKSPACE_SUBDIR)


def epic_dirs(workspace_root: str) -> list:
    """List of ALL Epic directories — direct epic-* + initiative-*/epic-* (4-tier).

    When the Initiative tier (flow-procedure-initiative) is used, an Epic is nested
    one level deeper (initiative-*/epic-*), so collect those together with direct epic-*.
    Includes completed (✅) epics — gate scans must use active_epic_dirs instead.
    """
    ws = workspace_dir(workspace_root)
    return (
        glob.glob(os.path.join(ws, "epic-*"))
        + glob.glob(os.path.join(ws, "initiative-*", "epic-*"))
    )


def active_epic_dirs(workspace_root: str) -> list:
    """epic_dirs excluding explicitly completed (✅) epics.

    Gate scans (Rule 1/2/7/13) must not be polluted by completed epics — a leftover
    in-progress action or a missing retro/review inside a ✅ epic is an archive
    concern, not a live-gate signal. An epic dir with a missing or unreadable
    _epic.md stays INCLUDED (status unknown → keep the gates active; preserves
    the pre-filter behavior for such dirs).
    """
    out = []
    for d in epic_dirs(workspace_root):
        epic_file = os.path.join(d, "_epic.md")
        if os.path.isfile(epic_file):
            try:
                with open(epic_file, "r", encoding="utf-8") as f:
                    if is_completed(f.read()):
                        continue
            except (OSError, UnicodeDecodeError):
                pass  # unreadable → status unknown → include
        out.append(d)
    return out


# ----- Retrospective placeholder/quality check -----
RETRO_PLACEHOLDER_PATTERNS = re.compile(
    r'(?i)\b(?:TODO|TBD|FIXME|placeholder)\b'
    r'|not\s*yet\s*written|being\s*written|drafting|write\s*later|after\s*work|after\s*completion'
)
MIN_RETRO_CHARS = 30  # minimum character count for a meaningful retrospective

# ----- Review & evaluation record check (no-merge-without-review) -----
# The deliverable review & evaluation enforces only "was it recorded", not "what and how" (project-independent).
# The concrete review is delegated to a project review skill/agent (.claude/agents, .claude/skills).
# Heading-anchored on purpose: matches "## Review", "## Review & Evaluation", "## Review/Evaluation"
# etc., but never a prose mention of the word "Review" (which is not a recorded review).
REVIEW_MARKER_RE = re.compile(r"(?im)^#{2,3}\s*Review\b")
MIN_REVIEW_CHARS = 20  # minimum character count for a meaningful review & evaluation record

# ----- no-shared-branch-merge -----
# Even if a flag (-f / --force / --no-ff etc.) sits between push/merge and the branch, or a refspec
# (HEAD:main, feature:main) is used, this catches the shared-branch destination. It does not cross command
# separators (|&;), which blocks false positives on chained commands. lookbehind/lookahead prevent
# false positives from partial branch-name matches like feature-main/main-x (only when the shared branch is a standalone token / after a colon).
SHARED_BRANCH_RE = re.compile(
    r'\bgit\s+(?:push|merge)\b[^|&;]*?'
    r'(?<![\w/-])(?:develop|main|master|release/\S+)(?![\w-])'
)

# ----- no-finish-without-archive: PR-creation detection (best-effort) -----
# `gh pr create` / `gh api ...pulls` (REST PR creation) — right before PR creation is the archive-gate trigger.
# A shared-branch merge/push (SHARED_BRANCH_RE) is the same trigger. Only \b boundaries so it does not cross command separators.
# Limitation (best-effort): web-UI PRs, GitHub auto-PR after a branch push, and MCP GitHub tools are not shell commands and
# go undetected. A direct shared-branch push/merge is caught separately by SHARED_BRANCH_RE, so the "reflect onto shared" essence is covered.
PR_CREATE_RE = re.compile(r'\bgh\s+(?:pr\s+create\b|api\s+\S*pulls\b)')


def creates_pr(command: str) -> bool:
    """Whether this is a PR-creation command (gh pr create / gh api ...pulls) — best-effort."""
    return bool(PR_CREATE_RE.search(command))

# git commit verify-skip flags: --no-verify or the shorthand -n (including combined forms -nm/-an).
# Fail-closed bias — a -n that happens to appear in the message body may also be blocked, but for a
# verify-skip blocking gate conservative blocking is safe (the user can lift it with an explicit override).
NO_VERIFY_RE = re.compile(r'(?:^|\s)(?:--no-verify\b|-[A-Za-z]*n[A-Za-z]*(?=\s|$))')


def uses_no_verify(command: str) -> bool:
    """Whether git commit uses --no-verify / -n (including combined shorthand)."""
    return bool(NO_VERIFY_RE.search(command))


USER_MERGE_KEYWORDS = (
    "merge", "merge it", "merge into",
    "push", "push it", "push into",
    "to develop", "onto develop",
    "to main", "onto main",
    "release/", "to release", "onto release", "to the release", "onto the release",
    "combine", "let's combine", "please combine",
    "apply it", "put it up",
)


def _merge_kw_pattern(kw: str) -> "re.Pattern":
    """Word-boundary pattern for a merge keyword — 'push' must not match 'pushover'.

    Boundary guards are applied only where the keyword edge is a word character
    (e.g. 'release/' ends with '/', so no trailing guard there).
    """
    prefix = r"(?<!\w)" if re.match(r"\w", kw[0]) else ""
    suffix = r"(?!\w)" if re.match(r"\w", kw[-1]) else ""
    return re.compile(prefix + re.escape(kw) + suffix, re.IGNORECASE)


_USER_MERGE_PATTERNS = tuple(_merge_kw_pattern(kw) for kw in USER_MERGE_KEYWORDS)


def has_active_epic(workspace_root: str) -> bool:
    """Check if there's an active (non-completed) epic. (epic-* + initiative-*/epic-*)"""
    for epic_dir in epic_dirs(workspace_root):
        epic_file = os.path.join(epic_dir, "_epic.md")
        if not os.path.isfile(epic_file):
            continue
        try:
            with open(epic_file, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if not is_completed(content):  # self-status — prevents contamination from a child Step's ✅
            return True
    return False


def has_action_doc(workspace_root: str) -> bool:
    """Check if any in-progress Action doc exists in an ACTIVE epic. (reads whole files)"""
    # Story directory glob `[UT]S-*` matches both US-* (User Story) and TS-* (Technical Story).
    # (ssot-vocabulary: 2 Story types. Epic 3 US-003 — added a technical-Story container)
    # active_epic_dirs: a leftover in-progress action inside a ✅ epic must not satisfy Rule 1.
    for d in active_epic_dirs(workspace_root):
        for action_file in glob.glob(os.path.join(d, "[UT]S-*", "A-*.md")):
            try:
                with open(action_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            if self_status(content) in ("🔄", "⬜"):  # self-status (in-progress/pending Action)
                return True
    return False


def has_playbook_field(workspace_root: str) -> bool:
    """Check whether the active (non-✅) Epic's _epic.md has a ``**playbook**`` field.

    The playbook (work type) is chosen by flow-playbook-selection in Plan Mode and
    recorded in the _epic.md ``**playbook**`` field. Returns True if any active Epic
    has the field (a signal that the current work's work type has been pinned).

    Returns True if there is no active Epic (not subject to the check — the caller runs has_active_epic first).
    """
    found_active = False
    for epic_dir in epic_dirs(workspace_root):
        epic_file = os.path.join(epic_dir, "_epic.md")
        if not os.path.isfile(epic_file):
            continue
        try:
            with open(epic_file, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if is_completed(content):  # self-status — skip completed Epics
            continue
        found_active = True
        if "**playbook**" in content:
            return True
    # If there is an active Epic but none has a playbook field, return False
    return not found_active


# Non-SSOT file path patterns — subject to blocking edits without an Action doc (no-story-without-action-doc)
# Project-independent common source directories.
SSOT_EXTERNAL_PATTERNS = (
    "/.claude/skills/",
    "/.claude/rules/",
    "/apps/",
    "/packages/",
    "/plugins/",
    "/lib/",
    "/src/",
)


def has_active_story_missing_action_doc(workspace_root: str) -> bool:
    """Check whether an in-progress (🔄) Story directory inside an active Epic has 0 A-*.md.

    True means: the active Story has no Action doc → subject to blocking meta work.
    A Planning (⬜) status Story has not started yet, so it is skipped (created in bulk during the Story Planning Phase).
    """
    for epic_dir in epic_dirs(workspace_root):
        if not os.path.isdir(epic_dir):
            continue
        epic_file = os.path.join(epic_dir, "_epic.md")
        if os.path.isfile(epic_file):
            try:
                with open(epic_file, "r", encoding="utf-8") as f:
                    epic_content = f.read()
                if is_completed(epic_content):  # self-status — skip completed Epics
                    continue
            except (OSError, UnicodeDecodeError):
                continue
        # Check every Story directory in this Epic — only in-progress (🔄) Stories
        for story_dir in glob.glob(os.path.join(epic_dir, "[UT]S-*")):
            if not os.path.isdir(story_dir):
                continue
            story_file = os.path.join(story_dir, "_story.md")
            if not os.path.isfile(story_file):
                continue  # no _story.md means an undefined Story (skip)
            try:
                with open(story_file, "r", encoding="utf-8") as f:
                    story_content = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            # Check only in-progress (🔄) Stories. Skip ⬜/✅.
            if self_status(story_content) != "🔄":  # self-status — only in-progress Stories
                continue
            action_files = glob.glob(os.path.join(story_dir, "A-*.md"))
            if not action_files:
                return True  # found 0 A-*.md
    return False


def repo_relative_path(file_path: str, workspace_root: str) -> str:
    """Convert an absolute path to a path relative to workspace_root (with a leading '/').

    Ensures that even if workspace_root itself contains '/apps/' etc. (e.g. /workspace/apps/myrepo),
    the repo-internal path check does not false-positive.
    If it is outside workspace_root or conversion fails, return the original (normalized) (conservative).
    """
    if not file_path:
        return ""
    norm = file_path.replace("\\", "/")
    if not workspace_root:
        return norm
    try:
        rel = os.path.relpath(norm, workspace_root).replace("\\", "/")
    except ValueError:
        return norm
    if rel == "." or rel.startswith(".."):
        return norm
    return "/" + rel


def matches_ssot_external(file_path: str, workspace_root: str = "") -> bool:
    """Whether the file path is a non-SSOT protected target (skills/rules/apps/packages/plugins/lib/src).

    Checked on a path relative to workspace_root → prevents false positives from the repo location (/apps/...).
    """
    rel = repo_relative_path(file_path, workspace_root)
    return any(p in rel for p in SSOT_EXTERNAL_PATTERNS)


# ----- no-shell-node-write (block bypassing node creation via shell redirection, best-effort) -----
# File-write rules (no-node-without-purpose etc.) only check the Write/Edit tools. Creating a workspace
# node via shell redirection (`> _story.md`, `>>`, `tee`) bypasses them.
# Best-effort block only the common forms (>, >>, tee + workspace node path).
# Limitation (not caught): python -c open(...,'w') / sed -i / variable paths / heredoc. Shell forms are unbounded
# → perfect blocking is impossible. Block only the common bypasses to nudge toward "create it with Write/Edit (node gate applied)".
# Match only when the redirection/tee operator **directly targets** a workspace node path.
# The token right after the operator (after whitespace) must be the node path → this blocks false positives from an
# unrelated redirect (stderr) plus a node path elsewhere, like `2>&1 ... ; grep _epic.md` (found in real dogfooding).
SHELL_NODE_WRITE_RE = re.compile(
    r'(?:>>?|\btee\b)\s*\S*\.flow/workspace/\S*?(?:_initiative|_epic|_story|A-\d+)\.md'
)


def shell_writes_workspace_node(command: str) -> bool:
    """Whether the shell command writes a workspace node file via redirection/tee (best-effort).

    True only when the operator (`>`/`>>`/`tee`) directly targets the node path — a redirect unrelated to
    the node such as `2>&1` does not false-positive.
    """
    return bool(SHELL_NODE_WRITE_RE.search(command))


# ----- VS Code / Copilot apply_patch compatibility -----
# When VS Code Copilot's editing tool comes in as apply_patch, the file path is not in tool_input.filePath
# but inside the patch string (`*** Add/Update/Delete File: ...`). Looking only at the existing Write/Edit aliases
# would fail-open, so extract the file list and Add File body from the patch and connect them to the existing rules.
PATCH_FILE_RE = re.compile(r"^\*\*\* (Add|Update|Delete) File: (.+)$")


def _patch_text(tool_input: dict) -> str:
    """Extract the patch body from an apply_patch-style tool_input (absorbs key differences)."""
    for key in ("input", "patch", "content", "contents", "diff"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def extract_patch_changes(tool_input: dict) -> list:
    """Extract per-file changes (action/path/content) from a V4A patch string.

    Return example: [{"action": "Add", "path": "/abs/A-001.md", "content": "..."}]
    content preserves the raw lines of the Add/Update block (including +, -, context). The purpose-field check
    only needs to see whether the `**Ultimate purpose**` substring is present, so a + prefix is safe.
    """
    changes = []
    current = None
    for line in _patch_text(tool_input).splitlines():
        m = PATCH_FILE_RE.match(line)
        if m:
            if current:
                current["content"] = "\n".join(current.get("content_lines", []))
                current.pop("content_lines", None)
                changes.append(current)
            current = {"action": m.group(1), "path": m.group(2).strip(), "content_lines": []}
            continue
        if line.startswith("*** End Patch"):
            break
        if current is not None:
            current.setdefault("content_lines", []).append(line)
    if current:
        current["content"] = "\n".join(current.get("content_lines", []))
        current.pop("content_lines", None)
        changes.append(current)
    return changes


def _add_path(paths: list, value):
    """Accumulate a string path without duplicates (with simple file:// URI support)."""
    if not isinstance(value, str) or not value:
        return
    path = value
    if path.startswith("file://"):
        path = path[len("file://"):]
    if path not in paths:
        paths.append(path)


def extract_tool_file_paths(tool_name: str, tool_input: dict) -> list:
    """Extract the per-tool file path list (absorbs Claude Code + VS Code Copilot aliases)."""
    if tool_name in PATCH_TOOLS:
        return [c["path"] for c in extract_patch_changes(tool_input) if c.get("path")]

    paths = []
    for key in ("filePath", "file_path", "path", "uri"):
        _add_path(paths, tool_input.get(key))

    files = tool_input.get("files")
    if isinstance(files, list):
        for item in files:
            if isinstance(item, str):
                _add_path(paths, item)
            elif isinstance(item, dict):
                for key in ("filePath", "file_path", "path", "uri"):
                    _add_path(paths, item.get(key))

    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for item in edits:
            if isinstance(item, dict):
                for key in ("filePath", "file_path", "path", "uri"):
                    _add_path(paths, item.get(key))
    return paths


# ----- no-node-without-purpose (enforce purpose-anchoring chain propagation) -----
# On new creation of a workspace node SSOT (_initiative/_epic/_story/A-NNN), require an **Ultimate purpose** restatement.
# A precondition for purpose-anchoring (runtime derivation) — the purpose must be embedded in the node so it can be read and derived at runtime.
PURPOSE_FIELD_RE = re.compile(r"\*\*Ultimate purpose\*\*")
NODE_FILE_RE = re.compile(r"^(?:_initiative|_epic|_story|A-\d+)\.md$")

# ----- no-action-without-depends-on (D3 dependency-graph precondition) -----
# On new creation of A-NNN.md, block a missing **depends_on** field. Always enforced regardless of AT.
DEPENDS_ON_FIELD_RE = re.compile(r"\*\*depends_on\*\*:\s*(?:\[\]|\[.*?\])")
ACTION_FILE_RE = re.compile(r"^A-\d+\.md$")

# ----- fan-out-attempt-mandatory (D3 enforcement, AT env branch) -----
# On the first code edit of an in-progress Story, block if there is no spawn-tool call trace in the transcript.
# AT on only. A silent fallback (attempted then failed) leaves a trace, so it passes. Consistent with D4.
AGENT_TEAMS_ENV = "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
# assistant tool_use block in the transcript JSONL — matches the name field (Flow/Agent/Task)
FAN_OUT_TOOL_RE = re.compile(r'"name"\s*:\s*"(?:Flow|Agent|Task)"')
EMPTY_DEPENDS_ON_RE = re.compile(r"\*\*depends_on\*\*:\s*\[\s*\]")


def is_workspace_node_file(file_path: str, workspace_root: str) -> bool:
    """Whether the file is a workspace node SSOT (_initiative/_epic/_story/A-NNN.md)."""
    rel = repo_relative_path(file_path, workspace_root)
    if "/.flow/workspace/" not in rel:
        return False
    return bool(NODE_FILE_RE.search(os.path.basename(rel)))


def detect_level_from_name(name: str) -> str:
    """Extract the level from a workspace-unit directory name (for the Rule 11 §4-8 branch).

    - ``initiative-*`` → ``"initiative"``
    - ``epic-*``       → ``"epic"``
    - otherwise        → ``"story"`` (default — story-*/US-*/TS-* are all story level)
    """
    if name.startswith("initiative-"):
        return "initiative"
    if name.startswith("epic-"):
        return "epic"
    return "story"


# ----- AskUserQuestion question gate — "stop once per question" state marker -----
# The hook does not judge whether a question is bad. It stops the AskUserQuestion call once to recall the four-way brief,
# and passes it on the re-call after re-examination (1 cycle). The AI decides whether to judge/ask.
# "delete the marker on pass (allow)" is the main mechanism → stop once per question attempt (not once per session).
# The TTL is a safety net so a marker left after a deny without a re-call does not wrongly pass the next question.
ASKQ_GATE_MARKER = ".askq_gate"
ASKQ_GATE_TTL = 120  # seconds — validity window of the stop trace (room for one re-examination turn + stale prevention)


def askq_gate_recently_stopped(workspace_root: str) -> bool:
    """Whether the previous AskUserQuestion gate stop trace is within the TTL (1-cycle pass determination)."""
    path = os.path.join(runtime_dir(workspace_root), ASKQ_GATE_MARKER)
    try:
        return (time.time() - os.path.getmtime(path)) < ASKQ_GATE_TTL
    except OSError:
        return False


def mark_askq_gate(workspace_root: str) -> None:
    """Record a single stop (so the next re-call is judged as a pass)."""
    try:
        d = runtime_dir(workspace_root)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, ASKQ_GATE_MARKER), "w", encoding="utf-8") as f:
            f.write("")
    except OSError:
        pass


def clear_askq_gate(workspace_root: str) -> None:
    """Delete the marker on pass (allow) → the next question stops again (once per question)."""
    try:
        os.remove(os.path.join(runtime_dir(workspace_root), ASKQ_GATE_MARKER))
    except OSError:
        pass


KPT_MARKER_RE = re.compile(r"(?im)^[\s\-*]*(Keep|Problem|Try|Good\s*points|Problem\s*points|Improvement\s*points)\b")


def check_retro_not_empty(workspace_root: str) -> bool:
    """Check that in-progress Action has substantive retro content.

    Per the `flow-retrospective` Part 4 §4-8 hook mapping table, branch the determination on the settings
    ``retrospective.levels.action.rigor`` label:

    - ``none``       → exempt (pass everything)
    - ``minimal``    → no placeholder + body ≥ 1 line
    - ``template``   → 1+ KPT marker + 5 chars, or placeholder-excluded body ≥ MIN_RETRO_CHARS (current behavior)
    - ``template+rt``→ ``template`` + an explicit ``R3 self-attack result`` section (consistent with §RETRO-1-05)

    When settings are absent, default = ``template`` (equivalent to current hook behavior — §4-5 compatibility-safe).
    """
    rigor_settings = read_retrospective_settings(workspace_root)
    action_rigor = rigor_settings.get("action", "template")
    if action_rigor == "none":
        return True  # §4-1 exempt

    action_files = []
    for d in active_epic_dirs(workspace_root):  # ✅ epics are archive concerns, not gate signals
        action_files += glob.glob(os.path.join(d, "[UT]S-*", "A-*.md"))
    for action_file in action_files:
        try:
            with open(action_file, "r", encoding="utf-8") as f:
                content = nfc(f.read())
        except (OSError, UnicodeDecodeError):
            continue
        if self_status(content) != "🔄":  # self-status — only in-progress Actions
            continue
        retro_match = re.search(r"## Retrospective|### Retrospective|## Retrospective", content)
        if not retro_match:
            return False
        retro_section = content[retro_match.start():]
        # HTML comments are not retro content — strip before judging (multiline included)
        retro_section = re.sub(r"<!--.*?-->", "", retro_section, flags=re.DOTALL)
        lines = retro_section.strip().split("\n")
        content_lines = [
            l for l in lines[1:]
            if l.strip()
            and not l.strip().startswith("#")
            and not RETRO_PLACEHOLDER_PATTERNS.search(l)
        ]
        meaningful_text = " ".join(content_lines).strip()

        # §4-1 minimal — no placeholder + body ≥ 1 line
        if action_rigor == "minimal":
            if not content_lines:
                return False
            continue  # this file passes

        # template / template+rt — current behavior (1+ KPT marker + 5 chars, or body ≥ MIN_RETRO_CHARS)
        kpt_with_content = [
            l for l in content_lines
            if KPT_MARKER_RE.search(l)
            and len(l.split(":", 1)[-1].strip()) >= 5
        ]
        if not kpt_with_content and len(meaningful_text) < MIN_RETRO_CHARS:
            return False

        # §4-1 template+rt — the above + an explicit R3 self-attack result section (§RETRO-1-05)
        if action_rigor == "template+rt":
            if not re.search(r"R3\s*self-attack\s*result|###\s*R3\b", retro_section):
                return False
    return True


def check_review_eval_recorded(workspace_root: str) -> bool:
    """Check whether a deliverable review & evaluation is recorded in _story.md at Story-finish time.

    Trigger conditions (false-positive prevention — the finish window only):
    - _story.md is in-progress (🔄), and
    - that Story has at least one A-*.md and **all are completed (✅)** (= right before wrap-up)
    Only then is a review & evaluation record required in _story.md. Otherwise (in progress / Actions incomplete) it passes.

    Pass criterion: after a heading review marker (## Review / ## Review & Evaluation /
    ## Review/Evaluation), non-placeholder meaningful text of at least MIN_REVIEW_CHARS.
    HTML comments are stripped BEFORE the marker search — a commented-out template
    heading is not a recorded review. Only active (non-✅) epics are scanned.
    """
    for epic_dir in active_epic_dirs(workspace_root):
        for story_dir in glob.glob(os.path.join(epic_dir, "[UT]S-*")):
            story_file = os.path.join(story_dir, "_story.md")
            if not os.path.isfile(story_file):
                continue
            try:
                with open(story_file, "r", encoding="utf-8") as f:
                    story_content = nfc(f.read())
            except (OSError, UnicodeDecodeError):
                continue
            if self_status(story_content) != "🔄":  # self-status — only in-progress Stories
                continue  # only in-progress Stories
            action_files = glob.glob(os.path.join(story_dir, "A-*.md"))
            if not action_files:
                continue  # no Action created — not a finish
            all_done = True
            for af in action_files:
                try:
                    with open(af, "r", encoding="utf-8") as f:
                        if not is_completed(f.read()):  # self-status (Action completed)
                            all_done = False
                            break
                except (OSError, UnicodeDecodeError):
                    all_done = False
                    break
            if not all_done:
                continue  # not yet the finish window → pass
            # finish window — require a review & evaluation record.
            # Strip HTML comments BEFORE the marker search: a template heading inside
            # a comment must not count as a recorded review.
            visible = re.sub(r"<!--.*?-->", "", story_content, flags=re.DOTALL)
            m = REVIEW_MARKER_RE.search(visible)
            if not m:
                return False
            section = visible[m.start():]
            lines = section.strip().split("\n")
            content_lines = [
                l for l in lines[1:]
                if l.strip()
                and not l.strip().startswith("#")
                and not RETRO_PLACEHOLDER_PATTERNS.search(l)
            ]
            if len(" ".join(content_lines).strip()) < MIN_REVIEW_CHARS:
                return False
    return True


def targets_shared_branch(command: str) -> bool:
    """Detect git push/merge to shared branches (develop/main/master/release/*)."""
    return bool(SHARED_BRANCH_RE.search(command))


def is_agent_teams_on() -> bool:
    """Whether the AT env (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) is active.

    Assumes Claude Code inherits env into the hook subprocess. Empty string / '0' / 'false'
    are treated as inactive. Other truthy values (e.g. '1') are active.
    """
    val = os.environ.get(AGENT_TEAMS_ENV, "")
    if not val:
        return False
    return val.strip().lower() not in ("0", "false", "no", "off")


def is_subagent_session(input_data: dict) -> bool:
    """Whether this hook call occurred inside a subagent/teammate session.

    When a hook fires inside `--agent`/a subagent (Task tool)/an Agent Teams teammate, Claude Code
    adds `agent_id` to the input JSON (absent in the main session). So the presence of `agent_id`
    = a non-main session. (Official hooks docs — agent_id "Present only when the hook
    fires inside a subagent call".)

    Fan-out is the **main session's responsibility** (subagent-deployment-timing (b)/(c)), so a code edit
    inside a teammate does not require a fan-out attempt (Rule 13 exemption). If the field is absent,
    treat it as main — the safe side (preserves existing behavior).
    """
    return bool(input_data.get("agent_id"))


def find_parallel_ready_story(workspace_root: str):
    """Find an in-progress Story where 'the parallelizable first wave is not yet complete'.

    Conditions (all must hold):
    - the containing Epic is active (non-✅ — a story in a completed epic is not a fan-out target)
    - `_story.md` self-status = 🔄 (in progress)
    - A-NNN.md ≥ 2 (parallelism is meaningful)
    - `depends_on: []` incomplete (not ✅) A-NNN.md ≥ 2 (first wave parallelizable + remaining)

    Returns: the matching Story directory path, or None.

    H2 recovery (0.12.0 RT-FIX — PR #24): the old `all_pending` (all ⬜) condition allowed a bypass
    where, per normal procedure, flipping an Action ⬜→🔄 before editing code turned Rule 13 off.
    Changed to fire on 2+ independent Actions that are "not ✅" — blocks the status-transition bypass.
    """
    for epic_dir in active_epic_dirs(workspace_root):
        for story_dir in glob.glob(os.path.join(epic_dir, "[UT]S-*")):
            story_file = os.path.join(story_dir, "_story.md")
            if not os.path.isfile(story_file):
                continue
            try:
                with open(story_file, "r", encoding="utf-8") as f:
                    if self_status(f.read()) != "🔄":
                        continue
            except (OSError, UnicodeDecodeError):
                continue
            action_files = glob.glob(os.path.join(story_dir, "A-*.md"))
            if len(action_files) < 2:
                continue
            empty_dep_unfinished_count = 0
            for af in action_files:
                try:
                    with open(af, "r", encoding="utf-8") as f:
                        ac = f.read()
                except (OSError, UnicodeDecodeError):
                    continue
                # ✅ (completed) is not a fan-out target — others (⬜ / 🔄) are remaining candidates
                if self_status(ac) == "✅":
                    continue
                if EMPTY_DEPENDS_ON_RE.search(ac):
                    empty_dep_unfinished_count += 1
            if empty_dep_unfinished_count >= 2:
                return story_dir
    return None


def transcript_has_fan_out_attempt(transcript_path: str) -> bool:
    """Whether the recent part of the transcript JSONL has a spawn-tool call trace (Flow/Agent/Task).

    Best-effort: read only the last 200KB and regex-match. Traces too old are irrelevant (focus on recent attempts).
    Absent transcript (e.g. test environment) → returns False (a state where Rule 13 can fire).
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return False
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 200_000))
            tail_bytes = f.read()
        tail = tail_bytes.decode("utf-8", errors="ignore")
    except OSError:
        return False
    return bool(FAN_OUT_TOOL_RE.search(tail))


def get_recent_user_messages(transcript_path: str, n: int = 5) -> list:
    """Extract last N user messages from transcript JSONL."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []
    msgs = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "user":
            continue
        msg = entry.get("message", {}) or {}
        content = msg.get("content", "")
        if isinstance(content, str):
            msgs.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    msgs.append(item.get("text", ""))
        if len(msgs) >= n:
            break
    return msgs


def user_requested_shared_merge(transcript_path: str) -> bool:
    """Whether a recent user message contains an explicit merge/push instruction.

    Word-boundary matching (no 'pushover' ⊃ 'push' false-positives). Known limit:
    negations ("don't push") still match — keyword scanning cannot parse intent,
    so the gate stays conservative and the user confirms at the ask.
    """
    msgs = get_recent_user_messages(transcript_path, n=5)
    combined = " ".join(m.lower() for m in msgs)
    return any(p.search(combined) for p in _USER_MERGE_PATTERNS)


def validate(input_data: dict) -> dict:
    """Run validation rules and return hook output."""
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    # Shared resolver across the 4 hooks — CLAUDE_PROJECT_DIR takes priority. Using cwd directly risks scanning
    # the wrong directory after a cd → missing the active epic (fail-open) + recurring absolute-path fallback false positives.
    workspace_root = resolve_workspace_root(input_data)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }

    # ===== Rule 5: no-shared-branch-merge (transcript-based, epic-independent) =====
    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "")
        if targets_shared_branch(command):
            transcript_path = input_data.get("transcript_path", "")
            if not user_requested_shared_merge(transcript_path):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Flow violation (no-shared-branch-merge): "
                            "merge/push to a shared branch (develop/main/master/release/*) "
                            "is allowed only on an explicit user request. "
                            "No keyword (merge/push/to develop, etc.) in the recent user messages."
                        ),
                    }
                }

    # ===== Rule 9: no-node-without-purpose (purpose-anchoring chain propagation, epic-independent) =====
    # On new creation (Write/full-replace) of a workspace node SSOT, require an **Ultimate purpose** restatement.
    # Independent of whether an epic exists — includes _epic/_initiative creation time. Edit (partial edit) is excluded to avoid false positives.
    if tool_name in WRITE_NEW_TOOLS:
        node_file_path = tool_input.get("filePath", "") or tool_input.get("file_path", "")
        if node_file_path and is_workspace_node_file(node_file_path, workspace_root):
            content = nfc(tool_input.get("content", "") or tool_input.get("contents", ""))
            if not PURPOSE_FIELD_RE.search(content):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Flow rule violation (no-node-without-purpose): "
                            "when creating a workspace node (_initiative/_epic/_story/A-NNN.md), "
                            "an **Ultimate purpose** restatement is required (purpose-anchoring precondition). "
                            "Restate the parent node's ultimate purpose in one line and include it in the header."
                        ),
                    }
                }

    if tool_name in PATCH_TOOLS:
        for change in extract_patch_changes(tool_input):
            if change.get("action") != "Add":
                continue
            node_file_path = change.get("path", "")
            if node_file_path and is_workspace_node_file(node_file_path, workspace_root):
                content = nfc(change.get("content", ""))
                if not PURPOSE_FIELD_RE.search(content):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow rule violation (no-node-without-purpose): "
                                "when newly creating a workspace node (_initiative/_epic/_story/A-NNN.md) "
                                "via apply_patch, an **Ultimate purpose** restatement is also required. "
                                "Restate the parent node's ultimate purpose in one line and include it in the header."
                            ),
                        }
                    }

    # ===== Rule 12: no-action-without-depends-on (D3 dependency-graph precondition) =====
    # On new creation of A-NNN.md (Write/full-replace + apply_patch Add File), block a missing **depends_on**
    # field. The dependency graph = a precondition for the fan-out attempt (D3) — always enforced regardless of AT.
    # Edit (partial edit) is excluded to avoid false positives (consistent with the Rule 9 pattern).
    # VS Code Copilot's core write path (apply_patch Add File) is enforced the same way (X1/H1 recovery — 0.12.0 RT-FIX, PR #24).
    if tool_name in WRITE_NEW_TOOLS:
        node_file_path = tool_input.get("filePath", "") or tool_input.get("file_path", "")
        if node_file_path:
            basename = os.path.basename(node_file_path)
            if ACTION_FILE_RE.match(basename) and is_workspace_node_file(node_file_path, workspace_root):
                content = tool_input.get("content", "") or tool_input.get("contents", "")
                if content and not DEPENDS_ON_FIELD_RE.search(content):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow rule violation (no-action-without-depends-on): "
                                "when newly creating A-NNN.md, the **depends_on** field is required "
                                "(D3 dependency-graph precondition — fan-out attempt). "
                                "Add **depends_on**: [] (no dependency) or "
                                "**depends_on**: [A-001] (a preceding Action) to the header."
                            ),
                        }
                    }

    if tool_name in PATCH_TOOLS:
        for change in extract_patch_changes(tool_input):
            if change.get("action") != "Add":
                continue
            node_file_path = change.get("path", "")
            if node_file_path:
                basename = os.path.basename(node_file_path)
                if ACTION_FILE_RE.match(basename) and is_workspace_node_file(node_file_path, workspace_root):
                    content = change.get("content", "")
                    if content and not DEPENDS_ON_FIELD_RE.search(content):
                        return {
                            "hookSpecificOutput": {
                                "hookEventName": "PreToolUse",
                                "permissionDecision": "deny",
                                "permissionDecisionReason": (
                                    "Flow rule violation (no-action-without-depends-on): "
                                    "when newly creating A-NNN.md via apply_patch, the **depends_on** "
                                    "field is also required (D3 dependency-graph precondition). "
                                    "Add **depends_on**: [] or [A-001] to the header."
                                ),
                            }
                        }

    # ===== Rule 13: fan-out-attempt-mandatory (D3 enforcement, AT env on only) =====
    # If an in-progress Story has a 'parallelizable first wave' (A-NNN.md ≥2 + depends_on: [] ≥2, all ⬜)
    # and there is no spawn trace in the transcript on the first code-edit attempt → block.
    # AT off / silent fallback (attempt→fail→main directly; a trace remains) / serial Story all pass.
    # teammate (subagent) session exemption: fan-out is the main session's responsibility — when a teammate
    # edits its own Action code, do not require fan-out (agent_id present = non-main → pass).
    if tool_name in FILE_WRITE_TOOLS and is_agent_teams_on() and not is_subagent_session(input_data):
        file_paths = extract_tool_file_paths(tool_name, tool_input)
        # Editing only workspace nodes passes (procedure in progress) — gate only at project-source edit time
        is_code_modify = any(
            p and not is_workspace_node_file(p, workspace_root)
            for p in file_paths
        )
        if is_code_modify:
            ready_story = find_parallel_ready_story(workspace_root)
            if ready_story:
                transcript_path = input_data.get("transcript_path", "")
                if not transcript_has_fan_out_attempt(transcript_path):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow violation (fan-out-attempt-mandatory): the in-progress Story "
                                f"[{os.path.basename(ready_story)}] has a parallelizable first wave, but "
                                "there is no spawn-tool (Flow/Agent/Task) call trace in the transcript. "
                                "With AT on, a fan-out 'attempt' is mandatory (D3 enforcement). "
                                "Attempt a parallel spawn of independent Actions via Flow.parallel / Agent. "
                                "Failure after the attempt passes as a silent fallback (a trace remains). "
                                "To intentionally disable, turn off the AT env (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS)."
                            ),
                        }
                    }

    # ===== Rule 10: no-shell-node-write (bypass node creation via shell redirection, epic-independent) =====
    # Creating a workspace node via `>`/`>>`/`tee` bypasses the Write/Edit-only node gate
    # (no-node-without-purpose etc.). Best-effort block the common forms.
    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "")
        if shell_writes_workspace_node(command):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "Flow rule violation (no-shell-node-write): creating/editing a workspace node "
                        "(_initiative/_epic/_story/A-NNN.md) via shell redirection (>/>>/tee) "
                        "bypasses the node gate (no-node-without-purpose etc.). Author it with the "
                        "Write/Edit tools (so Ultimate purpose etc. are enforced)."
                    ),
                }
            }

    # ===== Rule 11: no-finish-without-archive (block PR/merge when a completed item is unarchived, epic-independent) =====
    # The archive step of epic/initiative-finish (extract & consolidate retro into retro.md) is a text procedure
    # and is repeatedly skipped → block unarchived completed items right before PR creation (gh pr create)/shared-branch merge.
    # Enforcement = "whether archives/retro-<name>.md exists" (flat retro consolidation). The git commit is procedurally enforced (hook = working tree).
    # Preserving/deleting the workspace is up to the user (flow-archive v2.0.0).
    #
    # `flow-retrospective` Part 4 §4-8 label branch: units at a level with settings.levels.{level}.rigor == "none"
    # are exempt from the archive check. initiative cannot reach exemption because the reader guard (§4-4) enforces
    # template+rt — so the automatic archive check applies.
    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "")
        if creates_pr(command) or targets_shared_branch(command):
            unarchived = completed_unarchived(workspace_root)
            if unarchived:
                # §4-8 per-level branch — extract the level from the unit prefix, then exempt if rigor=none
                rigor = read_retrospective_settings(workspace_root)
                blocking = [
                    u for u in unarchived
                    if rigor.get(detect_level_from_name(u), "template") != "none"
                ]
                if blocking:
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow violation (no-finish-without-archive): the retrospective of the completed (✅) item(s) "
                                f"[{', '.join(blocking)}] has not been extracted & consolidated into .flow/archives/retro-<name>.md. "
                                "Archiving is required before PR/merge (flow-archive — archive precedes PR). "
                                "Extract & consolidate the retrospective into .flow/archives/retro-<name>.md (flat, no folder) + git commit, then retry "
                                "(preserving/deleting the workspace original is up to you)."
                            ),
                        }
                    }

    # ===== if no epic, skip Rule 1-3 =====
    if not has_active_epic(workspace_root):
        return result

    # ===== AskUserQuestion question gate (stop once + recall the four-way brief, Epic-conditional) =====
    # The hook does not judge whether a question is "bad" (it cannot judge meaning). It **stops the question attempt once**,
    # shows the four-way brief (forcing re-examination), and passes it on the re-call after re-examination (1 cycle).
    # The AI decides whether to judge/ask: if it follows from the purpose, drop the question / if the purpose is missing, off,
    # or a value judgment is needed, ask again as-is (pass). On pass, delete the marker → once per question (not once per session).
    # General work (no active Epic) is excluded by the early-return above. Text questions are not caught (not a tool)
    # → the SessionStart baseline covers those.
    if tool_name == "AskUserQuestion":
        if askq_gate_recently_stopped(workspace_root):
            clear_askq_gate(workspace_root)  # went through re-examination → pass (the next question stops again)
            return result  # allow
        mark_askq_gate(workspace_root)  # record a single stop
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Pre-question four-way decision gate (decision-criteria-first) — this question is stopped once. Re-examine it with the four-way brief below: "
                    "If the answer follows from the ultimate purpose, do not ask — proceed (one-line report). "
                    "If you cannot find the purpose / the purpose seems off / a value judgment is needed, ask the question again as-is (it will pass). "
                    + FOUR_WAY_BRIEF
                ),
            }
        }

    file_paths = extract_tool_file_paths(tool_name, tool_input)
    file_path = file_paths[0] if file_paths else ""

    # ===== Rule 1: no-action-without-doc =====
    if tool_name in FILE_WRITE_TOOLS:
        for file_path in file_paths:
            if file_path and matches_ssot_external(file_path, workspace_root):
                if not has_action_doc(workspace_root):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow rule violation (no-action-without-doc): there is an active Epic but no "
                                "in-progress A-NNN.md. Create an Action doc first."
                            ),
                        }
                    }

    # ===== Rule 6: no-story-without-action-doc =====
    # Block edits to non-SSOT files (skills/rules/apps/packages/plugins/lib/src) when the active Story directory has 0 A-*.md
    # Force A-NNN.md to be authored beforehand even for meta work (editing an Agent/Skill/Rule)
    if tool_name in FILE_WRITE_TOOLS:
        for file_path in file_paths:
            if file_path and matches_ssot_external(file_path, workspace_root):
                if has_active_story_missing_action_doc(workspace_root):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow rule violation (no-story-without-action-doc): "
                                "the active Story directory has 0 A-*.md files. "
                                "Before editing non-SSOT files (skills/rules/apps/packages/plugins/lib/src), "
                                "you must create an Action doc first."
                            ),
                        }
                    }

    # ===== Rule 8: no-work-without-playbook =====
    # When editing code/SSOT in the execution stage (an in-progress Action doc exists), block if the active Epic's
    # _epic.md has no **playbook** (work type) field.
    # Planning-window exemption: if there are 0 Action docs (still Planning — no playbook selected yet, which is normal),
    # skip. The playbook is chosen in Plan Mode (Planning), so writes during Planning are not blocked.
    # → Fires only in the execution stage (has_action_doc). Consistent with flow-playbook-selection.
    if tool_name in FILE_WRITE_TOOLS:
        for file_path in file_paths:
            if file_path and (
                "/apps/" in repo_relative_path(file_path, workspace_root)
                or "/packages/" in repo_relative_path(file_path, workspace_root)
                or "/plugins/" in repo_relative_path(file_path, workspace_root)
                or matches_ssot_external(file_path, workspace_root)
            ):
                if has_action_doc(workspace_root) and not has_playbook_field(workspace_root):
                    return {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                "Flow rule violation (no-work-without-playbook): "
                                "the active Epic's _epic.md has no **playbook** (work type) field. "
                                "Use flow-playbook-selection to choose a work-type playbook and "
                                "record it in the _epic.md **playbook** field before proceeding. "
                                "(no planning, no work — Φ4)"
                            ),
                        }
                    }

    # ===== Rule 2: no-commit-without-retro + block --no-verify =====
    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "")
        if "git commit" in command:
            if uses_no_verify(command):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Flow rule violation (no-verify-skip): verify-skip flags (--no-verify / -n) are "
                            "not allowed. You must go through the verification procedure."
                        ),
                    }
                }
            if not check_retro_not_empty(workspace_root):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Flow rule violation (no-commit-without-retro): the in-progress Action's retrospective section is "
                            "empty or placeholder/too-short. Write the retrospective before committing."
                        ),
                    }
                }
            # Rule 7: no-merge-without-review — require a deliverable review & evaluation record at Story-finish
            if not check_review_eval_recorded(workspace_root):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Flow rule violation (no-merge-without-review): this is a Story where all Actions "
                            "are complete, but there is no deliverable review & evaluation record. Add a "
                            "'## Review & Evaluation' record (review result + AC evaluation) to _story.md before committing. "
                            "The concrete review is delegated to a project review skill/agent (.claude/agents · .claude/skills)."
                        ),
                    }
                }

    # ===== Rule 3: no-push-workspace (single check) =====
    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "")
        if "git push" in command:
            decision = "deny" if is_codex_hook(input_data) else "ask"
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": (
                        "git push detected (no-push-workspace): check that no .flow/workspace/ files are "
                        "included. `git diff --stat <base-branch> HEAD -- .flow/workspace/` "
                        "(base-branch: the project's shared branch)"
                    ),
                }
            }

    return result


def is_codex_hook(input_data: dict) -> bool:
    """Whether this hook payload came from Codex.

    Codex includes turn-scoped fields such as ``turn_id`` and currently does
    not support ``permissionDecision: ask`` for PreToolUse. In that environment,
    warning-style gates must deny with a retry instruction instead of returning
    an unsupported ask decision that Codex would ignore.

    Discriminator = ``turn_id`` ONLY. ``permission_mode`` must NOT be used:
    it is a COMMON Claude Code hook field (present in every real payload —
    https://code.claude.com/docs/en/hooks), so keying on it would flip every
    Claude Code ask gate to deny.
    """
    return "turn_id" in input_data


def build_block_entry(input_data: dict, output: dict, workspace_root: str):
    """Build an audit record when deny/ask fires (None if allow — testable).

    Record: {ts, tool, decision, blocked_rule, unit_id?}. The allow path fires no rule
    (it passes) so it is not recorded — returns None. blocked_rule is extracted from the reason
    ("unknown" if the pattern does not match). Attributed to a work item via the same unit_id as the post record.
    """
    hso = output.get("hookSpecificOutput", {}) or {}
    decision = hso.get("permissionDecision", "allow")
    if decision == "allow":
        return None
    reason = hso.get("permissionDecisionReason", "") or ""
    m = BLOCKED_RULE_RE.search(reason)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": input_data.get("tool_name", ""),
        "decision": decision,
        "blocked_rule": m.group(1) if m else "unknown",
    }
    unit = active_unit_id(workspace_root)
    if unit:
        entry["unit_id"] = unit
    return entry


def fail_safe_output(tool_name: str, exc: Exception) -> dict:
    """Conservative decision on an internal hook exception (A-001 fail-safe).

    If validate() dies on an unexpected exception, stdout is empty → the harness treats it as allow (fail-open)
    and the strongest enforcement layer is silently breached. To prevent this, catch the exception:
    - Hard-to-undo high-stakes tools (write/edit/patch/shell) deny (advise retry after fixing the hook)
    - Others (read-type) allow (prevents a single hook bug from halting all work)
    Either way, leave the exception on stderr (no silence — observable).
    """
    print(
        f"[hook_pre_tool_validate] validate() exception — applying fail-safe: "
        f"{type(exc).__name__}: {exc}",
        file=sys.stderr,
    )
    if tool_name in HIGH_STAKES_TOOLS:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Internal flow hook error — blocked for safety (fail-safe). "
                    "This is a hard-to-undo operation, so check and fix the hook error before retrying."
                ),
            }
        }
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }


def main():
    # Prevent Hangul mojibake under Windows Python's default encoding (cp949 etc.) → force UTF-8 on both
    # stdin/stdout. Fixing only stdout leaves the output (block message) fine, but stdin stays cp949,
    # so the Hangul (**Ultimate purpose** etc.) in the UTF-8 payload sent by Claude Code is misread and
    # the gate false-denies (R9 no-node-without-purpose etc.). macOS/Linux are already UTF-8, so this is a no-op.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    try:
        output = validate(input_data)
    except Exception as exc:  # noqa: BLE001 — fail-safe: no exception may silently pass the hook (fail-open)
        output = fail_safe_output(input_data.get("tool_name", ""), exc)
    print(json.dumps(output, ensure_ascii=False))

    # Record an audit entry when a block/warn rule fires (allow is None). Ignore non-blocking failures — the decision output
    # is already done above. Measurement capture is an add-on, so no exception may break the hook.
    try:
        workspace_root = resolve_workspace_root(input_data)
        block = build_block_entry(input_data, output, workspace_root)
        if block:
            append_audit(workspace_root, block)
    except Exception:
        pass


if __name__ == "__main__":
    main()
