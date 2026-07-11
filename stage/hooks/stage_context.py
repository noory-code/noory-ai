# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Sibling modules load by bare name; make the hooks dir importable whether this
# module is reached through stage_guard (already bootstrapped) or imported on
# its own by name or file path.
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import normalize_path_text  # noqa: E402  (after sys.path bootstrap)
from stage_work import (  # noqa: E402  (after sys.path bootstrap)
    WORK_OPEN_STATUSES,
    item_is_open,
    load_work_items,
    parse_frontmatter,
    stage_completion_blockers,
)
from stage_runtime import latest_session_summaries  # noqa: E402  (after sys.path bootstrap)


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
        "- Modifying `.stage/past/` is gated ONLY by a pending intent (`scripts/promote_intent.py`) that names "
        "the completed work item being promoted or archived — no NEW work item is needed, and `.stage/` is not "
        "governed source so the registration/commit gates never fire on it. To archive, use the `stage-archive` skill.",
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
