# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Sibling modules load by bare name; make the hooks dir importable whether this
# module is reached through stage_guard (already bootstrapped) or imported on
# its own by name or file path.
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from stage_paths import (  # noqa: E402  (after sys.path bootstrap)
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    clean_path_text,
    entry_relative_to_workspace,
    is_outside_workspace,
    is_source_path,
    normalize_path_text,
    relative_to_workspace,
    stage_relative_forms,
)
from stage_git import _is_shell_redirection, iter_git_commands  # noqa: E402
import stage_topology  # noqa: E402
from stage_record_paths import (  # noqa: E402
    hierarchy_parent_record_path,
    record_paths,
    work_record_scale,
)


WORK_OPEN_STATUSES = {"active", "review", "blocked"}
WORK_FINAL_STATUSES = {"completed", "archived", "rejected"}
# Planned work cards (DE-00000007) live in future/backlog/items/ and move to
# present/work/items/ when work starts — one W card per piece of work across
# its whole life. `rejected` may also appear on a planned card (decided not to
# do before any work started).
WORK_PLANNED_STATUSES = {"captured", "triaged", "ready", "selected", "deferred", "rejected"}
VERIFICATION_DONE = {"passed", "not_required"}
RETROSPECTIVE_DONE = {"completed"}
PROMOTION_FINAL = {"approved", "promoted", "deferred", "not_applicable", "rejected"}

# Full valid enum sets: open/final plus the single in-progress value. The audit
# derives the identical sets; the PreToolUse enum gate imports THESE so a write
# the gate allows is one the audit accepts (one owning definition — SSOT).
STATUS_VALUES = WORK_OPEN_STATUSES | WORK_FINAL_STATUSES
# Decision records: `open` means undecided; work depending on one must not
# complete (DE-00000005). Final decision states that can carry authority:
DECISION_FINAL_STATUSES = {"decided", "promoted"}
# Machine-readable authorization a decision must declare (frontmatter
# `authorizes:`) to excuse a venue-policy exception. One contract shared by
# the registration CLI and the audit.
VENUE_EXCEPTION_AUTHORIZATION = "venue_exception"
# Reserved venue_routing value marking a kind as mixed-by-definition: it must
# split into design/implementation items instead of registering as one.
VENUE_SPLIT_TOKEN = "split"
VERIFICATION_VALUES = VERIFICATION_DONE | {"pending"}
RETROSPECTIVE_VALUES = RETROSPECTIVE_DONE | {"pending"}
PROMOTION_VALUES = PROMOTION_FINAL | {"pending"}
# Review is OPTIONAL: an item that never asks for it (absent -> defaulted
# not_required) completes without any review. Declaring `review: pending` opts
# THAT item in — it then cannot complete until `review: passed`. Same shape as
# verification, but bypassed by default.
REVIEW_DONE = {"passed", "not_required"}
REVIEW_VALUES = REVIEW_DONE | {"pending"}
_WORK_ENUM_FIELDS = (
    ("status", STATUS_VALUES),
    ("verification", VERIFICATION_VALUES),
    ("retrospective", RETROSPECTIVE_VALUES),
    ("promotion", PROMOTION_VALUES),
    ("review", REVIEW_VALUES),
)
WORK_ITEMS_PREFIX = ".stage/present/work/items/"


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
    venue: str = ""
    parent: str = ""
    review: str = "not_required"
    autonomous: bool = False
    acceptance: tuple[str, ...] = ()


