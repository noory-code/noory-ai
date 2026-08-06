---
id: W-00000230
title: 무인 실행 결과를 본 가지로 들인다
kind: ops
venue: codex
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
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/test_drive_parallel.py, stage/CHANGELOG.md, .stage/work/
promotes:
decision_refs:
---

# W-00000230 무인 실행 결과를 본 가지로 들인다

## Purpose

무인 실행은 카드를 스스로 닫고 격리된 가지에만 쓰므로 결과가 본 가지에 들어가려면 사람이 병합해야 하는데, 그 시점에는 열린 작업이 없어 커밋 게이트가 막으므로, 이 항목이 그 병합을 담아 결과를 들이고 병렬 실행이 만든 회고 번호 충돌을 푼다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- W-00000228 의 무인 실행 결과가 본 가지에 들어가고 그 시험이 본 가지에서 통과한다
- 두 무인 실행이 같은 번호로 만든 회고가 서로 다른 번호를 갖는다
- 감사가 오류 없이 통과한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
