---
id: W-00000187
title: 무인 실행을 자기 작업 디렉터리에서 돌린다
kind: development
venue: codex
milestone: M-00000001
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q -p test_drive_unattended.py"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive.py, stage/scripts/drive_parallel.py, stage/scripts/tests/, stage/docs/, stage/operations/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000187 무인 실행을 자기 작업 디렉터리에서 돌린다

## Purpose

무인 실행이 사람과 같은 작업 디렉터리를 써서 실패할 때마다 사람의 편집을 지운다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

무인 실행을 걸어 두고 그 옆에서 일할 수 있다. 지금은 실행자 시도가 실패할 때마다 사람이
편집하던 것이 지워진다.

## Scope

### Included

- 무인 실행이 자기 작업 디렉터리를 만들어 거기서 돈다. 끝나면 치운다.
- 되돌리고 지우는 동작이 그 디렉터리 안에서만 돈다.
- 사람이 자기 자리에서 파일을 만져도 무인 실행이 그것을 안 지우고 안 섞는지 보는 시험.

### Excluded

- **감독 실행.** DE-00000055 가 지금은 안 옮기기로 정했다. O-00000013 이 그 몫으로 열려 있다.
- 나누는 선을 다시 정하는 일. DE-00000055 가 소유한다.

## Risks

- **무인 실행이 사람 자리의 무언가를 필요로 할 수 있다** — 설정, 캐시, 인증. 나눈 뒤 실제로
  도는지 보고, 필요한 것이 나오면 그것이 나누는 선이 틀렸다는 신호다(결정이 그렇게 적었다).
- **만들고 치우는 값이 붙는다.** 한 바퀴 값에서 무시할 만한지 재고 적는다.
- **치우다 실패하면 찌꺼기가 남는다.** 되살리는 길이 없는 모양은 이 프로젝트에 이미 둘 있다
  (O-00000016·17). 같은 모양을 하나 더 만들지 않는다.

## Success criteria

- 무인 실행이 도는 동안 사람이 자기 자리에서 파일을 만져도, 그 파일이 안 지워지고 실행자 몫에
  안 섞인다.
- 실행자가 만든 변경은 여전히 다 잡히고 커밋된다.
- 두 갈래를 다 보는 시험이 있다.
- 치우다 실패해도 사람이 되살릴 길이 있다.
- 사람이 겪는 결과: 무인 실행을 걸어 두고 하던 일을 계속할 수 있다.

## Next action

무인 실행이 지금 가지를 만드는 자리를 읽고, 같은 자리에서 디렉터리도 만들게 한다. 되돌리고
지우는 세 자리(`drive.py:2354`·`2357`·`2395`)가 그 안에서만 돌게 한다.

## Related truth

- **DE-00000055** — 가르는 신호가 없으면 나눈다. 무인 실행이 자기 작업 디렉터리에서 돈다.
  감독 실행은 그대로 둔다.
- **W-00000186** — 무인 실행의 격리가 가지만 가르고 작업 디렉터리는 같다는 것, 그리고 실패할
  때마다 커밋 안 된 변경을 전부 지운다는 것을 실측했다.


## Progress


## Verification


## Retrospective


## Promotion decision
