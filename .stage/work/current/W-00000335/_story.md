---
id: W-00000335
title: cd 로 들어간 폴더 아래에서도 같은 명령에서 정한 변수 경로를 풀어 범위 알림에서 뺀다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000335
promotion: not_applicable
review: passed
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md, .stage/state/observations/O-00000057.md, .stage/state/current.md
promotes:
decision_refs:
---

# W-00000335 cd 로 들어간 폴더 아래에서도 같은 명령에서 정한 변수 경로를 풀어 범위 알림에서 뺀다

## Purpose

cd 로 다른 폴더에 들어간 뒤 같은 명령에서 정한 변수 경로에 쓸 때 훅이 그 경로를 프로젝트 파일로 잘못 알리지 않게 한다

## Actions

없음 — 변수를 푸는 함수 한 곳을 고치고 테스트를 더하는 일이라 나누지 않는다.

## User value

`cd 다른폴더 && S=/tmp/... && cat > "$S/a.md"` 처럼 쓰는 명령에 범위를 넘었다는 알림과 전체
작업 맥락이 더 붙지 않는다. 보고서나 PR 본문을 임시 폴더에 쓰는 명령에서 자주 나오는 모양이다.

## Scope

### Included

- 훅이 쓰기 대상 경로를 `cd` 한 폴더 아래로 붙여 읽은 경우에도, 그 경로가 같은 명령에서 정한
  변수로 시작했으면 그 변수를 풀어서 판정한다.
- 변수 값이 절대 경로면 `cd` 한 폴더를 떼고 그 값으로 읽는다. 상대 경로면 지금처럼 `cd` 한
  폴더 아래로 읽는다.
- 쓰기 대상이 실제로 변수로 시작했는지는 명령에 적힌 인자로 확인한다. 경로 가운데에 변수가
  있는 인자(`dir/$S/x`)는 지금처럼 둔다.
- O-00000057 을 원인과 함께 닫는다.

### Excluded

- 등록 게이트, 커밋 게이트, `.stage` 게이트는 바꾸지 않는다. 범위 알림만 바뀐다.
- `.stage/.runtime/` 아래 쓰기를 범위 알림에서 빼는 일은 하지 않는다. 같은 날 따로 본 경우라
  관찰로 남길지 따로 정한다.

## Risks

- 인자가 변수로 시작했는지 확인하는 방법이 명령 글자를 다시 읽는 것이라, 따옴표나 리다이렉트를
  특이하게 쓴 명령에서는 놓칠 수 있다. 놓치면 지금처럼 알린다(알림이 남는 쪽으로 틀린다).
- `stage/hooks/` 를 고치는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).

## Success criteria

- cd 로 프로젝트 안 폴더에 들어간 뒤 같은 명령에서 프로젝트 밖 절대 경로로 정한 변수에 쓰면 범위를 넘었다고 알리지 않는다
- 변수 값이 상대 경로이면 지금처럼 cd 한 폴더 아래 경로로 읽는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다
- O-00000057 에 원인과 고친 곳을 적고 닫는다

## Next action

`test_stage_guard.py` 에 깨지는 테스트를 먼저 쓰고 `expand_leading_shell_variable` 을 고친다.

## Related truth

- O-00000057 — 이 카드가 닫을 관찰.
- W-00000332 — 같은 명령에서 정한 변수 경로를 범위 알림에서 뺀 카드(보관됨). 그때는 경로가
  변수로 시작하는 경우만 다뤘다.
- DE-00000086 — codex 가 없는 로컬 세션에서 Claude 가 실행하고 닫기 리뷰를 따로 받는다.
- DE-00000087 — `stage/hooks/` 를 바꾸는 카드는 사용자 확인 뒤에 닫는다.

## Progress

- 2026-11-16: `origin/main`(82e8f7cc)에서 딴 worktree `claude/stage-cd-variable-target` 에서
  진행했다. venue 정책은 fix -> codex 지만 DE-00000086 에 따라 `local-no-codex` 환경에서 Claude 가
  실행했다. 팀원을 띄우지 않고 감독 세션이 직접 했다.
- 원인: 셸 파서가 `"$S/a.md"` 를 `cd` 한 폴더 아래에 붙여 `src/$S/a.md` 로 넘기고,
  `expand_leading_shell_variable` 은 경로가 변수로 시작할 때만 풀었다.
- `stage_guard.py`: `_anchored_variable_operand` 를 더했다. 경로에서 처음 나오는 `/$이름` 앞을
  떼고, 명령에 그 인자가 `$이름/…` 으로 적혀 있을 때만 그 둘로 나눈다.
  `expand_leading_shell_variable` 은 명령을 받아 이 경우를 풀고, 값이 절대 경로면 앞 폴더를 떼고
  상대 경로면 그 아래에 둔다. 범위 알림(`purpose_tool_context`)만 명령을 넘긴다.
