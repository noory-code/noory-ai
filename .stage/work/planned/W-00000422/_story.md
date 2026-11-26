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

2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 W-00000421 의 후속 후보에서 등록했다(DE-00000102: 지금 깨져 있고 재현 명령이 있다).
증거: W-00000421 을 닫기 전에
`python3 stage/scripts/subsession_brief.py --project-root . W-00000421 --po-session session_x --role pm --branch b | tail -4` 가
`- …14 candidates not shown — read .stage/state/rule-candidates.md` 와
`- 25 more candidates are proposed: hold and are not listed — …` 를 냈다. 브리핑과 색인을 합쳐 10,000자를 넘으면 후보가 먼저
빠진다(DE-00000100 의 줄이는 순서).

## Scope

### Included


### Excluded


## Risks


## Success criteria

- python3 stage/scripts/subsession_brief.py --project-root . <시작된 카드> --po-session session_x --role pm --branch b 의 끝부분이 proposed: promote 줄을 한 줄 이상 싣는다

## Next action

지금 목록에 새 문턱을 적용한 뒤에 다시 잰다. promote 줄이 줄어 재현되지 않으면 시작하지 않고 닫는다.

Order: 규칙 후보 목록에 DE-00000104 를 적용하는 일 뒤, set by the PO session on the user's delegation on 2026-11-26
