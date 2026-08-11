---
id: W-00000258
title: 회고 번호를 카드 번호에서 만들지 말고 빈 번호를 잡는다
kind: fix
venue: codex
milestone: M-00000004
autonomous: true
acceptance:
  - "grep -q collision stage/scripts/tests/test_close_work.py && python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000260
promotion: not_applicable
review: passed
scope: stage/scripts/driver_lifecycle.py, stage/skills/stage-retrospective/close_work.py, stage/skills/stage-retrospective/SKILL.md, stage/scripts/tests/test_close_work.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000258 회고 번호를 카드 번호에서 만들지 말고 빈 번호를 잡는다

## Purpose

회고 번호를 카드 번호에서 그대로 만드는데 과거 회고들이 따로 번호를 매겨 와서 그 자리가 이미 차 있으면 카드를 못 닫으므로, 카드 등록이 하듯 빈 번호를 잡게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 회고 자리가 이미 찬 카드도 닫히고, 그 회고가 빈 번호를 받는다
- 이미 자기 번호를 쓰고 있는 카드는 그 번호를 그대로 쓴다

## Actions

없음 — 번호를 잡는 함수 하나를 고치고 그 시험을 붙이는 한 덩어리다.

## User value

카드를 닫을 때 번호 때문에 막히지 않는다. 지금은 막히면 사람이 빈 번호를 손으로 찾아 파일
이름과 본문 두 자리를 고쳐야 한다.

## Scope

### Included

**감독이 등록 전에 잰 것.**

| 잰 것 | 값 |
|---|---|
| 회고 254장 중 번호가 자기 카드와 안 맞는 것 | **168장** |
| 다음에 등록될 카드 | W-00000258 — **이 카드다** |
| 그 카드의 회고 자리 | **이미 찼다.** R-00000258 은 W-00000243 것 |

**이 카드가 자기 고장을 밟는다.** 고치지 않으면 이 카드 자신이 못 닫힌다. 시험이 아니라
실제로 그렇다.

- **번호를 잡는 자리를 고친다.** `driver_lifecycle.py:236` `retrospective_id_for_work_item` 이
  카드 번호에서 `R-` + 숫자로 만든다. 카드 등록(`register_work.py:180-198`)이 하듯 **빈 번호를
  찾아 원자적으로 잡는** 모양으로 바꾼다.
- **이미 자기 번호를 쓰는 카드는 그대로 둔다.** 168장이 안 맞지만 나머지는 맞고, 맞는 것을
  옮기면 링크가 깨진다.
- **손으로 닫는 쪽은 번호를 아예 안 잡는다.** `close_work.py` 는 사람이 정한 번호를 받아
  이미 쓰인 번호인지만 본다(`:696-708`). 그래서 사람이 번호를 손으로 골라야 하고, 감독이
  R-00000243 을 골랐다가 감사에 걸린 판이 그것이다. **`close_work.py` 에 빈 회고 번호 하나를
  찍고 끝나는 옵션을 붙여** 사람도 같은 함수로 번호를 받게 한다. 회고 파일은 닫기 전에
  사람이 쓰므로, 번호를 주는 자리는 닫기보다 앞이어야 한다.

### Excluded

- **이미 있는 회고 168장을 안 옮긴다.** 번호가 안 맞는 것이 문제가 아니라, 새로 잡을 때 찬
  자리를 피하는 것이 문제다. 옮기면 `retrospective_ref` 와 감사 링크가 전부 따라 움직인다.
- 카드 번호를 안 바꾼다.
- 회고 본문의 틀을 안 바꾼다.
- **worktree 를 갈라 놓았을 때의 충돌을 안 막는다.** `O-00000046` 이 소유한다. 아래
  「거부와 처분」을 읽는다.

## 거부와 처분

2026-08-11 첫 실행에서 실행자가 카드를 거부했다. 이유는 **`x` 모드가 worktree 사이에서는
번호를 못 지킨다**는 것이었다.

**사실은 맞다.** 감독이 코드를 열어 확인했다. 처분은 **받되 이 카드 밖으로 뺀다**이고,
근거는 셋이다.

| 근거 | 확인한 자리 |
|---|---|
| 같은 약점을 카드 번호도 갖는다 — 카드가 따라 하라고 지목한 코드가 그것이다 | `stage/skills/stage-work/register_work.py:180-198` |
| 회고 번호를 잡는 유일한 자리는 무인 실행뿐이다. 감독이 붙어 도는 실행은 카드를 안 닫으므로 번호를 아예 안 잡는다 | `stage/scripts/driver_unattended.py:607`, `:975` |
| 그래서 밟으려면 **무인 드라이버가 둘 이상 동시에** 돌아야 한다. 그런 판은 아직 없다 | 미실측 — 돌린 적이 있는지 확인 안 했다 |

