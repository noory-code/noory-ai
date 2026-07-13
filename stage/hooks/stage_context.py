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

from stage_paths import (  # noqa: E402  (after sys.path bootstrap)
    ACTIVE_TOPOLOGY_V4,
    DEFAULT_LANGUAGE,
    active_topology,
    load_language,
    load_venue_routing,
    normalize_path_text,
)
import stage_topology  # noqa: E402
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


LIFECYCLE_VIEW_RECORD_LIMIT = 3


def lifecycle_view_record_ids(
    directory: Path, limit: int = LIFECYCLE_VIEW_RECORD_LIMIT
) -> tuple[list[str], int]:
    """Return a bounded artifact-ID sample and total from one registry scan root."""

    records: list[str] = []
    try:
        paths = sorted(directory.glob("*.md"))
    except OSError:
        return records, 0
    for path in paths:
        if path.name.startswith("_") or path.name.lower() in {"index.md", "readme.md"}:
            continue
        fields = parse_frontmatter(path)
        record_id = fields.get("id") or path.stem
        if re.fullmatch(r"(?:DE|TH|[WRDOQAKMP])-\d{3,}", record_id) is None:
            continue
        records.append(record_id)
    return records[:limit], len(records)


def derived_lifecycle_view(stage_root: Path) -> str:
    """Render a read-only v4 lifecycle summary from registry context scan roots."""

    grouped: dict[str, list[str]] = {
        lifecycle: [] for lifecycle in stage_topology.LIFECYCLE_STATES
    }
    roadmap: list[str] = []
    for root in stage_topology.scan_roots("context"):
        resolved = stage_topology.resolve_zone(root)
        if resolved is None:
            continue
        _family, zone = resolved
        if zone.resolver_policy == "derived-view":
            continue
        record_ids, total = lifecycle_view_record_ids(stage_root / root)
        if not total:
            continue
        suffix = f" (+{total - len(record_ids)} more)" if total > len(record_ids) else ""
        summary = f"`{root}`: {', '.join(record_ids)}{suffix}"
        if zone.lifecycle_state in grouped:
            grouped[zone.lifecycle_state].append(summary)
        elif zone.resolver_policy == "decision-chain":
            roadmap.append(summary)

    lines = ["### Lifecycle view (derived, read-only)"]
    for lifecycle in stage_topology.LIFECYCLE_STATES:
        entries = grouped[lifecycle]
        if entries:
            detail = "; ".join(entries)
        elif lifecycle == "official":
            detail = f"none under `{stage_topology.OFFICIAL_ROOT}/`"
        else:
            detail = "none"
        lines.append(f"- {lifecycle} — {detail}")
    if roadmap:
        lines.append(
            "- roadmap (decision-derived lifecycle) — " + "; ".join(roadmap)
        )
    return "\n".join(lines)


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

    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        current_work = stage_topology.card_location_for_status("active")
        planned_work = stage_topology.card_location_for_status("selected")
        current_retro, _ = stage_topology.retrospective_locations()
        decision_paths = stage_topology.resolve_artifact_reference(
            "DE-00000000"
        ).candidate_paths
        state_roots = {
            prefix: stage_topology.resolve_artifact_reference(
                f"{prefix}-00000000"
            ).candidate_paths[0].rsplit("/", 1)[0]
            for prefix in ("O", "Q", "A", "K")
        }
        proposal_root = stage_topology.get_zone("proposals", "planned").canonical_path
        milestone_root = stage_topology.get_zone("roadmap", "milestones").canonical_path
        principles_path = next(
            path
            for path in stage_topology.get_zone("canon", "official").index_surfaces
            if path.endswith("principles.md")
        )
        parts = [
            "## Stage context",
            "- Global lifecycle axis: `planned` is intended, `current` is in progress, "
            "`official` is settled truth.",
            "- Space axis: `canon`, `model`, `decisions`, `work`, `state`, `proposals`, "
            "`roadmap`, `operations` divide responsibility.",
            f"- Core principles (full catalog: `{principles_path}`):",
            "  SSOT — one owning location per durable fact. MECE — no overlap, no known gaps.",
            "  Fail Fast — surface wrong premises early. AHA — no abstraction before repetition.",
            "  Completion — external view + internal view + retrospective, all three.",
            "  Honesty — never assert unverified facts; no partial completion, no silent substitution.",
            "- Cite the governing principles in every decision record and retrospective.",
            f"- Register an active work item in `.stage/{current_work}/` before modifying governed files "
            "(nearly all files are governed by default; see `.stage/settings.json`).",
            f"- Modifying `.stage/{stage_topology.OFFICIAL_ROOT}/` is gated ONLY by a pending intent "
            "(`scripts/promote_intent.py`) that names the completed work item being promoted or "
            "archived — no NEW work item is needed, and `.stage/` is not governed source so the "
            "registration/commit gates never fire on it. To archive, use the `stage-archive` skill.",
            f"- Artifact map — W current work `{current_work}` · R retro `{current_retro}` · "
            f"DE pending decision `{decision_paths[0].rsplit('/', 1)[0]}` · official decisions "
            f"`{decision_paths[1].rsplit('/', 1)[0]}` · O state `{state_roots['O']}` · "
            f"Q state `{state_roots['Q']}` · A state `{state_roots['A']}` · "
            f"K state `{state_roots['K']}` · planned "
            f"W cards `{planned_work}` · P proposal `{proposal_root}` · M milestone "
            f"`{milestone_root}`. A work card is ONE artifact moving planned -> current -> official; "
            "start a planned card with `scripts/start_work.py` (never hand-move it). Full catalog: "
            "`operations/artifacts.md` in the installed Stage plugin; routing: `index.md`.",
        ]
    else:
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
            "O/Q/A/K state `present/state/*` · planned W cards `future/backlog/items` · P proposal · M milestone. "
            "A work card is ONE artifact moving future -> present -> past; start a planned card with "
            "`scripts/start_work.py` (never hand-move it). "
            "Full catalog: `operations/artifacts.md` in the installed Stage plugin; routing: `index.md`.",
        ]

    routing = load_venue_routing(stage_root)
    if routing:
        routing_text = ", ".join(f"{kind} -> {venue}" for kind, venue in sorted(routing.items()))
        parts.append(
            f"- Venue routing (declared role policy): {routing_text}. Derive `venue` from this "
            "policy when registering work — do not ask the human during normal routing; a "
            "contradicting venue registers only with a decided decision record declaring "
            "`authorizes: venue_exception` (register_work --decision). A kind routed to `split` "
            "is mixed by definition: Split mixed design+implementation work into separate items "
            "with `parent` lineage instead of assigning one ambiguous item. An implementation "
            "venue that hits an unresolved product/design decision registers a planning-venue "
            "item carrying the evidence and the exact decision needed."
        )

    language = load_language(stage_root)
    if language != DEFAULT_LANGUAGE:
        parts.append(
            f"- Stage document language: `{language}`. Write human-readable Stage content "
            "(titles after the ID, prose bodies, index labels) in that language. Keep machine "
            "tokens exactly as templates declare: IDs, paths, frontmatter keys and enum values, "
            "work kinds, venue and principle names, and record section headings "
            "(`## Purpose`, `## Verification`, ...)."
        )

    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        parts.append("\n" + derived_lifecycle_view(stage_root))
        state_index = next(
            path
            for path in stage_topology.get_zone("state", "current").index_surfaces
            if path.endswith("current.md")
        )
        active_index, review_index = stage_topology.get_zone(
            "work", "current"
        ).index_surfaces
        snippets: list[tuple[str, Path | None]] = [
            ("Current state", stage_root / state_index),
            ("Active work", stage_root / active_index),
            ("Review candidates", stage_root / review_index),
        ]
    else:
        snippets = [
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
    if pre_init:
        directive = CONSUMER_CONTEXT_DIRECTIVE_PRE_INIT
    elif stage_root is not None and active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        question_root = stage_topology.resolve_artifact_reference(
            "Q-00000000"
        ).candidate_paths[0].rsplit("/", 1)[0]
        directive = (
            "- Consult these when planning and executing — they are project norms, "
            "not optional reading. Root-level sources bind everywhere; a source inside "
            "a package directory binds work under that subtree only; within a source, "
            "honor its own applicability (a path-scoped rule or a trigger-scoped skill "
            "applies only per its own declaration). If an applicable instruction contradicts "
            "observed reality or Stage truth, do not silently deviate or silently obey: "
            f"register the conflict as an open question (`{question_root}/`) with your proposed "
            "correction and ask the user to fix the instruction."
        )
    else:
        directive = CONSUMER_CONTEXT_DIRECTIVE
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
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        question_root = stage_topology.resolve_artifact_reference(
            "Q-00000000"
        ).candidate_paths[0].rsplit("/", 1)[0]
        directory = stage_root / question_root
    else:
        directory = stage_root / "present" / "state" / "questions"
    for path in record_files(directory):
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
