# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import re
import sys
from datetime import date, datetime, timezone, tzinfo
from pathlib import Path

# Sibling modules load by bare name; make the hooks dir importable whether this
# module is reached through stage_guard (already bootstrapped) or imported on
# its own by name or file path.
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import (  # noqa: E402  (after sys.path bootstrap)
    ACTIVE_TOPOLOGY_V4,
    DEFAULT_LANGUAGE,
    active_topology,
    load_language,
    load_venue_routing,
    normalize_path_text,
)
import stage_topology  # noqa: E402
import stage_roadmap  # noqa: E402
from stage_work import (  # noqa: E402  (after sys.path bootstrap)
    ACTIVE_VIEW_STATUSES,
    REVIEW_VIEW_STATUSES,
    WORK_OPEN_STATUSES,
    item_is_open,
    load_work_items,
    parse_frontmatter,
    stage_completion_blockers,
)
from stage_runtime import latest_session_summaries  # noqa: E402  (after sys.path bootstrap)
from stage_memory_index import (  # noqa: E402,F401  (helpers stay importable from here)
    SESSION_CONTEXT_CHAR_LIMIT,
    SESSION_CONTEXT_LINE_LIMIT,
    Block,
    bounded_record_line,
    decision_roots,
    decision_title_lines,
    find_lines,
    fit_blocks,
    id_sort_key,
    record_files,
    rule_candidate_lines,
    RULE_CANDIDATE_LIST,
)


def read_if_exists(path: Path, limit: int = 1400) -> str:
    """A bounded snippet of one file, and — when the cap bites — how much of it
    the session is NOT seeing. A silent tail cut reads as a complete document,
    so the marker names the loss and where to read the rest."""
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    kept = text[:limit].rstrip()
    dropped = len(text.splitlines()) - len(kept.splitlines())
    location = f"{path.parent.name}/{path.name}"
    return kept + f"\n…{dropped} more lines truncated — read `{location}` in full"


# States the inline-interpreter gate (`stage_shell.interpreter_inline_stage_write`) at session
# start. Without it a session learns the rule only from the denial and pays a refused call to
# find out.
INLINE_INTERPRETER_RULE_LINE = (
    "- A shell command that runs inline interpreter code (`python -c`, `node -e`, `bash -c`, "
    "an interpreter heredoc) and mentions `.stage` is refused, read-only code included. "
    "Use Write/Edit or a script file."
)


def standing_rule_lines(
    lifecycle: str, principles_path: str, current_work: str, official_root: str
) -> list[str]:
    """The rules every session starts with, one line each.

    A line stays here only when a session needs it before its first tool call. What a
    refusal, a skill, or an operations document already says is named, not repeated
    (W-00000417): these lines share the limit with the index, so every sentence here is
    a decision title the index cannot carry.
    """
    return [
        "## Stage context",
        f"- Lifecycle: {lifecycle}. Where each record kind lives: `.stage/index.md`; "
        f"principles: `{principles_path}`.",
        f"- Modifying governed files (nearly all files; see `.stage/settings.json`) needs an "
        f"active work item in `.stage/{current_work}/`; modifying `.stage/{official_root}/` "
        "needs a promotion intent, not a new work item. The hook's refusal names the command.",
        INLINE_INTERPRETER_RULE_LINE,
    ]


def active_milestone_table(stage_root: Path) -> str:
    """Render the compact v4 active-milestone view from decision chains."""

    lines = [
        "### Active milestones (decision-derived)",
        "| Milestone | Theme | Title |",
        "|---|---|---|",
    ]
    milestones = stage_roadmap.active_milestones(stage_root)
    if not milestones:
        lines.append("| — | — | None |")
        return "\n".join(lines)
    for milestone in milestones:
        link = f"roadmap/milestones/{milestone.record_id}.md"
        title = milestone.title.replace("|", "\\|")
        lines.append(
            f"| [{milestone.record_id}]({link}) | {milestone.theme or '—'} | {title} |"
        )
    return "\n".join(lines)


def _table_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|") or "—"


