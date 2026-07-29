---
id: W-00000051
title: Stage 초기화가 .gitignore에 .stage/.runtime/ 등록
kind: development
venue: codex
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000050
promotion: not_applicable
review: not_required
scope: stage/scripts/init_stage.py, stage/scripts/tests/, stage/skills/stage-init/SKILL.md, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000051 Stage 초기화가 .gitignore에 .stage/.runtime/ 등록

## Purpose

Stage 기계 상태(.stage/.runtime/)가 커밋되지 않도록 초기화 시점에 .gitignore 항목을 자동 등록한다

## Scope

`stage/scripts/init_stage.py`가 초기화 때마다 프로젝트 `.gitignore`에 `.stage/.runtime/` 한 줄을
보장한다. 새 테스트 파일, stage-init 스킬 문서, CHANGELOG, 매니페스트 두 개의 버전 상향을 포함한다.

## Success criteria

- git 저장소면 `.gitignore`가 없을 때 만들고, 있으면 기존 내용을 그대로 둔 채 항목만 덧붙인다.
- 항목이 이미 있으면 아무것도 하지 않는다. 슬래시 유무와 앞뒤 공백을 같은 항목으로 본다.
  주석 처리된 줄은 있는 것으로 치지 않는다.
- git 저장소가 아니면 `.gitignore`를 만들지 않는다. `.git`이 파일인 워크트리·서브모듈도 저장소로 본다.
- `python3 -m unittest discover -s stage/scripts/tests -q`와 `-s stage/hooks/tests -q` 모두 통과.

## Related truth

- `.stage/.runtime/`에는 세션 요약, 승격 의도, 질문 확인 표시, 스키마 유지보수 마커가 들어간다.
  기계 상태이므로 커밋 대상이 아니다. 반면 `.stage/`의 나머지는 프로젝트 이력이라 추적한다.
- `init_stage.py`에는 그동안 테스트 파일이 없었다. 이번에 `test_init_stage.py`를 새로 만들었다.

## Progress

- `ensure_runtime_ignore_entry()` 추가. 바이트 단위로 읽고 써서 기존 내용과 줄바꿈 방식을 보존한다.
- 초기화 결과 출력에 `Runtime ignore entry:` 한 줄 추가.
- `stage/scripts/tests/test_init_stage.py` 신설 — 생성·덧붙임·중복 방지·줄바꿈 없는 마지막 줄·
  `.git` 파일·비 git 디렉터리·주석 줄 7가지.
- stage-init 스킬 문서에 동작 명시, CHANGELOG 0.38.0, 매니페스트 0.37.2 → 0.38.0.

## Verification


### Executed at close — 2026-07-24

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784848278 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784848278
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784848278. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784848278 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784848278. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784848279 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784848279
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784848279
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784848279 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784848279
[W-00000003] completed on stage/driver/W-00000001-1784848279
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784848279. Human review + merge required; the base branch was not modified.
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete and strict audit clean.
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
Schema-v4 migration complete and strict audit clean.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 300 tests in 28.087s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784848306 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784848306
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784848306. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784848307 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784848307. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784848307 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784848307
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784848307
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784848307 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784848307
[W-00000003] completed on stage/driver/W-00000001-1784848307
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784848307. Human review + merge required; the base branch was not modified.
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete and strict audit clean.
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
Schema-v4 migration complete and strict audit clean.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 300 tests in 28.517s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 321 tests in 0.880s

OK
```

## Retrospective


## Promotion decision
