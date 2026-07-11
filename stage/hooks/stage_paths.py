# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def clean_path_text(path: str) -> str:
    """Surface cleanup only — strip quotes, unify separators, collapse repeated
    slashes, drop leading `./`. Keeps `..` INTACT so a filesystem resolve can
    follow symlinks before collapsing `..` (lexical collapse first would
    mis-target a symlink parent). Preserves a Windows UNC prefix (`\\\\server`)."""
    value = path.strip().strip("'\"`")
    value = value.replace("\\", "/")
    unc = value.startswith("//")  # UNC share root — keep the double slash
    leading_slash = value.startswith("/")
    core = re.sub(r"/+", "/", value).lstrip("/")  # `.//src` must not become `/src`
    if unc:
        value = "//" + core
    elif leading_slash:
        value = "/" + core
    else:
        value = core
    while value.startswith("./"):
        value = value[2:]
    return value


def normalize_path_text(path: str) -> str:
    """Cleaned path with `.`/`..` collapsed lexically — for string comparisons
    and slot keys that never hit the filesystem. For classifying a real write
    target, go through `relative_to_workspace` (resolves symlinks first)."""
    return collapse_dot_segments(clean_path_text(path))


def collapse_dot_segments(value: str) -> str:
    """Lexically resolve `.`/`..` so `.stage/../src` cannot masquerade as a
    `.stage`-internal path (and vice versa). Purely textual — no filesystem
    access, so it is safe for not-yet-existing targets and identical on every
    host. Leading `..` that escapes the anchor is preserved (it still reads as
    outside the workspace to every gate)."""
    if not value:
        return value
    absolute_prefix = ""
    rest = value
    drive = re.match(r"^([A-Za-z]:)(.*)$", rest)
    if drive:
        absolute_prefix = drive.group(1)
        rest = drive.group(2)
    if rest.startswith("/"):
        absolute_prefix += "/"
        rest = rest.lstrip("/")
    stack: list[str] = []
    for segment in rest.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if stack and stack[-1] != "..":
                stack.pop()
            elif not absolute_prefix:
                stack.append("..")
            # An absolute path cannot escape its own root: drop the `..`.
            continue
        stack.append(segment)
    return absolute_prefix + "/".join(stack)


def stage_real_root(workspace_root: Path) -> Path | None:
    """The real filesystem location of `<workspace>/.stage`, following a
    symlinked `.stage` itself. Used to classify writes against the true tree.

    Returns None for a degenerate root (`.stage -> .` or `-> ..`) that equals or
    contains the workspace — otherwise every ordinary write would remap into a
    logical `.stage/...` and be excluded from governance."""
    try:
        workspace_resolved = workspace_root.resolve()
        stage = (workspace_root / ".stage").resolve()
    except (OSError, RuntimeError):  # RuntimeError = symlink loop on Python 3.9
        return None
    if stage == workspace_resolved:
        return None
    try:
        workspace_resolved.relative_to(stage)  # workspace lies inside stage → ancestor
        return None
    except ValueError:
        return stage


def relative_to_workspace(path: str | Path, workspace_root: Path) -> str:
    """Canonical workspace-relative form of a write target (P28 single model).

    Resolves symlink components and `..` in filesystem order (symlinks first,
    then `..`), then re-maps a target that lands inside the REAL `.stage` tree
    back to a logical `.stage/...` string — so `link/../past` (link ->
    `.stage/present`), `.stage/../src`, and a symlinked `.stage -> data` all
    classify by where the write truly lands, not how it was spelled. A path that
    escapes the workspace keeps its lexical form so outside-workspace checks
    still fire; unresolvable input degrades to lexical.
    """
    text = clean_path_text(str(path))
    try:
        candidate = Path(text).expanduser()
    except RuntimeError:
        # `~user` with no such account raises on POSIX (e.g. `~draft.py`) — it is
        # an ordinary workspace-relative filename, not a home reference.
        candidate = Path(text)
    try:
        workspace_resolved = workspace_root.resolve()
    except (OSError, RuntimeError):
        workspace_resolved = workspace_root
    base = candidate if candidate.is_absolute() else (workspace_resolved / text)
    try:
        resolved = base.resolve()
    except (OSError, RuntimeError):  # RuntimeError = symlink loop on Python 3.9
        return normalize_path_text(text)

    stage_real = stage_real_root(workspace_root)
    if stage_real is not None:
        if resolved == stage_real:
            return ".stage"
        try:
            return ".stage/" + resolved.relative_to(stage_real).as_posix()
        except ValueError:
            pass
    try:
        return normalize_path_text(resolved.relative_to(workspace_resolved).as_posix())
    except ValueError:
        # Resolved outside the workspace (e.g. `~/…`, an escaping symlink): return
        # the absolute path so outside-workspace checks fire — not the lexical
        # spelling, which would read as a governed workspace path.
        return resolved.as_posix()


