"""ClaudeRunner — subprocess wrapper for `claude -p` calls.

All LLM invocations go through this module.
Tests can mock `run()` to avoid real subprocess calls.
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass

logger = logging.getLogger("evonest")


@dataclass
class ClaudeResult:
    """Result from a claude -p invocation."""

    output: str
    exit_code: int
    success: bool
    stderr: str = ""


_RATE_LIMIT_SIGNALS = ("rate limit", "429", "too many requests", "overloaded")


def _is_rate_limit(stderr: str) -> bool:
    lower = stderr.lower()
    return any(sig in lower for sig in _RATE_LIMIT_SIGNALS)


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
        "--setting-sources",
        "user",  # skip project .mcp.json to avoid loading unrelated MCP servers
    ]

    logger.debug("Running: claude -p ... --model %s --max-turns %d", model, max_turns)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=600,  # 10 minute timeout
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode != 0:
            logger.warning(
                "claude -p exited with code %d. stderr: %s",
                result.returncode,
                stderr[:500] if stderr else "(none)",
            )
        elif not output:
            logger.warning(
                "claude -p exited 0 but produced no output. stderr: %s",
                stderr[:500] if stderr else "(none)",
            )
        # claude -p outputs "Error: Reached max turns (N)" to stdout when turns exhausted
        max_turns_hit = output.startswith("Error: Reached max turns")
        if max_turns_hit:
            logger.warning("claude -p reached max turns limit: %s", output[:100])
        return ClaudeResult(
            output=output if not max_turns_hit else "",
            exit_code=result.returncode,
            success=result.returncode == 0 and len(output) > 0 and not max_turns_hit,
            stderr=stderr if not max_turns_hit else output,
        )
    except subprocess.TimeoutExpired as exc:
        raw_stderr = exc.stderr or b""
        stderr_text = (
            raw_stderr.decode(errors="replace") if isinstance(raw_stderr, bytes) else raw_stderr
        )
        if _retry and _is_rate_limit(stderr_text):
            logger.warning("claude -p rate limited — waiting 30s before retry")
            time.sleep(30)
            return run(
                prompt,
                model=model,
                max_turns=max_turns,
                allowed_tools=allowed_tools,
                cwd=cwd,
                _retry=False,
            )
        logger.error("claude -p timed out after 600s")
        return ClaudeResult(output="", exit_code=-1, success=False, stderr=stderr_text or "timeout")
    except FileNotFoundError:
        logger.error("claude command not found. Is Claude Code CLI installed?")
        return ClaudeResult(output="", exit_code=-1, success=False)