def parse_yaml_string(value: str) -> str:
    """Parse the quoted scalar subset used by Stage's string-list fields."""

    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
        return parsed if isinstance(parsed, str) else value
    if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def parse_string_list(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(entry for entry in value if isinstance(entry, str) and entry.strip())


def parse_bool_field(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.strip().lower() == "true")


def format_yaml_string_list(values: tuple[str, ...] | list[str]) -> str:
    """Serialize strings as the JSON-compatible subset of YAML."""

    if not values:
        return "[]"
    return "\n" + "\n".join(
        f"  - {json.dumps(value, ensure_ascii=False)}" for value in values
    )


def parse_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    fields: dict[str, Any] = {}
    sequence_key = ""
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if sequence_key and line.startswith("- "):
            current = fields.get(sequence_key)
            if not isinstance(current, list):
                current = []
                fields[sequence_key] = current
            current.append(parse_yaml_string(line[2:].strip()))
            continue
        sequence_key = ""
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            fields[key] = ""
            sequence_key = key
        elif value == "[]":
            fields[key] = []
        else:
            fields[key] = parse_yaml_string(value)
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
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        root = stage_topology.card_location_for_status("active")
        return load_items_from(stage_root / root)
    return load_items_from(stage_root / "present" / "work" / "items")


def load_archive_work_items(stage_root: Path) -> list[WorkItem]:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        root = stage_topology.card_location_for_status("archived")
        return load_items_from(stage_root / root)
    return load_items_from(stage_root / "past" / "work" / "archive" / "items")


def load_planned_work_items(stage_root: Path) -> list[WorkItem]:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        root = stage_topology.get_zone("work", "planned").canonical_path
        return load_items_from(stage_root / root)
    return load_items_from(stage_root / "future" / "backlog" / "items")


def load_all_work_items(stage_root: Path) -> list[WorkItem]:
    """Load work cards from every lifecycle zone for hierarchy aggregation."""

    return (
        load_work_items(stage_root)
        + load_planned_work_items(stage_root)
        + load_archive_work_items(stage_root)
    )


# The one frontmatter->WorkItem constructor, with the missing-field policy an
# explicit argument: enforcement reads absent lifecycle fields as safe
# progress (a sparse item must not crash or over-deny a gate), while the
# audit keeps them empty so its enum checks fire. Both policies are pinned
# (hooks: WorkItemDefaultsTest; scripts: audit-defaults test).
GATE_FIELD_DEFAULTS = {
    "status": "active",
    "verification": "pending",
    "retrospective": "pending",
    "promotion": "pending",
}
AUDIT_FIELD_DEFAULTS = {
    "status": "",
    "verification": "",
    "retrospective": "",
    "promotion": "",
}


def item_from_fields(
    path: Path,
    fields: dict[str, Any],
    defaults: dict[str, str],
    *,
    items_root: Path | None = None,
) -> WorkItem:
    def scalar(name: str) -> str:
        value = fields.get(name)
        return value if isinstance(value, str) else ""

    parent = scalar("parent").strip()
    if items_root is not None:
        try:
            work_record_scale(items_root, path)
        except ValueError:
            parent = ""
        else:
            parent = ""
            parent_path = hierarchy_parent_record_path(items_root, path)
            if parent_path is not None:
                if parent_path.is_file():
                    parent_fields = parse_frontmatter(parent_path)
                    parent_value = parent_fields.get("id")
                    if isinstance(parent_value, str):
                        parent = parent_value.strip()
                if not parent:
                    parent = parent_path.parent.name

    return WorkItem(
        path=path,
        item_id=scalar("id") or path.stem,
        title=scalar("title") or path.stem,
        status=(scalar("status") or defaults["status"]).lower(),
        verification=(scalar("verification") or defaults["verification"]).lower(),
        retrospective=(scalar("retrospective") or defaults["retrospective"]).lower(),
        promotion=(scalar("promotion") or defaults["promotion"]).lower(),
        scope=split_scope(scalar("scope")),
        promotes=split_scope(scalar("promotes")),
        retrospective_ref=scalar("retrospective_ref").strip(),
        kind=scalar("kind").strip().lower(),
        venue=scalar("venue").strip().lower(),
        parent=parent,
        review=(scalar("review") or "not_required").strip().lower(),
        autonomous=parse_bool_field(fields.get("autonomous")),
        acceptance=parse_string_list(fields.get("acceptance")),
    )


def load_items_from(items_root: Path) -> list[WorkItem]:
    if not items_root.exists():
        return []

    items: list[WorkItem] = []
    for path in record_paths(items_root):
        if path.name in {"README.md", "_template.md", "index.md"}:
            continue
        items.append(
            item_from_fields(
                path,
                parse_frontmatter(path),
                GATE_FIELD_DEFAULTS,
                items_root=items_root,
            )
        )
    return items


def item_is_open(item: WorkItem) -> bool:
    return item.status in WORK_OPEN_STATUSES


def item_is_completed(item: WorkItem) -> bool:
    return item.status == "completed"


def non_terminal_children(parent_id: str, items: list[WorkItem]) -> list[WorkItem]:
    """Return direct children whose outcome is not final, in deterministic order."""

    return sorted(
        (
            item
            for item in items
            if item.parent == parent_id and item.status not in WORK_FINAL_STATUSES
        ),
        key=lambda item: (item.item_id, item.path.as_posix()),
    )


def children_are_terminal(parent_id: str, items: list[WorkItem]) -> bool:
    """Whether every direct child is final; leaves satisfy the query vacuously."""

    return not non_terminal_children(parent_id, items)


def parent_completion_blockers(parent_id: str, items: list[WorkItem]) -> list[str]:
    children = non_terminal_children(parent_id, items)
    if not children:
        return []
    detail = ", ".join(f"{child.item_id} (`{child.status}`)" for child in children)
    return [f"{parent_id}: non-terminal children block completion: {detail}"]


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
        if item.autonomous and item.review != "passed":
            blockers.append(
                f"{item.item_id}: independent review `{item.review}` "
                "(autonomous work must reach passed)"
            )
        elif item.review not in REVIEW_DONE:
            blockers.append(
                f"{item.item_id}: review `{item.review}` "
                "(declared review must reach passed)"
            )
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
    if active_topology(workspace_root / ".stage") == ACTIVE_TOPOLOGY_V4:
        prefix = f".stage/{stage_topology.card_location_for_status('archived')}/"
    else:
        prefix = ".stage/past/work/archive/items/"
    if not relative.startswith(prefix):
        return ""
    archive_relative = Path(relative[len(prefix) :])
    parts = archive_relative.parts
    name = archive_relative.name
    if len(parts) == 1 and name.lower().endswith(".md"):
        return name[:-3]
    if name == stage_topology.EPIC_RECORD_NAME and len(parts) == 2:
        return archive_relative.parent.name
    if name == stage_topology.STORY_RECORD_NAME and len(parts) in {2, 3}:
        return archive_relative.parent.name
    if name.lower().endswith(".md") and not name.startswith("_") and len(parts) in {2, 3}:
        return name[:-3]
    return ""


def archive_target_retro_id(path: str, workspace_root: Path) -> str:
    relative = entry_relative_to_workspace(path, workspace_root)
    if active_topology(workspace_root / ".stage") == ACTIVE_TOPOLOGY_V4:
        _, archive_root = stage_topology.retrospective_locations()
        prefix = f".stage/{archive_root}/"
    else:
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


def resolve_decision_record(stage_root: Path, ref: str) -> Path:
    """Owning file for a decision reference: DE-* records live in
    present/work/decisions, promoted D-* records in past/decisions/records."""
    name = ref if ref.endswith(".md") else f"{ref}.md"
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        artifact_id = Path(name).stem
        reference = stage_topology.resolve_artifact_reference(artifact_id)
        candidates = tuple(stage_root / path for path in reference.candidate_paths)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]
    if ref.startswith("D-"):
        return stage_root / "past" / "decisions" / "records" / name
    return stage_root / "present" / "work" / "decisions" / name


