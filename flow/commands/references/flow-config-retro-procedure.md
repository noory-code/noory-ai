# /flow-config-retro detailed procedure

Stage 3 reference for `commands/flow-config-retro.md`. The command file remains the entrypoint for retrospective policy configuration, and this file is the SSOT for the detailed procedure.

## Purpose

Inject and update the `retrospective.levels` retrospective-rigor policy in the project's `.flow/settings.json`. The AI performs ground-truth inspection of the work type and the existing retrospective pattern to make recommendations, and the user only confirms or corrects.

## Label definitions

| Label | Meaning |
|------|------|
| `none` | Retrospective exempt. However, initiative cannot be exempt |
| `minimal` | Block placeholders + at least one line of content |
| `template` | KPT format baseline |
| `template+rt` | KPT + R3 self-attack result |

The definition SSOT is `flow-retrospective` Part 4. This procedure only covers the user explanation and the injection flow.

## Phase 1: Ground-truth inspection

| Inspection target | Purpose |
|-----------|------|
| `.flow/settings.json` `playbooks[]` | Judge the ratio of work types / meta work |
| `.flow/archives/retro-*.md` | Check the existing retrospective-writing pattern |
| `.claude/rules/retro-evolution.md` | Whether the retrospective evolution loop is active |
| Active `_epic.md`/`_story.md` retrospectives | Diagnose the current retrospective depth |

## Phase 2: Recommendation

Recommended defaults:

| Level | Recommendation |
|------|------|
| action | `template`, or if it is repetitive meta work, `none` is possible after user agreement |
| story | `template` |
| epic | `template+rt` |
| initiative | `template+rt` |

When the ratio of meta / technical work is high — as with `plugin-dev`, `refactor`, `feature` — raise the rigor; when the work is mostly `docs` / simple changes, it can be lowered.

## Phase 3: User explanation and confirmation

First, explain the labels in plain terms.

```text
Retrospective rigor is how strongly the retrospective written at the end of a task is enforced.
none=exempt, minimal=block empty shells, template=KPT, template+rt=KPT+self-attack.
```

Then recommend based on the ground-truth inspection.

```text
Got it — active playbooks [list], work type [meta/simple/mixed].
Recommended: action=[X], story=[Y], epic=[Z], initiative=[W].
Shall we go with this, or would you like to adjust a specific level?
```

## Phase 4: Injection gate

The settings injection happens only after the user's explicit confirmation response.

- Silence, re-invoking the command, or simply continuing the flow is not treated as confirmation.
- If there are corrections, apply them and get confirmation again.

## Phase 5: settings patch

Preserve the existing `playbooks` / `agents` and delta-patch only `retrospective`.

```json
{
  "retrospective": {
    "levels": {
      "action": { "rigor": "template" },
      "story": { "rigor": "template" },
      "epic": { "rigor": "template+rt" },
      "initiative": { "rigor": "template+rt" }
    }
  }
}
```

## Phase 6: Installation verification

1. Confirm each level value is one of `none|minimal|template|template+rt`.
2. Confirm `initiative.rigor != none`.
3. Verify by ground-truth inspection that the hook reader reads the settings as-is.

Example:

```bash
uv run --no-project python -c "import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/hooks'); import _flow_state as ws; print(ws.read_retrospective_settings('<project root>'))"
```

## Phase 7: Re-tuning

Re-run whenever the work type or the retrospective-burden policy changes. Update only the delta, and if it is already consistent with the current settings, finish with "nothing to update".
