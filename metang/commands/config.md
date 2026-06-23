---
description: View or change metang settings — toggle on/off, seed the current defaults, customize the explaining/asking rules, or reset
argument-hint: "[on|off|status|init|reset|explain <text>|ask <text>] [global]"
---

The plugin's current built-in defaults (single source — the hook script):

```
!`python3 ${CLAUDE_PLUGIN_ROOT}/hooks/metang_hook.py --dump-defaults`
```

Manage the metang plugin's `.metang.json` config based on the arguments: `$ARGUMENTS`

**Target file:**
- Default: `.metang.json` in the current project root.
- If the arguments contain the word `global`: `~/.metang.json` instead.

**Steps:**

1. Pick the target file per the rule above. If it exists, read it (it is JSON); otherwise treat the current config as `{}`.

2. Interpret the first argument (ignore a trailing `global`):
   - empty or `status` → Do NOT edit. Report: target file path, whether it exists, the effective `enabled` value (default `true` when unset), and whether `explainRules` / `askRules` are customized. Then stop.
   - `on` → set `"enabled": true`.
   - `off` → set `"enabled": false`.
   - `init` → write the current built-in defaults (shown above) into the target file, so the user has the live behavior as an editable starting point. Overwrite the file with that JSON.
   - `reset` → delete the `enabled`, `explainRules`, and `askRules` keys (restore built-in defaults).
   - `explain` → set `"explainRules"` to the text that follows the word `explain`.
   - `ask` → set `"askRules"` to the text that follows the word `ask`.
   - anything else → list the valid actions and stop.

3. For an edit action: write the merged JSON back to the target file, 2-space indented, preserving any keys you did not touch.

4. Confirm what changed in one line. Note that the hook reads this file every turn, so the change applies from the next message — no restart needed.