- 테스트: 빼야 할 경우 둘(heredoc, 중괄호 변수)과 여전히 알려야 할 경우 셋(상대 값, 프로젝트를
  가리키는 절대 값, 가운데 변수)을 더했다.
- 변경 기록 `## Unreleased` 한 항목. O-00000057 은 원인을 적고 `close_record.py` 로 닫았다.
- 코드 커밋 `ce81f2b5`.

## Verification

- 판별 확인: 고치기 전에 새 테스트를 돌려 다섯 경우 중 네 경우가 깨지는 것을 봤다. 가운데
  변수 경우만 고치기 전에도 통과했다(바뀌면 안 되는 경우다). 고친 뒤 다섯 경우 모두 통과했다.
- 실제 명령으로 비교: 이 프로젝트의 최근 세션 15개에서 Bash 명령 1,396개를 고치기 전 훅과
  고친 훅에 넣었다. 프로젝트 안 경로로 판정된 대상은 178개에서 176개로, 그 가운데 풀지 못한
  변수가 남은 대상은 7개에서 5개로 줄었다. 남은 다섯은 반복문 변수(`$t`, `$B`)와 파일 이름
  가운데 변수다.
- 관찰에 적힌 원래 명령은 그 명령이 `cd` 한 폴더가 지금 없어서 다시 일으킬 수 없었다. 같은
  모양의 명령을 새로 만들어 일으켰다.
- `python3 -m unittest discover -s stage/hooks/tests -q`: 445건 통과.
- `python3 -m unittest discover -s stage/scripts/tests -q`: 757건 통과(2건 건너뜀).
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0, warnings=32(모두 보관된
  카드의 기존 경고).
- 둘째 기준: 상대 값은 `src/notes/a.md` 로 알린다(테스트 "relative value stays under the cd
  folder").
- 닫기 리뷰는 codex 가 없어 Claude 대역(`stage/scripts/claude_review_companion.py`)으로 돌린 같은
  모델의 리뷰이며, 교차 venue 리뷰가 아니다(DE-00000086).
- 사용자 확인 — 2026-11-16: `stage/hooks/` 를 바꾼 카드라 닫은 결과를 본 가지에 옮기기 전에
  사용자에게 보였다(DE-00000087). 보인 것은 바뀐 경로와 한 줄씩의 요약, 완료 기준 네 개의 리뷰
  판정과 리뷰어가 확인한 것, 리뷰어가 실행 없이 판정한 기준이 없다는 것, 같은 모델의 리뷰라는
  것, 팀원 없이 감독 세션이 직접 구현했다는 것이다. 사용자가 "확인, 닫기"로 답했다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 265 tests in 1.297s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 445 tests in 7.184s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794809764
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794809764. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmperhsylgm/unattended/W-00000001-1794809764
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
Ran 757 tests in 197.241s

OK (skipped=2)
```

### Review at close — 2026-11-16

```
Review report: .stage/.runtime/driver/logs/W-00000335.md
Criteria:
- PASS: cd 로 프로젝트 안 폴더에 들어간 뒤 같은 명령에서 프로젝트 밖 절대 경로로 정한 변수에 쓰면 범위를 넘었다고 알리지 않는다
  Reason: I ran python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q (265 tests OK); the subtests 'heredoc into a variable after cd' and 'redirect into a braced variable after cd' assert an empty scope message for an absolute out-of-project value, and _anchored_variable_operand plus the absolute branch of expand_leading_shell_variable implement it.
- PASS: 변수 값이 상대 경로이면 지금처럼 cd 한 폴더 아래 경로로 읽는다
  Reason: In the same run the subtest 'relative value stays under the cd folder' passed, asserting 'Scope boundary crossed: src/notes/a.md.'; the code joins a relative value under the anchor folder.
- PASS: 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다
  Reason: I ran the new test against the pre-fix stage_guard.py (ce81f2b5~1) in a scratch copy: 4 of 5 subtests failed (the two left-out cases, the relative case, the absolute-into-project case) and only the unchanged middle-variable case passed; with the fix all pass.
- PASS: O-00000057 에 원인과 고친 곳을 적고 닫는다
  Reason: O-00000057 now sits in .stage/official/state/archive/ with a Status naming cd anchoring as the cause and W-00000335 as the fix, a close-record block, an archive index row, and its line removed from state/current.md.
```

## Retrospective

[R-00000335](../../retrospectives/R-00000335.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
