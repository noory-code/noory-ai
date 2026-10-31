---
id: W-00000310
title: 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_claude_review_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/driver_supervised.py, stage/scripts/driver_unattended.py, stage/scripts/driver_review.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/claude_review_companion.py, stage/templates/v4/project-stage/settings.jsonc, stage/scripts/tests/, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000310 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다

## Purpose

Codex 리뷰어나 다른 프로젝트의 Claude 리뷰어가 돌린 시험 코드가 저장소를 바꿔도 그 리뷰가 승인으로 끝나지 않게 한다

## Actions

- W-00000309 가 `stage/scripts/claude_review_companion.py` 에 넣은 앞뒤 스냅숏 비교(`driver_repository.repository_path_snapshot`)를
  리뷰어 명령을 부르는 자리(감독·무인 드라이버, `close_work.py`)로 옮겨 모든 리뷰어에 건다. 대역의 검사는 그 공통 검사로
  대체해 한 곳만 남긴다(SSOT).
- v4 템플릿(`stage/templates/v4/project-stage/settings.jsonc`)의 Claude 리뷰 명령이 공통 검사를 받게 한다.

## User value


## Scope

### Included


### Excluded


## Risks

- 리뷰 중에 사람이 같은 체크아웃을 만지면 그 변경도 리뷰 실패로 잡힌다(O-00000013 과 같은 모양). 실패 메시지가 그
  가능성을 알려야 한다.
- 실측 근거: W-00000309 의 Progress. `python3 -m unittest` 가 돌린 시험 코드는 권한 규칙과 상관없이 썼다.


## Success criteria

- 드라이버와 close_work 가 어느 리뷰어 명령이든 앞뒤 저장소를 비교해 판정 파일 밖이 바뀌면 리뷰를 실패로 기록하고 바뀐 경로를 알린다는 것을 테스트가 확인한다
- v4 템플릿의 Claude 리뷰 명령이 같은 검사를 받는다는 것을 테스트가 확인한다

## Next action

## Related truth

## Progress

## Verification

## Retrospective

## Promotion decision
