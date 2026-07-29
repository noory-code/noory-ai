---
id: W-00000021
title: archive_work.py review-row removal misses hand-written rows
kind: fix
venue: codex
priority: harness integrity
status: archived
verification: passed
retrospective: completed
retrospective_ref: R-00000021
promotion: not_applicable
scope: stage/skills/stage-archive/,stage/scripts/tests/,stage/CHANGELOG.md,stage/.claude-plugin/plugin.json,stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000021 archive_work.py review-row removal misses hand-written rows

## Purpose

The archiver's review.md row removal only matches machine-generated rows (

## Source

Observed while operating the Stage harness in novel-workspace (2026-07-12/13); details in that
project's memory note stage-plugin-defects-observed.

## User value

 W-NNNNNNNN | ... |). Rows whose artifact column is free text survive archiving and trip INDEX002. Observed 2026-07-12 in novel-workspace: W-1/7/12/13/14 rows needed manual removal while W-15's machine row was removed fine.|Match rows by the item link (items/W-NNNNNNNN.md) instead of the whole-row shape, and add a test with a hand-written row.

## Scope

### Included

- stage/skills + a regression test per the fix note above.

### Excluded

- Behavior changes beyond the defect.

## Dependencies

None.

## Progress

- 2026-07-13: `review.md` 행 삭제 기준을 artifact 열의 고정 형태에서
  `items/W-NNNNNNNN.md` 항목 링크로 변경했다. 손으로 작성한 artifact 열을 포함한 회귀
  테스트가 수정 전 실패하고 수정 후 통과함을 확인했으며, 기존 기계 생성 행 테스트도
  유지했다.

## Verification

Executed this session:

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 3
Migration complete.
  unchanged operations/verification.md (unchanged)
Migration complete.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 3
Migration complete.
----------------------------------------------------------------------
Ran 173 tests in 5.288s

OK

$ python3 stage/scripts/audit_stage.py --project-root . --strict
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision
