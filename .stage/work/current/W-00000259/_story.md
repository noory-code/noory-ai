---
id: W-00000259
title: 회고 번호를 카드 등록 때 잡아서 워크트리가 갈려도 안 겹치게 한다
kind: fix
venue: codex
milestone: M-00000004
autonomous: true
acceptance:
  - "grep -q retrospective_ref stage/scripts/tests/test_register_work.py && python3 -m unittest discover -s stage/scripts/tests -p test_register_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/skills/stage-work/register_work.py, stage/scripts/start_work.py, stage/scripts/driver_lifecycle.py, stage/skills/stage-retrospective/close_work.py, stage/skills/stage-retrospective/SKILL.md, stage/scripts/tests/test_register_work.py, stage/scripts/tests/test_close_work.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000259 회고 번호를 카드 등록 때 잡아서 워크트리가 갈려도 안 겹치게 한다

## Purpose

회고 번호를 카드를 닫을 때 잡는데 워크트리마다 기록을 따로 들고 있어서 나란히 돈 실행 둘이 같은 번호를 집으므로, 번호를 본 체크아웃에서 한 번에 일어나는 카드 등록으로 옮겨 잡고 카드에 적어 둔다

## Actions

없음 — 번호를 정하는 시점을 닫기에서 등록으로 옮기는 한 덩어리다.

## User value

카드를 나란히 돌려도 회고 번호가 안 겹친다. 지금은 겹치면 합칠 때 사람이 한쪽 번호를 손으로
바꾸고 파일 이름과 카드의 `retrospective_ref` 두 자리를 같이 고쳐야 한다.

## Scope

### Included

**감독이 실제로 돌려 확인한 것.** `.stage` 를 세 번 복사해 각각 번호를 잡게 했다. 워크트리
셋이 같은 시점에서 갈라진 상태와 같다.

| 카드 | 받은 번호 |
|---|---|
| W-00000243 | R-00000261 |
| W-00000244 | R-00000261 |
| W-00000245 | R-00000261 |

**셋이 같은 번호를 받는다.** 자기 번호 자리가 차 있으면 "마지막 번호 다음"으로 가는데, 그
"마지막"을 각자 자기 사본에서만 세기 때문이다. 회고 254장 중 168장이 자리를 차지하고 있어
이 조건은 드물지 않다.

- **번호를 정하는 시점을 등록으로 옮긴다.** 카드를 등록할 때 빈 회고 번호를 정해 카드의
  `retrospective_ref` 에 적는다. 등록은 본 체크아웃에서 한 번에 일어나므로 거기서는 지금
  방식이 그대로 통한다. 계획으로 담는 등록과 바로 시작하는 등록 둘 다 해당한다.
- **빈 번호를 셀 때 카드에 적힌 번호도 센다.** 회고 파일이 아직 없어도 그 번호는 임자가
  있다. 파일만 세면 두 카드가 같은 번호를 받는다.
- **닫을 때는 카드에 적힌 번호를 쓴다.** 오늘 만든 배정 함수(`driver_lifecycle.py:233`)는
  카드에 번호가 안 적힌 경우에만 도는 대체 경로로 내려간다.
- **손으로 받는 옵션의 뜻이 바뀐다.** `close_work.py --allocate-retrospective` 는 새로 잡는
  대신 카드에 적힌 번호를 알려 주고 회고 틀 파일을 만든다. 절차 문서
  (`stage/skills/stage-retrospective/SKILL.md`)도 같이 고친다.

### Excluded

- **이미 있는 회고를 안 옮긴다.** 번호가 안 맞는 것이 문제가 아니라 새로 잡을 때 겹치는 것이
  문제다.
- **이미 등록된 카드에 번호를 소급해 안 채운다.** 지금 열린 카드는 이 카드 하나뿐이고, 번호가
  안 적힌 카드는 대체 경로로 지금처럼 닫힌다.
- 카드 번호를 잡는 방식은 안 건드린다. 같은 약점을 갖지만 등록이 본 체크아웃에서만 일어나므로
  실제로 안 밟는다.

## Risks

- **번호를 잡아 놓고 안 쓰는 카드가 생긴다.** 거절되거나 아카이브로 가는 카드의 번호는 빈
  자리로 남는다. 번호가 연속이어야 한다는 규칙은 없으니 받는다. 다만 그 번호를 다른 카드가
  다시 집으면 안 된다.
- **감사가 미리 채운 번호를 문제 삼을 수 있다.** 감독이 확인한 바로는 `retrospective_ref` 를
  보는 규칙 둘(`audit_stage.py:497`, `:901`)이 회고가 완료 표시된 카드에만 걸리므로 지금은
  안 걸린다. 규칙을 새로 만들면 이것부터 다시 본다.
- **등록이 회고 파일을 미리 만들면 계획 카드마다 빈 회고가 트리에 쌓인다.** 번호만 카드에
  적고 파일은 안 만드는 쪽을 먼저 재 본다.

## Success criteria

- 카드를 등록하면 그 카드에 회고 번호가 이미 적혀 있고, 이미 쓰인 번호와 안 겹친다
- 별도 체크아웃 둘에서 각각 등록한 카드가 서로 다른 회고 번호를 받는다
- 카드에 적힌 번호로 회고가 만들어지고, 닫을 때 번호를 새로 안 잡는다
- 회고 번호가 안 적힌 카드도 지금처럼 닫힌다

## Next action

**`stage/scripts/driver_lifecycle.py:233` `retrospective_id_for_work_item` 을 먼저 읽는다.**
어제 이 함수가 생겼다. 자기 번호 자리가 비면 그 번호를 쓰고, 차 있으면 마지막 번호 다음으로
간다. 겹치는 원인이 그 "마지막 번호 다음"이다.

**옮겨 갈 자리는 `stage/skills/stage-work/register_work.py` 다.** 카드 번호를 잡는
`create_hierarchy_item_atomic`(`:180-198`) 바로 옆이다.

**빈 번호를 셀 때 카드에 적힌 번호도 세야 한다.** 회고 파일만 세면 아직 회고를 안 쓴 카드의
번호를 다른 카드가 집는다. 지금 함수는 파일만 센다.

**시험은 실패하는 것부터 쓴다.** 저장된 인수 명령이 `grep -q retrospective_ref` 로 등록 시험
파일을 먼저 보는데, 지금 그 낱말이 0번 나온다. 낱말만 넣으면 통과하니 시험이 실제로 겹침을
밟게 쓴다.

**변경 기록도 카드 범위다.** `stage/CHANGELOG.md` 맨 위 `## Unreleased` 에 줄을 넣는다.

## Related truth

- `O-00000046` — 이 고장을 소유한 관찰 기록. 카드 번호와 회고 번호가 같은 약점을 갖는다는 것,
  회고 번호를 잡는 자리가 어디인지가 거기 있다.
- `R-00000260` — 어제 번호 배정을 만든 판의 회고. 왜 그때 워크트리 충돌을 안 고쳤는지 적혀
  있다.
- M-00000004 완료 기준 셋째("병렬로 돈 실행들이 만든 기록이 번호에서 겹치지 않는다")가 이
  카드로 닫힌다.

## Progress


## Verification


## Retrospective


## Promotion decision
