---
id: W-00000272
title: Stage·Distill·Avatar로 기준 변경과 세션 인계를 연결한다
kind: planning
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/research/llm-work/, stage/, avatar/, /Users/woogis/Workspace/novel-workspace/novel-ai/plugins/distill/
promotes:
decision_refs:
---

# W-00000272 Stage·Distill·Avatar로 기준 변경과 세션 인계를 연결한다

## Purpose

사용자가 밝힌 판단 기준을 다른 AI 세션에서도 적용하고 기준이 바뀐 이유와 실제 선택을 다시 살펴볼 수 있게 합니다

## Stories

| 순서 | 작업 | 결과 |
|---|---|---|
| 1 | [연결 약속](W-00000273/_story.md) | 기록의 소유 위치와 교환 형식, 변경 처리 방법을 정합니다. |
| 2 | [Distill](W-00000274/_story.md) | 출처와 적용 조건을 보존하고 현재 기준을 돌려줍니다. |
| 3 | [Stage](W-00000275/_story.md) | 목적과 현재 기준, 실제 결과를 읽고 이어갑니다. |
| 4 | [Avatar](W-00000276/_story.md) | 선택과 기준의 변화를 돌아보고 수정합니다. |
| 5 | [실제 AI 검증](W-00000277/_story.md) | 두 호스트에서 첫 흐름을 끝까지 확인합니다. |

## User value

이미 밝힌 기준을 매번 다시 설명하는 수고를 줄이고, 기준을 바꾼 뒤에도 AI가 옛 기준을 계속 쓰는 일을 막으려 합니다.

사용자는 “Stage·Distill·Avatar 세 플러그인”을 지정한 뒤 제안한 첫 구현 흐름에 “네 진행해주세요.”라고 답했습니다.
마일스톤 질문에는 “마일스톤 없이 이번 구현을 하나의 작업 묶음으로 등록”이라고 답했습니다.

## Scope

### Included

- Stage와 Distill의 기존 구조를 보완하고 Avatar를 새로 만듭니다.
- 기준 저장, 다른 AI의 작업 인계, 기준 변경 반영, Avatar의 출처·변경 이유 조회를 연결합니다.
- 공개 도구나 파일과 안정적인 ID로 연결하며 다른 플러그인의 내부 모듈을 가져오지 않습니다.
- 첫 버전은 사용자가 밝힌 기준과 허용한 기록을 다룹니다. 자동 수집 범위는 설계에서 명시합니다.

### Excluded

- 관련 없는 기존 변경의 정리, 자동 커밋·푸시, 공개 배포는 이 묶음의 완료 조건에 넣지 않습니다.
- 사람의 취향을 완전히 학습했다거나 메타인지가 개선됐다고 주장하지 않습니다.

| 포함한 결과 | 증명할 성공 기준 |
|---|---|
| 기준을 적용하며 세션을 이어갑니다. | 첫 번째 기준 |
| 기준 변경을 반영합니다. | 두 번째 기준 |
| 선택을 돌아보고 기준을 고칩니다. | 세 번째 기준 |
| 독립 사용과 두 호스트의 연결을 확인합니다. | 네 번째 기준 |

## Risks

| 확인할 부분 | 수 | 영향받는 곳 | 확인했지만 바꾸지 않을 곳 |
|---|---:|---|---|
| 진입 경로와 사용자 | 4곳 | Claude, Codex, Stage 재개, Avatar에서 사람이 기준을 수정하는 경로 | 기존 리뷰의 독립성은 유지합니다. |
| 상태 변화 | 6가지 | 생성, 확인, 임시 예외, 변경, 철회, 세션 재개 | 첫 범위에서 외부 서비스의 실행을 자동 재시도하지 않습니다. |
| 기존 책임 | 3곳 | Stage의 작업·결정 기록, Distill의 저장·검색·규칙 생성, Avatar의 개인 기준 | Distill의 전역 기억 기능을 새 기능처럼 만들지 않습니다. |
| 결과와 실패 기록 | 4곳 | 조회 결과, Stage 인계, Avatar 변경 이력, 실제 CLI 검증 기록 | 관련 없는 기존 작업 기록은 보존합니다. |

두 저장소의 변경·검증·릴리스 규칙이 다릅니다. 외부 저장소 변경을 noory-ai 드라이버의 관측 결과처럼 보고하지 않습니다.
현재 noory-ai에는 기존 미커밋 변경이 있습니다. 독립 실행에 앞서 이 변경과 새 등록만 구별해야 합니다.

## Success criteria

- 기준을 저장한 뒤 다른 AI가 그 기준과 앞선 결과를 읽고 같은 작업을 이어갑니다
- 기준을 바꾸면 다음 판단에서 이전 기준을 현재 기준처럼 적용하지 않습니다
- Avatar에서 선택의 근거와 기준의 변경 이력을 출처까지 확인하고 개인 기준을 고칠 수 있습니다
- 각 플러그인은 독립적으로 사용할 수 있고 Claude와 Codex에서 첫 연결 흐름을 실제 실행해 확인합니다

## Next action

연결 약속을 정하는 W-00000273부터 수행합니다. 설계는 Claude, 구현은 Codex로 나눕니다.
2026-10-05 사용자가 새 카드 6개와 인덱스 행 6개만 커밋하고 계속 진행하도록 승인했습니다. 이 등록을 커밋한 뒤 별도 worktree에서 설계를 진행합니다.

## Related truth

- 원칙: SSOT, MECE, AHA, TDD, Honesty, Completion.
- 기존 연구는 /Users/woogis/Workspace/repo/noory-ai/.stage/research/llm-work/synthesis.md에서 시작합니다.
- Stage 목적은 stage/docs/PHILOSOPHY.md를 따릅니다.
- Distill 저장소는 /Users/woogis/Workspace/novel-workspace/novel-ai입니다. 해당 저장소 CLAUDE.md와 plugins/distill/CONTRIBUTING.md를 따릅니다.

## Progress

2026-10-05: 사용자 합의에 따라 마일스톤 없이 묶음과 하위 작업 다섯 개를 등록했습니다. 제품 구현은 아직 시작하지 않았습니다.

## Verification

등록 후 Stage 감사를 실행했습니다. 오류는 0개였고 기존 보관 기록의 빈 성공 기준에 대한 경고 32개가 나왔습니다.
연구 자료 검사와 `git diff --check`도 통과했습니다. 구현과 실제 CLI 검증은 하위 작업에서 증거를 모읍니다.

## Retrospective

하위 작업의 결과와 독립 검토가 끝난 뒤 작성합니다.

## Promotion decision

설계 결정은 소유자가 승인한 뒤 해당 작업에서 승격 여부를 정합니다.
