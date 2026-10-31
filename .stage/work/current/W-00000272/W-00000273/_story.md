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
retrospective: completed
retrospective_ref: R-00000273
promotion: pending
review: pending
scope: .stage/research/llm-work/implementation-design.md, .stage/decisions/pending/
promotes: .stage/official/decisions/records/DE-00000074.md
decision_refs: DE-00000074
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

설계·실행 준비물을 승인받아 커밋했고 세 제품도 구현했습니다. W-00000277의 실제 시험 결과를 확인한 뒤 설계 카드의 회고와 종료를 마칩니다.
2026-10-05 사용자가 등록 커밋을 승인했습니다. 해당 커밋에서 별도 worktree를 만들어 Claude가 설계하고 Codex가 검토합니다.

## Related truth

SSOT, MECE, AHA, SoC, Honesty를 적용합니다.
부모 카드의 연구 경로에서 decision-criteria.md, session-continuity.md, avatar.md와 findings/2026-10-05-distill.md를 읽습니다.
Stage와 Distill의 현재 코드를 다시 대조하며 연구 문서를 구현 사실로 대신하지 않습니다.

## Progress

2026-10-05: 작업을 등록했습니다. 연결 설계는 아직 작성하지 않았습니다.

2026-10-05: Claude(Opus 5.5)가 설계 초안을 썼습니다. [구현 설계](../../../../research/llm-work/implementation-design.md)와 [DE-00000074](../../../../decisions/pending/DE-00000074.md)(`status: open`)입니다.
첫 실행에서 Claude가 소스를 읽고 있을 때 Codex 실행자가 SIGINT를 보내 그 실행을 멈췄습니다. 이어진 실행에서 같은 Claude 작성자가 초안을 마쳤습니다.
설계는 Distill(`f186e001`)과 이 worktree의 Stage 소스를 직접 읽고 썼습니다. 연구 문서를 구현 사실로 대신하지 않았습니다.
당시 Distill 프로젝트 판별 비교는 실행 권한이 없어 돌리지 못했고, 실행자에게 요청으로 남겼습니다.

2026-10-05: Codex·감독 독립 검토가 초안을 반려했습니다. 지적 13개를 모두 받아들여 Claude(Opus 5.5)가 설계 문서와 DE-00000074를 고쳤습니다.
고친 내용:
- snapshot 나이 대신, 넘기는 순간에 생산자 CLI를 부르고 선택 직전마다 `criteria check`를 부릅니다.
- TTY 확인을 없애고 대화 원문과 출처를 받는 확인 동작으로 바꿨습니다.
- 멱등 키와 의미 digest로 같은 요청을 가립니다.
- 출처에 참조·원문·digest·행위자를 남깁니다. `stage:` 출처를 지원하고, 출처가 바뀌거나 없어지면 표시합니다.
- 앞선 결과는 파일 sha256과 실행 증거로 대조합니다.
- Avatar 출처 투영의 규칙을 정했습니다.
- Distill은 선언된 정적 검사를 전부 통과해야 완료입니다.
- novel-ai 구현 worktree에서 그 worktree의 드라이버로 실행합니다. 기점은 `f186e001`로 고정했습니다.
- 기준 충돌을 푸는 순서와 조건의 AND/OR·경로 판정을 정했습니다.
- 실제 검증은 과제를 미리 고정하고, 결과를 모두 남깁니다.
- 명령 예시의 경로는 자리표시자로 바꿨습니다.
표식 파일 비교는 감독이 실제로 실행했고, 그 결과를 감독이 보고한 출력으로 인용했습니다. 제품 코드, 설정, 커밋은 바꾸지 않았습니다.

2026-10-05: Codex 재검토는 전체 방향을 받아들였습니다. 다만 계약 오류 8개가 남았다고 지적했습니다. Claude(Opus 5.5)가 해당 절만 고치고 DE-00000074를 맞췄습니다.
- 생산자 명령을 JSON argv 배열(`shell=False`)로 받습니다. 받은 AI에게는 완성된 check 배열을 packet에 실어 줍니다.
- 멱등 digest에 동작 이름, 대상 ID와 버전, payload 전체를 넣습니다.
- 투영을 버전 digest와 봉투 digest로 나눴습니다.
- `check` 결과는 `eligible_current`일 때만 적용합니다. 확인되지 않은 버전, 제안 상태, 다른 범위의 기준은 적용하지 않습니다.
- `partial`과 `needs_judgment`는 판단을 기록한 뒤에 적용합니다. 조건 항목끼리는 AND, 항목 안에서는 OR로 판정합니다.
- `stage:` 출처의 경로 안전과 출처 상태를 정하고, 출처가 바뀌거나 사라진 결정은 `unresolved`로 처리합니다.
- Distill 완료 검사를 `uv run mypy src/`와 `uv run ruff format --check src/ tests/`를 포함한 네 가지로 바로잡았습니다.
- novel-ai 구현 worktree 준비는 감독이 했다고 보고한 사실로 반영했습니다.
외부 worktree는 읽지도 고치지도 않았습니다.