def entry_relative_to_workspace(path: str | Path, workspace_root: Path) -> str:
    """Canonical workspace-relative form that keeps FINAL-ENTRY identity:
    parent components are resolved (symlinks first, then `..`), the last
    component is kept as named. Exact-entry authorizations (a work item's
    `promotes`, pending intents, archive filenames) name entries, not targets —
    `rm`/`mv` act on the entry a path NAMES, and two symlinked leaves aliasing
    one target are distinct grants. A spelling with no leaf identity (trailing
    `/` or `/.`, bare `.`/`..`) falls back to the fully resolved form."""
    text = clean_path_text(str(path))
    stripped = text.rstrip()
    name = Path(text).name if text else ""
    if name in ("", ".", "..") or stripped.endswith("/") or stripped.endswith("/."):
        return relative_to_workspace(text, workspace_root)
    parent = relative_to_workspace(str(Path(text).parent), workspace_root)
    if parent in ("", "."):
        return name
    return parent.rstrip("/") + "/" + name


def stage_relative_forms(path: str | Path, workspace_root: Path) -> tuple[str, str, str]:
    """(fully-resolved, entry-canonical, lexical) forms of one write target.
    Detection gates classify by the union of the three — fail closed: the
    resolved form catches symlink/`..` re-entry, the entry form catches an
    aliased parent whose LEAF is itself an outward symlink, the lexical form
    catches a degenerate `.stage -> .` and plain spellings."""
    return (
        relative_to_workspace(path, workspace_root),
        entry_relative_to_workspace(path, workspace_root),
        normalize_path_text(str(path)),
    )


