---
id: W-00000241
title: 드라이버를 책임별로 나눈다
kind: development
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
scope: stage/scripts/drive.py, stage/scripts/drive_parallel.py, stage/scripts/tests/, stage/CHANGELOG.md, .stage/decisions/
promotes:
decision_refs: DE-00000067
---

# W-00000241 드라이버를 책임별로 나눈다

## Purpose

드라이버가 한 파일에 3,952줄로 들어 있어 서로 다른 카드가 같은 파일을 고칠 때마다 남의 코드를 피해 다녀야 하므로, 책임별로 나눠 한 카드가 한 자리만 만지게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 드라이버의 어느 파일도 1,000줄을 넘지 않고 965개 테스트가 그대로 통과한다
- 한 파일을 열었을 때 그 파일이 무슨 책임을 지는지 파일 이름만으로 말할 수 있다

## Next action

## Related truth

## Progress

## Verification

## Retrospective

## Promotion decision
