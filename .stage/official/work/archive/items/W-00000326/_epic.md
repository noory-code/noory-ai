---
id: W-00000326
title: 일감마다 맞는 모델과 에포트 레벨을 Stage 가 고르게 한다
kind: planning
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000326
promotion: not_applicable
review: not_required
scope: stage/
promotes:
decision_refs:
---

# W-00000326 일감마다 맞는 모델과 에포트 레벨을 Stage 가 고르게 한다

## Purpose

Stage가 일감마다 맞는 모델과 에포트 레벨을 고르게 한다

## Stories

- W-00000327 (design, claude) — 등급 표 설계와 Agent 훅 실측 결과를 카드에 남긴다. 아래 구현 story 넷이 따르는 설계의 SSOT 다.
- W-00000328 (development, claude · local-no-codex) — 등급 표 설정을 읽어 등록하는 카드에 tier 를 적는다.
- W-00000329 (development, claude · local-no-codex) — 드라이버가 카드 등급의 모델과 에포트를 실행기와 리뷰어에 넘긴다. W-00000328 의 공용 모듈을 쓴다.
- W-00000330 (development, claude · local-no-codex) — Agent 호출의 모델과 에포트를 카드 등급에 맞추는 훅을 넣는다. W-00000328 의 공용 모듈을 쓴다.
- W-00000331 (development, claude · local-no-codex) — 카드 등급과 실제로 돈 모델·에포트가 다르면 감사가 경고하게 한다. W-00000329 와 W-00000330 이 남기는 기록을 읽는다.

## User value

하위 에이전트와 드라이버 실행기가 부모 세션의 비싼 모델(Fable)을 그대로 물려받지 않는다. 일의 크기에 맞는 모델과 에포트를 설정 한 곳에서 고르고, 어긋나면 감사에서 보인다. 출발점은 다시나 프로젝트에서 하위 에이전트가 계속 Fable 로 돈 일이다.

## Scope

### Included

- `stage/` 플러그인의 설정 읽기, 등록, 드라이버 환경, Claude Code 훅, 감사
- 플러그인 문서(`stage/docs/SCHEMA_V5.md`, 관련 스킬, 훅 README)와 `stage/CHANGELOG.md` 의 `## Unreleased`

### Excluded

- 이 저장소의 `.stage/settings.json` 에 `model_tiers` 를 켜는 일 (켜지 않아도 지금처럼 돌아야 한다는 것이 완료 기준이다)
- 다시나 프로젝트 설정 변경과 릴리스(버전 올리기)
- Codex 호스트의 하위 에이전트 (Codex 에는 Agent 도구가 없다)

## Risks

- Claude Code 의 Agent 입력·SubagentStop 입력 모양이 바뀌면 훅과 기록이 조용히 빗나갈 수 있다. W-00000327 에 실측한 버전(2.1.321)을 적어 둔다.
- 등급 순서를 잘못 읽으면 싼 모델을 비싸다고 막거나 그 반대가 된다.
- `stage_guard.py` 의 작업 맥락 블록(`append_purpose_context`)을 다른 세션이 손보고 있다. 이 에픽은 `handle_event` 에서 Agent 와 SubagentStop 을 새 모듈로 넘기는 몇 줄만 고친다.


## Success criteria

- 일감을 등록하면 설정의 등급 표(일의 종류와 크기로 고름)가 고른 tier 가 카드에 남고, 프로젝트가 표를 덮어쓸 수 있으며, 사람이 카드에서 바꾼 tier 가 우선한다
- 드라이버가 실행기와 리뷰어를 부를 때 카드 등급의 그 venue 값을 STAGE_MODEL·STAGE_EFFORT 로 넘겨서, 실행기·리뷰어 명령에 모델을 박아 두지 않아도 된다
- 세션 안에서 Agent 도구로 맡길 때 모델·에포트를 적지 않은 호출과 카드 등급보다 비싼 모델을 이유 없이 고른 호출을 훅이 알려 주거나 막는다
- 카드에 적힌 등급의 모델·에포트와 드라이버 작업 기록·하위 에이전트 기록에 남은 실제 값이 다르면 감사가 경고한다
- settings 에 model_tiers 가 없는 스키마 v5 프로젝트는 설정을 바꾸지 않아도 지금과 똑같이 돈다(환경 변수 없음, 카드에 tier 없음, 훅 무동작)

## Next action


## Related truth


## Progress

- 2026-11-14: W-00000328 을 드라이버로 Codex 실행기에 맡겼으나 Codex 가 `The 'gpt-6-astra' model is not supported when using Codex with a ChatGPT account.` 로 실패했다(저장소 변경 없음). 사용자가 "local-no-codex 로 여기서 진행" 을 골라, 구현 story 넷을 `venue: claude`, `environment: local-no-codex`, `review: pending` 으로 바꿨다. 근거는 설정의 `environment_venues` 다(DE-00000082).

## Verification


### Executed at close — 2026-11-14

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 438 tests in 5.434s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794631581
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794631581. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpl90___hh/unattended/W-00000001-1794631581
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
Ran 757 tests in 149.472s

OK (skipped=2)

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

## Retrospective


## Promotion decision
