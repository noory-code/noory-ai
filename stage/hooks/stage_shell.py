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
SHELL_SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}
INLINE_INTERPRETERS = {
    "python",
    "python2",
    "python3",
    "node",
    "nodejs",
    "deno",
    "bun",
    "ruby",
    "perl",
    "sh",
    "bash",
    "zsh",
}
INLINE_E_INTERPRETERS = {"node", "nodejs", "ruby", "perl"}
INTERPRETER_VERSION_SUFFIX_RE = re.compile(r"(?:\d+(?:\.\d+)*|\.\d+(?:\.\d+)*)")
# normalize_shell_control masks quoted `<` and leaves arithmetic shifts inside
# `$((...))` embedded in non-command tokens. A real heredoc redirect is either
# a redirection token (optionally fd-prefixed) or attached to a command word.
HEREDOC_TOKEN_RE = re.compile(r"^(?:\d*|[^$()=<> \t]+)<<-?(?!<)")


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
_SENTINELS = {";": "", "&": "", "|": "", "<": "", ">": ""}
# Double-quoted `<`/`>` mask differently: text in double quotes can still
# EXECUTE via command substitution, so the substitution scan restores these
# (soft) while single-quoted/escaped ones (hard, above) stay data.
_SENTINELS_DQ = {";": "", "&": "", "|": "", "<": "", ">": ""}
_SOFT_REDIRECT_REVERSE = {0xE005: "<", 0xE006: ">"}
_SENTINEL_REVERSE = {ord(v): k for k, v in _SENTINELS.items()}
_SENTINEL_REVERSE.update({ord(v): k for k, v in _SENTINELS_DQ.items()})


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
            quote_map = _SENTINELS_DQ if quote == '"' else _SENTINELS
            out.append(quote_map.get(char, char) if char in quote_map else char)
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


def _walk_cd(anchor: Path, target: str, created: set[Path] | None = None) -> Path | None:
    """LOGICAL directory after `cd <target>` from `anchor`, or None when the
    real shell's cd would FAIL. Bash `cd -L` (the default) applies `..` to the
    logical path — `cd link ; cd ..` (link -> build/deep) returns to link's
    logical parent, not the physical one — so `..` pops a segment lexically and
    symlinks stay UNRESOLVED in the returned path. Each visited prefix must be a
    traversable directory (existence + execute permission), so
    `cd build/missing/..` and a permission-denied `cd` both fail. A prefix in
    `created` (an earlier `mkdir` in the same command) counts as traversable —
    it will exist by the time the cd runs. Write classification resolves this
    logical path later (relative_to_workspace)."""
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
        if not _is_traversable_dir(cursor) and (created is None or cursor not in created):
            return None
    return cursor


REDIRECT_OPERATOR_RE = re.compile(r"^(?:\d*(?:>>?|<)|[&]>>?|>[&]|<<<?)$")
REDIRECT_ATTACHED_RE = re.compile(r"^(?:\d*(?:>>?|<)|[&]>>?)")
# The fd-redirect `&` (`&>`, `2>&1`) arrives as its SENTINEL (normalization
# marks it so it is not a background separator), while a QUOTED `>`/`<` is a
# different sentinel that stays data — so the redirect patterns accept the
# `&` sentinel before a LITERAL `>` and nothing else.
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


REDIRECT_INFIX_RE = re.compile(r"\d*(?:>>?|<)|[&]>>?")


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
        # Directories an earlier `mkdir` in the same command will create —
        # they do not exist at hook time but a following cd into them succeeds.
        self.created: set[Path] = set()

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
            dest = _walk_cd(anchor, operand, self.created)
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


