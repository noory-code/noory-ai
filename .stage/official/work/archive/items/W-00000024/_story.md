---
id: W-00000024
title: No guard against duplicate retrospective ids across present and archive
kind: fix
venue: codex
priority: harness integrity
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000024
promotion: not_applicable
scope: stage/scripts/,stage/skills/stage-retrospective/,stage/skills/stage-archive/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000024 No guard against duplicate retrospective ids across present and archive

## Purpose

Nothing validates that a new R-id is globally unique; the audit only cross-checks work_item linkage after the fact. Root cause of the 2026-07-13 clobber (new retro numbered from present/ only, ignoring archive/).

## Source

Observed while operating the Stage harness in novel-workspace (2026-07-12/13); details in that
project's memory note stage-plugin-defects-observed.

## User value

Audit rule (or close_work check) that R-ids are unique across present/work/retrospectives and past/work/archive/retrospectives.

## Scope

### Included

- stage/skills + a regression test per the fix note above.

### Excluded

- Behavior changes beyond the defect.

## Dependencies

None.

## Progress

- 2026-07-13: 현재·보관 회고에 같은 R-ID가 존재하는 감사 테스트와, 다른 작업의 보관
  회고 ID를 재사용한 채 닫기를 시도하는 테스트를 red-first로 추가했다.
- 2026-07-13: 감사에 `RETRO003` 전역 회고 ID 규칙을 추가하고, `close_work.py`가 검증
  실행과 상태 변경 전에 다른 `work_item`의 보관 회고 충돌을 거부하도록 수정했다.

## Verification

### Executed at close — 2026-07-13

```
$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision
