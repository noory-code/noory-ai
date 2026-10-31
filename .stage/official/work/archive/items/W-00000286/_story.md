---
id: W-00000286
title: 닫기 리뷰가 판정 파일을 쓰게 하고 Codex 명령을 gpt-6-astra high로 고정한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000286
promotion: not_applicable
review: passed
scope: .stage/settings.json, stage/scripts/tests/test_template_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000286 닫기 리뷰가 판정 파일을 쓰게 하고 Codex 명령을 gpt-6-astra high로 고정한다

## Purpose

close_work 로 리뷰가 필요한 카드를 닫을 때 Codex 리뷰어가 판정 파일을 직접 써서 닫기가 통과하고, 드라이버와 리뷰의 Codex 명령이 사용자가 정한 gpt-6-astra 모델과 high 생각 깊이로 돈다.

## Actions

- 지금 동작: `.stage/settings.json` 의 `review.strengths` 프로필 명령 네 개(`light`, `standard`,
  `deep`, `red-team`)는 `codex-companion.mjs task ... --fresh` 로 돌고 `--write` 가 없다.
  `--write` 가 없으면 Codex 가 읽기 전용으로 돌아 `$STAGE_REVIEW_VERDICT_FILE` 을 쓰지 못한다.
  `close_work.py` 는 `review: pending` 카드를 닫을 때 `review.stages.implementation`
  (`standard`) 명령을 부르므로, 지금은 리뷰가 승인해도 "review verdict file is missing" 으로
  닫기가 막힌다. 2026-10-31 W-00000268 닫기에서 실제로 이렇게 막혔다.
- 드라이버용 리뷰 명령 `review.reviewers.codex` 에는 2026-08-03 커밋 `e4e96af9` 에서
  `--write` 가 들어갔다. 프로필 명령 네 개에는 2026-07-12 처음 생길 때부터 없었다.
- 고칠 것 1: 프로필 명령 네 개의 `task` 인자에 `--write` 를 넣는다. 지시문 문장은 바꾸지 않는다.
- 고칠 것 2: Codex 명령 여섯 개의 `--model gpt-6-sol` 을 `--model gpt-6-astra --effort high` 로
  바꾼다. 여섯 개는 `executors.codex`, `review.reviewers.codex`, `review.strengths` 의 네 개다.
  `preflights.codex` 와 `cancel` 명령은 모델을 쓰지 않으므로 그대로 둔다.
- 사용자가 2026-10-31 "코덱스 아스트라 하이로 적극 사용하세요" 라고 정했다. 이것은 2026-10-15
  `gpt-6-sol` 고정 결정(W-00000285)을 대신한다. 같은 날 `gpt-6-astra` 에 `--effort high` 를 준
  companion task 호출이 정상 응답을 돌려준 것을 확인했다.
- `stage/scripts/tests/test_template_v4.py` 의
  `test_project_pins_the_current_model_in_all_eight_driver_commands` 기대값을 고친다. Codex 명령
  여섯 개에 `--model gpt-6-astra` 와 `--effort high` 가 모두 있는지 본다. 프로필 명령 네 개에
  `--write` 가 있는지 보는 시험을 더한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다(영어).

## User value

리뷰가 필요한 카드를 `close_work.py` 로 닫을 수 있다. W-00000268·W-00000269·W-00000270 이 모두
이 길로 닫힌다. Codex 실행과 리뷰가 사용자가 고른 모델과 깊이로 돈다.

## Scope

### Included

- 프로필 리뷰 명령 네 개가 판정 파일을 쓸 수 있게 하는 것
- Codex 명령 여섯 개의 모델과 생각 깊이
- 그 두 가지를 지키는 시험과 변경 기록 한 줄

### Excluded

- Claude 명령 두 개(`executors.claude`, `review.reviewers.claude`)의 모델
- 지시문 문장, 리뷰 단계 설정(`review.stages`), 시도 한도(`limits`)
- `stage/templates/` 의 설정 템플릿. 이 카드는 이 저장소 설정만 바꾼다.
- `close_work.py` 의 리뷰 제한 시간(W-00000270 몫)

## Risks

- 이 카드를 드라이버로 돌리는 동안 실행자가 `executors.codex` 를 바꾸면, 두 번째 시도부터는 바뀐
  모델로 돈다. `gpt-6-astra` 호출은 확인했으므로 실패 원인이 되지는 않는다.
- 리뷰어에게 쓰기 권한을 주면 리뷰어가 판정 파일 말고 다른 파일도 고칠 수 있다. 드라이버 리뷰
  명령은 이미 `--write` 로 돌고 있고, `close_work.py` 는 HEAD 커밋의 경로만 리뷰 대상으로 넘긴다.

## Success criteria

- 닫을 때 쓰는 리뷰 프로필 명령 네 개(light, standard, deep, red-team)가 모두 --write 를 가져 판정 파일을 쓸 수 있다는 것을 시험이 확인한다
- Codex 명령 여섯 개(실행, 드라이버 리뷰, 프로필 리뷰 네 개)가 모두 --model gpt-6-astra --effort high 로 돈다는 것을 시험이 확인하고, Claude 명령 두 개의 모델 고정은 그대로다

## Next action

Codex 드라이버로 실행한다. 닫을 때 `close_work.py` 의 `standard` 리뷰가 고친 명령으로 처음
돈다. 판정 파일이 써져 닫기가 통과하면 그것이 끝에서 끝까지 확인한 증거다.

## Related truth


## Progress

이번 실행의 변경 경로와 판단은 `.stage/.runtime/driver/logs/W-00000286.md`에 있다.

## Verification

2026-10-31에 카드의 필수 시험 23개, Stage scripts 전체 시험 660개, hooks 전체 시험 378개가
통과했다. Stage 감사에서는 오류가 없었고 기존 보관 카드에 대한 경고 32건이 나왔다. 전체 시험은
임시 Git 인덱스 변수 `GIT_INDEX_FILE`을 제외하고 실행했다. 실제 `close_work.py` 닫기와
독립 리뷰는 아직 실행하지 않았다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 23 tests in 0.007s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 23 tests in 0.007s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793423033
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793423033. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp88bqbu7f/unattended/W-00000001-1793423033
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
Ran 660 tests in 105.118s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 1.956s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000286.md
```

## Retrospective

[R-00000286](../../retrospectives/R-00000286.md).

## Promotion decision

이 카드에는 연결된 결정이나 승격 경로가 없어 `not_applicable`로 정했다.
