---
id: W-00000339
title: 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_audit_stage.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000339
promotion: not_applicable
review: pending
scope: stage/scripts/audit_stage.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000339 감사가 열린 기록과 그 목록 줄이 어긋난 것을 알린다

## Purpose

열린 관찰·질문·제안 기록에 목록 줄이 없거나 목록 줄이 없는 기록을 가리킬 때 감사가 알려, 닫기 도구가 막히기 전에 어긋남을 찾게 한다

## Actions

없음 — 감사 검사 하나와 테스트를 더하는 일이라 나누지 않는다.

## User value

열린 관찰이나 질문이 목록과 어긋나면 감사가 그 자리에서 알린다. 2026-11-16 에 관찰 12개가 목록
줄만 지워진 채 열린 폴더에 남아 있었는데, 감사는 오류 0개로 통과했고 세션 시작 글은 그 12개를
계속 열린 관찰로 실었다.

## Scope

### Included

- 열린 관찰(`state/observations`)과 질문(`state/questions`)이 각자의 목록(`state/current.md`,
  `state/questions.md`)과 맞는지 양쪽으로 본다. 맞지 않으면 경고(`RECORD_LIVE001`, `RECORD_LIVE002`).

### Excluded

- 제안은 넣지 않는다. 제안 목록은 `PROPOSAL001`/`PROPOSAL002` 가 이미 양쪽으로 본다. 카드 목적에
  "제안"이 들어 있지만 겹치지 않게 뺐다.
- 오류가 아니라 경고로 둔다. 이 어긋남이 있는 다른 프로젝트의 닫기가 갑자기 막히지 않게 한다.

## Risks

- 감사를 바꾸는 카드라 닫기 전에 사용자 확인을 받는다(DE-00000087).

## Success criteria

- 열린 기록에 목록 줄이 없으면 감사가 기록 이름과 함께 경고한다
- 목록 줄이 가리키는 열린 기록이 없으면 감사가 경고한다
- 목록과 기록이 맞으면 아무것도 알리지 않는다
- 이 경우를 확인하는 테스트가 고치기 전에는 깨지고 고친 뒤에는 통과한다

## Next action

닫기 리뷰를 받고 사용자 확인 뒤에 닫는다.

## Related truth

- 2026-11-16 PR #41 — 목록 줄만 지워진 관찰 12개를 닫기 도구로 정리했다.
- `close_record.py` — 목록 줄이 있어야 기록을 닫는다. 이 검사는 그 도구의 기록 묶음 정의를 쓴다.

## Progress

- 2026-11-16: `audit_stage.py` 에 `audit_live_state_indexes` 를 더했다. `close_record.FAMILIES` 의 O 와
  Q 묶음에서 열린 폴더의 기록과 목록의 줄(목록 항목의 `[O-…]` 링크, 표의 첫 칸)을 맞춰 본다.
- 테스트 `test_live_record_indexes_match_their_records`: 목록 줄이 없는 관찰, 기록이 없는 목록 줄,
  목록 줄이 없는 질문, 둘이 맞는 경우.
- 코드 커밋 `b32be111`.
- 전체 테스트에서 세 건이 깨져 `86c2a80e` 로 고쳤다. 기록 파일을 직접 훑던 것을 감사가 이미 모아 둔
  기록 목록(`graph.state`)을 쓰게 바꿨다. 기록 파일 찾기는 `stage_record_paths` 한 곳에서만 하도록
  테스트로 묶여 있다. 또 두 테스트의 준비 데이터가 열린 질문을 만들면서 목록 줄은 넣지 않아 새 검사에
  걸렸으므로, 준비 데이터에 목록 줄을 넣었다.
- 범위를 넘은 경로: `stage/scripts/tests/test_audit_link_pin.py`, `stage/scripts/tests/test_schema_v4_consumers.py`.
  위 준비 데이터를 고치느라 넘었다.

## Verification

- 판별 확인: 고치기 전에 새 테스트에서 경고가 나와야 할 경우들이 깨졌다. 둘이 맞는 경우는 고치기
  전에도 통과했다(바뀌면 안 되는 경우다).
- 실제 사례로 확인: 오늘 정리하기 전의 `.stage`(`956f5566`)에 새 감사를 돌리자 `RECORD_LIVE001`
  경고가 정확히 그 12개(O-00000020, 36, 42, 45, 47, 50, 51, 52, 53, 54, 55, 56)에만 나왔다.
- 지금 저장소에는 새 경고가 없다(감사 errors=0, warnings=32 그대로).
- 세 카드(W-00000338~340)의 변경을 모두 넣고 처음 돌린 전체 테스트는 실패했다(hooks 1건, scripts
  2건, 모두 이 카드의 감사 검사 때문). `86c2a80e` 로 고친 뒤 hooks 446건, scripts 758건(2건
  건너뜀)이 통과했다. 정리 전 `.stage` 에서 12개를 잡는 것도 고친 뒤 다시 확인했다. 이 줄은 처음에
  실행 전에 "통과"로 적었다가 실제 결과로 고쳤다.
- 닫기 리뷰는 codex 가 없어 Claude 대역으로 돌린 같은 모델의 리뷰이며, 교차 venue 리뷰가 아니다
  (DE-00000086).

## Retrospective

[R-00000339](../../retrospectives/R-00000339.md)

## Promotion decision

`not_applicable` — 공식 문서로 올릴 산출물이 없다.
