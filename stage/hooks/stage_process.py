"""Run a command whose time limit ends the whole process tree it started.

`subprocess.run(..., timeout=...)` kills only the direct child. When that child is a shell
(`cmd.exe` on Windows, or a POSIX shell running a compound command) or a script that starts its
own children, the descendants survive, keep the stdout/stderr pipes open, and the `communicate()`
that follows the kill waits until they finish. The time limit then bounds nothing (W-00000381:
a 1-second limit on a 5-second command took 5.5 seconds on Windows).

`run_bounded` starts the command in its own process group and, on timeout or interrupt, ends
that group: `taskkill /T /F` on Windows, `killpg` on POSIX. It keeps the
`subprocess.run` contract callers already use: it returns a `CompletedProcess` with text output
and raises `subprocess.TimeoutExpired` on timeout.

Output is read as UTF-8, and a stream that is not valid UTF-8 is read in the Windows OEM code
page instead: `cmd.exe` writes its own messages there (cp949 on Korean Windows), and reading them
as UTF-8 turned a failed check's message into replacement characters (W-00000394).

Calls nest: the driver runs close_work, which runs a review through run_review, which runs the
reviewer, each through `run_bounded`. `taskkill /T` follows the parent chain, so on Windows the
outer kill reaches every level. On POSIX each level is a group of its own, and a `killpg` of the
outer group does not reach the inner ones (W-00000391). So the POSIX kill sends SIGTERM to the
group first, and `run_bounded`, while it waits on the main thread, answers SIGTERM by ending its
own command's group before it exits. SIGKILL follows after `TERM_GRACE_SECONDS`, for a process
that ignores SIGTERM.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
from collections.abc import Iterator, Mapping, Sequence
from typing import Any
from contextlib import contextmanager
from pathlib import Path

# After the tree is killed, wait at most this long for the pipes to close. A descendant that
# escaped the group (it started its own session or job) may still hold them; the call then
# returns without its output rather than waiting for it.
DRAIN_SECONDS = 2.0
TASKKILL_SECONDS = 10.0
# How long a POSIX group gets to end its own descendants after SIGTERM before SIGKILL.
TERM_GRACE_SECONDS = 2.0


def decode_output(data: bytes | None, fallback: str | None = None) -> str:
    """Read a command's output as UTF-8, or in the fallback encoding when it is not UTF-8.

    The fallback defaults to the OEM code page on Windows, where `cmd.exe` writes its own
    messages, and to UTF-8 with replacement elsewhere.
    """

    if not data:
        return ""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        encoding = fallback or ("oem" if sys.platform == "win32" else "utf-8")
        return data.decode(encoding, errors="replace")
TERMINATED_STATUS = 128 + 15


def _group_options() -> dict[str, object]:
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    # `process_group` needs Python 3.11; Stage runs on 3.9. preexec_fn is unsafe with the
    # threads drive_parallel.py runs drivers on.
    return {"start_new_session": True}


def kill_process_tree(proc: "subprocess.Popen[Any]") -> None:
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
        # descendants of a shell that already exited. SIGTERM first lets a nested
        # run_bounded end the group it started, which this group's kill cannot reach.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except OSError:
            pass
        else:
            try:
                proc.wait(timeout=TERM_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                pass
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        proc.kill()
    except OSError:
        pass


def _exit_on_sigterm(signum: int, frame: object) -> None:
    raise SystemExit(TERMINATED_STATUS)


@contextmanager
def _sigterm_ends_tree() -> Iterator[None]:
    """Turn SIGTERM into SystemExit while waiting, so the caller ends its tree on the way out.

    Signal handlers can be set only on the main thread; a worker thread's caller is the
    outermost level (drive_parallel.py), which no outer kill has to reach.
    """
    if sys.platform == "win32" or threading.current_thread() is not threading.main_thread():
        yield
        return
    previous = signal.signal(signal.SIGTERM, _exit_on_sigterm)
    try:
        yield
    finally:
        # None means the handler was not set from Python; the default is the closest match.
        signal.signal(signal.SIGTERM, signal.SIG_DFL if previous is None else previous)


def _drain(proc: subprocess.Popen[bytes]) -> tuple[str, str]:
    try:
        stdout, stderr = proc.communicate(timeout=DRAIN_SECONDS)
    except subprocess.TimeoutExpired:
        return "", ""
    return decode_output(stdout), decode_output(stderr)


def run_bounded(
    command: str | Sequence[str],
    *,
    timeout: float,
    shell: bool = False,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run `command`, capturing its output as text, and end its process tree at `timeout`."""
    with _sigterm_ends_tree():
        proc = subprocess.Popen(
            command,
            shell=shell,
            cwd=None if cwd is None else str(cwd),
            env=None if env is None else dict(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **_group_options(),  # type: ignore[call-overload]
        )
        try:
            raw_stdout, raw_stderr = proc.communicate(timeout=timeout)
            stdout, stderr = decode_output(raw_stdout), decode_output(raw_stderr)
        except subprocess.TimeoutExpired:
            kill_process_tree(proc)
            stdout, stderr = _drain(proc)
            raise subprocess.TimeoutExpired(
                command, timeout, output=stdout, stderr=stderr
            ) from None
        except BaseException:
            # A separate process group no longer receives the terminal's Ctrl+C, so an
            # interrupt of this process, or an outer run_bounded's SIGTERM, must end the
            # tree itself instead of leaving it running.
            kill_process_tree(proc)
            _drain(proc)
            raise
    return subprocess.CompletedProcess(command, proc.returncode, stdout or "", stderr or "")