def derived_work_view(stage_root: Path, statuses: tuple[str, ...], review: bool) -> str:
    """Render current cards whose status is in ``statuses`` as a Markdown table.

    The cards own their status; this view replaces the retired `work/active.md`
    and `work/review.md` files (DE-00000091), so it cannot disagree with them.
    Returns "" when no card qualifies.
    """

    items = sorted(
        (item for item in load_work_items(stage_root) if item.status in statuses),
        key=lambda item: id_sort_key(item.item_id),
    )
    if not items:
        return ""
    if review:
        lines = [
            "| Work | Title | Status | Verification | Retrospective | Promotion | Card |",
            "|---|---|---|---|---|---|---|",
        ]
    else:
        lines = [
            "| Work | Title | Kind | Venue | Status | Card |",
            "|---|---|---|---|---|---|",
        ]
    for item in items:
        try:
            link = item.path.relative_to(stage_root).as_posix()
        except ValueError:
            link = item.path.as_posix()
        card = f"[{link}]({link})"
        if review:
            cells = (
                item.item_id, item.title, item.status, item.verification,
                item.retrospective, item.promotion, card,
            )
        else:
            cells = (item.item_id, item.title, item.kind, item.venue, item.status, card)
        lines.append(
            "| " + " | ".join(cell if cell == card else _table_cell(cell) for cell in cells) + " |"
        )
    return "\n".join(lines)


def work_hierarchy_view(stage_root: Path, listed_statuses: tuple[str, ...] = ()) -> str:
    """Render current work as a deterministic parent/child tree.

    `listed_statuses` names the statuses whose cards another view of the same text already
    carries with their title (the session index's work tables). Such a card is not carried
    a second time: a card with no parent and no child is left out, and a card inside a tree
    is named by id and status only, because the tree is the one thing the tables do not
    say. Returns "" when every current card is left out that way.
    """

    items = load_work_items(stage_root)
    by_id = {item.item_id: item for item in items}
    children: dict[str, list] = {}
    roots = []
    for item in items:
        if item.parent and item.parent in by_id:
            children.setdefault(item.parent, []).append(item)
        else:
            roots.append(item)
    for siblings in children.values():
        siblings.sort(key=lambda item: id_sort_key(item.item_id))
    roots.sort(key=lambda item: id_sort_key(item.item_id))

    lines = ["### Current work hierarchy"]

    def append_item(item, depth: int, seen: set[str]) -> None:
        indent = "  " * depth
        title = "" if item.status in listed_statuses else " ".join(item.title.split())
        label = f"{item.item_id} {title}".rstrip()
        lines.append(f"{indent}- {label} [{item.status}]")
        if item.item_id in seen:
            return
        next_seen = {*seen, item.item_id}
        for child in children.get(item.item_id, []):
            append_item(child, depth + 1, next_seen)

    for root in roots:
        if root.status in listed_statuses and not children.get(root.item_id):
            continue
        append_item(root, 0, set())
    if not roots:
        lines.append("- None")
    return "\n".join(lines) if len(lines) > 1 else ""


def session_context(workspace_root: Path) -> str:
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        # The stage-init session itself must still see host instructions.
        return pre_init_context(workspace_root)

    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        current_work = stage_topology.card_location_for_status("active")
        principles_path = next(
            path
            for path in stage_topology.get_zone("canon", "official").index_surfaces
            if path.endswith("principles.md")
        )
        parts = standing_rule_lines(
            "`planned` is intended, `current` is in progress, `official` is settled truth",
            principles_path,
            current_work,
            stage_topology.OFFICIAL_ROOT,
        )
    else:
        parts = standing_rule_lines(
            "`past` is official, `present` is in progress, `future` is planned",
            "past/canon/principles.md",
            "present/work/items",
            "past",
        )

    routing = load_venue_routing(stage_root)
    if routing:
        routing_text = ", ".join(f"{kind} -> {venue}" for kind, venue in sorted(routing.items()))
        parts.append(
            f"- Venue routing (declared role policy): {routing_text}. `register_work.py` "
            "derives `venue` from it; do not ask the human during normal routing. Exceptions "
            "and `split` kinds: the `stage-work` skill. For execution, spawn a teammate agent "
            "for `claude`-venue work and hand `codex`-venue work to the driver; read "
            "`.stage/operations/claude-venue.md` for the procedure."
        )

    language = load_language(stage_root)
    if language != DEFAULT_LANGUAGE:
        parts.append(
            f"- Stage document language: `{language}` for human-readable content. Machine "
            "tokens stay as templates declare: IDs, paths, frontmatter keys and enum values, "
            "work kinds, venue and principle names, record section headings."
        )

    # The rules above are the same every session; the index below is derived from the
    # records each time and is what the limit shortens (DE-00000100).
    head = "\n".join(parts)
    index = session_index(workspace_root, SESSION_CONTEXT_CHAR_LIMIT - len(head) - 1)
    return f"{head}\n{index}" if index else head[:SESSION_CONTEXT_CHAR_LIMIT]


