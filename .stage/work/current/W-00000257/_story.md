---
id: W-00000257
title: 세션 시작이 venue 별로 어떻게 돌리는지까지 말하게 한다
kind: development
venue: codex
milestone:
autonomous: true
acceptance:
  - "test -f stage/hooks/tests/test_session_context_venue.py && python3 -m unittest discover -s stage/hooks/tests -p test_session_context_venue.py -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000257
promotion: not_applicable
review: passed
scope: stage/hooks/stage_context.py, stage/hooks/tests/test_session_context_venue.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000257 세션 시작이 venue 별로 어떻게 돌리는지까지 말하게 한다

## Purpose

세션 시작이 어느 kind 가 어느 venue 인지까지만 말하고 그 venue 를 어떻게 돌리는지는 안 말해서 감독이 claude 몫 카드 다섯 중 넷을 팀원 없이 직접 해 버렸으므로, 라우팅 문장이 실행 방법까지 말하게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 세션 시작 문장이 claude 몫은 팀원을 띄워 주고 codex 몫은 드라이버에 넘긴다는 것을 말한다
- 그 문장이 절차 문서를 이름으로 가리켜 어디를 열지가 보인다

## Actions

없음 — 세션 시작이 내는 문장 하나를 늘리고 그 시험을 붙이는 한 덩어리다.

## User value

세션이 열리자마자 "이 카드는 팀원에게 준다"는 것을 안다. 지금은 사용자가 매번 말해 줘야 한다.

## Scope

### Included

**감독이 잰 것.** 세션 시작 훅을 직접 돌려 확인했다.

| 지금 말하는 것 | 지금 안 말하는 것 |
|---|---|
| `design -> claude`, `fix -> codex` 같은 라우팅 | **claude 몫 카드는 팀원을 띄워 준다는 것** |
| `.stage/operations/claude-venue.md` 라는 파일이 있다는 것 | 그 파일을 열라는 것 |

라우팅 문장은 "카드를 등록할 때 venue 를 이렇게 정하라"까지만 말한다. 정해진 뒤 어떻게
돌리는지는 문장에 없다.

- **라우팅 문장에 실행 방법을 붙인다.** claude 몫은 팀원을 띄워 주고, codex 몫은 드라이버에
  넘긴다. 그 문장이 `.stage/operations/claude-venue.md` 를 이름으로 가리킨다.
- 시험을 `stage/hooks/tests/test_session_context_venue.py` 에 새로 만든다.

### Excluded

- **못 지키는 것을 막지 않는다.** 훅은 도구 호출을 보는데 "팀원을 안 띄우고 감독이 직접 했다"는
  것은 도구 호출이 아니다. O-00000021 이 같은 자리를 적었다. 이 카드가 약속하는 것은 세션이
  그 문장을 받는다는 것까지다.
- `.stage/operations/claude-venue.md` 본문을 안 싣는다. DE-00000069 가 본문을 안 싣기로 정했다 —
  세션 안에 규칙의 복사본이 생기면 파일이 바뀌어도 안 바뀐다.
- venue 라우팅 정책 자체(`.stage/settings.json` 의 `venue_routing`)는 안 바꾼다.

## Risks

- **말해 줘도 안 지킬 수 있다.** 이 세션이 그 증거다 — 라우팅은 실려 있었고 절차 파일도 있었는데
  감독이 다섯 중 넷을 직접 했다. 문장이 실행 방법까지 말하면 나아지는지는 다음 세션들에서
  세야 안다.
- 문장이 길어지면 라우팅 목록 자체가 안 읽힌다. 한 줄 안에서 끝낸다.

## Next action

**`stage/hooks/stage_context.py:261-271` 을 먼저 읽는다.** 라우팅 문장을 만드는 자리다. 지금
`kind -> venue` 목록과 "등록할 때 이 정책에서 venue 를 정하라"까지 낸다.

거기에 붙일 것은 실행 방법 한 줄이다 — claude 몫은 팀원을 띄워 주고 codex 몫은 드라이버에
넘긴다, 절차는 `.stage/operations/claude-venue.md`.

**저장된 인수 명령 첫째가 `test -f` 로 시험 파일의 실재를 먼저 본다** — 파일을 안 만들면
`unittest` 가 `Ran 0 tests ... OK` 에 exit 0 을 내기 때문이다(R-00000244).

## Related truth

- `.stage/operations/claude-venue.md` — claude 몫 카드를 팀원으로 돌리는 절차의 소유자.
  첫 줄이 "감독 세션이 드라이버에 넘기지 않고 팀원 에이전트를 띄워 카드를 준다"이다.
- O-00000042 — 규칙이 있는데 세션이 안 읽는 관측. 이 카드는 그 계열인데 다르다 — 파일 이름은
  이제 실리는데 **무엇을 하라는 문장이 없다.**
- O-00000021 — 도구를 안 쓰는 행동은 훅이 못 본다. 이 카드가 막지 않고 말해 주기만 하는 근거.
- DE-00000069 — 이름만 싣고 본문은 안 싣기로 한 결정. 이 카드가 그 선을 지킨다.


## Related truth


## Progress


## Verification


### Executed at close — 2026-08-10

```
$ test -f stage/hooks/tests/test_session_context_venue.py && python3 -m unittest discover -s stage/hooks/tests -p test_session_context_venue.py -q
[exit 0]
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 374 tests in 1.464s

OK
```

### Independent review at close — 2026-08-10

```
Review report: .stage/.runtime/driver/logs/W-00000257.md
```

## Retrospective


## Promotion decision
