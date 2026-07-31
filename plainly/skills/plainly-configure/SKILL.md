---
name: plainly-configure
description: Interview the user, list, inspect, select, reset, or override Plainly response styles for the active project. Use when the user asks to personalize how the AI writes, choose a built-in Plainly style, configure a project-owned external style file, or view the active style.
---

# Plainly Configure

Use Plainly's deterministic configuration script at
`${CLAUDE_PLUGIN_ROOT}/scripts/configure.py`. If the host does not expand that variable, resolve the
plugin root two directories above this `SKILL.md` and use the same `scripts/configure.py` path.

## Where settings live

- A project's choice lives at `<workspace>/.plainly/settings.json`. Pass the workspace root through
  `--project-root`.
- The person's own default lives at `<home>/.plainly/settings.json` and applies wherever a project
  pins nothing. Reach it with `--user`.
- A project always wins over that default. Ask which one the request means before writing either.
- The user-wide file may name a built-in profile only. An external style file there would read from
  outside every project it applies to, so `set-file` has no `--user` form.
- Environment variables remain temporary overrides.

## Commands

Run the corresponding command with `python3`:

```text
<cli> list
<cli> show --project-root <workspace>
<cli> set-profile <profile> --project-root <workspace>
<cli> set-profile <profile> --user
<cli> set-file <path> --project-root <workspace>
<cli> apply-interview --length <standard|shortest> --structure <direct|step-by-step> --tone <conversational|formal> --project-root <workspace>
<cli> reset --project-root <workspace>
<cli> reset --user
```

Do not hand-edit settings. The script validates profile names and style files and writes settings
atomically. Report the project root and note that the new style applies from the next user prompt.

## Onboarding interview

When the user asks to personalize Plainly without naming a profile, conduct this interview. Ask one
question at a time, in the order below. Show both example answers side by side and ask the user to
choose A or B. Do not mention profile names or style terminology while asking.

| Axis | A | B | Record |
|---|---|---|---|
| Length | "The link expires in 10 minutes. Open it to reset your password." | "Reset it within 10 minutes." | A = `standard`; B = `shortest` |
| Structure | "Open Settings, select Security, then turn on two-step verification." | "To turn it on: 1) Open Settings. 2) Select Security. 3) Enable two-step verification." | A = `direct`; B = `step-by-step` |
| Tone | "The report is ready. I recommend reviewing the risks next." | "The report is complete. The recommended next action is a review of the identified risks." | A = `conversational`; B = `formal` |

After all three answers, run `apply-interview` with the recorded values. The script maps an exact
zero-or-one preference delta to the nearest built-in preset: baseline, brief, guided, or
professional. A combination with two or three deltas has no exact preset; only then the script
atomically writes `<workspace>/.plainly/interview-style.md`, validates it through the same
project-confined file-selection path as `set-file`, and points settings at that file. Never create
or edit the custom file by hand.

## Behavior

- `set-profile` replaces any saved external style file for the project.
- `set-file` replaces any saved built-in profile for the project.
- `plain` remains accepted as a compatibility alias for `baseline`.
- `apply-interview` writes a custom style only when no built-in preset exactly matches all answers.
- `set-file` accepts only files that resolve inside the project root.
- `reset` removes the project's saved settings.
- Environment overrides remain higher priority than saved settings.
