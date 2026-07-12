---
name: plainly-configure
description: List, inspect, select, reset, or override Plainly response-style profiles for the active project. Use when the user asks to change how the AI writes, choose a built-in Plainly style, configure a project-owned external style file, or view the active style.
---

# Plainly Configure

Use Plainly's deterministic configuration script at
`${CLAUDE_PLUGIN_ROOT}/scripts/configure.py`. If the host does not expand that variable, resolve the
plugin root two directories above this `SKILL.md` and use the same `scripts/configure.py` path.

## Project ownership

- Plainly persists settings only at `<workspace>/.plainly/settings.json`.
- Pass the active workspace root through `--project-root`.
- Environment variables remain temporary overrides; there is no persisted user-global scope.

## Commands

Run the corresponding command with `python3`:

```text
<cli> list
<cli> show --project-root <workspace>
<cli> set-profile <profile> --project-root <workspace>
<cli> set-file <path> --project-root <workspace>
<cli> reset --project-root <workspace>
```

Do not hand-edit settings. The script validates profile names and style files and writes settings
atomically. Report the project root and note that the new style applies from the next user prompt.

## Behavior

- `set-profile` replaces any saved external style file for the project.
- `set-file` replaces any saved built-in profile for the project.
- `set-file` accepts only files that resolve inside the project root.
- `reset` removes the project's saved settings.
- Environment overrides remain higher priority than saved settings.
