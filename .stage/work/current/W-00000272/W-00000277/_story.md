---
id: W-00000277
title: Claude와 Codex에서 기준 변경과 작업 인계를 끝까지 검증한다
kind: qa
venue: codex
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/research/llm-work/integration/, .stage/research/llm-work/findings/
promotes:
decision_refs:
---

# W-00000277 Claude와 Codex에서 기준 변경과 작업 인계를 끝까지 검증한다

## Purpose

세 플러그인이 실제 AI 작업에서 기준을 적용하고 변경을 반영하며 선택의 이유를 남기는지 확인합니다

## Actions

앞선 세 구현이 준비되면 임시 프로젝트에서 실제 CLI 시험을 수행합니다.

## User value

파일이 존재한다는 사실을 넘어 AI가 기준을 읽고 바뀐 기준으로 이어서 일하는지 확인합니다.

## Scope

### Included

- 사용자 기준을 저장하고 다른 AI가 조회하여 남은 작업을 이어가는 사례를 양방향으로 실행합니다.
- 기준 변경과 프로젝트 예외를 넣고 옛 기준을 그대로 적용하는지 검사합니다.
- Avatar에서 출처·기준 변경·선택을 실제 명령으로 조회합니다.
- 반복한 작업, 재질문, 입력량과 경과 시간을 기록합니다.
- 새 기능을 끈 비교 조건을 함께 기록해 개선 주장의 범위를 제한합니다.

### Excluded

- 실제 개인 데이터나 기존 진행 중 작업을 실험 데이터로 변경하지 않습니다.
- 작은 사례의 결과를 일반적인 성공률이나 비용 절감률로 확대하지 않습니다.

## Risks

CLI가 정상 응답해도 파일 변경이 없을 수 있고 오류가 나도 변경은 끝났을 수 있습니다. 응답과 실제 결과를 각각 확인합니다.
CLI나 모델 설정이 바뀌면 실행 환경을 나누어 기록합니다.

## Success criteria

- 실제 Claude와 Codex에서 저장·조회·작업 인계·기준 변경·Avatar 확인 흐름을 임시 데이터로 실행한 증거를 남깁니다
- 기준 미확인과 범위 불일치와 기준 변경을 시험하고 같은 설명을 다시 요구한 횟수와 반복한 작업을 기록합니다
- 관찰한 성공과 실패와 측정할 수 없었던 항목을 구별하며 제품별 테스트와 연구 자료 검사가 통과합니다

## Next action

W-00000274부터 W-00000276까지 구현이 준비되면 입력·기대 결과·실행 한도를 먼저 고정한 뒤 시험합니다.

## Related truth

MECE, TDD, Honesty, Completion을 적용합니다. 부모 카드의 연구 경로에 있는 기존 실행 기록과 새 제품 검증을 구별합니다.

## Progress

2026-10-05: 검증 작업을 등록했습니다. 새 모델 호출은 아직 수행하지 않았습니다.

## Verification

두 저장소의 테스트 결과와 원본 CLI 응답, 실제 파일·기준 버전·Avatar 조회 결과를 함께 보존합니다.

## Retrospective

실제 비교 결과를 정리한 뒤 작성합니다.

## Promotion decision

pending
