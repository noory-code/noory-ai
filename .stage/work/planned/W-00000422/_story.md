---
id: W-00000422
title: 이 저장소의 클라우드 브리핑에 proposed: promote 규칙 후보가 한 줄도 실리지 않는다
kind: fix
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/hooks/stage_context.py,stage/hooks/stage_memory_index.py,stage/scripts/subsession_brief.py,stage/hooks/tests,stage/scripts/tests,stage/CHANGELOG.md
---

# W-00000422 이 저장소의 클라우드 브리핑에 proposed: promote 규칙 후보가 한 줄도 실리지 않는다

## Purpose

클라우드 세션의 브리핑이 proposed: promote 규칙 후보를 수만이 아니라 줄로 보여 준다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- python3 stage/scripts/subsession_brief.py --project-root . <시작된 카드> --po-session session_x --role pm --branch b 의 끝부분이 proposed: promote 줄을 한 줄 이상 싣는다

## Next action
