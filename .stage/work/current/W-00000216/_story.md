---
id: W-00000216
title: 감사가 두-자리 허가증을 잡는 동작을 시험으로 못 박는다
kind: qa
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000216 감사가 두-자리 허가증을 잡는 동작을 시험으로 못 박는다

## Purpose

다 쓴 허가증이 대기 서랍과 보관함에 함께 남는 상태를 감사가 잡는 것은 확인됐지만 그 동작을 붙드는 시험이 없어 일반 규칙에 예외가 하나 더 붙으면 소리 없이 사라질 수 있으므로, 그 상태를 만든 픽스처 시험으로 동작을 못 박는다

## Actions

없음 — 시험 하나를 더하는 한 덩어리다.

## User value

허가증(venue 예외 결정)을 보관함으로 옮기다 마지막 삭제만 실패하면 같은 기록이 대기 서랍과
보관함에 함께 남고, 그때 다 쓴 허가증이 새 카드를 정책과 다른 venue 에 등록시킬 수 있다.
지금은 감사의 일반 중복 규칙(SSOT001)이 이 상태를 잡는 것이 확인돼 있지만(2026-08-06,
W-00000213 에서 두 번 재현), 그 규칙은 W 중복과 R 중복을 이미 예외로 빼는 중이라 예외가
하나 더 붙으면 이 보호가 시험 하나 안 깨지고 사라진다. 시험이 생기면 그 후퇴가 소리를 낸다.

## Scope

### Included

- `test_audit_stage.py` 에 픽스처 시험 하나: 같은 `DE-` id 의 기록 파일을
  `decisions/pending/` 과 `official/decisions/archive/` 양쪽에 둔 프로젝트에서 감사가
  그 상태를 오류로 잡을 것을 요구한다.
- 오류 코드가 SSOT001 인지까지는 못 박지 않는다 — 계약은 "잡는다"이지 "어느 규칙이 잡는다"가
  아니다.

### Excluded

- 감사 규칙 자체(`audit_stage.py`)는 안 바꾼다. 동작은 이미 있고 시험만 없다.
- 옮기기를 원자적으로 만드는 길, 참조 해석 순서를 바꾸는 길은 O-00000032 가 적어 둔 다른
  갈래로 남는다.

## Risks

- 픽스처가 실제 실패 상태와 같아야 한다. 보관 코드는 파일 이름과 본문을 그대로 옮기므로
  (`archive_work.py` 의 `apply_consumed_decisions`), 픽스처도 같은 이름·본문 사본이어야 한다.

## Success criteria

- 같은 DE 기록을 decisions/pending 과 official/decisions/archive 에 함께 둔 픽스처에서 감사 오류를 요구하는 시험이 있고 통과한다
- 그 시험이 생긴 근거로 O-00000032 를 닫는다

## Next action

`test_audit_stage.py` 의 기존 픽스처 헬퍼를 찾아 두-자리 상태를 만들고 감사 오류를 요구하는
시험을 더한다.

## Related truth

- O-00000032 — 실측 원문. 이 카드가 닫히면 그 관측을 닫는다(둘째 성공 기준). 닫는 것 자체는
  감독 세션이 한다.

## Progress

## Verification

## Retrospective

## Promotion decision
