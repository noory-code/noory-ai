---
id: W-00000288
title: 상태 기록의 work_items 연결 검사가 계획 칸 카드도 센다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000288
promotion: not_applicable
review: passed
scope: stage
promotes:
decision_refs:
---

# W-00000288 상태 기록의 work_items 연결 검사가 계획 칸 카드도 센다

## Purpose

STATE001(audit_state_links)이 상태 기록의 work_items 를 진행 중·보관 카드에만 대조해 계획 칸 카드를 가리키는 상태 기록을 없는 카드로 보고하는데, operations/artifacts.md 는 상태 기록이 관련 카드를 잇는 것을 막지 않고 상위 카드 검사(audit_stage.py:786)는 이미 계획 칸 카드를 세므로, 상태 기록 연결 검사도 계획 칸 카드를 세게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- work_items 가 work/planned/ 의 카드를 가리키는 상태 기록은 감사를 통과하고, 어디에도 없는 카드를 가리키면 여전히 STATE001 로 실패한다. scripts unittest 가 두 경우를 고정하고 hooks·scripts 시험이 모두 통과한다. novel-workspace 감사에서 Q-00000037 오류(계획 칸 W-00000437 연결)가 사라진다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: 상태 기록의 work_items 검사에서 계획 카드도 인정하도록 수정했습니다. 현재·보관 카드와 계획 카드의 epic/story/action 연결을 Q/O/A/K 기록의 현재·보관 위치 8가지 조합으로 시험하고, 유효한 참조와 없는 참조가 섞여도 없는 참조만 STATE001로 보고하는지 확인했습니다. stage/CHANGELOG.md의 Unreleased에 변경을 적고 카드의 promotion을 not_applicable로 설정했습니다.
Why: 존재하는 계획 카드를 없는 카드로 잘못 보고하던 오류를 없애고, 실제로 없는 카드를 찾는 검사는 유지하기 위해서입니다.
Decisions made: 공통 graph.work_ids의 의미는 유지하고 audit_state_links에서 기존 graph.backlog_by_id도 조회하기로 했습니다. 테스트를 먼저 실패시킨 뒤 수정했습니다. 첫 전체 시험에서는 드라이버의 GIT_INDEX_FILE이 테스트용 저장소에 섞여 hooks가 실패하고 scripts에서 Git 오류가 반복되어 scripts 실행을 중단했습니다. 두 전체 시험과 저장소 diff 검사는 해당 프로세스에서만 GIT_INDEX_FILE을 해제해 다시 실행했습니다. 플러그인 버전은 변경하지 않았습니다. 연결된 결정과 승격 경로가 없어 promotion을 not_applicable로 정했습니다. scope는 그대로 두었습니다. stage 범위 밖에서는 요청받은 .stage/work/current/W-00000288/_story.md의 promotion과 .stage/.runtime/driver/logs/W-00000288.md만 변경했습니다. 성공 기준 확인을 위해 /Users/woogis/Workspace/novel-workspace를 읽기 전용으로 감사했습니다.
Work not done: 독립 리뷰와 카드 종료는 드라이버의 후속 절차로 남아 있습니다.
```

## Verification


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793455535
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793455535. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpe0v7kklc/unattended/W-00000001-1793455535
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 710 tests in 143.020s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 2.409s

OK

$ python3 stage/scripts/audit_stage.py --project-root /Users/woogis/Workspace/novel-workspace
[exit 0]
... (3 earlier lines omitted)
 work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000053/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000054/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000059/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000073/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000075/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000077/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000078/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK028 [.stage/official/work/archive/items/W-00000133/_story.md]: Purpose is empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000133/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK028 [.stage/official/work/archive/items/W-00000134/_story.md]: Purpose is empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000134/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK028 [.stage/official/work/archive/items/W-00000135/_story.md]: Purpose is empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000135/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING KIND001 [.stage/official/work/archive/items/W-00000377/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000438/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000440/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000441/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000445/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000446/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000498/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING KIND001 [.stage/official/work/archive/items/W-00000509/_story.md]: Work kind `research` has no `passed` criterion in operations/verification.md.
WARNING GOV002 [.stage/settings.json]: Governance excludes paths/extensions from the broad default: playground, temp
Summary: errors=0, warnings=41
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000288.md
Criteria:
- PASS: work_items 가 work/planned/ 의 카드를 가리키는 상태 기록은 감사를 통과하고, 어디에도 없는 카드를 가리키면 여전히 STATE001 로 실패한다. scripts unittest 가 두 경우를 고정하고 hooks·scripts 시험이 모두 통과한다. novel-workspace 감사에서 Q-00000037 오류(계획 칸 W-00000437 연결)가 사라진다
  Reason: audit_state_links가 현재·보관 카드와 계획 카드를 함께 조회합니다. 회귀 시험 2개는 Q/O/A/K의 현재·보관 위치 8가지 조합에서 계획 epic/story/action 참조를 인정하고, 유효한 참조와 섞인 없는 카드에는 STATE001을 냅니다. 수정 전 조건을 메모리에서 적용하면 9개 사례가 실패합니다. GIT_INDEX_FILE을 해제한 hooks 378개와 scripts 710개 시험이 모두 통과했습니다. novel-workspace 감사는 오류 0건·경고 41건이며 Q-00000037의 계획 카드 W-00000437 참조 오류가 사라졌습니다. 최신 Decisions made와 Work not done은 구현 선택, 범위 밖 카드·로그 변경, 외부 작업 공간의 읽기 전용 감사와 후속 종료 절차를 명시하여 목적과 범위 보고 계약을 지켰습니다.
```

## Retrospective
[R-00000288](../../retrospectives/R-00000288.md).

## Promotion decision

이 카드는 결정을 소유하지 않으므로 `not_applicable`이다.