def _fixed_block(heading: str, body: str) -> Block:
    return Block(heading, [body] if body else [])


def session_index(workspace_root: Path, limit: int = SESSION_CONTEXT_CHAR_LIMIT) -> str:
    """The index a session starts with, in at most `limit` characters (DE-00000100).

    One line per record and no bodies, derived from the records on every call. The
    SessionStart hook appends it to its rules and `scripts/subsession_brief.py` appends it
    to a cloud session's brief, so both kinds of session start from the same index.

    What the session is doing now is never shortened. Over the limit, lines go in this
    order, each block leaving one line that counts what it left out and names where to read
    it: rule candidates from the end of their list, then decision titles from the oldest,
    then the previous session's handoff, then the two lists of rule files. Candidates go
    first because a decision binds work and a candidate is not yet a rule (W-00000413: 39
    candidates had pushed every decision title out). Only `proposed: promote` candidates
    are listed; one line that is never shortened counts the rest (DE-00000104).
    """
    stage_root = workspace_root / ".stage"
    if not stage_root.exists():
        return ""
    v4 = active_topology(stage_root) == ACTIVE_TOPOLOGY_V4

    blocks: list[Block] = []
    if v4:
        blocks.append(_fixed_block("", "\n" + active_milestone_table(stage_root)))
        # The two tables below carry every current card once; the tree adds only parent
        # and child relations, so it does not repeat a card they list (W-00000410).
        hierarchy = work_hierarchy_view(stage_root, ACTIVE_VIEW_STATUSES + REVIEW_VIEW_STATUSES)
        blocks.append(_fixed_block("", "\n" + hierarchy if hierarchy else ""))
        snippets: list[tuple[str, str]] = [
            ("Active work", derived_work_view(stage_root, ACTIVE_VIEW_STATUSES, review=False)),
            (
                "Review candidates",
                derived_work_view(stage_root, REVIEW_VIEW_STATUSES, review=True),
            ),
        ]
    else:
        snippets = [
            ("Active work", read_if_exists(stage_root / "present" / "work" / "active.md")),
            ("Review candidates", read_if_exists(stage_root / "present" / "work" / "review.md")),
        ]
    # The observation index file (`state/current.md`) owns nothing this view
    # does not derive from the records themselves, and reading it through a
    # character cap is what dropped the newest observations. The derived list
    # replaces it rather than duplicating it.
    blocks.append(Block("### Open observations", open_observation_lines(stage_root)))
    for title, body in snippets:
        blocks.append(_fixed_block(f"### {title}", body))
    blocks.append(Block("### Open questions", open_question_lines(stage_root)))
    blocks.append(Block("### Selected backlog", selected_backlog_lines(stage_root)))

    recent_bodies = [
        body
        for body in (read_if_exists(path) for path in latest_session_summaries(stage_root))
        if body
    ]
    heading = "Most recent session" if len(recent_bodies) == 1 else "Most recent sessions (concurrent)"
    blocks.append(
        Block(
            f"### {heading}",
            recent_bodies,
            shed=3,
            noun="session handoffs",
            read_at="`.stage/.runtime/sessions/`",
            separator="\n\n",
        )
    )

    decisions = decision_title_lines(stage_root)
    candidates, candidate_status = rule_candidate_lines(stage_root)
    if decisions or candidates or candidate_status:
        blocks.append(Block("### Finding a record", tail=find_lines(stage_root)))
    blocks.append(
        Block(
            "### Decisions (titles only, newest first)",
            decisions,
            shed=2,
            noun="older decisions",
            read_at=" and ".join(f"`.stage/{root}/`" for root in decision_roots(stage_root)),
        )
    )

    consumer = consumer_context_lines(workspace_root, stage_root=stage_root)
    if consumer:
        blocks.append(
            Block(
                "### Project instructions (host-defined)",
                consumer,
                tail=[consumer_context_directive(stage_root)],
                shed=4,
                noun="instruction sources",
                read_at="the project root and each package directory",
            )
        )
    operations = project_operations_lines(workspace_root)
    if operations:
        blocks.append(
            Block(
                "### Project operations (project-defined)",
                operations,
                tail=[PROJECT_OPERATIONS_DIRECTIVE],
                shed=5,
                noun="operation files",
                read_at="`.stage/operations/`",
            )
        )
    blocks.append(
        Block(
            "### Rule candidates (not yet rules)",
            candidates,
            tail=candidate_status,
            shed=1,
            noun="candidates",
            read_at=f"`.stage/{RULE_CANDIDATE_LIST}`",
        )
    )
    return fit_blocks(blocks, limit)