def decision_status(stage_root: Path, ref: str) -> str:
    """The decision's frontmatter status, or '' when the record is unreadable."""
    fields = parse_frontmatter(resolve_decision_record(stage_root, ref))
    return (fields.get("status") or "").strip()


def venue_exception_error(stage_root: Path, ref: str) -> str:
    """'' when `ref` names a decision that validly authorizes a venue-policy
    exception (DE-00000005): the record exists, its status is final
    (decided/promoted), and it declares `authorizes: venue_exception`.
    Otherwise the human-readable reason. The work_item back-link is validated
    by the audit, which knows the allocated item id."""
    path = resolve_decision_record(stage_root, ref)
    fields = parse_frontmatter(path)
    if not fields:
        return f"decision {ref} not found or unreadable at {path.name}"
    status = (fields.get("status") or "").strip()
    if status not in DECISION_FINAL_STATUSES:
        return (
            f"decision {ref} has status `{status or 'missing'}`; a venue exception needs "
            f"one of {sorted(DECISION_FINAL_STATUSES)}"
        )
    if (fields.get("authorizes") or "").strip() != VENUE_EXCEPTION_AUTHORIZATION:
        return (
            f"decision {ref} does not declare `authorizes: {VENUE_EXCEPTION_AUTHORIZATION}`"
        )
    return ""


