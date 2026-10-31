---
id: W-00000310
title: 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_claude_review_guard.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000310
promotion: not_applicable
review: passed
scope: stage/scripts/driver_supervised.py, stage/scripts/driver_unattended.py, stage/scripts/driver_review.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/claude_review_companion.py, stage/templates/v4/project-stage/settings.jsonc, stage/scripts/tests/, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000310 모든 리뷰어에 판정 파일 밖 쓰기 검사를 건다

## Purpose

Codex 리뷰어나 다른 프로젝트의 Claude 리뷰어가 돌린 시험 코드가 저장소를 바꿔도 그 리뷰가 승인으로 끝나지 않게 한다

## Actions

- W-00000309 가 `stage/scripts/claude_review_companion.py` 에 넣은 앞뒤 스냅숏 비교(`driver_repository.repository_path_snapshot`)를
  리뷰어 명령을 부르는 자리(감독·무인 드라이버, `close_work.py`)로 옮겨 모든 리뷰어에 건다. 대역의 검사는 그 공통 검사로
  대체해 한 곳만 남긴다(SSOT).
- v4 템플릿(`stage/templates/v4/project-stage/settings.jsonc`)의 Claude 리뷰 명령이 공통 검사를 받게 한다.

## User value


## Scope

### Included


### Excluded


## Risks

- 리뷰 중에 사람이 같은 체크아웃을 만지면 그 변경도 리뷰 실패로 잡힌다(O-00000013 과 같은 모양). 실패 메시지가 그
  가능성을 알려야 한다.
- 실측 근거: W-00000309 의 Progress. `python3 -m unittest` 가 돌린 시험 코드는 권한 규칙과 상관없이 썼다.


## Success criteria

- 드라이버와 close_work 가 어느 리뷰어 명령이든 앞뒤 저장소를 비교해 판정 파일 밖이 바뀌면 리뷰를 실패로 기록하고 바뀐 경로를 알린다는 것을 테스트가 확인한다
- v4 템플릿의 Claude 리뷰 명령이 같은 검사를 받는다는 것을 테스트가 확인한다

## Next action

## Related truth

## Progress

2026-11-01 클라우드 세션. 검사를 대역(`claude_review_companion.py`)에서 `close_work.run_close_review` /
`reject_review_writes` 와 감독 드라이버로 옮겼다. 무인 드라이버는 리뷰를 `close_work` 로 돌리므로 따로 고칠 것이 없다.
v4 템플릿의 `reviewers.claude` 는 빈 값이고 프로젝트가 직접 채운다. 검사가 명령 바깥에 있으니 어떤 명령이든
걸리며, 템플릿에는 그 사실을 안내 주석으로 적었다.

실측(`LiveReviewerWriteProbeTest`, CLI `2.1.316 (Claude Code)`, 권한은 두 경로 모두 `Edit(//<판정 파일>)` 과
`Bash(python3 -m unittest:*)`)으로 `close_work.run_close_review` 를 거쳐 확인했다.

| 경로 | 시험 실행 | 통과 | 남은 변경 | 판정 파일 |
|---|---|---|---|---|
| cloud 대역 | 했다 | 아니오 | ` M tracked.txt` (직접 쓰기 셋은 없음) | 지워짐 |
| 프로젝트 `reviewers.claude` 1판 | 안 했다 | 예 | 없음 | 남음 — 검사가 걸릴 일이 없던 판 |
| 프로젝트 `reviewers.claude` 2판 | 했다 | 아니오 | ` M tracked.txt` | 지워짐 |

프로젝트 경로 1판에서 리뷰어는 "직접 돌려서 통과한다"는 기준을 시험을 돌리지 않고 통과시켰다. 시험을 돌릴지는
모델이 고르므로, 실측 시험은 시험이 돌지 않은 판을 미완료로 기록하고 건너뛰게 했다.

### Executor report at close — 2026-10-31

```
What changed: close_work.py gains reject_review_writes(), which compares two driver_repository snapshots, ignores the verdict file, removes the verdict and names the changed paths when anything else changed, and run_close_review(), which both close review branches (autonomous independent review and pending review) now share and which snapshots around the review command, removing the verdict if the second snapshot fails; the supervised driver snapshots before its reviewer, applies reject_review_writes() after it, skips the narrow merge on a write failure, and counts it as a real failed attempt rather than an infrastructure retry; the unattended driver reviews through close_work, so it is covered unchanged; claude_review_companion.py is a thin wrapper again and its docstring points at the shared check; the v4 template's review comment says review commands are checked; test_claude_review_guard.py now drives run_close_review with an arbitrary reviewer command that runs a real unittest process writing at import, setUp, or test-body time, checks clean and failing reviews and an unignored verdict file, checks the template note, and its live probe goes through run_close_review and records an unexercised run as inconclusive; test_drive.py checks that a reviewer writing a file fails the supervised round, removes the verdict, keeps the file, and spends one attempt; cloud-execution.md and the CHANGELOG entry are rewritten for the new location.
Why: W-00000310 - a review command that alters the repository, whichever reviewer runs it, must end as a failed review that names what changed.
Decisions made: Put the check in close_work.py rather than driver_review.py or driver_repository.py, because driver_review imports close_work (a cycle) and driver_repository is outside the card scope, while both drivers already import from close_work; remove the companion's own check so one implementation remains (SSOT); leave the template's empty reviewers.claude alone and document the check, since the check is outside the command and covers whatever a project writes; treat a write as a real failed attempt, not a free infrastructure retry; changed files stay in place and the message says that a person's edits during the review count too; driver_unattended.py and driver_review.py needed no change; out-of-scope paths changed: none.
Work not done: A reviewer killed before the second snapshot is not checked; files a failed review leaves inside the card scope can still be included by the driver's next item commit if the person does not discard them, as the message tells them to.
```

## Verification

2026-11-01 클라우드 세션에서 코드 커밋 `55f42715` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다. 이 리뷰도 이 카드가 넣은
`close_work` 쓰기 검사를 거쳤다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_claude_review_guard.py -q
[exit 0]
----------------------------------------------------------------------
Ran 8 tests in 1.354s

OK (skipped=2)

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793462111
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793462111. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpcklfiww5/unattended/W-00000001-1793462111
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
Ran 728 tests in 153.959s

OK (skipped=2)
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000310.md
Criteria:
- PASS: 드라이버와 close_work 가 어느 리뷰어 명령이든 앞뒤 저장소를 비교해 판정 파일 밖이 바뀌면 리뷰를 실패로 기록하고 바뀐 경로를 알린다는 것을 테스트가 확인한다
  Reason: close_work.run_close_review snapshots around any command and reject_review_writes removes the verdict and names paths; CloseReviewWriteGuardTest drives arbitrary commands writing at import/setUp/test time, and the new test_drive supervised test asserts failure, the path message, the removed verdict and one spent attempt; unattended reviews go through close_work; both pass locally.
- PASS: v4 템플릿의 Claude 리뷰 명령이 같은 검사를 받는다는 것을 테스트가 확인한다
  Reason: The template's reviewers.claude is empty and project-filled, the check sits outside the command in run_close_review so any filled command is covered, and ProjectReviewerCommandTest asserts the template note that every review command is compared and failed on writes; the executor report states this decision, the unchanged files, no out-of-scope paths, and the residual gaps.
```

## Retrospective

## Promotion decision
