---
id: W-00000296
title: claude 리뷰어 권한에서 쓰이지 않는 Write 규칙을 뺀다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .stage/settings.json, stage/scripts/claude_review_companion.py, stage/scripts/tests/test_environment_venues.py, stage/scripts/tests/test_template_v4.py, stage/templates/v4/project-stage/settings.jsonc, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000296 claude 리뷰어 권한에서 쓰이지 않는 Write 규칙을 뺀다

## Purpose

리뷰 명령이 쓰이지 않는 권한 규칙 때문에 매번 경고를 남기지 않고, 권한 설명이 실제로 쓰기를 허락하는 규칙과 맞게 한다.

## Actions

- 지금 동작: W-00000295 가 리뷰어에게 판정 파일의 `Write(...)` 와 `Edit(...)` 규칙을 함께 준다. 그 카드의 닫기에서
  Claude Code 가 "파일 권한 검사는 `Edit(path)` 규칙만 맞춘다"고 경고했고, 판정 파일은 `Edit` 규칙만으로 새로
  써졌다(R-00000295). `Write` 규칙은 쓰이지 않고 리뷰마다 경고만 남긴다.
- 프로젝트 `reviewers.claude` 명령, `claude_review_companion.py`, 두 시험, 템플릿 안내에서 `Write` 규칙을 뺀다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일에 Edit 규칙만 주고 Write 규칙을 주지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
