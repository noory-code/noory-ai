---
id: W-00000338
title: 등록 게이트도 같은 명령에서 정한 변수 경로를 풀어서 판정한다
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
retrospective_ref: R-00000338
promotion: not_applicable
review: passed
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000338 등록 게이트도 같은 명령에서 정한 변수 경로를 풀어서 판정한다

## Purpose

열린 카드가 없을 때 같은 명령에서 프로젝트 밖으로 정한 변수 경로에 쓰는 명령을 등록 게이트가 프로젝트 파일 쓰기로 보고 막지 않게 한다

## Actions

없음 — 게이트를 부르는 한 자리를 고치고 테스트와 문서를 맞추는 일이라 나누지 않는다.

## User value

열린 카드가 없는 상태에서 보고서나 PR 본문을 `S=/tmp/... && cat > "$S/x.md"` 처럼 임시 폴더에
쓰는 명령이 막히지 않는다. 2026-11-16 에 열린 카드가 0장이 되자 이 모양의 명령 두 개가 막혔다.

## Scope

### Included

- 셸 명령의 등록 게이트가 판정하기 전에, 같은 명령에서 정한 변수나 훅 환경 변수로 시작하는 쓰기
  대상을 범위 알림과 같은 방법으로 푼다.
- `stage/operations/hooks.md` 의 등록 게이트 절과 범위 알림 절을 맞춘다.

### Excluded

- 풀 수 없는 변수는 지금처럼 둔다. 게이트는 여전히 막는 쪽으로 틀린다.
- `.stage` 게이트(공식 기록, 삭제, 인라인 코드)는 바꾸지 않는다.

## Risks

- 게이트를 바꾸는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).
- 변수 풀기가 틀리면 프로젝트 안 쓰기를 밖으로 볼 수 있다. 풀기는 명령어 자리의 `이름=값` 만
  읽고 값에 변수가 들어 있으면 버린다(W-00000332). 프로젝트 안을 가리키는 값은 그대로 막힌다.

## Success criteria

- 열린 카드가 없을 때 S=프로젝트 밖 경로 다음에 "$S/파일" 에 쓰는 명령을 등록 게이트가 막지 않는다
- 변수 값이 프로젝트 안을 가리키거나 풀 수 없는 변수면 지금처럼 막는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action

닫기 리뷰를 받고 사용자 확인 뒤에 닫는다.

## Related truth

- W-00000332, W-00000335 — 범위 알림에서 같은 명령의 변수를 풀게 한 카드(보관됨).
- DE-00000086, DE-00000087 — codex 없는 로컬 실행과 게이트 카드의 사용자 확인.

## Progress

- 2026-11-16: 사용자가 "자 또 해야 할 일이 있다면 다 하죠"라고 했다. 같은 날 플레인리 에픽을 닫는
  PR 본문을 쓰다가 이 게이트에 막혔다.
- `stage_guard.py` 의 셸 쓰기 등록 게이트 호출 앞에서 `expand_leading_shell_variable` 로 대상을 푼다.
  범위 알림이 쓰는 함수와 같다.
- 테스트 `test_registration_gate_expands_a_same_command_variable_before_judging`: 통과해야 할 셋
  (리다이렉트, cd 뒤 heredoc, 중괄호 변수)과 막아야 할 둘(프로젝트 안 값, 풀 수 없는 변수).
- 코드 커밋 `2a0389b2`.

## Verification

- 판별 확인: 고치기 전에 새 테스트에서 통과해야 할 세 경우가 모두 막혔다. 막아야 할 두 경우는
  고치기 전에도 막혔다(바뀌면 안 되는 경우다). 고친 뒤 다섯 경우 모두 기대대로다.
- 세 카드(W-00000338~340)의 변경을 모두 넣고 처음 돌린 전체 테스트는 실패했다(hooks 1건, scripts
  2건, 모두 W-00000339 의 감사 검사 때문). `86c2a80e` 로 고친 뒤 hooks 446건, scripts 758건(2건
  건너뜀)이 통과했고 감사는 errors=0 이다. 이 줄은 처음에 실행 전에 "통과"로 적었다가 실제 결과로
  고쳤다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).
- 사용자 확인 — 2026-11-16: 게이트를 바꾼 카드라 닫은 결과를 본 가지에 옮기기 전에 사용자에게
  보였다(DE-00000087). 보인 것은 세 카드(W-00000338~340)의 바뀐 경로와 요약, 기준별 리뷰 판정과
  리뷰어가 실행한 것, 실행 없이 판정한 기준이 없다는 것, 같은 모델의 리뷰라는 것, 테스트 결과를
  미리 적었다가 고친 일, 팀원 없이 직접 구현했다는 것이다. 사용자가 "확인, 닫기"로 답했다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 266 tests in 0.997s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 446 tests in 5.564s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794821428
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794821428. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp5yl8l2ma/unattended/W-00000001-1794821428
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
Ran 758 tests in 142.768s

OK (skipped=2)
```

### Review at close — 2026-11-16

```
Review report: .stage/.runtime/driver/logs/W-00000338.md
Criteria:
- PASS: 열린 카드가 없을 때 S=프로젝트 밖 경로 다음에 "$S/파일" 에 쓰는 명령을 등록 게이트가 막지 않는다
  Reason: stage_guard.py 가 등록 게이트 호출 전에 same_command_assignments 와 expand_leading_shell_variable 로 대상을 푼다; 새 테스트의 리다이렉트·cd 뒤 heredoc·중괄호 변수 세 경우가 allow 이고, 열린 카드 없는 임시 프로젝트에 'S=/tmp/zz && echo x > "$S/a.py"' 를 직접 넣어 보니 allow 였다
- PASS: 변수 값이 프로젝트 안을 가리키거나 풀 수 없는 변수면 지금처럼 막는다
  Reason: 새 테스트의 프로젝트 안 절대 경로·풀 수 없는 변수 두 경우가 deny 이고, 직접 돌린 탐침에서 상대 값 S=src, S=., 프로젝트 안으로 돌아오는 S=<root>/src/.., 값에 변수가 든 S=$HOME/x, 설정되지 않은 변수가 모두 deny 였다
- PASS: 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다
  Reason: python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q 가 266건 OK 였고, 스크래치 복사본에서 stage_guard.py 만 2a0389b2^ 판으로 되돌려 새 테스트를 돌리니 통과해야 할 세 하위 사례가 'deny' != 'allow' 로 실패했다
```

## Retrospective

[R-00000338](../../retrospectives/R-00000338.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
