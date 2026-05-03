"""v0.13 Phase 2: auto-export per-kind schemas + MD templates.

Plot's data has two surfaces per Foundation node:
1. **canvas.json entry** — graph data (id, position, label, parent_id, ...).
   The shape is governed by Pydantic's ``BaseNodeFields`` and the kind
   subclass; we export it as JSON Schema for IDE / tool consumption.
2. **{kind}.md** — typed-text template (heading-section format). We export
   a literal template file that shows the expected section headings; the
   parser reads any number of these sections back into typed fields.

Files land in ``{project_root}/.plot/{project_id}/schema/``:

  _meta.json                — schema_version, plot_version, kinds
  {kind}.json               — JSON Schema (canvas.json node fields only)
  mission.md.template       — heading template for the mission kind
  core_value.md.template    — ditto
  identity.md.template      — ditto
  (project has no template — typed text is empty)

The export is idempotent: same content yields no rewrite.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from plot_mcp.models import (
    FOUNDATION_TYPED_TEXT_FIELDS,
    CoreValueNode,
    IdentityNode,
    MissionNode,
    ProjectNode,
)

# Canonical heading + body format used in the MD templates. Mirrored on the
# parser side (Phase 3, ``md_template.py``).
SECTION_LABELS: dict[str, dict[str, str]] = {
    "mission": {
        "what_we_do": "What we do",
        "why": "Why",
        "direction": "Direction",
    },
    "core_value": {
        "definition": "Definition",
        "do": "Do",
        "dont": "Don't",
    },
    "identity": {
        "description": "Description",
        "do": "Do",
        "dont": "Don't",
    },
}

SCHEMA_VERSION = 1
PLOT_VERSION = "0.13.0"

_FOUNDATION_KIND_CLASSES = {
    "project": ProjectNode,
    "mission": MissionNode,
    "core_value": CoreValueNode,
    "identity": IdentityNode,
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
    """JSON Schema for what this kind's canvas.json node looks like — i.e.
    only the BaseNodeFields graph data, **excluding** typed text. The
    typed text fields live in the MD template."""
    cls = _FOUNDATION_KIND_CLASSES[kind]
    raw = cls.model_json_schema()
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


def export_foundation_schemas(project_root: Path, project_id: str) -> None:
    """Write the schema/ directory for ``project_id``. Idempotent."""
    schema_dir = _schema_dir(project_root, project_id)
    schema_dir.mkdir(parents=True, exist_ok=True)

    # _meta.json
    meta = {
        "schema_version": SCHEMA_VERSION,
        "plot_version": PLOT_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "kinds": list(_FOUNDATION_KIND_CLASSES.keys()),
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

    # {kind}.json — JSON Schema for canvas.json entry
    for kind in _FOUNDATION_KIND_CLASSES:
        schema = _node_canvas_schema(kind)
        _atomic_write(
            schema_dir / f"{kind}.json",
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        )

    # {kind}.md.template — only for kinds with typed text
    for kind in _FOUNDATION_KIND_CLASSES:
        if not FOUNDATION_TYPED_TEXT_FIELDS.get(kind):
            continue
        _atomic_write(
            schema_dir / f"{kind}.md.template",
            _render_md_template(kind),
        )
