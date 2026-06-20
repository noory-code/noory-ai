"""Pydantic models for Plot sketches — facade (D-2026-06-11-B).

The 993-line god module was split along its own section headers into
focused modules; this file re-exports every public name so no import
site changes:

    models_kinds.py        — Shape, NodeKind, ValueForm, BaseNodeFields
    models_foundation.py   — Foundation 4 (project / mission / core_value /
                              identity) + FoundationNode + FOUNDATION_*
                              + PROJECT_ANCHOR_ID
    models_actors.py       — actor / actor_ref / service / category +
                              mission_ref / value_ref / identity_ref
    models_composition.py  — metric / step / decision / group / rule / content
    models_union.py        — SketchNode (15-way union) + SketchNodeAdapter
                              + SketchEdge
    models_canvas.py       — CanvasDoc + AnchorPlacement + ProjectDoc
                              + CanvasKind + _ALLOWED_KINDS_BY_CANVAS
    models_discovery.py    — DiscoveredProject / WorkspaceDiscoveryResponse /
                              DirTreeNode / DirTreeResponse

`tests/test_module_size.py` pins every module (and this facade) under the
monorepo 500-line rule so the god module cannot re-grow.

v0.2 schema — typed node `kind` + `parent_id` for nested containers,
and edge `action_verb` + `value_form` for value-flow semantics. See
`plot/docs/PHILOSOPHY.md` for the design rationale (two-layer structure,
Service-as-hub, composition vs decomposition).

v0.1 files remain loadable: all new fields default to None/[] and legacy
fields are unchanged.
"""

from __future__ import annotations

from plot_mcp.models_actors import (
    ActorNode as ActorNode,
)
from plot_mcp.models_actors import (
    ActorRefNode as ActorRefNode,
)
from plot_mcp.models_actors import (
    CategoryNode as CategoryNode,
)
from plot_mcp.models_actors import (
    FeatureNode as FeatureNode,
)
from plot_mcp.models_actors import (
    ServiceNode as ServiceNode,
)
from plot_mcp.models_canvas import (
    _ALLOWED_KINDS_BY_CANVAS as _ALLOWED_KINDS_BY_CANVAS,
)
from plot_mcp.models_canvas import (
    _FOUNDATION_REFS as _FOUNDATION_REFS,
)
from plot_mcp.models_canvas import (
    AnchorPlacement as AnchorPlacement,
)
from plot_mcp.models_canvas import (
    CanvasDoc as CanvasDoc,
)
from plot_mcp.models_canvas import (
    CanvasKind as CanvasKind,
)
from plot_mcp.models_canvas import (
    ProjectDoc as ProjectDoc,
)
from plot_mcp.models_canvas import (
    _default_anchors as _default_anchors,
)
from plot_mcp.models_composition import (
    DecisionNode as DecisionNode,
)
from plot_mcp.models_composition import (
    NoteNode as NoteNode,
)
from plot_mcp.models_composition import (
    RuleNode as RuleNode,
)
from plot_mcp.models_composition import (
    StepNode as StepNode,
)
from plot_mcp.models_discovery import (
    DirTreeNode as DirTreeNode,
)
from plot_mcp.models_discovery import (
    DirTreeResponse as DirTreeResponse,
)
from plot_mcp.models_discovery import (
    DiscoveredProject as DiscoveredProject,
)
from plot_mcp.models_discovery import (
    WorkspaceDiscoveryResponse as WorkspaceDiscoveryResponse,
)
from plot_mcp.models_foundation import (
    FOUNDATION_MD_FIELDS as FOUNDATION_MD_FIELDS,
)
from plot_mcp.models_foundation import (
    FOUNDATION_TYPED_TEXT_FIELDS as FOUNDATION_TYPED_TEXT_FIELDS,
)
from plot_mcp.models_foundation import (
    PROJECT_ANCHOR_ID as PROJECT_ANCHOR_ID,
)
from plot_mcp.models_foundation import (
    CoreValueNode as CoreValueNode,
)
from plot_mcp.models_foundation import (
    FoundationNode as FoundationNode,
)
from plot_mcp.models_foundation import (
    IdentityNode as IdentityNode,
)
from plot_mcp.models_foundation import (
    MissionNode as MissionNode,
)
from plot_mcp.models_foundation import (
    ProjectNode as ProjectNode,
)
from plot_mcp.models_kinds import (
    _COMPOSITION_KINDS as _COMPOSITION_KINDS,
)
from plot_mcp.models_kinds import (
    BaseNodeFields as BaseNodeFields,
)
from plot_mcp.models_kinds import (
    NodeKind as NodeKind,
)
from plot_mcp.models_kinds import (
    Shape as Shape,
)
from plot_mcp.models_kinds import (
    ValueForm as ValueForm,
)
from plot_mcp.models_union import (
    SketchEdge as SketchEdge,
)
from plot_mcp.models_union import (
    SketchNode as SketchNode,
)
from plot_mcp.models_union import (
    SketchNodeAdapter as SketchNodeAdapter,
)