def fallback_index_blockers(stage_root: Path) -> list[str]:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        active_path, review_path = stage_topology.get_zone("work", "current").index_surfaces
        active = parse_index_rows(stage_root / active_path)
        review = parse_index_rows(stage_root / review_path)
    else:
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

    current_items = load_work_items(stage_root)
    if not current_items:
        return fallback_index_blockers(stage_root)

    all_items = load_all_work_items(stage_root)

    blockers: list[str] = []
    for item in current_items:
        blockers.extend(item_completion_blockers(item))
        if item_is_completed(item):
            blockers.extend(parent_completion_blockers(item.item_id, all_items))
    return blockers


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
    if active_topology(workspace_root / ".stage") == ACTIVE_TOPOLOGY_V4:
        current_root = stage_topology.card_location_for_status("active")
        return (
            "Stage registration gate violation: before modifying governed files, establish a story "
            "first, then register an active work item with a matching scope in "
            f"`.stage/{current_root}/`. "
            "Unregistered targets: " + ", ".join(uncovered[:5])
        )
    return (
        "Stage registration gate violation: before modifying governed files, establish a story "
        "first, then register an active work item with a matching scope in "
        "`.stage/present/work/items/`. "
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


def git_add_paths_from_command(command: str, workspace_root: Path) -> list[str]:
    paths: list[str] = []
    for subcommand, args in iter_git_commands(command):
        if subcommand != "add":
            continue
        explicit: list[str] = []
        for arg in args:
            if _is_shell_redirection(arg):
                break
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


def frontmatter_field_from_text(text: str, field: str) -> str:
    # [ \t]* (not \s*): \s crosses the newline after an empty `field:` line and
    # would capture the NEXT line as the value (e.g. empty `parent:` followed by
    # `source:` read back as parent="source:" — a false hierarchy deny).
    match = re.search(rf"^{re.escape(field)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def _is_planned_card_path(relative: str) -> bool:
    """True when ``relative`` (a ``.stage/...`` form) is a planned work card.

    Planned cards (work/planned zone) carry the PLANNED status enum, not the
    current-work enum — the same split the audit makes (BACKLOG001 vs WORK005).
    """
    if not relative:
        return False
    planned = stage_topology.resolve_artifact_reference("W-00000000").candidate_paths[0]
    return relative.startswith(f".stage/{Path(planned).parent.as_posix()}/")


def work_item_enum_error(text: str, relative: str = "") -> str:
    """A non-empty work-item enum field whose value is invalid, or '' if all valid.

    Empty fields are not flagged (absence is the audit's and other gates' concern);
    this catches a wrong VALUE — the `retrospective: not_required` / `status: done`
    class of typo that the audit would only surface later, after the write landed.

    ``relative`` selects the status enum by zone: a planned card validates status
    against WORK_PLANNED_STATUSES (triaged/ready/...), a current/archive card
    against STATUS_VALUES. The other fields never appear on a planned card (absent
    -> skipped), so one field table serves both.
    """
    status_valid = WORK_PLANNED_STATUSES if _is_planned_card_path(relative) else STATUS_VALUES
    enum_fields = (("status", status_valid),) + _WORK_ENUM_FIELDS[1:]
    for field_name, valid in enum_fields:
        value = frontmatter_field_from_text(text, field_name)
        if value and value not in valid:
            return (
                f"Stage enum gate violation: work item `{field_name}: {value}` is not one of "
                f"{sorted(valid)}."
            )
    return ""


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

    # A tool outside the built-in names that carries a whole-file `content`
    # and no replacement pairs (a registered extra write tool) is a full
    # write — projecting it as a no-op would hide its post-state from the
    # hierarchy gate.
    if not replacements:
        content = data.get("content")
        if isinstance(content, str):
            return content

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



def work_item_relative(raw: str, workspace_root: Path) -> str:
    """Work-item relative path if any form names a governed W-card location."""
    if active_topology(workspace_root / ".stage") == ACTIVE_TOPOLOGY_V4:
        prefixes = tuple(
            f".stage/{Path(relative).parent.as_posix()}/"
            for relative in stage_topology.resolve_artifact_reference(
                "W-00000000"
            ).candidate_paths
        )
    else:
        prefixes = (WORK_ITEMS_PREFIX,)
    for form in stage_relative_forms(raw, workspace_root):
        if any(form.startswith(prefix) for prefix in prefixes):
            return form
    return ""
