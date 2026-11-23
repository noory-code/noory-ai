---
id: W-00000416
title: 닫기 리뷰어가 저장소 밖을 읽거나 고친 것을 되돌려 숨기지 못한다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000416
promotion: not_applicable
review: passed
scope: stage/scripts/claude_review_companion.py,stage/scripts/run_review.py,stage/scripts/tests,stage/skills/stage-retrospective,stage/operations/review.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000416 닫기 리뷰어가 저장소 밖을 읽거나 고친 것을 되돌려 숨기지 못한다

## Purpose

리뷰어에게 셸을 열어 준 뒤에도, 리뷰어가 프로젝트 파일을 고쳤다가 되돌리거나 저장소 밖의 기록을 읽어 판정에 쓰는 일이 닫기에서 드러난다 (DE-00000101, W-00000414)

## Actions


## User value


## Scope

### Included


### Excluded

- 리뷰어를 다른 venue(codex)나 검증 세션에 견주는 일.
- 리뷰어의 셸 권한을 다시 좁히는 일. DE-00000101 이 넓히기로 했다. 좁혀야만 기준을 채울 수 있으면 그렇다고 보고한다.


## Risks


## Success criteria

- 리뷰어가 추적되는 파일을 고친 뒤 git checkout 이나 git restore 로 되돌려도 닫기가 그 리뷰를 실패시킨다
- 리뷰어가 git 이 무시하는 파일에 쓴 것도 닫기의 앞뒤 비교에 걸린다
- 리뷰어가 세션 기록 폴더(~/.claude)와 GitHub API 를 읽지 못하거나, 읽으면 닫기가 그것을 알린다
- 막은 것과 여전히 막지 못하는 것이 리뷰 절차 문서에 적혀 있다

## Next action

없음. 닫고 보관한 뒤 병합한다.


## Related truth

- W-00000413 의 실제 리뷰어 탐침: 리뷰어가 시험이 쓴 파일을 보고 스스로 `git checkout -- tracked.txt` 로 되돌리고 `__pycache__` 를 지웠다. 트리를 되돌린 리뷰어는 앞뒤 비교를 통과한다.
- W-00000414 의 재기(`.stage/research/review-judgment/measurement.md`, `runs/`): 리뷰어가 GitHub API 로 PR 의 지금 상태를 한 번, 이 컨테이너의 `~/.claude/projects/` 세션 기록을 두 번 읽었다. 무시되는 파일과 저장소 밖 파일에 쓰는 시험 코드는 걸리지 않는다(W-00000309 의 기준 3).
- W-00000408 이 넣은 거부 규칙은 접두어 규칙이라 `sh -c` 나 스크립트 안의 명령은 보지 못한다.
- 사용자가 2026-11-23 에 실기기에서 해야 할 일만 두고 나머지를 진행하라고 했다("실기기에서 해야할 일은 두고 나머지는 합시다"). 목적과 성공 기준은 지휘 세션이 옮겨 적었다.


## Sessions

- session_018VXR6QdPTqWEDctnhbFeWu — work — 2026-11-23 — opened from the index: DE-00000101


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 2401aebb 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6QdPTqWEDctnhbFeWu (`claude/w416-contain-reviewer`)를 띄웠다. 번호 묶음은 잡지 않았다.


- 2026-11-23 작업 세션 session_018VXR6QdPTqWEDctnhbFeWu 가 263cdf04 를 보고했다. 성공 기준 1-4 를 주장했다. 실제 리뷰어를 돌려 `ls ~/.claude/projects` 와 고쳤다가 되돌리는 명령을 실행한 리뷰가 실패하고 경고가 나오는 것을 보았다고 보고했다. 지휘 세션이 squash 커밋에서 scripts 1023, hooks 489 통과와 audit 오류 0 을 다시 확인했다. 범위 밖 변경은 `stage/operations/cloud-execution.md` 한 곳이다.
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: 무시되는 파일의 쓰기와 저장소 밖 읽기는 실패가 아니라 경고다. 읽기는 막지 않는다. DE-00000087 이 요구하는 카드별 사용자 확인은 받지 않았다(O-00000062).
- Follow-up candidate: 리뷰어의 저장소 밖 읽기를 막는다(셸을 좁히거나 리뷰어에게 따로 된 홈 폴더를 준다).
- Follow-up candidate: 템플릿 설정의 주석이 대역이 만드는 명령을 옛 인자로 적고 있다.
- Follow-up candidate: 드라이버의 회차 사이 리뷰에도 되돌리기 검사와 흔적을 넣는다. 프로젝트와 템플릿의 리뷰 명령에도 같은 규칙을 적어 Codex 리뷰어도 받게 한다.
- Follow-up candidate: 아직 보지 못하는 것: `git fetch`, `.git` 과 `.stage/.runtime/` 안의 변경, 스크립트 파일에 숨은 읽기, 수정 시각까지 되돌리는 Windows 의 복원.

### Executor report at close — 2026-11-23

