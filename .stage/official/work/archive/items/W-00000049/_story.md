---
id: W-00000049
title: unattended 드라이버 — Codex 리뷰 지적 수정 (W-48 후속)
kind: development
venue: claude
priority: 1
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000048
promotion: approved
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/skills/stage-retrospective/, stage/docs/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs: DE-00000026, DE-00000027
---

# W-00000049 unattended 드라이버 — Codex 리뷰 지적 수정 (W-48 후속)

## Purpose

W-00000048 무인 루프의 Codex 독립 리뷰(CHANGES-REQUESTED) 지적 4 P1 + 5 P2를 수정하고 재검토한다. 수정 전까지 --unattended는 사용 불가.

## Source

W-00000048 Codex 독립 리뷰(CHANGES-REQUESTED, 2026-07-23). 실행자=claude였고 자동 codex 판정 경로가 막혀, 사용자가 Codex 창에서 리뷰를 수행했다.

## User value

무인 루프를 실제로 안전하게 쓸 수 있게 한다(현재는 사용 불가).

## Scope

### Included

- `stage/scripts/drive.py`의 무인 경로(run_unattended 및 헬퍼) 수정 + 테스트 보강 + 문서.

### Excluded

- supervised dry-run/--execute 경로(변경 없음).

## Dependencies

- 없음(단, 재검토는 Codex 창 또는 복구된 codex 경로 필요).

## Risks

- **수정 전 `--unattended` 사용 금지.** P1 #4(lifecycle 미커밋)가 가장 큰 데이터-무결성 구멍.

## Success criteria

- [P1] executor 실패(`executor_ok` 미검사)를 즉시 감지해 escalate; "nothing to commit"이 실패를 삼키지 않게.
- [P1] lifecycle 기록(work card·retrospective·index·pending decision)을 run 브랜치에 커밋(현재 executor 결과만 커밋됨).
- [P1] 매 명령·커밋 전에 현재 브랜치가 run 브랜치인지 재검증(base 무수정 보장).
- [P1] 비자율 부모 close에도 독립 리뷰 보장, 또는 부모 close 계약을 명시적으로 결정·문서화.
- [P2] retrospective를 acceptance·review 통과 후에 기록(현재는 close 전에 성공 기록).
- [P2] escalate/부모 close 반환값 검사·전파.
- [P2] 전역 wall-clock을 subprocess에 적용(남은 예산으로 timeout 제한; git/close/escalate에도 timeout).
- [P2] 직접 자식뿐 아니라 서브트리 전체의 적격 leaf 선택(현재 parent==target만).
- [P2] item 커밋 전 clean index 요구/확립(기존 staged 변경 혼입 방지).
- 실제 실패 경로(executor 실패·lifecycle 커밋·브랜치 전환)를 stub 없이 커버하는 테스트 추가.
- 수정 후 Codex 독립 리뷰 재수행 → APPROVED.

## Next action

start_work → P1 4개부터 수정 → 테스트 보강 → Codex 재검토(APPROVED까지 --unattended 사용 금지).

## Progress

## Verification

### Executed at close — 2026-07-23

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 321 tests in 1.024s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784806019 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784806019
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784806019. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784806020 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784806020. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784806020 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784806020
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784806020
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784806020 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784806020
[W-00000003] completed on stage/driver/W-00000001-1784806020
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784806020. Human review + merge required; the base branch was not modified.
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
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
Ran 293 tests in 32.381s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
WARNING KIND001 [.stage/official/work/archive/items/W-00000040.md]: Work kind `bug` has no `passed` criterion in operations/verification.md.
Summary: errors=0, warnings=1
```

## Retrospective

## Promotion decision
