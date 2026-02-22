"""ClaudeRunner — subprocess wrapper for `claude -p` calls.

All LLM invocations go through this module.
Tests can mock `run()` to avoid real subprocess calls.
"""

from __future__ import annotations

import json
import logging
import subprocess
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

    Uses stream-json --verbose to log progress per turn.

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
        "stream-json",
        "--verbose",
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

        output_text = ""
        stderr_lines: list[str] = []
        turn = 0

        assert proc.stdout is not None
        assert proc.stderr is not None

        # Read stdout line-by-line (stream-json emits one JSON object per line)
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")
            subtype = event.get("subtype", "")

            if etype == "assistant":
                turn += 1
                # Log tool use if present
                msg = event.get("message", {})
                tool_names = [
                    b.get("name", "?")
                    for b in msg.get("content", [])
                    if isinstance(b, dict) and b.get("type") == "tool_use"
                ]
                elapsed = (datetime.now() - started_at).total_seconds()
                if tool_names:
                    logger.info(
                        "  turn %d (%.1fs): %s", turn, elapsed, ", ".join(tool_names)
                    )
                else:
                    logger.info("  turn %d (%.1fs): responding", turn, elapsed)

            elif etype == "result":
                # Final result event — extract the text output
                output_text = event.get("result", "")
                num_turns = event.get("num_turns", turn)
                duration_ms = event.get("duration_ms", 0)
                is_error = event.get("is_error", False)
                elapsed = duration_ms / 1000
                if is_error or subtype != "success":
                    logger.warning(
                        "claude -p result: %s after %.1fs (%d turns)",
                        subtype,
                        elapsed,
                        num_turns,
                    )
                else:
                    logger.info(
                        "claude -p completed in %.1fs (%d turns, output=%d chars)",
                        elapsed,
                        num_turns,
                        len(output_text),
                    )

        # Drain stderr
        stderr_raw = proc.stderr.read()
        if stderr_raw:
            stderr_lines.append(stderr_raw.strip())

        proc.wait(timeout=10)
        returncode = proc.returncode
        stderr_text = "\n".join(stderr_lines).strip()
        elapsed_total = (datetime.now() - started_at).total_seconds()

        if returncode != 0 and not output_text:
            logger.warning(
                "claude -p exited with code %d after %.1fs. stderr: %s",
                returncode,
                elapsed_total,
                stderr_text[:500] if stderr_text else "(none)",
            )

        if _is_rate_limit(stderr_text):
            logger.warning("claude -p rate limited after %.1fs — waiting 30s before retry", elapsed_total)
            time.sleep(30)
            return run(
                prompt,
                model=model,
                max_turns=max_turns,
                allowed_tools=allowed_tools,
                cwd=cwd,
                _retry=False,
            )

        output = output_text.strip()
        max_turns_hit = output.startswith("Error: Reached max turns")
        if max_turns_hit:
            logger.warning("claude -p reached max turns limit: %s", output[:100])

        return ClaudeResult(
            output=output if not max_turns_hit else "",
            exit_code=returncode,
            success=returncode == 0 and len(output) > 0 and not max_turns_hit,
            stderr=stderr_text if not max_turns_hit else output,
        )

    except subprocess.TimeoutExpired:
        elapsed = (datetime.now() - started_at).total_seconds()
        logger.error("claude -p timed out after %.1fs", elapsed)
        try:
            proc.kill()
        except Exception:
            pass
        return ClaudeResult(output="", exit_code=-1, success=False, stderr="timeout")

    except FileNotFoundError:
        logger.error("claude command not found. Is Claude Code CLI installed?")
        return ClaudeResult(output="", exit_code=-1, success=False)
