# CLAUDE.md — flow working guidelines

This file provides the plugin-local guidelines that apply when modifying assets inside `flow/`.

## flow-upgrade impact-review obligation

Whenever you modify a `flow` asset, always review the `/flow-upgrade` command alongside it.

Review targets:

- Changes to `flow/rules/*.md`
- Changes to `flow/skills/**/SKILL.md`
- Changes to `flow/commands/*.md`
- Changes to `flow/hooks/*.py`
- Changes to `flow/docs/*.md`
- Changes to `flow/playbooks/*.md`
- Changes to the plugin manifest / marketplace version

Review criteria:

- If it is a rule change, confirm that `/flow-upgrade` still accurately describes the canonical-rule → `.claude/rules/` copy synchronization boundary.
- If it is a skill/command/hook/docs/playbook/manifest change, confirm that `/flow-upgrade` still accurately describes the boundary that "these are plugin-upgrade targets and are not copied directly."
- Do not accumulate a per-release asset list inside the body of `/flow-upgrade`. Keep change details in `CHANGELOG.md` as the SSOT.
- Record the review result in the relevant Action or Story document. If no change is needed, leave "Review result: no change needed."

## No project-specific source names

When upstreaming an external project's retrospective, do not leave project-specific source names in the release artifacts or the work SSOT. When necessary, generalize them to phrasings like "external project", "downstream", or "external retrospective".
