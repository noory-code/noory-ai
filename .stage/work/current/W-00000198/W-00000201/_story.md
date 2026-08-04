---
id: W-00000201
title: 기록을 닫고 되돌리는 명령을 만든다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_record.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/close_record.py, stage/scripts/tests/test_close_record.py, stage/hooks/stage_paths.py, stage/hooks/stage_runtime.py, stage/hooks/tests/test_archive_gate.py, stage/skills/, stage/CHANGELOG.md
promotes: .stage/official/decisions/records/DE-00000057.md
decision_refs:
---

# W-00000201 기록을 닫고 되돌리는 명령을 만든다

## Purpose

제안과 관측과 질문을 닫는 일이 손 편집이라 인덱스가 따로 낡고 절이 통째로 빠지기도 하므로, 닫힘과 되돌리기를 한 명령이 맡아 본문과 자리와 인덱스를 함께 옮기게 한다

## Actions

없음 — 닫기와 되돌리기는 같은 이동의 양방향이라 따로 만들면 두 번 다 짜게 된다.

## User value

관측 하나를 닫는 데 파일 본문, 파일 자리, 인덱스 세 곳을 기억해서 고치지 않는다. 명령 한 줄로
셋이 같이 움직이고, 잘못 닫았으면 되돌린다.

## Scope

### Included

- **보관함에 쓸 수 있게 게이트를 넓힌다.** `.stage/official/` 아래 쓰기는 통행증이 있어야 하는데,
  보관용 통행증이 허락하는 자리가 `official/work/archive/` 하나뿐이다. 지금 상태로는 이 명령이
  새 보관함 셋에 아예 못 쓴다. 자리를 아는 통행증으로 넓히거나, 이 명령이 스스로 내고 쓰는
  통행증을 만든다 — 카드 보관 명령이 이미 그렇게 한다.
- 제안·관측·질문을 닫는 명령. 닫는 근거를 필수로 받아 본문 상태 절에 적고, 파일을 보관함으로
  옮기고, 인덱스에서 그 줄을 내린다.
- DE-00000057 의 "닿는 자리" 표에 그 게이트를 더한다. 결정을 쓸 때 빠뜨린 자리다.
- 제안은 실림·접힘·절반 중 하나를 함께 받는다.
- 되돌리기. 닫은 기록을 살아 있는 서랍으로 되돌리고 인덱스에 줄을 되살린다.
- 중간에 실패하면 아무것도 안 옮긴 상태로 남긴다. 파일만 가고 인덱스가 옛 줄을 들고 있는 꼴이
  제일 나쁘다.

### Excluded

- 다 쓴 허가증은 이 명령이 안 옮긴다. 그쪽은 계산되니 카드 보관이 맡는다(W-00000202).
- 이 저장소의 기존 기록은 안 건드린다. 비우는 것은 W-00000203 이다.
- 기록을 새로 만드는 명령은 안 만든다. 지금 손으로 만들다 절이 빠지는 문제는 감사가
  잡는 쪽으로 간다(W-00000200).

## Risks

- **게이트를 안 넓히면 이 카드가 만든 명령이 아무것도 못 옮긴다.** 그러면 W-00000203 도 못
  돈다. 이 위험이 나머지보다 앞선다.
- 게이트를 넓히는 것은 공식 영역을 지키는 잠금을 건드리는 일이다. 넓힌 만큼만 열려야 하고,
  다른 자리로 새면 안 된다.
- **상태 인덱스에는 갱신 명령이 없다.** 결정 인덱스만 스스로 만들어진다. 이 명령이 인덱스를
  직접 고치지 않으면 지난 세션의 실패가 그대로 반복된다.
- 상태 인덱스는 안내 문서 예외 목록에 올라 있어 갱신 규칙이 다른 문서와 다르다.
- 되돌리기를 안 만들면 사람이 손으로 옮기게 되고, 그 순간 이 카드가 막으려던 자리가 다시 열린다.

## Success criteria

- 사람이 통행증을 따로 내지 않고 명령 한 줄로 기록을 보관함에 넣는다.
- 넓힌 게이트가 보관함 셋 밖의 공식 자리는 여전히 막는다.
- 관측·질문·제안을 닫으면 본문 근거·파일 자리·인덱스가 한 번에 맞는다.
- 근거 없이 닫으려 하면 명령이 거부한다.
- 닫은 기록을 되돌리면 인덱스 줄이 되살아난다.
- 옮기다 실패하면 아무것도 안 옮겨진 상태로 남고, 사람이 무엇이 왜 막혔는지 읽는다.
- 닫은 뒤 감사가 오류 없이 통과한다.

## Next action

공식 영역 쓰기 게이트부터 읽는다(`stage/hooks/stage_paths.py` 의 보관 경로 판정과
`stage/hooks/stage_runtime.py` 의 통행증 검사). 여기가 안 열리면 나머지를 만들어도 못 쓴다.

## Related truth

- O-00000029 — 내가 기억해서 적어야 하는 상태는 예외 없이 낡는다. 한 세션에서 네 서랍 열아홉 장.
- `refresh_decision_index.py` — 서랍에서 표를 만들어 내는 이미 있는 본보기.

## Progress


## Verification


## Retrospective


## Promotion decision
