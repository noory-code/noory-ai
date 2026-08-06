---
id: W-00000213
title: 감사가 대기 서랍과 보관함의 같은 기록을 잡게 한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q"
status: archived
terminal_disposition: rejected
verification: pending
retrospective: completed
retrospective_ref: R-00000212
promotion: not_applicable
review: not_required
scope: stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000213 감사가 대기 서랍과 보관함의 같은 기록을 잡게 한다

## Purpose

허가증을 보관함으로 옮기다 마지막 삭제만 실패하면 다 쓴 허가증이 대기 서랍에 남아 다시 통과하므로, 같은 결정 기록이 대기 서랍과 보관함에 함께 있으면 감사가 오류로 잡게 한다

## Actions

없음 — 감사 규칙 하나와 그 시험을 더하는 한 덩어리다.

## User value

venue 예외 허가증은 카드 한 장만 위한 것이다. 옮기다 마지막 삭제만 실패해 두 자리에 남으면
다 쓴 허가증이 새 카드를 정책과 다른 venue 에 등록시킬 수 있는데, 지금은 그 상태를 아무도
안 잡는다. 감사가 잡으면 사람이 수습할 자리를 안다.

## Scope

### Included

- `audit_stage.py` 에 규칙을 더한다: 같은 `DE-` id 의 기록 파일이 `decisions/pending/` 과
  `official/decisions/archive/` 양쪽에 있으면 오류를 낸다.
- 그 상태를 만든 프로젝트 픽스처로 시험을 `test_audit_stage.py` 에 더한다.

### Excluded

- 옮기기 자체를 원자적으로 만드는 길, 참조 해석 순서를 바꾸는 길은 안 간다. O-00000032 가
  세 갈래를 적었고 감사가 잡는 것이 가장 싸다 — 명령이 실패를 이미 알리므로, 남는 위험은
  "사람이 놓친 뒤"뿐이고 감사가 그 자리를 덮는다.

## Risks

- 기존 규칙(`SSOT001` 계열)과 겹치면 같은 상태에 오류가 두 번 나 소음이 된다. 겹치는지
  확인하고, 겹치면 기존 규칙을 넓히는 쪽이 맞다.

## Success criteria

- 같은 DE 기록이 decisions/pending 과 official/decisions/archive 양쪽에 있으면 감사가 오류를 낸다
- 정상 프로젝트의 감사 결과는 달라지지 않는다

## Next action

`audit_stage.py` 에서 결정 인덱스·기록을 이미 읽는 자리를 찾아, 거기에 두-자리 검사를 끼울지
새 규칙으로 세울지 정한다.

## Related truth

- O-00000032 — 구멍의 원문: 네 걸음 중 마지막 삭제만 실패하면 대기본이 이기고, 유효성 검사가
  그 사본을 읽어 다 쓴 허가증이 다시 통과한다. 이 카드가 닫히면 그 관측을 닫을 근거가 된다.


## Progress

워크트리 병렬 실행 1바퀴. 실행자(코덱스)가 규칙을 더하지 않고 "이미 충족"으로 판정했다 —
감사의 일반 중복 규칙(SSOT001)이 대기 서랍과 보관함을 둘 다 소유 경로로 읽는다. 판정자
(클로드)가 두 번 재현했다: 빈 템플릿 프로젝트와 이 프로젝트 `.stage` 사본에 같은 DE 기록을
두 자리에 두니 각각 SSOT001 오류가 났다(errors 0 → 3, 그중 SSOT001 두 건).

## Verification

판정: 기준 둘 다 PASS, approved. 판정자 소견의 처분 —

- 동작은 있지만 이 짝을 붙드는 시험이 없다. SSOT001 은 이미 W·R 중복을 예외로 빼는 중이라
  예외 하나가 더 붙으면 이 구멍이 시험 하나 안 깨지고 다시 열린다 → **수용.** 이미 되는
  동작을 픽스처 시험으로 못 박는 계획 카드를 등록하고, O-00000032 는 그 카드가 닫힐 때까지
  열어 둔다.

## Retrospective

R-00000212 참조.

## Promotion decision

not_applicable — 결정 기록 없음, 승격 경로 없음. 카드 자체는 물림(2026-08-06, 감독 세션):
목적이 등록 시점에 이미 충족돼 있었다. 못 박는 시험은 계획 카드로 넘겼다.
