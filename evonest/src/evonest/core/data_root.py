"""Evonest per-project data root — `.noory/evonest/` (noory-ai overhaul R9).

Every noory plugin's per-project artifacts consolidate under ONE `.noory/`
dotfolder (`.noory/plot/`, `.noory/distill/`, `.noory/evonest/`, …). A legacy
`.evonest/` dir is migrated lazily on first access (one move, same volume);
if BOTH roots exist, the new root wins and the legacy dir is preserved for
the user to reconcile — never merged blindly.

This module is the ONE place that knows the location. Everything else
(state, initializer, CLI walk-up, tool log paths) resolves through it.
"""

from __future__ import annotations

import shutil
from pathlib import Path

LEGACY_DIRNAME = ".evonest"
# Ignore ONLY our subtree. `.noory/` is SHARED with plugins whose artifacts
# are source-of-truth data (e.g. plot canvases) — a blanket `.noory/` ignore
# would silently untrack them.
GITIGNORE_ENTRY = ".noory/evonest/"


def evonest_data_root(project: Path, *, create: bool = False) -> Path:
    """Resolve `<project>/.noory/evonest/`, lazily migrating a legacy
    `<project>/.evonest/`. ``create=False`` (default) never creates
    directories — read paths stay side-effect-free."""
    new_root = project / ".noory" / "evonest"
    legacy = project / LEGACY_DIRNAME
    if legacy.is_dir() and not new_root.exists():
        new_root.parent.mkdir(exist_ok=True)
        shutil.move(str(legacy), str(new_root))
        _carry_gitignore_intent(project)
    if create:
        new_root.mkdir(parents=True, exist_ok=True)
    return new_root


def _carry_gitignore_intent(project: Path) -> None:
    """A project that ignored `.evonest/` must keep ignoring the data after
    the move — otherwise the next blanket `git add` silently tracks runtime
    data. Only appends when the user had the legacy entry; never invents
    ignore policy for projects that tracked their data on purpose."""
    gitignore = project / ".gitignore"
    if not gitignore.is_file():
        return
    content = gitignore.read_text(encoding="utf-8")
    if LEGACY_DIRNAME + "/" in content and GITIGNORE_ENTRY not in content:
        with open(gitignore, "a", encoding="utf-8") as f:
            f.write(f"\n# Evonest evolution data (R9 location)\n{GITIGNORE_ENTRY}\n")


def has_data_root(directory: Path) -> bool:
    """True if the directory hosts an evonest data root — new layout first,
    legacy `.evonest/` accepted (it will migrate on first real access)."""
    return (directory / ".noory" / "evonest").is_dir() or (
        directory / LEGACY_DIRNAME
    ).is_dir()