```
What changed: New module stage/skills/stage-retrospective/review_containment.py: review_snapshot() adds, to the content snapshot the drivers use, each tracked and untracked file's inode, modified time and change time, and each Git-ignored file's mode, size and modified time (without .stage/.runtime/); reject_restored_files() removes the verdict and fails the review when a file has its earlier content and a different identity or times; review_traces() collects ignored files that were written, created or deleted and the reviewer tool calls whose text names the session record folder (~/.claude, $HOME/.claude, the home folder's absolute path in POSIX, Windows and Git Bash spelling, $CLAUDE_CONFIG_DIR) or GitHub (gh <subcommand>, api.github.com). close_work.run_close_review() uses that snapshot, sets STAGE_REVIEW_TOOL_CALLS_FILE in the reviewer's environment, reports a changed file and a restored file together, prints each trace as "<id>: WARNING ...", and hands the traces to main(), which writes "- Reviewer traces at close <date>: ..." after the review line on a passed and on a rejected review. claude_review_companion.py runs claude with --output-format stream-json --verbose, prints the result event's text as the answer, appends each tool call to the record file as it is seen and ends it with a line naming the calls the host refused, and adds REVIEWER_RULES to every prompt (leave a changed file and name it, do not restore, do not read ~/.claude or GitHub). New tests in test_review_containment.py; test_environment_venues.py and test_template_v4.py pin the new arguments. operations/review.md gains "What the close sees of the reviewer" with what fails, what is told, and what is still not seen; BLUEPRINT.md lists the module and the behavior; cloud-execution.md's table and CHANGELOG.md follow.
Why: The card's four success criteria: a tracked file changed and then restored with git checkout or git restore fails the close review; a write to an ignored file is caught by the comparison; a read of ~/.claude or the GitHub API is reported by the close; and what is held and what is not is written in the review procedure (DE-00000101, W-00000413, W-00000414).
Decisions made: (1) A write to an ignored file and a command naming an outside record do NOT fail the review; they are printed as a WARNING and written on the card. Failing on ignored files would fail every review whose commands write a cache (__pycache__, .pytest_cache, Flutter build output): the two Stage suites alone wrote 33 ignored .pyc files in a measured run. Failing on a text match would fail a review that only searches the project for the string. The other choice, failing both, is a few lines in run_close_review; the main session or the user may prefer it for criterion 2. (2) The reads are named, not stopped. Stopping them needs the shell narrowed (an OS sandbox, or a separate home folder that takes the reviewer's credentials), which the card excludes; no new deny rule was added, because denying gh alone made the measured reviewer switch to curl. (3) A restore is detected through file identity and times, so anything else that rewrites a repository file during a review fails it too; a measured run of both Stage suites and audit_stage.py rewrote no tracked file. (4) Ignored files are compared by size and modified time and never read, so a large ignored tree costs one lstat per file. (5) The tool-call record is venue-neutral (one JSON object per line in the file STAGE_REVIEW_TOOL_CALLS_FILE names); only the Claude stand-in writes it, and a missing record prints nothing. (6) The stand-in appends the rules to the prompt instead of editing the project's and the template's review prompt, which are outside the scope; without the sentence a reviewer that tidies up, as W-00000413's did, costs a failed round. (7) The supervised driver's review between rounds still uses the content comparison only; its close goes through close_work.py. (8) Path changed outside the card's scope: stage/operations/cloud-execution.md, because its table said the comparison is the only check and that nothing is done about reads outside the repository; two rows were changed to match and point to review.md. (9) No record was created.
Work not done: Nothing was run on Windows or macOS; the pull request's CI jobs are that check, and the Windows-specific parts (st_ctime as creation time, PowerShell and %USERPROFILE% spellings) are covered by unit tests of the text matching only. stage/templates/v4/project-stage/settings.jsonc still says the stand-in "builds exactly this command" and lists the arguments without --output-format stream-json --verbose; it is outside the scope and was left. The supervised driver's between-round review was not given the restore check or the traces. Git reads of the remote (git fetch, git ls-remote), changes inside .git and .stage/.runtime/, and reads hidden in a script file are not seen; review.md lists them. Live runs with claude 2.1.330 on Linux: STAGE_LIVE_REVIEW_PROBE=1 python3 -m unittest -v test_claude_review_guard.LiveReviewerWriteProbeTest ran 2 tests, OK, both paths exercised (the project path was skipped as inconclusive before this change, because the reviewer restored the tree); one haiku run through run_close_review that ran `ls ~/.claude/projects` and `echo changed > tracked.txt && git checkout -- tracked.txt` was failed for the restored file and printed the warning naming the ls command. Checks run on Linux: python3 -m unittest discover -s stage/scripts/tests -q (1023 tests, OK, skipped=2), python3 -m unittest discover -s stage/hooks/tests -q (487 tests, OK, skipped=2), python3 stage/scripts/audit_stage.py (errors=0, warnings=32).
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다. 이 카드가 넣은 되돌리기 검사와 흔적 기록으로 도는 첫 리뷰다.

- Checks at close 2026-11-23: 1 passed — `python3 -m unittest discover -s stage/scripts/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS ran, 4 PASS read)
- Reviewer traces at close 2026-11-23: commands naming the session record folder (~/.claude) 2; commands naming GitHub 2
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
