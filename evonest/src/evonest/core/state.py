"""ProjectState — container for EvonestPaths and domain repositories.

Every module accesses project files through this class.
Never construct .evonest/ paths manually elsewhere.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evonest.core.paths import EvonestPaths
from evonest.core.repositories import (
    AdviceRepository,
    BacklogRepository,
    DecisionRepository,
    EnvironmentRepository,
    HistoryRepository,
    IdentityRepository,
    MutationsRepository,
    PendingRepository,
    ProgressRepository,
    ProposalRepository,
    ScoutRepository,
    StimulusRepository,
)

logger = logging.getLogger("evonest")


def _atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """파일에 atomic write 수행 (임시 파일 생성 후 rename).

    디스크 풀, 권한 오류 등으로 쓰기 중 실패 시 원본 파일을 보호합니다.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding=encoding)
        os.replace(str(tmp_path), str(path))
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


class ProjectState:
    """Container for EvonestPaths and all domain repositories.

    Access files via typed repositories:
        state.progress.read()
        state.identity.write(content)
        state.proposals.add(content)
    """

    def __init__(self, project_path: str | Path) -> None:
        project = Path(project_path).resolve()
        if not project.is_dir():
            raise FileNotFoundError(f"Project directory not found: {project}")

        root = project / ".evonest"
        if not root.is_dir():
            raise FileNotFoundError(f"Project not initialized. Run: evonest init {project}")

        self.project = project
        self.paths = EvonestPaths(project, root)

        # Domain repositories
        self.identity = IdentityRepository(self.paths)
        self.progress = ProgressRepository(self.paths)
        self.backlog = BacklogRepository(self.paths)
        self.mutations = MutationsRepository(self.paths)
        self.advice = AdviceRepository(self.paths)
        self.environment = EnvironmentRepository(self.paths)
        self.scout = ScoutRepository(self.paths)
        self.pending = PendingRepository(self.paths)
        self.stimuli = StimulusRepository(self.paths)
        self.decisions = DecisionRepository(self.paths)
        self.history = HistoryRepository(self.paths)
        self.proposals = ProposalRepository(self.paths, self.progress)

    # --- Convenience path accessors (delegate to paths) ---

    @property
    def root(self) -> Path:
        return self.paths.root

    @property
    def config_path(self) -> Path:
        return self.paths.config_path

    @property
    def identity_path(self) -> Path:
        return self.paths.identity_path

    @property
    def progress_path(self) -> Path:
        return self.paths.progress_path

    @property
    def backlog_path(self) -> Path:
        return self.paths.backlog_path

    @property
    def lock_path(self) -> Path:
        return self.paths.lock_path

    @property
    def log_path(self) -> Path:
        return self.paths.log_path

    @property
    def history_dir(self) -> Path:
        return self.paths.history_dir

    @property
    def stimuli_dir(self) -> Path:
        return self.paths.stimuli_dir

    @property
    def processed_stimuli_dir(self) -> Path:
        return self.paths.processed_stimuli_dir

    @property
    def decisions_dir(self) -> Path:
        return self.paths.decisions_dir

    @property
    def dynamic_personas_path(self) -> Path:
        return self.paths.dynamic_personas_path

    @property
    def dynamic_adversarials_path(self) -> Path:
        return self.paths.dynamic_adversarials_path

    @property
    def advice_path(self) -> Path:
        return self.paths.advice_path

    @property
    def environment_path(self) -> Path:
        return self.paths.environment_path

    @property
    def proposals_dir(self) -> Path:
        return self.paths.proposals_dir

    @property
    def proposals_done_dir(self) -> Path:
        return self.paths.proposals_done_dir

    @property
    def scout_path(self) -> Path:
        return self.paths.scout_path

    @property
    def pending_path(self) -> Path:
        return self.paths.pending_path

    @property
    def observe_path(self) -> Path:
        return self.paths.observe_path

    @property
    def plan_path(self) -> Path:
        return self.paths.plan_path

    @property
    def execute_path(self) -> Path:
        return self.paths.execute_path

    @property
    def meta_observe_path(self) -> Path:
        return self.paths.meta_observe_path

    # --- Deprecated direct I/O (delegate to repositories) ---
    # Keep for backward compatibility; callers should migrate to repositories.

    def read_identity(self) -> str:
        return self.identity.read()

    def write_identity(self, content: str) -> None:
        self.identity.write(content)

    def read_progress(self) -> dict[str, Any]:
        return self.progress.read()

    def write_progress(self, data: dict[str, Any]) -> None:
        self.progress.write(data)

    def read_backlog(self) -> dict[str, Any]:
        return self.backlog.read()

    def write_backlog(self, data: dict[str, Any]) -> None:
        self.backlog.write(data)

    def read_dynamic_personas(self) -> list[Any]:
        return self.mutations.read_personas()

    def write_dynamic_personas(self, data: list[Any]) -> None:
        self.mutations.write_personas(data)

    def read_dynamic_adversarials(self) -> list[Any]:
        return self.mutations.read_adversarials()

    def write_dynamic_adversarials(self, data: list[Any]) -> None:
        self.mutations.write_adversarials(data)

    def read_advice(self) -> dict[str, Any]:
        return self.advice.read()

    def write_advice(self, data: dict[str, Any]) -> None:
        self.advice.write(data)

    def read_environment(self) -> dict[str, Any]:
        return self.environment.read()

    def write_environment(self, data: dict[str, Any]) -> None:
        self.environment.write(data)

    def read_scout(self) -> dict[str, Any]:
        return self.scout.read()

    def write_scout(self, data: dict[str, Any]) -> None:
        self.scout.write(data)

    def read_pending(self) -> dict[str, Any]:
        return self.pending.read()

    def write_pending(self, data: dict[str, Any]) -> None:
        self.pending.write(data)

    def clear_pending(self) -> None:
        self.pending.clear()

    def add_proposal(
        self, content: str, title: str | None = None, persona_id: str | None = None
    ) -> str:
        return self.proposals.add(content, title=title, persona_id=persona_id)

    def list_proposals(self) -> list[Path]:
        return self.proposals.list()

    def mark_proposal_done(self, filename: str) -> Path:
        return self.proposals.mark_done(filename)

    def add_stimulus(self, content: str) -> str:
        return self.stimuli.add(content)

    def consume_stimuli(self) -> list[str]:
        return self.stimuli.consume()

    def add_decision(self, content: str) -> str:
        return self.decisions.add(content)

    def consume_decisions(self) -> list[str]:
        return self.decisions.consume()

    def save_cycle_history(self, cycle_num: int, data: dict[str, Any]) -> Path:
        return self.history.save_cycle(cycle_num, data)

    def list_history_files(self) -> list[Path]:
        return self.history.list_files()

    # --- Generic I/O (kept for callers using raw paths) ---

    def read_json(self, path: Path) -> dict[str, Any] | list[Any]:
        """Read and parse a JSON file. Returns empty dict if missing or corrupt."""
        import json

        if not path.exists():
            return {}
        try:
            data: dict[str, Any] | list[Any] = json.loads(path.read_text(encoding="utf-8"))
            return data
        except json.JSONDecodeError:
            logger.warning("Corrupt JSON file, returning empty dict: %s", path)
            return {}

    def write_json(self, path: Path, data: dict[str, Any] | list[Any]) -> None:
        """Write data as pretty-printed JSON."""
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        _atomic_write_text(path, content, encoding="utf-8")

    def read_text(self, path: Path) -> str:
        """Read a text file. Returns empty string if missing."""
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        """Write text to a file."""
        _atomic_write_text(path, content)

    # --- Utilities ---

    def log(self, message: str) -> None:
        """Append a timestamped message to the orchestrator log."""
        try:
            self.paths.log_path.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            with open(self.paths.log_path, "a", encoding="utf-8") as f:
                f.write(f"{ts}: {message}\n")
        except OSError as e:
            # 로깅 실패는 조용히 처리 (디스크 풀, 권한 문제 등)
            logger.warning("Failed to write to orchestrator log: %s", e)
        logger.info(message)

    def summary(self) -> str:
        """Return a human-readable status summary."""
        prog = self.progress.read()
        total = prog.get("total_cycles", 0)
        successes = prog.get("total_successes", 0)
        failures = prog.get("total_failures", 0)
        rate = round(successes / total * 100) if total > 0 else 0
        last_run = prog.get("last_run", "never")
        locked = self.paths.lock_path.exists()
        convergence = prog.get("convergence_flags", {})

        pending = len(self.proposals.list())
        lines = [
            f"Project: {self.project}",
            f"Cycles: {total} (success: {successes}, failure: {failures}, rate: {rate}%)",
            f"Last run: {last_run}",
            f"Running: {'yes' if locked else 'no'}",
            f"Pending proposals: {pending}",
        ]
        if convergence:
            conv_areas = [k for k, v in convergence.items() if v]
            if conv_areas:
                lines.append(f"Converged areas: {', '.join(conv_areas)}")
        return "\n".join(lines)

    def ensure_dirs(self) -> None:
        """Create all required subdirectories."""
        for d in (
            self.paths.root,
            self.paths.history_dir,
            self.paths.root / "logs",
            self.paths.stimuli_dir,
            self.paths.processed_stimuli_dir,
            self.paths.decisions_dir,
            self.paths.proposals_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)