def _command_groups(
    command: str, workspace_root: Path | None = None
) -> list[tuple[list[Path], str, list[str]]]:
    """(possible-cwd anchors, command name, restored tokens) per simple
    command, with cd/pushd/popd groups consumed into the anchor tracking.

    Relative operands are anchored where the shell IS: a preceding `cd` group
    rebases them (`cd build && find . -delete` traverses build, not the
    workspace). Control flow is not evaluated, so the tracker keeps a SET of
    possible cwds: a cd whose own execution is conditional (preceded by
    `&&`/`||`/`|`, e.g. `false && cd build ; rm -rf .stage`) ADDS the rebased
    state alongside the previous ones; a definite cd (first group or after
    `;`/newline) replaces them. Consumers must treat a hit from ANY possible
    anchor as a hit — fail closed."""
    anchors: list[Path] = []
    if workspace_root is not None:
        try:
            anchors = [workspace_root.resolve()]
        except (OSError, RuntimeError):
            anchors = [workspace_root]
    tracker = _CwdTracker(anchors)

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

    groups: list[tuple[list[Path], str, list[str]]] = []
    for index, (separator, raw_group) in enumerate(entries):
        if not raw_group:
            continue
        # Groups carry their SENTINELS: a quoted/escaped operator must stay
        # distinguishable from a real one until each consumer has classified
        # redirects; consumers restore per token. Names classify on a
        # restored copy. Peel leading builtin-capable wrappers
        # (`command cd x`) so the real command is classified, and map
        # PowerShell cwd verbs to POSIX.
        group = list(raw_group)
        head = 0
        while head < len(group) - 1 and Path(_restore_sentinels(group[head])).name.lower() in COMMAND_WRAPPERS:
            head += 1
        group = group[head:]
        head_name = Path(_restore_sentinels(group[0])).name.lower()
        name = POWERSHELL_CWD.get(head_name, head_name)
        # cwd-changing groups are consumed into the tracker but still yielded
        # (with their PRE-change anchors): a redirect on the cd itself
        # (`cd build > log`) writes where the shell was.
        if name in {"mkdir", "md"} and workspace_root is not None:
            # A later cd may enter a directory this very command creates
            # (`mkdir scratch && cd scratch && …`) — record every prefix the
            # mkdir would materialize so the tracker can follow. Extra
            # candidates only ADD possible anchors (fail closed).
            for token in [_restore_sentinels(t) for t in _strip_redirections(list(group[1:]))]:
                if token == "--" or token.startswith("-"):
                    continue
                text = clean_path_text(token)
                if not text:
                    continue
                try:
                    base = Path(text).expanduser()
                except RuntimeError:
                    base = Path(text)
                starts = (
                    [Path(base.anchor)] if base.is_absolute() else list(tracker.anchors)
                )
                segments = base.parts[1:] if base.is_absolute() else base.parts
                for start in starts:
                    cursor = start
                    for segment in segments:
                        if segment == ".":
                            continue
                        cursor = cursor.parent if segment == ".." else cursor / segment
                        tracker.created.add(cursor)
        if name in {"cd", "pushd", "popd"} and workspace_root is not None:
            groups.append((list(tracker.anchors), name, group))
            positional = [_restore_sentinels(t) for t in _strip_redirections(list(group[1:]))]
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
        groups.append((list(tracker.anchors), name, group))
    return groups


def _interpreter_family(command_word: str) -> str | None:
    """Explicit interpreter family for a case-sensitive command basename.

    Version suffixes are accepted so names such as `python3.11` count without
    broad prefix matching that would misclassify unrelated commands such as
    `python-config` or `shred`.
    """
    basename = Path(command_word).name
    for name in sorted(INLINE_INTERPRETERS, key=len, reverse=True):
        if basename == name:
            return name
        if basename.startswith(name) and INTERPRETER_VERSION_SUFFIX_RE.fullmatch(
            basename[len(name) :]
        ):
            return name
    return None


def _has_inline_option(family: str, arguments: list[str]) -> bool:
    """Whether interpreter options select inline code before a script/module."""
    for argument in arguments:
        if argument == "--":
            return False
        if argument == "-m":
            return False
        if argument == "-c" and family in INLINE_INTERPRETERS:
            return True
        if argument == "-e" and family in INLINE_E_INTERPRETERS:
            return True
    return False