반면 이 카드가 고치는 고장은 **지금 터져 있다.** 회고 254장 중 168장이 안 맞고, 이 카드
자신이 못 닫힌다.

`O-00000046` 이 worktree 충돌을 열어 둔 채로 소유한다. **이 카드는 그것을 안 고친다.**
`x` 모드 방식을 그대로 쓴다.

## 범위를 넓힌 기록

사람이 2026-08-11 에 두 파일을 범위에 넣었다. 실행자가 스스로 넓힌 것이 아니다.

| 파일 | 왜 |
|---|---|
| `stage/scripts/tests/test_drive.py` | 옛 시험이 "번호가 겹치면 거부한다"를 기대해서 새 완료 기준과 정면으로 어긋났다. 실행자가 넘어서 고치고 그렇게 보고했다 |
| `stage/skills/stage-retrospective/SKILL.md` | 번호를 받는 옵션이 붙어도 절차 문서가 안 알려 주면 사람은 계속 손으로 고른다. 그 길이 이 카드가 없애려던 사고다 |

둘째는 독립 리뷰어가 통과시키면서 남긴 지적이다. 완료 기준 밖이라 안 막았지만, 카드의 목적
절반이 안 닿는다고 짚었다.

## Risks

- **원자적으로 안 잡으면 병렬 실행이 같은 번호를 집는다.** 오늘 병렬로 둘을 돌렸고, 그때
  드라이버가 회고를 각자 만들었다. `register_work.py` 가 쓰는 모양(파일을 `x` 모드로 열어
  실패하면 다음 번호)을 그대로 따른다.
- **맞는 짝을 옮기면 링크가 깨진다.** 지금 자기 번호를 쓰는 회고는 그대로 둬야 한다.
- 이 카드가 못 닫히면 드라이버가 그 자리에서 멈춘다. 그것이 이 카드가 고치는 고장이므로
  옳은 실패다.

## Next action

**「거부와 처분」을 먼저 읽는다.** worktree 사이 충돌은 이미 처분됐고 `O-00000046` 이 갖는다.
그것을 이유로 다시 멈추지 않는다.

**`stage/scripts/driver_lifecycle.py:236` `retrospective_id_for_work_item` 을 읽는다.**
지금 카드 번호에서 회고 번호를 만든다. 그 1:1 짝이 과거 기록에서 이미 깨져 있다 — 168장이
안 맞는다.

따라갈 모양은 `stage/skills/stage-work/register_work.py:180-198`
`create_hierarchy_item_atomic` 이다. 최대값+1 로 시작해 파일을 `x` 모드로 열고, 이미 있으면
다음 번호로 넘어간다.

**시험은 실패하는 것부터 쓴다.** 고침을 되돌리면 그 시험이 깨져야 한다. 저장된 인수 명령이
`grep -q collision` 으로 시험 파일을 먼저 보지만, 그 낱말은 주석에 있어도 통과한다. 낱말이
아니라 시험이 고장을 밟아야 한다.

**변경 기록도 카드 범위다.** `stage/CHANGELOG.md` 맨 위 `## Unreleased` 에 이 카드의 줄을
넣는다. 인수 명령이 이것을 안 본다.

## Related truth

- `stage/skills/stage-work/register_work.py:180-198` — 카드 번호를 원자적으로 잡는 자리.
  따라갈 모양이다.
- R-00000258 — 이 고장을 감독이 손으로 겪은 판. 회고를 R-00000243 으로 썼다가 감사가 잡아
  R-00000258 로 옮겼다.
- M-00000004 완료 기준 넷째("사람이 한 일이 판단뿐")에 걸린다. 번호를 손으로 찾아 고치는 것은
  판단이 아니라 장부질이다.


## Related truth


## Progress


## Verification


### Executed at close — 2026-08-11

```
$ grep -q collision stage/scripts/tests/test_close_work.py && python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 57 tests in 6.770s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (296 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1786429355
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1786429355. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpjx2y_gzt/unattended/W-00000001-1786429355
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
Ran 632 tests in 114.031s

OK

$ grep -q collision stage/scripts/tests/test_close_work.py && python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 57 tests in 7.016s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (296 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1786429474
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1786429474. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpbvm04eem/unattended/W-00000001-1786429474
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
Ran 632 tests in 104.190s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 374 tests in 1.511s

OK

$ python3 stage/scripts/audit_stage.py
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

### Independent review at close — 2026-08-11

```
Review report: .stage/.runtime/driver/logs/W-00000258.md
```

## Retrospective


## Promotion decision
