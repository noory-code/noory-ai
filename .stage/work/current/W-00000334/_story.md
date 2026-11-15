---
id: W-00000334
title: 세션 시작 글에 인라인 코드 규칙을 싣는다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_session_context_inline_rule.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000334
promotion: not_applicable
review: passed
scope: stage/hooks/stage_context.py, stage/hooks/tests/test_session_context_inline_rule.py, stage/hooks/README.md, stage/operations/hooks.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000334 세션 시작 글에 인라인 코드 규칙을 싣는다

## Purpose

Stage 작업 폴더를 건드리는 인라인 인터프리터 코드를 훅이 거절한다는 규칙을 세션이 시작할 때 알려, 거절당하고 다시 시도하는 왕복을 줄인다

## Actions

없음 — 한 함수에 한 줄을 넣고 시험과 문서를 맞추는 일이라 나누지 않는다.

## User value

세션이 `.stage` 를 건드리는 `python3 -c` 나 인터프리터 heredoc 을 쓰기 전에 그 명령이 거절된다는
것을 안다. 지금은 거절당한 뒤에야 알고 다른 방법으로 다시 시도한다. 최근 세션 50개(2026-11-02
~11-16)에서 이 거절이 67번 났고, Stage 훅이 낸 거절 115번 가운데 가장 많았다.

## Scope

### Included

- 세션 시작 글의 기본 안내에 규칙 한 줄을 넣는다. 그 줄은 무엇이 거절되는지와 대신 쓸 방법
  (Write/Edit, 이름 있는 스크립트 파일)을 말한다.
- 새 구조(v4)와 옛 구조 두 갈래가 같은 줄을 쓴다.
- 그 줄이 두 갈래에 실리는지 확인하는 시험을 더한다.
- 세션 시작 글을 설명하는 두 문서(`stage/hooks/README.md`, `stage/operations/hooks.md`)와 변경
  기록을 맞춘다.

### Excluded

- 거절 조건과 거절 메시지를 바꾸지 않는다. 훅은 인라인 코드가 무엇을 쓰는지 볼 수 없으므로
  거절은 그대로 둔다.
- 세션 시작 글의 다른 부분을 줄이거나 합치지 않는다. 열린 관찰 목록에 개수 상한을 두지 않는다
  (`db9f74f1` 이 일부러 없앴다).
- 하위 에이전트와 드라이버 실행자에게 이 규칙을 따로 전하지 않는다. 그쪽이 세션 시작 글을
  받는지는 확인하지 않았다.

## Risks

- 긴 세션이 요약되면 시작 글도 함께 줄어든다. 그 뒤에는 이 줄이 남지 않을 수 있어 거절이 모두
  사라지지는 않는다.
- 세션 시작 글이 한 줄만큼 길어진다(약 200자). 세션마다 치르는 값이다.
- 거절 횟수가 실제로 줄었는지는 이 카드 안에서 잴 수 없다. 며칠 치 세션 기록이 쌓인 뒤 같은
  방법으로 다시 잰다.

## Success criteria

- 세션 시작 글에 그 규칙이 한 줄로 실리고, 새 구조(v4)와 옛 구조 두 갈래 모두에 실린다
- 훅의 거절 동작과 거절 메시지는 그대로다
- 그 줄이 실리는지 확인하는 시험이 있고 통과한다

## Next action

`stage/hooks/tests/test_session_context_inline_rule.py` 에 깨지는 시험을 먼저 쓰고,
`stage/hooks/stage_context.py` 의 `session_context` 두 갈래에 같은 줄을 넣는다.

## Related truth

- `stage/hooks/stage_guard.py` 의 `interpreter_inline_stage_write` — 거절을 내는 자리. 이 카드는
  건드리지 않는다.
- DE-00000086 — codex 가 없는 로컬 세션에서 Claude 가 실행하고 닫기 리뷰를 따로 받는다.
- DE-00000087 — `stage/hooks/` 를 바꾸는 카드는 사용자 확인 뒤에 닫는다.

## Progress

- 2026-11-16: `origin/main`(3ef8eaa3)에서 딴 worktree `claude/stage-inline-rule-hint` 에서 진행했다.
  venue 정책은 fix -> codex 지만 DE-00000086 에 따라 `local-no-codex` 환경에서 Claude 가 실행했다.
  팀원을 띄우지 않고 감독 세션이 직접 했다.
- `stage_context.py`: 상수 `INLINE_INTERPRETER_RULE_LINE`(285자)을 두고, `session_context` 의 두
  갈래가 끝난 자리에서 한 번 덧붙인다. `.stage` 가 없는 프로젝트에는 싣지 않는다.
- 시험 `test_session_context_inline_rule.py` 다섯 개: 새 구조에 한 번 실림, 옛 구조에 같은 줄이
  실림, 줄이 거절 대상과 대안을 말함, 줄의 예가 실제 훅 판정과 맞음, `.stage` 없는 프로젝트에는
  없음.
