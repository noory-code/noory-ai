"""Pydantic models for Plot sketches.

A sketch is deliberately schema-free at the domain level — the only
invariants we enforce are structural (unique node ids, edge endpoints
reference existing nodes). Semantics (what a "Fan" or a "buys" edge
means) live in the user's head and optionally in the node/edge labels.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Shape = Literal["rectangle", "rounded", "circle", "ellipse", "diamond", "hexagon"]


class SketchNode(BaseModel):
    """A freeform node on the canvas."""

    id: str = Field(..., min_length=1)
    label: str = ""
    body: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 180.0
    height: float = 80.0
    color: str = "#ffffff"
    shape: Shape = "rounded"
    icon: str | None = None


class SketchEdge(BaseModel):
    """A freeform edge between two nodes."""

    id: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    source_handle: str | None = Field(default=None, alias="sourceHandle")
    target_handle: str | None = Field(default=None, alias="targetHandle")
    label: str = ""
    style: Literal["solid", "dashed"] = "solid"

    model_config = {"populate_by_name": True}


class SketchDoc(BaseModel):
    """Full sketch document. One file per sketch under ``.plot/sketches/``."""

    id: str = Field(..., min_length=1)
    name: str = ""
    created: str = ""  # ISO date (YYYY-MM-DD)
    updated: str = ""  # ISO datetime
    version: int = 1
    nodes: list[SketchNode] = Field(default_factory=list)
    edges: list[SketchEdge] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _kebab_id(cls, v: str) -> str:
        """Sketch ids become filenames — reject anything that could surprise the filesystem."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"sketch id must be alphanumeric with -/_ only, got {v!r}"
            )
        return v

    @model_validator(mode="after")
    def _edges_reference_nodes(self) -> SketchDoc:
        node_ids = {n.id for n in self.nodes}
        dangling = [
            e for e in self.edges if e.source not in node_ids or e.target not in node_ids
        ]
        if dangling:
            missing = sorted({e.id for e in dangling})
            raise ValueError(f"edges reference unknown nodes: {missing}")
        if len({e.id for e in self.edges}) != len(self.edges):
            raise ValueError("edge ids must be unique")
        if len({n.id for n in self.nodes}) != len(self.nodes):
            raise ValueError("node ids must be unique")
        return self


class SketchSummary(BaseModel):
    """Lightweight sketch metadata for the list endpoint."""

    id: str
    name: str
    updated: str
    node_count: int
    edge_count: int
