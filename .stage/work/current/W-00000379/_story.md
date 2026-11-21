---
id: W-00000379
title: Stage CI 의 테스트를 여러 잡으로 나눠 PR 결과가 빨리 나온다
kind: ops
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .github/workflows/stage.yml,.github/scripts
promotes:
decision_refs:
---

# W-00000379 Stage CI 의 테스트를 여러 잡으로 나눠 PR 결과가 빨리 나온다

## Purpose

Stage PR 의 CI 결과가 Windows 테스트 한 잡을 기다리느라 10분 걸리던 것이 줄어든다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- PR 에서 stage 워크플로가 시작해서 끝날 때까지 걸린 시간이 바꾸기 전(약 10분)보다 줄었다
- 나눈 잡들이 실행한 테스트 수의 합이 나누기 전 한 잡이 실행한 수와 같다

## Next action


## Related truth


## Progress


## Verification
