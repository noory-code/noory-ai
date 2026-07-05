---
name: flow-must-not
description: "Situational prohibitions for Flow. Reference for blocking procedure bypass / auto-progression / retrospective placeholders. Core rules are in the plugin rules/."
user-invocable: false
metadata:
  type: reference
  version: v1.0.0
---

# Situational prohibitions for Flow

> **The core rules live in the plugin rules/ (SSOT)** (auto-loaded when `flow-config` syncs them to the project `.claude/rules/`).
> The blocking policy (procedure bypass · auto-progression · retrospective-placeholder blocking) is enforced by the Agent Teams hooks (PreToolUse blocking).
> This file retains only the **situational supplementary prohibitions** that are not enforced by hooks and apply only in specific situations.

## Situational supplementary prohibitions

- ❌ **Running an implementation Action's spec without a prior design result** (design Action completes → its output is the spec for the next implementation Action. User confirmation is required when the spec changes)
- ❌ **Merging several independent tasks into one Action on a "it's small, so bundle it" judgment** (merging applies only the Action Planning merge criteria. No arbitrary merging without user approval)
- ❌ **Writing a "work summary / result recap" in the retrospective** (retrospective = evaluation of AI behavior, not a summary of work results)
- ❌ **Loading a completed (✅) Action file in full** (a waste of context. Load in full only in-progress (🔄) ones)
- ❌ **Using a script to write files** (use the `Write`/`Edit` tools — the tools can handle Hangul/emoji)
