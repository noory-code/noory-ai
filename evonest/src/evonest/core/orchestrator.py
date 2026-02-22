"""Main cycle loop — the evolution engine.

Orchestrates: Meta-observe → Mutation selection → Observe → Plan → Execute → Verify
for each cycle. Tracks progress, archives history, handles git checkpoints.
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evonest.core import claude_runner
from evonest.core.backlog import prune
from evonest.core.config import EvonestConfig
from evonest.core.lock import EvonestLock
from evonest.core.meta_observe import apply_meta_results, build_meta_prompt, should_run_meta
from evonest.core.mutations import select_mutation
from evonest.core.notify import notify
from evonest.core.phases import _gather_static_context, run_execute, run_observe, run_plan, run_verify
from evonest.core.progress import recalculate_weights, update_progress
from evonest.core.scout import apply_scout_results, build_scout_prompt, should_run_scout
from evonest.core.state import ProjectState

logger = logging.getLogger("evonest")


@dataclass
class CycleResult:
    """Result from a single evolution cycle."""

    cycle_num: int
    success: bool
    persona_id: str
    persona_name: str
    adversarial_id: str | None
    duration_seconds: int
    commit_message: str
    changed_files: list[str]
    skipped_reason: str | None = None


async def run_analyze(
    project: str,
    persona_id: str | None = None,
    adversarial_id: str | None = None,
    group: str | None = None,
    all_personas: bool = False,
    observe_mode: str | None = None,
    level: str | None = None,
) -> str:
    """Run Observe-only pass, saving ALL improvements to proposals/.

    No Plan, Execute, or Verify phases are run.
    No backlog storage: every improvement item becomes a proposal.
    Returns a summary string.
    """
    config = EvonestConfig.load(project)
    if level is not None:
        config.active_level = level
        config._apply_level(level)
    if observe_mode is not None:
        config.observe_mode = observe_mode

    state = ProjectState(project)
    state.ensure_dirs()

    file_count = _count_source_files(project)
    config.max_turns.observe = max(
        config.observe_turns_min_quick,
        int(file_count * config.observe_turns_quick_ratio),
    )
    config.max_turns.observe_deep = max(
        config.observe_turns_min_deep,
        int(file_count * config.observe_turns_deep_ratio),
    )

    # Build persona sweep queue if --all-personas requested
    persona_queue: list[str] | None = None
    if all_personas:
        from evonest.core.mutations import load_personas

        persona_queue = [p["id"] for p in load_personas(state)]

    total = len(persona_queue) if persona_queue is not None else 1
    saved_total = 0

    state.log(f"Evonest analyze starting ({total} persona(s))")

    # Gather static context once — shared across all personas to avoid redundant LLM tool calls
    static_context = _gather_static_context(project, config)
    if static_context:
        state.log(f"  [Analyze] Static context gathered ({len(static_context)} chars)")

    with EvonestLock(state.lock_path):
        for i in range(total):
            effective_persona_id = persona_queue[i] if persona_queue is not None else persona_id

            mutation = select_mutation(
                state,
                config.adversarial_probability,
                config,
                persona_id=effective_persona_id,
                adversarial_id=adversarial_id,
                group=group,
            )

            progress = state.read_progress()
            total_so_far = progress.get("total_cycles", 0)
            if config.observe_mode == "deep":
                deep_observe = True
            elif config.observe_mode == "quick":
                deep_observe = False
            else:
                deep_observe = (
                    config.deep_cycle_interval > 0
                    and total_so_far > 0
                    and total_so_far % config.deep_cycle_interval == 0
                )

            state.log(f"  [Analyze {i + 1}/{total}] persona={mutation['persona_name']}")
            result = run_observe(
                state, config, mutation,
                deep=deep_observe, analyze_mode=True,
                static_context=static_context,
            )

            if result.success:
                count = result.metadata.get("proposals_saved", 0)
                saved_total += count
                state.log(f"  [Analyze] {count} proposals saved")
            else:
                stderr_detail = f" stderr: {result.stderr[:200]}" if result.stderr else ""
                state.log(f"  [Analyze] Observe failed.{stderr_detail}")

    summary = f"Analyze complete: {saved_total} proposals saved from {total} persona(s)"
    state.log(summary)
    return summary


async def run_cycles(
    project: str,
    cycles: int | None = None,
    dry_run: bool = False,
    no_meta: bool = False,
    no_scout: bool = False,
    observe_mode: str | None = None,
    persona_id: str | None = None,
    adversarial_id: str | None = None,
    group: str | None = None,
    all_personas: bool = False,
    cautious: bool = False,
    resume: bool | None = None,
    level: str | None = None,
) -> str:
    """Run N evolution cycles on a project.

    Args:
        cautious: If True, pause after Plan and return plan summary for review.
                  Call again with resume=True to proceed or resume=False to cancel.
        resume: True = resume a paused cautious session; False = cancel it;
                None = normal run (no pending state interaction).

    Returns a summary string of the run.
    """
    # Handle resume/cancel for cautious mode
    if resume is True:
        return await _resume_cautious(project)

    if resume is False and _has_pending(project):
        state_tmp = ProjectState(project)
        state_tmp.clear_pending()
        return "Cautious evolve cancelled. No changes made."

    # Deprecate --dry-run: redirect to run_analyze
    if dry_run:
        import warnings

        warnings.warn(
            "--dry-run is deprecated. Use `evonest analyze` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        _state_dep = ProjectState(project)
        _state_dep.log("WARNING: --dry-run is deprecated. Redirecting to analyze mode.")
        return await run_analyze(
            project=project,
            persona_id=persona_id,
            adversarial_id=adversarial_id,
            group=group,
            all_personas=all_personas,
            observe_mode=observe_mode,
        )
    config = EvonestConfig.load(project, dry_run=dry_run)
    if level is not None:
        config.active_level = level
        config._apply_level(level)
    if cycles is not None:
        config.max_cycles_per_run = cycles
    if observe_mode is not None:
        config.observe_mode = observe_mode

    state = ProjectState(project)
    state.ensure_dirs()
    proj_name = Path(project).name

    # Dynamically compute observe max_turns based on project file count
    # Use git ls-files to respect .gitignore (excludes .venv, node_modules, etc.)
    file_count = _count_source_files(project)
    config.max_turns.observe = max(
        config.observe_turns_min_quick,
        int(file_count * config.observe_turns_quick_ratio),
    )
    config.max_turns.observe_deep = max(
        config.observe_turns_min_deep,
        int(file_count * config.observe_turns_deep_ratio),
    )

    # Build persona sweep queue if --all-personas requested
    persona_queue: list[str] | None = None
    if all_personas:
        from evonest.core.mutations import load_personas

        _state_tmp = ProjectState(project)
        persona_queue = [p["id"] for p in load_personas(_state_tmp)]
        config.max_cycles_per_run = len(persona_queue)

    total_cycles = config.max_cycles_per_run
    completed = 0
    results: list[CycleResult] = []

    state.log(
        f"Evonest starting ({total_cycles} cycles, model={config.model}, "
        f"dry_run={config.dry_run}, files={file_count})"
    )

    proj_name = Path(project).resolve().name

    # Gather static context once — reused across all cycles/personas
    static_context = _gather_static_context(project, config)
    if static_context:
        state.log(f"  Static context gathered ({len(static_context)} chars)")

    with EvonestLock(state.lock_path):
        for cycle in range(1, total_cycles + 1):
            state.log(f"=== Cycle {cycle}/{total_cycles} ===")
            cycle_start = time.time()

            # --- Meta-observe check ---
            if not no_meta and not config.dry_run:
                progress = state.read_progress()
                if should_run_meta(progress, config):
                    state.log("  [META] Running meta-observe...")
                    _run_meta_observe(state, config)

            # --- Scout check (external search) ---
            if not no_scout and not config.dry_run:
                progress = state.read_progress()
                if should_run_scout(progress, config):
                    state.log("  [SCOUT] Running external scout...")
                    _run_scout(state, config)

            # --- Select mutation ---
            effective_persona_id = (
                persona_queue[cycle - 1] if persona_queue is not None else persona_id
            )
            mutation = select_mutation(
                state,
                config.adversarial_probability,
                config,
                persona_id=effective_persona_id,
                adversarial_id=adversarial_id,
                group=group,
            )
            state.log(
                f"  Mutation: persona={mutation['persona_name']} "
                f"({mutation['persona_id']}), "
                f"adversarial={mutation.get('adversarial_name') or 'none'}"
            )

            # --- Phase 1: Observe ---
            progress = state.read_progress()
            total_so_far = progress.get("total_cycles", 0)
            if config.observe_mode == "deep":
                deep_observe = True
            elif config.observe_mode == "quick":
                deep_observe = False
            else:  # "auto"
                deep_observe = (
                    config.deep_cycle_interval > 0
                    and total_so_far > 0
                    and total_so_far % config.deep_cycle_interval == 0
                )
            observe_turns = (
                config.max_turns.observe_deep if deep_observe else config.max_turns.observe
            )
            mode_label = "deep" if deep_observe else "quick"
            state.log(f"  [1/4] Observe ({mode_label}, max_turns={observe_turns})...")
            observe_result = run_observe(
                state, config, mutation,
                deep=deep_observe,
                static_context=static_context,
            )
            if not observe_result.success:
                stderr_detail = (
                    f" stderr: {observe_result.stderr[:300]}" if observe_result.stderr else ""
                )
                state.log(f"  ERROR: Observe produced no output. Skipping cycle.{stderr_detail}")
                notify(f"Evonest [{proj_name}] — ⚠️ Skipped", "Observe produced no output")
                update_progress(
                    state, False, mutation["persona_id"], mutation["adversarial_id"], []
                )
                _record_cycle(state, cycle, cycle_start, False, mutation, [], "")
                continue

            state.log(f"  Observe complete ({len(observe_result.output)} bytes)")
            notify(f"Evonest [{proj_name}] — Observe ✓", "→ Plan 단계로")

            # --- Phase 2: Plan ---
            state.log("  [2/4] Plan...")
            plan_result = run_plan(state, config)
            if not plan_result.success:
                stderr_detail = f" stderr: {plan_result.stderr[:300]}" if plan_result.stderr else ""
                state.log(f"  ERROR: Plan produced no output. Skipping cycle.{stderr_detail}")
                notify(f"Evonest [{proj_name}] — ⚠️ Skipped", "Plan produced no output")
                update_progress(
                    state, False, mutation["persona_id"], mutation["adversarial_id"], []
                )
                _record_cycle(state, cycle, cycle_start, False, mutation, [], "")
                continue

            if plan_result.metadata.get("no_improvements"):
                state.log("  No improvements needed. Stopping.")
                break

            state.log(f"  Plan complete ({len(plan_result.output)} bytes)")
            notify(f"Evonest [{proj_name}] — Plan ✓", "→ Execute 단계로")

            # --- Cautious mode: pause after Plan ---
            if cautious:
                plan_summary = plan_result.output[:500]
                pending_data = {
                    "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "project": str(state.project),
                    "cycle": cycle,
                    "mutation": {
                        "persona_id": mutation["persona_id"],
                        "persona_name": mutation["persona_name"],
                        "adversarial_id": mutation.get("adversarial_id"),
                    },
                    "plan_summary": plan_summary,
                    "plan_path": str(state.plan_path),
                    "config_snapshot": {
                        "model": config.model,
                        "code_output": config.code_output,
                    },
                    "status": "waiting_for_confirmation",
                }
                state.write_pending(pending_data)
                state.log("  [Cautious] Paused after Plan. Awaiting confirmation.")
                return (
                    f"CAUTIOUS MODE: Paused after Plan phase.\n\n"
                    f"Persona: {mutation['persona_name']}\n\n"
                    f"Plan summary:\n{plan_summary}\n\n"
                    f"To proceed: call evonest_evolve(project=..., resume=True)\n"
                    f"To cancel:  call evonest_evolve(project=..., resume=False)"
                )

            # --- Phase 3: Execute (skip if dry-run) ---
            if config.dry_run:
                state.log("  [3/4] Execute: SKIPPED (dry run)")
                state.log("  [4/4] Verify: SKIPPED (dry run)")
                update_progress(state, True, mutation["persona_id"], mutation["adversarial_id"], [])
                completed += 1
                _recalculate(state, mutation)
                _record_cycle(state, cycle, cycle_start, True, mutation, [], "dry-run")
                results.append(
                    CycleResult(
                        cycle_num=cycle,
                        success=True,
                        persona_id=mutation["persona_id"],
                        persona_name=mutation["persona_name"],
                        adversarial_id=mutation["adversarial_id"],
                        duration_seconds=int(time.time() - cycle_start),
                        commit_message="",
                        changed_files=[],
                        skipped_reason="dry_run",
                    )
                )
                continue

            state.log("  [3/4] Execute...")

            # Git checkpoint
            _git_stash(state.project)

            execute_result = run_execute(state, config, mutation.get("decisions_section", ""))
            state.log(f"  Execute complete ({len(execute_result.output)} bytes)")
            notify(f"Evonest [{proj_name}] — Execute ✓", "→ Verify 단계로")

            # --- Phase 4: Verify ---
            state.log("  [4/4] Verify...")
            verify = run_verify(state, config, cycle)

            if verify.overall and verify.changed_files:
                # Success — commit or PR
                state.log(f"  PASS: {verify.commit_message}")
                notify(f"Evonest [{proj_name}] — ✅ PASS", verify.commit_message[:80])
                if config.code_output == "pr":
                    branch = f"evonest/cycle-{cycle}-{mutation['persona_id']}"
                    _git_commit_pr(state.project, verify.commit_message, branch, state, mutation)
                else:
                    _git_commit(state.project, verify.commit_message)
                _git_stash_drop(state.project)
                completed += 1

                update_progress(
                    state,
                    True,
                    mutation["persona_id"],
                    mutation["adversarial_id"],
                    verify.changed_files,
                )
                _recalculate(state, mutation)
                prune(state, state.read_progress().get("total_cycles", 0))
                _record_cycle(
                    state,
                    cycle,
                    cycle_start,
                    True,
                    mutation,
                    verify.changed_files,
                    verify.commit_message,
                )
                results.append(
                    CycleResult(
                        cycle_num=cycle,
                        success=True,
                        persona_id=mutation["persona_id"],
                        persona_name=mutation["persona_name"],
                        adversarial_id=mutation["adversarial_id"],
                        duration_seconds=int(time.time() - cycle_start),
                        commit_message=verify.commit_message,
                        changed_files=verify.changed_files,
                    )
                )

            elif verify.overall and not verify.changed_files:
                # No changes made
                state.log("  SKIP: No changes made. Dropping stash.")
                _git_stash_drop(state.project)
                update_progress(
                    state, False, mutation["persona_id"], mutation["adversarial_id"], []
                )
                _recalculate(state, mutation)
                _record_cycle(state, cycle, cycle_start, False, mutation, [], "")

            else:
                # Verification failed — revert
                state.log(f"  FAIL: {verify.notes} — Reverting.")
                notify(f"Evonest [{proj_name}] — ❌ FAIL", "Reverting changes...")
                _git_revert(state.project)
                update_progress(
                    state, False, mutation["persona_id"], mutation["adversarial_id"], []
                )
                _recalculate(state, mutation)
                _record_cycle(state, cycle, cycle_start, False, mutation, [], "")

            duration = int(time.time() - cycle_start)
            state.log(f"  Cycle {cycle} complete ({duration}s)")

    summary = f"Evonest complete: {completed}/{total_cycles} cycles succeeded"
    state.log(summary)
    return summary


def _run_meta_observe(state: ProjectState, config: EvonestConfig) -> None:
    """Run the meta-observe sub-phase."""
    prompt = build_meta_prompt(state, config)
    result = claude_runner.run(
        prompt,
        model=config.model,
        max_turns=config.max_turns.meta,
        allowed_tools=claude_runner.META_TOOLS,
        cwd=str(state.project),
    )

    state.write_text(state.meta_observe_path, result.output)

    if result.success:
        progress = state.read_progress()
        current_cycle = progress.get("total_cycles", 0)
        apply_meta_results(state, result.output, config, current_cycle)
        progress["last_meta_cycle"] = current_cycle
        state.write_progress(progress)
        state.log("  [META] Meta-observe complete")
    else:
        state.log("  [META] No output from meta-observe")


def _run_scout(state: ProjectState, config: EvonestConfig) -> None:
    """Run the scout sub-phase (external search-based mutation generation)."""
    prompt = build_scout_prompt(state)
    result = claude_runner.run(
        prompt,
        model=config.model,
        max_turns=config.max_turns.scout,
        allowed_tools=claude_runner.SCOUT_TOOLS,
        cwd=str(state.project),
    )

    state.write_text(state.root / "scout.txt", result.output)

    if result.success:
        progress = state.read_progress()
        current_cycle = progress.get("total_cycles", 0)
        summary = apply_scout_results(state, result.output, config, current_cycle)
        progress["last_scout_cycle"] = current_cycle
        state.write_progress(progress)
        state.log(
            f"  [SCOUT] Scout complete: {summary['findings_injected']} injected, "
            f"{summary['findings_skipped_score']} below threshold"
        )
    else:
        state.log("  [SCOUT] No output from scout")


def _recalculate(state: ProjectState, mutation: dict[str, Any]) -> None:
    """Recalculate weights for the personas/adversarials used."""
    from evonest.core.mutations import load_adversarials, load_personas

    personas = load_personas(state)
    adversarials = load_adversarials(state)
    recalculate_weights(
        state,
        [p["id"] for p in personas],
        [a["id"] for a in adversarials],
    )


def _record_cycle(
    state: ProjectState,
    cycle_num: int,
    start_time: float,
    success: bool,
    mutation: dict[str, Any],
    changed_files: list[str],
    commit_message: str,
) -> None:
    """Archive the cycle result to history."""
    duration = int(time.time() - start_time)
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = {
        "cycle": cycle_num,
        "success": success,
        "duration_seconds": duration,
        "timestamp": ts,
        "mutation": {
            "persona": mutation["persona_name"],
            "persona_id": mutation["persona_id"],
            "adversarial": mutation.get("adversarial_name"),
            "adversarial_id": mutation.get("adversarial_id"),
        },
        "improvement_title": commit_message or None,
        "commit_message": commit_message,
        "files_changed": changed_files,
    }
    progress = state.read_progress()
    total = progress.get("total_cycles", cycle_num)
    state.save_cycle_history(total, data)


# ── File counting ────────────────────────────────────────


def _count_source_files(project: str) -> int:
    """Count tracked Python source files, respecting .gitignore.

    Falls back to rglob excluding common non-source dirs if git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.py"],
            capture_output=True,
            text=True,
            cwd=project,
            timeout=15,
        )
        if result.returncode == 0:
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            return len(lines)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Fallback: rglob excluding common non-source directories
    exclude_dirs = {
        ".venv",
        "venv",
        "node_modules",
        ".git",
        "dist",
        "build",
        "__pycache__",
        ".tox",
        ".eggs",
        "*.egg-info",
    }
    count = 0
    for p in Path(project).rglob("*.py"):
        if not any(part in exclude_dirs for part in p.parts):
            count += 1
    return count


