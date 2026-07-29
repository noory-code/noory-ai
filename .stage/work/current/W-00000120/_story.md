---
id: W-00000120
title: 깊이 1 예외에서 카드 이름 모양을 다시 뺀다
kind: fix
venue: codex
milestone:
priority: 2
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000126
promotion: not_applicable
review: not_required
scope: stage/hooks/, stage/hooks/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000120 깊이 1 예외에서 카드 이름 모양을 다시 뺀다

## Purpose

W-00000114 가 수명 주기 루트 깊이 1 의 .md 를 카드 모양 검사에서 빼면서, 은퇴한 v4 평평한 카드(work/current/W-xxx.md)도 함께 통과하게 됐다. 전에는 게이트가 그 자리에서 막았고 지금은 감사(WORK026)가 나중에 잡는다 — 조기 차단이 사후 감지로 내려앉았다. 깊이 1 예외에서 작업 ID 모양 이름(W-숫자.md)만 도로 빼서 조기 차단을 되살린다. 인덱스·README·템플릿은 그대로 통과해야 한다.

## Actions

- 깊이 1 예외에서 **작업 ID 모양 이름**(`W-` + 숫자 + `.md`)만 도로 뺀다. 인덱스·README·
  템플릿은 그대로 통과해야 한다 — 그것을 막던 것이 W-00000114 가 고친 잠금이다.
- 은퇴한 평평한 카드가 게이트에서 다시 거절되는 것을 테스트로 고정한다. 그러면서 W-00000114
  가 연 자리(계획 인덱스 편집 허용)가 안 깨지는 것도 같은 묶음에서 고정한다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## User value

손으로 만든 옛 모양 카드가 게이트에서 바로 막힌다. 지금은 통과했다가 나중에 감사에서
`WORK026` 으로 잡히는데, 조기 차단이 사후 감지로 내려앉은 상태다.

## Scope

### Included


### Excluded


## Risks

- 예외를 좁히다 인덱스·템플릿까지 막으면 W-00000114 가 고친 잠금이 되살아난다. 두 성질을
  같은 테스트 묶음에서 함께 고정해 한쪽을 고치다 다른 쪽이 깨지지 않게 한다.

## Success criteria

- 수명 주기 폴더 깊이 1 에 놓인 `W-<숫자>.md` 파일 쓰기가 게이트에서 거절된다. 테스트가
  고정한다.
- `index.md`·`README.md`·`_template.md` 편집은 그대로 통과한다. 같은 묶음의 테스트가
  고정한다.
- 깊이 2·3 의 진짜 카드 검사와 부모 게이트는 그대로다 — 기존 훅 테스트가 전부 통과한다.
- `python3 -m unittest discover -s stage/hooks/tests -q` 와
  `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Next action

## Progress

첫 병렬 실전, 자기 트리에서 1라운드에 완성. 게이트가 `W-숫자.md` 를 도로 거절하고
인덱스·README·템플릿은 계속 통과한다.

## Verification

병합 뒤 본 체크아웃에서 훅 343개·스크립트 477개 전부 통과, 감사 0/0. 드라이버 실패 두 번은
카드와 무관 — 1라운드는 물려받은 프로젝트 변수가 훅 스위트를 오염(144개), 2라운드는 일이
이미 끝나 "변경 없음". 1라운드 실행자가 격리 환경 전체 통과를 스스로 증명해 뒀다. 처분은
R-00000126.

### Executed at close — 2026-07-29

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.083s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (193 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] close failed (acceptance or independent review); close_work output:
independent review did not pass; retry 1/2
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785336212
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785336212. Human review + merge required; the base branch was not modified.
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
Ran 477 tests in 72.723s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.026s

OK
```

## Retrospective

[R-00000126](../../retrospectives/R-00000126.md)

## Promotion decision

not_applicable — 플러그인 소스 수정.