# Host-project instruction sources, relative to the workspace root. Stage
# works without any of them; when present they are project norms the session
# must actively use (and challenge when wrong) rather than ignore.
CONSUMER_CONTEXT_FILES: tuple[str, ...] = (
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
)
CONSUMER_CONTEXT_DIRS: tuple[str, ...] = (
    ".claude/rules",
    ".claude/skills",
    ".agents/rules",
    ".agents/skills",
)
CONSUMER_CONTEXT_MAX_LINES = 10


PROJECT_OPERATIONS_DIRECTIVE = (
    "- Read the applicable files in full when planning and executing; "
    "this list carries names only."
)


def project_operations_lines(workspace_root: Path) -> list[str]:
    """List project-owned operation files without copying their contents."""

    operations_root = workspace_root / ".stage" / "operations"
    try:
        files = sorted(entry for entry in operations_root.iterdir() if entry.is_file())
    except OSError:
        return []
    return [f"- `{entry.relative_to(workspace_root).as_posix()}`" for entry in files]


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


def consumer_context_directive(stage_root: Path) -> str:
    """How a session uses the listed instruction sources, naming this topology's question folder."""

    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return CONSUMER_CONTEXT_DIRECTIVE
    question_root = stage_topology.resolve_artifact_reference(
        "Q-00000000"
    ).candidate_paths[0].rsplit("/", 1)[0]
    return (
        "- Consult these when planning and executing — they are project norms, "
        "not optional reading. Root-level sources bind everywhere; a source inside "
        "a package directory binds work under that subtree only; within a source, "
        "honor its own applicability (a path-scoped rule or a trigger-scoped skill "
        "applies only per its own declaration). If an applicable instruction contradicts "
        "observed reality or Stage truth, do not silently deviate or silently obey: "
        f"register the conflict as an open question (`{question_root}/`) with your proposed "
        "correction and ask the user to fix the instruction."
    )


def pre_init_context(workspace_root: Path) -> str:
    """What a session sees before `stage-init`: the notice and the host instructions."""

    text = (
        "## Stage\n"
        "This project has no `.stage/`. If the Stage harness applies to this project, "
        "create the artifact structure first with `stage-init`."
    )
    consumer = consumer_context_lines(workspace_root)
    if not consumer:
        return text
    block = Block(
        "### Project instructions (host-defined)",
        consumer,
        tail=[CONSUMER_CONTEXT_DIRECTIVE_PRE_INIT],
        shed=1,
        noun="instruction sources",
        read_at="the project root and each package directory",
    )
    return text + "\n" + fit_blocks([block], SESSION_CONTEXT_CHAR_LIMIT - len(text) - 1)


SESSION_CONTEXT_RECORD_LIMIT = 3


