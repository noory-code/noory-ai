from __future__ import annotations

import os
from collections.abc import Mapping


DRIVER_REVIEW_ENVIRONMENT_VARIABLES = (
    "STAGE_CHANGED_PATHS_FILE",
    "STAGE_PREVIOUS_REVIEW_VERDICT_FILE",
    "STAGE_REVIEW_FAILED_CRITERIA_FILE",
    "STAGE_REVIEW_MODE",
    "STAGE_REVIEW_VERDICT_FILE",
    "STAGE_WORK_ITEM_PATH",
    "STAGE_WORK_LOG_PATH",
)


def sanitized_driver_test_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    for name in DRIVER_REVIEW_ENVIRONMENT_VARIABLES:
        environment.pop(name, None)
    return environment


def sanitize_current_driver_test_environment() -> None:
    clean = sanitized_driver_test_environment()
    os.environ.clear()
    os.environ.update(clean)
