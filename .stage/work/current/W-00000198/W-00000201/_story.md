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
scope: stage/scripts/close_record.py, stage/scripts/tests/test_close_record.py, stage/skills/, stage/CHANGELOG.md
promotes:
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

- 제안·관측·질문을 닫는 명령. 닫는 근거를 필수로 받아 본문 상태 절에 적고, 파일을 보관함으로
  옮기고, 인덱스에서 그 줄을 내린다.
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

- **상태 인덱스에는 갱신 명령이 없다.** 결정 인덱스만 스스로 만들어진다. 이 명령이 인덱스를
  직접 고치지 않으면 지난 세션의 실패가 그대로 반복된다.
- 상태 인덱스는 안내 문서 예외 목록에 올라 있어 갱신 규칙이 다른 문서와 다르다.
- 되돌리기를 안 만들면 사람이 손으로 옮기게 되고, 그 순간 이 카드가 막으려던 자리가 다시 열린다.

## Success criteria

- 관측·질문·제안을 닫으면 본문 근거·파일 자리·인덱스가 한 번에 맞는다.
- 근거 없이 닫으려 하면 명령이 거부한다.
- 닫은 기록을 되돌리면 인덱스 줄이 되살아난다.
- 옮기다 실패하면 아무것도 안 옮겨진 상태로 남고, 사람이 무엇이 왜 막혔는지 읽는다.
- 닫은 뒤 감사가 오류 없이 통과한다.

## Next action

상태 인덱스를 누가 소유하는지부터 확인한다 — 명령이 고칠지, 결정 인덱스처럼 스스로
만들어지게 할지가 갈린다.

## Related truth

- O-00000029 — 내가 기억해서 적어야 하는 상태는 예외 없이 낡는다. 한 세션에서 네 서랍 열아홉 장.
- `refresh_decision_index.py` — 서랍에서 표를 만들어 내는 이미 있는 본보기.

## Progress


## Verification


## Retrospective


## Promotion decision
