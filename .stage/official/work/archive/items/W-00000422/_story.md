---
id: W-00000422
title: 이 저장소의 클라우드 브리핑에 proposed: promote 규칙 후보가 한 줄도 실리지 않는다
kind: fix
venue:
milestone:
status: archived
terminal_disposition: rejected
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

없다. 시작하지 않고 거절한다.

2026-11-26 PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 규칙 후보 목록에 DE-00000104 를 적용한 뒤(W-00000423, W-00000424) 다시 쟀다.
목록에 `proposed: promote` 줄이 0건이다. 여섯 줄은 규칙이 됐고 한 줄은 사용자가 거절해 `hold` 가 됐다. 이 카드의 성공 기준은
"브리핑이 `proposed: promote` 줄을 한 줄 이상 싣는다"인데 실을 줄이 없어서 등록할 때의 고장이 재현되지 않는다.
`grep -n "proposed: promote" .stage/state/rule-candidates.md` 는 머리말의 한 줄만 낸다. 이 카드를 등록할 때 "재현되지 않으면
시작하지 않고 닫는다"고 적어 두었다.

같은 때 본 다른 것: 스토리가 여섯인 에픽 W-00000424 의 PM 브리핑은 11,264자였고 색인이 2,703자에서 잘려 결정 제목이 한 줄도
실리지 않는다(`python3 stage/scripts/subsession_brief.py --project-root . W-00000424 --po-session s --role pm --branch b | tail -1`
가 `…cut at 2703 characters` 를 낸다). 이것은 DE-00000100 이 정한 줄이는 순서대로의 동작이고 이 카드의 성공 기준이 아니다.
상한 10,000자는 잰 값이 아니라고 DE-00000100 이 적어 두었다. 따로 카드로 만들지는 않았다.