# Predicates below take a CANONICAL workspace-relative path (from
# relative_to_workspace) — do not pass a raw, unresolved spelling.
def path_targets_stage_root(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/" in normalized or normalized.endswith("/.stage")


def path_targets_stage_past(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/past/" in normalized or normalized.startswith("/.stage/past/")


def path_targets_stage_archive(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/past/work/archive/" in normalized or normalized.startswith("/.stage/past/work/archive/")


def is_stage_internal_path(path: str, workspace_root: Path) -> bool:
    # Union of forms: a symlinked `.stage/settings.json` (resolve lands outside)
    # must stay stage-internal or the malformed-governance gate would deny the
    # very repair it asks for.
    return any(
        form == ".stage" or form.startswith(".stage/")
        for form in stage_relative_forms(path, workspace_root)
    )


def load_governance(stage_root: Path) -> dict[str, Any]:
    settings_path = stage_root / "settings.json"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    governance = data.get("governance")
    return governance if isinstance(governance, dict) else {}


# Version of the `.stage` artifact/settings contract, independent of the
# plugin release version. stage-init stamps new harnesses via the settings
# template; preserved older settings are never overwritten — the audit warns
# on a missing or different value instead. Bump only when the recorded
# contract changes shape; introduce an idempotent sequential migration when a
# second persistent transition actually exists.
STAGE_SCHEMA_VERSION = 1


def configured_write_tools(stage_root: Path) -> set[str]:
    """Tool names settings.json registers as additional write tools.

    A host or MCP tool that writes files under a name outside the built-in
    allowlist bypasses every gate (see hooks/README.md §Limits); a project
    registers such names in `extra_write_tools` so the write gates classify
    them. Broken settings yield the empty set: the registered names cannot be
    read back, so those tools fall back to the documented ungated default
    while built-in tools stay behind the governance fail-closed deny."""
    settings_path = stage_root / "settings.json"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(data, dict):
        return set()
    names = data.get("extra_write_tools")
    if not isinstance(names, list):
        return set()
    return {str(name).strip() for name in names if str(name).strip()}


def governance_broken(stage_root: Path) -> bool:
    """True when settings.json exists but cannot be trusted (fail-closed signal)."""
    settings_path = stage_root / "settings.json"
    if not settings_path.exists():
        return False
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    if not isinstance(data, dict):
        return True
    # A mistyped tool registration means the writer the project meant to gate
    # would silently fall back to the ungated unknown-name default — treat the
    # whole file as untrusted until repaired.
    extra_tools = data.get("extra_write_tools")
    if extra_tools is not None and (
        not isinstance(extra_tools, list)
        or any(not isinstance(name, str) for name in extra_tools)
    ):
        return True
    governance = data.get("governance")
    return governance is not None and not isinstance(governance, dict)


DEFAULT_EXCLUDED_PREFIXES = (".stage", ".git", ".discuss")


def path_has_prefix(relative: str, prefix: str) -> bool:
    clean = prefix.rstrip("/")
    return bool(clean) and (relative == clean or relative.startswith(clean + "/"))


def is_outside_workspace(relative: str) -> bool:
    return (
        not relative
        or relative.startswith("/")
        or bool(re.match(r"^[A-Za-z]:", relative))
        or relative.startswith("../")
        or relative == ".."
        or relative == "~"
        or relative.startswith("~/")  # home dir — but `~draft.py` is a real file
    )


def is_source_path(path: str, workspace_root: Path, follows_symlink: bool = False) -> bool:
    """Whether a write target is a governed workspace source.

    Operation semantics decide which forms classify. A CONTENT write
    (`follows_symlink=True`: Write/Edit) modifies the DEREFERENCED target, so it
    is classified by the resolved form alone — a write to `.git/link.py`
    (-> src/app.py) governs `src/app.py`, not the `.git` entry. An UNLINK/move
    (default) acts on the named ENTRY, so exclusions win on the entry and
    lexical forms (deleting `src/link -> .git/config` targets the entry) while
    inclusion holds across all forms (a symlink entry into governed space stays
    governed when its resolve derefs outward)."""
    resolved, entry, lexical = stage_relative_forms(path, workspace_root)
    if follows_symlink:
        forms = [resolved] if not is_outside_workspace(resolved) else []
        exclude_forms = forms
    else:
        forms = [form for form in (resolved, entry, lexical) if not is_outside_workspace(form)]
        exclude_forms = [form for form in (entry, lexical) if not is_outside_workspace(form)]
    if not forms:
        return False
    if any(
        path_has_prefix(form, prefix)
        for form in exclude_forms
        for prefix in DEFAULT_EXCLUDED_PREFIXES
    ):
        return False

    governance = load_governance(workspace_root / ".stage")
    if any(_form_excluded(form, governance, workspace_root) for form in exclude_forms):
        return False
    return any(_form_included(form, governance, workspace_root) for form in forms)


def _governance_prefix_forms(raw_prefix: str, workspace_root: Path) -> set[str]:
    """Canonical AND lexical forms of a configured prefix. A prefix that is a
    symlink needs both: the canonical form matches writes that reach its target
    directory, the lexical form keeps matching spellings under the entry itself
    when the target escapes the workspace (`generated -> /mnt/generated`)."""
    return {
        relative_to_workspace(raw_prefix, workspace_root),
        normalize_path_text(raw_prefix),
    }


def _form_excluded(relative: str, governance: dict[str, Any], workspace_root: Path) -> bool:
    """Configured (settings.json) exclusions only — structural `.stage`/`.git`/
    `.discuss` prefixes are checked across all forms in is_source_path."""
    raw_exclude_paths = governance.get("exclude_paths")
    if isinstance(raw_exclude_paths, list):
        for raw_prefix in raw_exclude_paths:
            if any(
                path_has_prefix(relative, prefix)
                for prefix in _governance_prefix_forms(str(raw_prefix), workspace_root)
            ):
                return True
    suffix = Path(relative).suffix.lower()
    raw_exclude_extensions = governance.get("exclude_extensions")
    if isinstance(raw_exclude_extensions, list) and suffix in {
        str(ext).lower() for ext in raw_exclude_extensions
    }:
        return True
    return False


def _form_included(relative: str, governance: dict[str, Any], workspace_root: Path) -> bool:
    # Configured prefixes are canonicalized the same way as the target so a
    # symlinked `governance.paths` entry matches the resolved file.
    raw_paths = governance.get("paths")
    suffix = Path(relative).suffix.lower()
    raw_extensions = governance.get("extensions")
    ext_governed = isinstance(raw_extensions, list) and bool(raw_extensions)
    if isinstance(raw_paths, list) and raw_paths:
        for raw_prefix in raw_paths:
            if any(
                path_has_prefix(relative, prefix)
                for prefix in _governance_prefix_forms(str(raw_prefix), workspace_root)
            ):
                return True
        # Paths allowlist present: only listed paths (or listed extensions).
        return ext_governed and suffix in {str(ext).lower() for ext in raw_extensions}
    if ext_governed:
        return suffix in {str(ext).lower() for ext in raw_extensions}
    # Broad default: every non-excluded workspace file is governed.
    return True
