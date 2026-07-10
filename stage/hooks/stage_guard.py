#!/usr/bin/env python3
"""Stage hook guard.

The hook keeps Stage rules executable without depending on host-specific shell
scripts. It accepts Claude hook JSON on stdin and writes hook JSON on stdout.
"""

from __future__ import annotations

import hashlib
import json
import uuid
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Sibling modules load by bare name; make the hooks dir importable whether this
# file is run directly (hooks.json), imported (`import stage_guard`), or loaded
# by file path (`spec_from_file_location` in the CLI and tests).
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import (  # noqa: E402  (after sys.path bootstrap)
    DEFAULT_EXCLUDED_PREFIXES,
    clean_path_text,
    entry_relative_to_workspace,
    governance_broken,
    is_outside_workspace,
    is_source_path,
    is_stage_internal_path,
    load_governance,
    normalize_path_text,
    path_has_prefix,
    path_targets_stage_archive,
    path_targets_stage_past,
    path_targets_stage_root,
    relative_to_workspace,
    stage_real_root,
    stage_relative_forms,
)


SHELL_TOOLS = {"Bash", "run_in_terminal"}
WRITE_TOOLS = {
    "Edit",
    "MultiEdit",
    "NotebookEdit",
    "Write",
    "apply_patch",
    "create_file",
    "editFiles",
    "edit_files",
    "edit_notebook_file",
    "multi_replace_string_in_file",
    "replace_string_in_file",
}

STAGE_MUTATION_TOOLS = SHELL_TOOLS | WRITE_TOOLS
OS_SCRIPT_SUFFIXES = (".sh", ".bash", ".zsh", ".fish", ".ps1", ".cmd", ".bat")
SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".dart",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".scss",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".adoc"}
GIT_GLOBAL_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
# find options legal BEFORE the start paths (GNU `-H/-L/-P/-O/-D`, BSD adds
# `-E/-X/-x/-s/-d/-f`). Argument-consuming ones (`-D`, `-f`) are handled at the
# scan site. BSD clusters the argument-less ones into one token (`-Lx`, `-dsx`)
# — FIND_PRE_PATH_CLUSTER_RE matches any such cluster.
FIND_PRE_PATH_FLAGS = {"-H", "-L", "-P", "-E", "-X", "-x", "-s", "-d"}
FIND_PRE_PATH_CLUSTER_RE = re.compile(r"-[HLPEXdsx]+")
WORK_OPEN_STATUSES = {"active", "review", "blocked"}
WORK_FINAL_STATUSES = {"completed", "archived", "rejected"}
VERIFICATION_DONE = {"passed", "not_required"}
RETROSPECTIVE_DONE = {"completed"}
PROMOTION_FINAL = {"approved", "promoted", "deferred", "not_applicable", "rejected"}
REDIRECT_RE = re.compile(r"(?:^|[\s])(?:>>|[0-9]?>)\s*(?P<path>[^&|;\s]+)")
PATCH_FILE_RE = re.compile(r"^\*{3} (?:Add|Update|Delete) File: (?P<path>.+)$|^\*{3} Move to: (?P<move>.+)$", re.MULTILINE)
SHELL_SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}


@dataclass(frozen=True)
class WorkItem:
    path: Path
    item_id: str
    title: str
    status: str
    verification: str
    retrospective: str
    promotion: str
    scope: tuple[str, ...]
    promotes: tuple[str, ...]
    retrospective_ref: str = ""
    kind: str = ""
    parent: str = ""


