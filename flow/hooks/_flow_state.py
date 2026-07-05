#!/usr/bin/env python3
"""Shared flow-state discovery for flow plugin hooks.

Scans .flow/workspace/ for active Initiative/Epic/Story/Action state.
Used by both inject_flow_context (SessionStart) and session_relay (Stop)
so the 4-tier (Initiative > Epic > Story > Action) discovery logic stays SSOT.

This module lives in the same directory as the hook scripts, so when a hook is
run via `python3 <hook>.py` it is on sys.path[0] and can be imported with
`from _flow_state import ...`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata

# Workspace root (project-independent standard path)
WORKSPACE_SUBDIR = (".flow", "workspace")

# Permanent relocation target for completed work items (archive)
ARCHIVES_SUBDIR = (".flow", "archives")

# Runtime byproducts (audit log / session summary) — gitignored
RUNTIME_SUBDIR = (".flow", ".runtime")

# Workspace node directory naming (shared constants — status scan + metrics)
# US-=User Story / TS-=Technical Story (ssot-vocabulary §flow units)
_STORY_PREFIXES = ("US-", "TS-")
_ACTION_NAME_RE = re.compile(r"A-\d+")

# Purpose chain — extracts the top-level node's one-line ultimate purpose
PURPOSE_RE = re.compile(r"\*\*Ultimate purpose\*\*:\s*(.+)")

# The document's own status marker (⬜/🔄/✅) — extracted from the header area only
STATUS_RE = re.compile(r"\*\*Status\*\*:\s*([⬜🔄✅])")

# Pre-question four-way triage compact trigger (SSOT) — shared by inject(SessionStart) + pre_tool(PreToolUse·AskUserQuestion).
# Definition SSOT = plugin rules/decision-criteria-first.md. This constant is the compact summary for injection (≤3 lines).
# Kept in one place (here) to prevent divergence between the two hooks.
FOUR_WAY_BRIEF = (
    "> Pre-question four-way triage (decision-criteria-first) — applies to every question, whether the AskUserQuestion tool or a plain-text 'shall I…?': "
    "(0) attribution→reversible details with the same outcome (execution order, commit timing, etc.) are the AI's call (don't ask) / "
    "(d) missing data→gather it yourself (don't ask, go find it) / "
    "(c) ambiguous application→derive from the ultimate purpose + report in 1 line (purpose-anchoring) / (b) conflicting criteria→prioritize / "
    "(a) no criteria→ask for the criteria. Never say 'pick A/B' without triage (offloading the decision, whether via tool or text). "
    "The 'ultimate purpose' above is the top-level criterion for (c) derivation."
)


def nfc(s: str) -> str:
    """Unicode NFC normalization — guards status/gate matching against NFC/NFD mismatch.

    Regexes that embed literal markers (``**Status**`` / ``**Ultimate purpose**`` /
    ``Retrospective`` / ``Review`` etc.) come from NFC (composed) source, so they only
    match NFC content. If content arrives as NFD (decomposed) — via macOS (APFS/HFS+
    NFD-normalized filenames), some editors, model emission, or a drift-sync round-trip —
    the same characters carry different code points and the match fails → false-deny on
    no-node-without-purpose etc. + silent status misjudgment in STATUS_RE/PURPOSE_RE.
    Normalizing the haystack to NFC right before matching blocks that (idempotent — no
    effect on NFC input). The file itself is left untouched; normalization happens only
    at the point of consumption (read).
    """
    return unicodedata.normalize("NFC", s)


def self_status(content: str) -> str | None:
    """The document's *own* status (⬜/🔄/✅) — extracted only from the header area
    (before the first ``## `` section).

    Judging completion with ``"**Status**: ✅" in content`` (a whole-document substring)
    gets polluted by the status markers of child Step/Story/Action nodes and misjudges an
    *in-progress* document as complete (the status-misjudgment defect). This helper looks
    only at the document's own header status, blocking that pollution.

    If the header has no ``**Status**:`` field, returns None — the caller conservatively
    treats it as unfinished (active), so the rule fires on the safe side. _epic.md /
    _initiative.md carry a header status field (enforced by template), as do
    _story.md / A-NNN.md.
    """
    header = content.split("\n## ", 1)[0]
    m = STATUS_RE.search(nfc(header))
    return m.group(1) if m else None


def is_completed(content: str) -> bool:
    """Whether the document itself is complete (✅) — based on self_status (not a whole-document substring)."""
    return self_status(content) == "✅"


def resolve_workspace_root(input_data: dict) -> str:
    """Resolve the workspace root. CLAUDE_PROJECT_DIR takes priority (Claude Code always
    provides an absolute path) — input.cwd may change after a cd, so it is used only as a fallback."""
    return os.environ.get("CLAUDE_PROJECT_DIR") or input_data.get("cwd") or os.getcwd()


def workspace_dir(workspace_root: str) -> str:
    return os.path.join(workspace_root, *WORKSPACE_SUBDIR)


def runtime_dir(workspace_root: str) -> str:
    return os.path.join(workspace_root, *RUNTIME_SUBDIR)


def archives_dir(workspace_root: str) -> str:
    return os.path.join(workspace_root, *ARCHIVES_SUBDIR)


def completed_unarchived(workspace_root: str) -> list[str]:
    """Names of top-level work-item units that are complete (✅) but not yet relocated into .flow/archives/.

    For a top-level workspace unit (initiative-*/epic-*/story-*), if the *top SSOT node*
    (priority _initiative.md > _epic.md > _story.md) has self_status ✅ but there is no
    archives/retro-<name>.md, it is treated as an unarchived completed work item. Here
    <name> is the workspace directory basename verbatim — the initiative-/epic-/story-
    prefix is not stripped.

    The archive enforcement (no-finish-without-archive) judges on "whether
    archives/retro-<name>.md exists" (flat — retro-{unit name}.md directly under
    archives/, no folder; prevents parallel collisions + queues unmerged retrospectives).
    Whether it is git-committed is enforced by the flow-archive procedure (the hook only
    sees the working tree, so it does not check commits). Preserving/deleting the
    workspace is up to the user (flow-archive), so it is not considered here.
    """
    ws = workspace_dir(workspace_root)
    arch = archives_dir(workspace_root)
    if not os.path.isdir(ws):
        return []
    result: list[str] = []
    for name in sorted(os.listdir(ws)):
        unit = os.path.join(ws, name)
        if not os.path.isdir(unit):
            continue
        top = None
        for fn in ("_initiative.md", "_epic.md", "_story.md"):
            p = os.path.join(unit, fn)
            if os.path.isfile(p):
                top = p
                break
        if top is None:
            continue
        try:
            with open(top, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if is_completed(content) and not os.path.isfile(os.path.join(arch, f"retro-{name}.md")):
            result.append(name)
    return result


def extract_purpose(content: str) -> str:
    """Extract the `**Ultimate purpose**` line value (purpose-anchoring re-injection)."""
    m = PURPOSE_RE.search(nfc(content))
    return m.group(1).strip() if m else ""


def _read_text(path: str) -> str | None:
    """Read a workspace file; None if unreadable/non-UTF-8 — a single bad file
    must be skipped, never crash the SessionStart/Stop hooks (fail-safe)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def parse_epic(epic_dir: str, name: str) -> dict | None:
    """Parse one epic dir. Returns None if the epic is completed or unreadable."""
    epic_file = os.path.join(epic_dir, "_epic.md")
    if not os.path.isfile(epic_file):
        return None

    content = _read_text(epic_file)
    if content is None:
        return None

    # Skip completed epics (self-status — prevents pollution from child Step ✅)
    if is_completed(content):
        return None

    epic_info: dict = {"name": name, "purpose": extract_purpose(content), "stories": []}

    # Find stories (US- User Story / TS- Technical Story — scan both)
    for story_entry in sorted(os.listdir(epic_dir)):
        if not story_entry.startswith(_STORY_PREFIXES):
            continue
        story_dir = os.path.join(epic_dir, story_entry)
        story_file = os.path.join(story_dir, "_story.md")
        if not os.path.isfile(story_file):
            continue

        story_content = _read_text(story_file)
        if story_content is None:
            continue

        # Determine story status (self-status — prevents pollution from child Action ✅)
        story_status = self_status(story_content) or "⬜"

        # Find actions
        actions = []
        for action_file in sorted(os.listdir(story_dir)):
            if not re.match(r"A-\d+", action_file):
                continue
            action_path = os.path.join(story_dir, action_file)
            if not os.path.isfile(action_path):
                continue

            action_content = _read_text(action_path)  # whole file (status may sit after the retro)
            if action_content is None:
                continue

            action_status = self_status(action_content) or "⬜"

            # Extract handoff_to/delegate_to
            delegate = ""
            m = re.search(
                r"\*\*(?:handoff_to|delegate_to)\*\*:\s*(\S+)", action_content
            )
            if m:
                delegate = m.group(1)

            actions.append(
                {
                    "file": action_file,
                    "status": action_status,
                    "delegate_to": delegate,
                }
            )

        epic_info["stories"].append(
            {
                "name": story_entry,
                "status": story_status,
                "actions": actions,
            }
        )

    return epic_info


