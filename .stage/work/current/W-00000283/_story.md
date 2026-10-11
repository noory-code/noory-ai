---
id: W-00000283
title: 범위를 넘은 호출의 훅 메시지를 대화창 한 줄과 에이전트 맥락으로 나눈다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_schema_v4_consumers.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000283
promotion: not_applicable
review: not_required
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/scripts/tests/test_schema_v4_consumers.py, stage/scripts/tests/test_drive_parallel.py, stage/operations/hooks.md, stage/hooks/README.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000283 범위를 넘은 호출의 훅 메시지를 대화창 한 줄과 에이전트 맥락으로 나눈다

## Purpose

Stage 훅이 범위를 넘은 호출마다 대화창에 열린 카드 전체를 찍지 않게 하고, 범위를 넘었다는 알림은 에이전트에게 실제로 전달되게 한다.

## Actions

한 번에 끝나는 고침이라 하위 작업을 나누지 않는다.

1. `stage/hooks/stage_guard.py`의 `append_purpose_context`에서 허용된 호출이 범위를 넘었을 때의 출력을 바꾼다.
   - 지금: `purpose_tool_context`가 만든 전체 맥락(열린 카드 전부의 범위와 목적)을 `systemMessage`에 붙인다.
   - 바꿀 것: 전체 맥락은 `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": <맥락>}}`로 보낸다.
     `systemMessage`에는 `Scope boundary crossed: <경로>.` 한 줄만 붙인다. 이미 다른 검사가 넣은 `systemMessage`가 있으면 그 뒤에 이 한 줄을 잇는다.
   - 막힌 호출(`permissionDecision: "deny"`)은 지금처럼 `permissionDecisionReason`에 맥락을 붙인다. 바꾸지 않는다.
   - 범위를 넘지 않은 허용 호출은 지금처럼 아무것도 출력하지 않는다.
2. `systemMessage` 안의 문구를 검사하던 테스트를 새 출력에 맞춘다. `Stage work context` 같은 전체 맥락 문구는 `additionalContext`에서 찾는다. `Scope boundary crossed:` 줄은 `systemMessage`에 남는지 확인한다. 사용자 화면용 메시지가 한 줄인지도 검사한다.
3. `stage/operations/hooks.md`의 "Purpose context" 절과 `stage/hooks/README.md`의 출력 표에 두 출력이 각각 누구에게 가는지 적는다.
4. `stage/CHANGELOG.md`의 `## Unreleased`에 고친 내용을 적는다. 플러그인 버전은 바꾸지 않는다.

## User value

사용자는 2026-10-11 대화에서 "여기 로그가 왜 이렇게 많이 나오죠", "다시나하고 관련 없습니다"라고 했다. 다시나 카드의 파일 하나를 고쳐도 대화창에 열린 카드 15장의 범위와 목적이 30줄 넘게 찍혔다. 고치고 나면 대화창에는 어느 경로가 범위를 넘었는지 한 줄만 보인다.

에이전트 쪽도 나아진다. `systemMessage`는 Claude Code와 Codex 둘 다 사용자 화면에만 띄우고 모델에게는 보내지 않는다. 그래서 "범위를 넘은 경로를 보고하라"는 지시가 지금은 에이전트에게 닿지 않는다. `additionalContext`로 옮기면 에이전트가 이 지시를 받는다.

근거 문서:
- Claude Code: https://code.claude.com/docs/en/hooks.md — `systemMessage`는 "Warning message shown to the user", PreToolUse의 `additionalContext`는 "String added to Claude's context".
- Codex: https://learn.chatgpt.com/docs/hooks — `systemMessage`는 UI 경고로 띄우고, `additionalContext`는 모델 맥락에 더한다. PreToolUse에서 둘 다 지원한다.

## Scope

### Included

- 범위를 넘은 허용 호출에서 사용자 화면에 나가는 메시지를 한 줄로 줄인다.
- 같은 호출에서 범위·목적 맥락과 보고 지시를 `additionalContext`로 에이전트에게 보낸다.
- 막힌 호출과 범위를 넘지 않은 호출의 출력은 지금과 같게 유지된다.
- 두 출력이 누구에게 가는지 훅 계약 문서에 적는다.

### Excluded

- 맥락에 찍는 카드를 관련 카드로 좁히는 일. 범위 밖 경로는 정의상 어느 카드에도 맞지 않아 고를 기준이 없다. 대화창에서 빠지면 이 문제는 사라진다.
- 세션 시작 맥락(`SessionStart`)의 길이.
- 릴리스. 카드가 닫힌 뒤 Claude가 `release_plugin.py`로 따로 한다.

## Risks