def interpreter_inline_stage_write(command: str) -> bool:
    """Whether opaque inline interpreter code may act on the Stage tree.

    The `.stage` check deliberately scans the unmodified command, including
    heredoc bodies, so computed paths such as `Path('.stage') / relative` are
    visible. Interpreter bodies remain opaque: `-c`, supported `-e`, or a
    structural heredoc on the interpreter's own command group therefore fail
    closed, while named scripts and `-m` module invocations remain inspectable
    command forms.
    """
    if ".stage" not in command:
        return False

    for _anchors, _name, raw_group in _command_groups(command):
        group_has_heredoc = any(HEREDOC_TOKEN_RE.match(token) for token in raw_group)
        group = [_restore_sentinels(token) for token in raw_group]
        if not group:
            continue
        command_word = group[0]
        heredoc_match = HEREDOC_TOKEN_RE.match(command_word)
        if heredoc_match and heredoc_match.end() < len(command_word):
            command_word = command_word[: command_word.find("<<")]
        family = _interpreter_family(command_word)
        if family is None:
            continue
        if group_has_heredoc or _has_inline_option(family, group[1:]):
            return True
    return False


def command_deletes_stage(command: str, workspace_root: Path | None = None) -> bool:
    """Whether a shell command recursively removes the whole `.stage` tree.

    Tokenized (not a free-text regex) so recursive flags in any spelling are
    caught: `rm -r/-R/-rf/--recursive`, PowerShell `Remove-Item -Recurse`,
    Windows `rmdir /s`, and `find <.stage> -delete`/`-exec|-execdir rm`.
    Operands are resolved through symlinks when workspace_root is given.
    Non-recursive `rm .stage` cannot remove a directory, so it is not blocked.
    Classification denies if ANY possible cwd anchor removes the Stage tree
    (see _command_groups) — fail closed.
    """

    def hits_stage(arg: str, anchors: list[Path]) -> bool:
        if not anchors:
            return _targets_stage_root(arg, workspace_root)
        return any(
            _targets_stage_root(arg, workspace_root, base_dir=anchor)
            for anchor in anchors
        )

    for anchors, name, raw_group in _command_groups(command, workspace_root):
        group = [_restore_sentinels(tok) for tok in raw_group]
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
            if recursive and any(hits_stage(arg, anchors) for arg in args):
                return True
        elif name == "rmdir":
            if any(flag.lower() in {"/s", "-s", "--recursive"} for flag in flags) and any(
                hits_stage(arg, anchors) for arg in args
            ):
                return True
        elif name in {"remove-item", "ri", "rd", "del", "erase"}:
            recursive = any(flag.lower() in {"-recurse", "-r", "/s"} for flag in flags)
            force = any(flag.lower() in {"-force", "-f"} for flag in flags)
            if (recursive or force) and any(hits_stage(arg, anchors) for arg in group[1:]):
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
                if not anchors:
                    return _targets_stage_root(arg, workspace_root, follow_symlinks=follows)
                return any(
                    _targets_stage_root(
                        arg, workspace_root, follow_symlinks=follows, base_dir=anchor
                    )
                    for anchor in anchors
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


OUT_REDIRECT_BARE_RE = re.compile(r"^(?:\d*>>?|[&]>>?)$")
OUT_REDIRECT_ATTACHED_RE = re.compile(r"^(?:\d*>>?|[&]>>?)(?P<path>.+)$")


# A redirect INSIDE a command substitution executes when the substitution
# runs — scan a substitution-bearing token's text for output redirects.
SUBSTITUTION_REDIRECT_RE = re.compile(r"(?:^|[\s(])(?:\d*>>?|&>>?)\s*(?P<path>[^&|;\s)]+)")


def _output_redirect_targets(raw_group: list[str]) -> list[str]:
    """OUTPUT-redirect targets among one command group's SENTINEL-carrying
    tokens: a bare operator (`>`, `>>`, `2>`, `&>`) takes the following token;
    an attached form (`>/dev/null`, `2>>log`) carries its own. A quoted or
    escaped `>` is a sentinel here, so it is data, not a redirect; fd
    duplications (`2>&1`) are not file writes. A token carrying a command
    substitution is additionally text-scanned — its inner redirect executes
    with the substitution. Returned targets are sentinel-restored."""
    targets: list[str] = []

    def add(raw: str) -> None:
        restored = _restore_sentinels(raw)
        if restored and not restored.startswith("&"):
            targets.append(restored)

    skip_next = False
    for index, token in enumerate(raw_group):
        if skip_next:
            skip_next = False
            continue
        if OUT_REDIRECT_BARE_RE.match(token):
            if index + 1 < len(raw_group):
                add(raw_group[index + 1])
            skip_next = True
            continue
        match = OUT_REDIRECT_ATTACHED_RE.match(token)
        if match:
            add(match.group("path"))
        if "$(" in token or "`" in token:
            for inner in SUBSTITUTION_REDIRECT_RE.finditer(
                token.translate(_SOFT_REDIRECT_REVERSE)
            ):
                candidate = _restore_sentinels(inner.group("path"))
                if not candidate.startswith("&"):
                    targets.append(candidate)
    return targets


def _positional_operands(tokens: list[str]) -> list[str]:
    """Non-flag operands with `--` ending option parsing."""
    operands: list[str] = []
    after_ddash = False
    for token in tokens:
        if after_ddash:
            operands.append(token)
        elif token == "--":
            after_ddash = True
        elif token.startswith("-"):
            continue
        else:
            operands.append(token)
    return operands


def shell_write_paths(command: str, workspace_root: Path | None = None) -> list[str]:
    """Write targets of a shell command — output-redirect targets plus cp/mv
    destinations, tee targets, and sed -i files — rebased at every possible
    effective cwd (fail closed; see _command_groups). Unexpanded globs and
    variables pass through as literals (best-effort, README §Limits)."""
    paths: list[str] = []

    def add(raw: str, anchors: list[Path]) -> None:
        # Keep `..` intact (see collect_explicit_paths) for symlink-safe resolve.
        text = clean_path_text(raw)
        if not text:
            return
        try:
            absolute = Path(text).expanduser().is_absolute()
        except (RuntimeError, ValueError):
            absolute = False
        candidates = [text] if absolute or not anchors else [
            str(anchor / text) for anchor in anchors
        ]
        for candidate in candidates:
            if candidate not in paths:
                paths.append(candidate)

    for anchors, name, raw_group in _command_groups(command, workspace_root):
        for target in _output_redirect_targets(raw_group):
            add(target, anchors)
        positional = [_restore_sentinels(t) for t in _strip_redirections(list(raw_group[1:]))]
        operands = _positional_operands(positional)
        if name in {"cp", "mv"} and len(operands) >= 2:
            add(operands[-1], anchors)
        elif name == "tee":
            for operand in operands:
                add(operand, anchors)
        elif name == "sed":
            in_place = any(
                token == "-i" or (token.startswith("-i") and token != "-i")
                for token in positional
                if token.startswith("-")
            )
            if in_place and operands:
                add(operands[-1], anchors)

    return paths


DELETE_COMMANDS = {"rm", "del", "erase", "remove-item", "ri"}


def shell_delete_paths(command: str, workspace_root: Path) -> list[str]:
    """Path operands of file-delete commands, rebased at every possible
    effective cwd (fail closed — any anchor's classification may deny).

    Deleting a governed file is a governed modification, so these operands go
    through the same write-gate pipeline as redirect/cp/mv/tee targets. Flags
    are skipped, `--` ends option parsing, redirections are stripped, and
    unexpanded globs/variables pass through as literals (best-effort, see
    hooks/README.md §Limits)."""
    paths: list[str] = []
    for anchors, name, raw_group in _command_groups(command, workspace_root):
        if name not in DELETE_COMMANDS:
            continue
        operands: list[str] = []
        after_ddash = False
        for token in [_restore_sentinels(t) for t in _strip_redirections(list(raw_group[1:]))]:
            if after_ddash:
                operands.append(token)
            elif token == "--":
                after_ddash = True
            elif token.startswith("-"):
                continue
            else:
                operands.append(token)
        for operand in operands:
            text = clean_path_text(operand)
            if not text:
                continue
            try:
                absolute = Path(text).expanduser().is_absolute()
            except (RuntimeError, ValueError):
                absolute = False
            candidates = [text] if absolute or not anchors else [
                str(anchor / text) for anchor in anchors
            ]
            for candidate in candidates:
                if candidate not in paths:
                    paths.append(candidate)
    return paths
