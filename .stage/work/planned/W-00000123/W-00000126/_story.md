---
id: W-00000126
title: 도는 작업과 겹치는 카드는 시작을 거절한다
kind: development
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/skills/stage-drive/, stage/CHANGELOG.md
---

# W-00000126 도는 작업과 겹치는 카드는 시작을 거절한다

## Purpose

DE-00000040 §3. 카드가 선언한 scope 가 이미 도는 작업의 scope 와 겹치면 시작하지 않는다. 겹침 판단을 사람의 기억에 맡기면 언젠가 틀리고, 그때 나는 실패는 대조 불일치라는 엉뚱한 모양으로 온다. 카드가 이미 scope 를 선언하므로 새 개념을 만들지 않고 그것을 쓴다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action