- 문서: `stage/hooks/README.md` 의 SessionStart 설명에 한 문장, `stage/operations/hooks.md` 의 막는
  행동 목록에 이 규칙 한 항목(그 문서는 "아래"라고 가리켜 놓고 목록에 없었다), 변경 기록
  `## Unreleased` 한 항목.
- 코드 커밋 `a757651c`.

## Verification

- 판별 확인: 고치기 전에 새 시험을 돌려 다섯 개 중 세 개(두 갈래에 실림, 문구)가 깨지는 것을
  봤다. 나머지 두 개는 고치기 전에도 참이어야 하는 조건(훅 판정, `.stage` 없는 프로젝트)이다.
- 줄에 든 예를 훅 함수에 직접 넣었다: `python3 -c`, 인터프리터 heredoc, `node -e`, `bash -c` 는
  거절, 이름 있는 스크립트와 `python3 -m` 은 통과.
- `python3 -m unittest discover -s stage/hooks/tests -q`: 444건 통과.
- `python3 -m unittest discover -s stage/scripts/tests -q`: 757건 통과(2건 건너뜀).
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0, warnings=32(모두 보관된 카드의
  기존 경고).
- 둘째 완료 기준(거절 동작과 메시지는 그대로): `stage_guard.py` 와 `stage_shell.py` 를 바꾸지
  않았다. `git show --stat a757651c` 에 두 파일이 없다.
- 재지 못한 것: 이 줄로 거절 횟수가 실제로 줄었는지. 세션 기록이 쌓인 뒤 다시 센다.
- 닫기 리뷰는 codex 가 없어 Claude 대역(`stage/scripts/claude_review_companion.py`)으로 돌린 같은
  모델의 리뷰이며, 교차 venue 리뷰가 아니다(DE-00000086).
- 사용자 확인 — 2026-11-16: `stage/hooks/` 를 바꾼 카드라 닫은 결과를 본 가지에 옮기기 전에
  사용자에게 보였다(DE-00000087). 보인 것은 바뀐 경로 다섯 개와 한 줄씩의 요약, 세션이 읽게 될
  줄의 전문, 완료 기준 세 개의 리뷰 판정과 리뷰어가 본 근거, 리뷰어가 실행 없이 판정한 기준이
  없다는 것, 재지 못한 두 가지(거절 횟수 감소, 하위 에이전트·드라이버 실행자가 이 글을 받는지),
  팀원 없이 감독 세션이 직접 구현했다는 것이다. 사용자가 "확인, 닫기"로 답했다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_session_context_inline_rule.py -q
[exit 0]
----------------------------------------------------------------------
Ran 5 tests in 0.083s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 444 tests in 5.952s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794756595
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794756595. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpf8bs_7du/unattended/W-00000001-1794756595
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
Ran 757 tests in 163.810s

OK (skipped=2)
```

### Review at close — 2026-11-16

```
Review report: .stage/.runtime/driver/logs/W-00000334.md
Criteria:
- PASS: 세션 시작 글에 그 규칙이 한 줄로 실리고, 새 구조(v4)와 옛 구조 두 갈래 모두에 실린다
  Reason: stage_context.session_context 가 v4·옛 구조 분기가 모두 끝난 뒤 parts.append(INLINE_INTERPRETER_RULE_LINE) 를 한 번 부르고, 상수는 줄바꿈 없는 한 줄이며 .stage 가 없는 프로젝트는 그 전에 반환한다; 시험 test_current_topology_states_the_rule_once 와 test_legacy_topology_states_the_same_rule 가 두 갈래에 같은 줄이 정확히 한 번 실리는 것을 확인한다.
- PASS: 훅의 거절 동작과 거절 메시지는 그대로다
  Reason: git diff 3ef8eaa3..HEAD -- stage/hooks/stage_guard.py stage/hooks/stage_shell.py 를 돌려 0줄을 확인했다; 바뀐 경로 다섯 개(changed-paths.json)에도 두 파일이 없고, 이번 리뷰 중 python3 -c 를 실제로 보냈을 때 기존 거절 메시지가 그대로 나왔다.
- PASS: 그 줄이 실리는지 확인하는 시험이 있고 통과한다
  Reason: acceptance 명령 python3 -m unittest discover -s stage/hooks/tests -p test_session_context_inline_rule.py -v 를 돌려 5건 모두 ok 를 봤고, python3 -m unittest discover -s stage/hooks/tests -q 도 444건 OK 였다; 줄의 예(-m 허용, python -c·perl -e 거절)는 stage_shell.interpreter_inline_stage_write 에 직접 넣어 줄의 서술과 맞는 것을 확인했다.
```

## Retrospective

[R-00000334](../../retrospectives/R-00000334.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