2026-10-06: Avatar 확인이 기존 버전을 고치지 않고 N+1을 만든다는 점과 scope 객체 모양을 설계에 명시했습니다. 원래 검토본의 digest를 남겼으며 Claude의 최종 수정 리뷰가 이 설명을 승인했습니다. Stage의 모호한 경로를 unresolved로 두는 규칙도 표에 반영했습니다. SSOT·Honesty를 적용합니다.

## Verification

Stage 감사는 구조 검사입니다. 설계의 타당성과 소유자 승인까지 대신하지 않습니다.

`design` 종류의 통과 기준은 소유자의 리뷰와 승인입니다.
2026-10-05: 작업 소유자 Codex가 Claude와 다른 입장에서 수정본을 검토했고 성공 기준 3개 모두 통과로 판단했습니다. 판정 원본은 `.stage/.runtime/driver/reviews/W-00000273-owner.json`입니다.
기록 소유자와 공개 호출 경로, 확인·범위·변경·철회 처리, 두 저장소의 별도 실행과 검증 경계를 확인했습니다.
기존 경로에 기준 기능을 더하지 않는다는 문구는 정적 검사 오류 수정까지 금지한다는 뜻이 아니므로, 동작을 보존하는 수정은 허용한다고 명시했습니다.
설계를 채택했지만 종료 명령과 회고는 아직 실행하지 않았습니다. frontmatter의 완료 관련 표시는 그 절차 뒤에 갱신합니다.
실행 조건: 구현 카드를 드라이버로 돌리려면 따로 승인받은 설계 커밋이 필요합니다. novel-ai 구현 worktree에도 하네스 커밋 승인이 필요합니다.
수정 전 초안에서 실행한 검사 결과(2026-10-05):

- `python3 stage/scripts/audit_stage.py --project-root .`: 종료 코드 1, 오류 1개, 경고 32개. 경고는 보관 기록의 빈 성공 기준(WORK029)으로 등록 때와 같습니다. 오류는 `DECISION004`입니다. 새 DE-00000074가 생성형 인덱스 `.stage/decisions/index.md`에 아직 없습니다. 이 파일은 작성자의 쓰기 허용 경로 밖이라 감독이 `python3 stage/scripts/refresh_decision_index.py --project-root .`로 고쳐야 합니다.
- `git diff --check`: 출력 없음. 새 파일 두 개는 `git diff --no-index --check /dev/null <path>`로 따로 보았고 출력이 없었습니다.

수정본에서 다시 실행한 검사 결과(2026-10-05):

- 감사: 종료 코드 1, 오류 1개(`DECISION004`, 인덱스는 감독이 갱신할 몫), 경고 32개(WORK029). 수정 전과 같습니다. 구조 검사가 덜 끝난 상태이고, 제품 실패는 아닙니다.
- `git diff --check`와 새 파일 두 개의 `--no-index --check`: 출력 없음.

계약 수정 뒤 다시 실행한 검사 결과(2026-10-05):

- 감사: 오류 0개, 경고 32개(WORK029)입니다. `DECISION004`가 사라졌습니다. 작성자는 인덱스를 고치지 않았으므로 감독이 갱신한 결과로 봅니다.
- `git diff --check`와 새 파일 두 개의 `--no-index --check`: 출력 없음.
- 구조 검사와 공백 검사가 통과했을 뿐입니다. 설계 승인이나 `design` 검증 통과는 아닙니다.

## Retrospective

[R-00000273](../../../retrospectives/R-00000273.md).

## Promotion decision

2026-10-31 사용자 결정에 따라 DE-00000074 를 공식 기록으로 올린다. 닫은 뒤 `.stage/official/decisions/records/DE-00000074.md` 로 옮긴다.
