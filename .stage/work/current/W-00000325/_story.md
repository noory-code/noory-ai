---
id: W-00000325
title: 루트 CLAUDE.md 에서 코드로 알 수 있는 내용을 지운다
kind: documentation
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
review: not_required
scope: CLAUDE.md
promotes:
decision_refs:
---

# W-00000325 루트 CLAUDE.md 에서 코드로 알 수 있는 내용을 지운다

## Purpose

세션마다 읽히는 루트 CLAUDE.md 에서 코드로 알 수 있는 내용을 지워, 모든 세션이 읽는 분량을 약 500 토큰(추정) 줄인다.

## Actions

- 이 story 하나로 끝난다. 나눌 단계가 없다.

## User value

Claude 와 Codex 세션이 시작할 때마다 읽는 분량이 줄어든다. 사용자가 /doctor 점검 결과를 보고 이 정리를 고른 일이다.

## Scope

### Included

- 루트 `CLAUDE.md` 에서 디렉터리 트리 코드 블록을 지운다. 어떤 패키지가 uv 프로젝트가 아닌지 밝힌 문단은 남긴다.
- `## Commands` 의 표준 `uv` 명령 블록과 Evonest 전용 명령 블록을 지운다. 패키지 폴더 안에서 실행한다는 안내 문단은 남긴다.
- `## Architecture` 의 `### Evonest` 절과 `## Code Conventions` 의 `- Evonest uses dataclasses` 줄을 지운다. 같은 내용이 `evonest/CLAUDE.md` 에 있다.

### Excluded

- 다른 규칙 절(언어, 핵심 원칙, 플러그인 변경, 크로스 플랫폼, Novel AI)은 손대지 않는다.
- `AGENTS.md` 와 `evonest/CLAUDE.md` 는 바꾸지 않는다.

## Risks

- Codex 는 `AGENTS.md` 를 거쳐 루트 `CLAUDE.md` 를 읽는다. `AGENTS.md` 는 이 파일에 배치·명령·아키텍처가 있다고 적었는데, 배치 문단과 명령 안내와 Novel AI 절이 남으므로 그 설명은 계속 맞다.
- Evonest 의 핵심 파일 목록(`orchestrator.py`, `phases.py`, `mutations.py`)은 `evonest/CLAUDE.md` 에 없다. 파일 이름은 `ls` 로 알 수 있고, 규칙은 그쪽에 모두 있다.


## Success criteria

- git diff 에서 디렉터리 트리, 표준 uv 명령 블록, Evonest 아키텍처 절, Evonest dataclasses 줄만 빠지고 나머지 규칙과 패키지 폴더 안에서 실행한다는 안내는 그대로 남는다.
- 빠진 Evonest 규칙(Tool/Core 분리, state.py 단일 입구, 3단 설정, mutations 읽기 전용)을 evonest/CLAUDE.md 에서 모두 찾을 수 있다.
- audit_stage.py 가 errors=0 을 낸다.

## Next action

루트 `CLAUDE.md` 에서 네 덩어리를 지우고 완료 기준을 확인한다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
