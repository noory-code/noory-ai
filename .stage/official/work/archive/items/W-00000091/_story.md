---
id: W-00000091
title: close_work 가 돌리는 리뷰에도 카드 경로를 준다
kind: fix
venue: codex
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000090
promotion: not_applicable
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/, stage/docs/SCHEMA_V4.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000091 close_work 가 돌리는 리뷰에도 카드 경로를 준다

## Purpose

리뷰 계약(DE-00000032)은 리뷰어가 `STAGE_WORK_ITEM_PATH` 로 카드를 읽어 성공 기준에 대고
판정하는 것인데, 그 변수를 넣어 주는 곳은 감독 드라이버뿐이다(W-00000085). `close_work.py`
가 직접 돌리는 리뷰 둘 — 자율 카드의 독립 리뷰(무인 모드가 닫을 때 타는 경로)와 단계별
리뷰 — 은 `run_check(review_command, ...)` 를 환경 없이 불러서, 프롬프트 속
`$STAGE_WORK_ITEM_PATH` 가 빈 값으로 풀린다. 리뷰어는 카드를 못 찾고 diff 만 보게 되어
계약이 그 경로에서 소리 없이 반쪽이 된다. `close_work` 는 카드 경로를 이미 알고 있으므로
드라이버와 같은 방식으로 환경에 넣으면 된다.

## Source

W-00000087 준비 중 `close_work.py` 를 확인하다 발견 (2026-07-26). 계약: DE-00000032.


## User value

무인 모드가 카드를 닫을 때 도는 독립 리뷰가 드디어 카드를 읽고 기준에 대고 판정한다. 지금은
그 경로의 리뷰어가 카드 경로를 빈 값으로 받아 diff 만 보므로, 리뷰 계약이 감독 모드에서만
온전하다.

## Scope

### Included

- `close_work.py` 의 리뷰 실행 둘(독립 리뷰 `close_work.py:346` 부근, 단계별 리뷰
  `close_work.py:364` 부근)에 카드의 절대 경로를 `STAGE_WORK_ITEM_PATH` 환경 변수로 넘긴다.
  감독 드라이버가 리뷰어에게 넘기는 값과 같은 의미다.
- `stage/docs/SCHEMA_V4.md` 의 리뷰 환경 계약에 적는다: close_work 가 돌리는 리뷰도 같은
  변수를 받는다.

### Excluded

- 리뷰 명령 문구 — W-00000087 이 이미 끝냈다.
- 드라이버 쪽 리뷰 환경 — W-00000085 가 이미 끝냈다.

## Dependencies

- 없음 (W-00000087 완료 상태에서 시작).

## Risks

- 환경 변수 하나를 더하는 변경이라 작지만, close_work 는 드라이버·무인 모드·손 마감이 모두
  쓰는 공용 경로다 — 기존 close_work 테스트가 전부 그대로 통과해야 한다.

## Success criteria

- close_work 의 독립 리뷰와 단계별 리뷰 모두 리뷰 명령 환경에 닫는 카드의 절대 경로가
  `STAGE_WORK_ITEM_PATH` 로 들어 있다. 그것을 확인하는 테스트가 있고 고치기 전 코드에서
  실패한다.
- 기존 테스트 전부 통과 — `python3 -m unittest discover -s stage/scripts/tests -q`,
  `python3 -m unittest discover -s stage/hooks/tests -q`.
- `SCHEMA_V4.md` 가 close_work 리뷰의 환경 계약을 적고 있다.
- 두 `plugin.json` 의 version 이 올라 있고 `stage/CHANGELOG.md` 에 항목이 있다.

제약:

- **커밋하지 않는다.** 작업 트리에 변경만 남기고 멈춘다.
- 저장소 산출물은 영어. `.stage/` 안의 글만 한국어.
- scope 밖은 건드리지 않는다.


## Next action

`close_work.py` 의 리뷰 실행 둘(독립 리뷰, 단계별 리뷰)에 `STAGE_WORK_ITEM_PATH` 를 환경으로
넘긴다. 그것을 확인하는 테스트를 만들고 고치기 전 코드에서 실패하는지 본다. W-00000087 과
같은 계약의 다른 면이므로 같은 날 이어서 하면 좋다.

## Progress

## Verification

### 기준 판정 — 반대 venue (Claude), DE-00000032 방식 (2026-07-26)

- close_work 의 리뷰 둘 다 카드 절대 경로를 `STAGE_WORK_ITEM_PATH` 로 받는다 — 채움. 독립
  리뷰와 단계별 리뷰의 `run_check` 호출 둘 다 환경을 받는다.
- 테스트가 있고 고치기 전 코드에서 실패한다 — 확인. 저장소 밖 사본(0.43.15 코드)에 새 테스트를
  얹어 돌리니 두 경로 모두 실패(RED)했고, 고친 코드에서는 test_close_work 37개 포함 전체
  357 + 327 이 통과한다.
- `SCHEMA_V4.md` 가 close_work 리뷰의 환경 계약을 적고 있다 — 채움.
- 버전 0.43.16, CHANGELOG 항목 — 채움. 감사 errors=0.

### 그 밖에 본 것 (기준 밖 관찰)

- 없음. 차단할 지적 없음.

이로써 O-00000001 전수 지도의 실행 자리 세 줄이 전부 닫혔다 — 리뷰 계약(카드 기준 판정)이
감독 드라이버·무인 닫기·단계별 리뷰 어디서든 같은 입력을 받는다.

### Executed at close — 2026-07-26

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (34 earlier lines omitted)
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1785047772. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785047772 (base: main)
[W-00000001] completed on stage/driver/W-00000001-1785047772
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785047772. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785047773 (base: main)
Outcome: blocked — cannot commit pre-close lifecycle for W-00000002: simulated lifecycle commit failure
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1785047773 (base: main)
[W-00000002] close failed (acceptance or independent review); close_work output:
obsolete first review output; retry 1/2
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785047773. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785047774 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785047774. Human review + merge required; the base branch was not modified.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 357 tests in 40.103s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

R-00000090. 핵심: 마지막 실행 자리가 닫혀 리뷰 계약이 모든 경로에서 온전해졌다.

## Promotion decision

official 로 올릴 산출물 없음(promotion: not_applicable). 카드와 회고는 아카이브로 간다.
