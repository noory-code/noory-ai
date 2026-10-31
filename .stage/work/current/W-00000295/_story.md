---
id: W-00000295
title: claude 리뷰어에게 판정 파일 쓰기와 시험 실행만 허락한다
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
scope: .stage/settings.json, stage/scripts/claude_review_companion.py, stage/scripts/tests/test_environment_venues.py, stage/scripts/tests/test_template_v4.py, stage/templates/v4/project-stage/settings.jsonc, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000295 claude 리뷰어에게 판정 파일 쓰기와 시험 실행만 허락한다

## Purpose

비대화형 claude 리뷰어가 사용자 권한 설정에 기대지 않고 판정 파일을 쓰고 시험을 돌리되 다른 파일은 고치지 못하게 한다.

## Actions

- 지금 동작: 이 프로젝트의 `reviewers.claude` 명령은 `claude -p` 를 권한 옵션 없이 띄운다. 비대화형 세션은
  `$STAGE_REVIEW_VERDICT_FILE` 을 쓰지도, 프로젝트 밖의 `$STAGE_CHANGED_PATHS_FILE` 을 읽지도, 시험을 돌리지도
  못한다(W-00000287 닫기에서 확인). 로컬에서는 사용자 권한 설정에 기대 왔을 가능성이 크다. 대역 리뷰어
  `claude_review_companion.py` 는 `--permission-mode acceptEdits` 로 프로젝트 파일 전체 편집을 허락한다.
- 둘 다 `--add-dir <변경 경로 파일 폴더>`, `--allowedTools "Write(/$STAGE_REVIEW_VERDICT_FILE)"
  "Edit(/$STAGE_REVIEW_VERDICT_FILE)" "Bash(python3 -m unittest:*)"` 로 바꾼다. 드라이버의 좁은 재리뷰는 판정
  파일을 임시 폴더에 두므로 폴더가 아니라 파일 하나를 허락한다.
- 2026-10-31 이 세션에서 `claude -p` 로 실험해, 판정 파일 쓰기와 바깥 폴더 읽기와 unittest 실행은 되고 같은
  폴더의 다른 파일과 프로젝트 파일 쓰기는 막히는 것을 확인했다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일 하나에만 쓰기를, 변경 경로 파일 폴더에 읽기를, unittest 실행만을 허락하고 프로젝트 파일 편집 권한을 주지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
