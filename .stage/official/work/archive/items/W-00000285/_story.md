---
id: W-00000285
title: Codex 드라이버 명령에 gpt-6-sol 모델을 다시 적는다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage.scripts.tests.test_template_v4 -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000285
promotion: not_applicable
review: not_required
scope: .stage/settings.json, stage/scripts/tests/test_template_v4.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000285 Codex 드라이버 명령에 gpt-6-sol 모델을 다시 적는다

## Purpose

드라이버가 사용자 홈 설정과 상관없이 정해진 Codex 모델로 돌고, 그 사실을 지키는 Stage 시험이 다시 통과한다.

## Actions

1. `.stage/settings.json`에서 `executors.codex`, `review.reviewers.codex`, `review.strengths`의 `light`·`standard`·`deep`·`red-team` 명령 여섯 개의 `codex-companion.mjs" task` 뒤에 `--model gpt-6-sol`을 넣는다. 나머지 문장은 바꾸지 않는다. preflight·reaper 명령은 바꾸지 않는다.
2. `stage/scripts/tests/test_template_v4.py`의 `test_project_pins_the_current_model_in_all_eight_driver_commands`가 Codex 명령에 `--model gpt-6-sol`을 기대하게 한다.
3. `stage/CHANGELOG.md` Unreleased에 한 줄 적는다.

## User value

2026-10-12 커밋 `5dcc858d`가 Codex 명령의 모델 고정(`gpt-5.6-sol`, 용량 부족으로 거절됨)을 빼서 홈 설정을 따르게 했다. 그 뒤 Stage 시험 6개가 실패하고 있었다. 플러그인 템플릿은 "모든 명령에 모델을 직접 적고 홈 기본값에 기대지 않는다"고 한다. 사용자가 2026-10-15 지금 홈 설정의 모델인 `gpt-6-sol`로 다시 고정하기로 정했다.

## Scope

### Included


### Excluded


## Risks


## Success criteria

- 이 저장소 .stage/settings.json의 Codex 실행 명령, Codex 리뷰 명령, 리뷰 강도 명령 4개(light, standard, deep, red-team)가 모두 --model gpt-6-sol을 담고, Claude 명령 두 개는 지금처럼 --model 'opus[1m]'을 담는다
- test_template_v4의 모델 고정 시험이 gpt-6-sol을 기대하고, python3 -m unittest discover -s stage/scripts/tests -q 전체가 통과한다
- stage CHANGELOG Unreleased에 이 변경이 적힌다

## Next action


## Related truth


## Progress

드라이버 1판의 변경 내용은 `.stage/.runtime/driver/logs/W-00000285.md`에 있다. 1판 리뷰가 기준 3개를 모두 승인했다(`.stage/.runtime/driver/verdicts/W-00000285.json`).

## Verification

2026-10-15 Claude가 직접 확인했다.

- 리뷰어는 지시상 `git diff`를 쓰지 않아 "나머지 문장은 그대로"를 글자 단위로 확인하지 못했다고 적었다. Claude가 `git diff --word-diff=porcelain .stage/settings.json`으로 봤고, 바뀐 낱말은 `--model gpt-6-sol` 추가 6개뿐이다.
- 리뷰어의 다른 지적: Codex가 명령으로 넘긴 `gpt-6-sol`을 받아들이는지는 다음 noory-ai 드라이버 실행에서 처음 확인된다(defer — 오늘 Codex 실행은 모두 홈 설정 `gpt-6-sol`로 돌았으므로 모델 자체는 쓸 수 있다). CHANGELOG Unreleased의 다른 줄은 W-00000284 것이다(no change needed).
- 닫을 때 Stage scripts 전체 시험을 검사로 돌린다(아래 기록).

### Executed at close — 2026-10-15

```
$ python3 -m unittest stage.scripts.tests.test_template_v4 -q
[exit 0]
----------------------------------------------------------------------
Ran 22 tests in 0.010s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1792043924
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1792043924. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpv5vdqzhp/unattended/W-00000001-1792043924
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
Ran 659 tests in 135.176s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 1.794s

OK
```

## Retrospective

[R-00000285](../../retrospectives/R-00000285.md).

## Promotion decision

이 작업 카드가 소유한 결정이나 승격 경로가 없으므로 `not_applicable`이다.
