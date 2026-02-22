"""EvonestPaths — all .evonest/ path calculations in one place.

Pure path properties, no I/O. Accepts any validated project root.
"""

from __future__ import annotations

from pathlib import Path


class EvonestPaths:
    """Computes paths for every file/directory inside a .evonest/ root."""

    def __init__(self, project: Path, root: Path) -> None:
        self.project = project
        self.root = root

    # --- Config / meta ---

    @property
    def config_path(self) -> Path:
        return self.root / "config.json"

    @property
    def identity_path(self) -> Path:
        return self.root / "identity.md"

    @property
    def progress_path(self) -> Path:
        return self.root / "progress.json"

    @property
    def backlog_path(self) -> Path:
        return self.root / "backlog.json"

    @property
    def lock_path(self) -> Path:
        return self.root / "lock"

    @property
    def log_path(self) -> Path:
        return self.root / "logs" / "orchestrator.log"

    @property
    def advice_path(self) -> Path:
        return self.root / "advice.json"

    @property
    def environment_path(self) -> Path:
        return self.root / "environment.json"

    @property
    def scout_path(self) -> Path:
        return self.root / "scout.json"

    @property
    def pending_path(self) -> Path:
        return self.root / "pending.json"

    # --- Dynamic mutations ---

    @property
    def dynamic_personas_path(self) -> Path:
        return self.root / "dynamic-personas.json"

    @property
    def dynamic_adversarials_path(self) -> Path:
        return self.root / "dynamic-adversarials.json"

    # --- Directories ---

    @property
    def history_dir(self) -> Path:
        return self.root / "history"

    @property
    def stimuli_dir(self) -> Path:
        return self.root / "stimuli"

    @property
    def processed_stimuli_dir(self) -> Path:
        return self.root / "stimuli" / ".processed"

    @property
    def decisions_dir(self) -> Path:
        return self.root / "decisions"

    @property
    def proposals_dir(self) -> Path:
        return self.root / "proposals"

    @property
    def proposals_done_dir(self) -> Path:
        return self.root / "proposals" / "done"

    # --- Phase output paths ---

    @property
    def observe_path(self) -> Path:
        return self.root / "observe.md"

    @property
    def plan_path(self) -> Path:
        return self.root / "plan.md"

    @property
    def execute_path(self) -> Path:
        return self.root / "execute.md"

    @property
    def meta_observe_path(self) -> Path:
        return self.root / "meta-observe.md"
