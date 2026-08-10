---
id: W-00000255
title: 들이는 명령이 바뀐 규칙 파일을 알린다
kind: development
venue: codex
milestone:
autonomous: true
acceptance:
  - "grep -q operations stage/scripts/tests/test_land_run.py && python3 -m unittest discover -s stage/scripts/tests -p test_land_run.py -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000255
promotion: not_applicable
review: not_required
scope: stage/scripts/land_run.py, stage/scripts/tests/test_land_run.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000255 들이는 명령이 바뀐 규칙 파일을 알린다

## Purpose

세션이 읽은 뒤에 규칙 파일이 바뀌면 아무도 안 알려 줘서 낡은 규칙으로 계속 도므로, DE-00000069 가 정한 대로 그 변경을 들여오는 명령이 바뀐 규칙 파일 이름을 낸다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 규칙 파일을 건드린 병합을 들이면 그 파일 이름이 명령 출력에 나온다
- 규칙 파일을 안 건드린 병합에서는 그 알림이 안 나온다

## Next action

**`DE-00000069.md` 를 먼저 읽는다.** 왜 훅이 이 자리를 못 잡는지가 거기 있다 — 규칙 파일을
바꾸는 것이 서브프로세스라 훅이 보는 것은 셸 명령 한 줄뿐이다.

`land_run.py` 는 들여오는 변경 목록을 **이미 계산한다**(`changed_paths_against`, 200줄, 부르는
자리 354줄). 새로 계산하지 말고 그 값을 쓴다. 알림이 붙을 자리는 성공 메시지를 내는 415줄
옆이다.

**저장된 인수 명령이 `grep -q operations` 로 시험 파일을 먼저 본다** — 지금
`test_land_run.py` 에 `operations` 가 0번 나오므로, 시험을 안 쓰면 이 검사가 막는다. 기존
18개는 고치기 전에도 통과하기 때문이다(R-00000244).

## Related truth

- DE-00000069 — 이 카드의 명세. 둘째 자리(읽은 뒤 바뀐다)를 왜 이 명령이 잡는지의 근거.
- O-00000042 — 이 고장의 관측. 2026-08-09 사례가 이 카드가 고치는 모양이다.
- W-00000254 — 첫 사례(모른다)를 잡는 형제 카드. 범위가 안 겹친다.
- `stage/operations/hooks.md` — 훅이 서브프로세스의 쓰기를 못 본다는 사실의 소유자.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
