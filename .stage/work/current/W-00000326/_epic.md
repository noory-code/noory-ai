---
id: W-00000326
title: 일감마다 맞는 모델과 에포트 레벨을 Stage 가 고르게 한다
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
scope: stage/
promotes:
decision_refs:
---

# W-00000326 일감마다 맞는 모델과 에포트 레벨을 Stage 가 고르게 한다

## Purpose

Stage가 일감마다 맞는 모델과 에포트 레벨을 고르게 한다

## Stories

- W-00000327 (design, claude) — 등급 표 설계와 Agent 훅 실측 결과를 카드에 남긴다. 아래 구현 story 넷이 따르는 설계의 SSOT 다.
- W-00000328 (development, codex) — 등급 표 설정을 읽어 등록하는 카드에 tier 를 적는다.
- W-00000329 (development, codex) — 드라이버가 카드 등급의 모델과 에포트를 실행기와 리뷰어에 넘긴다. W-00000328 의 공용 모듈을 쓴다.
- W-00000330 (development, codex) — Agent 호출의 모델과 에포트를 카드 등급에 맞추는 훅을 넣는다. W-00000328 의 공용 모듈을 쓴다.
- W-00000331 (development, codex) — 카드 등급과 실제로 돈 모델·에포트가 다르면 감사가 경고하게 한다. W-00000329 와 W-00000330 이 남기는 기록을 읽는다.

## User value

하위 에이전트와 드라이버 실행기가 부모 세션의 비싼 모델(Fable)을 그대로 물려받지 않는다. 일의 크기에 맞는 모델과 에포트를 설정 한 곳에서 고르고, 어긋나면 감사에서 보인다. 출발점은 다시나 프로젝트에서 하위 에이전트가 계속 Fable 로 돈 일이다.

## Scope

### Included

- `stage/` 플러그인의 설정 읽기, 등록, 드라이버 환경, Claude Code 훅, 감사
- 플러그인 문서(`stage/docs/SCHEMA_V5.md`, 관련 스킬, 훅 README)와 `stage/CHANGELOG.md` 의 `## Unreleased`

### Excluded

- 이 저장소의 `.stage/settings.json` 에 `model_tiers` 를 켜는 일 (켜지 않아도 지금처럼 돌아야 한다는 것이 완료 기준이다)
- 다시나 프로젝트 설정 변경과 릴리스(버전 올리기)
- Codex 호스트의 하위 에이전트 (Codex 에는 Agent 도구가 없다)

## Risks

- Claude Code 의 Agent 입력·SubagentStop 입력 모양이 바뀌면 훅과 기록이 조용히 빗나갈 수 있다. W-00000327 에 실측한 버전(2.1.321)을 적어 둔다.
- 등급 순서를 잘못 읽으면 싼 모델을 비싸다고 막거나 그 반대가 된다.
- `stage_guard.py` 의 작업 맥락 블록(`append_purpose_context`)을 다른 세션이 손보고 있다. 이 에픽은 `handle_event` 에서 Agent 와 SubagentStop 을 새 모듈로 넘기는 몇 줄만 고친다.


## Success criteria

- 일감을 등록하면 설정의 등급 표(일의 종류와 크기로 고름)가 고른 tier 가 카드에 남고, 프로젝트가 표를 덮어쓸 수 있으며, 사람이 카드에서 바꾼 tier 가 우선한다
- 드라이버가 실행기와 리뷰어를 부를 때 카드 등급의 그 venue 값을 STAGE_MODEL·STAGE_EFFORT 로 넘겨서, 실행기·리뷰어 명령에 모델을 박아 두지 않아도 된다
- 세션 안에서 Agent 도구로 맡길 때 모델·에포트를 적지 않은 호출과 카드 등급보다 비싼 모델을 이유 없이 고른 호출을 훅이 알려 주거나 막는다
- 카드에 적힌 등급의 모델·에포트와 드라이버 작업 기록·하위 에이전트 기록에 남은 실제 값이 다르면 감사가 경고한다
- settings 에 model_tiers 가 없는 스키마 v5 프로젝트는 설정을 바꾸지 않아도 지금과 똑같이 돈다(환경 변수 없음, 카드에 tier 없음, 훅 무동작)

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