def configure_stdio() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_workspace_root(payload: dict[str, Any]) -> Path:
    # Claude Code sets CLAUDE_PROJECT_DIR; Codex sets no workspace env var and
    # instead runs hooks with cwd = workspace plus a `cwd` payload field.
    for key in ("CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()

    for key in ("cwd", "workspace_root", "workspaceRoot", "project_root", "projectRoot"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return Path(value).expanduser().resolve()

    return Path.cwd().resolve()


def normalize_event(event: str | None, payload: dict[str, Any]) -> str:
    candidate = event or payload.get("hook_event_name") or payload.get("hookEventName") or ""
    return str(candidate).strip().replace("_", "-").lower()


def tool_name(payload: dict[str, Any]) -> str:
    value = payload.get("tool_name") or payload.get("toolName") or payload.get("tool")
    return str(value or "")


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input") or payload.get("toolInput") or {}
    return value if isinstance(value, dict) else {}


def iter_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(iter_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(iter_strings(item))
    return strings


def collect_explicit_paths(payload: dict[str, Any]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(path: str) -> None:
        # Keep `..` (clean, not normalize): a symlink-then-`..` target must reach
        # relative_to_workspace intact so the filesystem resolve — not a lexical
        # pre-collapse — decides where the write truly lands.
        cleaned = clean_path_text(path)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            found.append(cleaned)

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                visit(child_value, str(child_key))
            return
        if isinstance(value, list):
            for child_value in value:
                visit(child_value, key)
            return
        if not isinstance(value, str):
            return

        lowered_key = key.lower()
        if "path" in lowered_key or "file" in lowered_key:
            add(value)

    visit(payload)
    return found


def command_text(payload: dict[str, Any]) -> str:
    data = tool_input(payload)
    for key in ("command", "cmd", "script"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return ""


SHELL_OPERATOR_CHARS = ";&|"
def _parse_heredoc_delimiter(command: str, pos: int) -> tuple[str, bool, int] | None:
    """Delimiter word after `<<`/`<<-`, with shell quote removal: `<<\\EOF`,
    `<<'EOF'`, and `<<E"OF"` all yield `EOF`. Returns (delimiter, dash, end
    index) — `dash` is True for `<<-` (body lines may be tab-indented) — or None
    if no word follows."""
    index = pos
    length = len(command)
    dash = index < length and command[index] == "-"
    if dash:
        index += 1
    while index < length and command[index] in " \t":
        index += 1
    delim: list[str] = []
    quote: str | None = None
    while index < length:
        char = command[index]
        if quote:
            if char == quote:
                quote = None
            else:
                delim.append(char)
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            index += 1
            continue
        if char == "\\" and index + 1 < length:
            delim.append(command[index + 1])
            index += 2
            continue
        if char in " \t\n\r;&|<>()`":
            break
        delim.append(char)
        index += 1
    if not delim:
        return None
    return "".join(delim), dash, index
# Sentinels stand in for QUOTED/ESCAPED control chars and for the `&` inside an
# fd redirection, so the shlex pass never treats them as real separators. They
# are private-use code points that cannot occur in a real command; the path and
# name extractors restore them via _restore_sentinels before use.
_SENTINELS = {";": "", "&": "", "|": ""}
_SENTINEL_REVERSE = {ord(v): k for k, v in _SENTINELS.items()}


def _restore_sentinels(text: str) -> str:
    return text.translate(_SENTINEL_REVERSE)


def normalize_shell_control(command: str) -> str:
    """Prepare a command for single-pass tokenization with a quote/escape state
    machine — the only structure the delete/write gates need above shlex:

    - splice backslash-newline line continuations,
    - turn UNQUOTED newlines into `;` separators (multiline quotes stay intact),
    - replace quoted/escaped `;`/`&`/`|` and fd-redirection `&` (`2>&1`, `&>`,
      `>&`) with sentinels so they are not read as command separators,
    - drop heredoc BODIES (`cat <<EOF … EOF`) — data, not commands — but ONLY
      for an unquoted `<<` outside `$(( ))` arithmetic (a quoted `'<<EOF'` and
      the shift in `$((1<<2))` are not heredocs). `<<<` never triggers this.
    """
    out: list[str] = []
    quote: str | None = None
    pending_delims: list[tuple[str, bool]] = []
    arith_depth = 0  # `$((` nesting — a `<<` inside is a shift, not a heredoc
    index = 0
    length = len(command)
    while index < length:
        char = command[index]
        if quote:
            out.append(_SENTINELS.get(char, char) if char in _SENTINELS else char)
            if char == "\\" and quote == '"' and index + 1 < length:
                nxt = command[index + 1]
                out.append(_SENTINELS.get(nxt, nxt))
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            out.append(char)
            index += 1
            continue
        if char in ("\\", "`") and index + 1 < length:
            # `\` (POSIX) and PowerShell backtick both escape the next char.
            nxt = command[index + 1]
            if char == "\\" and nxt == "\n":  # line continuation → splice lines
                index += 2
                continue
            if nxt in _SENTINELS:  # escaped operator is a literal, not a separator
                out.append(_SENTINELS[nxt])
                index += 2
                continue
            out.append(char)
            out.append(nxt)
            index += 2
            continue
        if command[index : index + 3] == "$((":
            arith_depth += 1
            out.append("$((")
            index += 3
            continue
        # Bare arithmetic command `(( … ))` — a `<<` inside is a shift, not a
        # heredoc. Distinct from a subshell `( ( … ) )` (a space between parens).
        if command[index : index + 2] == "((":
            arith_depth += 1
            out.append("((")
            index += 2
            continue
        if arith_depth and command[index : index + 2] == "))":
            arith_depth -= 1
            out.append("))")
            index += 2
            continue
        if char == "&":  # fd redirection `&` (`2>&1`, `&>`, `>&`) is not background
            prev = out[-1] if out else ""
            nxt = command[index + 1 : index + 2]
            if prev.endswith(">") or nxt == ">":
                out.append(_SENTINELS["&"])
                index += 1
                continue
        if (
            char == "<"
            and not arith_depth
            and command[index + 1 : index + 2] == "<"
            and command[index + 2 : index + 3] != "<"  # not a `<<<` here-string
        ):
            parsed = _parse_heredoc_delimiter(command, index + 2)
            if parsed is not None:
                delimiter, dash, end = parsed
                pending_delims.append((delimiter, dash))
                out.append(command[index:end])
                index = end
                continue
        if char in "\n\r":
            out.append(";")  # unquoted newline separates commands
            index += 1
            if pending_delims:
                index = _skip_heredoc_bodies(command, index, pending_delims)
                pending_delims = []
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _skip_heredoc_bodies(command: str, start: int, delimiters: list[tuple[str, bool]]) -> int:
    """Advance past heredoc body lines, one delimiter at a time (a command may
    open several: `cmd <<A <<B`). The terminator line must equal the delimiter
    EXACTLY for `<<` (a space- or tab-indented line is still body); for `<<-`
    only leading TABS are stripped. If a delimiter line never appears, the `<<`
    was not really a heredoc (a misdetection) — return to `start` so the body is
    scanned conservatively rather than swallowing the rest of the command."""
    length = len(command)
    cursor = start
    for delimiter, dash in delimiters:
        found = False
        while cursor < length:
            line_end = command.find("\n", cursor)
            if line_end == -1:
                line_end = length
            line = command[cursor:line_end]
            cursor = line_end + 1 if line_end < length else length
            candidate = line.lstrip("\t") if dash else line
            if candidate.rstrip("\r") == delimiter:
                found = True
                break
        if not found:
            return start
    return cursor


def shell_tokens(command: str) -> list[str]:
    """Tokenize a command with shell control operators (`;`, `&`, `&&`, `|`,
    `||`) as their OWN tokens even without surrounding whitespace, so the
    delete-gate grouping is not fooled by `true;find .stage -delete`. Quoting is
    honored (a `;` inside quotes stays in its word), line continuations are
    spliced, heredoc bodies are dropped, and unquoted newlines become `;`
    separators — the whole command is tokenized once so multiline quotes
    survive."""
    prepared = normalize_shell_control(command)
    try:
        lexer = shlex.shlex(
            prepared, posix=os.name != "nt", punctuation_chars=SHELL_OPERATOR_CHARS
        )
        lexer.whitespace_split = True
        lexer.commenters = ""  # shlex.split does not treat `#` as a comment
        return list(lexer)
    except ValueError:
        return []


def _is_traversable_dir(path: Path) -> bool:
    """An existing directory the shell can actually cd into — `is_dir()` alone
    is not enough, a directory without execute/traverse permission fails."""
    try:
        return path.is_dir() and os.access(path, os.X_OK)
    except (OSError, RuntimeError):
        return False


def _walk_cd(anchor: Path, target: str) -> Path | None:
    """LOGICAL directory after `cd <target>` from `anchor`, or None when the
    real shell's cd would FAIL. Bash `cd -L` (the default) applies `..` to the
    logical path — `cd link ; cd ..` (link -> build/deep) returns to link's
    logical parent, not the physical one — so `..` pops a segment lexically and
    symlinks stay UNRESOLVED in the returned path. Each visited prefix must be a
    traversable directory (existence + execute permission), so
    `cd build/missing/..` and a permission-denied `cd` both fail. Write
    classification resolves this logical path later (relative_to_workspace)."""
    text = clean_path_text(target)
    try:
        candidate = Path(text).expanduser()
    except RuntimeError:
        candidate = Path(text)
    if candidate.is_absolute():
        cursor = Path(candidate.anchor)
        segments = candidate.parts[1:]
    else:
        cursor = anchor
        segments = candidate.parts
    for segment in segments:
        if segment == ".":
            continue
        cursor = cursor.parent if segment == ".." else cursor / segment
        if not _is_traversable_dir(cursor):
            return None
    return cursor


REDIRECT_OPERATOR_RE = re.compile(r"^(?:\d*(?:>>?|<)|&>>?|>&|<<<?)$")
REDIRECT_ATTACHED_RE = re.compile(r"^(?:\d*(?:>>?|<)|&>>?)")
# Wrappers that can run the shell BUILTIN `cd` (`command cd x`, `builtin cd x`).
# External-process wrappers (`nohup`, `nice`, `time`, `stdbuf`) cannot — they
# would fail to find an external `cd`, leaving the shell put — so they are not
# peeled: their `cd` is treated as a no-op, which keeps the caller anchor.
COMMAND_WRAPPERS = {"command", "builtin", "exec"}
# PowerShell cwd verbs/aliases mapped to their POSIX cwd-command equivalent.
POWERSHELL_CWD = {
    "set-location": "cd",
    "sl": "cd",
    "chdir": "cd",
    "push-location": "pushd",
    "pop-location": "popd",
}


def _cd_has_unknown_option(positional: list[str]) -> bool:
    """A `cd` flag bash does not support (`cd -Z`) makes the real cd fail. Only
    `-L`/`-P`/`-e`/`-@` are valid; `--` ends option parsing, `-` is OLDPWD."""
    for token in positional:
        if token == "--":
            return False
        if token in ("-", "") or not token.startswith("-"):
            continue
        if not set(token[1:]) <= set("LPe@"):
            return True
    return False


def _cd_operands(positional: list[str]) -> list[str]:
    """cd/pushd path operands. A `--` ends option parsing, so a dash-led path
    after it (`cd -- -foo`) is a real operand, not a flag."""
    operands: list[str] = []
    after_ddash = False
    for token in positional:
        if after_ddash:
            operands.append(token)
        elif token == "--":
            after_ddash = True
        elif token == "-" or token.startswith("-"):
            continue
        else:
            operands.append(token)
    return operands


REDIRECT_INFIX_RE = re.compile(r"\d*(?:>>?|<)|&>>?")


def _strip_redirections(tokens: list[str]) -> list[str]:
    """Drop redirection operators and their targets so `cd build >/dev/null`
    parses as a single-operand `cd build`, not a multi-operand error. A bare
    operator (`>`, `2>`, `<`) consumes the following target token; an attached
    prefix (`>/dev/null`) is dropped whole; and a redirection glued to an
    operand (`build>/dev/null`) keeps only the operand prefix."""
    positional: list[str] = []
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            continue
        if REDIRECT_OPERATOR_RE.match(token):
            skip_next = True
            continue
        if REDIRECT_ATTACHED_RE.match(token):
            continue
        match = REDIRECT_INFIX_RE.search(token)
        if match and match.start() > 0:  # `build>/dev/null` → keep `build`
            positional.append(token[: match.start()])
            continue
        positional.append(token)
    return positional


def _is_separator(token: str) -> bool:
    """A command separator: a known operator, or a run of only `;` (`;;`, from a
    `;` immediately followed by a newline that normalization turns into `;`)."""
    return token in SHELL_SEPARATORS or (bool(token) and set(token) == {";"})


def _dedup_dirs(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        if path not in out:
            out.append(path)
    return out


class _CwdTracker:
    """Best-effort effective-cwd tracker for the delete gate.

    The shell's cwd is dynamic, so this keeps a SET of POSSIBLE cwds and denies
    if ANY of them would delete the Stage tree — fail closed. A definite change
    (first group, or after `;`/`&`/newline) replaces the set; a change whose
    own execution is uncertain (after `&&`/`||`/`|`, or feeding a pipeline that
    runs it in a subshell) UNIONS the new state with the prior one. Failed cd
    (missing directory) and unknown targets keep the prior anchors."""

    def __init__(self, anchors: list[Path]):
        self.anchors = list(anchors)
        self.oldpwd = list(anchors)  # `cd -` destination
        self.stack: list[list[Path]] = []  # pushd/popd directory stack

    def _home(self) -> list[Path]:
        try:
            return [Path.home().resolve()]
        except (OSError, RuntimeError):
            return list(self.anchors)

    def _walk_all(self, operand: str) -> tuple[list[Path], bool]:
        # Per anchor: the rebased dir if cd succeeds there, else the anchor
        # itself (the real shell stays put on a failed cd) — both branches kept.
        # `ok` is True if the cd succeeded from ANY branch.
        dirs: list[Path] = []
        ok = False
        for anchor in self.anchors:
            dest = _walk_cd(anchor, operand)
            dirs.append(dest if dest is not None else anchor)
            ok = ok or dest is not None
        return dirs, ok

    def apply(self, name: str, operands: list[str], has_dash: bool, conditional: bool) -> None:
        old = list(self.anchors)
        succeeded = True  # OLDPWD/stack mutate only when the change really ran
        pushed = False
        if name == "cd":
            if has_dash:  # cd - → OLDPWD
                rebased = list(self.oldpwd)
            elif not operands:  # bare cd → HOME
                rebased = self._home()
            elif len(operands) > 1:  # `cd a b` is a bash error — shell stays put
                rebased, succeeded = old, False
            else:
                rebased, succeeded = self._walk_all(operands[0])
        elif name == "pushd":
            if operands and not has_dash:
                # `pushd +N`/`-N` (indexed stack rotation) is best-effort: the
                # operand is not a path, so _walk_all fails and the anchor is
                # kept. Deliberately not modelled (see hooks/README.md §Limits).
                rebased, succeeded = self._walk_all(operands[0])
                if succeeded:
                    self.stack.append(old)
                    pushed = True
            elif self.stack:  # bare pushd swaps cwd with stack top
                rebased = list(self.stack[-1])
                self.stack[-1] = old
            else:
                rebased, succeeded = old, False
        elif name == "popd":
            if self.stack:
                rebased = list(self.stack[-1])
                if not conditional:
                    self.stack.pop()
            else:  # empty stack → popd fails, shell stays put
                rebased, succeeded = old, False
        else:
            rebased = old
        # OLDPWD advances only on a successful cd/pushd that is not a phantom.
        if succeeded and (name != "pushd" or pushed or not operands):
            self.oldpwd = old
        self.anchors = _dedup_dirs(old + rebased if conditional else rebased)


def _contains_stage(target: Path, stage_real: Path) -> bool:
    """Whether recursively deleting `target` removes the Stage root — target IS
    the Stage root or an ANCESTOR of it (`rm -rf .`, `find . -delete` from the
    workspace traverse into `.stage` and erase it with everything else)."""
    try:
        stage_real.relative_to(target)
        return True
    except ValueError:
        return False


def _targets_stage_root(
    arg: str,
    workspace_root: Path | None = None,
    follow_symlinks: bool = False,
    base_dir: Path | None = None,
) -> bool:
    """follow_symlinks: the caller's tool TRAVERSES a symlink operand (find
    -H/-L/-follow) instead of acting on the link itself — classify by the fully
    dereferenced location and drop the link-only exemption. base_dir: anchor
    for relative operands when a preceding `cd` moved the shell off the
    workspace root."""
    if workspace_root is not None:
        # `rm`/`find -delete` unlink what the operand NAMES: parent symlinks and
        # `..` are traversed, but a final symlink operand removes only the LINK
        # (its target survives). So resolve the parent, keep the final entry —
        # `find link/.. -delete` (link -> .stage/present) hits `.stage`, while
        # `rm -rf alias` (alias -> .stage) removes only `alias`.
        try:
            text = clean_path_text(arg)
            # A trailing slash OR `/.` forces the OS to dereference a symlink
            # operand (`rm -rf alias/`, `find alias/. -delete` delete the target
            # dir), so classify by the fully resolved location in that case.
            stripped = arg.rstrip()
            trailing_slash = (
                stripped.endswith("/")
                or stripped.endswith("\\")
                or stripped.endswith("/.")
                or stripped.endswith("\\.")
            )
            base = Path(text).expanduser()
            if not base.is_absolute():
                anchor = base_dir if base_dir is not None else workspace_root.resolve()
                base = anchor / text
            stage_real = stage_real_root(workspace_root)
            try:
                logical_entry = workspace_root.resolve() / ".stage"
            except (OSError, RuntimeError):
                logical_entry = workspace_root / ".stage"

            def removes_stage(candidate: Path) -> bool:
                # The real tree, or the workspace's logical `.stage` ENTRY (an
                # ancestor delete detaches an externally symlinked harness). A
                # candidate that IS the `.stage` entry is always blocked; a
                # STRICT ancestor (`rm -rf .`) is blocked only when a `.stage`
                # actually exists, so a pre-init workspace is not over-denied.
                for base in (stage_real, logical_entry):
                    if base is None:
                        continue
                    try:
                        rel = base.relative_to(candidate).as_posix()
                    except ValueError:
                        continue
                    if rel == ".":  # candidate is the stage entry itself
                        return True
                    if base.exists() or base.is_symlink():  # strict ancestor
                        return True
                return False

            # Canonical classification is authoritative: allow/deny is decided
            # here, and the lexical fallback below serves only resolution
            # failures or calls without a workspace root — otherwise a foreign
            # `.stage` basename (`cd build && rm -rf .stage` = build/.stage)
            # would be denied by spelling alone.
            if trailing_slash:
                return removes_stage(base.resolve())
            name = base.name
            parent_real = base.parent.resolve()
            if name in ("", "."):
                target = parent_real
            elif name == "..":
                target = parent_real.parent
            else:
                target = parent_real / name
            if follow_symlinks and name not in ("", ".", ".."):
                target = target.resolve()
            if removes_stage(target):
                # A final symlink operand deletes the link, not the tree —
                # unless the tool follows it (find -H/-L/-follow), and never
                # for the workspace's own `.stage` entry, whose removal
                # detaches the harness even when only the link goes.
                if (
                    not follow_symlinks
                    and name not in ("", ".", "..")
                    and target != logical_entry
                    and target.is_symlink()
                ):
                    return False
                return True
            return False
        except (OSError, RuntimeError, ValueError):
            pass
    normalized = normalize_path_text(arg)
    return normalized == ".stage" or normalized.endswith("/.stage")


def command_deletes_stage(command: str, workspace_root: Path | None = None) -> bool:
    """Whether a shell command recursively removes the whole `.stage` tree.

    Tokenized (not a free-text regex) so recursive flags in any spelling are
    caught: `rm -r/-R/-rf/--recursive`, PowerShell `Remove-Item -Recurse`,
    Windows `rmdir /s`, and `find <.stage> -delete`/`-exec|-execdir rm`.
    Operands are resolved through symlinks when workspace_root is given.
    Non-recursive `rm .stage` cannot remove a directory, so it is not blocked.
    """
    # Relative delete operands are anchored where the shell IS: a preceding
    # `cd` group rebases them (`cd build && find . -delete` traverses build,
    # not the workspace). Control flow is not evaluated, so the tracker keeps a
    # SET of possible cwds: a cd whose own execution is conditional (preceded
    # by `&&`/`||`/`|`, e.g. `false && cd build ; rm -rf .stage`) ADDS the
    # rebased state alongside the previous ones; a definite cd (first group or
    # after `;`/newline) replaces them. Classification denies if ANY possible
    # anchor removes the Stage tree — fail closed.
    anchors: list[Path] = []
    if workspace_root is not None:
        try:
            anchors = [workspace_root.resolve()]
        except (OSError, RuntimeError):
            anchors = [workspace_root]
    tracker = _CwdTracker(anchors)

    def hits_stage(arg: str) -> bool:
        if not tracker.anchors:
            return _targets_stage_root(arg, workspace_root)
        return any(
            _targets_stage_root(arg, workspace_root, base_dir=anchor)
            for anchor in tracker.anchors
        )

    tokens = shell_tokens(command)
    simple: list[str] = []
    entries: list[tuple[str, list[str]]] = []
    previous_separator = ""
    # Grouping uses the sentinel-carrying tokens: only a REAL (unquoted,
    # unescaped) `;`/`&`/`|` is a separator. A find `-exec … \;` terminator is a
    # sentinel, so it never splits the group and a trailing `-delete` stays in.
    for token in tokens + ["\n"]:
        if _is_separator(token):
            if simple:
                entries.append((previous_separator, simple))
            simple = []
            previous_separator = token
        else:
            simple.append(token)
    for index, (separator, raw_group) in enumerate(entries):
        if not raw_group:
            continue
        # Sentinels are restored now — past the separator decision, every token
        # is a command name, flag, or path.
        group = [_restore_sentinels(tok) for tok in raw_group]
        # Peel leading builtin-capable wrappers (`command cd x`) so the real
        # command is classified, and map PowerShell cwd verbs to POSIX.
        head = 0
        while head < len(group) - 1 and Path(group[head]).name.lower() in COMMAND_WRAPPERS:
            head += 1
        group = group[head:]
        name = POWERSHELL_CWD.get(Path(group[0]).name.lower(), Path(group[0]).name.lower())
        if name in {"cd", "pushd", "popd"} and workspace_root is not None:
            positional = _strip_redirections(group[1:])
            if name == "cd" and _cd_has_unknown_option(positional):
                continue  # bash rejects the option → cwd unchanged
            pushd_no_cd = name == "pushd" and "-n" in positional
            operands = _cd_operands(positional)
            has_dash = "-" in positional and not operands
            if pushd_no_cd:  # `pushd -n DIR` edits the stack only — cwd unchanged
                continue
            # A cd whose own execution is conditional (after `&&`/`||`/`|`) may
            # not have run; a cd feeding a pipeline (`cd build | …`) or backgrounded
            # (`cd build & …`) runs in a subshell and never changes the caller's
            # cwd. Keep both states in those cases.
            next_separator = entries[index + 1][0] if index + 1 < len(entries) else "\n"
            conditional = separator in {"&&", "||", "|"} or next_separator in {"|", "&"}
            tracker.apply(name, operands, has_dash, conditional)
            continue
        flags = [tok for tok in group[1:] if tok.startswith("-") or tok.startswith("/")]
        # Path operands = anything not a `-` flag. A leading `/` is an ABSOLUTE
        # PATH on Unix (`/ws/.stage`), not a flag — Windows switches like `/s`
        # stay in `flags` but never match `_targets_stage_root`, so keeping them
        # in `args` too is harmless and lets absolute `.stage` targets be seen.
        args = [tok for tok in group[1:] if not tok.startswith("-")]
        if name == "rm":
            recursive = any(
                tok == "--recursive" or (tok.startswith("-") and not tok.startswith("--") and "r" in tok.lower())
                for tok in flags
            )
            if recursive and any(hits_stage(arg) for arg in args):
                return True
        elif name == "rmdir":
            if any(flag.lower() in {"/s", "-s", "--recursive"} for flag in flags) and any(
                hits_stage(arg) for arg in args
            ):
                return True
        elif name in {"remove-item", "ri", "rd", "del", "erase"}:
            recursive = any(flag.lower() in {"-recurse", "-r", "/s"} for flag in flags)
            force = any(flag.lower() in {"-force", "-f"} for flag in flags)
            if (recursive or force) and any(hits_stage(arg) for arg in group[1:]):
                return True
        elif name == "find":
            # find's start paths are the operands before the first expression.
            # Pre-path traversal/debug options (`find [-H|-L|-P] [-E…] [-Olevel]
            # [-D opts] [-f path] path…`) are skipped — stopping at them would
            # record no roots and wave `find -L .stage -delete` through. A
            # destructive action is `-delete`, or `-exec|-execdir` running
            # rm/rmdir/unlink ON THE DISCOVERED entry (`{}`) — not on an
            # unrelated file (`find .stage -exec rm /tmp/lock \\;`).
            roots: list[str] = []
            idx = 1
            after_ddash = False  # every operand past `--` is a start path
            while idx < len(group):
                tok = group[idx]
                if after_ddash:
                    if tok in {"(", "!"} or (tok.startswith("-") and len(tok) > 1 and tok[1].isalpha()):
                        break  # first expression primary ends the root list
                    roots.append(tok)
                    idx += 1
                    continue
                if tok == "--":  # end of options — start paths follow
                    after_ddash = True
                    idx += 1
                    continue
                if tok in FIND_PRE_PATH_FLAGS or FIND_PRE_PATH_CLUSTER_RE.fullmatch(tok):
                    idx += 1
                    continue
                if tok.startswith("-O"):  # GNU -Olevel (attached argument)
                    idx += 1
                    continue
                if tok == "-D":  # GNU debug options: consumes one argument
                    idx += 2
                    continue
                if tok == "-f":  # BSD: `-f path` names a start path
                    if idx + 1 < len(group):
                        roots.append(group[idx + 1])
                    idx += 2
                    continue
                if tok.startswith("-") or tok in {"(", "!"}:
                    break
                roots.append(tok)
                idx += 1
            deletes = False
            for idx, tok in enumerate(group):
                if tok == "-delete":
                    deletes = True
                    break
                if tok in {"-exec", "-execdir"} and idx + 1 < len(group):
                    if Path(group[idx + 1]).name in {"rm", "rmdir", "unlink"} and _find_exec_hits_found(group[idx + 1:]):
                        deletes = True
                        break
            if not roots:
                # GNU find roots at the effective current directory when no
                # start path is given (`find -delete`).
                roots.append(".")
            # `-H`/`-L` (pre-path, possibly clustered: `-Lx`) and `-follow`
            # (expression) make find traverse a symlink root instead of
            # visiting the link itself. POSIX honors the LAST of -H/-L/-P, so
            # scan in order (`find -L -P alias` runs in -P mode); a later
            # `-follow` turns following back on. Tokens INSIDE an `-exec`/
            # `-execdir` clause are the program's own arguments (`-exec echo -P
            # {}`) — skip to the terminator so they cannot pose as find options.
            follows = False
            i = 0
            while i < len(group):
                tok = group[i]
                if tok in {"-exec", "-execdir"}:
                    i += 1
                    while i < len(group) and group[i] not in {";", "+", "\\;"}:
                        i += 1
                    i += 1
                    continue
                if tok == "-follow":
                    follows = True
                elif FIND_PRE_PATH_CLUSTER_RE.fullmatch(tok):
                    for ch in tok[1:]:
                        if ch in "HL":
                            follows = True
                        elif ch == "P":
                            follows = False
                i += 1

            def find_root_hits(arg: str) -> bool:
                if not tracker.anchors:
                    return _targets_stage_root(arg, workspace_root, follow_symlinks=follows)
                return any(
                    _targets_stage_root(
                        arg, workspace_root, follow_symlinks=follows, base_dir=anchor
                    )
                    for anchor in tracker.anchors
                )

            if deletes and any(find_root_hits(arg) for arg in roots):
                return True
    return False


def _find_exec_hits_found(rest: list[str]) -> bool:
    """Whether a `find -exec CMD …` clause passes the discovered path (`{}`) to
    the destructive command before its terminator (`;` / `+`)."""
    for tok in rest[1:]:
        if tok in {";", "+", "\\;"}:
            break
        if "{}" in tok:
            return True
    return False


def shell_write_paths(command: str) -> list[str]:
    paths: list[str] = []

    def add(path: str) -> None:
        # Keep `..` intact (see collect_explicit_paths) for symlink-safe resolve.
        # Restore sentinels: a path is a real operand, not a separator boundary.
        cleaned = clean_path_text(_restore_sentinels(path))
        if cleaned and cleaned not in paths:
            paths.append(cleaned)

    for match in REDIRECT_RE.finditer(command):
        add(match.group("path"))

    tokens = shell_tokens(command)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        command_name = Path(token).name

        if command_name in {"cp", "mv"}:
            args: list[str] = []
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor] not in SHELL_SEPARATORS:
                current = tokens[cursor]
                if not current.startswith("-"):
                    args.append(current)
                cursor += 1
            if len(args) >= 2:
                add(args[-1])
            index = cursor
            continue

        if command_name == "tee":
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor] not in SHELL_SEPARATORS:
                current = tokens[cursor]
                if not current.startswith("-"):
                    add(current)
                cursor += 1
            index = cursor
            continue

        if command_name == "sed":
            cursor = index + 1
            in_place = False
            args: list[str] = []
            while cursor < len(tokens) and tokens[cursor] not in SHELL_SEPARATORS:
                current = tokens[cursor]
                if current == "-i" or current.startswith("-i"):
                    in_place = True
                elif not current.startswith("-"):
                    args.append(current)
                cursor += 1
            if in_place and args:
                add(args[-1])
            index = cursor
            continue

        index += 1

    return paths


def iter_git_commands(command: str) -> list[tuple[str, list[str]]]:
    tokens = shell_tokens(command)
    commands: list[tuple[str, list[str]]] = []

    for index, token in enumerate(tokens):
        if Path(token).name != "git":
            continue

        cursor = index + 1
        while cursor < len(tokens):
            current = tokens[cursor]
            if current in GIT_GLOBAL_OPTIONS_WITH_VALUE:
                cursor += 2
                continue
            if current.startswith("--git-dir=") or current.startswith("--work-tree="):
                cursor += 1
                continue
            if current.startswith("-"):
                cursor += 1
                continue
            args: list[str] = []
            arg_cursor = cursor + 1
            while arg_cursor < len(tokens) and tokens[arg_cursor] not in SHELL_SEPARATORS:
                args.append(_restore_sentinels(tokens[arg_cursor]))
                arg_cursor += 1
            commands.append((_restore_sentinels(current), args))
            break
    return commands


def git_subcommand(command: str) -> str:
    commands = iter_git_commands(command)
    return commands[0][0] if commands else ""


def command_has_git_commit(command: str) -> bool:
    return any(subcommand == "commit" for subcommand, _args in iter_git_commands(command))


def git_add_paths_from_command(command: str, workspace_root: Path) -> list[str]:
    paths: list[str] = []
    for subcommand, args in iter_git_commands(command):
        if subcommand != "add":
            continue
        explicit: list[str] = []
        for arg in args:
            if arg in {"-A", "--all", "-u", "--update"}:
                explicit.extend(changed_files(workspace_root, include_untracked=arg in {"-A", "--all"}))
            elif arg.startswith("-"):
                continue
            elif arg in {".", ":"}:
                explicit.extend(changed_files(workspace_root, include_untracked=True))
            else:
                explicit.append(arg)
        if not explicit:
            explicit.extend(changed_files(workspace_root, include_untracked=True))
        for path in explicit:
            normalized = normalize_path_text(path)
            if normalized not in paths:
                paths.append(normalized)
    return paths


GIT_COMMIT_VALUE_LONG_FLAGS = {"--message", "--file", "--author", "--date", "--reuse-message", "--reedit-message", "--fixup", "--squash", "--gpg-sign"}
GIT_COMMIT_VALUE_SHORT_LETTERS = set("mFCcS")


def git_commit_pathspec_files(command: str, workspace_root: Path) -> list[str]:
    """Files a `git commit` names directly as pathspec — `git commit -- a b`,
    `git commit --only path`, or trailing paths — which commit unstaged tracked
    changes without ever being `git add`-ed, bypassing the staged-files check.
    """
    paths: list[str] = []
    for subcommand, args in iter_git_commands(command):
        if subcommand != "commit":
            continue
        after_ddash = False
        index = 0
        while index < len(args):
            arg = args[index]
            if after_ddash:
                paths.append(arg)
            elif arg == "--":
                after_ddash = True
            elif arg.startswith("--"):
                name = arg.split("=", 1)[0]
                if name in GIT_COMMIT_VALUE_LONG_FLAGS and "=" not in arg:
                    index += 1  # value is the next token
            elif arg.startswith("-"):
                # Short cluster like -m, -am, -F: a value-taking letter as the
                # LAST char consumes the next token (unless attached, -mMSG).
                cluster = arg[1:]
                if cluster and cluster[-1] in GIT_COMMIT_VALUE_SHORT_LETTERS:
                    index += 1
            else:
                # A bare non-flag arg to commit is a pathspec (commit-only-these).
                paths.append(arg)
            index += 1
    normalized: list[str] = []
    for path in paths:
        value = normalize_path_text(path)
        if value and value not in {".", ":"} and value not in normalized:
            normalized.append(value)
    return normalized


def git_commit_all_requested(command: str) -> bool:
    for subcommand, args in iter_git_commands(command):
        if subcommand != "commit":
            continue
        for arg in args:
            if arg == "--all" or arg.startswith("--all="):
                return True
            if arg.startswith("-") and not arg.startswith("--") and "a" in arg[1:]:
                return True
    return False


def pre_tool_allow() -> dict[str, Any]:
    """Allow = empty output (exit 0, no stdout).

    Cross-host contract: Claude Code treats exit 0 with no stdout as "no opinion"
    — the call falls through to the host's normal permission flow (an explicit
    `permissionDecision: "allow"` would bypass permission prompts, which is not
    this gate's job). Codex additionally rejects `permissionDecision: "allow"`
    without `updatedInput` as unsupported output (the hook run is marked failed).
    """
    return {}


def deny(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def continue_output(message: str | None = None) -> dict[str, Any]:
    """Non-blocking event output: `systemMessage` only, or empty.

    Cross-host contract: Codex's Stop parser accepts `decision` only as the
    literal `"block"` — any other value fails deserialization and marks the hook
    run failed ("invalid stop hook JSON output"). Both hosts accept a bare
    `systemMessage` and treat empty stdout as "proceed".
    """
    if message:
        return {"systemMessage": message}
    return {}


def parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    fields: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def split_scope(value: str) -> tuple[str, ...]:
    """Cleaned (NOT dot-collapsed) declaration entries. `..` survives so a
    declaration spelled through a symlink (`scope: alias/../other`) reaches the
    entry canonicalization intact — a lexical pre-collapse would mis-anchor it
    (`other`) and reject the exact declared spelling."""
    if not value:
        return ()
    parts = [clean_path_text(part) for part in re.split(r"[,;]", value)]
    clean = tuple(part for part in parts if part)
    return clean


def load_work_items(stage_root: Path) -> list[WorkItem]:
    return load_items_from(stage_root / "present" / "work" / "items")


def load_archive_work_items(stage_root: Path) -> list[WorkItem]:
    return load_items_from(stage_root / "past" / "work" / "archive" / "items")


def load_items_from(items_root: Path) -> list[WorkItem]:
    if not items_root.exists():
        return []

    items: list[WorkItem] = []
    for path in sorted(items_root.glob("*.md")):
        if path.name in {"README.md", "_template.md"}:
            continue
        fields = parse_frontmatter(path)
        item_id = fields.get("id") or path.stem
        items.append(
            WorkItem(
                path=path,
                item_id=item_id,
                title=fields.get("title") or path.stem,
                status=(fields.get("status") or "active").lower(),
                verification=(fields.get("verification") or "pending").lower(),
                retrospective=(fields.get("retrospective") or "pending").lower(),
                promotion=(fields.get("promotion") or "pending").lower(),
                scope=split_scope(fields.get("scope", "")),
                promotes=split_scope(fields.get("promotes", "")),
                retrospective_ref=(fields.get("retrospective_ref") or "").strip(),
                kind=(fields.get("kind") or "").strip().lower(),
                parent=(fields.get("parent") or "").strip(),
            )
        )
    return items


def item_is_open(item: WorkItem) -> bool:
    return item.status in WORK_OPEN_STATUSES


def item_is_completed(item: WorkItem) -> bool:
    return item.status == "completed"


def item_completion_blockers(item: WorkItem) -> list[str]:
    blockers: list[str] = []
    if item.status not in WORK_OPEN_STATUSES | WORK_FINAL_STATUSES:
        blockers.append(f"{item.item_id}: unknown status `{item.status}`")
    if item_is_completed(item):
        if item.verification not in VERIFICATION_DONE:
            blockers.append(f"{item.item_id}: verification `{item.verification}`")
        if item.retrospective not in RETROSPECTIVE_DONE:
            blockers.append(f"{item.item_id}: retrospective `{item.retrospective}`")
        if item.promotion not in PROMOTION_FINAL:
            blockers.append(f"{item.item_id}: promotion `{item.promotion}`")
    return blockers


def item_matches_path(
    item: WorkItem, path: str, workspace_root: Path, follows_symlink: bool = False
) -> bool:
    # A CONTENT write (`follows_symlink=True`: Write/Edit) modifies the
    # dereferenced target, so it is matched by the RESOLVED form — a scope of
    # `aliases` must not authorize a write to `aliases/link.py -> src/app.py`,
    # which lands in src/. An UNLINK/move is matched by the entry-canonical form
    # ONLY: the leaf-dereferenced form would let two leaves aliasing one target
    # cross-authorize (`scope: src` covering a delete of `other/b.py` that
    # points at src/shared.py); the lexical form would let a collapsed spelling
    # smuggle authorization. The SCOPE side keeps all forms: a scope entry that
    # is itself a symlinked directory (`scope: link`, link -> src) is the user's
    # declared alias for that subtree.
    if follows_symlink:
        target = relative_to_workspace(path, workspace_root)
        target_forms = [target] if target and not is_outside_workspace(target) else []
    else:
        target_entry = entry_relative_to_workspace(path, workspace_root)
        target_forms = [target_entry] if target_entry else []
    for scope in item.scope:
        if normalize_path_text(scope) == "*":
            return True
        if normalize_path_text(scope) in {"", "."}:
            continue
        for normalized in _scope_match_forms(scope, workspace_root):
            for relative in target_forms:
                if relative == normalized or relative.startswith(normalized.rstrip("/") + "/"):
                    return True
    return False


def _scope_match_forms(scope: str, workspace_root: Path) -> set[str]:
    """Canonical forms a scope authorizes. The entry and lexical forms always
    apply. The leaf-dereferenced (resolved) form is added ONLY when the scope
    resolves to a DIRECTORY — a scope naming a symlinked directory (`scope:
    link`, link -> src/) is the user's alias for that subtree, but a scope
    naming a symlinked FILE (`aliases/link.py` -> src/actual.py) names one
    entry and must not authorize the distinct target it points at."""
    resolved, entry, lexical = stage_relative_forms(scope, workspace_root)
    forms = {form for form in (entry, lexical) if form}
    try:
        if (workspace_root / clean_path_text(scope)).is_dir() and resolved:
            forms.add(resolved)
    except (OSError, RuntimeError):
        pass
    return forms


def item_promotes_path(item: WorkItem, path: str, workspace_root: Path) -> bool:
    # Entry-canonical on BOTH sides: a promotion grant names an exact entry, so
    # two symlinked leaves aliasing one target must not share one grant.
    relative = entry_relative_to_workspace(path, workspace_root)
    for promoted_path in item.promotes:
        if entry_relative_to_workspace(promoted_path, workspace_root) == relative:
            return True
    return False


def archive_target_item_id(path: str, workspace_root: Path) -> str:
    relative = entry_relative_to_workspace(path, workspace_root)
    prefix = ".stage/past/work/archive/items/"
    if not relative.startswith(prefix):
        return ""
    name = Path(relative).name
    if name.lower().endswith(".md"):
        return name[:-3]
    return ""


def archive_target_retro_id(path: str, workspace_root: Path) -> str:
    relative = entry_relative_to_workspace(path, workspace_root)
    prefix = ".stage/past/work/archive/retrospectives/"
    if not relative.startswith(prefix):
        return ""
    name = Path(relative).name
    if name.lower().endswith(".md"):
        return name[:-3]
    return ""


def retrospective_ref_id(item: WorkItem) -> str:
    ref = normalize_path_text(item.retrospective_ref)
    if not ref:
        return ""
    name = Path(ref).name
    return name[:-3] if name.lower().endswith(".md") else name


def fallback_index_blockers(stage_root: Path) -> list[str]:
    active = parse_index_rows(stage_root / "present" / "work" / "active.md")
    review = parse_index_rows(stage_root / "present" / "work" / "review.md")
    blockers: list[str] = []
    if active:
        blockers.append("Work item SSOT is missing: move active.md rows into items/*.md")
    if review:
        blockers.append("Review item SSOT is missing: move review.md rows into items/*.md or retrospectives/*.md")
    return blockers


def parse_index_rows(path: Path) -> list[list[str]]:
    if not path.exists():
        return []
    rows: list[list[str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and not all(re.fullmatch(r"\s*:?-{2,}:?\s*", cell) for cell in cells):
            rows.append(cells)
    return rows[1:] if len(rows) > 1 else []


def stage_completion_blockers(workspace_root: Path) -> list[str]:
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return []

    items = load_work_items(stage_root)
    if not items:
        return fallback_index_blockers(stage_root)

    blockers: list[str] = []
    for item in items:
        blockers.extend(item_completion_blockers(item))
    return blockers


def open_items_for_paths(workspace_root: Path, paths: list[str]) -> list[WorkItem]:
    stage_root = workspace_root / ".stage"
    items = [item for item in load_work_items(stage_root) if item_is_open(item)]
    if not paths:
        return items
    return [item for item in items if any(item_matches_path(item, path, workspace_root) for path in paths)]


def staged_files(workspace_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace_root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files(workspace_root: Path, *, include_untracked: bool = False) -> list[str]:
    commands = [
        ["git", "-C", str(workspace_root), "diff", "--name-only", "--diff-filter=ACMR"],
        ["git", "-C", str(workspace_root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
    ]
    if include_untracked:
        commands.append(["git", "-C", str(workspace_root), "ls-files", "--others", "--exclude-standard"])

    paths: list[str] = []
    seen: set[str] = set()
    for command in commands:
        try:
            result = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
            )
        except OSError:
            continue
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            path = normalize_path_text(line.strip())
            if path and path not in seen:
                seen.add(path)
                paths.append(path)
    return paths


def source_registration_blocker(
    workspace_root: Path, paths: list[str], follows_symlink: bool = False
) -> str:
    source_paths = [path for path in paths if is_source_path(path, workspace_root, follows_symlink)]
    if not source_paths:
        return ""
    open_items = [item for item in load_work_items(workspace_root / ".stage") if item_is_open(item)]
    # Every governed target must be covered — otherwise one legitimate target
    # would smuggle arbitrary unregistered targets through in the same call.
    uncovered = [
        path
        for path in source_paths
        if not any(item_matches_path(item, path, workspace_root, follows_symlink) for item in open_items)
    ]
    if not uncovered:
        return ""
    return (
        "Stage registration gate violation: before modifying governed files, register an active "
        "work item with a matching scope in `.stage/present/work/items/`. "
        "Unregistered targets: " + ", ".join(uncovered[:5])
    )


def commit_blocker(workspace_root: Path, paths: list[str]) -> str:
    source_paths = [path for path in paths if is_source_path(path, workspace_root)]
    if not source_paths:
        return ""

    items = load_work_items(workspace_root / ".stage")
    missing: list[str] = []
    blockers: list[str] = []
    for path in source_paths:
        matched = [item for item in items if item_matches_path(item, path, workspace_root)]
        if not matched:
            missing.append(path)
            continue
        for item in matched:
            if item_is_completed(item):
                blockers.extend(item_completion_blockers(item))

    if missing:
        return (
            "Stage commit gate violation: committed governed files are not registered to a work item. "
            "Targets: " + ", ".join(missing[:5])
        )
    if blockers:
        return (
            "Stage completion gate violation: close the completed item's verification, retrospective, "
            "and promotion decision first. " + " / ".join(blockers)
        )
    return ""


def runtime_slot_name(value: str) -> str:
    """Filesystem-safe slot name for per-session/per-item runtime files."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", value.strip())
    return cleaned or "default"


def session_slot(payload: dict[str, Any]) -> str:
    """Concurrency dimension for `.runtime/`: both hosts send `session_id` in hook stdin."""
    return runtime_slot_name(str(payload.get("session_id") or "default"))


def intents_root(stage_root: Path) -> Path:
    return stage_root / ".runtime" / "intents"


def migrate_legacy_runtime(stage_root: Path) -> None:
    """Move 0.1.0 single-slot runtime files into the per-item/per-session layout.

    Projects initialized by the 0.1.0 release may hold a pending
    `promote-intent.json` or a `session-summary.md`; ignoring them would deny a
    legitimately prepared promotion or drop the last handoff.
    """
    runtime = stage_root / ".runtime"
    legacy_intent = runtime / "promote-intent.json"
    if legacy_intent.exists():
        try:
            data = json.loads(legacy_intent.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, dict):
            declared = intent_paths(data)
            written = [write_intent_file(stage_root, data, one) for one in declared]
            if all(target is not None for target in written):
                try:
                    legacy_intent.unlink()
                except OSError:
                    pass
    # A crashed session can leave `*.json.claim-*` reservation files behind;
    # the reservation itself already consumed the intent, so finishing the
    # deletion after a day is safe.
    now = datetime.now(timezone.utc).timestamp()
    try:
        for claim in intents_root(stage_root).glob("*.json.claim-*"):
            try:
                if now - claim.stat().st_mtime > 24 * 60 * 60:
                    claim.unlink()
            except OSError:
                pass
    except OSError:
        pass
    legacy_summary = runtime / "session-summary.md"
    if legacy_summary.exists():
        sessions = sessions_root(stage_root)
        try:
            sessions.mkdir(parents=True, exist_ok=True)
            # Never overwrite or drop an existing handoff: a taken `legacy.md`
            # slot means a prior migration or a live session already owns it, so
            # claim a fresh numbered slot instead of unlinking the incoming one.
            target = sessions / "legacy.md"
            index = 1
            while target.exists():
                target = sessions / f"legacy-{index}.md"
                index += 1
            legacy_summary.replace(target)
        except OSError:
            pass


def write_intent_file(stage_root: Path, intent: dict[str, Any], path_value: str) -> Path | None:
    """Persist a single-path intent; the slot is (work item, canonical path).

    The path is canonicalized to the ENTRY-relative workspace form (parents
    resolved, leaf kept as named) before slotting and storage, so replanting
    the same target as absolute vs relative stays idempotent while two aliased
    leaves stay distinct slots. The filename embeds the basename plus a digest
    of the full path — bounded regardless of target depth. A slot collision
    with a DIFFERENT logical (item, path) pair falls through to a numbered
    suffix instead of overwriting someone else's pending authorization.
    """
    root = intents_root(stage_root)
    try:
        workspace_root = stage_root.parent.resolve()
    except OSError:
        workspace_root = stage_root.parent
    normalized = entry_relative_to_workspace(path_value, workspace_root)
    record = {**intent, "paths": [normalized]}
    item = str(intent.get("work_item") or "intent")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]
    basename = runtime_slot_name(Path(normalized).name)[:40]
    base = f"{runtime_slot_name(item)}--{basename}-{digest}"
    try:
        root.mkdir(parents=True, exist_ok=True)
        for index in range(20):
            target = root / (base + ("" if index == 0 else f"-{index}") + ".json")
            if target.exists():
                try:
                    existing = json.loads(target.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    existing = None
                same_slot = (
                    isinstance(existing, dict)
                    and str(existing.get("work_item") or "") == item
                    and [entry_relative_to_workspace(p, workspace_root) for p in intent_paths(existing)]
                    == [normalized]
                )
                if not same_slot:
                    continue
            target.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            return target
    except OSError:
        pass
    return None


def read_intent_files(stage_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    try:
        files = sorted(intents_root(stage_root).glob("*.json"))
    except OSError:
        return []
    intents: list[tuple[Path, dict[str, Any]]] = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            intents.append((path, data))
    return intents


def load_promotion_intents(stage_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """All pending intents — one file per (work item, path) so authorizing a
    write consumes state by an atomic rename reservation, never by rewriting a
    shared file."""
    migrate_legacy_runtime(stage_root)
    intents = read_intent_files(stage_root)
    split_any = False
    for path, data in intents:
        declared = intent_paths(data)
        if len(declared) <= 1:
            continue
        # Normalize a multi-path file (pre-split layout) into per-path slots.
        if all(write_intent_file(stage_root, data, one) is not None for one in declared):
            split_any = True
            try:
                path.unlink()
            except OSError:
                pass
    if split_any:
        return read_intent_files(stage_root)
    return intents


def intent_paths(intent: dict[str, Any]) -> list[str]:
    # Cleaned, NOT dot-collapsed (see split_scope): a legacy intent spelled
    # with `..` must reach entry canonicalization intact.
    raw = intent.get("paths")
    if isinstance(raw, list):
        return [clean_path_text(str(item)) for item in raw if str(item).strip()]
    raw_path = intent.get("path")
    if isinstance(raw_path, str) and raw_path.strip():
        return [clean_path_text(raw_path)]
    return []


def promotion_blocker(workspace_root: Path, target_paths: list[str]) -> str:
    """Per-path intents make consumption an atomic rename reservation.

    Each pending intent covers exactly one path (the loader normalizes
    multi-path files), so authorizing a write never rewrites another intent's
    state — the read-modify-write race that could resurrect an already
    consumed authorization cannot occur. Acquisition is the rename to a claim
    file; the losing concurrent session is denied.
    """
    stage_root = workspace_root / ".stage"
    intents = load_promotion_intents(stage_root)
    if not intents:
        return (
            "Stage promotion gate violation: modifying `.stage/past/` requires an out-of-band "
            "promotion intent. Run `stage-retrospective`, then create one with "
            "`scripts/promote_intent.py` (writes `.stage/.runtime/intents/<work-item>--<path>.json`)."
        )

    # Entry-canonical matching: an intent authorizes the exact entry it names,
    # never a sibling alias of the same resolved target.
    requested = {entry_relative_to_workspace(path, workspace_root) for path in target_paths}
    by_path: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for intent_file, intent in intents:
        for declared in intent_paths(intent):
            by_path.setdefault(entry_relative_to_workspace(declared, workspace_root), []).append(
                (intent_file, intent)
            )

    selected: dict[Path, dict[str, Any]] = {}
    covered_paths: dict[Path, list[str]] = {}
    for path in sorted(requested):
        matching = by_path.get(path, [])
        if not matching:
            return (
                "Stage promotion gate violation: no pending intent's paths match the "
                f"modification targets ({path})."
            )
        if len(matching) > 1:
            # Fail closed on ambiguity: consuming an arbitrary intent could let
            # one work item's write ride another item's authorization.
            names = ", ".join(sorted(intent_file.name for intent_file, _ in matching))
            return (
                "Stage promotion gate violation: multiple pending intents cover the modification "
                f"targets ({names}). Remove or narrow the intents so exactly one matches."
            )
        intent_file, intent = matching[0]
        selected[intent_file] = intent
        covered_paths.setdefault(intent_file, []).append(path)

    # Validate every involved intent before consuming any (no partial consume
    # on a failing multi-target write).
    for intent_file, intent in selected.items():
        error = intent_validation_blocker(
            stage_root,
            workspace_root,
            intent_file,
            intent,
            covered_paths[intent_file],
            set(covered_paths[intent_file]),
        )
        if error:
            return error

    # Atomic reservation: rename is the acquisition point. If another session
    # already consumed an intent between validation and here, acquisition
    # fails and this write is denied instead of riding the same one-shot
    # authorization. Deterministic (name) order keeps partial overlaps
    # fail-fast; acquired claims are rolled back on failure.
    claimed: list[tuple[Path, Path]] = []
    for intent_file in sorted(selected, key=lambda path: path.name):
        claim = intent_file.with_name(f"{intent_file.name}.claim-{uuid.uuid4().hex[:8]}")
        try:
            intent_file.rename(claim)
        except OSError:
            for original, taken in claimed:
                try:
                    taken.rename(original)
                except OSError:
                    pass
            return (
                "Stage promotion gate violation: a pending intent for these targets was just "
                "consumed by another session. Re-plant the intent if this write is still intended."
            )
        claimed.append((intent_file, claim))
    for _, claim in claimed:
        try:
            claim.unlink()
        except OSError:
            pass
    return ""


def intent_validation_blocker(
    stage_root: Path,
    workspace_root: Path,
    intent_file: Path,
    intent: dict[str, Any],
    target_paths: list[str],
    requested: set[str],
) -> str:
    """Validate one path-matching intent; consumes it and returns "" on success."""
    work_item_id = str(intent.get("work_item") or "").strip()
    if not work_item_id:
        return "Stage promotion gate violation: the promotion intent has no work_item."

    items = load_work_items(stage_root) + load_archive_work_items(stage_root)
    matched = [item for item in items if item.item_id == work_item_id or item.path.stem == work_item_id]
    if not matched:
        return f"Stage promotion gate violation: work_item `{work_item_id}` was not found."

    item = matched[0]
    intent_type = str(intent.get("type") or "promotion").strip().lower()
    if intent_type == "archive":
        if not all(path_targets_stage_archive(path) for path in target_paths):
            return "Stage archive gate violation: an archive intent may only target `.stage/past/work/archive/`."
        item_targets = [path for path in target_paths if archive_target_item_id(path, workspace_root)]
        retro_targets = [path for path in target_paths if archive_target_retro_id(path, workspace_root)]
        if len(item_targets) + len(retro_targets) != len(target_paths):
            return (
                "Stage archive gate violation: archive targets must be "
                "`items/<id>.md` or `retrospectives/<id>.md`."
            )
        item_ids = {archive_target_item_id(path, workspace_root) for path in item_targets}
        if item_targets and item_ids != {item.item_id}:
            return "Stage archive gate violation: the items/ target filename must match the work_item ID."
        ref_id = retrospective_ref_id(item)
        for path in retro_targets:
            if not ref_id or archive_target_retro_id(path, workspace_root) != ref_id:
                return (
                    "Stage archive gate violation: the retrospectives/ target filename must match "
                    "the work item's retrospective_ref."
                )
        if item.status not in {"completed", "rejected", "archived"}:
            return (
                f"Stage archive gate violation: work_item `{work_item_id}` status must be "
                f"completed/rejected. status `{item.status}`"
            )
        blockers = item_completion_blockers(item) if item_is_completed(item) else []
        if blockers:
            return (
                "Stage archive gate violation: close the completed item's verification, retrospective, "
                "and promotion decision first. " + " / ".join(blockers)
            )
        return ""

    blockers = item_completion_blockers(item)
    if blockers or not item_is_completed(item) or item.promotion not in {"approved", "promoted"}:
        detail = " / ".join(blockers) if blockers else f"{work_item_id}: status `{item.status}`"
        if item.promotion not in {"approved", "promoted"}:
            detail = f"{work_item_id}: promotion `{item.promotion}`"
        return "Stage promotion gate violation: the linked work item is not in a completed state. " + detail
    if not all(item_promotes_path(item, path, workspace_root) for path in target_paths):
        return "Stage promotion gate violation: the target paths do not match the work item's promotes list."

    return ""


# AskUserQuestion = Claude Code; request_user_input = Codex (core tool name).
QUESTION_TOOLS = {"AskUserQuestion", "request_user_input"}


def question_purpose_reminder(workspace_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Remind once per question to derive the answer from purpose and principles first.

    The ack marker is per session: another session's pending question must not
    consume this session's reminder (or vice versa).
    """
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return pre_tool_allow()
    marker = stage_root / ".runtime" / "question-ack" / session_slot(payload)
    if marker.exists():
        try:
            marker.unlink()
        except OSError:
            pass
        return pre_tool_allow()
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), encoding="utf-8")
    except OSError:
        return pre_tool_allow()
    return deny(
        "Stage question gate: before asking, re-read the work item's Purpose and "
        "`past/canon/principles.md`. If the answer follows from the purpose or a principle, "
        "decide and report in one line instead of asking. If the user's decision is genuinely "
        "required (value judgment, conflicting principles, irreversible impact), ask again — "
        "this reminder fires once per question."
    )


def frontmatter_field_from_text(text: str, field: str) -> str:
    # [ \t]* (not \s*): \s crosses the newline after an empty `field:` line and
    # would capture the NEXT line as the value (e.g. empty `parent:` followed by
    # `source:` read back as parent="source:" — a false hierarchy deny).
    match = re.search(rf"^{re.escape(field)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def read_existing_text(workspace_root: Path, relative: str) -> str:
    try:
        return (workspace_root / relative).read_text(encoding="utf-8")
    except OSError:
        return ""


def projected_file_text(existing: str, name: str, data: dict[str, Any]) -> str:
    """Best-effort post-edit file text for a Write/Edit/MultiEdit style tool call."""
    if name in {"Write", "create_file"}:
        content = data.get("content")
        return content if isinstance(content, str) else existing

    replacements: list[tuple[str, str]] = []
    edits = data.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                replacements.append(
                    (str(edit.get("old_string") or ""), str(edit.get("new_string") or ""))
                )
    for old_key, new_key in (("old_string", "new_string"), ("old_str", "new_str"), ("oldText", "newText")):
        new_value = data.get(new_key)
        if isinstance(new_value, str):
            old_value = data.get(old_key)
            replacements.append((old_value if isinstance(old_value, str) else "", new_value))

    text = existing
    for old, new in replacements:
        if old and old in text:
            text = text.replace(old, new)
        elif new:
            # Prepend immediately (fragment first so its field values win over stale
            # existing lines) so later edits apply sequentially to this fragment too.
            text = new + ("\n" + text if text else "")
    return text


def projected_patch_text(patch_text: str, target_relative: str, workspace_root: Path) -> str:
    """Best-effort post-patch file text for one file inside an apply_patch payload.

    A section counts toward the target when its File header matches, or when its
    `Move to:` destination matches — a moved file carries the source's existing text
    plus the section's hunks into the new path.
    """
    added: list[str] = []
    removed: set[str] = set()
    collecting = False
    base_relative = target_relative
    current_source = ""
    for line in patch_text.splitlines():
        if line.startswith("*** "):
            header = line[4:]
            matched_header = False
            for prefix in ("Add File: ", "Update File: ", "Delete File: "):
                if header.startswith(prefix):
                    raw_path = header[len(prefix):]
                    # Match the way the target was SELECTED (any form): a
                    # symlinked work-item leaf keeps its lexical `.stage/...`
                    # form while a plain resolve derefs outside — an equality on
                    # the resolved form alone would skip the hunks and hide a
                    # `parent:` change from the hierarchy gate.
                    collecting = target_relative in stage_relative_forms(raw_path, workspace_root)
                    current_source = (
                        target_relative
                        if collecting
                        else relative_to_workspace(raw_path, workspace_root)
                    )
                    if collecting:
                        base_relative = current_source
                    matched_header = True
                    break
            if not matched_header:
                if header.startswith("Move to: "):
                    raw_move = header[len("Move to: "):]
                    if (
                        target_relative in stage_relative_forms(raw_move, workspace_root)
                        and current_source
                    ):
                        collecting = True
                        base_relative = current_source
                elif header.strip() == "End Patch":
                    collecting = False
            continue
        if not collecting:
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.add(line[1:])
    existing = read_existing_text(workspace_root, base_relative)
    kept = [line for line in existing.splitlines() if line not in removed]
    return "\n".join(added + kept)


WORK_ITEMS_PREFIX = ".stage/present/work/items/"


def work_item_relative(raw: str, workspace_root: Path) -> str:
    """Work-item relative path if ANY form (resolved, entry, lexical) is under
    `present/work/items/` — a work-item file that is a symlink to outside
    (resolve derefs away) still counts, since `load_work_items` follows it."""
    for form in stage_relative_forms(raw, workspace_root):
        if form.startswith(WORK_ITEMS_PREFIX):
            return form
    return ""


def hierarchy_item_targets(workspace_root: Path, payload: dict[str, Any], name: str) -> list[tuple[str, str]]:
    """(relative_path, projected_post_edit_text) for every targeted work item file."""
    data = tool_input(payload)
    targets: list[tuple[str, str]] = []

    if name == "apply_patch":
        for text_value in iter_strings(data):
            for match in PATCH_FILE_RE.finditer(text_value):
                raw = match.group("path") or match.group("move") or ""
                relative = work_item_relative(raw, workspace_root)
                if relative:
                    targets.append(
                        (relative, projected_patch_text(text_value, relative, workspace_root))
                    )
        return targets

    target = ""
    for key in ("file_path", "path", "filePath"):
        value = data.get(key)
        if isinstance(value, str) and value:
            target = value
            break
    if not target:
        return []
    relative = work_item_relative(target, workspace_root)
    if not relative:
        return []
    existing = read_existing_text(workspace_root, relative)
    targets.append((relative, projected_file_text(existing, name, data)))
    return targets


def hierarchy_blocker(workspace_root: Path, payload: dict[str, Any], name: str) -> str:
    targets = hierarchy_item_targets(workspace_root, payload, name)
    if not targets:
        return ""

    stage_root = workspace_root / ".stage"
    items = load_work_items(stage_root) + load_archive_work_items(stage_root)

    # Post-state status per work-item ID: disk first, then this call's projected
    # edits overlaid — so a patch that finalizes a parent AND opens a child under
    # it in the same call is judged against the parent's FINAL status, not its
    # stale on-disk status.
    status_by_id: dict[str, str] = {}
    for item in items:
        status_by_id.setdefault(item.item_id, item.status)
    projected_id_by_stem: dict[str, str] = {}
    for relative, projected in targets:
        projected_id = frontmatter_field_from_text(projected, "id") or Path(relative).stem
        projected_id_by_stem[Path(relative).stem] = projected_id
        status_by_id[projected_id] = (
            frontmatter_field_from_text(projected, "status") or "active"
        ).lower()

    for relative, projected in targets:
        parent_id = frontmatter_field_from_text(projected, "parent")
        if not parent_id:
            continue

        target_stem = Path(relative).stem
        self_id = projected_id_by_stem.get(target_stem, target_stem)
        if parent_id in {target_stem, self_id}:
            return f"Stage hierarchy gate violation: a work item cannot be its own parent: {parent_id}"

        parent_status = status_by_id.get(parent_id)
        if parent_status is None:
            return f"Stage hierarchy gate violation: parent work item not found: {parent_id}"

        child_status = (frontmatter_field_from_text(projected, "status") or "active").lower()
        if parent_status in WORK_FINAL_STATUSES and child_status in WORK_OPEN_STATUSES:
            return (
                "Stage hierarchy gate violation: cannot open a child under a finalized parent "
                f"({parent_status}): {parent_id}"
            )
    return ""


def validate_pre_tool(payload: dict[str, Any]) -> dict[str, Any]:
    name = tool_name(payload)
    if name in QUESTION_TOOLS:
        return question_purpose_reminder(resolve_workspace_root(payload), payload)
    if name and name not in STAGE_MUTATION_TOOLS:
        return pre_tool_allow()

    # Shell semantics apply only to shell tools: on Codex, apply_patch carries
    # its PATCH BODY under tool_input.command, and parsing that as a shell
    # command extracted junk targets (diff lines, markdown links) and could
    # trip the delete/commit gates on mere content (live false deny, 2026-07-10).
    command = command_text(payload) if name in SHELL_TOOLS else ""
    explicit_paths = collect_explicit_paths(payload)
    shell_write_targets: list[str] = []
    if command:
        shell_write_targets = shell_write_paths(command)
        for path in shell_write_targets:
            if path and path not in explicit_paths:
                explicit_paths.append(path)
    if name == "apply_patch":
        for text_value in iter_strings(tool_input(payload)):
            for match in PATCH_FILE_RE.finditer(text_value):
                # Keep `..` (clean, not normalize) for symlink-safe resolve.
                cleaned = clean_path_text(match.group("path") or match.group("move") or "")
                if cleaned and cleaned not in explicit_paths:
                    explicit_paths.append(cleaned)
    workspace_root = resolve_workspace_root(payload)
    stage_root = workspace_root / ".stage"

    # An explicit `.stage` delete is always blocked; a strict-ancestor delete
    # (`rm -rf .`) is filtered inside command_deletes_stage to fire only when a
    # `.stage` exists, so a pre-init workspace is not over-denied.
    if command and command_deletes_stage(command, workspace_root):
        return deny(
            "Stage rule violation: deleting `.stage` entirely is blocked. "
            "Modify only the specific files you need so official artifacts, current work status, "
            "and plans are not lost."
        )

    # Classify each write target by the UNION of its forms (resolved, entry,
    # lexical — see stage_relative_forms). Union is fail-closed: the resolved
    # form catches symlink/`..` re-entry into `.stage`, the entry form catches
    # an aliased parent whose leaf is an outward symlink, the lexical form
    # catches a degenerate `.stage -> .` and an unlink/move of a symlink whose
    # leaf sits in `.stage/past` (where resolve would deref away).
    def targets_root(raw: str) -> bool:
        return any(
            path_targets_stage_root(form) for form in stage_relative_forms(raw, workspace_root)
        )

    def targets_past(raw: str) -> bool:
        return any(
            path_targets_stage_past(form) for form in stage_relative_forms(raw, workspace_root)
        )

    for raw in explicit_paths:
        # Per-form conjunction: the SAME form must be both stage-internal and
        # script-suffixed — `.stage/run.sh -> outside.txt` leaves an executable
        # `.sh` entry inside `.stage` even though its resolve ends `.txt`, while
        # a `.md` entry pointing at an outside `.sh` leaves none.
        if any(
            path_targets_stage_root(form) and form.lower().endswith(OS_SCRIPT_SUFFIXES)
            for form in stage_relative_forms(raw, workspace_root)
        ):
            return deny(
                "Stage portability rule violation: OS-specific executable scripts are not allowed "
                "inside `.stage`. Use the Python standard library or Markdown artifacts so behavior "
                "stays identical on Codex, Claude, Windows, Linux, and macOS."
            )

    past_gate_raw = explicit_paths if name in WRITE_TOOLS else shell_write_targets
    # The promotion gate consumes exact-entry authorizations, so hand it the
    # entry-canonical form (parents resolved, leaf kept as named).
    target_past_paths = [
        entry_relative_to_workspace(raw, workspace_root)
        for raw in past_gate_raw
        if targets_past(raw)
    ]
    if target_past_paths:
        blocker = promotion_blocker(workspace_root, target_past_paths)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and governance_broken(stage_root):
        write_targets = explicit_paths if name in WRITE_TOOLS else shell_write_targets
        external_targets = [
            path for path in write_targets if not is_stage_internal_path(path, workspace_root)
        ]
        if external_targets:
            return deny(
                "Stage governance violation: `.stage/settings.json` exists but is unreadable or "
                "malformed, so the governed scope cannot be trusted. Repair `.stage/settings.json` "
                "before modifying other files."
            )

    if stage_root.exists() and name in WRITE_TOOLS:
        blocker = hierarchy_blocker(workspace_root, payload, name)
        if blocker:
            return deny(blocker)
        # Write/Edit/MultiEdit are CONTENT writes — they follow a symlink target
        # and modify the dereferenced file (not the entry). apply_patch mixes
        # add/update/delete, so it stays entry-based (best-effort).
        follows = name in {"Write", "Edit", "MultiEdit"}
        blocker = source_registration_blocker(workspace_root, explicit_paths, follows)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command:
        blocker = source_registration_blocker(workspace_root, shell_write_targets)
        if blocker:
            return deny(blocker)

    if stage_root.exists() and name in SHELL_TOOLS and command and command_has_git_commit(command):
        files = staged_files(workspace_root)
        files.extend(path for path in git_add_paths_from_command(command, workspace_root) if path not in files)
        files.extend(path for path in git_commit_pathspec_files(command, workspace_root) if path not in files)
        if git_commit_all_requested(command):
            files.extend(path for path in changed_files(workspace_root) if path not in files)
        blocker = commit_blocker(workspace_root, files)
        if blocker:
            return deny(blocker)

    return pre_tool_allow()


def read_if_exists(path: Path, limit: int = 1400) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def session_context(workspace_root: Path) -> str:
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        # The stage-init session itself must still see host instructions.
        return (
            "## Stage\n"
            "This project has no `.stage/`. If the Stage harness applies to this project, "
            "create the artifact structure first with `stage-init`."
            + consumer_context_section(workspace_root, pre_init=True)
        )

    parts = [
        "## Stage context",
        "- Global time axis: `past` is official, `present` is in progress, `future` is planned.",
        "- Space axis: `canon`, `model`, `decisions`, `work`, `state`, `operations` divide responsibility.",
        "- Core principles (full catalog: `past/canon/principles.md`):",
        "  SSOT — one owning location per durable fact. MECE — no overlap, no known gaps.",
        "  Fail Fast — surface wrong premises early. AHA — no abstraction before repetition.",
        "  Completion — external view + internal view + retrospective, all three.",
        "  Honesty — never assert unverified facts; no partial completion, no silent substitution.",
        "- Cite the governing principles in every decision record and retrospective.",
        "- Register an active work item in `.stage/present/work/items/` before modifying governed files "
        "(nearly all files are governed by default; see `.stage/settings.json`).",
        "- Modifying `past` requires a pending intent (`scripts/promote_intent.py`) and a completed work item.",
        "- Artifact map — W work `present/work/items` · R retro `present/work/retrospectives` · "
        "DE decision `present/work/decisions` · D approved `past/decisions/records` · "
        "O/Q/A/K state `present/state/*` · B backlog `future/backlog/items` · P proposal · M milestone. "
        "Full catalog: `operations/artifacts.md`; routing: `index.md`.",
    ]

    snippets: list[tuple[str, Path | None]] = [
        ("Current state", stage_root / "present" / "state" / "current.md"),
        ("Active work", stage_root / "present" / "work" / "active.md"),
        ("Review candidates", stage_root / "present" / "work" / "review.md"),
    ]
    for title, path in snippets:
        body = read_if_exists(path) if path is not None else ""
        if body:
            parts.append(f"\n### {title}\n{body}")

    consumer_section = consumer_context_section(workspace_root)
    if consumer_section:
        parts.append(consumer_section)

    questions = open_question_lines(stage_root)
    if questions:
        parts.append("\n### Open questions\n" + "\n".join(questions))
    backlog = selected_backlog_lines(stage_root)
    if backlog:
        parts.append("\n### Selected backlog\n" + "\n".join(backlog))

    recent_bodies = [
        body
        for body in (read_if_exists(path) for path in latest_session_summaries(stage_root))
        if body
    ]
    if recent_bodies:
        heading = "Most recent session" if len(recent_bodies) == 1 else "Most recent sessions (concurrent)"
        parts.append(f"\n### {heading}\n" + "\n\n".join(recent_bodies))

    return "\n".join(parts)


# Host-project instruction sources, relative to the workspace root. Stage
# works without any of them; when present they are project norms the session
# must actively use (and challenge when wrong) rather than ignore.
CONSUMER_CONTEXT_FILES: tuple[str, ...] = (
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
)
CONSUMER_CONTEXT_DIRS: tuple[str, ...] = (
    ".claude/rules",
    ".claude/skills",
    ".agents/skills",
)
CONSUMER_CONTEXT_MAX_LINES = 10


def agents_instruction_file(directory: Path) -> str | None:
    """Codex reads AGENTS.override.md INSTEAD of AGENTS.md when both exist —
    listing both would mark an intentional override as a contradiction."""
    for name in ("AGENTS.override.md", "AGENTS.md"):
        if (directory / name).is_file():
            return name
    return None


def directory_instruction_lines(directory: Path, prefix: str = "") -> list[str]:
    """Instruction sources of one directory — the same list applies to the
    workspace root and to each monorepo package one level down."""
    lines: list[str] = []
    for relative in CONSUMER_CONTEXT_FILES:
        if (directory / relative).is_file():
            lines.append(f"- `{prefix}{relative}`")
    agents_name = agents_instruction_file(directory)
    if agents_name:
        lines.append(f"- `{prefix}{agents_name}`")
    for relative in CONSUMER_CONTEXT_DIRS:
        candidate = directory / relative
        try:
            count = sum(1 for entry in candidate.iterdir() if not entry.name.startswith("."))
        except OSError:
            continue
        if count:
            lines.append(f"- `{prefix}{relative}/` ({count} entries)")
    return lines


# Dependency/build trees are not project-owned: a third-party package must not
# be able to inject "host instructions" into the session.
UNOWNED_DIR_NAMES = {
    "node_modules",
    "vendor",
    "third_party",
    "external",
    "dist",
    "build",
    "target",
    "venv",
}


def child_directories(directory: Path, workspace_root: Path) -> list[Path]:
    try:
        resolved_root = workspace_root.resolve()
    except OSError:
        resolved_root = workspace_root
    children: list[Path] = []
    try:
        entries = sorted(directory.iterdir())
    except OSError:
        return []
    for entry in entries:
        if entry.name.startswith(".") or entry.name in UNOWNED_DIR_NAMES:
            continue
        try:
            if not entry.is_dir():
                continue
            # A symlink escaping the workspace is not project-owned either.
            if not entry.resolve().is_relative_to(resolved_root):
                continue
        except OSError:
            continue
        children.append(entry)
    return children


def active_scope_paths(stage_root: Path) -> set[str]:
    """Full scoped subtree paths of the packages current or next work touches,
    from open work items' `scope`. Full paths (not just the first segment) so a
    two-level scope like `packages/zapp` prioritizes that exact subtree's
    instructions over its 10 alphabetical siblings under `packages/` (P35). A
    selected backlog item's relevant scope is its realizing work item's scope,
    already open here — backlog records carry no scope of their own."""
    scopes: set[str] = set()
    try:
        items = load_work_items(stage_root)
    except OSError:
        return scopes
    for item in items:
        if item.status not in WORK_OPEN_STATUSES:
            continue
        for scope in item.scope:
            normalized = normalize_path_text(scope).strip("/")
            if normalized and normalized != "*":
                scopes.add(normalized)
    return scopes


def _instruction_source_dir(line: str) -> str:
    """The owning package directory of an inventory line like
    ``- `pkg/.claude/CLAUDE.md` ``. Metadata containers (`.claude`, `.agents`,
    `.github`) are stripped so the source attributes to the package (`pkg`),
    which is what a work-item scope names."""
    inner = line.split("`", 2)
    if len(inner) < 2:
        return ""
    ref = inner[1].rstrip("/")
    ref = ref.rsplit("/", 1)[0] if "/" in ref else ""
    segments = ref.split("/") if ref else []
    trimmed: list[str] = []
    for segment in segments:
        if segment in {".claude", ".agents", ".github"}:
            break
        trimmed.append(segment)
    return "/".join(trimmed)


def _scope_prioritized(source_dir: str, scopes: set[str]) -> bool:
    """A source is prioritized if its directory and a scope path are on the same
    branch (one is a prefix of the other)."""
    for scope in scopes:
        if source_dir == scope or source_dir.startswith(scope + "/") or scope.startswith(source_dir + "/"):
            return True
    return False


def consumer_context_lines(
    workspace_root: Path,
    limit: int = CONSUMER_CONTEXT_MAX_LINES,
    stage_root: Path | None = None,
) -> list[str]:
    root_lines = directory_instruction_lines(workspace_root)

    # Monorepo packages carry their own subtree-scoped instructions; container
    # layouts (packages/foo, apps/web) put them two levels down. Discovery is
    # bounded to depth 2 and the total line cap below.
    package_lines: list[str] = []
    for child in child_directories(workspace_root, workspace_root):
        package_lines.extend(directory_instruction_lines(child, prefix=f"{child.name}/"))
        for grandchild in child_directories(child, workspace_root):
            package_lines.extend(
                directory_instruction_lines(
                    grandchild, prefix=f"{child.name}/{grandchild.name}/"
                )
            )

    # Sources on the branch of an active work item's scope come first so the cap
    # never drops the guide governing the work at hand — full-path, not first
    # segment, so `packages/zapp` beats `packages/a00…`.
    scopes = active_scope_paths(stage_root) if stage_root else set()
    package_lines.sort(
        key=lambda line: (not _scope_prioritized(_instruction_source_dir(line), scopes),)
    )
    lines = root_lines + package_lines

    if len(lines) > limit:
        overflow = len(lines) - limit
        lines = lines[:limit] + [f"- …and {overflow} more instruction sources"]
    return lines


CONSUMER_CONTEXT_DIRECTIVE = (
    "- Consult these when planning and executing — they are project norms, "
    "not optional reading. Root-level sources bind everywhere; a source inside "
    "a package directory binds work under that subtree only; within a source, "
    "honor its own applicability (a path-scoped rule or a trigger-scoped skill "
    "applies only per its own declaration). If an applicable "
    "instruction contradicts observed reality or Stage truth, do not silently "
    "deviate or silently obey: register the conflict as an open question "
    "(`present/state/questions/`) with your proposed correction and ask the "
    "user to fix the instruction."
)

# Before stage-init there is no question family to write into.
CONSUMER_CONTEXT_DIRECTIVE_PRE_INIT = (
    "- Consult these when planning and executing — they are project norms, "
    "not optional reading. Root-level sources bind everywhere; a source inside "
    "a package directory binds work under that subtree only; within a source, "
    "honor its own applicability (a path-scoped rule or a trigger-scoped skill "
    "applies only per its own declaration). If an applicable "
    "instruction contradicts observed reality, raise it with the user directly "
    "(Stage question records become available after `stage-init`)."
)


def consumer_context_section(workspace_root: Path, pre_init: bool = False) -> str:
    stage_root = None if pre_init else workspace_root / ".stage"
    consumer = consumer_context_lines(workspace_root, stage_root=stage_root)
    if not consumer:
        return ""
    directive = CONSUMER_CONTEXT_DIRECTIVE_PRE_INIT if pre_init else CONSUMER_CONTEXT_DIRECTIVE
    return (
        "\n### Project instructions (host-defined)\n"
        + "\n".join(consumer)
        + "\n"
        + directive
    )


SESSION_CONTEXT_RECORD_LIMIT = 3
SESSION_CONTEXT_LINE_LIMIT = 160


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
    """Individual record files of an artifact family (skips index/template files)."""
    try:
        files = sorted(directory.glob("*.md"))
    except OSError:
        return []
    return [
        path
        for path in files
        if not path.name.startswith("_") and path.name.lower() != "readme.md"
    ]


def open_question_lines(stage_root: Path, limit: int = SESSION_CONTEXT_RECORD_LIMIT) -> list[str]:
    """Every record under `present/state/questions/` is open by definition —
    answered questions are promoted out of the directory. Newest first."""
    records: list[tuple[str, str, str]] = []
    for path in record_files(stage_root / "present" / "state" / "questions"):
        fields = parse_frontmatter(path)
        records.append(
            (
                fields.get("id") or path.stem,
                fields.get("title") or "",
                fields.get("work_items") or "",
            )
        )
    # Sort by the frontmatter ID (filenames may diverge from it), numerically.
    records.sort(key=lambda entry: id_sort_key(entry[0]), reverse=True)
    lines: list[str] = []
    for item_id, title, blocked in records[:limit]:
        suffix = f" (blocks: {blocked})" if blocked else ""
        lines.append(bounded_record_line(item_id, title, suffix))
    if len(records) > limit:
        lines.append(f"- …and {len(records) - limit} more in `present/state/questions/`")
    return lines


def selected_backlog_lines(stage_root: Path, limit: int = SESSION_CONTEXT_RECORD_LIMIT) -> list[str]:
    """Backlog records with `status: selected` — the queue the session should
    pick up next. Ordered by ID for determinism."""
    lines: list[str] = []
    selected: list[tuple[str, str, str]] = []
    for path in record_files(stage_root / "future" / "backlog" / "items"):
        fields = parse_frontmatter(path)
        if (fields.get("status") or "").lower() != "selected":
            continue
        item_id = fields.get("id") or path.stem
        selected.append((item_id, fields.get("title") or "", fields.get("priority") or ""))
    selected.sort(key=lambda entry: id_sort_key(entry[0]))
    for item_id, title, priority in selected[:limit]:
        suffix = f" (priority: {priority})" if priority else ""
        lines.append(bounded_record_line(item_id, title, suffix))
    if len(selected) > limit:
        lines.append(f"- …and {len(selected) - limit} more in `future/backlog/items/`")
    return lines


QUESTION_ACK_MAX_AGE_SECONDS = 24 * 60 * 60


def prune_question_ack_markers(stage_root: Path) -> None:
    """Ack markers live seconds (deny → re-ask); anything older is an abandoned session's."""
    root = stage_root / ".runtime" / "question-ack"
    now = datetime.now(timezone.utc).timestamp()
    try:
        markers = list(root.iterdir())
    except OSError:
        return
    for marker in markers:
        try:
            if now - marker.stat().st_mtime > QUESTION_ACK_MAX_AGE_SECONDS:
                marker.unlink()
        except OSError:
            pass


def handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    workspace_root = resolve_workspace_root(payload)
    prune_question_ack_markers(workspace_root / ".stage")
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": session_context(workspace_root),
        }
    }


def summarize_stage(stage_root: Path) -> str:
    items = load_work_items(stage_root)
    open_items = [item.item_id for item in items if item_is_open(item)]
    blockers = stage_completion_blockers(stage_root.parent)
    open_text = ", ".join(open_items) if open_items else "none"
    blocker_text = " / ".join(blockers) if blockers else "none"
    return (
        "# Stage Session Summary\n"
        f"- End time: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- Open work: {open_text}\n"
        f"- Completion blockers: {blocker_text}\n"
        "- Handoff condition: open work items carry current status and next actions\n"
    )


SESSION_SUMMARY_KEEP = 5


def sessions_root(stage_root: Path) -> Path:
    return stage_root / ".runtime" / "sessions"


def summaries_by_recency(stage_root: Path) -> list[Path]:
    """Session summaries newest-first; per-file stat so a concurrently pruned file is skipped."""
    stamped: list[tuple[float, Path]] = []
    try:
        candidates = list(sessions_root(stage_root).glob("*.md"))
    except OSError:
        return []
    for path in candidates:
        try:
            stamped.append((path.stat().st_mtime, path))
        except OSError:
            continue
    # Filename is a deterministic tiebreaker so coarse-resolution mtime ties
    # give a stable order instead of an arbitrary one.
    stamped.sort(key=lambda entry: (entry[0], entry[1].name), reverse=True)
    return [path for _, path in stamped]


def latest_session_summary(stage_root: Path) -> Path | None:
    migrate_legacy_runtime(stage_root)
    files = summaries_by_recency(stage_root)
    return files[0] if files else None


def latest_session_summaries(stage_root: Path) -> list[Path]:
    """The newest handoff plus any others sharing its mtime — on a coarse-
    resolution filesystem two sessions can Stop in the same tick, and injecting
    only one would silently drop a concurrent session's handoff (P30)."""
    migrate_legacy_runtime(stage_root)
    files = summaries_by_recency(stage_root)
    if not files:
        return []
    try:
        newest_mtime = files[0].stat().st_mtime
    except OSError:
        return files[:1]
    tied: list[Path] = []
    for path in files:
        try:
            if path.stat().st_mtime == newest_mtime:
                tied.append(path)
            else:
                break
        except OSError:
            continue
    return tied or files[:1]


SUMMARY_MIN_PRUNE_AGE_SECONDS = 24 * 60 * 60


def prune_session_summaries(
    stage_root: Path, keep: int = SESSION_SUMMARY_KEEP, keep_path: Path | None = None
) -> None:
    # keep_path pins the summary this Stop just wrote — mtime ties and
    # another host's clock running ahead must neither delete it nor let the
    # retained set exceed the cap, so the retained set is derived first and
    # keep_path swapped in for the oldest retained entry when necessary.
    # Additionally, a file younger than a day (by this host's clock) is never
    # pruned: under clock skew another session's just-written handoff can sort
    # below older files, and deleting it would lose a live session's handoff.
    # The cap is therefore soft for at most a day under skew.
    files = summaries_by_recency(stage_root)
    retained = files[:keep]
    if keep_path is not None and keep_path in files and keep_path not in retained:
        retained = retained[: keep - 1] + [keep_path]
    retained_set = set(retained)
    now = datetime.now(timezone.utc).timestamp()
    for stale in files:
        if stale in retained_set:
            continue
        try:
            if now - stale.stat().st_mtime < SUMMARY_MIN_PRUNE_AGE_SECONDS:
                continue
            stale.unlink()
        except OSError:
            pass


def handle_stop(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("stop_hook_active"):
        return continue_output()

    workspace_root = resolve_workspace_root(payload)
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return continue_output()

    # One summary per session so concurrent Claude/Codex sessions keep their
    # own handoff instead of last-write-wins on a single slot.
    migrate_legacy_runtime(stage_root)
    summary_path = sessions_root(stage_root) / f"{session_slot(payload)}.md"
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summarize_stage(stage_root), encoding="utf-8")
    except OSError as exc:
        return continue_output(f"Stage session summary write failed: {exc}")

    prune_session_summaries(stage_root, keep_path=summary_path)
    return continue_output(
        f"Stage session summary saved: .stage/.runtime/sessions/{summary_path.name}"
    )


def handle_event(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_event(event, payload)
    if normalized in {"session-start", "sessionstart"}:
        return handle_session_start(payload)
    if normalized in {"pre-tool-use", "pretooluse"}:
        return validate_pre_tool(payload)
    if normalized == "stop":
        return handle_stop(payload)
    return continue_output()


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    args = list(sys.argv[1:] if argv is None else argv)
    event = args[0] if args else None
    payload = load_payload()
    output = handle_event(event or "", payload)
    # Empty output means "proceed": both hosts accept it, and Codex rejects
    # explicit allow/approve decisions as unsupported.
    if output:
        print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
