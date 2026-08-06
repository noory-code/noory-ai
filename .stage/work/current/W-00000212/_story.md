---
id: W-00000212
title: 보관 명령이 계층을 만나도 끝까지 가게 한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/skills/stage-archive/archive_work.py, stage/scripts/tests/test_archive_work.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000212 보관 명령이 계층을 만나도 끝까지 가게 한다

## Purpose

보관 명령의 --all-completed 가 리뷰 표의 액션 행을 따로 보관 단위로 잡아 계층을 만나면 중간에 죽으므로, 최상위 항목만 보관 단위로 담아 한 번에 끝나게 한다

## Actions

없음 — 후보 고르기 한 함수를 고치고 회귀 시험을 더하는 한 덩어리다.

## User value

리뷰 표를 한 번에 비우는 명령이 계층 앞에서 안 죽는다. 지금은 중간에 죽으면 반쯤 옮겨진
상태(감사 오류 6개)가 남고, 찌꺼기가 승격 게이트 뒤에 있어 하니스 안에서 못 치운다.

## Scope

### Included

- `archive_work.py` 의 `completed_ids_from_review`(148행 근처)가 리뷰 표의 모든 `W-` 행을
  종료 상태만 보고 담는 것을, **최상위 항목만** 담게 고친다. 보관은 최상위 하나를 통째로
  옮기는 일이고, 자식과 그 회고는 그때 함께 움직인다.
- 스토리+액션 계층이 표에 함께 있는 경우의 회귀 시험을 `test_archive_work.py` 에 더한다.

### Excluded

- 보관이 중간에 죽었을 때 스스로 되돌리는 장치는 이 카드가 안 만든다. 그 구멍은
  O-00000016 에 적혀 있고 따로 다룬다 — 이 카드는 죽는 원인 하나를 없앤다.

## Risks

- 실측 사례(W-00000161 계층)와 같은 모양을 시험이 재현해야 한다. 최상위만 담는 판정이
  중첩 스토리의 독립 보관(액션 없이 홀로 종료된 카드)을 놓치면 반대 방향으로 깨진다.

## Success criteria

- 스토리와 그 액션들이 함께 리뷰 표에 있어도 --all-completed 가 오류 없이 끝난다
- 액션이 따로 보관 단위로 잡히지 않는다

## Next action

`completed_ids_from_review` 가 표의 행에서 최상위 여부를 어떻게 알 수 있는지(링크 경로의
깊이가 이미 답을 들고 있다) 확인하고 판정을 끼운다.

## Related truth

- O-00000016 — 실측 기록: `FileNotFoundError: R-00000162.md` 로 중단, `git clean` 으로 수습.
  이 카드가 닫히면 그 관측의 명령 결함 부분이 근거를 얻는다.


## Progress


## Verification


## Retrospective


## Promotion decision
