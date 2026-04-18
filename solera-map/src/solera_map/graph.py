"""Parse a Solera workspace into a typed graph.

The graph is the source of truth the HTTP layer and the MCP tools hand out.
Reads are idempotent — every call rebuilds from the filesystem. A future phase
adds an SQLite cache layer and a file watcher; for now, correctness first.

Data origin:
- `workspace/identity/*.md`           → Identity
- `workspace/concepts/*.md`           → Concept (Living axis)
- `workspace/concept-graph.json`      → Concept ↔ Concept edges (solera-map only)
- `workspace/milestones/*.md`         → Milestone (Time-bound)
- `workspace/stories/{id}/_story.md`  → Story (Time-bound)
- `workspace/stories/{id}/ACT-*.md`   → ActionItem
- `workspace/releases/{tag}/.released` → Release (Immutable)
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

ConceptStatus = Literal["active", "deprecated", "archived"]
MilestoneStatus = Literal["proposed", "agreed", "in-progress", "released"]
WorkStatus = Literal["pending", "in_progress", "complete", "on_hold", "cancelled"]

STATUS_ICON_MAP: dict[str, WorkStatus] = {
    "⏳": "pending",
    "🔄": "in_progress",
    "✅": "complete",
    "⏸️": "on_hold",
    "❌": "cancelled",
}


class Concept(BaseModel):
    id: str
    name: str
    status: ConceptStatus
    intent: str
    current_design: str
    current_shape: str
    horizon: str | None = None
    parent: str | None = None  # Concept ID of the containing Concept; None = top-level surface


class ConceptEdge(BaseModel):
    """Concept ↔ Concept relation. Free-text label by design (per plan)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    label: str
    created: str | None = None


class Story(BaseModel):
    id: str
    name: str
    story_type: str  # US / TS
    status: WorkStatus
    contributes_to: list[str] = Field(default_factory=list)
    belongs_to: str | None = None


class ActionItem(BaseModel):
    story_id: str
    id: str
    name: str
    status: WorkStatus
    depends_on: list[str] = Field(default_factory=list)


class Milestone(BaseModel):
    id: str
    name: str
    status: MilestoneStatus
    scope: list[str] = Field(default_factory=list)


class Identity(BaseModel):
    mission: str | None = None
    vision: str | None = None
    values: str | None = None
    goals: str | None = None
    tone_and_manner: str | None = None
    # Any other `workspace/identity/*.md` files we don't recognize above are
    # surfaced here keyed by filename stem (e.g., "brand-voice").
    extras: dict[str, str] = Field(default_factory=dict)


class Release(BaseModel):
    tag: str
    milestone_id: str | None = None
    released_at: str | None = None


class Graph(BaseModel):
    identity: Identity | None = None
    concepts: list[Concept] = Field(default_factory=list)
    concept_edges: list[ConceptEdge] = Field(default_factory=list)
    milestones: list[Milestone] = Field(default_factory=list)
    stories: list[Story] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    releases: list[Release] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
_SECTION_RE = re.compile(r"^# (.+?)\n(.*?)(?=\n# |\Z)", re.MULTILINE | re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[[^\]]*?/?([\w.-]+?)(?:\|[^\]]*)?\]\]")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file into (frontmatter dict, body).

    Malformed YAML frontmatter yields an empty dict and a warning log — real
    Solera workspaces contain hand-edited files where quoting slipped, and we
    prefer to surface them as under-populated nodes over hard-failing the read.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        _log.warning("malformed frontmatter: %s", exc)
        return {}, text[match.end() :]
    if not isinstance(fm, dict):
        return {}, text[match.end() :]
    return fm, text[match.end() :]


def parse_sections(body: str) -> dict[str, str]:
    """Split body by top-level `# Heading` blocks. Returns {heading: content}."""
    out: dict[str, str] = {}
    for m in _SECTION_RE.finditer(body):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def _status_from_icon_or_text(raw: str | None) -> WorkStatus:
    if not raw:
        return "pending"
    raw = raw.strip()
    for icon, status in STATUS_ICON_MAP.items():
        if icon in raw:
            return status
    lowered = raw.lower().replace("-", "_").replace(" ", "_")
    if lowered in ("pending", "in_progress", "complete", "on_hold", "cancelled"):
        return lowered  # type: ignore[return-value]
    return "pending"


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------


