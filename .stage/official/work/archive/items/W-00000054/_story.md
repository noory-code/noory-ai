---
id: W-00000054
title: 승격 게이트가 셸로 실행한 스크립트의 official 쓰기를 막지 못함
kind: fix
venue: codex
priority: high
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000053
promotion: not_applicable
scope: stage/hooks/stage_shell.py, stage/hooks/stage_guard.py, stage/hooks/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000054 승격 게이트가 셸로 실행한 스크립트의 official 쓰기를 막지 못함

## Purpose

Stage 가드가 셸 명령의 쓰기 대상을 파싱하지만, 인터프리터 안에서 일어나는 쓰기는 보지 못한다.
`python3 -c "..."`나 `python3 - <<EOF ... EOF`로 넘긴 코드는 본문이 데이터로 취급돼 파서가
건너뛴다. 그 결과 인라인 코드가 `.stage/official/`을 승격 의도 없이 수정할 수 있다.

## Source

W-00000053 진행 중 실제로 이 우회가 두 번 발생했다(`python3 - <<EOF` + `shutil.copyfile`).
두 번 다 되돌리고 정식 절차를 다시 밟았다. R-00000052에서 결함으로 캡처.

## User value

Stage 사용자가 official 구역의 무결성을 신뢰할 수 있다. 게이트가 자신이 검사할 수 없는 입력을
정직하게 거부하므로, 정직하지만 부주의한 에이전트의 의도치 않은 official 쓰기가 막힌다.

## Scope

### Included

- `stage/hooks/stage_shell.py`: 불투명 인라인 인터프리터 호출 감지기 추가.
- `stage/hooks/stage_guard.py`: `validate_pre_tool`에서 감지 시 deny.
- 회귀 테스트, CHANGELOG, 매니페스트 두 개 버전 상향.

### Excluded

- 파이프 stdin(`echo ... | python3`)은 이번 범위 밖. 히어독·`-c`·`-e`부터.
- 인터프리터 본문을 실제로 해석해 쓰기 경로를 알아내는 시도(정적으로 불가능).

## Dependencies

없음.

## Risks

오탐: `.stage`를 언급하는 무해한 인라인 코드가 차단된다. 완화 — 탈출구가 항상 있다(Write/Edit는
게이트를 거쳐 정상 동작, 이름 있는 스크립트도 통과). 게이트 메시지가 이 경로를 안내한다.

## Success criteria

- `python3 - <<EOF`/`python3 -c`/`node -e`/`perl -e` 등이 인라인 코드로 실행되며 명령문에
  `.stage`가 있으면 deny 되고, 재현 테스트가 통과한다.
- 통과해야 하는 것이 통과한다: `python3 stage/scripts/foo.py`(이름 있는 스크립트),
  `python3 -m unittest ...`(모듈), `.stage`를 언급하지 않는 인라인 코드.
- Stage 자체 도구 호출(`promote_intent.py`, `close_work.py`, `archive_work.py`,
  `audit_stage.py`)이 계속 동작한다.
- `python3 -m unittest discover -s stage/hooks/tests -q`와 `-s stage/scripts/tests -q` 통과.

## Decision (2026-07-25, 사용자 승인)

불투명 인라인 인터프리터 코드 차단 방식을 택한다. 본문에 `.stage/official` 문자열이 있을 때만
막는 방식은 계산된 경로(`Path('.stage')/rel`)를 놓쳐 실제 발생한 우회를 못 잡으므로 기각.
경고만 하는 방식은 구멍을 실제로 닫지 못하므로 기각. 원칙: Fail Fast(검사 불가한 입력은 거부),
Honesty(가드가 볼 수 없는 것을 통과시키지 않음).

## Next action

Codex 구현.

## Progress

- `stage_shell.py`에 `interpreter_inline_stage_write` 추가. 명령에 `.stage`가 있고, 인터프리터
  그룹이 `-c`·`-e`이거나 자기 그룹으로 히어독을 읽으면 True.
- `stage_guard.py`의 `validate_pre_tool` 셸 게이트에 연결, 적중 시 deny.
- 리뷰에서 오탐 발견: 히어독 판정이 명령 전체 전역이라, 무관한 `cat` 히어독 뒤의 이름 있는
  스크립트까지 차단됐다. 그룹 단위 판정으로 수정하고 회귀 테스트 2건 추가.
- 신설 테스트 `test_interpreter_inline_guard.py`.

## Verification

### Executed at close — 2026-07-25

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 324 tests in 0.875s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784944620 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784944620
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784944620. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784944621 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784944621. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784944621 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784944621
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784944621
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784944621 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784944621
[W-00000003] completed on stage/driver/W-00000001-1784944621
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784944621. Human review + merge required; the base branch was not modified.
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
Ran 300 tests in 27.420s

OK
```

## Retrospective

## Promotion decision
