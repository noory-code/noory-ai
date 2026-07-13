# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
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
    path_targets_stage_archive,
)
import stage_roadmap  # noqa: E402
import stage_roadmap_closure  # noqa: E402
import stage_topology  # noqa: E402
from stage_work import (  # noqa: E402  (after sys.path bootstrap)
    RETROSPECTIVE_DONE,
    archive_target_item_id,
    archive_target_retro_id,
    item_completion_blockers,
    item_is_completed,
    item_promotes_path,
    load_archive_work_items,
    load_work_items,
    parse_frontmatter,
    retrospective_ref_id,
)


def runtime_slot_name(value: str) -> str:
    """Filesystem-safe slot name for per-session/per-item runtime files."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", value.strip())
    return cleaned or "default"


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
    restore_stale_claims(stage_root)
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


# A claim older than this belongs to a run whose PostToolUse never arrived
# (crash, rejected permission, a host without the event) — restore it for
# retry. Younger claims may belong to a tool still executing; restoring those
# early would double-spend the authorization.
CLAIM_RESTORE_AGE_SECONDS = 10 * 60


def restore_stale_claims(stage_root: Path) -> None:
    """Rename aged `*.json.claim-*` reservations back to pending intents. A
    re-planted intent under the original name is authoritative — the stale
    claim is dropped instead, so one authorization never becomes two."""
    now = datetime.now(timezone.utc).timestamp()
    try:
        claims = list(intents_root(stage_root).glob("*.json.claim-*"))
    except OSError:
        return
    for claim in claims:
        try:
            if now - claim.stat().st_mtime <= CLAIM_RESTORE_AGE_SECONDS:
                continue
            original = claim.with_name(claim.name.rsplit(".claim-", 1)[0])
            if original.exists():
                claim.unlink()
                continue
            try:
                data = json.loads(claim.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.pop("claimed_by", None) is not None:
                    claim.write_text(
                        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
            except (OSError, json.JSONDecodeError):
                pass
            claim.rename(original)
        except OSError:
            pass


def consume_claims_for(
    stage_root: Path, workspace_root: Path, target_paths: list[str], owner: str = ""
) -> None:
    """Complete the reservations whose declared paths were just written:
    PostToolUse confirms the tool ran, so the matching claims are consumed.

    Only claims stamped by the SAME owner (the reserving call's tool_use_id,
    or its session slot when the host sends none) are consumed — a re-planted
    intent claimed by a concurrent run keeps its own reservation, and its
    fate is decided by its own post or the age-based restore."""
    requested = {entry_relative_to_workspace(path, workspace_root) for path in target_paths}
    try:
        claims = list(intents_root(stage_root).glob("*.json.claim-*"))
    except OSError:
        return
    for claim in claims:
        try:
            data = json.loads(claim.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        claimed_by = str(data.get("claimed_by") or "")
        if claimed_by and owner and claimed_by != owner:
            continue
        declared = {
            entry_relative_to_workspace(path, workspace_root) for path in intent_paths(data)
        }
        if declared & requested:
            try:
                claim.unlink()
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


def promotion_blocker(
    workspace_root: Path, target_paths: list[str], claim_owner: str = ""
) -> str:
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
        try:
            # Rename preserves the intent's old mtime; the restore age must
            # measure from RESERVATION, or a long-planted intent's claim would
            # read as stale while its tool is still running (double-spend).
            claim.touch()
            if claim_owner:
                # Stamp who reserved it, so the completing post consumes only
                # its own claim (we own the file past the rename — no race).
                data = json.loads(claim.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data["claimed_by"] = claim_owner
                    claim.write_text(
                        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
        except (OSError, json.JSONDecodeError):
            pass
    # The claims are KEPT through tool execution: PostToolUse completes them
    # (consume_claims_for), and a claim whose post never arrives is restored
    # for retry after CLAIM_RESTORE_AGE_SECONDS (restore_stale_claims).
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
        # The archive index row carries the item's final status (the transition
        # evidence the `archived` overwrite erases), so the same intent may
        # update it alongside the item and retrospective moves.
        index_targets = [
            path
            for path in target_paths
            if entry_relative_to_workspace(path, workspace_root)
            == ".stage/past/work/archive/index.md"
        ]
        if len(item_targets) + len(retro_targets) + len(index_targets) != len(target_paths):
            return (
                "Stage archive gate violation: archive targets must be "
                "`items/<id>.md`, `retrospectives/<id>.md`, or the archive `index.md`."
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
        # Location-aware status rule: a present item archives only from a
        # closed terminal state; `archived` names a record already living in
        # the archive (maintenance edits), never a shortcut out of present.
        try:
            item.path.relative_to(stage_root / "past" / "work" / "archive" / "items")
            in_archive = True
        except ValueError:
            in_archive = False
        if in_archive:
            if item.status != "archived":
                return (
                    f"Stage archive gate violation: an archive-located work item must keep "
                    f"status archived. status `{item.status}`"
                )
        elif item.status not in {"completed", "rejected"}:
            return (
                f"Stage archive gate violation: work_item `{work_item_id}` status must be "
                f"completed/rejected. status `{item.status}`"
            )
        # Rejection reasons are learning assets: a rejected item records its
        # completed retrospective before archiving, like a completed one.
        if item.status == "rejected" and (
            item.retrospective not in RETROSPECTIVE_DONE or not item.retrospective_ref
        ):
            return (
                "Stage archive gate violation: a rejected item records its completed "
                f"retrospective (retrospective_ref) before archiving. retrospective `{item.retrospective}`"
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

    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        closure_error = closure_promotion_revalidation_blocker(
            stage_root, workspace_root, target_paths
        )
        if closure_error:
            return closure_error

    return ""


def closure_promotion_revalidation_blocker(
    stage_root: Path,
    workspace_root: Path,
    target_paths: list[str],
    overlays: dict[str, str | None] | None = None,
) -> str:
    """Fail closed before a closure decision enters the official zone."""

    pending_root = stage_topology.get_zone("decisions", "pending").canonical_path
    official_root = stage_topology.get_zone("decisions", "official").canonical_path
    official_prefix = f".stage/{official_root}/"
    for target in sorted(target_paths):
        relative = entry_relative_to_workspace(target, workspace_root)
        if not relative.startswith(official_prefix) or not relative.endswith(".md"):
            continue
        decision_id = Path(relative).stem
        if re.fullmatch(r"DE-\d{3,}", decision_id) is None:
            continue
        pending_path = stage_root / pending_root / f"{decision_id}.md"
        official_path = stage_root / official_root / f"{decision_id}.md"
        source = pending_path if pending_path.is_file() else official_path
        if not source.is_file():
            return (
                "Stage closure promotion revalidation denied: decision source "
                f"`{decision_id}` is missing, so the promotion type cannot be determined."
            )
        fields = parse_frontmatter(source)
        transition = (fields.get("transition") or "").strip().lower()
        if transition not in stage_roadmap.CLOSURE_TRANSITIONS:
            continue
        diffs = stage_roadmap_closure.closure_basis_diff(
            stage_root, source, overlays
        )
        if diffs:
            return (
                f"Stage closure promotion revalidation denied for {decision_id}:\n"
                + "\n".join(f"- {diff}" for diff in diffs)
            )
    return ""


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
