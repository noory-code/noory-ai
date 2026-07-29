---
id: W-00000102
title: 드라이버 설명 문서를 계약 다섯 층에 맞춘다
kind: documentation
venue: claude
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000101
promotion: not_applicable
review: not_required
scope: stage/docs/SCHEMA_V4.md, stage/skills/stage-drive/SKILL.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000102 드라이버 설명 문서를 계약 다섯 층에 맞춘다

## Purpose

DE-00000034 의 다섯 층이 다 들어가면서 드라이버가 실제로 하는 일이 바뀌었다. 그것을 설명하는
문서는 그대로다. `stage/docs/SCHEMA_V4.md` 의 `### Unattended driver loop`(328 행)는 아직
"성공하면 실행자 산출물을 커밋한다" 고 적혀 있고, 리뷰 지적을 주고받는 왕복도, 실패가 로그에
남는 것도, 띄운 것을 거두는 것도 없다. `stage/skills/stage-drive/SKILL.md` 는 그 문서를 규칙의
주인으로 가리키고 있어서, 읽는 사람이 낡은 쪽을 진짜로 믿게 된다.

W-00000097 리뷰어가 기준 밖 관찰로 짚었다. 그 카드 범위 밖 파일이라 그때 안 고쳤다.

## Scope

- `SCHEMA_V4.md` 의 무인 드라이버 절을 지금 동작에 맞춘다 — 리뷰 지적 왕복과 처리 표기, 실패가
  공용 로그에 남는 것, 상한에 닿으면 커밋하지 않고 사람에게 넘기는 것, 바퀴가 띄운 것을 거두는 것.
- `stage-drive` 스킬이 가리키는 규칙 주인과 실제 내용이 어긋나지 않게 맞춘다.

범위 밖: 계약 자체(DE-00000034)는 이미 최신이다. 드라이버 코드도 안 건드린다.

## Success criteria

- 무인 드라이버 절이 계약 다섯 층을 다 담는다. 낡은 서술("성공하면 실행자 산출물을 커밋한다")이
  남아 있지 않다.
- 스킬이 가리키는 주인 문서와 실제 동작이 같다.
- 인수 검사 두 개가 통과한다. 버전을 올리고 CHANGELOG 에 적는다.

## Related truth

DE-00000034 가 계약을 소유한다. 이 카드는 그 계약을 설명하는 문서를 맞추는 일이다.


## Progress

- `SCHEMA_V4.md` 의 무인 드라이버 절에 계약 다섯 층을 넣었다 — 공용 작업 로그, 실행자 주장과
  드라이버 관찰의 대조, 실패가 로그에 남는 것(못 남기면 그 자체가 오류), 리뷰 지적이 다음
  바퀴로 흐르며 받는다/안 받는다/미룬다 를 근거와 함께 적는 것, 상한에 닿으면 커밋하지 않고
  넘기는 것, 바퀴가 띄운 것을 거두는 것(없는 venue 는 `null` 로 밝힘).
- `stage-drive` 스킬의 규칙 주인 목록에 DE-00000034 를 넣었다.
- 인수 검사 두 개 통과(scripts 389, hooks 327), 감사 오류 0. 버전 0.49.2, CHANGELOG 갱신.

## Verification

사람이 직접 확인했다.

- 낡은 서술("성공하면 실행자 산출물을 커밋한다")이 이제 다섯 층 설명 뒤에 놓여 실제 동작과
  어긋나지 않는다.
- 스킬이 가리키는 규칙 주인에 계약(DE-00000034)이 들어 있다.
- 인수 검사 두 개를 직접 돌렸다: scripts 389개 OK, hooks 327개 OK.

### Executed at close — 2026-07-27

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137853
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137853. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137854 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137854. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137855 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137855
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137855. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137856 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137856. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 59.043s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 1.036s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective 메모

이 카드는 없었어야 한다. C1~C5 각 층이 자기가 바꾼 설명 문서까지 범위에 넣었으면 문서가
따로 밀리지 않았다. 자리를 셀 때 코드 호출 지점만 세고 설정·문서·실패 경로를 안 센 것이
오늘 반복된 실수다 (W-00000098 이 넣은 규칙의 다음 판).


## Verification


## Retrospective


## Promotion decision
