---
id: W-00000311
title: 범위 넘음 알림에서 고치지 않은 경로를 뺀다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000311
promotion: not_applicable
review: passed
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, .stage/state/observations/O-00000050.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000311 범위 넘음 알림에서 고치지 않은 경로를 뺀다

## Purpose

범위 넘음 알림 한 줄이 실제로 범위 밖 프로젝트 파일을 고친 경우에만 떠서 사람과 에이전트가 진짜 넘음을 가려낼 수 있게 한다

## Actions

- 지금 동작(O-00000050, 2026-11-01 재현): `purpose_tool_context` 가 Edit·Write 에 `transcript_path` 를,
  `cp … "$TMPDIR/x"` 에 `$TMPDIR/x` 를, `> /dev/null` 에 `/dev/null` 을, `> /tmp/foo.txt` 에 `/tmp/foo.txt` 를 넘은 경로로 낸다.
- 원인 셋: `collect_explicit_paths` 가 `tool_input` 이 아니라 페이로드 전체를 훑어 최상위 `transcript_path` 를 줍는다.
  셸 변수를 펼치지 않은 대상이 작업 폴더 밑 상대 경로가 된다. 장치 파일과 OS 임시 폴더도 범위 밖으로 센다.
- `collect_explicit_paths` 는 `tool_input` 만 본다. 범위 넘음 보고에서만 장치 파일(`/dev/…`, Windows `NUL`)과 OS 임시
  폴더(`tempfile.gettempdir()`, `$TMPDIR`)를 빼고, 앞에 붙은 셸 변수는 훅 환경에 값이 있을 때 펼쳐서 판단한다. `.stage`
  쓰기 게이트는 바꾸지 않는다. O-00000050 을 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- Edit·Write 호출의 세션 transcript 경로, 출력을 버리는 /dev/null, OS 임시 폴더 안 경로, 환경에서 펼칠 수 있는 셸 변수로 시작하는 임시 경로가 범위 넘음으로 알려지지 않는다는 것을 테스트가 확인한다
- 범위 밖 프로젝트 파일과 작업 폴더 밖의 다른 경로는 여전히 범위 넘음으로 알려지고, .stage 쓰기를 막는 게이트는 그대로라는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: Attempt one made collect_explicit_paths() read only the tool input, expanded a leading shell variable in scope targets when the hook environment defines it, and left devices and OS-temporary-folder files outside the workspace out of the scope report, with tests, hooks.md, the CHANGELOG line, and O-00000050 closed; attempt two makes scratch_target() resolve relative targets against the workspace root instead of the process cwd, and adds a test that moves the process into a temporary folder and still expects the out-of-scope project file to be reported.
Why: W-00000311 - the scope-crossing line must appear only when a call really changes a path outside its card's scope, whatever directory the hook runs from.
Decisions made: Apply the device and temporary-folder exclusions to the report only, not to the .stage gates; keep reporting other paths outside the workspace and unexpandable variable targets; read targets from tool_input only; never treat a path inside the workspace as scratch, and resolve relative targets in the workspace, because the hook's cwd is not the workspace in a driver, a worktree, or a close run; out-of-scope paths changed: none.
Work not done: None
```

## Verification

2026-11-01 클라우드 세션에서 코드 커밋 `84894387`·`b05185fe` 의 worktree(마지막 커밋) 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 262 tests in 1.403s

OK (skipped=1)

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 397 tests in 5.676s

OK (skipped=1)

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793463798
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793463798. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp3irco_z7/unattended/W-00000001-1793463798
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
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
Ran 728 tests in 153.805s

OK (skipped=2)
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000311.md
Criteria:
- PASS: Edit·Write 호출의 세션 transcript 경로, 출력을 버리는 /dev/null, OS 임시 폴더 안 경로, 환경에서 펼칠 수 있는 셸 변수로 시작하는 임시 경로가 범위 넘음으로 알려지지 않는다는 것을 테스트가 확인한다
  Reason: test_scope_report_leaves_out_paths_the_call_does_not_change asserts an empty scope message for an Edit and a Write with transcript_path, '> /dev/null', cp into a TemporaryDirectory, and cp to "$STAGE_TEST_SCRATCH/..." with the variable set; collect_explicit_paths now reads only tool_input, and scratch_target plus expand_leading_shell_variable implement this; 262 tests pass.
- PASS: 범위 밖 프로젝트 파일과 작업 폴더 밖의 다른 경로는 여전히 범위 넘음으로 알려지고, .stage 쓰기를 막는 게이트는 그대로라는 것을 테스트가 확인한다
  Reason: test_scope_report_still_names_real_crossings checks src/app.py beside a transcript, a variable that expands into the project, an unexpandable variable, and a non-temp path outside the workspace; the cwd test checks relative targets resolve in the workspace; test_stage_gate_still_reads_the_tool_input_beside_a_transcript_path and the existing gate tests still deny .stage writes; the full hooks suite (397 tests) passes.
```

## Retrospective


## Promotion decision
