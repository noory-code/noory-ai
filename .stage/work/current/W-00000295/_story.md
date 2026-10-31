---
id: W-00000295
title: claude 리뷰어에게 판정 파일 쓰기와 시험 실행만 허락한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
  - "python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000295
promotion: not_applicable
review: passed
scope: .stage/settings.json, stage/scripts/claude_review_companion.py, stage/scripts/tests/test_environment_venues.py, stage/scripts/tests/test_template_v4.py, stage/templates/v4/project-stage/settings.jsonc, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000295 claude 리뷰어에게 판정 파일 쓰기와 시험 실행만 허락한다

## Purpose

비대화형 claude 리뷰어가 사용자 권한 설정에 기대지 않고 판정 파일을 쓰고 시험을 돌리되 다른 파일은 고치지 못하게 한다.

## Actions

- 지금 동작: 이 프로젝트의 `reviewers.claude` 명령은 `claude -p` 를 권한 옵션 없이 띄운다. 비대화형 세션은
  `$STAGE_REVIEW_VERDICT_FILE` 을 쓰지도, 프로젝트 밖의 `$STAGE_CHANGED_PATHS_FILE` 을 읽지도, 시험을 돌리지도
  못한다(W-00000287 닫기에서 확인). 로컬에서는 사용자 권한 설정에 기대 왔을 가능성이 크다. 대역 리뷰어
  `claude_review_companion.py` 는 `--permission-mode acceptEdits` 로 프로젝트 파일 전체 편집을 허락한다.
- 둘 다 `--add-dir <변경 경로 파일 폴더>`, `--allowedTools "Write(/$STAGE_REVIEW_VERDICT_FILE)"
  "Edit(/$STAGE_REVIEW_VERDICT_FILE)" "Bash(python3 -m unittest:*)"` 로 바꾼다. 드라이버의 좁은 재리뷰는 판정
  파일을 임시 폴더에 두므로 폴더가 아니라 파일 하나를 허락한다.
- 2026-10-31 이 세션에서 `claude -p` 로 실험해, 판정 파일 쓰기와 바깥 폴더 읽기와 unittest 실행은 되고 같은
  폴더의 다른 파일과 프로젝트 파일 쓰기는 막히는 것을 확인했다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일 하나에만 쓰기를, 변경 경로 파일 폴더에 읽기를, unittest 실행만을 허락하고 프로젝트 파일 편집 권한을 주지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: The project's reviewers.claude command and stage/scripts/claude_review_companion.py now pass --add-dir with the folder of $STAGE_CHANGED_PATHS_FILE, --allowedTools with Write and Edit rules for the absolute path of $STAGE_REVIEW_VERDICT_FILE plus Bash(python3 -m unittest:*), and -- before the prompt, instead of no flags or --permission-mode acceptEdits; the stand-in refuses to run without STAGE_REVIEW_VERDICT_FILE; the settings template explains these flags without backticks; the cloud procedure describes the narrower stand-in; tests check the stand-in's exact command and run the real project reviewer command in a shell with a fake claude that records its arguments.
Why: W-00000295 - a reviewer must be able to write its verdict and run tests without relying on user-level permission rules, and must not be able to edit the work it judges.
Decisions made: Allow the single verdict file rather than the verdicts folder, because the driver's narrow re-review writes its verdict into a temporary folder; use a leading // to make the rule absolute and -- to end the variadic --add-dir and --allowedTools before the prompt; allow only `python3 -m unittest` for Bash so the reviewer can verify tests without a general shell; base all three on a 2026-10-31 experiment in this session where the verdict write, the outside read, and the unittest run succeeded while another file in the same folder and a project file were blocked.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `639f2b6b` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 이 카드가 권한을 좁힌 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의
`implementation` 리뷰 명령을 설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 1.682s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_template_v4.py -q
[exit 0]
----------------------------------------------------------------------
Ran 24 tests in 0.048s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793451402
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793451402. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpog3pjy7o/unattended/W-00000001-1793451402
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
Ran 704 tests in 129.399s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000295.md
Criteria:
- PASS: 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일 하나에만 쓰기를, 변경 경로 파일 폴더에 읽기를, unittest 실행만을 허락하고 프로젝트 파일 편집 권한을 주지 않는다는 것을 테스트가 확인한다
  Reason: test_environment_venues pins the stand-in's exact argv (--add-dir changed-path folder, --allowedTools Write/Edit for the absolute verdict path plus Bash(python3 -m unittest:*), --, no acceptEdits or --permission-mode) and test_template_v4 runs the real .stage/settings.json claude command through a fake claude asserting the same argv; both suites pass, the shell test would fail on the old flagless command, and the executor report's Decisions made and Work not done fields are filled and consistent with the card scope.
```

## Retrospective

[R-00000295](../../retrospectives/R-00000295.md).

## Promotion decision