# ── Git helpers ──────────────────────────────────────────


def _git_stash(project: Path) -> None:
    try:
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        subprocess.run(
            ["git", "stash", "push", "-m", f"evonest-checkpoint-{ts}", "--quiet"],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        pass


def _git_stash_drop(project: Path) -> None:
    try:
        subprocess.run(
            ["git", "stash", "drop", "--quiet"],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        pass


def _git_commit(project: Path, message: str) -> None:
    try:
        subprocess.run(
            ["git", "add", "-A"],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
        full_msg = f"{message}\n\nCo-Authored-By: Evonest <noreply@evonest.dev>"
        subprocess.run(
            ["git", "commit", "-m", full_msg, "--quiet"],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        pass


def _pr_body(mutation: dict[str, Any] | None) -> str:
    persona = mutation.get("persona_name", "unknown") if mutation else "unknown"
    adversarial = mutation.get("adversarial_name") if mutation else None
    lines = [f"Automated improvement by Evonest.\n\nPersona: **{persona}**"]
    if adversarial:
        lines.append(f"Adversarial: **{adversarial}**")
    lines.append("\n---\n*Review and merge if this looks good.*")
    return "\n".join(lines)


def _git_commit_pr(
    project: Path,
    message: str,
    branch: str,
    state: ProjectState | None = None,
    mutation: dict[str, Any] | None = None,
) -> None:
    """Commit changes to a new branch and open a pull request via gh CLI."""
    try:
        # Get current branch to return to later
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(project),
            timeout=30,
        )
        base_branch = result.stdout.strip() or "main"

        # Create and switch to new branch
        subprocess.run(
            ["git", "checkout", "-b", branch],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )

        # Commit
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(project), timeout=30)
        full_msg = f"{message}\n\nCo-Authored-By: Evonest <noreply@evonest.dev>"
        subprocess.run(
            ["git", "commit", "-m", full_msg, "--quiet"],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )

        # Push
        push_proc = subprocess.run(
            ["git", "push", "-u", "origin", branch],
            capture_output=True,
            text=True,
            cwd=str(project),
            timeout=60,
        )
        if push_proc.returncode != 0:
            logger.warning(
                "git push failed (code %d): %s",
                push_proc.returncode,
                push_proc.stderr.strip()[:300] if push_proc.stderr else "(none)",
            )
            raise subprocess.SubprocessError("git push failed")

        # Create PR
        pr_proc = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                message,
                "--body",
                _pr_body(mutation),
                "--base",
                base_branch,
            ],
            capture_output=True,
            text=True,
            cwd=str(project),
            timeout=60,
        )
        if pr_proc.returncode != 0:
            logger.warning(
                "gh pr create failed (code %d): %s",
                pr_proc.returncode,
                pr_proc.stderr.strip()[:300] if pr_proc.stderr else "(none)",
            )
            raise subprocess.SubprocessError("gh pr create failed")

        # Return to base branch
        subprocess.run(
            ["git", "checkout", base_branch],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fallback to direct commit if gh or git fails
        logger.warning("PR creation failed — falling back to direct commit on current branch")
        if state is not None:
            state.log("  WARNING: PR creation failed — falling back to direct commit")
        _git_commit(project, message)


def _git_revert(project: Path) -> None:
    try:
        subprocess.run(
            ["git", "checkout", "."],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
        subprocess.run(
            ["git", "stash", "pop", "--quiet"],
            capture_output=True,
            cwd=str(project),
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        pass


# ── Cautious mode helpers ─────────────────────────────────


def _has_pending(project: str) -> bool:
    """Check if a cautious-mode pending session exists."""
    try:
        state = ProjectState(project)
        return state.pending_path.exists()
    except Exception:
        return False


async def _resume_cautious(project: str) -> str:
    """Resume a paused cautious evolve cycle (Execute + Verify + commit)."""
    state = ProjectState(project)
    pending = state.read_pending()
    if not pending:
        return "No paused cautious session found."

    config = EvonestConfig.load(project)

    snap = pending.get("config_snapshot", {})
    if snap.get("code_output"):
        config.code_output = snap["code_output"]

    cycle_num = pending.get("cycle", 1)
    mutation = pending.get("mutation", {})

    state.log(f"  [Cautious] Resuming cycle {cycle_num} (Execute + Verify)")
    cycle_start = time.time()

    _git_stash(state.project)

    execute_result = run_execute(state, config, "")
    state.log(f"  [Cautious] Execute complete ({len(execute_result.output)} bytes)")

    verify = run_verify(state, config, cycle_num)

    if verify.overall and verify.changed_files:
        state.log(f"  [Cautious] PASS: {verify.commit_message}")
        if config.code_output == "pr":
            branch = f"evonest/cycle-{cycle_num}-{mutation.get('persona_id', 'unknown')}"
            _git_commit_pr(state.project, verify.commit_message, branch, state, mutation)
        else:
            _git_commit(state.project, verify.commit_message)
        _git_stash_drop(state.project)
        state.clear_pending()
        duration = int(time.time() - cycle_start)
        return (
            f"Cautious evolve complete: {verify.commit_message}\n"
            f"Changed: {', '.join(verify.changed_files)}\n"
            f"Duration: {duration}s"
        )
    elif verify.overall and not verify.changed_files:
        _git_stash_drop(state.project)
        state.clear_pending()
        return "Cautious evolve: Execute succeeded but no files were changed."
    else:
        _git_revert(state.project)
        state.clear_pending()
        return f"Cautious evolve FAILED: {verify.notes}. Changes reverted."
