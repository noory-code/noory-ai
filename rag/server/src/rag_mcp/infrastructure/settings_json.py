"""Pydantic schema for `.noory/rag/settings.json` and conversion to domain models.

Pydantic is used at the infrastructure boundary for validation only. The use
cases receive plain dataclasses from ``rag_mcp.domain.models``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, model_validator

from ..domain.models import SourceSpec

DEFAULT_EMBED_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_EMBED_DIM = 384


class _SourceSpecJSON(BaseModel):
    path: str
    recursive: bool = True
    include: list[str] = Field(
        default_factory=lambda: [
            "**/*.md",
            "**/*.mdx",
            "**/*.txt",
            "**/*.pdf",
            "**/*.png",
            "**/*.jpg",
            "**/*.jpeg",
            "**/*.gif",
            "**/*.webp",
        ]
    )
    exclude: list[str] = Field(default_factory=list)

    def to_domain(self) -> SourceSpec:
        return SourceSpec(
            path=self.path,
            recursive=self.recursive,
            include=tuple(self.include),
            exclude=tuple(self.exclude),
        )


class _EmbeddingJSON(BaseModel):
    provider: Literal["local"] = "local"
    model: str = DEFAULT_EMBED_MODEL
    dim: int = Field(DEFAULT_EMBED_DIM, ge=1)


class _ChunkingJSON(BaseModel):
    target_tokens: int = Field(400, ge=1)
    max_tokens: int = Field(800, ge=1)
    min_tokens: int = Field(100, ge=1)

    @model_validator(mode="after")
    def _ordered_bounds(self) -> "_ChunkingJSON":
        if self.min_tokens > self.target_tokens:
            raise ValueError("min_tokens must be <= target_tokens")
        if self.max_tokens < self.target_tokens:
            raise ValueError("max_tokens must be >= target_tokens")
        return self


class _GraphJSON(BaseModel):
    expand_depth: int = Field(2, ge=0)
    community_algo: Literal["leiden"] = "leiden"


class _SettingsJSON(BaseModel):
    sources: list[_SourceSpecJSON] = Field(default_factory=list)
    embedding: _EmbeddingJSON = Field(default_factory=_EmbeddingJSON)
    chunking: _ChunkingJSON = Field(default_factory=_ChunkingJSON)
    graph: _GraphJSON = Field(default_factory=_GraphJSON)


@dataclass(frozen=True)
class Embedding:
    provider: str
    model: str
    dim: int


@dataclass(frozen=True)
class Chunking:
    target_tokens: int
    max_tokens: int
    min_tokens: int


@dataclass(frozen=True)
class Graph:
    expand_depth: int
    community_algo: str


@dataclass(frozen=True)
class Settings:
    sources: tuple[SourceSpec, ...]
    embedding: Embedding
    chunking: Chunking
    graph: Graph

    def to_dict(self) -> dict[str, Any]:
        return {
            "sources": [
                {
                    "path": s.path,
                    "recursive": s.recursive,
                    "include": list(s.include),
                    "exclude": list(s.exclude),
                }
                for s in self.sources
            ],
            "embedding": {
                "provider": self.embedding.provider,
                "model": self.embedding.model,
                "dim": self.embedding.dim,
            },
            "chunking": {
                "target_tokens": self.chunking.target_tokens,
                "max_tokens": self.chunking.max_tokens,
                "min_tokens": self.chunking.min_tokens,
            },
            "graph": {
                "expand_depth": self.graph.expand_depth,
                "community_algo": self.graph.community_algo,
            },
        }


class SettingsError(Exception):
    pass


def _from_pydantic(s: _SettingsJSON) -> Settings:
    return Settings(
        sources=tuple(src.to_domain() for src in s.sources),
        embedding=Embedding(
            provider=s.embedding.provider, model=s.embedding.model, dim=s.embedding.dim
        ),
        chunking=Chunking(
            target_tokens=s.chunking.target_tokens,
            max_tokens=s.chunking.max_tokens,
            min_tokens=s.chunking.min_tokens,
        ),
        graph=Graph(
            expand_depth=s.graph.expand_depth,
            community_algo=s.graph.community_algo,
        ),
    )


def default_settings() -> Settings:
    return _from_pydantic(
        _SettingsJSON(
            sources=[_SourceSpecJSON(path=".noory/rag/raw/", recursive=True)],
        )
    )


def load(settings_file: Path) -> Settings:
    if not settings_file.exists():
        raise SettingsError(f"settings file not found: {settings_file}")
    try:
        raw = json.loads(settings_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SettingsError(f"invalid JSON in {settings_file}: {e}") from e
    try:
        return _from_pydantic(_SettingsJSON.model_validate(raw))
    except ValidationError as e:
        raise SettingsError(f"settings schema invalid: {e}") from e


def save(settings_file: Path, settings: Settings) -> None:
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(
        json.dumps(settings.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_dict(data: dict[str, Any]) -> Settings:
    try:
        return _from_pydantic(_SettingsJSON.model_validate(data))
    except ValidationError as e:
        raise SettingsError(str(e)) from e
