---
id: W-00000275
title: Stage에서 현재 기준과 실제 결과를 확인하고 작업을 이어간다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_handoff_packet.py -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 stage/scripts/audit_stage.py --project-root ."
  - "git diff --check"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000275
promotion: not_applicable
review: passed
scope: stage/scripts/, stage/skills/, stage/docs/, stage/README.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000275 Stage에서 현재 기준과 실제 결과를 확인하고 작업을 이어간다

## Purpose

AI 세션이 바뀌어도 프로젝트의 목적과 현재 기준을 따라 남은 작업을 이어갈 수 있게 합니다

## Actions

W-00000273의 약속과 W-00000274의 조회 경로를 바탕으로 좁은 실행 항목을 정합니다.

검토를 마친 `.stage/research/llm-work/implementation-design.md`의 Stage 계약을 구현합니다.
실제 파일과 기준이 바뀌는 사례를 먼저 실패하는 테스트로 확인합니다.
생산자의 공개 CLI만 호출하고, 형제 플러그인의 코드나 DB를 직접 읽지 않습니다.
독립 검토 뒤 확인된 Distill·Avatar 명령 출력을 연결 시험에도 사용합니다.

## User value

새 세션에서 이미 한 일을 반복하거나 옛 기준을 적용하는 일을 줄입니다.

## Scope

### Included

- 프로젝트 목적을 먼저 읽고 적용할 기준과 출처를 전달하는 명시적인 경로를 제공합니다.
- 인계 자료에 기준의 식별자·버전과 실제 작업 결과를 연결합니다.
- 이어받을 때 관련 기준이 바뀌었는지 확인하고 변경을 드러냅니다.
- 스킬과 실행 코드를 연결하고 기존 기능의 회귀를 검사합니다.

### Excluded

- 현재 독립 리뷰를 저장된 판정으로 대체하지 않습니다.
- 일반 대화의 모든 판단을 가로채거나 Stage 목적을 임의로 만들지 않습니다.

## Risks

링크만 제공한 연구에서는 AI가 파일을 읽지 않았습니다. 결과를 전달하고 사용한 증거를 확인해야 합니다.
기록 시점과 실제 수정 시점이 다를 수 있습니다. 실제 파일 상태를 확인합니다.

## Success criteria

- 프로젝트 목적을 먼저 확인하고 목적만으로 정할 수 없을 때 관련 기준을 조회하는 경로를 제공합니다
- 이어받는 세션이 앞선 실제 결과와 기준의 변경을 확인할 수 있으며 대체된 기준을 그대로 현재 기준처럼 전달하지 않습니다
- Distill이나 Avatar가 없어도 기존 Stage 작업과 독립 리뷰가 정상 동작합니다

## Next action

제품별 테스트와 독립 리뷰를 마쳤습니다. W-00000277의 세 번째 시험은 실제 수신 세션 여섯 개가 모두 정상 종료했고 독립 리뷰도 통과했습니다.
2026-10-07 사용자 승인 뒤 전용 worktree의 제품 소스를 커밋했습니다. 커밋 번호는 구현·검증 기록에서 확인합니다.
작업별 회고와 완료 절차를 진행합니다.

## Related truth

SSOT, TDD, Honesty, Completion을 적용합니다. stage/CLAUDE.md와 stage/docs/PHILOSOPHY.md를 따릅니다.

## Progress

2026-10-05: 작업을 등록했습니다. 기존 드라이버와 독립 리뷰 코드는 바꾸지 않았습니다.

2026-10-06: Codex CLI의 사용량 오류 뒤 사용자가 이 세션에서 직접 구현하도록 허용했습니다. 감독이 전용 worktree에서 구현과 검사를 이어갔습니다. Claude CLI로 독립 리뷰를 받았으며, 반려된 항목은 실패 시험으로 재현하고 수정했습니다. 드라이버의 완료 판정으로 보고하지 않습니다. 제품 커밋·푸시는 아직 하지 않았습니다.

2026-10-31: 원래 제품 커밋 `4f9bb277`(`codex/criteria-stage`)과 같은 변경(`git patch-id --stable` 일치)이 배포용 커밋 `149a32cb` 로 `main` 에 들어가 있습니다. 닫기는 `149a32cb` 를 HEAD 로 둔 임시 작업 공간에서 했습니다. `.stage/` 는 `c692799e` 상태로 커밋하지 않고 덮어 썼습니다. 다만 `.stage/settings.json` 은 `149a32cb` 시점 것(`gpt-5.6-sol`)에 닫기 리뷰 프로필 네 개의 `--write` 만 더해 썼습니다. 이 카드 범위 안의 그 시점 모델 고정 시험이 `gpt-5.6-sol` 을 기대하기 때문입니다. 그래서 이 카드의 닫기 리뷰는 `gpt-6-astra` 가 아니라 `gpt-5.6-sol` 로 돌았습니다.

## Verification

좁은 연결 테스트 후 Stage hooks와 scripts 전체 unittest를 실행합니다.

2026-10-06: 실행 위치, 제품별 검사 수, 리뷰 원본과 한계는 [구현·검증 기록](../../../../research/llm-work/integration/implementation-status.md)에 모았습니다. 실제 두 호스트 인계와 제품 소스 보존이 남아 있어 이 카드를 완료로 바꾸지 않습니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_handoff_packet.py -q
[exit 0]
----------------------------------------------------------------------
Ran 18 tests in 0.267s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 376 tests in 1.867s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (296 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793426617
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793426617. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp47qi7fh2/unattended/W-00000001-1793426617
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
Ran 655 tests in 122.035s

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

$ git diff --check
[exit 0]

```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000275.md
```

## Retrospective

[R-00000275](../../../retrospectives/R-00000275.md).

## Promotion decision

이 카드는 결정이나 승격 경로를 소유하지 않으므로 `not_applicable`이다.
