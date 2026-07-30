from __future__ import annotations

import os
from collections.abc import Mapping


PROJECT_BINDINGS = frozenset({"CLAUDE_PROJECT_DIR", "PROJECT_ROOT"})
STAGE_WORK_PREFIX = "STAGE_WORK_"


def sanitized_hook_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    environment = os.environ if source is None else source
    return {
        key: value
        for key, value in environment.items()
        if key not in PROJECT_BINDINGS and not key.startswith(STAGE_WORK_PREFIX)
    }


def sanitize_current_hook_environment() -> None:
    clean = sanitized_hook_environment()
    os.environ.clear()
    os.environ.update(clean)
