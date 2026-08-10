---
id: W-00000254
title: 세션 시작이 프로젝트 규칙 파일 이름을 싣게 한다
kind: development
venue: codex
milestone:
autonomous: true
acceptance:
  - "test -f stage/hooks/tests/test_session_context_operations.py && python3 -m unittest discover -s stage/hooks/tests -p test_session_context_operations.py -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/hooks/stage_context.py, stage/hooks/tests/test_session_context_operations.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000254 세션 시작이 프로젝트 규칙 파일 이름을 싣게 한다

## Purpose

프로젝트가 세운 규칙 파일이 있다는 것조차 세션이 몰라서 적어 둔 규칙이 안 지켜지므로, DE-00000069 가 정한 대로 세션 시작이 그 파일 이름을 실어 준다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 새 세션에 .stage/operations/ 의 파일 이름이 하나도 빠짐없이 들어온다
- 본문은 안 실리고, 파일이 늘어도 이름만 는다는 것이 시험으로 잡힌다

## Next action

**`DE-00000069.md` 를 먼저 읽는다.** 왜 이름만 싣고 본문은 안 싣는지가 거기 있다 — 크기 때문이
아니라, 본문을 실으면 세션 안에 규칙의 복사본이 생기고 그 복사본은 파일이 바뀌어도 안 바뀌기
때문이다.

붙일 자리는 세션 시작이 호스트 지시(`CLAUDE.md`, `AGENTS.md` 등)를 파일 이름 목록으로 싣는
그 자리다. `stage/hooks/stage_context.py` 안에 있다.

**감독이 잰 것** — 지금 세션 시작은 6,125자이고, `.stage/operations/` 파일 넷 중 이름이라도
들어오는 것이 **0개**다. "operations" 라는 낱말이 두 번 나오는데 둘 다 구역 이름을 나열하는
자리다. 이 값은 다시 세라.

**저장된 인수 명령 첫째가 `test -f` 로 시험 파일의 실재를 먼저 본다** — 파일을 안 만들면
`unittest` 가 `Ran 0 tests ... OK` 에 exit 0 을 내기 때문이다(R-00000244).

## Related truth

- DE-00000069 — 이 카드의 명세. 첫 자리(모른다)를 세션 시작이 잡는 근거.
- O-00000042 — 이 고장의 관측. 사례 둘이 있고 이 카드는 **첫 사례만** 고친다.
- W-00000255 — 둘째 사례(읽은 뒤 바뀐다)를 잡는 형제 카드. 범위가 안 겹친다.


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
