"""Phase execution — Observe, Plan, Execute, Verify prompt assembly + runner.

Each phase function:
1. Assembles a prompt from template + context
2. Calls claude_runner.run()
3. Saves output to .evonest/
4. Returns a PhaseResult
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from importlib import resources
from typing import Any

from evonest.core import claude_runner
from evonest.core.backlog import build_context as build_backlog_context
from evonest.core.backlog import save_observations
from evonest.core.config import EvonestConfig
from evonest.core.history import build_history_summary
from evonest.core.progress import build_convergence_context
from evonest.core.state import ProjectState

logger = logging.getLogger("evonest")


# ── Static context gathering ──────────────────────────────


def _gather_static_context(project: str, config: EvonestConfig) -> str:
    """Collect deterministic project signals once and return as a markdown string.

    Gathers: recent git log, source file tree, and test list (collection only, no execution).
    This is injected into the Observe prompt so the LLM does not need to re-discover
    these facts via Bash tool calls — reducing turns and cost, especially with --all-personas.

    Silently skips any command that fails or times out.
    """
    sections: list[str] = []

    # 1. Recent git log (last 5 commits with stats)
    try:
        result = subprocess.run(
            ["git", "log", "--stat", "-5", "--oneline", "--", project],
            capture_output=True,
            text=True,
            cwd=project,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            sections.append(f"### Recent Git History\n\n```\n{result.stdout.strip()}\n```")
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # 2. Source file tree (tracked files, respects .gitignore)
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "."],
            capture_output=True,
            text=True,
            cwd=project,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            files = [
                line
                for line in result.stdout.splitlines()
                if line.strip() and not any(
                    pat in line
                    for pat in (".venv/", "node_modules/", "__pycache__/", ".mypy_cache/")
                )
            ]
            if files:
                file_list = "\n".join(files[:150])  # cap at 150 lines
                sections.append(f"### Source File Tree\n\n```\n{file_list}\n```")
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # 3. Test list (pytest --collect-only, no execution)
    test_cmd = config.verify.test or ""
    if test_cmd:
        # Derive pytest invocation from verify.test (e.g. "uv run pytest" → add --collect-only -q)
        # We attempt collection only — never run tests here.
        collect_args = test_cmd.split() + ["--collect-only", "-q", "--no-header"]
        try:
            result = subprocess.run(
                collect_args,
                capture_output=True,
                text=True,
                cwd=project,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().splitlines()
                test_lines = [l for l in lines if "::" in l][:100]  # cap at 100 test IDs
                if test_lines:
                    sections.append(
                        f"### Test Inventory ({len(test_lines)} tests)\n\n"
                        f"```\n{chr(10).join(test_lines)}\n```"
                    )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    if not sections:
        return ""

    return "## Pre-gathered Project Signals\n\n" + "\n\n".join(sections)


def _load_prompt(name: str) -> str:
    """Load a prompt template by name."""
    ref = resources.files("evonest") / "prompts" / f"{name}.md"
    try:
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return ""


@dataclass
class PhaseResult:
    """Result from a phase execution."""

    phase: str
    output: str
    success: bool
    skipped: bool = False
    stderr: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Observe ──────────────────────────────────────────────


def run_observe(
    state: ProjectState,
    config: EvonestConfig,
    mutation: dict[str, Any],
    *,
    deep: bool = False,
    analyze_mode: bool = False,
    static_context: str = "",
) -> PhaseResult:
    """Run the observe phase.

    Args:
        analyze_mode: If True, save ALL improvements as proposals (no backlog).
                      Used by `evonest analyze`. Default False (normal evolve behavior).
        static_context: Pre-gathered project signals (git log, file tree, test list)
                        injected into the prompt. Pass the output of
                        `_gather_static_context()` to avoid redundant LLM tool calls.
    """
    parts = [_load_prompt("observe_deep" if deep else "observe")]

    # Pre-gathered static context (injected before LLM exploration begins)
    if static_context:
        parts.append(f"\n---\n\n{static_context}")

    # Identity
    identity = state.read_identity()
    if identity:
        parts.append(f"\n---\n\n## Project Identity\n\n{identity}")

    # History context
    history = build_history_summary(state, count=5)
    if history:
        parts.append(f"\n---\n\n{history}")

    # Convergence warnings
    convergence = build_convergence_context(state)
    if convergence:
        parts.append(f"\n---\n\n{convergence}")

    # Advisor's guidance (from meta-observe guru)
    advice = state.read_advice()
    if advice and advice.get("strategic_direction"):
        advice_parts = [
            "\n---\n\n## Advisor's Guidance (from accumulated experience)\n",
            f"**Strategic direction**: {advice['strategic_direction']}",
        ]
        if advice.get("recommended_focus"):
            advice_parts.append(f"**Recommended focus**: {advice['recommended_focus']}")
        if advice.get("untapped_areas"):
            areas = ", ".join(advice["untapped_areas"])
            advice_parts.append(f"**Untapped areas**: {areas}")
        parts.append("\n".join(advice_parts))

    # Previous environment scan (avoid repeating known issues)
    env = state.read_environment()
    if env and env.get("items"):
        env_summary = json.dumps(env["items"][:10], indent=2)
        parts.append(
            f"\n---\n\n## Previous Environment Scan\n\n"
            f"Already reported (do not repeat):\n```json\n{env_summary}\n```"
        )

    # Persona perspective
    parts.append(
        f"\n---\n\n## Your Perspective This Cycle: {mutation['persona_name']}\n\n"
        f"{mutation['persona_text']}"
    )

    # Adversarial challenge
    if mutation.get("adversarial_section"):
        parts.append(f"\n---\n\n{mutation['adversarial_section']}")

    # External stimuli
    if mutation.get("stimuli_section"):
        parts.append(f"\n---\n\n{mutation['stimuli_section']}")

    # Human decisions
    if mutation.get("decisions_section"):
        parts.append(f"\n---\n\n{mutation['decisions_section']}")

    # Language instruction (only when non-English)
    if config.language.lower() != "english":
        parts.append(
            f"\n---\n\n## Language Instruction\n\n"
            f"Write ALL content — descriptions, observations, titles, rationale, "
            f"commit messages — in **{config.language}**. "
            f"Use {config.language} throughout your entire response."
        )

    prompt = "\n".join(parts)

    result = claude_runner.run(
        prompt,
        model=config.model,
        max_turns=config.max_turns.observe_deep if deep else config.max_turns.observe,
        allowed_tools=claude_runner.OBSERVE_TOOLS,
        cwd=str(state.project),
    )

    state.write_text(state.observe_path, result.output)

    if not result.success:
        return PhaseResult(
            phase="observe", output=result.output, success=False, stderr=result.stderr
        )

    if analyze_mode:
        count = _save_all_as_proposals(state, result.output, mutation["persona_id"], config)
        return PhaseResult(
            phase="observe",
            output=result.output,
            success=True,
            metadata={"proposals_saved": count},
        )

    # Save observations to backlog (normal evolve behavior)
    _save_observations_from_output(state, result.output, mutation["persona_id"], config)

    return PhaseResult(phase="observe", output=result.output, success=True)


def _save_observations_from_output(
    state: ProjectState,
    output: str,
    persona_id: str,
    config: EvonestConfig | None = None,
) -> None:
    """Extract improvements JSON from observe output and save to backlog.

    - "proposal" category items → saved to .evonest/proposals/ (not backlog)
    - "ecosystem" category items → cached in environment.json (also in backlog)
    - All other items → saved to backlog as usual
    """
    match = re.search(r"```json\s*\n(.*?)```", output, re.DOTALL)
    if not match:
        return
    try:
        data = json.loads(match.group(1))
        improvements = data.get("improvements", [])
        if not improvements:
            return

        progress = state.read_progress()
        cycle = progress.get("total_cycles", 0)

        # Separate proposals from regular improvements
        proposals = [imp for imp in improvements if imp.get("category") == "proposal"]
        regular = [imp for imp in improvements if imp.get("category") != "proposal"]

        # Save regular improvements to backlog
        if regular:
            save_observations(state, regular, persona_id, cycle)

        # Save proposals to .evonest/proposals/ (human review required)
        language = config.language if config else "english"
        for proposal in proposals:
            _save_proposal(state, proposal, persona_id, cycle, language=language)

        # Cache ecosystem items to environment.json
        eco_items = [imp for imp in regular if imp.get("category") == "ecosystem"]
        if eco_items:
            env = state.read_environment()
            existing = env.get("items", [])
            existing_ids = {e.get("id") for e in existing}
            for item in eco_items:
                if item.get("id") and item["id"] not in existing_ids:
                    existing.append(item)
            env["items"] = existing
            env["last_scan_cycle"] = cycle
            state.write_environment(env)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Observe: JSON extraction failed, improvements not saved")


def _save_all_as_proposals(
    state: ProjectState,
    output: str,
    persona_id: str,
    config: EvonestConfig | None = None,
) -> int:
    """Extract ALL improvements from observe output and save every one as a proposal.

    Used in analyze mode: no backlog, no category filtering — everything becomes a proposal.
    Returns count of proposals saved.
    """
    match = re.search(r"```json\s*\n(.*?)```", output, re.DOTALL)
    if not match:
        return 0
    try:
        data = json.loads(match.group(1))
        improvements = data.get("improvements", [])
        if not improvements:
            return 0

        progress = state.read_progress()
        cycle = progress.get("total_cycles", 0)
        language = config.language if config else "english"

        for imp in improvements:
            _save_proposal(state, imp, persona_id, cycle, language=language)

        return len(improvements)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Analyze: JSON extraction failed, proposals not saved")
        return 0


_PROPOSAL_LABELS: dict[str, dict[str, str]] = {
    "korean": {
        "heading": "제안",
        "priority": "우선순위",
        "persona": "작성 페르소나",
        "cycle": "사이클",
        "status": "상태",
        "status_value": "검토 대기",
        "description": "설명",
        "files": "관련 파일",
        "footer1": "*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  ",
        "footer2": "*팀에서 검토, 거부 또는 실행하세요.*",
    },
    "english": {
        "heading": "Proposal",
        "priority": "Priority",
        "persona": "From persona",
        "cycle": "Cycle",
        "status": "Status",
        "status_value": "pending review",
        "description": "Description",
        "files": "Relevant Files",
        "footer1": "*This is a design-level proposal. No code was changed.*  ",
        "footer2": "*Review, reject, or act on this as the team sees fit.*",
    },
}


def _save_proposal(
    state: ProjectState,
    proposal: dict[str, Any],
    persona_id: str,
    cycle: int,
    *,
    language: str = "english",
) -> None:
    """Save a business-logic proposal to .evonest/proposals/."""
    lbl = _PROPOSAL_LABELS.get(language.lower(), _PROPOSAL_LABELS["english"])

    title = proposal.get("title", "Untitled Proposal")
    description = proposal.get("description", "")
    priority = proposal.get("priority", "medium")
    files = proposal.get("files", [])

    lines = [
        f"# {lbl['heading']}: {title}",
        "",
        f"**{lbl['priority']}**: {priority}  ",
        f"**{lbl['persona']}**: {persona_id}  ",
        f"**{lbl['cycle']}**: {cycle}  ",
        f"**{lbl['status']}**: {lbl['status_value']}",
        "",
        f"## {lbl['description']}",
        "",
        description,
    ]
    if files:
        lines += ["", f"## {lbl['files']}", ""]
        lines += [f"- {f}" for f in files]

    lines += [
        "",
        "---",
        "",
        lbl["footer1"],
        lbl["footer2"],
    ]

    state.add_proposal("\n".join(lines))


# ── Plan ─────────────────────────────────────────────────


def run_plan(
    state: ProjectState,
    config: EvonestConfig,
) -> PhaseResult:
    """Run the plan phase."""
    observe_text = state.read_text(state.observe_path)
    if not observe_text:
        return PhaseResult(phase="plan", output="", success=False)

    parts = [_load_prompt("plan")]

    # Identity
    identity = state.read_identity()
    if identity:
        parts.append(f"\n---\n\n## Project Identity\n\n{identity}")

    # Backlog context
    backlog_ctx = build_backlog_context(state)
    if backlog_ctx:
        parts.append(f"\n---\n\n{backlog_ctx}")

    # Observations
    parts.append(f"\n---\n\n## Observations from Previous Phase\n\n{observe_text}")

    # Language instruction (only when non-English)
    if config.language.lower() != "english":
        parts.append(
            f"\n---\n\n## Language Instruction\n\n"
            f"Write ALL content — descriptions, plans, titles, rationale, "
            f"commit messages — in **{config.language}**. "
            f"Use {config.language} throughout your entire response."
        )

    prompt = "\n".join(parts)

    result = claude_runner.run(
        prompt,
        model=config.model,
        max_turns=config.max_turns.plan,
        allowed_tools=claude_runner.PLAN_TOOLS,
        cwd=str(state.project),
    )

    state.write_text(state.plan_path, result.output)

    if not result.success:
        return PhaseResult(phase="plan", output=result.output, success=False, stderr=result.stderr)

    # Check for "no improvements needed"
    if _plan_says_no_improvements(result.output):
        return PhaseResult(
            phase="plan",
            output=result.output,
            success=True,
            metadata={"no_improvements": True},
        )

    return PhaseResult(phase="plan", output=result.output, success=True)


def _plan_says_no_improvements(output: str) -> bool:
    """Check if plan output indicates no improvements are needed."""
    lower = output.lower()
    return any(
        phrase in lower
        for phrase in [
            "no improvements",
            "nothing to do",
            '"selected_improvement": null',
            '"selected_improvement":null',
        ]
    )


# ── Execute ──────────────────────────────────────────────


def run_execute(
    state: ProjectState,
    config: EvonestConfig,
    decisions_section: str = "",
) -> PhaseResult:
    """Run the execute phase."""
    plan_text = state.read_text(state.plan_path)
    if not plan_text:
        return PhaseResult(phase="execute", output="", success=False)

    parts = [_load_prompt("execute")]

    # Identity
    identity = state.read_identity()
    if identity:
        parts.append(f"\n---\n\n## Project Identity\n\n{identity}")

    # Plan
    parts.append(f"\n---\n\n## Plan to Execute\n\n{plan_text}")

    # Human decisions (if any remaining)
    if decisions_section:
        parts.append(f"\n## Human Decisions\n\n{decisions_section}")

    # Language instruction (only when non-English)
    if config.language.lower() != "english":
        parts.append(
            f"\n---\n\n## Language Instruction\n\n"
            f"Write ALL content — code comments, commit messages, summaries — "
            f"in **{config.language}**. "
            f"Use {config.language} throughout your entire response."
        )

    prompt = "\n".join(parts)

    result = claude_runner.run(
        prompt,
        model=config.model,
        max_turns=config.max_turns.execute,
        allowed_tools=claude_runner.EXECUTE_TOOLS,
        cwd=str(state.project),
    )

    state.write_text(state.execute_path, result.output)

    return PhaseResult(
        phase="execute", output=result.output, success=result.success, stderr=result.stderr
    )


# ── Verify ───────────────────────────────────────────────


@dataclass
class VerifyResult:
    """Result from the verify phase."""

    build_passed: bool
    test_passed: bool
    overall: bool
    changed_files: list[str]
    diff_stat: str
    commit_message: str
    notes: str


def run_verify(
    state: ProjectState,
    config: EvonestConfig,
    cycle_num: int,
) -> VerifyResult:
    """Run build + test commands and check git status."""
    build_passed = True
    test_passed = True
    notes_parts: list[str] = []

    # Build check
    if config.verify.build:
        try:
            proc = subprocess.run(
                config.verify.build,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(state.project),
                timeout=300,
            )
            if proc.returncode == 0:
                notes_parts.append("build: passed")
                state.log("    Build: PASSED")
            else:
                build_passed = False
                notes_parts.append("build: FAILED")
                state.log("    Build: FAILED")
                if proc.stderr:
                    state.log(f"    Build stderr: {proc.stderr.strip()[-500:]}")
        except subprocess.TimeoutExpired:
            build_passed = False
            notes_parts.append("build: FAILED (timeout)")
            state.log("    Build: FAILED (timeout)")

    # Test check
    if config.verify.test:
        try:
            proc = subprocess.run(
                config.verify.test,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(state.project),
                timeout=300,
            )
            if proc.returncode == 0:
                notes_parts.append("tests: passed")
                state.log("    Tests: PASSED")
            else:
                test_passed = False
                notes_parts.append("tests: FAILED")
                state.log("    Tests: FAILED")
                if proc.stderr:
                    state.log(f"    Tests stderr: {proc.stderr.strip()[-500:]}")
        except subprocess.TimeoutExpired:
            test_passed = False
            notes_parts.append("tests: FAILED (timeout)")
            state.log("    Tests: FAILED (timeout)")

    # Git status
    diff_stat = _git_diff_stat(state.project)
    changed_files = _git_changed_files(state.project)

    # Extract commit message from plan
    plan_text = state.read_text(state.plan_path)
    commit_message = _extract_commit_message(plan_text, cycle_num)

    overall = build_passed and test_passed
    return VerifyResult(
        build_passed=build_passed,
        test_passed=test_passed,
        overall=overall,
        changed_files=changed_files,
        diff_stat=diff_stat,
        commit_message=commit_message,
        notes=", ".join(notes_parts),
    )


def _git_diff_stat(project: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD", "--", str(project)],
            capture_output=True,
            text=True,
            cwd=str(project),
            timeout=30,
        )
        return result.stdout.strip() if result.returncode == 0 else "no changes"
    except (subprocess.SubprocessError, FileNotFoundError):
        return "no changes"


def _git_changed_files(project: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", str(project)],
            capture_output=True,
            text=True,
            cwd=str(project),
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f for f in result.stdout.strip().split("\n") if f]
        return []
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _extract_commit_message(plan_text: str, cycle_num: int) -> str:
    """Try to extract commit message from plan JSON output."""
    match = re.search(r'"commit_message"\s*:\s*"([^"]*)"', plan_text)
    if match and match.group(1):
        return match.group(1)
    return f"evolve: auto-improvement (cycle {cycle_num})"
