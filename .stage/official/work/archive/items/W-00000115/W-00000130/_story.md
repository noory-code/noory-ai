---
id: W-00000130
title: 리뷰 계약을 설명하는 문서가 실제 동작과 같아진다
kind: documentation
venue: claude
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000127
promotion: not_applicable
review: not_required
scope: stage/operations/review.md, stage/docs/, stage/skills/stage-retrospective/SKILL.md, stage/skills/stage-drive/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000130 리뷰 계약을 설명하는 문서가 실제 동작과 같아진다

## Purpose

W-00000117 이 리뷰 판정을 JSON 파일로 옮기면서 문서 넷이 옛 계약을 그대로 말한다. 산문의 BLOCK: 표식으로 차단한다는 서술이 stage/operations/review.md:38, stage/docs/SCHEMA_V4.md:145·148·301, stage/skills/stage-retrospective/SKILL.md:76 에 남아 있는데, 이제 BLOCK: 을 찍고 0 으로 끝나면서 승인 판정을 쓴 명령은 카드를 닫는다. 그리고 stage-drive/SKILL.md:250-251 의 '리뷰어 인프라 실패는 시도를 안 쓴다'가 판정 파일이 없을 때만 참이다 — 파일이 있고 깨졌으면 타임아웃 문구가 섞여도 시도를 쓴다. 문서가 틀린 계약을 말하면 다음 사람이 그것을 믿고 리뷰 명령을 만든다.

## Actions

- 문서 넷에서 산문 `BLOCK:` 표식으로 차단한다는 서술을 걷고, 판정 파일이 통과를 정한다는
  실제 동작으로 바꾼다 — `stage/operations/review.md`, `stage/docs/SCHEMA_V4.md`(세 자리),
  `stage/skills/stage-retrospective/SKILL.md`.
- `stage/skills/stage-drive/SKILL.md` 의 "리뷰어 인프라 실패는 시도를 안 쓴다"를 조건과 함께
  다시 쓴다. 판정 파일이 있고 깨졌으면 타임아웃 문구가 섞여도 시도를 쓴다.
- 같은 문서에서 리뷰가 막았을 때 감독 실행에서 무엇을 하는지 갈라 적는다. 지금 "다시 돌리는
  것이 답이 아니다"와 "다음 실행자가 실패 항목을 처분한다"가 같은 문서에 있어 두 갈래로
  읽힌다(R-00000118 이 남긴 것). 무인은 왕복이 자동이고 감독은 사람이 정한다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## Scope

`stage/operations/review.md`, `stage/docs/`, `stage/skills/stage-retrospective/SKILL.md`,
`stage/skills/stage-drive/SKILL.md`, CHANGELOG 미출시 절.

**안 하는 것**: 코드 수정. 이 카드는 문서가 코드를 사실대로 말하게 하는 일이다.

## Success criteria

- 네 문서 어디에도 산문 `BLOCK:` 표식이 통과를 정한다는 서술이 없다. 판정 파일이 정한다고
  적혀 있다.
- 리뷰어 인프라 실패 서술이 조건을 밝힌다 — 판정 파일이 없을 때만 시도를 안 쓴다.
- 리뷰가 막았을 때의 다음 행동이 감독·무인으로 갈려 적혀 있다.
- 문서가 가리키는 동작이 실제 코드와 같은지 확인한 근거가 작업 로그에 있다. 문서를 고치면서
  코드를 안 읽으면 다음 어긋남이 그대로 생긴다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth


## Progress

첫 병렬 실전, 자기 트리에서 claude venue 로 완성. 문서 넷이 판정 파일 계약을 말하고, 무료
재시도 조건과 감독·무인의 다음 행동이 갈라 적혔다.

## Verification

병합 뒤 문서 diff 를 사람이 직접 읽어 코드와 대조 확인. 2라운드 실행자도 모든 새 서술을
코드에서 재확인했다. 드라이버 실패 두 번은 카드와 무관 — 1라운드는 900초가 편집엔 충분했으나
세션 종료엔 모자랐고(일은 그때 이미 완성), 2라운드는 같은 내용이라 "진전 없음". 처분은
R-00000127.

### Executed at close — 2026-07-29

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
[W-00000001] completed on stage/driver/W-00000001-1785336285
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785336285. Human review + merge required; the base branch was not modified.
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
Ran 477 tests in 71.571s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000127](../../../retrospectives/R-00000127.md)

## Promotion decision

not_applicable — 플러그인 문서 수정.
