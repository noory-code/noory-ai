"""Agent subprocess runner for Claude Code and Codex.

All LLM invocations go through this module.
Tests can mock `run()` to avoid real subprocess calls.
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from evonest.core.process_manager import ProcessManager

logger = logging.getLogger("evonest")


@dataclass
class AgentResult:
    """Result from a Claude Code or Codex invocation."""

    output: str
    exit_code: int
    success: bool
    stderr: str = ""
    truncated_reason: str | None = None


# Backwards-compatible public name used by existing integrations and tests.
ClaudeResult = AgentResult


OBSERVE_TOOLS = "Read,Glob,Grep,Bash"
PLAN_TOOLS = "Read,Glob,Grep,Bash"
EXECUTE_TOOLS = "Read,Glob,Grep,Edit,Write,Bash"
META_TOOLS = "Read,Glob,Grep,Bash"
SCOUT_TOOLS = "Read,WebFetch,Bash"
BACKEND_ENV = "EVONEST_AGENT_BACKEND"
CODEX_MODEL_ENV = "EVONEST_CODEX_MODEL"
VALID_BACKENDS = {"claude", "codex"}


def _resolve_backend() -> str:
    backend = os.environ.get(BACKEND_ENV, "claude").strip().lower()
    if backend not in VALID_BACKENDS:
        allowed = ", ".join(sorted(VALID_BACKENDS))
        raise ValueError(f"{BACKEND_ENV} must be one of: {allowed}; got {backend!r}")
    return backend


def _run_claude(
    prompt: str,
    *,
    model: str,
    max_turns: int,
    allowed_tools: str,
    cwd: str | None,
    retry: bool,
) -> AgentResult:
    cmd = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "text",
        "--max-turns",
        str(max_turns),
        "--allowedTools",
        allowed_tools,
        "--no-session-persistence",
        "--dangerously-skip-permissions",
        "--setting-sources",
        "user",
    ]
    return _execute(cmd, backend="claude", cwd=cwd, retry=retry)


def _run_codex(
    prompt: str,
    *,
    allowed_tools: str,
    cwd: str | None,
    retry: bool,
) -> AgentResult:
    writable = "Edit" in allowed_tools or "Write" in allowed_tools
    sandbox = "danger-full-access" if writable else "read-only"

    with tempfile.TemporaryDirectory(prefix="evonest-codex-") as temp_dir:
        output_path = Path(temp_dir) / "last-message.txt"
        cmd = [
            "codex",
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "--color",
            "never",
            "--sandbox",
            sandbox,
            "--config",
            'approval_policy="never"',
            "--output-last-message",
            str(output_path),
        ]
        codex_model = os.environ.get(CODEX_MODEL_ENV, "").strip()
        if codex_model:
            cmd.extend(["--model", codex_model])
        cmd.append(prompt)

        result = _execute(cmd, backend="codex", cwd=cwd, retry=retry)
        if output_path.is_file():
            output = output_path.read_text(encoding="utf-8").strip()
            if output:
                return AgentResult(
                    output=output,
                    exit_code=result.exit_code,
                    success=result.exit_code == 0,
                    stderr=result.stderr,
                )
        return result


def _execute(
    cmd: list[str], *, backend: str, cwd: str | None, retry: bool
) -> AgentResult:
    logger.info("%s agent starting (cwd=%s)", backend, cwd)
    process_manager = ProcessManager(
        timeout=600.0, retry_on_rate_limit=True, rate_limit_wait=30.0, max_retries=3
    )
    result = process_manager.run(cmd, cwd=cwd, _retry_attempt=0 if retry else 999)

    max_turns_hit = backend == "claude" and result.output.startswith(
        "Error: Reached max turns"
    )
    if max_turns_hit:
        logger.warning(
            "claude -p reached max turns limit after %.1fs: %s",
            result.elapsed_seconds,
            result.output[:100],
        )

    return AgentResult(
        output=result.output,
        exit_code=result.exit_code,
        success=result.success and not max_turns_hit,
        stderr=result.stderr,
        truncated_reason="max_turns" if max_turns_hit else None,
    )


def run(
    prompt: str,
    *,
    model: str = "sonnet",
    max_turns: int = 25,
    allowed_tools: str = OBSERVE_TOOLS,
    cwd: str | None = None,
    _retry: bool = True,
) -> AgentResult:
    """Run the host-selected agent subprocess and return the result.

    Args:
        prompt: The prompt text to send.
        model: Claude model name. Codex uses its configured default unless
            ``EVONEST_CODEX_MODEL`` is set.
        max_turns: Maximum Claude agentic turns. Codex is bounded by the
            process timeout and the surrounding Evonest phase.
        allowed_tools: Claude tool allowlist and Codex read/write mode signal.
        cwd: Working directory for the subprocess.

    Returns:
        AgentResult with output text and exit status.
    """
    backend = _resolve_backend()
    if backend == "codex":
        return _run_codex(
            prompt,
            allowed_tools=allowed_tools,
            cwd=cwd,
            retry=_retry,
        )
    return _run_claude(
        prompt,
        model=model,
        max_turns=max_turns,
        allowed_tools=allowed_tools,
        cwd=cwd,
        retry=_retry,
    )
