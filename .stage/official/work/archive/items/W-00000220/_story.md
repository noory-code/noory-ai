---
id: W-00000220
title: 워크트리 실행 환경을 본 체크아웃과 같게 준비한다
kind: fix
venue: codex
milestone: M-00000003
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q"
status: archived
terminal_disposition: rejected
verification: pending
retrospective: completed
retrospective_ref: R-00000220
promotion: not_applicable
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/test_drive_parallel.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000220 워크트리 실행 환경을 본 체크아웃과 같게 준비한다

## Purpose

카드마다 워크트리 실행 환경이 다르게 깨져 병렬로 돌릴 수 있는지 돌려 봐야 아는 상태이므로, 깨지는 원인을 재서 워크트리 준비가 그 차이를 없애게 한다

## Actions

- [W-00000221](W-00000221.md) — 워크트리에서 실행자 환경이 깨지는 원인을 잰다
- [W-00000222](W-00000222.md) — 워크트리 준비가 그 차이를 없앤다

## User value

카드를 워크트리에 걸 수 있는지 돌려 보기 전에 안다. 지금은 카드마다 다르게 깨지고
(2026-08-03: 넷 성공, 셋 각각 다른 이유로 멈춤), 깨져도 카드 탓이 아니라 환경 탓이라 판정
기록만 어지러워진다.

## Scope

### Included

- 두 액션이 전부다. 원인 측정(W-00000221), 준비 단계 수정(W-00000222).

### Excluded

- 드라이버 자체(`drive.py`)의 동작은 형제 카드 W-00000217 몫이다.
- 앞 바퀴를 커밋한 카드가 새 워크트리에서 어긋나는 문제(O-00000028 의 W-00000193 경우)는
  환경이 아니라 기준점 문제라 이 카드가 안 다룬다.

## Risks

- 이 카드 자신이 워크트리에서 돈다 — 재는 대상 위에서 재는 셈이라, 실행자는 측정 결과가
  자기 실행 환경의 영향을 받는지 밝혀 적어야 한다.
- 원인이 워크트리 준비 밖(예: 호스트 신뢰 설정)에 있으면 준비가 못 막는다. 그 경우 무엇이
  왜 남는지가 이 카드의 산출물이다.

## Success criteria

- 클로드 실행자가 워크트리에서 명령 실행 승인에 걸리는 원인이 재현 절차와 함께 기록된다
- 워크트리 준비가 그 원인을 막아, 같은 재현 절차가 준비된 워크트리에서 통과한다

## Next action

W-00000221 부터. 측정 없이 준비를 고치면 짐작 수리다.

## Related truth

- O-00000028 — 실측 원문: 같은 도구로 넷은 끝까지 가고 셋은 각각 다른 이유(코덱스 설정,
  클로드 python3, 기준점)로 멈췄다. 2026-08-06 다섯 카드 실행에서 코덱스 쪽은 재현 안 됐고
  클로드 실행자의 명령 승인 대기는 재현됐다.


## Progress

한 바퀴 만에 스토리의 전제가 무너졌다. 측정(W-00000221)이 "본 체크아웃과 워크트리는 이미
같다 — 클로드 실행자는 어디서든 명령 실행 권한이 없다"를 확인했다. 그동안 claude venue
카드가 통과한 것은 드라이버가 인수 검사를 대신 돌리기 때문이다. 없앨 차이가 없으므로 준비
단계를 고칠 일(W-00000222)도 없다.

## Verification

성공 기준 둘 다 존재하지 않는 차이를 전제한다. 판정 반려와 감독 세션의 대칭 탐침이 근거다.

## Retrospective

R-00000220 참조.

## Promotion decision

not_applicable — 결정 기록 없음. 물림: 진짜 남는 물음은 "클로드 실행자에게 권한을 줄 것인가,
클로드 venue 실행을 에이전트 팀으로 바꿀 것인가"이고, 그것은 사람이 정할 설계 카드다.
