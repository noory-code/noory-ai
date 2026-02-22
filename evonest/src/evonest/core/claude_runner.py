"""ClaudeRunner — subprocess wrapper for `claude -p` calls.

All LLM invocations go through this module.
Tests can mock `run()` to avoid real subprocess calls.
"""

from __future__ import annotations

import logging
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("evonest")


@dataclass
class ClaudeResult:
    """Result from a claude -p invocation."""

    output: str
    exit_code: int
    success: bool
    stderr: str = ""


_RATE_LIMIT_SIGNALS = ("rate limit", "429", "too many requests", "overloaded")


def _is_rate_limit(text: str) -> bool:
    lower = text.lower()
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

    Uses Popen to stream stderr in real time for progress logging.

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

    logger.info("claude -p starting (model=%s, max-turns=%d, cwd=%s)", model, max_turns, cwd)
    started_at = datetime.now()

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )

        stderr_lines: list[str] = []

        def _stream_stderr() -> None:
            assert proc.stderr is not None
            for line in proc.stderr:
                line = line.rstrip()
                if line:
                    stderr_lines.append(line)
                    elapsed = (datetime.now() - started_at).total_seconds()
                    logger.info("  (%.1fs) %s", elapsed, line)

        stderr_thread = threading.Thread(target=_stream_stderr, daemon=True)
        stderr_thread.start()

        # Block until process completes (timeout 600s)
        try:
            stdout_text, _ = proc.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            elapsed = (datetime.now() - started_at).total_seconds()
            logger.error("claude -p timed out after %.1fs (limit=600s)", elapsed)
            stderr_text = "\n".join(stderr_lines)
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
            return ClaudeResult(output="", exit_code=-1, success=False, stderr=stderr_text or "timeout")

        stderr_thread.join(timeout=5)

        elapsed = (datetime.now() - started_at).total_seconds()
        output = stdout_text.strip()
        stderr_text = "\n".join(stderr_lines).strip()

        if proc.returncode != 0:
            logger.warning(
                "claude -p exited with code %d after %.1fs. stderr: %s",
                proc.returncode,
                elapsed,
                stderr_text[:500] if stderr_text else "(none)",
            )
        elif not output:
            logger.warning(
                "claude -p exited 0 but produced no output after %.1fs. stderr: %s",
                elapsed,
                stderr_text[:500] if stderr_text else "(none)",
            )
        else:
            logger.info(
                "claude -p completed in %.1fs (output=%d chars)",
                elapsed,
                len(output),
            )

        if _is_rate_limit(stderr_text):
            logger.warning("claude -p rate limited after %.1fs — waiting 30s before retry", elapsed)
            time.sleep(30)
            return run(
                prompt,
                model=model,
                max_turns=max_turns,
                allowed_tools=allowed_tools,
                cwd=cwd,
                _retry=False,
            )

        # claude -p outputs "Error: Reached max turns (N)" to stdout when turns exhausted
        max_turns_hit = output.startswith("Error: Reached max turns")
        if max_turns_hit:
            logger.warning("claude -p reached max turns limit after %.1fs: %s", elapsed, output[:100])

        return ClaudeResult(
            output=output if not max_turns_hit else "",
            exit_code=proc.returncode,
            success=proc.returncode == 0 and len(output) > 0 and not max_turns_hit,
            stderr=stderr_text if not max_turns_hit else output,
        )

    except FileNotFoundError:
        logger.error("claude command not found. Is Claude Code CLI installed?")
        return ClaudeResult(output="", exit_code=-1, success=False)
