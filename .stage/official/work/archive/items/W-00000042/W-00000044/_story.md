---
id: W-00000044
title: 독립 판정 필수화 — review 훅을 자율 항목 종료 게이트로
kind: development
venue: codex
priority: 2
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000042
promotion: approved
scope: stage/hooks/stage_paths.py, stage/hooks/stage_work.py, stage/hooks/tests/, stage/skills/stage-retrospective/, stage/scripts/tests/, stage/docs/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs: DE-00000020
---

# W-00000044 독립 판정 필수화 — review 훅을 자율 항목 종료 게이트로

## Purpose

자율 대상 항목의 종료에 독립 판정(review 훅)을 필수 게이트로 강제한다. acceptance 통과해도 판정자 BLOCK 시 미종료. (DE-00000016)

## Source

parent: W-00000042 (자율 실행 드라이버 계약). 근거 결정 기록은 Purpose에 명시.

## User value

실행자의 자기 채점 위조를 막아 자율 실행을 신뢰 가능하게 한다.

## Scope

### Included

- 자율 대상 항목 종료에 review 훅(독립 판정) 필수화
- acceptance 통과 + 판정자 BLOCK = 미종료 경로

### Excluded

- 판정 로직 자체 — 기존 codex-companion review 자산 재사용

## Dependencies

W-00000043(acceptance) 이후 권장 — 종료 판정 경로 위에 얹힘.

## Risks

판정자 부재(codex-companion 미가용) 시 폴백 = 자율 불가·사람 대기.

## Success criteria

- 자율 항목은 독립 판정 없이는 종료 불가
- 판정자 BLOCK 시 재시도 또는 에스컬레이션
- 테스트 존재, audit_stage errors=0

## Next action

Codex 창에서 `start_work` W-00000044 → DE-00000016대로 구현.

## Progress

## Verification

### Executed at close — 2026-07-23

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 310 tests in 0.899s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete and strict audit clean.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete and strict audit clean.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 269 tests in 25.555s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
WARNING KIND001 [.stage/official/work/archive/items/W-00000040.md]: Work kind `bug` has no `passed` criterion in operations/verification.md.
Summary: errors=0, warnings=1
```

## Retrospective

## Promotion decision
