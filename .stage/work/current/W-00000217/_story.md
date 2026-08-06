---
id: W-00000217
title: 드라이버가 잘리거나 죽어도 하니스 안에서 이어 간다
kind: fix
venue: codex
milestone: M-00000003
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000217 드라이버가 잘리거나 죽어도 하니스 안에서 이어 간다

## Purpose

드라이버가 시간 한도에 잘리거나 도중에 죽으면 다 된 일도 카드가 갇히고 사람이 대신 검증하게 되므로, 드라이버가 끝난 일을 스스로 알아보고 죽은 자리에서 이어 가게 한다

## Actions

- [W-00000218](W-00000218.md) — 잘린 바퀴의 끝난 일을 드라이버가 알아본다 (갇힘을 없앤다)
- [W-00000219](W-00000219.md) — 죽은 드라이버를 그 자리에서 이어 간다 (이어가기 명령)

## User value

카드가 커도, 세션이 끊겨도 드라이버를 다시 걸면 그 자리부터 간다. 지금은 잘리면 시도만 타고
카드가 갇히며, 죽으면 사람이 검사를 손으로 돌려 닫는다 — 만든 쪽과 보는 쪽이 갈리지 않는다.

## Scope

### Included

- 두 액션이 전부다. 잘린 바퀴 인식 + 시간 한도 산정(W-00000218), 죽은 자리 이어가기 +
  되돌리기 겨냥(W-00000219).

### Excluded

- 무인 실행(unattended) 경로의 동작 변화는 목적이 요구하는 만큼만. 무인 쪽 계약은
  DE-00000055 가 소유한다.
- 워크트리 환경 준비는 형제 카드 W-00000220 몫이다.

## Risks

- 드라이버는 이 저장소의 실행 기둥이다. 판정 우회가 생기면 안 된다 — "인수 통과 = 진전"이
  판정(리뷰)을 건너뛰는 길이 되면 독립 검증이 죽는다. 인수 통과는 판정으로 **넘어가는**
  조건이지 판정을 **대신하는** 조건이 아니다.
- `test_drive.py` 는 넓은 시험 묶음이라 무관한 회귀도 잡는다. 이 카드에서는 그게 의도다
  (드라이버 전체가 카드의 결과물이다).

## Success criteria

- 시간 한도로 잘린 뒤 작업 트리가 그대로면 드라이버가 인수 검사를 먼저 돌리고, 통과하면 그 바퀴를 제자리걸음이 아니라 진전으로 처리한다
- 액션 없는 스토리의 명령 시간 한도가 자식 수가 아니라 카드가 선언한 크기 신호에서 나온다
- 드라이버가 죽은 카드를 running_role 이 가리키는 다음 단계부터 이어 가는 명령이 있다
- 되돌리기가 다음 실행할 카드가 아니라 실행 중 표시를 든 그 카드를 겨눈다

## Next action

W-00000218 부터. 두 액션 다 `stage/scripts/drive.py` 를 만지므로 순서대로 간다.

## Related truth

- O-00000030 — 네 고리(잘림 → 늦은 보고 → 고칠 것 없음 → 제자리걸음 판정)가 이어져 카드가
  갇힌 실측. W-00000200 이 세 바퀴로 전부 밟았다.
- O-00000031 — 액션 없는 스토리가 크기와 무관하게 최소 900초를 받는 실측.
- O-00000017 — 판정 도중 죽은 뒤 이어 갈 명령이 없어 사람이 대신 검증한 실측 (W-00000157).
- O-00000026 — 되돌리기가 표시 든 카드가 아니라 다음 실행할 카드를 겨눈 것, 그리고 사람이
  대신 커밋하면 기준점이 안 맞아 되살릴 명령이 없는 것 (`drive.py:2589`, `drive.py:321` 근처).
- 넷 다 이 스토리가 닫히면 닫을 후보다. 남는 절반이 있으면 그 절반만 남게 고쳐 쓴다.


## Progress


## Verification


## Retrospective


## Promotion decision