def find_active_epics(workspace_root: str) -> list[dict]:
    """Find top-level (outside an Initiative) epics with non-completed status."""
    ai_ws = workspace_dir(workspace_root)
    if not os.path.isdir(ai_ws):
        return []

    epics = []
    for entry in sorted(os.listdir(ai_ws)):
        if not entry.startswith("epic-"):
            continue
        epic = parse_epic(os.path.join(ai_ws, entry), entry)
        if epic is not None:
            epics.append(epic)
    return epics


def find_active_initiatives(workspace_root: str) -> list[dict]:
    """Find non-completed initiatives and their nested epics (scale-proportional re-injection — top level)."""
    ai_ws = workspace_dir(workspace_root)
    if not os.path.isdir(ai_ws):
        return []

    initiatives = []
    for entry in sorted(os.listdir(ai_ws)):
        if not entry.startswith("initiative-"):
            continue
        init_dir = os.path.join(ai_ws, entry)
        init_file = os.path.join(init_dir, "_initiative.md")
        if not os.path.isfile(init_file):
            continue

        content = _read_text(init_file)
        if content is None:
            continue

        if is_completed(content):  # self-status — prevents pollution from child Epic ✅
            continue

        epics = []
        for sub in sorted(os.listdir(init_dir)):
            if not sub.startswith("epic-"):
                continue
            epic = parse_epic(os.path.join(init_dir, sub), sub)
            if epic is not None:
                epics.append(epic)

        initiatives.append(
            {"name": entry, "purpose": extract_purpose(content), "epics": epics}
        )

    return initiatives


def iter_active_epics(workspace_root: str) -> list[tuple[str, dict]]:
    """Flatten all active epics into (path label, epic dict) pairs (Initiative-nested + top level)."""
    pairs: list[tuple[str, dict]] = []
    for init in find_active_initiatives(workspace_root):
        for epic in init["epics"]:
            pairs.append((f"{init['name']}/{epic['name']}", epic))
    for epic in find_active_epics(workspace_root):
        pairs.append((epic["name"], epic))
    return pairs


def summarize_inprogress(workspace_root: str) -> str:
    """One-line summary of in-progress (🔄) Actions. For session_relay(Stop) — scans all 4 tiers."""
    pairs = iter_active_epics(workspace_root)
    lines = []
    for label, epic in pairs:
        for story in epic["stories"]:
            if story["status"] != "🔄":
                continue
            for action in story["actions"]:
                if action["status"] == "🔄":
                    lines.append(f"{label}/{story['name']}/{action['file']} in progress")
    if lines:
        return "; ".join(lines)
    return "Active Epic present but no in-progress Action" if pairs else "No active Epic"


# ---------------------------------------------------------------------------
# Metrics capture (TS-001) — append to the audit log + single attribution to the
# in-progress work-item id. Shared SSOT for post_tool_validate (every call) +
# hook_pre_tool_validate (on deny/ask).
# ---------------------------------------------------------------------------

AUDIT_FILE = "hook_audit.jsonl"