def update_concept_frontmatter(path: Path, updates: dict[str, Any]) -> None:
    """Merge `updates` into the Concept file's frontmatter and rewrite.

    - Keys with value `None` are **removed** from frontmatter.
    - Keys with any other value **overwrite**.
    - Frontmatter ordering is preserved for keys that already existed; new
      keys append to the end.
    - The body (everything after the second `---`) is left untouched.
    - If the file has no frontmatter, a new block is inserted at the top.
    """
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    for key, value in updates.items():
        if value is None:
            fm.pop(key, None)
        else:
            fm[key] = value
    dumped = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    new_text = f"---\n{dumped}\n---\n{body}" if dumped else body
    path.write_text(new_text, encoding="utf-8")


def read_concept_file(path: Path) -> Concept:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    sections = parse_sections(body)
    concept_id = fm.get("id") or path.stem
    parent = fm.get("parent")
    return Concept(
        id=concept_id,
        name=fm.get("name", concept_id.replace("-", " ").title()),
        status=fm.get("status", "active"),
        intent=sections.get("Intent", ""),
        current_design=sections.get("Current Design", ""),
        current_shape=sections.get("Current Shape", ""),
        horizon=sections.get("Horizon"),
        parent=str(parent) if parent else None,
    )


def read_concepts(workspace: Path) -> list[Concept]:
    concepts_dir = workspace / "concepts"
    if not concepts_dir.exists():
        return []
    results: list[Concept] = []
    for md in sorted(concepts_dir.glob("*.md")):
        if md.name == "_index.md":
            continue
        results.append(read_concept_file(md))
    return results


def read_concept_graph(workspace: Path) -> list[ConceptEdge]:
    path = workspace / "concept-graph.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    edges: list[ConceptEdge] = []
    for i, e in enumerate(data.get("edges", [])):
        edges.append(
            ConceptEdge(
                id=f"{e['from']}--{e['to']}--{i}",
                **{"from": e["from"], "to": e["to"]},
                label=e.get("label", ""),
                created=e.get("created"),
            )
        )
    return edges


