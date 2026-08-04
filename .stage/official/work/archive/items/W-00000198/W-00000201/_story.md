---
id: W-00000201
title: 기록을 닫고 되돌리는 명령을 만든다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_record.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000200
promotion: promoted
review: not_required
scope: stage/scripts/close_record.py, stage/scripts/tests/test_close_record.py, stage/hooks/stage_paths.py, stage/hooks/stage_runtime.py, stage/hooks/tests/test_archive_gate.py, stage/skills/, stage/CHANGELOG.md
promotes: .stage/official/decisions/records/DE-00000057.md
decision_refs:
---

# W-00000201 기록을 닫고 되돌리는 명령을 만든다

## Purpose

제안과 관측과 질문을 닫는 일이 손 편집이라 인덱스가 따로 낡고 절이 통째로 빠지기도 하므로, 닫힘과 되돌리기를 한 명령이 맡아 본문과 자리와 인덱스를 함께 옮기게 한다

## Actions

없음 — 닫기와 되돌리기는 같은 이동의 양방향이라 따로 만들면 두 번 다 짜게 된다.

## User value

관측 하나를 닫는 데 파일 본문, 파일 자리, 인덱스 세 곳을 기억해서 고치지 않는다. 명령 한 줄로
셋이 같이 움직이고, 잘못 닫았으면 되돌린다.

## Scope

### Included

- **보관함에 쓸 수 있게 게이트를 넓힌다.** `.stage/official/` 아래 쓰기는 통행증이 있어야 하는데,
  보관용 통행증이 허락하는 자리가 `official/work/archive/` 하나뿐이다. 지금 상태로는 이 명령이
  새 보관함 셋에 아예 못 쓴다. 자리를 아는 통행증으로 넓히거나, 이 명령이 스스로 내고 쓰는
  통행증을 만든다 — 카드 보관 명령이 이미 그렇게 한다.
- 제안·관측·질문을 닫는 명령. 닫는 근거를 필수로 받아 본문 상태 절에 적고, 파일을 보관함으로
  옮기고, 인덱스에서 그 줄을 내린다.
- DE-00000057 의 "닿는 자리" 표에 그 게이트를 더한다. 결정을 쓸 때 빠뜨린 자리다.
- 제안은 실림·접힘·절반 중 하나를 함께 받는다.
- 되돌리기. 닫은 기록을 살아 있는 서랍으로 되돌리고 인덱스에 줄을 되살린다.
- 중간에 실패하면 아무것도 안 옮긴 상태로 남긴다. 파일만 가고 인덱스가 옛 줄을 들고 있는 꼴이
  제일 나쁘다.

### Excluded

- 다 쓴 허가증은 이 명령이 안 옮긴다. 그쪽은 계산되니 카드 보관이 맡는다(W-00000202).
- 이 저장소의 기존 기록은 안 건드린다. 비우는 것은 W-00000203 이다.
- 기록을 새로 만드는 명령은 안 만든다. 지금 손으로 만들다 절이 빠지는 문제는 감사가
  잡는 쪽으로 간다(W-00000200).

## Risks

- **게이트를 안 넓히면 이 카드가 만든 명령이 아무것도 못 옮긴다.** 그러면 W-00000203 도 못
  돈다. 이 위험이 나머지보다 앞선다.
- 게이트를 넓히는 것은 공식 영역을 지키는 잠금을 건드리는 일이다. 넓힌 만큼만 열려야 하고,
  다른 자리로 새면 안 된다.
- **상태 인덱스에는 갱신 명령이 없다.** 결정 인덱스만 스스로 만들어진다. 이 명령이 인덱스를
  직접 고치지 않으면 지난 세션의 실패가 그대로 반복된다.
- 상태 인덱스는 안내 문서 예외 목록에 올라 있어 갱신 규칙이 다른 문서와 다르다.
- 되돌리기를 안 만들면 사람이 손으로 옮기게 되고, 그 순간 이 카드가 막으려던 자리가 다시 열린다.

## Success criteria

