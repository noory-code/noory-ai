---
id: W-00000309
title: Claude 리뷰어의 파일 쓰기 제한을 실제 리뷰 경로에서 검증합니다
kind: qa
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000309
promotion: not_applicable
review: passed
scope: stage/scripts/claude_review_companion.py, stage/scripts/tests/, .stage/settings.json, stage/operations/cloud-execution.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000309 Claude 리뷰어의 파일 쓰기 제한을 실제 리뷰 경로에서 검증합니다

## Purpose

Claude 리뷰어가 판정 파일 밖에 쓸 수 있는지 실제 실행으로 확인하고 제한을 검증할 수 있게 합니다

## Actions
현재 권한 설정을 그대로 사용하는 두 리뷰 경로에서 파일 쓰기 fixture를 실행하고, 회귀를 잡는 검사를 남깁니다. 명령 인자 검사와 실제 파일 변경 검사를 구분합니다.

## User value
리뷰가 제품 파일을 바꾸지 않는다는 설명을 실행 결과로 확인할 수 있습니다.

## Scope

### Included
- 프로젝트 Claude 리뷰 명령과 cloud 대역 경로 두 곳에서 실제 프로세스를 실행합니다.
- import·setUp·테스트 본문 세 곳에서 판정 파일 밖의 생성·수정을 시도하고 실행 전후 파일을 비교합니다.
- 판정 파일 쓰기와 정상 테스트가 계속 동작하는지도 확인합니다. 쓰기 제한이 없으면 검사가 실패해야 합니다.
- 결과에는 CLI 버전, 사용한 권한 설정, 실행 명령, 종료 코드, 파일 변경 여부를 남깁니다. 실제 리뷰를 실행하지 못했다면 그 검증을 미완료로 표시합니다.

### Excluded
- 이번 등록에서는 구현하거나 리뷰 정책을 바꾸지 않습니다.
- 같은 모델 계열의 cloud 리뷰를 허용하는 정책 전체를 재설계하지 않습니다.

## Risks
W-00000299는 W-00000295의 argv 검사가 자식 프로세스의 쓰기까지 증명하지 못한다고 판정했습니다. 2026-11-01 현재 프로젝트 설정과 대역 모두 `Bash(python3 -m unittest:*)`를 허용합니다. 임시 폴더에서 같은 종류의 명령을 실행했을 때 테스트 한 개가 통과하면서 판정 파일이 아닌 파일을 만들었습니다. 이 재현은 실제 Claude의 권한 승인 동작까지 검증한 결과는 아닙니다.

영향을 확인한 곳은 다음과 같습니다.

| 구분 | 수 | 확인할 동작 |
|---|---:|---|
| 진입 경로 | 2곳 | 프로젝트 review.reviewers.claude와 claude_review_companion의 실제 실행 |
| 실행 상태 | 3가지 | 정상 판정, 다른 파일 쓰기 시도, 실패·중단 뒤 변경 보존 여부 |
| 기존 책임 | 2가지 | 판정 JSON 기록과 unittest 실행을 계속 허용해야 함 |
| 증거와 실패 | 3곳 | test_environment_venues.py, test_template_v4.py, 리뷰 로그·파일 비교 결과 |

쓰기 범위를 바꿀 때는 캐시와 결과 폴더도 구분해야 합니다. `stage/operations/cloud-execution.md`와 템플릿 권한 안내도 영향을 받는지 확인하고, 필요하면 범위 밖 변경으로 보고합니다. W-00000299의 표본 카드와 제품 소스는 이번 등록에서 수정하지 않습니다.

## Success criteria

- 프로젝트 Claude 리뷰 명령과 cloud 대역 리뷰 경로를 각각 실행해 판정 파일 이외의 파일 쓰기를 검사하고 재현 가능한 결과를 남깁니다
- unittest 모듈의 import·setUp·테스트 본문에서 쓰는 경우까지 검사하여 argv 검사만으로 쓰기 제한을 통과시키지 않습니다
- 허용한 판정 파일 쓰기와 정상 리뷰·테스트는 동작하며 다른 파일의 생성·수정 시도는 차단되거나 명확한 검증 실패로 드러납니다

## Next action

사용자가 요청한 계획 카드입니다. milestone은 연결하지 않았습니다. 실행 세션은 W-00000299의 후속 항목과 W-00000295의 기존 테스트를 읽고, 실제 리뷰 경로에서 재현하는 실패 검사부터 작성합니다. Included의 경로별 실행·쓰기 시도는 성공 기준 1·2가, 정상 동작과 실패 표시는 성공 기준 3이 검증합니다.

## Related truth

## Progress

2026-11-01 클라우드 세션에서 실제 `claude` 로 쟀다. CLI `2.1.316 (Claude Code)`, 권한 설정은 두 경로 모두
`Edit(//<판정 파일>)` 과 `Bash(python3 -m unittest:*)` 다.

고치기 전(대역 경로, 임시 저장소). 직접 쓰기는 막히고, 시험 코드의 쓰기는 다 통과했다.

| 시도 | 결과 |
|---|---|
| Write 도구로 새 파일 | 거부 |
| `echo hi > bash-write.txt` | 거부 |
| `python3 -m unittest ... && touch chained.txt` | 명령 전체 거부 |
| `python3 -m unittest discover -s tests -q` | 허용. import·setUp·본문에서 파일 셋을 만들고 추적 파일 하나를 고쳤다 |
| 판정 파일 쓰기 | 허용 |

