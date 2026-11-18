---
id: W-00000353
title: 카드 번호에서 만든 회고 번호를 다른 카드가 쓰고 있으면 주인을 따라가 빈 번호를 잡기
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest stage/scripts/tests/test_close_work.py stage/scripts/tests/test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/driver_lifecycle.py, stage/scripts/tests/test_close_work.py, stage/scripts/tests/test_drive.py, stage/skills/stage-retrospective/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000353 카드 번호에서 만든 회고 번호를 다른 카드가 쓰고 있으면 주인을 따라가 빈 번호를 잡기

## Purpose

예전에 회고 번호를 차례로 매긴 프로젝트에서 R-<카드 번호> 자리를 다른 카드의 회고가 쓰고 있으면 카드를 닫지 못하는 것을 고쳐, 세지 않고도 겹치지 않는 빈 번호를 받게 한다.

## Actions

이 스토리는 작은 수정 하나라서 따로 나눈 액션이 없다.

## User value

회고 번호를 예전에 차례로 매긴 프로젝트도 오래된 카드를 닫을 수 있다. 지금은 회고 자리가 막히면 사람이 빈 번호를
손으로 찾아 회고 파일 이름과 카드의 `retrospective_ref` 를 같이 고쳐야 한다.

## Scope

### Included

- `driver_lifecycle.py` 의 `reserve_retrospective` 가 `R-<카드 번호>` 자리를 다른 카드 `W-m` 이 쓰고 있으면
  `R-m` 을 다음으로 시도하고, 빈 자리가 나올 때까지 주인을 따라간다. `W-m` 은 이미 회고가 있어서 `R-m` 을 쓸 일이 없다.
- 카드의 `retrospective_ref` 가 이미 이 카드의 현재 회고를 가리키면 그 번호를 돌려준다. 손으로 번호를 정한 회고가
  둘이 되지 않게 하기 위해서다.
- 주인이 작업 카드가 아니거나, 따라가다 이미 지난 번호로 돌아오면 멈추고 무엇이 막는지 알린다.
- `close_work.py --allocate-retrospective` 와 드라이버가 같은 함수를 쓰므로 둘 다 고쳐진다.
- 절차 문서(`stage-retrospective/SKILL.md`)와 변경 기록을 맞춘다.

### Excluded

- 회고 파일을 훑어 "마지막 번호 다음"을 세는 방식은 다시 들이지 않는다(W-00000259). 워크트리 사본마다 같은 답을 낸다.
- 호출하는 쪽이 번호를 넘기는 옵션은 두지 않는다. 주인을 따라가면 사람이 번호를 고를 일이 없다.
- 이미 자기 카드와 번호가 안 맞는 기존 회고는 옮기지 않는다.

## Risks

- 기록이 서로 맞지 않으면(한 카드가 회고를 둘 가진 경우 등) 주인을 따라가는 길이 돌아올 수 있다. 그때는 멈추고 알린다.
- 카드가 손으로 만든 회고를 `retrospective_ref` 로 가리키지 않으면, 그 카드에 회고가 하나 더 생길 수 있다.

## Success criteria

- 카드 번호에서 만든 회고 자리를 다른 카드가 쓰고 있어도 회고를 만들 수 있고, 그 회고는 아무도 쓰지 않는 번호를 받는다.
- 회고 번호를 정할 때 회고 파일 목록을 훑어 마지막 번호 다음을 세지 않는다. 같은 시점에서 갈라진 사본 둘이 각각 회고를 만들어도 번호가 겹치지 않는다.
- 자기 번호 자리가 비어 있는 카드는 지금처럼 R-<카드 번호> 를 받고, 다시 실행해도 같은 번호를 돌려받는다.

## Next action

전체 테스트를 돌리고 회고를 쓴 뒤 닫기 리뷰를 받는다.

## Related truth

- novel-workspace 가 W-00000040 을 닫을 때 "retrospective R-00000040 is already archived for W-00000066, not
  W-00000040" 로 멈췄다. 사람이 R-00000168 을 손으로 만들어 닫았다.
- W-00000258 은 빈 번호를 세어 잡게 했고, W-00000259 는 사본마다 같은 번호를 세는 것을 보고 그 세기를 걷어내 멈춤으로 바꿨다.
  이 카드는 세지 않고 멈춤을 풀므로 W-00000259 의 판단(세지 않는다)을 지킨다.

## Progress


## Verification


## Retrospective


## Promotion decision
