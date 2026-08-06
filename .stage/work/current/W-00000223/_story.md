---
id: W-00000223
title: 훅 시험이 어느 셸에서 돌려도 같은 결과를 낸다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000223 훅 시험이 어느 셸에서 돌려도 같은 결과를 낸다

## Purpose

훅 시험이 CLAUDE_PROJECT_DIR 가 설정된 셸에서 144개 실패해 시험 결과를 코드가 아니라 환경이 정하므로, 시험이 스스로 환경을 고정해 어디서 돌려도 같은 결과가 나게 한다

## Actions

없음 — 시험 준비 한 자리를 고치는 한 덩어리다.

## User value

훅 시험 결과를 어느 셸에서든 믿을 수 있다. 지금은 클로드 코드 세션 안(변수가 늘 설정돼
있다)에서 돌리면 코드가 멀쩡해도 144개가 실패해, 시험이 코드가 아니라 환경을 잰다.

## Scope

### Included

- 시험이 스스로 환경을 고정한다 — `test_stage_guard.py` 의 준비 단계(setUp 또는 공용 헬퍼)가
  `CLAUDE_PROJECT_DIR` 를 지우거나 시험용 값으로 못 박는다. 원인: 작업 공간 뿌리를 정하는
  코드가 페이로드의 `cwd` 보다 그 환경 변수를 먼저 본다. 시험은 임시 디렉터리를 `cwd` 로
  넘기는데 변수가 실제 저장소를 가리키면 훅이 엉뚱한 곳을 보고 판정한다.
- 같은 이유로 흔들리는 변수가 더 있으면(예: `PROJECT_ROOT`) 같은 자리에서 함께 고정한다.

### Excluded

- 뿌리 결정 순서 자체(환경 변수 우선 → cwd 우선)는 안 바꾼다. 그 순서는 훅이 호스트에서
  도는 방식의 계약이라, 바꾸려면 별도 결정이 필요하다.

## Risks

- 고정이 시험 파일 하나에만 붙으면 다른 훅 시험 파일이 같은 자리를 밟는다. 준비가 공용
  자리에 있으면 거기에 붙인다 — 다만 이 카드의 범위는 `test_stage_guard.py` 이므로, 공용
  자리를 고치는 것이 맞으면 경계 넘음으로 보고한다.

## Success criteria

- CLAUDE_PROJECT_DIR 를 설정한 채 훅 시험을 돌려도 전부 통과한다
- 그 변수를 지운 채 돌려도 결과가 같다

## Next action

`test_stage_guard.py` 의 준비 단계에서 환경 변수를 고정하고, 설정한 채/지운 채 두 번 돌려
같은 결과를 확인한다.

## Related truth

- O-00000033 — 실측 원문(W-00000215 판정자 발견): 변수 유무만으로 144 실패 ↔ 전부 통과.
  이 카드가 닫히면 그 관측을 닫는다.


## Progress


## Verification


## Retrospective


## Promotion decision
