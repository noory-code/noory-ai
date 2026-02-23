"""evonest_personas — List, enable, and disable personas and adversarials."""

from __future__ import annotations

from evonest.server import mcp


def _format_list(
    personas: list[dict],
    adversarials: list[dict],
    personas_toggle: dict[str, bool],
    adversarials_toggle: dict[str, bool],
    group_filter: str | None = None,
) -> str:
    """Format a readable persona/adversarial listing with enabled/disabled status."""
    lines: list[str] = []

    # Group personas
    groups: dict[str, list[dict]] = {}
    for p in personas:
        g = p.get("group", "other")
        groups.setdefault(g, []).append(p)

    # Filter groups if requested
    if group_filter:
        groups = {k: v for k, v in groups.items() if k == group_filter}

    total = sum(len(v) for v in groups.values())
    lines.append(f"## Personas ({total})")
    lines.append("")

    for group_name in sorted(groups.keys()):
        items = sorted(groups[group_name], key=lambda p: p.get("id", ""))
        lines.append(f"### {group_name} ({len(items)})")
        for p in items:
            pid = p.get("id", "")
            name = p.get("name", "")
            disabled = personas_toggle.get(pid, True) is False
            mark = "x" if disabled else "o"
            suffix = " (disabled)" if disabled else ""
            lines.append(f"  [{mark}] {pid} — {name}{suffix}")
        lines.append("")

    # Adversarials
    if not group_filter:
        lines.append(f"## Adversarials ({len(adversarials)})")
        lines.append("")
        for a in sorted(adversarials, key=lambda a: a.get("id", "")):
            aid = a.get("id", "")
            name = a.get("name", "")
            disabled = adversarials_toggle.get(aid, True) is False
            mark = "x" if disabled else "o"
            suffix = " (disabled)" if disabled else ""
            lines.append(f"  [{mark}] {aid} — {name}{suffix}")
        lines.append("")

    # Summary
    all_disabled = [pid for pid, on in personas_toggle.items() if not on]
    all_disabled += [aid for aid, on in adversarials_toggle.items() if not on]
    if all_disabled:
        lines.append(f"Disabled: {', '.join(all_disabled)}")
    else:
        lines.append("All personas and adversarials are enabled.")

    return "\n".join(lines)


@mcp.tool()
async def evonest_personas(
    project: str,
    action: str = "list",
    ids: list[str] | None = None,
    group: str | None = None,
) -> str:
    """List, enable, or disable personas and adversarials.

    Args:
        project: Path to the target project.
        action: "list" to show all, "enable" to enable IDs, "disable" to disable IDs.
        ids: Persona or adversarial IDs to enable/disable.
        group: Filter by group (biz, tech, quality) — only for list action.
    """
    from evonest.core.config import EvonestConfig
    from evonest.core.mutations import list_all_adversarials, list_all_personas
    from evonest.core.state import ProjectState

    state = ProjectState(project)
    cfg = EvonestConfig.load(project)

    personas = list_all_personas(state)
    adversarials = list_all_adversarials(state)

    # Collect all known IDs for validation
    all_persona_ids = {p.get("id") for p in personas}
    all_adversarial_ids = {a.get("id") for a in adversarials}
    all_ids = all_persona_ids | all_adversarial_ids

    if action == "list":
        return _format_list(
            personas,
            adversarials,
            cfg.personas,
            cfg.adversarials,
            group_filter=group,
        )

    if action not in ("enable", "disable"):
        return f"Error: unknown action '{action}'. Use 'list', 'enable', or 'disable'."

    if not ids:
        return "Error: ids required for enable/disable action."

    # Validate IDs
    unknown = [i for i in ids if i not in all_ids]
    if unknown:
        return f"Error: unknown IDs: {', '.join(unknown)}"

    if action == "disable":
        for i in ids:
            if i in all_persona_ids:
                cfg.personas[i] = False
            elif i in all_adversarial_ids:
                cfg.adversarials[i] = False
        cfg.save()
        return f"Disabled: {', '.join(ids)}\n\n" + _format_list(
            personas,
            adversarials,
            cfg.personas,
            cfg.adversarials,
        )

    if action == "enable":
        for i in ids:
            if i in all_persona_ids:
                cfg.personas[i] = True
            if i in all_adversarial_ids:
                cfg.adversarials[i] = True
        cfg.save()
        return f"Enabled: {', '.join(ids)}\n\n" + _format_list(
            personas,
            adversarials,
            cfg.personas,
            cfg.adversarials,
        )

    # unreachable — action already validated above
    return f"Error: unknown action '{action}'. Use 'list', 'enable', or 'disable'."
