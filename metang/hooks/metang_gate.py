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

Targeting (why the answer is anchored to the last user turn): a ``Stop`` hook
can fire a beat before the just-finished assistant message is flushed to the
transcript. Reading "the last assistant message" then grabs the *previous*
turn's answer (the off-by-one seen in 1.4.0). So the gate judges only an
assistant reply that sits **after** the most recent user message, and briefly
polls for it to appear; if it never does, it skips (fail open) rather than judge
a stale turn.

Asks ``claude -p`` (the user's own subscription auth — no API key, not
separately billed) for a one-line verdict.

**Fails OPEN on every error.** A broken judge, missing CLI, timeout, malformed
transcript, or an un-flushed reply must never trap the conversation — when in
doubt, allow.

Guards against runaway:
- ``METANG_GATE_ACTIVE`` env set → no-op. The judge itself runs ``claude``,
  which may load this very hook; the env sentinel stops it judging its own
  output.
- ``stop_hook_active`` true → no-op. One bounce per turn; never loop.
- ``gateEnabled: false`` in config → no-op.
- ``METANG_GATE_FAKE_VERDICT`` env → skip the model call and use that string as
  the verdict (test seam).

Config (merged ~/.metang.json then project ``.metang.json``, project wins):
- ``gateEnabled`` (bool, default ``true``)
- ``gateModel`` (str, default ``"haiku"``)
- ``gateDebug`` (bool, default ``false``) — append one diagnostic line per fire
  to ``<tempdir>/metang_gate.log``.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
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
POLL_TOTAL = 2.0  # seconds — wait this long for the just-finished reply to flush
POLL_STEP = 0.15


def _allow() -> None:
    """Let the turn end (no output = no objection)."""
    sys.exit(0)


def _block(reason: str) -> None:
    """Refuse the stop; the reason is fed back so the model rewrites."""
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


def _text_blocks(content: object) -> list[str]:
    if isinstance(content, str):
        return [content] if content else []
    if isinstance(content, list):
        return [
            b["text"]
            for b in content
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text")
        ]
    return []


def _all_text(content: object) -> str:
    return "\n".join(_text_blocks(content))


def _first_text(content: object) -> str:
    """The user's real prompt is the first text block; later blocks are appended
    hook context (the metang reminder, system notes) — drop them."""
    blocks = _text_blocks(content)
    return blocks[0] if blocks else ""


def _scan(transcript_path: str) -> tuple[str, str, bool]:
    """Return (user_prompt, answer, answer_is_current).

    ``answer_is_current`` is True when, scanning from the end, the first
    text-bearing message is the assistant's — i.e. the reply to the latest user
    turn is already on disk. When the first text-bearing message is the user's,
    the reply has not flushed yet (the off-by-one window)."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return "", "", False
    user_prompt = answer = ""
    first_text_type: str | None = None
    for ln in reversed(lines):
        try:
            obj = json.loads(ln)
        except ValueError:
            continue
        content = (obj.get("message") or {}).get("content")
        if not _text_blocks(content):
            continue
        kind = obj.get("type")
        if first_text_type is None:
            first_text_type = kind
        if kind == "assistant" and not answer:
            answer = _all_text(content)
        elif kind == "user" and not user_prompt:
            user_prompt = _first_text(content)
        if answer and user_prompt:
            break
    return user_prompt, answer, first_text_type == "assistant"


def _rule_text() -> str:
    blocks = []
    if DEFAULT_EXPLAIN:
        blocks.append("Explaining:\n" + DEFAULT_EXPLAIN)
    if DEFAULT_ASK:
        blocks.append("Asking:\n" + DEFAULT_ASK)
    return (SCOPE + "\n\n" + "\n\n".join(blocks)).strip()


def _judge_prompt(user_text: str, answer: str) -> str:
    return (
        "You are a strict reviewer of HOW an assistant wrote one reply — not "
        "whether its topic is expected.\n\n"
        "THE DISCIPLINE:\n" + _rule_text() + "\n\n"
        "THE USER ASKED:\n" + (user_text[:1500] or "(unknown)") + "\n\n"
        "THE ASSISTANT REPLY (judge THIS):\n" + answer[:6000] + "\n\n"
        "Judge ONLY the writing: jargon or raw identifiers dumped without plain "
        "meaning; rambling or far longer than needed; dodging with empty "
        "abstractions; or asking something it should have just decided. The user "
        "may have steered the subject — do NOT fail a reply for changing topic, "
        "for being brief, or for content you lack the backstory on. When unsure, "
        "PASS.\n"
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


def _debug(cfg: dict[str, object], msg: str) -> None:
    if not cfg.get("gateDebug"):
        return
    try:
        log = Path(tempfile.gettempdir()) / "metang_gate.log"
        with log.open("a", encoding="utf-8") as fh:
            fh.write(msg + "\n")
    except OSError:
        pass


def main() -> None:
    # Guard 1 — never run inside the judge's own claude invocation.
    if os.environ.get("METANG_GATE_ACTIVE"):
        _allow()
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        _allow()
    # Guard 2 — one bounce per turn; if we already blocked once, let it through.
    if payload.get("stop_hook_active"):
        _allow()

    cfg = load_config()
    if cfg.get("gateEnabled", True) is False:
        _allow()

    path = str(payload.get("transcript_path") or "")
    # Anchor to the reply that sits AFTER the latest user message, polling for it
    # to flush. If it never appears, skip (don't judge the previous turn).
    waited = 0.0
    user_prompt, answer, current = _scan(path)
    while not current and waited < POLL_TOTAL:
        time.sleep(POLL_STEP)
        waited += POLL_STEP
        user_prompt, answer, current = _scan(path)
    if not current or not answer.strip():
        _debug(cfg, f"skip current={current} waited={waited:.2f} ans={len(answer)}")
        _allow()

    model = str(cfg.get("gateModel") or "haiku")
    try:
        verdict = _verdict(_judge_prompt(user_prompt, answer), model)
    except Exception as exc:  # judge failed → fail open
        _debug(cfg, f"judge-error {type(exc).__name__} waited={waited:.2f}")
        _allow()

    _debug(cfg, f"verdict={verdict[:60]!r} waited={waited:.2f} ans0={answer[:40]!r}")
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
