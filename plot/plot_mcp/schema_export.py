"""v0.13 Phase 2 + v0.15 Phase 1.3 — auto-export per-kind schemas + MD templates.

Plot's data has two surfaces per node:

1. **canvas.json entry** — graph data + per-kind typed fields. The shape
   is governed by a Pydantic class per kind (``BaseNodeFields`` + 15
   subclasses); we export it as JSON Schema for IDE / tool consumption.
2. **{kind}.md** — typed-text template (heading-section format).
   *Only* Foundation kinds (mission / core_value / identity) split
   typed text out of JSON into MD; the other 11 kinds keep their typed
   fields in the canvas.json entry, so they get only the JSON schema.

Files land in ``{project_root}/.plot/{project_id}/schema/``:

  _meta.json                — schema_version, plot_version, kinds
  {kind}.json               — JSON Schema for the canvas.json entry
                              of this kind (15 files, one per kind)
  mission.md.template       — heading template for the mission kind
  core_value.md.template    — ditto
  identity.md.template      — ditto
  (project + the 11 non-Foundation kinds have no MD template
   because they do not split typed text out of JSON.)

The export is idempotent: same content yields no rewrite.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from plot_mcp.models import (
    FOUNDATION_TYPED_TEXT_FIELDS,
    ActorNode,
    ActorRefNode,
    BaseNodeFields,
    CategoryNode,
    ContentNode,
    CoreValueNode,
    DecisionNode,
    FeatureNode,
    IdentityNode,
    IdentityRefNode,
    MetricNode,
    MissionNode,
    MissionRefNode,
    ProjectNode,
    RuleNode,
    ServiceNode,
    StepNode,
    ValueRefNode,
)

# Canonical heading + body format used in the MD templates. Mirrored on the
# parser side (Phase 3, ``md_template.py``).
SECTION_LABELS: dict[str, dict[str, str]] = {
    # mission: single statement section (v0.43.0, D-2026-06-06-C)
    "mission": {
        "statement": "Mission",
    },
    "core_value": {
        # v0.43.1 (D-2026-06-06-B): do/dont removed
        "definition": "Definition",
    },
    "identity": {
        # v0.43.2 (D-2026-06-06-B): do/dont removed
        "description": "Description",
    },
}

SCHEMA_VERSION = 2  # v0.15.3 — extended to all 17 kinds (decision/group registered)
PLOT_VERSION = "0.14.18"

# Full 17-kind map = the registered projection of the ``SketchNode`` union
# (``models_union.py``). It MUST cover every union member — ``decision`` /
# ``group`` shipped in the union + viewer while missing here for months
# (the "15/17 drift"); ``tests/test_schema_parity.py::test_export_map_covers_union``
# now guards against re-omission. (``group`` retirement is a separate
# *concept* decision — Chunk 2.0 — not this registration.)
_ALL_KIND_CLASSES: dict[str, type[BaseNodeFields]] = {
    # Foundation (4) — typed text lives in MD template
    "project": ProjectNode,
    "mission": MissionNode,
    "core_value": CoreValueNode,
    "identity": IdentityNode,
    # Actors / Services hub (3)
    "actor": ActorNode,
    "actor_ref": ActorRefNode,
    "service": ServiceNode,
    # feature — capability under a service; the sole drill target
    "feature": FeatureNode,
    # Grouping (1)
    "category": CategoryNode,
    # Foundation refs (3)
    "mission_ref": MissionRefNode,
    "value_ref": ValueRefNode,
    "identity_ref": IdentityRefNode,
    # Composition inside service_detail (5)
    "metric": MetricNode,
    "step": StepNode,
    "decision": DecisionNode,
    "rule": RuleNode,
    "content": ContentNode,
}


def _schema_dir(project_root: Path, project_id: str) -> Path:
    return project_root / project_id / "schema"


def _atomic_write(path: Path, content: str) -> None:
    """Write only if content differs from on-disk; preserves mtime when
    nothing changed (so git diffs / watchers don't churn)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def _render_md_template(kind: str, label_placeholder: str = "{label}") -> str:
    sections = SECTION_LABELS.get(kind, {})
    lines: list[str] = [f"# {label_placeholder}", ""]
    for _field, heading in sections.items():
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(f"<!-- {kind}.{_field} -->")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("<!-- free prose below the rule — Plot does not parse this -->")
    lines.append("")
    return "\n".join(lines)


def _node_canvas_schema(kind: str) -> dict[str, Any]:
    """JSON Schema for what this kind's canvas.json node looks like.

    For Foundation kinds (mission / core_value / identity) the typed-text
    fields are stripped because they live in the per-kind MD template,
    not in JSON. For the 11 non-Foundation kinds, every field including
    typed text is part of the canvas.json entry, so the schema returns
    the full Pydantic-generated shape unchanged.
    """
    cls = _ALL_KIND_CLASSES[kind]
    raw: dict[str, Any] = cls.model_json_schema()
    typed_text = set(FOUNDATION_TYPED_TEXT_FIELDS.get(kind, []))
    if typed_text:
        props = raw.get("properties", {})
        for field in typed_text:
            props.pop(field, None)
        required = raw.get("required") or []
        raw["required"] = [r for r in required if r not in typed_text]
        raw["description"] = (
            f"Schema for the canvas.json entry of a {kind!r} node. The "
            f"typed-text fields ({sorted(typed_text)}) live in the per-node "
            f"MD template, not in JSON."
        )
    return raw


def export_all_schemas(project_root: Path, project_id: str) -> None:
    """Write the schema/ directory for ``project_id``.

    Generates ``_meta.json`` + 15 ``{kind}.json`` JSON Schema files +
    3 ``{kind}.md.template`` heading templates (Foundation kinds only).

    Idempotent — files with unchanged content keep their mtime.
    """
    schema_dir = _schema_dir(project_root, project_id)
    schema_dir.mkdir(parents=True, exist_ok=True)

    # _meta.json
    meta = {
        "schema_version": SCHEMA_VERSION,
        "plot_version": PLOT_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "kinds": list(_ALL_KIND_CLASSES.keys()),
    }
    # generated_at changes every run; only rewrite when the rest changed.
    existing_meta_path = schema_dir / "_meta.json"
    write_meta = True
    if existing_meta_path.exists():
        try:
            old = json.loads(existing_meta_path.read_text(encoding="utf-8"))
            stable_old = {k: v for k, v in old.items() if k != "generated_at"}
            stable_new = {k: v for k, v in meta.items() if k != "generated_at"}
            if stable_old == stable_new:
                write_meta = False
        except (json.JSONDecodeError, OSError):
            write_meta = True
    if write_meta:
        _atomic_write(
            existing_meta_path,
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        )

    # {kind}.json — JSON Schema for canvas.json entry (all 15 kinds)
    for kind in _ALL_KIND_CLASSES:
        schema = _node_canvas_schema(kind)
        _atomic_write(
            schema_dir / f"{kind}.json",
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        )

    # {kind}.md.template — only Foundation kinds with typed text
    for kind in _ALL_KIND_CLASSES:
        if not FOUNDATION_TYPED_TEXT_FIELDS.get(kind):
            continue
        _atomic_write(
            schema_dir / f"{kind}.md.template",
            _render_md_template(kind),
        )


# ---------------------------------------------------------------------------
# Wire-contract snapshot (D-2026-06-10-E) — split-survivable parity artifact
# ---------------------------------------------------------------------------


def wire_contract() -> dict[str, Any]:
    """The server↔viewer wire contract as a plain, diffable dict.

    Pydantic is the SSOT: base fields + the full field set of each of the
    15 kind classes. Committed twice (``plot_mcp/wire_contract.json`` and
    ``viewer/src/schema/wire-contract.json``) so each side can verify its
    own sources against its own copy after the repo split
    (``tests/test_wire_contract.py`` / viewer ``tests/wire-contract.test.ts``).
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "base_fields": sorted(BaseNodeFields.model_fields.keys()),
        "kinds": {
            kind: sorted(cls.model_fields.keys())
            for kind, cls in sorted(_ALL_KIND_CLASSES.items())
        },
    }


def _write_wire_snapshots() -> None:
    root = Path(__file__).resolve().parent.parent
    payload = json.dumps(wire_contract(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    for target in (
        root / "plot_mcp" / "wire_contract.json",
        root / "viewer" / "src" / "schema" / "wire-contract.json",
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
        print(f"wrote {target}")


if __name__ == "__main__":
    import sys

    if "--wire" in sys.argv:
        _write_wire_snapshots()