def append_audit(workspace_root: str, entry: dict) -> None:
    """Append one line to the audit log (silently passes even on failure — the hook never blocks).

    post (every tool call) / pre (when deny·ask fires) both write to the same
    ``hook_audit.jsonl``. Record kinds are distinguished by key: post = ``success`` /
    pre-block = ``blocked_rule``.
    """
    log_file = os.path.join(runtime_dir(workspace_root), AUDIT_FILE)
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _header_status(path: str) -> "str | None":
    """Only the node file's header status (⬜/🔄/✅) — without parsing the whole body (cost reduction)."""
    try:
        with open(path, encoding="utf-8") as f:
            return self_status(f.read())
    except (OSError, UnicodeDecodeError):
        return None


def _active_in_epic(epic_dir: str, label: str) -> "str | None":
    """Return the deepest 🔄 node id in an epic directory (None if none).

    Priority: 🔄 Action > 🔄 Story > 🔄 Epic. On multiple 🔄, sort order wins (deterministic).
    Descends into Actions only on the active branch (🔄 Story) — reduces per-call cost.
    """
    epic_status = _header_status(os.path.join(epic_dir, "_epic.md"))
    if epic_status == "✅":
        return None
    try:
        entries = sorted(os.listdir(epic_dir))
    except OSError:
        entries = []
    for name in entries:
        if not name.startswith(_STORY_PREFIXES):
            continue
        sdir = os.path.join(epic_dir, name)
        if not os.path.isdir(sdir):
            continue
        if _header_status(os.path.join(sdir, "_story.md")) != "🔄":
            continue
        for af in sorted(os.listdir(sdir)):
            if not _ACTION_NAME_RE.match(af):
                continue
            ap = os.path.join(sdir, af)
            if os.path.isfile(ap) and _header_status(ap) == "🔄":
                return f"{label}/{name}/{os.path.splitext(af)[0]}"
        return f"{label}/{name}"  # no 🔄 Action → attribute to the Story
    if epic_status == "🔄":
        return label  # no 🔄 Story → attribute to the Epic
    return None


def active_unit_id(workspace_root: str) -> "str | None":
    """Single attribution to the deepest node id in the in-progress (🔄) tree (for audit tagging).

    Format: ``epic-x/TS-001-m/A-002`` (directory basenames joined). Scans both US-/TS- Stories.
    Priority 🔄 Action > 🔄 Story > 🔄 Epic > None. On multiple 🔄, sort order wins (deterministic).
    Header-only reads + descending only on the active branch reduce the per-PostToolUse cost.
    """
    ws = workspace_dir(workspace_root)
    if not os.path.isdir(ws):
        return None
    try:
        units = sorted(os.listdir(ws))
    except OSError:
        return None
    for name in units:  # initiative-* nested epics first
        if not name.startswith("initiative-"):
            continue
        idir = os.path.join(ws, name)
        if not os.path.isdir(idir):
            continue
        if _header_status(os.path.join(idir, "_initiative.md")) == "✅":
            continue
        for sub in sorted(os.listdir(idir)):
            if sub.startswith("epic-") and os.path.isdir(os.path.join(idir, sub)):
                r = _active_in_epic(os.path.join(idir, sub), f"{name}/{sub}")
                if r:
                    return r
    for name in units:  # top-level epic-*
        if not name.startswith("epic-"):
            continue
        edir = os.path.join(ws, name)
        if os.path.isdir(edir):
            r = _active_in_epic(edir, name)
            if r:
                return r
    return None


# ---------------------------------------------------------------------------
# Rule sync (plugin rules/ → project .claude/rules/) — judgment/state SSOT
#
# Since Claude Code does not auto-load the plugin's rules/, flow copies-and-delivers
# the rules into the project's .claude/rules/ (with a DO NOT EDIT marker attached).
# When the plugin is upgraded and the canonical source changes, the project copy goes
# stale. This section is the single SSOT for that drift-detection logic — the
# SessionStart hook (inject_flow_context) imports it to detect and notify, and the
# /flow-upgrade command invokes it via uv run to apply. The judgment logic lives in
# one place (here) to prevent hook/command divergence (isomorphic to the FOUR_WAY_BRIEF
# shared pattern).
# ---------------------------------------------------------------------------

# Copy's first-line marker (current ground truth — exactly this one line). Detection is hardened via prefix (absorbs variants like em-dash).
MARKER_LINE = (
    "<!-- DO NOT EDIT — generated from flow plugin rules/. "
    "Overwritten when flow-upgrade is re-run -->"
)
MARKER_PREFIX = "<!-- DO NOT EDIT"

# Rule sync state file (.flow/.runtime/ — gitignored, local per clone)
RULES_SYNC_STATE_FILE = "rules_sync_state.json"


def plugin_root_dir() -> str:
    """Plugin root (two levels up from hooks/_flow_state.py).

    Zero env dependency — CLAUDE_PLUGIN_ROOT is unverified since no hook reads it via
    os.environ, so the __file__ absolute path (realpath — resolves symlink caches) is
    robust (independent of uv run cwd changes).
    """
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def plugin_rules_dir() -> str:
    """Plugin rules canonical-source directory."""
    return os.path.join(plugin_root_dir(), "rules")


def project_rules_dir(workspace_root: str) -> str:
    """The project's auto-loaded rules directory (copy location)."""
    return os.path.join(workspace_root, ".claude", "rules")


# Propagated-rule marking (propagated-rule model): flow-upgrade registers **each propagated
# copy individually** in the repo .gitignore at file-path granularity (never a whole
# folder). A registered file = a propagated artifact — apply force-overwrites it when the
# canonical source changes and deletes it as an orphan when the canonical source drops it.
# Unregistered files under the same dirs = hand-authored consumer rules (protected,
# untouched by sync). The .gitignore itself is the marking (no separate state file).
# (Function names below keep the historical "override" wording — the registration
# mechanics are unchanged; only the meaning of a registered line flipped with the model.)
_OVERRIDE_PREFIXES = (
    (".claude/rules/", "rules"),
    (".claude/rule-details/", "details"),
)
# Marker comment written above the registered lines in the consumer .gitignore — must
# describe the current model (these are auto-synced propagated artifacts, not overrides).
_OVERRIDE_MARKER = (
    "# flow-upgrade propagated rules (auto-synced — apply overwrites/removes these; "
    "do not hand-edit)"
)
# Pre-reword marker text (said the opposite of reality). Still recognized when reading
# existing consumer .gitignore files so registration does not append a second marker;
# new writes always use _OVERRIDE_MARKER.
_OVERRIDE_MARKER_LEGACY = "# Consumer override rules (excluded from flow-upgrade sync — per file)"


