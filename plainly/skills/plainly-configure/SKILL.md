---
name: plainly-configure
description: List, inspect, select, reset, or override Plainly response-style profiles. Use when the user asks to change how the AI writes, choose a built-in Plainly style, configure an external style file, view the active style, or apply a style at user or project scope.
---

# Plainly Configure

Use Plainly's deterministic configuration script at
`${CLAUDE_PLUGIN_ROOT}/scripts/configure.py`. If the host does not expand that variable, resolve the
plugin root two directories above this `SKILL.md` and use the same `scripts/configure.py` path.

## Scope

- Use `user` scope unless the user explicitly says this project, repository, or workspace only.
- Use `project` scope only for those explicit project-local requests.
- Pass the active workspace root through `--project-root`.

## Commands

Run the corresponding command with `python3`:

```text
<cli> list
<cli> show --project-root <workspace>
<cli> set-profile <profile> --scope <user|project> --project-root <workspace>
<cli> set-file <path> --scope <user|project> --project-root <workspace>
<cli> reset --scope <user|project> --project-root <workspace>
```

Do not hand-edit settings. The script validates profile names and style files and writes settings
atomically. Report the selected scope and note that the new style applies from the next user prompt.

## Behavior

- `set-profile` replaces any saved external style file at the selected scope.
- `set-file` replaces any saved built-in profile at the selected scope.
- Project-scoped `set-file` accepts only files that resolve inside the project root.
- `reset` removes only the selected scope's saved settings.
- Environment overrides remain higher priority than saved settings.
