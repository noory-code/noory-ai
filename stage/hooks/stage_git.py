# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import re
import sys
from pathlib import Path

# Sibling modules load by bare name; make the hooks dir importable whether this
# module is reached through stage_guard (already bootstrapped) or imported on
# its own by name or file path.
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import normalize_path_text  # noqa: E402  (after sys.path bootstrap)
from stage_shell import (  # noqa: E402  (after sys.path bootstrap)
    SHELL_SEPARATORS,
    _restore_sentinels,
    shell_tokens,
)


GIT_GLOBAL_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


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


def command_has_git_commit(command: str) -> bool:
    return any(subcommand == "commit" for subcommand, _args in iter_git_commands(command))


GIT_COMMIT_VALUE_LONG_FLAGS = {"--message", "--file", "--author", "--date", "--reuse-message", "--reedit-message", "--fixup", "--squash", "--gpg-sign"}
GIT_COMMIT_VALUE_SHORT_LETTERS = set("mFCcS")

# A shell redirection token (`>`, `>>`, `2>`, `2>&1`, `&>`, `>&2`, `<`, `<<`).
# `>`/`<` are not in SHELL_OPERATOR_CHARS, so a token like `2>&1` survives whole
# and would otherwise be read as a commit pathspec — a redirection ends the git
# command's arguments, so arg scanning stops at the first one.
_REDIRECTION_RE = re.compile(r"^([0-9]*(>>?|<<?)|[0-9]*[<>]&[0-9-]*|&>>?)")


def _is_shell_redirection(token: str) -> bool:
    return bool(_REDIRECTION_RE.match(_restore_sentinels(token)))


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
            if _is_shell_redirection(arg):
                break  # redirection + everything after is not a git argument
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
