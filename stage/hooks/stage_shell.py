# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import os
import re
import shlex
import sys
from pathlib import Path

# Sibling modules load by bare name; make the hooks dir importable whether this
# module is reached through stage_guard (already bootstrapped) or imported on
# its own by name or file path.
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import (  # noqa: E402  (after sys.path bootstrap)
    clean_path_text,
    normalize_path_text,
    stage_real_root,
)


# find options legal BEFORE the start paths (GNU `-H/-L/-P/-O/-D`, BSD adds
# `-E/-X/-x/-s/-d/-f`). Argument-consuming ones (`-D`, `-f`) are handled at the
# scan site. BSD clusters the argument-less ones into one token (`-Lx`, `-dsx`)
# — FIND_PRE_PATH_CLUSTER_RE matches any such cluster.
FIND_PRE_PATH_FLAGS = {"-H", "-L", "-P", "-E", "-X", "-x", "-s", "-d"}
FIND_PRE_PATH_CLUSTER_RE = re.compile(r"-[HLPEXdsx]+")
REDIRECT_RE = re.compile(r"(?:^|[\s])(?:>>|[0-9]?>)\s*(?P<path>[^&|;\s]+)")
SHELL_SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}


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
