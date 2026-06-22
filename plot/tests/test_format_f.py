"""format F export (INT-2) — vP project snapshot + slug minting.

Walking-skeleton scope (docs/specs/format-f.md): the neutral published bundle
written alongside the existing per-node publish, not a replacement yet. Slugs
are minted into a per-project registry — explicit, stable, decoupled from label.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from plot_mcp.folder_io import create_project, read_canvas
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    return resolve_plot_root(str(tmp_path))


def test_publish_project_snapshot_writes_vp1(plot_root: Path) -> None:
    from plot_mcp.format_f import publish_project_snapshot

    create_project(plot_root, "alpha", "Alpha")
    m = publish_project_snapshot(plot_root, "alpha")

    assert m["format_f_version"] == 1
    assert m["scope"] == "project"
    assert m["release"] == "vP1"
    ids = {e["id"] for e in m["elements"]}
    assert "mission" in ids
    assert any(i.startswith("core_value/") for i in ids)
    assert any(i.startswith("identity/") for i in ids)
    assert any(i.startswith("actor/") for i in ids)
    # every element carries a content hash (ID-diff input)
    assert all(e.get("hash") for e in m["elements"])

    vp = plot_root / "published" / "_project" / "vP1"
    assert (vp / "manifest.json").is_file()
    assert (vp / "design" / "foundation.md").is_file()
    assert (vp / "design" / "actors.md").is_file()


def test_snapshot_release_bumps(plot_root: Path) -> None:
    from plot_mcp.format_f import publish_project_snapshot

    create_project(plot_root, "alpha", "Alpha")
    assert publish_project_snapshot(plot_root, "alpha")["release"] == "vP1"
    assert publish_project_snapshot(plot_root, "alpha")["release"] == "vP2"


def _add_service_referencing_seeds(plot_root: Path) -> str:
    """Add a service that references the seeded actor + core_value + identity,
    returning the service node id."""
    from plot_mcp.folder_io import write_canvas
    from plot_mcp.models import ServiceNode

    foundation = read_canvas(plot_root, "alpha", "foundation")
    actors = read_canvas(plot_root, "alpha", "actors")
    cv = next(n for n in foundation.nodes if n.kind == "core_value")
    idn = next(n for n in foundation.nodes if n.kind == "identity")
    act = next(n for n in actors.nodes if n.kind == "actor")
    svc = ServiceNode(
        id="svc-auth",
        label="Auth",
        problem="users need to sign in",
        value_created="secure access to the product",
        ref_actor_ids=[act.id],
        ref_value_ids=[cv.id],
        ref_identity_ids=[idn.id],
    )
    services = read_canvas(plot_root, "alpha", "services")
    write_canvas(plot_root, "alpha", services.model_copy(update={"nodes": [svc]}))
    return "svc-auth"


def test_publish_service_release_refs_into_vp(plot_root: Path) -> None:
    from plot_mcp.format_f import publish_project_snapshot, publish_service

    create_project(plot_root, "alpha", "Alpha")
    _add_service_referencing_seeds(plot_root)
    publish_project_snapshot(plot_root, "alpha")  # vP1 (bootstrap)
    m = publish_service(plot_root, "alpha", "svc-auth")

    assert m["scope"] == "service"
    assert m["service"].startswith("service/")
    assert m["release"] == "vS1"
    assert m["based_on"] == "vP1"
    # the service element is owned by the release
    assert any(e["id"] == m["service"] for e in m["elements"])
    # refs point at vP slugs (not copies)
    assert m["refs"]["actors"] and all(a.startswith("actor/") for a in m["refs"]["actors"])
    assert all(v.startswith("core_value/") for v in m["refs"]["anchors"]["core_values"])

    vs = plot_root / "published" / "auth" / "vS1"
    assert (vs / "manifest.json").is_file()
    assert (vs / "design" / "service.md").is_file()


def test_publish_service_without_vp_is_rejected(plot_root: Path) -> None:
    """Bootstrap invariant: a service release needs a project snapshot first."""
    from plot_mcp.format_f import publish_service

    create_project(plot_root, "alpha", "Alpha")
    _add_service_referencing_seeds(plot_root)
    with pytest.raises(ValueError, match="snapshot"):
        publish_service(plot_root, "alpha", "svc-auth")


def test_publish_service_with_dangling_ref_is_rejected(plot_root: Path) -> None:
    """refs-integrity gate: a ref that does not resolve in the based_on vP is
    refused at the write boundary."""
    from plot_mcp.folder_io import write_canvas
    from plot_mcp.format_f import publish_project_snapshot, publish_service
    from plot_mcp.models import ServiceNode

    create_project(plot_root, "alpha", "Alpha")
    publish_project_snapshot(plot_root, "alpha")  # vP1 has the seeded actors only
    svc = ServiceNode(
        id="svc-x",
        label="X",
        problem="p",
        value_created="v",
        ref_actor_ids=["ghost-actor-id"],  # not in any canvas → not in vP
    )
    services = read_canvas(plot_root, "alpha", "services")
    write_canvas(plot_root, "alpha", services.model_copy(update={"nodes": [svc]}))
    with pytest.raises(ValueError, match="refs|resolve"):
        publish_service(plot_root, "alpha", "svc-x")


def test_manifest_contract_shape_is_pinned(plot_root: Path) -> None:
    """Cross-repo contract guard (INT-1c, write side): the manifests Plot emits
    carry exactly the keys Solera's reader expects. Pinned here so a producer
    change that drops a field fails before it reaches Solera. The version is
    pinned in lock-step with ``intake.SUPPORTED_FORMAT_F_VERSION``."""
    from plot_mcp.format_f import (
        FORMAT_F_VERSION,
        publish_project_snapshot,
        publish_service,
    )

    assert FORMAT_F_VERSION == 1

    create_project(plot_root, "alpha", "Alpha")
    _add_service_referencing_seeds(plot_root)
    vp = publish_project_snapshot(plot_root, "alpha")
    assert set(vp) >= {"format_f_version", "scope", "release", "git_sha", "elements"}
    assert vp["format_f_version"] == FORMAT_F_VERSION
    assert all(set(e) >= {"id", "kind", "hash"} for e in vp["elements"])

    vs = publish_service(plot_root, "alpha", "svc-auth")
    assert set(vs) >= {
        "format_f_version", "scope", "service", "release", "based_on", "elements", "refs",
    }
    assert set(vs["refs"]) >= {"anchors", "actors", "entities"}


def test_publish_reachable_via_mcp_surface(tmp_path: Path) -> None:
    """format F is reachable on the MCP surface — the primary integration path
    per VISION ('주경로 = 사용자 에이전트가 MCP로 붙음'). The tools take a
    workspace path (not a plot_root)."""
    from plot_mcp.mcp_tools import (
        create_project_tool,
        publish_project_snapshot_tool,
        publish_service_tool,
    )

    create_project_tool(str(tmp_path), "alpha", "Alpha")
    vp = publish_project_snapshot_tool(str(tmp_path), "alpha")
    assert vp["scope"] == "project"
    assert vp["release"] == "vP1"
    assert callable(publish_service_tool)


def test_minted_slug_is_stable_across_label_change(plot_root: Path) -> None:
    """Explicit-slug invariant: once minted (keyed on node id), the slug does
    not move when the label changes — that is what makes it a stable contract."""
    from plot_mcp.format_f import mint_slug

    create_project(plot_root, "alpha", "Alpha")
    foundation = read_canvas(plot_root, "alpha", "foundation")
    cv = next(n for n in foundation.nodes if n.kind == "core_value")
    s1 = mint_slug(plot_root, "alpha", cv)
    s2 = mint_slug(plot_root, "alpha", cv.model_copy(update={"label": "Totally Renamed"}))
    assert s1 == s2
    assert s1.startswith("core_value/")
