---
id: W-00000340
title: 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000340
promotion: not_applicable
review: pending
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/skills/stage-retrospective/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000340 닫기 도구가 승격을 나중에 쓰는 순서를 게이트에 맞게 안내한다

## Purpose

승격을 나중에 쓰는 카드가 닫기 도구의 안내만 따라도 승격 게이트에 막히지 않게 실제로 통하는 순서를 알려 준다

## Actions

없음 — 안내 문구 두 곳과 테스트를 고치는 일이라 나누지 않는다.

## User value

결정을 나중에 공식 기록으로 올리는 사람이 닫기 도구의 안내만 따라도 승격 게이트에 막히지 않는다.
2026-11-16 에 DE-00000082 를 올릴 때 안내대로 `deferred` 로 닫았다가 게이트에 막혔다.

## Scope

### Included

- `close_work.py` 가 승격을 거절할 때 내는 안내에 실제로 통하는 순서를 적는다. `deferred` 로 닫기,
  `approved` 로 바꾸기, intent 만들기, 쓰기, `promoted` 로 기록하기.
- `stage-retrospective` 스킬의 Promotion intent 절에 같은 순서를 적는다.

### Excluded

- 동작은 바꾸지 않는다. 게이트가 `deferred` 를 받게 하거나 감사가 `approved` 를 받게 하는 것은
  게이트·감사 규칙을 바꾸는 결정이라 이 카드에서 하지 않는다.

## Risks

- 닫기 도구를 고치는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).
- `approved` 가 잠깐 남아 있는 동안 감사가 WORK027 오류를 낸다. 안내에 그 상태가 쓰는 동안만이라고
  적었다.

## Success criteria

- 닫기 도구가 deferred 로 닫은 뒤 approved 로 바꾸고 intent 를 만들어 쓰고 promoted 로 기록하는 순서를 안내한다
- 닫기 도구와 게이트와 감사의 동작은 바뀌지 않는다
- 안내 문구를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action

닫기 리뷰를 받고 사용자 확인 뒤에 닫는다.

## Related truth

- W-00000337 — DE-00000082 를 올리다 이 어긋남을 처음 겪은 카드(보관됨).
- `stage/hooks/stage_runtime.py` — 승격 게이트가 `approved`·`promoted` 만 받는 자리.
- `stage/scripts/audit_stage.py` 의 `completed_promotion_errors` — 닫힌 카드의 `approved` 를 WORK027
  오류로 보는 자리.

## Progress

- 2026-11-16: `close_work.py` 의 거절 안내와 `stage-retrospective/SKILL.md` 의 Promotion intent 절에
  순서를 적었다. 같은 날 W-00000337(DE-00000082)과 W-00000265(DE-00000073)를 이 순서로 올렸다.
- 테스트: `test_refuses_promotion_records_the_audit_rejects` 에 안내 문구 확인 세 줄을 더했다.
- 코드 커밋 `617e9ac6`.

## Verification

- 판별 확인: 고치기 전에 그 테스트의 네 경우가 모두 새 확인에서 깨졌다. 고친 뒤 close_work 테스트
  74건이 통과한다.
- 동작이 바뀌지 않았다: `close_work.py` 에서 바뀐 것은 거절 메시지 문자열뿐이다. 게이트와 감사
  파일은 이 카드의 커밋에 없다.
- 세 카드(W-00000338~340)의 변경을 모두 넣고 처음 돌린 전체 테스트는 실패했다(hooks 1건, scripts
  2건, 모두 W-00000339 의 감사 검사 때문). `86c2a80e` 로 고친 뒤 hooks 446건, scripts 758건(2건
  건너뜀)이 통과했고 감사는 errors=0 이다. 이 줄은 처음에 실행 전에 "통과"로 적었다가 실제 결과로
  고쳤다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).

## Retrospective

[R-00000340](../../retrospectives/R-00000340.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
