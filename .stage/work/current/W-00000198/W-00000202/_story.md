---
id: W-00000202
title: 다 쓴 허가증이 카드와 함께 자리를 옮긴다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_archive_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: not_applicable
review: not_required
scope: stage/skills/stage-archive/archive_work.py, stage/scripts/refresh_decision_index.py, stage/scripts/audit_stage.py, stage/scripts/tests/test_archive_work.py, stage/scripts/tests/test_refresh_decision_index.py, stage/scripts/tests/test_audit_stage.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000202 다 쓴 허가증이 카드와 함께 자리를 옮긴다

## Purpose

허가증의 효력은 카드가 끝나는 순간 사라지는데 아무도 옮기지 않아 대기 서랍에 쌓이므로, 카드를 보관하는 명령이 그 카드가 쓴 허가증을 같이 보관함으로 옮기게 한다

## Actions

없음 — 보관 명령에 한 걸음을 더하는 일이다.

## User value

허가증이 다 쓰였다는 것을 사람이 기억하지 않는다. 카드를 보관하면 그때 같이 빠지므로 대기
서랍에는 아직 안 쓴 허가증만 남는다.

## Scope

### Included

- 카드를 보관할 때 그 카드를 지목한 일회성 허가증을 함께 보관함으로 옮긴다.
- 결정 인덱스가 그 이동을 반영한다. 대기 표에 살아 있는 것만 남으면 효력 칸의 뜻이 달라지므로,
  그 칸을 어디에 둘지 같이 정한다.
- 이미 보관된 카드에 딸린 허가증 여섯 장을 옮기는 일회성 경로. 그 카드들은 이미 끝나서
  보관 명령이 다시 안 돈다.
- **보관 인덱스를 감사가 본다.** 지금 결정·제안·상태 보관 인덱스는 줄을 지워도 아무도 안 잡는다.
  살아 있는 서랍의 인덱스에는 그 검사가 있는데 보관함에는 없다(W-00000201 판정이 남긴 것).
  세 보관함을 한 번에 놓는다.

### Excluded

- 제안·관측·질문은 안 건드린다. 그쪽은 사람 판정이 필요해 W-00000201 의 명령이 맡는다.
- 구속하는 결정의 승격 규칙은 안 바꾼다. 바뀌는 것은 안 올린 허가증이 어디에 사는가 하나다.

## Risks

- **이미 보관된 카드의 허가증은 보관 명령이 다시 안 돈다.** 일회성 경로가 없으면 지금 남은
  여섯 장은 영영 대기 서랍에 있다.
- 허가증이 옮겨지면 그것을 가리키는 카드의 인용이 보관 경로로 해석돼야 한다. 그 자리는
  W-00000200 이 만든다 — 순서가 어긋나면 링크가 끊긴 채로 남는다.
- 카드 등록이 허가증을 확인할 때 보관된 허가증을 못 찾으면, 이미 쓴 것을 다시 쓰려는 시도가
  "없는 결정"으로 잘못 보고된다. "이미 다 썼다"로 읽혀야 한다.

## Success criteria

- 카드를 보관하면 그 카드의 허가증이 같은 걸음에 보관함으로 간다.
- 대기 서랍에 아직 안 쓴 허가증만 남는다.
- 이미 보관된 카드의 허가증 여섯 장이 명령으로 옮겨진다.
- 다 쓴 허가증을 다시 쓰려 하면 등록이 "이미 소진됐다"고 말한다.
- 보관 인덱스에서 줄을 지우면 감사가 잡는다. 세 보관함 다.

## Next action

W-00000200 이 보관 자리를 등록한 뒤에 시작한다. 자리가 없으면 옮길 곳이 없다.

## Related truth

- DE-00000006·8·25·26·41·45 — 지금 대기 서랍에 남은 여섯 장. 지목한 카드가 전부 보관됐다.
- `refresh_decision_index.py` — 이미 카드 상태를 읽어 효력을 계산하고 있다.

## Progress


## Verification


## Retrospective


## Promotion decision
