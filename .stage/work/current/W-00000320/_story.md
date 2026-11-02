---
id: W-00000320
title: Ubuntu 러너에서 Python 3.9 시험이 계속 돌게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000320
promotion: not_applicable
review: passed
scope: .github/workflows/stage.yml, .github/workflows/avatar.yml, .github/workflows/plainly.yml, stage/scripts/tests/test_ci_workflows.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000320 Ubuntu 러너에서 Python 3.9 시험이 계속 돌게 한다

## Purpose

Python 3.9 를 받치겠다는 Stage·Avatar·Plainly 의 약속을 Ubuntu 에서도 CI 가 계속 확인하게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 세 워크플로가 Ubuntu 의 Python 3.9 조합만 ubuntu-24.04 에서 돌리고, 나머지 조합(macOS·Windows 의 3.9, 모든 OS 의 3.12)은 그대로라는 것을 시험이 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-02

```
What changed: the stage, avatar, and plainly workflows exclude the ubuntu-latest and Python 3.9 combination and include ubuntu-24.04 with Python 3.9, leaving macOS and Windows 3.9 and every 3.12 job unchanged; stage/scripts/tests/test_ci_workflows.py expands each workflow's os and Python matrix with its exclude and include entries and pins the six expected combinations; the Stage CHANGELOG has a line; the card's scope gained stage/CHANGELOG.md in its own commit.
Why: W-00000320 - CI must keep checking the Python 3.9 support these plugins promise, on Ubuntu as well.
Decisions made: Move only the Ubuntu 3.9 job to the previous LTS image instead of dropping Python 3.9, because dropping it would silently retract a documented support promise; keep ubuntu-latest for 3.12 so the newest image stays covered; parse the matrix with the standard library so the test needs no YAML dependency; out-of-scope paths changed: none.
Work not done: Whether ubuntu-24.04 still offers Python 3.9 can only be confirmed by CI on the pull request.
```

## Verification

2026-11-02 클라우드 세션에서 코드 커밋 `12c78436` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.


### Executed at close — 2026-11-02

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q
[exit 0]
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793660099
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793660099. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp9sraf7i_/unattended/W-00000001-1793660099
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
Ran 736 tests in 152.806s

OK (skipped=2)
```

### Review at close — 2026-11-02

```
Review report: .stage/.runtime/driver/logs/W-00000320.md
Criteria:
- PASS: 세 워크플로가 Ubuntu 의 Python 3.9 조합만 ubuntu-24.04 에서 돌리고, 나머지 조합(macOS·Windows 의 3.9, 모든 OS 의 3.12)은 그대로라는 것을 시험이 확인한다
  Reason: stage.yml, avatar.yml, plainly.yml each exclude ubuntu-latest/3.9 and include ubuntu-24.04/3.9 with the original os and python lists untouched; test_ci_workflows.py expands each matrix with exclude/include and asserts exactly the six expected combinations, so restoring ubuntu-latest/3.9 or dropping any other combination would fail; I ran python3 -m unittest discover -s stage/scripts/tests -p test_ci_workflows.py -q and it showed Ran 1 test, OK; the executor's Decisions made (move only Ubuntu 3.9 to the previous LTS, stdlib parsing, no out-of-scope paths) and Work not done (runner availability confirmable only on PR CI) match the purpose, and the changed paths all lie within the card scope.
```

## Retrospective


## Promotion decision
