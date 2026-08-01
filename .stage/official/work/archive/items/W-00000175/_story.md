---
id: W-00000175
title: 밀린 결정을 공식으로 내리고 다시 안 쌓이게 한다
kind: development
venue: codex
milestone: M-00000001
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000178
promotion: not_applicable
review: not_required
scope: stage/skills/stage-retrospective/, stage/scripts/tests/, stage/operations/, stage/CHANGELOG.md, .stage/
promotes:
decision_refs:
---

# W-00000175 밀린 결정을 공식으로 내리고 다시 안 쌓이게 한다

## Purpose

DE-00000030 이 정한 승격 규칙을 사람이 손으로만 지켜서 앞으로를 구속하는 결정 여섯이 대기에 갇혔다.

## Actions

- W-00000176 — 밀린 결정 여섯을 공식으로 내린다 (기록 정리 · codex)
- W-00000177 — 카드를 닫을 때 승격 여부를 그 자리에서 판정하게 한다 (구현 · codex)
- W-00000178 — 드라이버가 승격 판정을 대신 찍지 못하게 한다 (구현 · codex)

## User value

프로젝트를 지금 구속하는 결정을 `official/decisions/` 한 자리에서 다 읽는다. 일회성 허가는
거기 안 섞인다. 카드를 보관해도 그 카드가 정한 규칙이 대기 서랍에 갇히지 않는다.

## Scope

### Included

- 대기에 갇힌 결정 여섯을 공식으로 옮기고 인덱스에 싣는다.
- 카드를 닫을 때 그 카드가 소유한 결정의 승격 여부를 판정하게 만든다.
- 그 계약을 지키는지 보는 시험.

### Excluded

- **일회성 venue 허가 여섯**(DE-6·8·25·26·41·45). DE-00000030 이 대기에 남기라고 정했다.
  건드리지 않는다.
- 승격 규칙 자체를 다시 정하는 일. DE-00000030 이 이미 소유한다.
- 보관된 카드가 승격할 수 있게 게이트를 여는 일. 지금 막힌 것을 푸는 데 그 변경이 필요 없다 —
  승격 게이트는 카드의 `promotes` 목록만 보므로 열려 있는 카드 하나로 내릴 수 있다.

## Risks

- **로드맵 착수 결정(DE-00000049)이 갈래가 다르다.** 일회성 허가가 아니니 규칙상 승격 대상인데,
  마일스톤 상태가 이 결정 사슬에서 계산되고 승격 때 사슬을 다시 검사하는 자리가 있다. 나머지
  다섯과 같이 옮기기 전에 그 검사를 통과하는지 먼저 봐야 한다.
- **닫을 때 판정을 강제하면 결정 없는 카드까지 걸릴 수 있다.** 결정을 안 가진 카드는 지금처럼
  지나가야 한다.

## Success criteria

- `decisions/pending/` 에 `authorizes: venue_exception` 없이 `decided` 로 남은 결정이 없다.
- 결정을 소유한 카드가 승격 여부를 안 정하고는 닫히지 않는다.
- 그 계약을 지키는지 보는 시험이 있고, 결정 없는 카드는 그대로 지나간다.
- 사람이 겪는 결과: 지금 나를 구속하는 규칙이 무엇인지 공식 서랍만 열면 다 보인다.

## Next action

없다. 자식 셋이 다 닫혔다.

## Verification

### 성공 기준 대조 — 2026-08-01

- **대기에 `authorizes: venue_exception` 없이 `decided` 로 남은 결정이 없다** — 일곱을 옮겼고
  남은 여섯은 전부 일회성 통행증이다. 옮긴 본문은 상태 한 줄 말고 글자가 안 바뀌었다(대조 확인).
- **결정을 소유한 카드가 승격 여부를 안 정하고는 닫히지 않는다** — 사람이 닫는 길과 드라이버가
  닫는 길 둘 다 막혔다. 결정도 승격 대상도 없는 집계 부모만 지나간다.
- **그 계약을 지키는지 보는 시험이 있고, 결정 없는 카드는 그대로 지나간다** — 세 갈래를 다 본다.
- **사람이 겪는 결과** — 공식 서랍만 열면 지금 구속하는 규칙이 다 보인다. 소진된 통행증은 안
  섞인다.

검증: 스크립트 531건, 훅 356건 통과. `audit_stage.py` 오류 0 · 경고 0.

자식 셋의 판정 처분은 각자의 카드에 있다.

### Executed at close — 2026-08-01

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 356 tests in 1.205s

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
[W-00000001] completed on stage/driver/W-00000001-1785562232
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785562232. Human review + merge required; the base branch was not modified.
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
Ran 531 tests in 74.793s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Related truth

- **DE-00000030** — 결정이 언제 공식이 되는가. 일회성 허가는 대기에 남고 나머지 `decided` 는
  승격한다. 그 결정이 남긴 후속("닫을 때 그 자리에서 판정한다")이 이 스토리의 뼈대다.


## Progress


## Verification


## Retrospective


## Promotion decision
