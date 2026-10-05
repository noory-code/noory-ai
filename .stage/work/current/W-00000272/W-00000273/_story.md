---
id: W-00000273
title: 세 플러그인이 기준과 근거를 주고받는 약속을 정한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/research/llm-work/implementation-design.md, .stage/decisions/pending/
promotes:
decision_refs:
---

# W-00000273 세 플러그인이 기준과 근거를 주고받는 약속을 정한다

## Purpose

각 플러그인이 독립적으로 동작하면서 같은 기준의 출처와 변경 이력을 잃지 않도록 연결 방법을 정합니다

## Actions

등록 커밋과 별도 worktree를 준비한 뒤 Claude가 설계합니다. Codex가 결과를 검토합니다.

## User value

다음 세션이 기준을 읽을 때 출처와 적용 범위를 추측하지 않아도 되도록 약속을 정합니다.

## Scope

### Included

- Stage 결정 원문, Distill의 파생 규칙, Avatar 개인 기준의 소유 위치와 안정적인 참조를 정합니다.
- 생성·확인·예외·변경·철회·조회·내보내기의 입력과 결과, 잘못된 입력의 처리를 정합니다.
- 각 플러그인이 없는 경우에도 가능한 동작과 두 저장소에서 별도로 검사할 경계를 정합니다.
- Claude와 Codex의 기준 전달 시점을 정하고 실제로 사용했음을 확인할 증거를 정합니다.
- 설계 결정을 pending에 기록하고 적용한 원칙을 적습니다.

### Excluded

- 제품 코드, 사용자 설정과 저장소 실행 정책을 임의로 바꾸지 않습니다.
- 전체 대화 자동 수집이나 모든 판단을 가로채는 기능을 첫 범위로 확대하지 않습니다.

## Risks

Distill은 이미 전역 기억과 관계 기록을 제공합니다. Avatar의 가치를 단순한 전역 저장으로 중복시키지 않습니다.
두 저장소를 하나의 변경 목록으로 취급하면 검증 증거가 빠집니다. 각 저장소의 실행과 검토 경계를 설계에 포함합니다.

## Success criteria

- 각 기록을 어디에서 고치고 다른 플러그인이 어떻게 참조하는지 한 곳에서 확인할 수 있습니다
- 새 기준과 예외와 AI의 추정을 구별하고 이전 기준을 적용하지 않을 조건을 구체적인 사례로 검토합니다
- 두 저장소에서 각각 구현하고 검증할 범위와 순서가 정해져 구현자가 제품 역할을 다시 정할 필요가 없습니다

## Next action

부모 카드의 사용자 합의와 현재 소스를 읽고 implementation-design.md 초안을 작성합니다. 데이터 필드와 실제 사례를 함께 제시한 뒤 독립 검토를 받습니다.
2026-10-05 사용자가 등록 커밋을 승인했습니다. 해당 커밋에서 별도 worktree를 만들어 Claude가 설계하고 Codex가 검토합니다.

## Related truth

SSOT, MECE, AHA, SoC, Honesty를 적용합니다.
부모 카드의 연구 경로에서 decision-criteria.md, session-continuity.md, avatar.md와 findings/2026-10-05-distill.md를 읽습니다.
Stage와 Distill의 현재 코드를 다시 대조하며 연구 문서를 구현 사실로 대신하지 않습니다.

## Progress

2026-10-05: 작업을 등록했습니다. 연결 설계는 아직 작성하지 않았습니다.

## Verification

Stage 감사는 구조 검사입니다. 설계의 타당성과 소유자 승인까지 대신하지 않습니다.

## Retrospective

설계 검토 뒤 작성합니다.

## Promotion decision

pending
