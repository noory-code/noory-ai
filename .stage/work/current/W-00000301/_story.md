---
id: W-00000301
title: worktree에 들어간 Claude 세션에서 훅이 그 worktree를 작업 루트로 판정하게 한다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_worktree_workspace_root.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000301
promotion: not_applicable
review: passed
scope: stage/hooks/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs: DE-00000084
---

# W-00000301 worktree에 들어간 Claude 세션에서 훅이 그 worktree를 작업 루트로 판정하게 한다

## Purpose

Claude Code 세션이 같은 저장소의 linked worktree로 들어가도 훅이 원래 checkout을 작업 루트로 잡아 worktree의 .stage 편집과 작업 등록을 막는 것을 고친다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Given 같은 저장소의 linked worktree에 들어간 Claude 세션(훅 입력 cwd는 worktree 안, CLAUDE_PROJECT_DIR는 원래 checkout), When 그 worktree의 파일을 편집하면, Then 훅은 그 worktree를 작업 루트로 판정한다: worktree의 .stage/ 편집은 원래 checkout에서처럼 governed가 아니고, 열린 작업 항목은 worktree의 .stage/에서 찾는다
- 드라이버가 고정한 환경, CLAUDE_PROJECT_DIR가 없고 cwd만 있는 Codex 훅, worktree 밖의 cwd, 다른 저장소의 worktree에서는 작업 루트 판정이 지금과 같다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: `_entered_worktree` in `stage/hooks/stage_guard.py` now moves the root only when CLAUDE_PROJECT_DIR is the sole binding (no `PROJECT_ROOT` or `STAGE_PROJECT_ROOT`) and names a main checkout; `stage/hooks/tests/test_worktree_workspace_root.py` adds a sibling worktree and the driver binding (both variables, with and without `STAGE_PROJECT_ROOT`); `stage/CHANGELOG.md` states which session moves.
Why: The Codex close review found that a driver-pinned root A moved to a sibling linked worktree B when the payload cwd sat in B, for both a main-checkout A and a linked-worktree A, which breaks success criterion 2.
Decisions made: The driver's binding is recognized by `PROJECT_ROOT` or `STAGE_PROJECT_ROOT`, which `driver_environment.project_environment` and the executor and reviewer environments always set and Claude Code does not document; a session that started inside a worktree keeps that worktree even when cwd moves to a sibling; only a main-checkout root (a `.git` directory) can move; Claude implemented under venue exception DE-00000084 at the user's request.
Work not done: The desktop app's worktree sessions, which the worktrees doc says run hooks "in that root", were not exercised; the fix reaches installed sessions only after a release and plugin update.
```

## Verification


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_worktree_workspace_root.py -q
[exit 0]
----------------------------------------------------------------------
Ran 15 tests in 3.073s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 393 tests in 5.380s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793455660
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793455660. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp2tng3cpd/unattended/W-00000001-1793455660
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
Ran 704 tests in 139.343s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000301.md
Criteria:
- PASS: Given 같은 저장소의 linked worktree에 들어간 Claude 세션(훅 입력 cwd는 worktree 안, CLAUDE_PROJECT_DIR는 원래 checkout), When 그 worktree의 파일을 편집하면, Then 훅은 그 worktree를 작업 루트로 판정한다: worktree의 .stage/ 편집은 원래 checkout에서처럼 governed가 아니고, 열린 작업 항목은 worktree의 .stage/에서 찾는다
  Reason: 실제 Git worktree를 만드는 테스트에서 루트와 하위 디렉터리의 cwd가 해당 worktree로 판정되고, .stage 편집 허용과 그 worktree의 열린 작업 조회를 확인했습니다. 원래 checkout에만 열린 작업이 있으면 소스 편집을 거절하며, 별도 재현에서 저장소 바깥 경로의 linked worktree도 올바르게 선택했습니다. 최신 Decisions made와 Work not done은 구현 판단, venue 예외, 데스크톱 앱 미검증과 릴리스 필요를 명시하며, 보고한 변경 경로 8개가 실제 변경과 일치하고 모두 scope 안에 있어 목적과 범위 경계 보고 계약을 지켰습니다.
- PASS: 드라이버가 고정한 환경, CLAUDE_PROJECT_DIR가 없고 cwd만 있는 Codex 훅, worktree 밖의 cwd, 다른 저장소의 worktree에서는 작업 루트 판정이 지금과 같다
  Reason: PROJECT_ROOT 또는 STAGE_PROJECT_ROOT가 있으면 worktree 전환을 건너뜁니다. 별도 재현에서 원래 checkout과 linked worktree 두 루트, 고정 변수 세 조합, cwd 여섯 위치를 조합한 36가지 경우 모두 고정 루트를 유지했습니다. 집중 테스트 15개와 전체 훅 테스트 393개가 통과했으며, Codex cwd 전용 입력, worktree 밖 cwd, 다른 저장소의 worktree에서도 기존 판정을 유지했습니다. 이전 실패를 수용한 이유와 수정 범위도 최신 보고에 명시했습니다.
```

## Retrospective


## Promotion decision