def question_is_answered(path: Path) -> bool:
    """Whether the question's Status section starts with the `answered` state token."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    match = re.search(
        r"^## Status[ \t]*\r?\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return False
    body = match.group("body").lstrip()
    return re.match(r"(?:[*_]{1,3})?answered\b", body, flags=re.IGNORECASE) is not None


def observation_root(stage_root: Path) -> Path:
    """The directory holding open observations. Closed ones leave it for the
    official archive, so every record found here is still open."""
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        family_root = stage_topology.resolve_artifact_reference(
            "O-00000000"
        ).candidate_paths[0].rsplit("/", 1)[0]
        return stage_root / family_root
    return stage_root / "present" / "state" / "observations"


def local_today(now: datetime | None = None, zone: tzinfo | None = None) -> date:
    """Today's date where the session runs. `opened:` is written by hand from
    the writer's own calendar, so the age is counted from the same calendar;
    the UTC date lags it by a day every morning east of Greenwich."""
    return (now or datetime.now(timezone.utc)).astimezone(zone).date()


def days_open(opened: str, today: date) -> int | None:
    """Days since the record declared it opened; None when undeclared or
    unparseable. Filesystem timestamps are not a substitute — a fresh clone or
    a git worktree checkout stamps every record with today."""
    try:
        return (today - date.fromisoformat(opened.strip())).days
    except ValueError:
        return None


def open_observation_lines(stage_root: Path, today: date | None = None) -> list[str]:
    """Every open observation, newest first, one bounded line each.

    Uncapped by count on purpose. A count cap drops the tail, the tail is the
    newest records, and an observation nobody sees is an observation nobody
    closes — which is the whole failure this view exists to end. Size stays
    bounded per record instead: a line carries the ID, the title, and how long
    the record has been open, never its body.
    """
    today = today or local_today()
    records: list[tuple[str, str, str]] = []
    for path in record_files(observation_root(stage_root)):
        fields = parse_frontmatter(path)
        records.append(
            (
                fields.get("id") or path.stem,
                fields.get("title") or "",
                fields.get("opened") or "",
            )
        )
    records.sort(key=lambda entry: id_sort_key(entry[0]), reverse=True)
    lines: list[str] = []
    for item_id, title, opened in records:
        age = days_open(opened, today) if opened else None
        suffix = f" (open {age}d)" if age is not None else " (open ?)"
        lines.append(bounded_record_line(item_id, title, suffix))
    return lines


def open_question_lines(stage_root: Path, limit: int = SESSION_CONTEXT_RECORD_LIMIT) -> list[str]:
    """Unanswered question records, newest first.

    Answered records normally move out of this directory. A record that must remain because other
    durable records cite it declares `answered` at the start of its Status section and is omitted.
    """
    records: list[tuple[str, str, str]] = []
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        question_root = stage_topology.resolve_artifact_reference(
            "Q-00000000"
        ).candidate_paths[0].rsplit("/", 1)[0]
        directory = stage_root / question_root
    else:
        directory = stage_root / "present" / "state" / "questions"
    for path in record_files(directory):
        if question_is_answered(path):
            continue
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
        if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
            lines.append(f"- …and {len(records) - limit} more in `{question_root}/`")
        else:
            lines.append(f"- …and {len(records) - limit} more in `present/state/questions/`")
    return lines


def selected_backlog_lines(stage_root: Path, limit: int = SESSION_CONTEXT_RECORD_LIMIT) -> list[str]:
    """Backlog records with `status: selected` — the queue the session should
    pick up next. Ordered by ID for determinism."""
    lines: list[str] = []
    selected: list[tuple[str, str, str]] = []
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        planned_root = stage_topology.card_location_for_status("selected")
        directory = stage_root / planned_root
    else:
        directory = stage_root / "future" / "backlog" / "items"
    for path in record_files(directory):
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
        if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
            lines.append(f"- …and {len(selected) - limit} more in `{planned_root}/`")
        else:
            lines.append(f"- …and {len(selected) - limit} more in `future/backlog/items/`")
    return lines


# Session-summary labels per language tag (DE-00000003). The values the labels
# carry (IDs, timestamps, blocker text) stay as produced. Unknown tags fall
# back to English.
SUMMARY_LABELS = {
    "en": {
        "title": "# Stage Session Summary",
        "end_time": "End time",
        "open_work": "Open work",
        "blockers": "Completion blockers",
        "handoff": "Handoff condition: open work items carry current status and next actions",
        "none": "none",
    },
    "ko": {
        "title": "# Stage 세션 요약",
        "end_time": "종료 시각",
        "open_work": "진행 중 작업",
        "blockers": "완료 차단 요소",
        "handoff": "인계 조건: 진행 중 작업 항목이 현재 상태와 다음 행동을 담고 있음",
        "none": "없음",
    },
}


def summarize_stage(stage_root: Path) -> str:
    items = load_work_items(stage_root)
    open_items = [item.item_id for item in items if item_is_open(item)]
    blockers = stage_completion_blockers(stage_root.parent)
    labels = SUMMARY_LABELS.get(load_language(stage_root), SUMMARY_LABELS["en"])
    open_text = ", ".join(open_items) if open_items else labels["none"]
    blocker_text = " / ".join(blockers) if blockers else labels["none"]
    return (
        f"{labels['title']}\n"
        f"- {labels['end_time']}: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- {labels['open_work']}: {open_text}\n"
        f"- {labels['blockers']}: {blocker_text}\n"
        f"- {labels['handoff']}\n"
    )
