"""Run a command whose time limit ends the whole process tree it started.

`subprocess.run(..., timeout=...)` kills only the direct child. When that child is a shell
(`cmd.exe` on Windows, or a POSIX shell running a compound command) or a script that starts its
own children, the descendants survive, keep the stdout/stderr pipes open, and the `communicate()`
that follows the kill waits until they finish. The time limit then bounds nothing (W-00000381:
a 1-second limit on a 5-second command took 5.5 seconds on Windows).

`run_bounded` starts the command in its own process group and, on timeout or interrupt, ends
that group: `taskkill /T /F` on Windows, `killpg(SIGKILL)` on POSIX. It keeps the
`subprocess.run` contract callers already use: it returns a `CompletedProcess` with text output
and raises `subprocess.TimeoutExpired` on timeout.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

# After the tree is killed, wait at most this long for the pipes to close. A descendant that
# escaped the group (it started its own session or job) may still hold them; the call then
# returns without its output rather than waiting for it.
DRAIN_SECONDS = 2.0
TASKKILL_SECONDS = 10.0


def _group_options() -> dict[str, object]:
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    # `process_group` needs Python 3.11; Stage runs on 3.9. preexec_fn is unsafe with the
    # threads drive_parallel.py runs drivers on.
    return {"start_new_session": True}


def kill_process_tree(proc: subprocess.Popen[str]) -> None:
    """End `proc` and every descendant that stayed in its process group."""
    if sys.platform == "win32":
        # taskkill walks the tree from a live parent; once the parent has exited its pid may
        # already belong to an unrelated process.
        if proc.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=TASKKILL_SECONDS,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
    else:
        # The group outlives its leader while any member remains, so this also reaches
        # descendants of a shell that already exited.
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        proc.kill()
    except OSError:
        pass


def _drain(proc: subprocess.Popen[str]) -> tuple[str, str]:
    try:
        stdout, stderr = proc.communicate(timeout=DRAIN_SECONDS)
    except subprocess.TimeoutExpired:
        return "", ""
    return stdout or "", stderr or ""


def run_bounded(
    command: str | Sequence[str],
    *,
    timeout: float,
    shell: bool = False,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run `command`, capturing UTF-8 text output, and end its process tree at `timeout`."""
    proc = subprocess.Popen(
        command,
        shell=shell,
        cwd=None if cwd is None else str(cwd),
        env=None if env is None else dict(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **_group_options(),  # type: ignore[call-overload]
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_process_tree(proc)
        stdout, stderr = _drain(proc)
        raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr) from None
    except BaseException:
        # A separate process group no longer receives the terminal's Ctrl+C, so an interrupt
        # of this process must end the tree itself instead of leaving it running.
        kill_process_tree(proc)
        _drain(proc)
        raise
    return subprocess.CompletedProcess(command, proc.returncode, stdout or "", stderr or "")
