---
id: W-00000290
title: 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구를 둔다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_import_executor_report.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/import_executor_report.py, stage/scripts/tests/test_import_executor_report.py, stage/skills/stage-retrospective/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000080
---

# W-00000290 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구를 둔다

## Purpose

작업 로그가 없는 자리에서 커밋 본문에 쓴 실행 보고를 손으로 옮기다 칸이 잘리거나 틀리는 일을 막는다.

## Actions

- 지금 동작: DE-00000075 의 실행 계약은 작업 로그가 없는 클라우드 세션에게 `### Executor report` 를 커밋
  메시지 본문에 쓰게 하고, 로컬이 그 보고를 작업 로그로 옮긴다. 옮기는 도구가 없어 손으로 한다. 커밋
  본문은 보통 72열에서 줄을 바꾸므로 "한 줄" 칸이 여러 줄로 나뉜다. 그대로 옮기면 닫기가 카드의
  Progress 에 첫 줄만 옮긴다(R-00000287).
- `stage/scripts/import_executor_report.py` 가 커밋 하나의 본문에서 실행 보고를 찾아, 나뉜 칸을 한 줄로
  잇고, 계약 순서로 다시 쓴 뒤, `close_work.executor_report_error()` 로 검증하고 작업 로그에 덧붙인다.
  주장한 변경 경로는 그 커밋이 바꾼 경로와 대조한다. 검증에 실패하면 로그를 바꾸지 않는다.
- `stage/skills/stage-retrospective/SKILL.md` 의 닫기 절에 이 도구를 언제 쓰는지 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

클라우드 세션의 결과를 로컬에서 닫을 때 실행 보고를 손으로 옮기지 않아도 되고, 칸이 잘린 채 카드에
남는 일이 없다.

## Scope

### Included


### Excluded

- DE-00000075 의 실행 계약 문장 자체를 바꾸는 일.
- 리뷰 판정이나 리뷰 보고를 커밋에서 옮기는 일.

## Risks


## Success criteria

- 커밋 본문의 실행 보고를 작업 로그로 옮기는 도구가 여러 줄로 나뉜 칸을 한 줄로 이어 붙여 옮긴다는 것을 테스트가 확인한다
- 옮긴 보고가 실행 보고 계약 검증을 통과하지 못하면 도구가 작업 로그를 바꾸지 않고 거절한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
