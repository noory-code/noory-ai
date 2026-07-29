---
id: W-00000134
title: 드라이버가 자식에게 주는 프로젝트 환경이 대상 트리를 가리킨다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000128
promotion: not_applicable
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/test_drive.py, stage/scripts/tests/test_drive_unattended.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000134 드라이버가 자식에게 주는 프로젝트 환경이 대상 트리를 가리킨다

## Purpose

첫 병렬 실전(2026-07-29)에서 카드 둘이 멀쩡한 일로 실패했다. 드라이버를 백그라운드 셸에서 띄우면 CLAUDE_PROJECT_DIR 와 PROJECT_ROOT 가 본 체크아웃을 가리킨 채 실려 오고, 드라이버가 그것을 실행자·리뷰어·인수 검사에 그대로 물려준다. Stage 훅은 그 변수를 payload cwd 보다 먼저 쓰므로 작업 트리 안의 훅 스폰 테스트 전부가 본 체크아웃을 프로젝트로 판정했다 — 훅 스위트 343개 중 144개, 스크립트 쪽 8개가 그렇게 무너졌고 카드 시도 둘이 깎였다. 드라이버가 만든 실행 환경은 드라이버가 책임진다(DE-00000039 의 원칙): 자식에게 주는 환경에서 그 두 변수를 --project-root 로 덮어쓴다. 실행자·리뷰어·사전 점검·인수 검사 네 자리 전부다.

## Actions

- 드라이버가 자식을 띄우는 자리 전부에서 `CLAUDE_PROJECT_DIR` 와 `PROJECT_ROOT` 를
  `--project-root` 의 절대 경로로 덮어쓴다. 자리 넷: 실행자, 리뷰어, venue 사전 점검,
  인수 검사(`run_check` 에 넘기는 환경).
- 지우는 것이 아니라 **덮어쓴다.** 훅이 그 변수를 쓰는 것 자체는 호스트 계약이다 — 문제는
  값이 다른 트리를 가리킨 채 새는 것이다. W-00000128 이 검증 probe 에서 같은 결론을 냈다
  (지우지 말고 맞다고 주장하라).
- reaper 는 그대로 둔다 — 이미 카드 경로로 대상을 고르므로 이 변수와 무관하고, 세는 김에
  확인만 한다.

## Scope

`stage/scripts/drive.py` 의 자식 환경 구성, 그 테스트 둘, CHANGELOG 미출시 절.

**안 하는 것**: 훅이 변수를 cwd 보다 먼저 읽는 우선순위 자체. 그것은 호스트가 프로젝트를
고정하라고 준 계약이고, 드라이버가 올바른 값을 주면 올바르게 동작한다.

## Success criteria

1라운드 뒤 실측이 계약을 갈랐다: 세션 자식(실행자·리뷰어·사전 점검·close_work)은 변수를
**박아야** 하고, 인수 검사는 변수를 **걷어야** 한다. 훅 스폰 테스트 스위트는 hermetic 이라
두 변수가 어떤 값이든 — 올바른 루트여도 — 실려 있으면 깨진다. 본 체크아웃에서 변수를 자기
루트로 박고 소비자 테스트를 돌리면 4개가 깨지는 것으로 확인했다(2026-07-29). 1라운드가
인수 검사에도 박은 것은 이 실측을 몰랐을 때의 선택이고, 그대로 두면 다음 드라이버 실행부터
모든 인수 검사가 무너진다 — 1라운드 리뷰가 통과한 것은 그 스텝의 검사를 아직 옛 코드(메모리에
로드된 드라이버)가 돌렸기 때문이다.

- 실행자·리뷰어·사전 점검·close_work 자식이 받는 환경에서 두 변수가 `--project-root` 를
  가리킨다. 엉뚱한 값을 밖에서 박아 놓고 돌려도 그렇다. 테스트가 고정한다.
- **인수 검사(`run_check`)가 받는 환경에는 두 변수가 없다.** 밖에서 어떤 값을 박아 놓고
  돌려도 없다. 테스트가 고정한다.
- 두 계약이 갈리는 이유가 코드 주석이 아니라 이 카드와 CHANGELOG 항목에 적혀 있다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- [DE-00000039](../../../official/decisions/records/DE-00000039.md) — 드라이버가 만든 것은
  드라이버가 처리한다
- [R-00000118](../../../work/retrospectives/R-00000118.md) — 같은 변수 쌍의 probe 쪽 결론


## Progress

두 바퀴, 2026-07-29. 1라운드는 넷 다 박는 구현 — 승인 리뷰를 받았으나 직후 실측이 절반을
뒤집어 기준을 갈라 다시 돌렸다. 2라운드가 검사 걷기·세션 박기로 갈라 넣었다.

## Verification

새 프로세스에서 스크립트 477개·훅 343개 전부 통과. 드라이버 자신의 판정은 두 바퀴 다
실패였는데 둘 다 받지 않았다 — 이 카드는 드라이버를 고치므로, 도는 드라이버(수정 전 코드)의
인수 검사가 걷어내기 전의 독으로 스스로 깨진다. 수정을 만든 스텝의 검사는 옛 코드가 돌린다.
검증은 새 프로세스가 한다. 상세는 R-00000128.

직접(드라이버 밖) 스위트 실행에 변수를 실으면 여전히 깨진다(소비자 테스트 7개) — 스위트의
성질이고, 이제 그 변수를 실어 보내는 경로가 없다. 테스트 헬퍼 강화는 겪으면 세운다.

### Executed at close — 2026-07-30

```
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
[W-00000001] completed on stage/driver/W-00000001-1785337172
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785337172. Human review + merge required; the base branch was not modified.
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
Ran 477 tests in 69.842s

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
[W-00000001] completed on stage/driver/W-00000001-1785337243
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785337243. Human review + merge required; the base branch was not modified.
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
Ran 477 tests in 71.170s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 343 tests in 1.004s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000128](../../../retrospectives/R-00000128.md)

## Promotion decision

not_applicable — 플러그인 소스 수정.