고친 뒤(`stage/scripts/tests/test_claude_review_guard.py` 의 `LiveReviewerWriteProbeTest`,
`STAGE_LIVE_REVIEW_PROBE=1` 일 때만 돈다). 두 경로 모두 시험 본문이 `tracked.txt` 를 고쳤다.

| 경로 | 명령 | 종료 코드 | 남은 변경 | 판정 파일 |
|---|---|---:|---|---|
| cloud 대역 | `python3 stage/scripts/claude_review_companion.py "<시도 프롬프트>"` | 3 | ` M tracked.txt` (직접 쓰기 셋은 없음) | 지워짐 |
| 프로젝트 `review.reviewers.claude` | `OUT=$(STAGE_CLAUDE_REVIEW_MODEL='opus[1m]' python3 stage/scripts/claude_review_companion.py "<프로젝트 리뷰 프롬프트>" 2>&1); ...` | 3 | ` M tracked.txt` | 지워짐, 로그에 경로가 남음 |

프로젝트 경로의 첫 두 판은 시험 준비가 잘못되어 무효다. 카드와 로그를 프로젝트 밖에 두어 리뷰어가 읽지 못했고,
복사한 파일을 커밋하지 않았다. 실제 위치(`.stage/work/…`, `.stage/.runtime/driver/logs/…`)로 옮겨 다시 쟀다.

### Executor report at close — 2026-10-31

```
What changed: claude_review_companion.py snapshots the repository (tracked files plus untracked non-ignored ones, via driver_repository) before and after the claude run, and when anything other than the verdict file changed it removes the verdict, reports the paths on stdout and stderr, leaves the files in place, and exits 3 (REVIEW_WROTE_FILES); a failed snapshot before the run refuses to review and one after it removes the verdict; the project's review.reviewers.claude command now runs through the companion with STAGE_CLAUDE_REVIEW_MODEL='opus[1m]' instead of its own claude -p arguments; test_claude_review_guard.py drives main() with a stand-in reviewer that runs a real unittest process writing at import, setUp, or test-body time, checks a clean review keeps its verdict and exit status and that an unignored verdict file is not a violation, pins the project command, and has a live probe of both paths that runs only with STAGE_LIVE_REVIEW_PROBE=1; test_template_v4 pins the reviewer model through the environment variable and compares the verdict rule with the resolved path; cloud-execution.md and the CHANGELOG describe the check.
Why: W-00000309 - prove by real runs whether the Claude reviewer can write outside its verdict file, and make such writes fail the review instead of passing an argv-only check.
Decisions made: Detect writes by comparing repository snapshots rather than sandboxing the process, because a sandbox is not available on every host Stage supports (Windows) and the permission rules already stop the reviewer's direct writes; remove the verdict and exit non-zero so both close_work and the driver see a failed review; leave changed files in place rather than reverting them, because a revert could discard a person's edits; route the project Claude reviewer through the companion so both review paths share one permission set and one check (SSOT), keeping the model pin explicit in the command through STAGE_CLAUDE_REVIEW_MODEL; ignored paths such as __pycache__ and .stage/.runtime are outside the check, matching the driver's snapshot view; out-of-scope paths changed: none.
Work not done: The Codex reviewer and the review strengths are not covered by this check, and the v4 template's Claude reviewer command in stage/templates still calls claude -p directly, so other projects stay unguarded until a follow-up card; a review killed before the companion's second snapshot leaves no check.
```

## Verification

2026-11-01 클라우드 세션에서 코드 커밋 `6a5b050d` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다. 이 카드가 넣은 쓰기 검사가 이
리뷰에도 걸렸다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 1.683s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793461138
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793461138. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpjagi0rh0/unattended/W-00000001-1793461138
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
Ran 725 tests in 154.374s

OK (skipped=2)
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000309.md
Criteria:
- PASS: 프로젝트 Claude 리뷰 명령과 cloud 대역 리뷰 경로를 각각 실행해 판정 파일 이외의 파일 쓰기를 검사하고 재현 가능한 결과를 남깁니다
  Reason: Progress records real claude 2.1.316 runs of both paths with permission rules, commands, exit codes (3), residual changes, and verdict state; LiveReviewerWriteProbeTest reproduces both paths under STAGE_LIVE_REVIEW_PROBE=1, and the two invalid project-path attempts are disclosed.
- PASS: unittest 모듈의 import·setUp·테스트 본문에서 쓰는 경우까지 검사하여 argv 검사만으로 쓰기 제한을 통과시키지 않습니다
  Reason: test_claude_review_guard.py runs a real unittest subprocess that writes at import, setUp, and test-body time and asserts exit 3, verdict removal, and the named path; the companion now checks repository snapshots instead of relying on argv rules; tests pass locally.
- PASS: 허용한 판정 파일 쓰기와 정상 리뷰·테스트는 동작하며 다른 파일의 생성·수정 시도는 차단되거나 명확한 검증 실패로 드러납니다
  Reason: Clean reviews keep the verdict and exit status (0 and 5) and an unignored verdict file is not flagged, while non-verdict writes fail with exit 3 and a stdout/stderr report; ignored-path and Codex/template gaps are disclosed in Decisions made and Work not done, and all changed paths are within the card scope.
```

## Retrospective

## Promotion decision
