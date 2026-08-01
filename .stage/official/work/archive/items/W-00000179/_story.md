---
id: W-00000179
title: 대기 결정 목록이 서랍과 같은 말을 하게 한다
kind: development
venue: codex
milestone: M-00000001
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000179
promotion: not_applicable
review: not_required
scope: stage/scripts/, stage/hooks/, stage/skills/, stage/docs/, stage/operations/, stage/templates/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000179 대기 결정 목록이 서랍과 같은 말을 하게 한다

## Purpose

통행증이 아직 살아 있는지 목록만 봐서는 알 수 없고 그 목록마저 서랍과 어긋나 있다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

서랍을 안 열어도 무엇이 아직 나를 구속하는지 목록에서 보인다. 그리고 목록이 다시 낡지 않는다.

## Scope

### Included

- 대기 결정 목록을 **서랍에서 만들어 낸다.** 손으로 쓰는 자리를 없앤다.
- 줄마다 어느 카드 것인지, 그 카드가 끝났는지를 싣는다. 카드 하나만 허가하고 끝나는 결정은
  그 카드가 끝나면 효력이 없으므로, 그 한 칸이 살았는지 죽었는지를 답한다.
- 감사가 그 목록과 서랍이 어긋나는지 본다.
- 이 저장소의 목록을 다시 만든다.

### Excluded

- **공식 결정 목록**(`official/decisions/index.md`, 46줄). 어긋난 적이 없다 — 반복이 보이기
  전에 같이 손대지 않는다.
- 결정에 새 상태값을 주는 일. "이 카드가 끝났는가"는 카드가 이미 소유한다. 통행증에 도장을 또
  찍으면 같은 사실이 두 곳에 생겨 언젠가 한쪽만 바뀐다.
- ~~결정을 옮기거나 만드는 명령이 목록을 쓰게 하는 일. 만들어 내는 쪽이면 그 자리가 필요 없다.~~
  **이 제외가 틀렸다(2026-08-01, 1바퀴 판정).** 손으로 쓰는 자리는 없어져도 만들어 내는 명령을
  누군가 돌려야 한다. 아래 "다음 행동"으로 옮긴다.

## Risks

- **만들어 낸 목록이 사람이 적어 둔 것을 지울 수 있다.** 지금 목록에 손으로 쓴 설명이 있는지
  먼저 보고, 있으면 그 자리를 남긴다. 같은 사고가 이 프로젝트에 있었다(O-00000012).
- **감사가 새 오류를 내면 다른 프로젝트가 걸릴 수 있다.** 목록이 없거나 모양이 다른 프로젝트가
  어떻게 되는지 보고 정한다.

## Success criteria

- 목록을 만들어 내는 명령이 있고, 손으로 쓰는 자리가 없다.
- 줄마다 어느 카드 것인지와 그 카드가 끝났는지가 있어, 서랍을 안 열어도 살았는지 알 수 있다.
- 목록과 서랍이 어긋나면 감사가 잡는다.
- 이 저장소 목록이 실제 서랍과 같다 — 지금은 낡은 다섯 줄이 있고 실제 여섯 줄이 빠져 있다.
- 사람이 겪는 결과: 대기 서랍을 열었을 때 아직 살아 있는 것이 무엇인지 한눈에 보인다.

## Next action

**카드를 닫을 때 목록을 다시 만든 뒤 감사를 돌린다** (사람이 정함, 2026-08-01).

2바퀴가 결정 만드는 세 자리에 갱신을 붙였는데, 판정이 같은 구멍이 자리만 옮겼다고 짚었다 —
목록에 "그 카드가 끝났는지" 칸이 있으니 **카드를 닫거나 보관할 때마다 그 값이 바뀐다.** 닫기는
매번 있는 일이라 막힌 카드 올리기보다 훨씬 자주 터진다.

세어 보니 목록에 영향을 주는 자리가 여덟쯤이고 **그중 하나는 명령이 아예 없다** — 결정을
공식으로 옮기는 것은 손으로 하는 일이다(2026-08-01 에 일곱을 그렇게 옮겼다). 그래서 "만드는
자리마다 붙이기"로는 끝까지 못 간다.

**닫는 자리 하나에 붙인다.** 카드가 끝나는 자리는 하나이고, 어느 길로 어긋났든 다음 닫기에서
맞춰진다. 손으로 옮긴 것도 저절로 따라온다.

곁가지 — `stage/docs/SCHEMA_V5.md:90` 의 이전 단계 목록에 대기 결정 목록 갱신 줄이 빠졌다.
이 카드 범위 안이다.

## Related truth

- **DE-00000030** — 카드 하나만 허가하고 끝나는 결정은 대기에 남고, 나머지는 공식으로 간다.
  그 결정은 서랍을 갈랐고, 이 카드는 **서랍 안에서 살았는지 죽었는지**를 보이게 한다.


## Progress


## Verification

### 판정 처분 — 2026-08-01

세 바퀴 돌았고 매 바퀴 판정이 구멍이 어디로 옮겨 갔는지 짚었다. 셋 다 받았다.

- **받음(1바퀴) — 결정 만드는 세 자리가 목록을 안 만든다.** 2바퀴에 붙였다.
- **받음(2바퀴) — 닫기·보관이 목록을 안 만든다.** 닫기가 훨씬 자주 있는 일이다. 사람이
  닫는 자리 하나로 정했고 3바퀴에 실었다.
- **받음(2·3바퀴) — 계약 문서 두 줄.** 하나는 거짓이 됐고 하나는 빠졌다. 둘 다 고쳤다.

**미룸 — 회고 스킬 문서가 닫기 실패 조건을 안 적는다.** 닫기가 목록을 못 맞추면 멈추는데
그 문서에 없다. 처음 만나면 이유를 모른다. 그 문서는 거부 조건을 다 세는 목록이 아니라
계약 위반은 아니다. 다음 카드로 넘긴다.

**판정이 기록만 한 것** — 보관과 다음 닫기 사이에 감사를 따로 돌리면 아직 빨갈 수 있다.
사람이 고른 경계 안이다. 사람이 읽는 답(효력이 살았나)은 그 사이에 안 바뀐다 — 끝난 카드와
보관된 카드 둘 다 최종 상태라 통행증은 어느 쪽이든 `expired` 다.

- 2026-08-01: `python3 -m unittest discover -s stage/scripts/tests -q` — 541개 통과.
- 2026-08-01: `python3 -m unittest discover -s stage/hooks/tests -q` — 356개 통과.
- 2026-08-01: `python3 stage/scripts/audit_stage.py` — 오류와 경고 없음.

### Executed at close — 2026-08-01

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.195s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (203 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785577552
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785577552. Human review + merge required; the base branch was not modified.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 541 tests in 77.615s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
