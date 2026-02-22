"""Domain repositories — each owns one concern in .evonest/.

Every repository receives an EvonestPaths instance and handles
its own file I/O using pathlib directly (no shared I/O helpers).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evonest.core.paths import EvonestPaths

logger = logging.getLogger("evonest")


def _slugify(title: str, max_len: int = 60) -> str:
    """Convert a proposal title to a filename-safe slug.

    Example: "Shell injection risk in verify.build" → "shell-injection-risk-in-verify-build"
    """
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_len].rstrip("-")


# ---------------------------------------------------------------------------
# Shared low-level helpers (module-private)
# ---------------------------------------------------------------------------


def _read_json(path: Path) -> dict[str, Any] | list[Any]:
    if not path.exists():
        return {}
    try:
        result: dict[str, Any] | list[Any] = json.loads(path.read_text(encoding="utf-8"))
        return result
    except json.JSONDecodeError:
        logger.warning("Corrupt JSON file, returning empty dict: %s", path)
        return {}


def _write_json(path: Path, data: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


class IdentityRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> str:
        p = self._paths.identity_path
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def write(self, content: str) -> None:
        p = self._paths.identity_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------


class ProgressRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> dict[str, Any]:
        data = _read_json(self._paths.progress_path)
        return data if isinstance(data, dict) else {}

    def write(self, data: dict[str, Any]) -> None:
        _write_json(self._paths.progress_path, data)


# ---------------------------------------------------------------------------
# Backlog
# ---------------------------------------------------------------------------


class BacklogRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> dict[str, Any]:
        if not self._paths.backlog_path.exists():
            return {"version": 2, "items": []}
        data = _read_json(self._paths.backlog_path)
        return data if isinstance(data, dict) else {"version": 2, "items": []}

    def write(self, data: dict[str, Any]) -> None:
        _write_json(self._paths.backlog_path, data)


# ---------------------------------------------------------------------------
# Mutations (dynamic personas & adversarials)
# ---------------------------------------------------------------------------


class MutationsRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read_personas(self) -> list[Any]:
        data = _read_json(self._paths.dynamic_personas_path)
        return data if isinstance(data, list) else []

    def write_personas(self, data: list[Any]) -> None:
        _write_json(self._paths.dynamic_personas_path, data)

    def read_adversarials(self) -> list[Any]:
        data = _read_json(self._paths.dynamic_adversarials_path)
        return data if isinstance(data, list) else []

    def write_adversarials(self, data: list[Any]) -> None:
        _write_json(self._paths.dynamic_adversarials_path, data)


# ---------------------------------------------------------------------------
# Advice (from meta-observe guru)
# ---------------------------------------------------------------------------


class AdviceRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> dict[str, Any]:
        data = _read_json(self._paths.advice_path)
        return data if isinstance(data, dict) else {}

    def write(self, data: dict[str, Any]) -> None:
        _write_json(self._paths.advice_path, data)


# ---------------------------------------------------------------------------
# Environment cache
# ---------------------------------------------------------------------------


class EnvironmentRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> dict[str, Any]:
        data = _read_json(self._paths.environment_path)
        return data if isinstance(data, dict) else {}

    def write(self, data: dict[str, Any]) -> None:
        _write_json(self._paths.environment_path, data)


# ---------------------------------------------------------------------------
# Scout cache
# ---------------------------------------------------------------------------


class ScoutRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> dict[str, Any]:
        data = _read_json(self._paths.scout_path)
        return data if isinstance(data, dict) else {}

    def write(self, data: dict[str, Any]) -> None:
        _write_json(self._paths.scout_path, data)


# ---------------------------------------------------------------------------
# Pending (cautious-mode pause state)
# ---------------------------------------------------------------------------


class PendingRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def read(self) -> dict[str, Any]:
        data = _read_json(self._paths.pending_path)
        return data if isinstance(data, dict) else {}

    def write(self, data: dict[str, Any]) -> None:
        _write_json(self._paths.pending_path, data)

    def clear(self) -> None:
        if self._paths.pending_path.exists():
            self._paths.pending_path.unlink()


# ---------------------------------------------------------------------------
# Proposals
# ---------------------------------------------------------------------------


class ProposalRepository:
    def __init__(self, paths: EvonestPaths, progress: ProgressRepository) -> None:
        self._paths = paths
        self._progress = progress

    def add(self, content: str, title: str | None = None, persona_id: str | None = None) -> str:
        """Save a proposal file and return its path.

        Filename format: {persona}-{title-slug}-{HHMMSS}.md
        Falls back to proposal-{HHMMSS}.md when title is absent.
        """
        self._paths.proposals_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%H%M%S")
        if title:
            title_slug = _slugify(title)
            if persona_id:
                persona_slug = _slugify(persona_id)
                stem = f"{persona_slug}-{title_slug}-{ts}"
            else:
                stem = f"{title_slug}-{ts}"
        else:
            stem = f"proposal-{ts}"
        path = self._paths.proposals_dir / f"{stem}.md"
        # Collision guard
        counter = 2
        while path.exists():
            path = self._paths.proposals_dir / f"{stem}-{counter}.md"
            counter += 1
        path.write_text(content, encoding="utf-8")
        return str(path)

    def list(self) -> list[Path]:
        """Return all pending proposal files sorted by name."""
        if not self._paths.proposals_dir.exists():
            return []
        return sorted(self._paths.proposals_dir.glob("*.md"))

    def mark_done(self, filename: str) -> Path:
        """Move a proposal to proposals/done/. Returns destination path.

        Args:
            filename: Bare filename or full path.

        Raises:
            FileNotFoundError: If the proposal file does not exist.
        """
        src = self._paths.proposals_dir / Path(filename).name
        if not src.exists():
            raise FileNotFoundError(f"Proposal not found: {src}")
        self._paths.proposals_done_dir.mkdir(parents=True, exist_ok=True)
        dest = self._paths.proposals_done_dir / src.name
        src.rename(dest)
        return dest


# ---------------------------------------------------------------------------
# Stimuli
# ---------------------------------------------------------------------------


class StimulusRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def add(self, content: str) -> str:
        """Save a stimulus file and return its path."""
        self._paths.stimuli_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        path = self._paths.stimuli_dir / f"stimulus-{ts}.md"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def consume(self) -> list[str]:
        """Read all unprocessed stimuli, move to .processed/, return contents."""
        self._paths.processed_stimuli_dir.mkdir(parents=True, exist_ok=True)
        results: list[str] = []
        if not self._paths.stimuli_dir.exists():
            return results
        for f in sorted(self._paths.stimuli_dir.glob("*.md")):
            results.append(f.read_text(encoding="utf-8"))
            f.rename(self._paths.processed_stimuli_dir / f.name)
        return results


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------


class DecisionRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def add(self, content: str) -> str:
        """Save a decision file and return its path."""
        self._paths.decisions_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        path = self._paths.decisions_dir / f"decision-{ts}.md"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def consume(self) -> list[str]:
        """Read all decision files, delete them, return contents."""
        results: list[str] = []
        if not self._paths.decisions_dir.exists():
            return results
        for f in sorted(self._paths.decisions_dir.glob("*.md")):
            results.append(f.read_text(encoding="utf-8"))
            f.unlink()
        return results


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


class HistoryRepository:
    def __init__(self, paths: EvonestPaths) -> None:
        self._paths = paths

    def save_cycle(self, cycle_num: int, data: dict[str, Any]) -> Path:
        """Save a cycle result to history."""
        self._paths.history_dir.mkdir(parents=True, exist_ok=True)
        path = self._paths.history_dir / f"cycle-{cycle_num:04d}.json"
        _write_json(path, data)
        return path

    def list_files(self) -> list[Path]:
        """Return history files sorted by name (oldest first)."""
        if not self._paths.history_dir.exists():
            return []
        return sorted(self._paths.history_dir.glob("cycle-*.json"))
