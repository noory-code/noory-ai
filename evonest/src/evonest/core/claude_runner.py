"""ClaudeRunner — subprocess wrapper for `claude -p` calls.

All LLM invocations go through this module.
Tests can mock `run()` to avoid real subprocess calls.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from evonest.core.process_manager import ProcessManager

logger = logging.getLogger("evonest")


@dataclass
class ClaudeResult:
    """Result from a claude -p invocation."""

    output: str
    exit_code: int
    success: bool
    stderr: str = ""


OBSERVE_TOOLS = "Read,Glob,Grep,Bash"
PLAN_TOOLS = "Read,Glob,Grep,Bash"
EXECUTE_TOOLS = "Read,Glob,Grep,Edit,Write,Bash"
META_TOOLS = "Read,Glob,Grep,Bash"
SCOUT_TOOLS = "Read,WebFetch,Bash"


def run(
    prompt: str,
    *,
    model: str = "sonnet",
    max_turns: int = 25,
    allowed_tools: str = OBSERVE_TOOLS,
    cwd: str | None = None,
    _retry: bool = True,
) -> ClaudeResult:
    """Run `claude -p` as a subprocess and return the result.

    Args:
        prompt: The prompt text to send.
        model: Model name (e.g. "sonnet", "opus").
        max_turns: Maximum agentic turns.
        allowed_tools: Comma-separated tool names.
        cwd: Working directory for the subprocess.

    Returns:
        ClaudeResult with output text and exit status.
    """
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
        "--no-session-persistence",  # don't save/load session history
        "--dangerously-skip-permissions",  # no TTY in detached process; skip permission prompts
        "--setting-sources",
        "user",  # skip project .mcp.json to avoid loading unrelated MCP servers
    ]

    logger.info("claude -p starting (model=%s, max-turns=%d, cwd=%s)", model, max_turns, cwd)

    # ProcessManager를 통해 subprocess 실행
    process_manager = ProcessManager(timeout=600.0, retry_on_rate_limit=True, rate_limit_wait=30.0)
    result = process_manager.run(cmd, cwd=cwd, _retry_attempt=_retry)

    # claude -p outputs "Error: Reached max turns (N)" to stdout when turns exhausted
    max_turns_hit = result.output.startswith("Error: Reached max turns")
    if max_turns_hit:
        logger.warning(
            "claude -p reached max turns limit after %.1fs: %s",
            result.elapsed_seconds,
            result.output[:100],
        )

    return ClaudeResult(
        output=result.output if not max_turns_hit else "",
        exit_code=result.exit_code,
        success=result.success and not max_turns_hit,
        stderr=result.stderr if not max_turns_hit else result.output,
    )
