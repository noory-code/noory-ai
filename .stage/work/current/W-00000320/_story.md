---
id: W-00000320
title: Ubuntu 러너에서 Python 3.9 시험이 계속 돌게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .github/workflows/stage.yml, .github/workflows/avatar.yml, .github/workflows/plainly.yml, stage/scripts/tests/test_ci_workflows.py
promotes:
decision_refs:
---

# W-00000320 Ubuntu 러너에서 Python 3.9 시험이 계속 돌게 한다

## Purpose

Python 3.9 를 받치겠다는 Stage·Avatar·Plainly 의 약속을 Ubuntu 에서도 CI 가 계속 확인하게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 세 워크플로가 Ubuntu 의 Python 3.9 조합만 ubuntu-24.04 에서 돌리고, 나머지 조합(macOS·Windows 의 3.9, 모든 OS 의 3.12)은 그대로라는 것을 시험이 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
