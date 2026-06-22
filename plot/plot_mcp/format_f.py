"""format F export (INT-2) — vP project snapshot + vS service release.

Implements the neutral published-bundle contract in ``docs/specs/format-f.md``.
**Walking-skeleton scope (D-2026-06-22, "워킹 스켈레톤 먼저"):** this is written
*alongside* the existing per-node publish (``node_publish.py``), not a
replacement yet — the per-node retirement is a separate later migration.

Slugs are minted into a per-project registry ``_slugs.json`` (P-4 = explicit
slug field): keyed on node id, so a slug is **stable across label changes** and
decoupled from the label — the connective tissue of the Plot↔Solera pipeline.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from plot_mcp.folder_io import read_canvas, read_project
from plot_mcp.storage import _project_dir, _read_json, _write_json

FORMAT_F_VERSION = 1

# Kinds published as a singleton (bare slug, no ``kind/`` prefix).
_SINGLETON_KINDS = frozenset({"mission"})

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-") or "x"


def _slug_store_path(plot_root: Path, project_id: str) -> Path:
    return _project_dir(plot_root, project_id) / "_slugs.json"


def mint_slug(plot_root: Path, project_id: str, node: Any) -> str:
    """Return the stable slug for ``node``, minting it on first sight.

    Keyed on ``node.id``: the slug is derived from the label *once* and then
    frozen in ``_slugs.json``, so renaming the label never moves the slug
    (explicit-slug invariant, P-4). Collisions within a project get a ``-N``
    suffix.
    """
    store_path = _slug_store_path(plot_root, project_id)
    store: dict[str, str] = _read_json(store_path) if store_path.exists() else {}
    existing = store.get(node.id)
    if existing is not None:
        return existing

    if node.kind in _SINGLETON_KINDS:
        candidate = str(node.kind)
    else:
        candidate = f"{node.kind}/{_slugify(node.label or node.id)}"

    taken = set(store.values())
    slug = candidate
    suffix = 2
    while slug in taken:
        slug = f"{candidate}-{suffix}"
        suffix += 1

    store[node.id] = slug
    _write_json(store_path, store)
    return slug


def _hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _git_sha(plot_root: Path) -> str:
    """Best-effort workspace git sha (the anchor of immutability). Empty when
    there is no repo — the walking skeleton does not require one."""
    from plot_mcp.workspace import workspace_root_from_plot_root

    try:
        ws = workspace_root_from_plot_root(plot_root)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ws),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except OSError:
        return ""


def _next_release(scope_dir: Path, prefix: str) -> int:
    """Next monotonic release number under ``scope_dir`` (e.g. ``vP`` / ``vS``)."""
    if not scope_dir.is_dir():
        return 1
    seen: list[int] = []
    for child in scope_dir.iterdir():
        if child.is_dir() and child.name.startswith(prefix):
            try:
                seen.append(int(child.name[len(prefix) :]))
            except ValueError:
                continue
    return (max(seen) + 1) if seen else 1


def _latest_release(scope_dir: Path, prefix: str) -> str | None:
    n = _next_release(scope_dir, prefix) - 1
    return f"{prefix}{n}" if n >= 1 else None


def publish_project_snapshot(plot_root: Path, project_id: str) -> dict[str, Any]:
    """Freeze the project's **shared structure** (本質·Actors·Entities) into a
    ``published/_project/vP{N}/`` snapshot — the project-scope layer of the
    2-layer model (D-2026-06-21-AB). Returns the manifest.
    """
    read_project(plot_root, project_id)  # validate id (404s on mismatch)
    snap_dir = _project_dir(plot_root, project_id) / "published" / "_project"
    release = f"vP{_next_release(snap_dir, 'vP')}"
    design = snap_dir / release / "design"
    design.mkdir(parents=True, exist_ok=True)

    elements: list[dict[str, Any]] = []

    # --- Foundation (mission / core_value / identity) ---
    foundation = read_canvas(plot_root, project_id, "foundation")
    f_blocks: list[str] = []
    for node in foundation.nodes:
        if node.kind not in ("mission", "core_value", "identity"):
            continue
        slug = mint_slug(plot_root, project_id, node)
        body = str(getattr(node, "body", "") or "")
        elements.append(
            {"id": slug, "kind": node.kind, "hash": _hash(f"{node.kind}|{node.label}|{body}")}
        )
        f_blocks.append(f"## {node.label} (`{slug}`)\n\n{body}\n")
    (design / "foundation.md").write_text(
        "# Foundation\n\n" + "\n".join(f_blocks), encoding="utf-8"
    )

    # --- Actors (role hierarchy + relations) ---
    actors = read_canvas(plot_root, project_id, "actors")
    a_blocks: list[str] = []
    for node in actors.nodes:
        if node.kind != "actor":
            continue
        slug = mint_slug(plot_root, project_id, node)
        body = str(getattr(node, "body", "") or "")
        side = str(getattr(node, "side", "") or "")
        elements.append(
            {"id": slug, "kind": "actor", "hash": _hash(f"actor|{node.label}|{side}|{body}")}
        )
        a_blocks.append(f"## {node.label} (`{slug}`) [{side}]\n\n{body}\n")
    (design / "actors.md").write_text("# Actors\n\n" + "\n".join(a_blocks), encoding="utf-8")

    # --- Entities (concept map) ---
    entities = read_canvas(plot_root, project_id, "entities")
    for node in entities.nodes:
        if node.kind != "entity":
            continue
        slug = mint_slug(plot_root, project_id, node)
        body = str(getattr(node, "body", "") or "")
        elements.append(
            {"id": slug, "kind": "entity", "hash": _hash(f"entity|{node.label}|{body}")}
        )
        ent_dir = design / "entities"
        ent_dir.mkdir(parents=True, exist_ok=True)
        (ent_dir / f"{slug.split('/')[-1]}.md").write_text(
            f"# {node.label}\n\n{body}\n", encoding="utf-8"
        )

    manifest: dict[str, Any] = {
        "format_f_version": FORMAT_F_VERSION,
        "scope": "project",
        "release": release,
        "git_sha": _git_sha(plot_root),
        "elements": elements,
    }
    _write_json(snap_dir / release / "manifest.json", manifest)
    return manifest


def publish_service(plot_root: Path, project_id: str, service_id: str) -> dict[str, Any]:
    """Freeze one **service** (5칸 + features + category) into a
    ``published/{service-slug}/vS{N}/`` release — the service-scope layer.

    Bootstrap (format-f.md §1.5): requires a project snapshot ``vP`` to exist;
    the release pins it via ``based_on`` and references the shared elements it
    uses (actors / core_values / identity) **by slug, not by copy**.
    refs-integrity gate (§1.4): every ref must resolve in that ``vP`` — else the
    publish is refused at the write boundary.
    """
    read_project(plot_root, project_id)  # validate id
    pdir = _project_dir(plot_root, project_id)
    snap_dir = pdir / "published" / "_project"

    vp = _latest_release(snap_dir, "vP")
    if vp is None:
        raise ValueError(
            "no project snapshot (vP) — run publish_project_snapshot first (bootstrap)"
        )
    vp_ids = {e["id"] for e in _read_json(snap_dir / vp / "manifest.json")["elements"]}

    services = read_canvas(plot_root, project_id, "services")
    svc = next((n for n in services.nodes if n.id == service_id and n.kind == "service"), None)
    if svc is None:
        raise FileNotFoundError(f"service not found: {service_id}")

    store_path = _slug_store_path(plot_root, project_id)
    store: dict[str, str] = _read_json(store_path) if store_path.exists() else {}

    def _resolve(ids: list[str]) -> tuple[list[str], list[str]]:
        ok: list[str] = []
        missing: list[str] = []
        for node_id in ids:
            slug = store.get(node_id)
            if slug is None or slug not in vp_ids:
                missing.append(node_id)
            else:
                ok.append(slug)
        return ok, missing

    actor_slugs, m_a = _resolve(list(svc.ref_actor_ids))
    value_slugs, m_v = _resolve(list(svc.ref_value_ids))
    identity_slugs, m_i = _resolve(list(svc.ref_identity_ids))
    missing = m_a + m_v + m_i
    if missing:
        raise ValueError(f"refs do not resolve in {vp} (refs-integrity): {missing}")

    svc_slug = mint_slug(plot_root, project_id, svc)
    out = pdir / "published" / svc_slug.split("/")[-1]
    release = f"vS{_next_release(out, 'vS')}"
    design = out / release / "design"
    design.mkdir(parents=True, exist_ok=True)

    body = f"**왜 필요한가:** {svc.problem}\n\n**뭐가 좋아지나:** {svc.value_created}\n"
    (design / "service.md").write_text(f"# {svc.label} (`{svc_slug}`)\n\n{body}", encoding="utf-8")

    elements: list[dict[str, Any]] = [
        {
            "id": svc_slug,
            "kind": "service",
            "hash": _hash(f"service|{svc.label}|{svc.problem}|{svc.value_created}"),
        }
    ]

    manifest: dict[str, Any] = {
        "format_f_version": FORMAT_F_VERSION,
        "scope": "service",
        "service": svc_slug,
        "release": release,
        "based_on": vp,
        "git_sha": _git_sha(plot_root),
        "elements": elements,
        "refs": {
            "anchors": {"core_values": value_slugs, "identity": identity_slugs},
            "actors": actor_slugs,
            "entities": [],
        },
    }
    _write_json(out / release / "manifest.json", manifest)
    return manifest
