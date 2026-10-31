---
id: W-00000303
title: 여러 판의 실행 보고를 판마다 커밋을 모아 옮긴다
kind: fix
venue: claude
environment: cloud
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
scope: stage/scripts/import_executor_report.py, stage/scripts/tests/test_import_executor_report.py, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000303 여러 판의 실행 보고를 판마다 커밋을 모아 옮긴다

## Purpose

여러 판에 걸친 카드의 실행 보고가 계약대로 모든 판의 변경 경로를 적어도 옮기기 도구가 거절하지 않게 한다.

## Actions

- 지금 동작: 실행 계약은 `Changed paths (JSON)` 에 모든 판의 변경 경로를 적으라고 한다. 그런데
  `import_executor_report.py` 는 보고의 경로를 커밋 하나가 바꾼 경로와만 대조한다. 그래서 여러 판에 걸친 클라우드
  카드는 계약대로 쓰면 도구가 거절하고, 도구에 맞추면 계약을 어긴다. W-00000300 의 두 번째 닫기 리뷰가 그 어긴
  보고(2판 경로만 적음)를 반려했다.
- `--commit` 을 여러 번 받는다. 보고는 마지막 커밋에서 읽고, 대조할 경로는 받은 커밋들이 바꾼 경로의 합이다.
  사이에 다른 카드의 커밋이 끼어 있어도 그 카드의 커밋만 골라 줄 수 있게 범위가 아니라 커밋 목록으로 받는다.
- `stage/operations/cloud-execution.md` 의 옮기기 절에 여러 판일 때의 쓰임을 적는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 옮기기 도구가 커밋 여러 개를 받으면 마지막 커밋의 보고를 그 커밋들이 바꾼 경로 전체와 대조해 옮긴다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