def gitignored_rule_files(workspace_root: str) -> dict:
    """Rule files registered in the repo .gitignore at **file-path granularity** = propagated-rule marks.

    Recognizes only the `.claude/rules/NAME.md` / `.claude/rule-details/NAME.md` form.
    Folder patterns (`.claude/rules/`), wildcards (`*`), and sub-paths are not treated as
    marks (file-granularity principle — ignoring a whole folder would switch off all
    governance, so it is forbidden).

    Returns: {"rules": set[name], "details": set[name]}.
    """
    result: dict = {"rules": set(), "details": set()}
    gi_path = os.path.join(workspace_root, ".gitignore")
    try:
        with open(gi_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return result
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        for prefix, key in _OVERRIDE_PREFIXES:
            if line.startswith(prefix):
                name = line[len(prefix):]
                # file granularity only — exclude folders/wildcards/sub-paths
                if name.endswith(".md") and "/" not in name and "*" not in name:
                    result[key].add(name)
    return result


def register_rule_override(workspace_root: str, name: str, is_detail: bool = False) -> bool:
    """Mark a propagated rule in the repo .gitignore at **file-path granularity** (idempotent).

    Adds just that one file-path line, not a whole folder. If already registered, no-op
    (False); if newly added, True. On first registration, also drops in the one-line
    explanatory marker (recognizes the legacy marker too so old consumer .gitignore
    files do not accumulate a second marker; new writes use the current text).
    """
    rel = (".claude/rule-details/" if is_detail else ".claude/rules/") + name
    gi_path = os.path.join(workspace_root, ".gitignore")
    existing = ""
    try:
        with open(gi_path, encoding="utf-8") as f:
            existing = f.read()
    except OSError:
        pass
    for line in existing.splitlines():
        if line.strip() == rel:
            return False  # already registered — idempotent
    lead = "" if existing == "" or existing.endswith("\n") else "\n"
    if _OVERRIDE_MARKER in existing or _OVERRIDE_MARKER_LEGACY in existing:
        add = f"{lead}{rel}\n"
    else:
        add = f"{lead}{_OVERRIDE_MARKER}\n{rel}\n"
    with open(gi_path, "a", encoding="utf-8") as f:
        f.write(add)
    return True


def unregister_rule_override(workspace_root: str, name: str, is_detail: bool = False) -> bool:
    """On deletion of a propagated rule (orphan), remove that one file-path line from the repo .gitignore (idempotent).

    The inverse of `register_rule_override` — if the line exists, remove it and return
    True; otherwise no-op False. The marker line (current or legacy) is left untouched
    since other propagated rules may remain (an empty marker is harmless).
    """
    rel = (".claude/rule-details/" if is_detail else ".claude/rules/") + name
    gi_path = os.path.join(workspace_root, ".gitignore")
    try:
        with open(gi_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return False
    kept = [ln for ln in lines if ln.strip() != rel]
    if len(kept) == len(lines):
        return False  # absent — idempotent
    with open(gi_path, "w", encoding="utf-8") as f:
        f.writelines(kept)
    return True


# rule-details = on-demand detail for a rule core (non-autoload). Synced the same way as
# rules/ (propagated-copy model — force-overwrite/orphan-delete), but since filenames
# overlap with rules/ (e.g. flow-rules.md exists in both), they are distinguished by
# prefix in unified reporting/application.
DETAIL_PREFIX = "rule-details/"


def plugin_rule_details_dir() -> str:
    """Plugin rule-details (on-demand) canonical-source directory."""
    return os.path.join(plugin_root_dir(), "rule-details")


def project_rule_details_dir(workspace_root: str) -> str:
    """The project's rule-details directory (copy location — non-autoload)."""
    return os.path.join(workspace_root, ".claude", "rule-details")


def _plugin_json_version(path: str) -> str:
    """Version at an arbitrary plugin.json path (fail-safe — absent/parse-failure → '')."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("version", "")
    except (OSError, ValueError):
        return ""


def read_plugin_version() -> str:
    """Plugin (installed) version (.claude-plugin/plugin.json). **For display** — not an input to drift detection."""
    return _plugin_json_version(
        os.path.join(plugin_root_dir(), ".claude-plugin", "plugin.json")
    )


def _cli_latest_version(norm_root: str) -> str:
    """CLI: cache/<mp>/<plugin>/<ver> → marketplaces/<mp>/plugins/<plugin> clone plugin.json."""
    try:
        after = norm_root.split(".claude/plugins/cache/", 1)[1]
        parts = after.split("/")
        mp, plugin = parts[0], parts[1]
    except (IndexError, ValueError):
        return ""
    clone = os.path.join(
        os.path.expanduser("~"), ".claude", "plugins", "marketplaces",
        mp, "plugins", plugin, ".claude-plugin", "plugin.json",
    )
    return _plugin_json_version(clone)


def _vscode_latest_version(root: str) -> str:
    """VS Code: the origin/main plugin.json of the git checkout (current ref — no fetch). fail-safe.

    CLAUDE_PLUGIN_ROOT = .../agent-plugins/.../<repo>/plugins/<plugin>. After extracting the
    repo root + relative path, read the latest version via `git show origin/main:<rel>`
    (zero network — the current origin ref).
    """
    norm = root.replace(os.sep, "/")
    try:
        repo, tail = norm.split("/plugins/", 1)
        rel = "plugins/" + tail.split("/")[0] + "/.claude-plugin/plugin.json"
    except (IndexError, ValueError):
        return ""
    try:
        out = subprocess.run(
            ["git", "-C", repo, "show", f"origin/main:{rel}"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode != 0:
            return ""
        return json.loads(out.stdout).get("version", "")
    except (OSError, ValueError, subprocess.SubprocessError):
        return ""


def detect_plugin_staleness(plugin_root: str | None = None) -> dict:
    """Detect whether the installed plugin lags the latest (environment-branched, current local state — zero network).

    Returns ``{env, installed, latest, stale}``. fail-safe (undeterminable → stale=False).
    - **env**: ``CLAUDE_PLUGIN_ROOT`` path — ``.vscode/agent-plugins``=vscode / ``.claude/plugins/cache``=cli
    - **installed**: installed plugin.json version
    - **latest** (current local — refreshing [marketplace update / git fetch] is user/guidance; here it is the current state):
      cli=marketplace clone plugin.json / vscode=the git checkout's origin/main plugin.json (current ref)
    - **stale**: installed != latest (when both exist — version strings differ)
    """
    root = plugin_root or plugin_root_dir()
    norm = root.replace(os.sep, "/")
    res = {"env": "unknown", "installed": "", "latest": "", "stale": False}
    if ".vscode/agent-plugins" in norm:
        res["env"] = "vscode"
    elif ".claude/plugins/cache" in norm:
        res["env"] = "cli"
    res["installed"] = _plugin_json_version(
        os.path.join(root, ".claude-plugin", "plugin.json")
    )
    if res["env"] == "cli":
        res["latest"] = _cli_latest_version(norm)
    elif res["env"] == "vscode":
        res["latest"] = _vscode_latest_version(root)
    res["stale"] = bool(
        res["installed"] and res["latest"] and res["installed"] != res["latest"]
    )
    return res


def resolve_plugin_upgrade_commands(plugin_root: str | None = None) -> dict:
    """Resolve the concrete commands to auto-upgrade a stale plugin from the CLI.

    Returns ``{stale, env, commands}``. commands = list of command strings to run — an
    empty list means no auto-run. Populated **only when CLI environment + stale** (vscode/
    unknown differ in their restart/apply means, so commands keep the existing manual
    guidance). Fills in the marketplace/plugin with real values and fixes scope to
    ``project`` (this marketplace uses a per-project install/management model). fail-safe —
    empty commands if the path cannot be parsed.

    **Marketplace-clone pre-refresh (breaking the chicken-and-egg)**: stale detection
    depends on the local marketplace clone version, and that clone is refreshed only by
    ``marketplace update``. If the clone is stale it misjudges "same as latest" and yields
    empty commands, and since that update command is emitted only when stale is detected,
    a chicken-and-egg arises where the first run never refreshes. → **Only in the CLI
    environment**, run ``marketplace update`` once right before detection so the judgment
    uses a refreshed clone. The detection function ``detect_plugin_staleness`` is also
    shared by the SessionStart hook (read-only · zero-network contract), so it is left
    untouched — the network call lives only on this CLI auto-upgrade path. An update
    failure is fail-safe (detection continues with the existing clone).
    """
    root = (plugin_root or plugin_root_dir()).replace(os.sep, "/")
    try:
        after = root.split(".claude/plugins/cache/", 1)[1]
        parts = after.split("/")
        mp, plugin = parts[0], parts[1]
    except (IndexError, ValueError):
        mp = plugin = None
    # Refresh the marketplace clone once right before detection — only in the CLI environment + on successful path parse (breaks the chicken-and-egg).
    if mp and detect_plugin_staleness(plugin_root)["env"] == "cli":
        try:
            subprocess.run(
                ["claude", "plugin", "marketplace", "update", mp],
                capture_output=True, text=True, timeout=120,
            )
        except (OSError, subprocess.SubprocessError):
            pass  # fail-safe: on refresh failure, continue detection with the existing clone
    info = detect_plugin_staleness(plugin_root)
    res = {"stale": info["stale"], "env": info["env"], "commands": []}
    if not info["stale"] or info["env"] != "cli" or not mp:
        return res
    res["commands"] = [
        f"claude plugin marketplace update {mp}",
        f"claude plugin update {plugin}@{mp} --scope project",
    ]
    return res


def strip_marker_prefix(content: str) -> str:
    """Strip the marker prefix (the one marker line + the single blank line right after) from a copy and return only the body.

    Marker-anchored: strips only when the first line is the marker (never based on a fixed
    line count). The inverse of wrap_with_marker.
    """
    lines = content.split("\n")
    if lines and lines[0].lstrip().startswith(MARKER_PREFIX):
        rest = lines[1:]
        if rest and rest[0].strip() == "":
            rest = rest[1:]
        return "\n".join(rest)
    return content


def wrap_with_marker(body: str) -> str:
    """Attach the marker prefix to a body (canonical → copy form). The inverse of strip_marker_prefix."""
    return MARKER_LINE + "\n\n" + body


def _hash_body(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def synced_rule_files(rules_dir: str) -> list[str]:
    """List of rule filenames eligible for sync (*.md, excluding README.md — it is guidance, not a rule)."""
    try:
        names = os.listdir(rules_dir)
    except OSError:
        return []
    return sorted(n for n in names if n.endswith(".md") and n != "README.md")


def detect_rule_drift(
    plugin_rules: str, project_rules: str, state: dict | None = None
) -> dict:
    """Detect drift between the plugin canonical source ↔ project copy (propagated rule = generated artifact, always overridden).

    A propagated rule (a copy of the canonical source) is a generated artifact, so it is
    always overwritten with the canonical source regardless of hand edits — **no conflict
    concept** (as a `.gitignore`-registered artifact, hand edits are not caught by git → no
    3-way state hash needed). Per file (P=canonical body / C=stripped current copy body):
      C==P            → in_sync (no action)
      C!=P            → stale   (override with the canonical source)
      copy absent     → missing_new
    (A canonical deletion (orphan) is invisible on a canonical-source walk — the copy walk
    in `detect_rule_drift_all` judges it.)
    The `state` argument is kept for call compatibility (unused — 3-way removed).

    Returns: {in_sync, stale, conflict(always []), missing_new, final_bodies, plugin_version}
    final_bodies[name] = the final body to write on sync (wrap applied) — apply_rule_upgrade
    applies it via write_rule_copy (content never passes through the AI, so it is byte-exact to the canonical source).
    """
    res: dict = {
        "in_sync": [],
        "stale": [],
        "conflict": [],  # propagated rules always overridden — always an empty array (kept for caller compatibility)
        "missing_new": [],
        "final_bodies": {},
        "plugin_version": read_plugin_version(),
    }
    # Self-reference guard (never happens on the normal path — even dogfooding has different canonical/copy paths)
    if os.path.realpath(plugin_rules) == os.path.realpath(project_rules):
        return res

    for name in synced_rule_files(plugin_rules):
        try:
            with open(os.path.join(plugin_rules, name), encoding="utf-8") as f:
                plugin_body = f.read()
        except OSError:
            continue
        proj_path = os.path.join(project_rules, name)
        if not os.path.isfile(proj_path):
            res["missing_new"].append(name)
            res["final_bodies"][name] = wrap_with_marker(plugin_body)
            continue
        try:
            with open(proj_path, encoding="utf-8") as f:
                proj_content = f.read()
        except OSError:
            continue
        if _hash_body(strip_marker_prefix(proj_content)) == _hash_body(plugin_body):
            res["in_sync"].append(name)
            continue
        # propagated rule = generated artifact — always override with the canonical source regardless of hand edits (conflict removed).
        res["stale"].append(name)
        res["final_bodies"][name] = wrap_with_marker(plugin_body)

    return res


def detect_rule_drift_all(workspace_root: str, state: dict | None = None) -> dict:
    """Unified drift detection for rules/ + rule-details/ (propagated-rule model).

    A flow propagated rule (a copy of the canonical source) is a generated artifact — on
    the **canonical-source walk** it is always overridden (in_sync/stale/missing_new, no
    conflict). It is not skipped based on gitignore registration (a propagated rule is a
    sync target; gitignore is merely artifact marking). On the **copy walk**, among files
    not in the canonical source, `.gitignore`-registered (propagation-marked)=orphan
    (delete), unregistered=protected (consumer-authored rule · preserve). SSOT for the
    directory-standard model. rule-details items are distinguished by `DETAIL_PREFIX`.
    `state` unused (compatibility — 3-way removed).

    Returns: in_sync/stale/conflict([])/missing_new/orphan/protected/final_bodies/plugin_version.
    orphan = deletion target (was propagated, then vanished from the canonical source),
    protected = self-authored rule (untouched by sync).
    """
    rules = detect_rule_drift(plugin_rules_dir(), project_rules_dir(workspace_root))
    details = detect_rule_drift(
        plugin_rule_details_dir(), project_rule_details_dir(workspace_root)
    )
    merged: dict = {
        "plugin_version": rules.get("plugin_version", ""),
        "final_bodies": dict(rules["final_bodies"]),
        "conflict": [],  # propagated rules always overridden — conflict concept removed
    }
    # canonical-source walk results — no overridden-skip (propagated rule = sync target).
    for key in ("in_sync", "stale", "missing_new"):
        merged[key] = list(rules[key]) + [DETAIL_PREFIX + n for n in details[key]]
    for name, body in details["final_bodies"].items():
        merged["final_bodies"][DETAIL_PREFIX + name] = body
    # copy walk → orphan (delete) vs protected (preserve self-authored). gitignore registration = propagated-rule marking.
    gitignored = gitignored_rule_files(workspace_root)
    orphan: list[str] = []
    protected: list[str] = []
    for plugin_dir, project_dir, gi_key, prefix in (
        (plugin_rules_dir(), project_rules_dir(workspace_root), "rules", ""),
        (
            plugin_rule_details_dir(),
            project_rule_details_dir(workspace_root),
            "details",
            DETAIL_PREFIX,
        ),
    ):
        plugin_set = set(synced_rule_files(plugin_dir))
        for name in synced_rule_files(project_dir):
            if name in plugin_set:
                continue  # present in canonical source = propagated rule (the canonical-source walk handles overriding)
            if name in gitignored[gi_key]:
                orphan.append(prefix + name)  # was propagated, then deleted from the canonical source → deletion target
            else:
                protected.append(prefix + name)  # self-authored rule → preserve (untouched)
    merged["orphan"] = sorted(orphan)
    merged["protected"] = sorted(protected)
    return merged


def rules_sync_state_path(workspace_root: str) -> str:
    return os.path.join(runtime_dir(workspace_root), RULES_SYNC_STATE_FILE)


def load_sync_state(workspace_root: str) -> dict | None:
    """Read the rule sync state (None if absent/corrupt — caller falls back to stateless)."""
    try:
        with open(rules_sync_state_path(workspace_root), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_sync_state(workspace_root: str, state: dict) -> None:
    """Write the rule sync state (atomic os.replace — POSIX·Windows compatible, blocks partial writes)."""
    os.makedirs(runtime_dir(workspace_root), exist_ok=True)
    path = rules_sync_state_path(workspace_root)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _compute_domain_hashes(
    prev_hashes: dict,
    plugin_dir: str,
    project_dir: str,
    skip_set: "set[str]",
) -> "tuple[dict, list[str]]":
    """Compute one domain's (rules or rule-details) (hash map, synced list).

    S(hashes[name]) = hash of the current project copy body. skip (unresolved conflict) =
    preserve the previous S (prevents misjudging a hand edit as upstream-stale next session
    and auto-overwriting it). If there is no previous S, it is not recorded."""
    hashes: dict = {}
    synced: list[str] = []
    for name in synced_rule_files(plugin_dir):
        proj_path = os.path.join(project_dir, name)
        if not os.path.isfile(proj_path):
            continue
        if name in skip_set:
            if name in prev_hashes:
                hashes[name] = prev_hashes[name]
            continue
        try:
            with open(proj_path, encoding="utf-8") as f:
                hashes[name] = _hash_body(strip_marker_prefix(f.read()))
            synced.append(name)
        except OSError:
            continue
    return hashes, synced


def build_sync_state(
    prev_state: dict | None,
    plugin_rules: str,
    project_rules: str,
    version: str,
    skip: "set[str] | tuple[str, ...]" = (),
    *,
    plugin_details: str | None = None,
    project_details: str | None = None,
    skip_details: "set[str] | tuple[str, ...]" = (),
) -> dict:
    """Build the state to persist after applying a sync.

    S(rule_hashes[name]) = hash of the current project copy body (= the last synced body).
    - applied · in_sync files: updated to the current copy hash (after applying, identical to the canonical source).
    - skip (unresolved conflict): **preserve the previous S** — so a hand edit is not
      misjudged as upstream-stale next session and auto-overwritten (blocks silent loss).
      If there is no previous S, it is not recorded (stateless next round).
    If rule-details domain dirs are provided, `rule_details_hashes`/`synced_detail_files`
    are also recorded (omitted → rules-only — compatible with existing calls). applied_at
    is stamped by the caller (this module does not access time)."""
    prev = prev_state or {}
    rule_hashes, synced = _compute_domain_hashes(
        prev.get("rule_hashes", {}), plugin_rules, project_rules, set(skip)
    )
    state = {
        "applied_version": version,
        "rule_hashes": rule_hashes,
        "synced_files": sorted(synced),
    }
    if plugin_details is not None and project_details is not None:
        detail_hashes, detail_synced = _compute_domain_hashes(
            prev.get("rule_details_hashes", {}),
            plugin_details,
            project_details,
            set(skip_details),
        )
        state["rule_details_hashes"] = detail_hashes
        state["synced_detail_files"] = sorted(detail_synced)
    return state


def write_rule_copy(project_rules: str, name: str, final_body: str) -> None:
    """Update the project copy (.claude/rules/{name}) to final_body (atomic os.replace).

    final_body = the wrap-applied body produced by detect_rule_drift — since the content
    never passes through the AI (blocking line-number/re-emit errors), it is byte-exact to
    the canonical source. Allowing a tool-usage script here is more robust than N Write-tool
    calls because this is a batch-transactional sync that needs backup+write+state atomicity.
    """
    path = os.path.join(project_rules, name)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(final_body)
    os.replace(tmp, path)


def backup_rule_copy(
    workspace_root: str,
    project_rules: str,
    name: str,
    suffix: str = "bak",
    domain: str = "rules",
) -> str | None:
    """Right before an override/conflict apply, preserve one copy of the current copy at
    .flow/.runtime/rules-backup/{domain}/{name}.{suffix} (the only safety net for
    uncommitted hand edits). None if the copy does not exist.

    domain = 'rules' | 'rule-details' — separated into per-domain subdirectories so that
    same-named files in rules/ and rule-details/ (e.g. flow-rules.md in both) do not
    overwrite each other when backed up in the same apply.
    """
    src = os.path.join(project_rules, name)
    if not os.path.isfile(src):
        return None
    bdir = os.path.join(runtime_dir(workspace_root), "rules-backup", domain)
    try:
        os.makedirs(bdir, exist_ok=True)
        with open(src, encoding="utf-8") as f:
            data = f.read()
        dst = os.path.join(bdir, f"{name}.{suffix}")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(data)
        return dst
    except OSError:
        return None


def apply_rule_upgrade(
    workspace_root: str,
    *,
    suffix: str = "bak",
    applied_at: str = "",
) -> dict:
    """The apply step of /flow-upgrade (rule-sync SSOT — invoked by the command).

    Propagated-rule model — a propagated rule (a copy of the canonical source) is a
    generated artifact, so it is **auto-synced** (no approval argument):
    - stale (canonical changed) + missing_new (new propagated rule): override/add via
      backup + write_rule_copy + register in `.gitignore` at file granularity (artifact marking, idempotent).
    - orphan (propagated rule that vanished from the canonical source): back up, then delete the copy + remove the `.gitignore` line.
    - protected (consumer-authored rule): untouched (reported only).
    rule-details are synced together — items are distinguished by `DETAIL_PREFIX` and routed to the correct directory.
    suffix/applied_at are passed by the command (this module does not access time — deterministic · resume-safe)."""
    project_rules = project_rules_dir(workspace_root)
    project_details = project_rule_details_dir(workspace_root)
    prev = load_sync_state(workspace_root)
    drift = detect_rule_drift_all(workspace_root)
    final = drift["final_bodies"]

    # Auto-apply propagated rules (stale=override + missing_new=new addition). No conflict — always applied.
    applied: list[str] = []
    backups: list[str] = []
    registered: list[str] = []
    # **All** propagated rules (those present in the canonical source = in_sync+stale+missing_new) → register in `.gitignore` (artifact marking).
    # Registration is independent of change (marking) — in_sync (unchanged) must also be registered so existing installs migrate from tracked→ignored.
    for name in drift["in_sync"] + drift["stale"] + drift["missing_new"]:
        is_detail = name.startswith(DETAIL_PREFIX)
        real = name[len(DETAIL_PREFIX):] if is_detail else name
        if register_rule_override(workspace_root, real, is_detail=is_detail):
            registered.append(name)
    # Apply (override=stale / new addition=missing_new). in_sync is unchanged (registration only, above).
    for name in list(drift["stale"]) + list(drift["missing_new"]):
        if name not in final:
            continue
        # DETAIL_PREFIX items are routed to the rule-details domain (prefix stripped from the name).
        if name.startswith(DETAIL_PREFIX):
            real, pdir, domain = name[len(DETAIL_PREFIX):], project_details, "rule-details"
        else:
            real, pdir, domain = name, project_rules, "rules"
        os.makedirs(pdir, exist_ok=True)  # .claude/rule-details may be absent on first sync
        b = backup_rule_copy(workspace_root, pdir, real, suffix, domain=domain)
        if b:
            backups.append(b)
        write_rule_copy(pdir, real, final[name])
        applied.append(name)

    # orphan deletion (propagated rule that vanished from the canonical source): back up, then rm + remove the .gitignore line. Self-authored rules untouched.
    deleted: list[str] = []
    for name in drift["orphan"]:
        if name.startswith(DETAIL_PREFIX):
            real, pdir, domain, is_detail = name[len(DETAIL_PREFIX):], project_details, "rule-details", True
        else:
            real, pdir, domain, is_detail = name, project_rules, "rules", False
        path = os.path.join(pdir, real)
        try:
            if os.path.isfile(path):
                backup_rule_copy(workspace_root, pdir, real, suffix, domain=domain)
                os.remove(path)
            unregister_rule_override(workspace_root, real, is_detail=is_detail)
            deleted.append(name)
        except OSError:
            continue

    version = drift.get("plugin_version", "")
    state = build_sync_state(
        prev,
        plugin_rules_dir(),
        project_rules,
        version,
        plugin_details=plugin_rule_details_dir(),
        project_details=project_details,
    )
    if applied_at:
        state["applied_at"] = applied_at
    write_sync_state(workspace_root, state)
    return {
        "applied": sorted(applied),
        "deleted": sorted(deleted),
        "registered": sorted(registered),
        "protected": sorted(drift["protected"]),
        "backups": backups,
        "plugin_version": version,
    }


# ===== Retrospective rigor =====
# SSOT body = `flow-retrospective` Part 4 (§4-1 labels / §4-3 schema / §4-4 guard / §4-5 default).

# §4-5 migration default — preserves current hook behavior when settings are absent (compatibility-safe).
RIGOR_DEFAULT = {
    "action":     "template",
    "story":      "template",
    "epic":       "template+rt",
    "initiative": "template+rt",  # §4-4 guard — none cannot be exempted
}

# §4-1 four label levels.
VALID_RIGOR = {"none", "minimal", "template", "template+rt"}


def read_retrospective_settings(workspace_root: str) -> dict:
    """SSOT shared by 4 hooks — returns ``.flow/settings.json``'s ``retrospective.levels`` fail-safe.

    Return shape: ``{"action": "<label>", "story": "...", "epic": "...", "initiative": "..."}``.

    **fail-safe** (throws zero exceptions) — returns the default in all 4 cases:

    1. file absent
    2. JSON parse failure
    3. ``retrospective`` key absent
    4. label value outside the 4 kinds (outside ``VALID_RIGOR``)

    **§4-4 initiative guard**: on finding ``initiative.rigor == "none"``, force ``template+rt`` + a stderr warning.

    Details: ``flow-retrospective`` Part 4.
    """
    result = dict(RIGOR_DEFAULT)
    settings_path = os.path.join(workspace_root, ".flow", "settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return result  # ①·② — file absent or JSON parse failure
    levels = (data.get("retrospective") or {}).get("levels") or {}  # ③ key absent
    for level in result:
        rigor = (levels.get(level) or {}).get("rigor")
        if rigor in VALID_RIGOR:  # ④ — invalid values keep the default
            result[level] = rigor
    # §4-4 initiative guard
    if result["initiative"] == "none":
        print(
            "[flow] WARNING: ignoring initiative.rigor = none. "
            "Forcing template+rt (value-proposition consistency evaluation is mandatory — §4-4).",
            file=sys.stderr,
        )
        result["initiative"] = "template+rt"
    return result


def seed_settings_defaults(workspace_root: str) -> dict:
    """Seed the plugin's internal defaults (``config-defaults.json``) into the project's
    ``.flow/settings.json`` — **idempotent · non-destructive**. Existing top-level keys
    are untouched (preserves team customizations).

    Purpose: invoked by ``/flow-upgrade`` — so an existing install receives new defaults
    (e.g. ``upstream_board`` — the retrospective upstream board) from an update alone,
    without reworking its settings.

    Returns: ``{"seeded": [key...], "preserved": [key...], "settings_missing": bool}``.

    **Non-destructive guarantee** (throws zero exceptions — consistent with the
    `read_retrospective_settings` fail-safe pattern):
    - settings file absent → ``settings_missing: True``, **not created** (an unconfigured project is config's job).
    - defaults file / settings JSON parse failure → no seeding (protects a broken file).
    - if a default key already exists in settings → ``preserved`` — not overwritten.
    - meta keys starting with ``_`` (``_comment``) are ignored.
    """
    defaults_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config-defaults.json",
    )
    try:
        with open(defaults_path, "r", encoding="utf-8") as f:
            raw_defaults = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"seeded": [], "preserved": [], "settings_missing": False}
    if not isinstance(raw_defaults, dict):
        return {"seeded": [], "preserved": [], "settings_missing": False}
    defaults = {k: v for k, v in raw_defaults.items() if not k.startswith("_")}

    settings_path = os.path.join(workspace_root, ".flow", "settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except FileNotFoundError:
        return {"seeded": [], "preserved": [], "settings_missing": True}
    except (OSError, json.JSONDecodeError):
        return {"seeded": [], "preserved": [], "settings_missing": False}
    if not isinstance(settings, dict):
        return {"seeded": [], "preserved": [], "settings_missing": False}

    seeded: list = []
    preserved: list = []
    for key, value in defaults.items():
        if key in settings:
            preserved.append(key)
        else:
            settings[key] = value
            seeded.append(key)

    if seeded:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
            f.write("\n")
    return {"seeded": seeded, "preserved": preserved, "settings_missing": False}


# ===== Quality-gate adapter (TS-003 — wiring up project check commands[]) =====
# The generic adapter stays thin (a calling convention); the actual checks are per-project. Adapter=quality_gate_cli.py.

# Check keys the adapter recognizes (declared by the project in settings.json `commands`).
QUALITY_CHECK_KEYS = ("test", "lint", "analyze")


def read_quality_commands(workspace_root: str) -> dict:
    """Return ``.flow/settings.json``'s ``commands`` fail-safe (TS-003 adapter input).

    Return shape: ``{"test": str|None, "lint": str|None, "analyze": str|None, "required_checks": [str]}``.
    ``required_checks`` = the list of check keys for which, on failure, the adapter triggers
    its **minimal failure action** (block · report · abort).

    **fail-safe** (throws zero exceptions — consistent with the `read_retrospective_settings` pattern):
    1. file absent / 2. JSON parse failure / 3. ``commands`` key absent or not a dict
       → all yield an empty config (``required_checks: []`` → adapter no-op pass).
    Value validity: a check command is a **non-empty str or non-empty argv list** (M-1 — OS-independent);
    ``required_checks`` accepts only declared check keys (QUALITY_CHECK_KEYS). (Handling the config-error of a key that is required but has no declared command is the adapter CLI's job — M-2.)
    """
    result: dict = {k: None for k in QUALITY_CHECK_KEYS}
    result["required_checks"] = []
    settings_path = os.path.join(workspace_root, ".flow", "settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return result  # ①·② absent/parse-failure
    commands = data.get("commands")
    if not isinstance(commands, dict):
        return result  # ③ key absent or malformed
    for key in QUALITY_CHECK_KEYS:
        value = commands.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value
        elif isinstance(value, list) and value:  # M-1: allow argv list (OS-independent — Windows-path safe)
            result[key] = [str(x) for x in value]
    required = commands.get("required_checks")
    if isinstance(required, list):
        # only declared check keys (typos/undefined keys ignored — fail-safe)
        result["required_checks"] = [c for c in required if c in QUALITY_CHECK_KEYS]
    return result