- 사람이 통행증을 따로 내지 않고 명령 한 줄로 기록을 보관함에 넣는다.
- 넓힌 게이트가 보관함 셋 밖의 공식 자리는 여전히 막는다.
- 관측·질문·제안을 닫으면 본문 근거·파일 자리·인덱스가 한 번에 맞는다.
- 근거 없이 닫으려 하면 명령이 거부한다.
- 닫은 기록을 되돌리면 인덱스 줄이 되살아난다.
- 옮기다 실패하면 아무것도 안 옮겨진 상태로 남고, 사람이 무엇이 왜 막혔는지 읽는다.
- 닫은 뒤 감사가 오류 없이 통과한다.

## Next action

공식 영역 쓰기 게이트부터 읽는다(`stage/hooks/stage_paths.py` 의 보관 경로 판정과
`stage/hooks/stage_runtime.py` 의 통행증 검사). 여기가 안 열리면 나머지를 만들어도 못 쓴다.

## Related truth

- O-00000029 — 내가 기억해서 적어야 하는 상태는 예외 없이 낡는다. 한 세션에서 네 서랍 열아홉 장.
- `refresh_decision_index.py` — 서랍에서 표를 만들어 내는 이미 있는 본보기.

## Progress

공식 영역 쓰기 잠금을 보관함 셋까지 열고, 닫고 되돌리는 명령과 그 스킬을 만들었다. 두 바퀴가
걸렸다.

첫 바퀴는 판정에서 물러났다 — 기준 일곱 중 여섯 통과, **"닫은 뒤 감사가 통과한다"가 실패했다.**
감사에는 모든 제안이 살아 있는 인덱스에 줄을 가져야 한다는 규칙이 있는데, 닫힌 제안은 그 줄을
일부러 떠난다. 실행자가 관측 갈래만 시험해서 못 봤고, 판정이 갓 만든 프로젝트에서 제안을 실제로
닫아 보고 잡았다. 두 번째 바퀴가 그 규칙을 살아 있는 서랍에만 걸도록 좁혔다.

**판정이 남긴 것 넷은 반려가 아니라 기록이다.**

| 남긴 것 | 판단 |
|---|---|
| 보관 인덱스를 아무도 감사하지 않는다 | 받되 이 카드에서 안 한다. 기준이 요구한 적 없고, 보관 인덱스 검사는 W-00000202 가 결정 보관함까지 함께 볼 때 한 번에 놓는 것이 맞다 |
| 되돌린 줄이 원래 자리가 아니라 인덱스 끝에 붙는다 | 받는다. 글자는 그대로고 기준은 "줄이 되살아난다"였다. 순서까지 지키려면 원래 위치도 보존해야 하는데, 되돌리기가 흔한 길이 아니라 값에 비해 비싸다 |
| 보관된 기록의 상태 절에 "열림."과 닫은 근거가 같이 남는다 | 받는다. 본문을 고치면 바이트 되돌리기가 깨진다. 폴더가 상태이므로 산문이 무엇이라 하든 판정은 자리가 한다 |
| 템플릿 프로젝트에서 마지막 관측을 닫으면 경고 하나 | 받는다. 목록이 비면서 템플릿의 빈 자리가 사라지는 것이고 오류가 아니다 |

`stage/README.md` 와 `stage/skills/README.md` 는 범위 밖인데 실행자가 새 스킬을 기존 목록에서
찾게 하려고 고쳤고 그 자리에서 밝혔다. 받는다 — 목록에 없는 스킬은 없는 것과 같다.

## Verification


### Executed at close — 2026-08-04

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_record.py -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 0.997s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 361 tests in 1.437s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (249 earlier lines omitted)
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785830493
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785830493. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmp456j3_1g/unattended/W-00000001-1785830493
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
Ran 572 tests in 96.499s

OK
```

## Retrospective

R-00000200.

## Promotion decision

DE-00000057 의 적용 위치 표에 세 보관함을 지키는 게이트를 더하는 승격을 승인한다. 이 규칙은
앞으로의 공식 영역 쓰기를 구속하므로 카드가 완료된 뒤 통행증으로 기록하고, 기록한 뒤
`promotion: promoted` 로 바꾼다.