- Codex가 PreToolUse에서 `hookSpecificOutput`을 `permissionDecision` 없이 받아 주는지는 문서로만 확인했다. 지원하지 않는 출력을 받으면 Codex는 훅 실행을 실패로 표시하고 호출은 계속한다. 실제 Codex 세션에서 확인한 적은 없다.
- 드라이버 시험(`test_drive_parallel.py`)이 `systemMessage`에서 `Scope boundary crossed:`를 찾는다. 이 줄을 `systemMessage`에 남기므로 깨지지 않아야 하지만, 시험을 돌려 확인해야 한다.

## Success criteria

- 범위 밖 파일 하나를 고치면 사용자 화면에는 넘은 경로를 담은 한 줄만 나간다
- 같은 호출에서 카드 범위·목적과 넘은 경로를 보고하라는 지시가 additionalContext로 에이전트에게 간다
- 막힌 호출은 지금처럼 막힌 이유와 맥락을 에이전트에게 전한다

## Next action

드라이버로 Codex가 위 Actions를 실행하고 Claude가 검토한다. 닫은 뒤 Claude가 Stage를 릴리스하고, 사용자가 `/plugin`으로 업데이트한 새 세션에서 범위 밖 파일을 고쳐 한 줄만 뜨는지 본다.

## Related truth

SoC: 사람에게 보이는 알림과 에이전트에게 주는 지시를 서로 다른 출력에 둔다. Fail Fast: 범위를 넘은 사실은 그 호출에서 바로 에이전트에게 알린다. 훅 계약은 `stage/operations/hooks.md`의 "Purpose context" 절이 소유한다.

## Progress

2026-10-11: 드라이버 한 판에서 Codex가 Actions 1~4를 실행했다. 실행 보고와 리뷰 보고는 공유 작업 로그
`.stage/.runtime/driver/logs/W-00000283.md`에 있다. Claude가 리뷰가 짚은 `stage/operations/hooks.md`의
과정 서술 한 구절을 지웠다.

## Verification

2026-10-11 Claude가 직접 확인한 것:

- 범위 밖 파일 `.claude/settings.local.json`을 고치는 Edit 입력을 훅에 넣었다. `systemMessage`는
  `Scope boundary crossed: .claude/settings.local.json.` 한 줄이고, `additionalContext`는 32줄이다.
  고치기 전에는 같은 입력에서 `systemMessage`가 30줄이었다.
- 이 세션은 저장소의 `stage/`를 플러그인으로 읽는다. 고친 뒤 범위를 넘은 Edit·Write·Bash 호출의 맥락이
  대화창 메시지가 아니라 Claude에게 들어왔다. Claude Code에서 실제 동작을 확인했다.
- 고치기 전 `stage_guard.py`로 되돌리면 hooks 시험이 11개 실패하고, 되살리면 모두 통과한다.
- 막힌 호출의 deny 분기 코드는 바뀌지 않았다. 시험이 막힌 이유와 그 뒤의 맥락을 확인한다.

드라이버의 인수 시험 3개와 Claude 독립 리뷰가 통과했다. 리뷰는 성공 기준 3개를 모두 PASS로 판정했다.

리뷰 지적 처리:

- `operations/hooks.md`의 "its output contract is unchanged"가 과정 서술이라는 지적 — accept. 그 구절을 지웠다.
- Codex에서 `permissionDecision` 없는 `hookSpecificOutput`을 받는지 실제로 확인하지 않았다는 지적 — defer.
  문서로는 지원한다. 릴리스 뒤 Codex 세션에서 확인하며 R-00000283의 Next changes에 적었다.
- `/dev/null`과 transcript `.jsonl`이 넘은 경로로 잘못 잡힌다는 지적 — defer. 이 카드의 출력 경로가
  아니라 경로를 뽑는 쪽 문제다. O-00000050으로 남겼다.

### Executed at close — 2026-10-11

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 1.750s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_schema_v4_consumers.py -q
[exit 0]
----------------------------------------------------------------------
Ran 9 tests in 0.220s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q
[exit 0]
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpli1pjj1x/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpli1pjj1x/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
Removed worktree and branch for W-00000001
Removed worktree and branch for W-00000001
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpnqga_4gf/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpnqga_4gf/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
W-00000003: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpnqga_4gf/worktrees/W-00000003
Merge branch: stage/worktree/W-00000003
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpwm71mu02/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpwm71mu02/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
W-00000001: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmplc7qc7_i/worktrees/W-00000001
Merge branch: stage/worktree/W-00000001
W-00000002: driver exited with status 0
Worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmplc7qc7_i/worktrees/W-00000002
Merge branch: stage/worktree/W-00000002
----------------------------------------------------------------------
Ran 33 tests in 4.170s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 1.780s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1791687748
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1791687748. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpge49nqi8/unattended/W-00000001-1791687748
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
Ran 659 tests in 105.701s

OK
```

## Retrospective

[R-00000283](../../retrospectives/R-00000283.md)

## Promotion decision

정책이나 결정 기록으로 옮길 것은 없다. 훅 계약은 `stage/operations/hooks.md`에 반영했다.
