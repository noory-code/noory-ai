---
id: W-00000103
title: 일감 규모 계층을 결정으로 확정하고 실행 단위로 쪼갠다
kind: design
venue: claude
source:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/**
promotes:
decision_refs: DE-00000035
---

# W-00000103 일감 규모 계층을 결정으로 확정하고 실행 단위로 쪼갠다

## Purpose

지금 Stage 는 카드 한 장이 진입점이고 그 위(목표)는 선택이다. 그래서 아무도 위를 안 세우고
사고가 날 때마다 카드가 한 장씩 는다. P-00000002 가 에픽·스토리·액션 세 규모를 도입하고 폴더가
그 계층을 갖게 하자고 제안했고, 사용자와의 토론에서 내용을 합의했다.

이 작업은 그 제안을 결정으로 확정하고 실행 단위로 쪼갠다. 코드를 고치지는 않는다.

## Scope

`.stage/**` — 결정 기록, 제안 문서, 계획 카드만 쓴다. `stage/` 플러그인 코드는 이 카드가 안
건드린다. 실행은 이 카드가 만드는 스토리들이 한다.

## Success criteria

- DE-00000035 가 `.stage/decisions/pending/` 에 있고 `status: decided` 이며 `work_item` 이
  W-00000103 을 가리킨다.
- 그 결정의 `## Where this applies` 가 코드·설정·문서·실패 경로 네 축을 각각 파일 단위로
  열거한다. 축 하나라도 비어 있으면 실패다.
- 그 결정이 스키마 v5 로 올리고 기존 카드를 전부 새 모양으로 옮기는 길을 택했다고 명시하고,
  택하지 않은 길(스캐너가 옛 모양과 새 모양을 함께 알아듣게 두는 것)과 그 이유를 적는다.
- P-00000002 의 `## Status` 가 DE-00000035 를 가리킨다.
- 실행 에픽 한 장과 그 밑 스토리들이 `.stage/work/planned/` 에 있고, 각 스토리의 `parent` 가
  에픽을 가리킨다.
- `python3 stage/scripts/audit_stage.py --project-root .` 이 errors=0 을 낸다.

## Related truth

- P-00000002 — 합의된 제안. 세 규모, 폴더 계층, 이동 단위, 마일스톤 분리, `parent` 제거.
- DE-00000007 — "한 덩어리가 세 자리를 지난다". 계층이 서도 이 정신은 남고 덩어리만 커진다.
- W-00000098 — 결정 기록에 적용 자리를 세어 적으라는 규칙을 넣었다.
- W-00000102 — 그 규칙을 코드 호출 지점 너머로 넓혀야 한다는 학습.

## Progress

- 적용 자리를 네 축에서 셌다. 코드 38자리(평평한 스캔 13, ID→경로 조립 23, 경로 SSOT 2)와
  `parent` 를 읽는 파일 5개, 설정 4개 키, 문서 14개 파일, 실패 경로 7군데.
- 세는 도중 제안서가 덜 답한 곳이 나왔다. "기존 카드 백 장은 그대로 두고 새것부터" 가 성립하지
  않는다 — 카드를 훑는 코드가 하나라서 옛것과 새것이 같은 스캐너 안에서 같이 산다. 사용자가
  스키마 v5 로 올리고 전부 옮기는 쪽을 택했다.
- DE-00000035 를 `decided` 로 기록했다.
- P-00000002 의 Status 가 DE-00000035 를 가리킨다.
- 에픽 W-00000104 와 스토리 다섯 장(W-00000105~110)을 등록했다.
- 쪼개는 도중 계층 게이트의 비대칭을 실제로 밟았다. 계획 카드는 계획 부모를 못 갖는다. 에픽을
  먼저 진행으로 올려 해결했고, 원인과 함께 DE-00000035 의 실패 경로 표와 W-00000107 에 적었다.

## Verification


## Retrospective


## Promotion decision
