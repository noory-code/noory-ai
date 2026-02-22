"""macOS notification utility for evonest phase completion."""

from __future__ import annotations

import platform
import subprocess


def notify(title: str, message: str) -> None:
    """Send a macOS notification. No-op on non-macOS or if osascript unavailable."""
    if platform.system() != "Darwin":
        return
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            timeout=3,
            capture_output=True,
        )
    except Exception:
        pass  # never crash the main flow
