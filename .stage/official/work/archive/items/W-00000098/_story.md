---
id: W-00000098
title: 결정 기록이 계약의 적용 자리를 세어 적게 한다
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
retrospective_ref: R-00000097
promotion: not_applicable
review: not_required
scope: stage/templates/v4/project-stage/decisions/pending/_template.md, stage/templates/v4/project-stage/official/decisions/records/_template.md, stage/skills/stage-decision/SKILL.md, .stage/decisions/pending/_template.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000098 결정 기록이 계약의 적용 자리를 세어 적게 한다

## Purpose

2026-07-26~27 에 같은 실패를 세 번 했다. 계약을 정할 때 그 계약이 실제로 적용되는 자리를
세지 않고, 눈에 보이는 한 자리만 보고 썼다. 나머지 자리는 구현하다가 하나씩 드러났고,
그때마다 카드가 늘었다. 마지막에는 한 자리를 고치면서 다른 자리를 깨뜨렸다 —
DE-00000034 를 쓸 때 리뷰어가 도는 자리를 하나로 봤는데 실제로는 셋이었다.

세는 데 드는 비용은 `grep` 한 번이다. 안 세서 치른 비용은 카드 열 장이다.

결정 기록에 그 자리를 세어 적는 절을 둔다.

## Scope

- 결정 기록 템플릿(대기/공식 둘 다)에 `## Where this applies` 절을 넣는다.
- `stage-decision` 스킬이 그 절을 코드에서 세어 채우도록 지시한다 — 추측이 아니라 실제
  호출 지점을 찾아 적는다.
- 이 프로젝트의 템플릿 사본에도 반영한다.

범위 밖: 감사로 강제하지 않는다. 강제하면 기존 결정 기록 서른세 건이 전부 걸려 고칠 일이
폭발한다. 스킬 지시는 결정을 쓸 때마다 읽히므로 다음 결정부터 적용된다.

## Success criteria

- 결정 기록 템플릿 둘에 적용 자리를 적는 절이 있다.
- `stage-decision` 스킬이 그 절을 어떻게 채우는지 지시한다 — 무엇을 세고(계약이 건드리는
  동작을 실제로 부르는 지점), 어떻게 적는지(자리마다 파일·줄·쓰는 설정).
- 기존 결정 기록 서른세 건은 그대로 두고 감사가 새로 막지 않는다.
- 인수 검사 두 개가 통과한다. 플러그인 버전을 올리고 CHANGELOG 에 적는다.

## Related truth

DE-00000034 의 "계약이 적용되는 자리" 절이 이 규칙의 첫 사례다.


## Progress

- 결정 기록 템플릿 둘에 `## Where this applies` 절을 넣었다 — 대기 기록(`Chosen direction`
  다음)과 공식 기록(`Alternatives considered` 다음).
- `stage-decision` 스킬에 "Count where it applies" 절을 넣었다. 기억으로 적지 말고 코드에서
  호출 지점을 찾아 적을 것, 자리마다 파일·줄과 그 자리가 읽는 설정을 적을 것, 명령 문자열이나
  설정 키를 공유하는 두 자리는 "부르는 쪽이 둘"이라고 밝힐 것을 지시한다. 빈 절은 세지 않았다는
  뜻이라고 못 박았다.
- 커버리지 게이트에서 그 절을 가리키게 했고, 기록 작성 목록에도 넣었다.
- 이 프로젝트의 템플릿 사본 둘을 갱신했다(공식 쪽은 `refresh_guidance.py`).
- 버전을 0.45.2 로 올리고 CHANGELOG 에 적었다.
- 인수 검사 두 개 통과(scripts 359, hooks 327), 감사 오류 0.

## Verification

사람이 직접 확인했다.

- 결정 기록 템플릿 둘에 `## Where this applies` 절이 있다 (대기·공식).
- `stage-decision` 스킬이 세 자리에서 그 절을 가리킨다 — 커버리지 게이트, 전용 절
  "Count where it applies", 기록 작성 목록.
- 스킬이 지시하는 내용: 기억이 아니라 코드에서 찾을 것, 자리마다 파일·줄과 읽는 설정을 적을
  것, 명령·설정 키·환경 변수를 공유하는 두 자리는 "부르는 쪽이 둘" 이라고 밝힐 것, 빈 절은
  세지 않았다는 뜻.
- 이 프로젝트 사본 둘을 갱신했다. 공식 쪽은 `refresh_guidance.py` 로 했고 감사 경고가
  사라졌다.
- 기존 결정 기록 서른세 건은 그대로다. 감사가 새로 막지 않는다 (오류 0).
- 인수 검사 두 개를 직접 돌렸다: scripts 359개 OK, hooks 327개 OK.
- 버전 SSOT 둘 다 0.45.2, CHANGELOG 갱신됨.


### Executed at close — 2026-07-27

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137298
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137298. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137299 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137299. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137300 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137300
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137300. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137301 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137301. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 58.729s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.964s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (112 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] review infrastructure failure; retry without spending attempt 0/1
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137358
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137358. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137359 (base: main)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137359. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137360 (base: main)
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1785137360
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785137360. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785137361 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785137361. Human review + merge required; the base branch was not modified.
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
Ran 389 tests in 58.998s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 1.007s

OK
```

## Retrospective


## Promotion decision