def read_layout(workspace: Path) -> dict[str, Any]:
    """Read `_views/map-layout.json` or return an empty layout."""
    path = workspace / "_views" / "map-layout.json"
    if not path.exists():
        return {"nodes": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _log.warning("malformed map-layout.json at %s; ignoring", path)
        return {"nodes": {}}
    if not isinstance(data, dict):
        return {"nodes": {}}
    nodes = data.get("nodes") or {}
    return {"nodes": nodes if isinstance(nodes, dict) else {}}


def write_layout(workspace: Path, layout: dict[str, Any]) -> None:
    """Persist a layout dict to `_views/map-layout.json` (pretty JSON).

    The schema is `{"nodes": {"<node_id>": {"x": float, "y": float}, ...}}`.
    Arbitrary extra keys are allowed and preserved.
    """
    views_dir = workspace / "_views"
    views_dir.mkdir(parents=True, exist_ok=True)
    path = views_dir / "map-layout.json"
    path.write_text(
        json.dumps(layout, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _extract_concept_id(bullet_line: str) -> str:
    """Pull a Concept id out of a Scope bullet.

    Accepted shapes:
        - authentication
        - [[../concepts/authentication]]
        - [[../concepts/authentication]] — annotation
        - [[../concepts/authentication|label]] — annotation
    """
    stripped = bullet_line.lstrip("- ").strip()
    wikilink = _WIKILINK_RE.search(stripped)
    if wikilink:
        return wikilink.group(1)
    # Bare id, optionally followed by em-dash annotation.
    return stripped.split("—")[0].split(" ")[0].strip()


def read_milestone_file(path: Path) -> Milestone:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    sections = parse_sections(body)
    milestone_id = fm.get("id") or path.stem
    scope_lines = sections.get("Scope", "")
    scope = [
        _extract_concept_id(line)
        for line in scope_lines.splitlines()
        if line.strip().startswith("-")
    ]
    return Milestone(
        id=milestone_id,
        name=fm.get("name", milestone_id),
        status=fm.get("status", "proposed"),
        scope=[s for s in scope if s],
    )


def read_milestones(workspace: Path) -> list[Milestone]:
    ms_dir = workspace / "milestones"
    if not ms_dir.exists():
        return []
    results: list[Milestone] = []
    for md in sorted(ms_dir.glob("*.md")):
        if md.name == "_index.md":
            continue
        results.append(read_milestone_file(md))
    return results


def read_story_file(path: Path) -> tuple[Story, list[ActionItem]]:
    text = path.read_text(encoding="utf-8")
    fm, _body = parse_frontmatter(text)
    # Solera field names evolved — tolerate both `id`/`name` and `story_id`/`story_name`.
    story_id = fm.get("id") or fm.get("story_id") or path.parent.name
    story_name = fm.get("name") or fm.get("story_name") or path.parent.name
    contributes_to_raw = fm.get("contributes_to") or []
    if isinstance(contributes_to_raw, str):
        contributes_to = [contributes_to_raw]
    else:
        contributes_to = list(contributes_to_raw)
    story = Story(
        id=str(story_id),
        name=str(story_name),
        story_type=fm.get("type", "US"),
        status=_status_from_icon_or_text(fm.get("status")),
        contributes_to=contributes_to,
        belongs_to=fm.get("belongs_to"),
    )
    acts: list[ActionItem] = []
    for act_md in sorted(path.parent.glob("ACT-*.md")):
        acts.append(_read_action_item(act_md, story.id))
    return story, acts


def _read_action_item(path: Path, story_id: str) -> ActionItem:
    text = path.read_text(encoding="utf-8")
    fm, _body = parse_frontmatter(text)
    act_id = fm.get("id") or path.stem.split("-", 2)[0] + "-" + path.stem.split("-", 2)[1]
    depends_on_raw = fm.get("depends_on") or []
    if isinstance(depends_on_raw, str):
        depends_on = [depends_on_raw]
    else:
        depends_on = list(depends_on_raw)
    return ActionItem(
        story_id=story_id,
        id=act_id,
        name=fm.get("name", path.stem),
        status=_status_from_icon_or_text(fm.get("status")),
        depends_on=depends_on,
    )


def read_stories(workspace: Path) -> tuple[list[Story], list[ActionItem]]:
    stories_dir = workspace / "stories"
    if not stories_dir.exists():
        return [], []
    stories: list[Story] = []
    acts: list[ActionItem] = []
    for story_dir in sorted(p for p in stories_dir.iterdir() if p.is_dir()):
        story_md = story_dir / "_story.md"
        if not story_md.exists():
            continue
        story, story_acts = read_story_file(story_md)
        stories.append(story)
        acts.extend(story_acts)
    return stories, acts


_IDENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    # canonical field → recognized filename stems (first match wins)
    "mission": ("mission",),
    "vision": ("vision",),
    "values": ("core-values", "values"),
    "goals": ("goals",),
    "tone_and_manner": ("tone-and-manner", "tone", "voice"),
}


def _read_identity_body(path: Path) -> str | None:
    if not path.exists():
        return None
    _fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return body.strip() or None


def read_identity(workspace: Path) -> Identity | None:
    id_dir = workspace / "identity"
    if not id_dir.exists():
        return None

    files = list(id_dir.glob("*.md"))
    if not files:
        return None

    # Index files by normalized stem ("vision_1" → "vision") to tolerate the
    # "_N" suffixes Obsidian appends when duplicating notes.
    def _norm(stem: str) -> str:
        return re.sub(r"_\d+$", "", stem).lower()

    by_stem: dict[str, Path] = {}
    for f in files:
        by_stem.setdefault(_norm(f.stem), f)

    picked: dict[str, str | None] = {}
    consumed: set[str] = set()
    for field, aliases in _IDENTITY_ALIASES.items():
        for alias in aliases:
            if alias in by_stem:
                picked[field] = _read_identity_body(by_stem[alias])
                consumed.add(alias)
                break
        picked.setdefault(field, None)

    extras: dict[str, str] = {}
    for stem, path in by_stem.items():
        if stem in consumed:
            continue
        body = _read_identity_body(path)
        if body:
            extras[stem] = body

    return Identity(
        mission=picked["mission"],
        vision=picked["vision"],
        values=picked["values"],
        goals=picked["goals"],
        tone_and_manner=picked["tone_and_manner"],
        extras=extras,
    )


def read_releases(workspace: Path) -> list[Release]:
    releases_dir = workspace / "releases"
    if not releases_dir.exists():
        return []
    results: list[Release] = []
    for tag_dir in sorted(p for p in releases_dir.iterdir() if p.is_dir()):
        marker = tag_dir / ".released"
        if not marker.exists():
            continue
        meta: dict[str, str] = {}
        for line in marker.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip()
        results.append(
            Release(
                tag=meta.get("release_tag", tag_dir.name),
                milestone_id=meta.get("milestone_id"),
                released_at=meta.get("released_at"),
            )
        )
    return results


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def build_graph(workspace: Path) -> Graph:
    """Read everything under `workspace/` and assemble a `Graph`."""
    stories, action_items = read_stories(workspace)
    return Graph(
        identity=read_identity(workspace),
        concepts=read_concepts(workspace),
        concept_edges=read_concept_graph(workspace),
        milestones=read_milestones(workspace),
        stories=stories,
        action_items=action_items,
        releases=read_releases(workspace),
    )
