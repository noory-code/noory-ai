---
id: W-00000292
title: 실행 환경을 venue 와 나누고 클라우드 실행을 정책으로 허용한다
kind: development
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_paths.py, stage/hooks/stage_work.py, stage/skills/stage-work/register_work.py, stage/scripts/start_work.py, stage/scripts/audit_stage.py, stage/scripts/claude_review_companion.py, stage/scripts/tests/test_environment_venues.py, stage/operations/cloud-execution.md, stage/docs/SCHEMA_V4.md, stage/templates/v4/project-stage/settings.jsonc, .stage/settings.json, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000082, DE-00000083
---

# W-00000292 실행 환경을 venue 와 나누고 클라우드 실행을 정책으로 허용한다

## Purpose

클라우드에서 실행하는 카드마다 같은 venue 예외 결정을 세우지 않고, 실행한 쪽과 실행한 자리를 카드에 따로 정직하게 남긴다.

## Actions

DE-00000082 의 "Where this applies" 표가 바꿀 자리를 센다. 요약:

- 카드에 선택 칸 `environment`, 설정에 `environment_venues` 를 둔다.
- 등록·시작 도구와 감사가 같은 허용 조건(선언된 환경, 그 환경의 venue, `review` 가 `pending`·`passed`)을
  공유 함수 하나로 판정한다. 조건을 어기면 이유와 함께 거절하고, 감사는 VENUE006 을 낸다.
- 클라우드 실행 계약(세션 브랜치 커밋·push, 커밋 본문 실행 보고와 이관 도구, 코드 커밋 worktree 에서
  닫기, codex 대역 리뷰)을 `stage/operations/cloud-execution.md` 로 옮긴다. 대역 리뷰를 돌리는
  `stage/scripts/claude_review_companion.py` 를 저장소에 둔다.

## User value

클라우드에서 카드를 돌릴 때 결정 기록을 새로 쓰지 않아도 되고, 카드만 보면 누가 어디서 실행했는지가
읽힌다.

## Scope

### Included


### Excluded

- 섞인 종류(`split`) 규칙.
- 이미 닫힌 클라우드 카드(W-00000268~291)의 기록을 고치는 일.

## Risks


## Success criteria

- environment 가 선언된 환경을 가리키고 venue 가 그 환경의 venue 이며 독립 닫기 리뷰를 요구하는 카드는 예외 결정 없이 등록·시작되고 감사를 통과한다는 것을 테스트가 확인한다
- 선언되지 않은 환경, 환경과 다른 venue, 닫기 리뷰를 요구하지 않는 카드는 등록·시작·감사에서 이유와 함께 거절된다는 것을 테스트가 확인한다
- 클라우드 실행·이관·닫기 절차가 한 문서에 있고 그 절차가 쓰는 도구가 저장소에 있다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
