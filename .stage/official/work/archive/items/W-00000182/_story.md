---
id: W-00000182
title: 드라이버가 성패를 무엇으로 재는지 바로잡는다
kind: development
venue: codex
milestone: M-00000001
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000184
promotion: not_applicable
review: not_required
scope: stage/scripts/, stage/operations/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000182 드라이버가 성패를 무엇으로 재는지 바로잡는다

## Purpose

드라이버가 옳게 한 일을 실패로 세고, 그때마다 사람이 손으로 우회한다.

## Actions

- W-00000183 — 실행에 쓴 시간만 재게 한다 (O-00000023)
- W-00000184 — 고칠 게 없는 바퀴와 로그 모양을 실패로 안 세게 한다 (O-00000019·25)
- W-00000185 — 사람이 만진 변경을 실행자 몫으로 안 섞이게 한다 (O-00000013) — **반려.**
  지금 구조로는 못 가른다는 것을 재서 카드에 남겼다. W-00000186 이 이어받는다.

## User value

드라이버에 일을 맡기고 그 옆에서 사람이 생각하고 얘기해도, 그 시간이 실행을 못 하게 만들지
않는다. 옳게 끝난 바퀴가 실패로 기록되지 않는다.

## Scope

### Included

- 시간을 실행에 쓴 것만 잰다.
- 바꿀 게 없는 바퀴와 로그를 고쳐 쓴 바퀴를 실패로 세지 않는다. 다만 조용히 넘어가지도 않는다.
- 사람이 만진 변경을 실행자 몫에 안 섞는다.

### Excluded

- 시간·시도 한도의 숫자 자체. 얼마로 하느냐가 아니라 **무엇을 재느냐**가 문제다.
- 판정하는 쪽이 무엇을 읽는지(O-00000024). 값의 크기 문제이지 성패를 재는 문제가 아니다.

## Risks

- **실패를 덜 세면 진짜 안 되는 카드가 안 멈춘다.** 시도 한도는 헛도는 카드를 끊으려고 있다.
  덜 세는 갈래마다 대신 무엇으로 끊을지가 있어야 한다.
- **사람이 만진 것을 가려내는 일이 격리된 체크아웃을 요구할 수 있다.** 그러면 이 스토리보다
  큰 변경이다. W-00000185 가 먼저 재고, 그 답이면 만들지 말고 보고한다.

## Success criteria

- 사람이 드라이버 옆에서 한 시간을 논의해도 다음 바퀴가 시간 한도에 안 막힌다.
- 일이 다 끝나서 바꿀 게 없는 바퀴가 실패로 안 세어진다. 대신 사람에게 끝났다고 알린다.
- 사람이 도는 중에 파일을 만져도 그 변경이 실행자가 한 것으로 안 적힌다.
- 사람이 겪는 결과: `--reset-attempts` 를 손으로 칠 일이 없다. **2026-08-02 하루에 네 번 쳤다.**

## Next action

없다. 자식 셋이 다 끝났다 — 둘은 실렸고 하나는 반려됐다.

## Verification

### 성공 기준 대조 — 2026-08-03

- **사람이 한 시간을 논의해도 다음 바퀴가 시간 한도에 안 막힌다** — 실행에 쓴 시간만 센다.
  실행자가 계속 매달리면 여전히 막힌다.
- **바꿀 게 없는 바퀴가 실패로 안 세어진다** — 대신 사람에게 알린다. 같은 헛것이 반복되면
  여전히 끊긴다. 로그를 고쳐 쓴 바퀴도 같다.
- **사람이 만진 변경이 실행자 몫으로 안 적힌다** — **못 지켰다.** 지금 구조로 못 가른다는 것을
  W-00000185 가 재서 남겼고 그 카드는 반려됐다. W-00000186 이 이어받는다.
- **`--reset-attempts` 를 손으로 칠 일이 없다** — 시간 때문에 치는 일은 없어졌다. 다만 죽고
  남은 표시를 치우는 용도로는 여전히 쓴다.

검증: 스크립트·훅 시험 전부 통과. `audit_stage.py` 오류 0 · 경고 0.

자식 셋의 판정 처분은 각자의 카드에 있다.

### Executed at close — 2026-08-03

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.212s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (237 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785731565
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785731565. Human review + merge required; the base branch was not modified.
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
Ran 553 tests in 83.152s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Related truth

- **O-00000023 · O-00000019 · O-00000025 · O-00000013** — 넷 다 같은 모양이다. 드라이버가
  "일이 제대로 됐나"를 엉뚱한 것으로 잰다: 시간은 벽시계로, 진행은 파일이 바뀌었는지로,
  성실함은 로그 모양으로 잰다. 그래서 옳게 한 일이 실패로 기록되고, 사람이 매번 손으로 우회한다.
  **손으로 풀 수 있다는 것이 더 나쁘다 — 장치가 틀렸는데 안 고쳐진다.**


## Progress


## Verification


## Retrospective


## Promotion decision
