#!/usr/bin/env python3
"""metang gate — judge the assistant's finished answer against the metang
discipline and bounce it back if it clearly breaks the rules.

Wired as a Claude Code ``Stop`` command hook. The ``UserPromptSubmit`` hook
(``metang_hook.py``) injects the discipline *before* the turn; on a long
tool-heavy turn that reminder is far from where the final answer is written, so
it loses pull. This gate closes the loop: it reads the answer the model just
produced and asks a cheap model whether it obeyed the discipline. A clear
violation blocks the stop with a reason, forcing a plain-language rewrite; a
pass lets the turn end.

Reads the Stop payload from stdin (``transcript_path`` + ``stop_hook_active``),
pulls the last assistant text from the transcript, and asks ``claude -p`` (the
user's own subscription auth — no API key, not separately billed) for a
one-line verdict.

**Fails OPEN on every error.** A broken judge, missing CLI, timeout, or
malformed transcript must never trap the conversation — when in doubt, allow.

Guards against runaway:
- ``METANG_GATE_ACTIVE`` env set → no-op. The judge itself runs ``claude``,
  which may load this very hook; the env sentinel (set on the judge subprocess)
  stops it judging its own output.
- ``stop_hook_active`` true → no-op. One bounce per turn; never loop. If the
  rewrite still fails, it ships rather than spin.
- ``gateEnabled: false`` in config → no-op.
- ``METANG_GATE_FAKE_VERDICT`` env → skip the model call and use that string as
  the verdict (test seam).

Config (merged ~/.metang.json then project ``.metang.json``, project wins):
- ``gateEnabled`` (bool, default ``true``)
- ``gateModel`` (str, default ``"haiku"``)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Reuse the discipline text + config loader so the rule has a single home
# (SSOT — never re-type the bullets here).
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from metang_hook import DEFAULT_ASK, DEFAULT_EXPLAIN, SCOPE, load_config
except Exception:  # pragma: no cover — import must never crash the gate
    SCOPE = ""
    DEFAULT_EXPLAIN = DEFAULT_ASK = ""

    def load_config() -> dict[str, object]:
        return {}


JUDGE_TIMEOUT = 45.0  # seconds — a haiku one-shot is ~3-4s; headroom for cold start


def _allow() -> None:
    """Let the turn end (no output = no objection)."""
    sys.exit(0)


def _block(reason: str) -> None:
    """Refuse the stop; the reason is fed back so the model rewrites."""
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


def _text_of(content: object) -> str:
    """Concatenate the text blocks of a transcript message's ``content``."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "\n".join(p for p in parts if p)
    return ""


def _last_messages(transcript_path: str) -> tuple[str, str]:
    """(last_user_text, last_assistant_text) from the JSONL transcript; empty
    strings when absent or unreadable."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return "", ""
    user_text = assistant_text = ""
    for ln in reversed(lines):
        try:
            obj = json.loads(ln)
        except ValueError:
            continue
        text = _text_of((obj.get("message") or {}).get("content"))
        if not text:
            continue
        kind = obj.get("type")
        if kind == "assistant" and not assistant_text:
            assistant_text = text
        elif kind == "user" and not user_text:
            user_text = text
        if assistant_text and user_text:
            break
    return user_text, assistant_text


def _rule_text() -> str:
    blocks = []
    if DEFAULT_EXPLAIN:
        blocks.append("Explaining:\n" + DEFAULT_EXPLAIN)
    if DEFAULT_ASK:
        blocks.append("Asking:\n" + DEFAULT_ASK)
    return (SCOPE + "\n\n" + "\n\n".join(blocks)).strip()


def _judge_prompt(user_text: str, answer: str) -> str:
    return (
        "You are a strict reviewer enforcing a reply-writing discipline on an "
        "assistant.\n\n"
        "THE DISCIPLINE:\n" + _rule_text() + "\n\n"
        "THE USER ASKED:\n" + (user_text[:2000] or "(unknown)") + "\n\n"
        "THE ASSISTANT REPLY (judge THIS, not the user):\n" + answer[:6000] + "\n\n"
        "Fail ONLY a clear violation the user would notice: jargon or raw "
        "identifiers dumped without plain meaning; rambling or far longer than "
        "needed; dodging with empty abstractions; or asking something it should "
        "have just decided. Be lenient on borderline cases — when unsure, PASS.\n"
        "Answer with ONE line and nothing else:\n"
        "PASS\n"
        "or\n"
        "FAIL: <max 14 words naming what to fix>"
    )


def _verdict(prompt: str, model: str) -> str:
    """One-line verdict from the cheap judge. Raises on transport failure
    (caller fails open)."""
    fake = os.environ.get("METANG_GATE_FAKE_VERDICT")
    if fake is not None:
        return fake.strip()
    cmd = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "text",
        "--max-turns",
        "1",
        "--allowedTools",
        "",  # the judge only reads + answers; no tools
        "--no-session-persistence",
        "--dangerously-skip-permissions",  # Stop-hook subprocess has no TTY
        "--setting-sources",
        "user",
    ]
    env = {
        **os.environ,
        "METANG_GATE_ACTIVE": "1",  # break recursion: judge must not judge itself
        "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
    }
    # stdin=DEVNULL is REQUIRED — without it ``claude -p`` reads inherited stdin
    # and answers that instead of the prompt arg (same class as the codex
    # stdin-leak bug, plot D-2026-06-23-F).
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=JUDGE_TIMEOUT,
        env=env,
        stdin=subprocess.DEVNULL,
    )
    return proc.stdout.strip()


def main() -> None:
    # Guard 1 — never run inside the judge's own claude invocation.
    if os.environ.get("METANG_GATE_ACTIVE"):
        _allow()
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        _allow()
    # Guard 2 — one bounce per turn. If we already blocked once this turn, let
    # the (rewritten) answer through rather than risk a loop.
    if payload.get("stop_hook_active"):
        _allow()

    cfg = load_config()
    if cfg.get("gateEnabled", True) is False:
        _allow()

    user_text, answer = _last_messages(str(payload.get("transcript_path") or ""))
    if not answer.strip():
        _allow()  # no final text to judge

    model = str(cfg.get("gateModel") or "haiku")
    try:
        verdict = _verdict(_judge_prompt(user_text, answer), model)
    except Exception:
        _allow()  # judge failed → fail open

    if verdict[:4].upper() == "FAIL":
        note = verdict.split(":", 1)[1].strip() if ":" in verdict else "broke the answer discipline"
        _block(
            "metang gate: your last reply broke the answer discipline "
            f"({note}). Rewrite it now — plain language, no raw jargon or "
            "identifier dumps, only as long as it needs to be — then finish."
        )
    _allow()


if __name__ == "__main__":
    main()
