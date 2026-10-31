---
id: W-00000287
title: 실행자가 정한 것을 닫을 때 카드에 남긴다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000287
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/skills/stage-drive/SKILL.md, stage/docs/SCHEMA_V4.md, stage/templates/v4/project-stage/settings.jsonc, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000078
---

# W-00000287 실행자가 정한 것을 닫을 때 카드에 남긴다

## Purpose

실행자가 스스로 정한 것과 하지 않은 일이 커밋되지 않는 작업 로그와 함께 사라지지 않고, 몇 달 뒤의 본인이 카드에서 읽을 수 있게 한다.

## Actions

- 지금 동작: 실행 보고는 `.stage/.runtime/driver/logs/<id>.md` 에만 있고 이 경로는 gitignore 대상이다.
  드라이버 커밋 메시지는 `driver: <id> executor output` 한 줄이다. 보관된 W-00000285 의 Progress 는
  커밋되지 않는 로그와 판정 파일을 가리킨다. 검증기 `executor_report_error()` 는 계약이 요구하는
  `Decisions made:`·`Work not done:` 을 검사하지 않는다.
- `close_work.py` 가 닫을 때 작업 로그의 마지막 `### Executor report` 에서 `What changed`, `Why`,
  `Decisions made`, `Work not done` 네 줄을 원문 그대로 카드의 `## Progress` 에 옮긴다. 로그에
  보고가 없으면(손으로 닫은 카드) 아무것도 옮기지 않고 닫기를 막지 않는다.
- 검증기가 `Decisions made:`·`Work not done:` 도 비어 있지 않은 한 줄로 요구한다(`None` 허용).
- 실행자 계약에 "마지막 판의 `Decisions made:` 는 그때까지 유효한 결정을 모두 다시 적는다"를 더한다.
  `stage/skills/stage-drive/SKILL.md`, `stage/docs/SCHEMA_V4.md`,
  `stage/templates/v4/project-stage/settings.jsonc` 실행 명령 안내가 같은 뜻으로 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

몇 달 손 뗐다가 돌아왔을 때, 다른 컴퓨터나 클라우드 체크아웃에서도 카드만 열면 실행자가 무엇을
왜 그렇게 정했는지 읽을 수 있다. "스스로 정한 것을 안 적으면 은폐다"(PHILOSOPHY)가 구조적으로
지켜진다.

## Scope

### Included

- 닫기의 실행 보고 이관, 검증기의 두 칸 요구, 실행자 계약 문장, 시험, 변경 기록 한 줄

### Excluded

- 실패한 판의 원재료 보존 — 회고가 소화한다(사용자 결정).
- 작업 로그를 커밋하는 일, 드라이버 커밋 메시지 본문을 채우는 일.
- `Executed at close` 출력 꼬리 40줄을 줄이는 일.

## Risks

- 판이 여럿이면 앞 판의 결정이 마지막 보고에서 빠질 수 있다. 누적 기재 계약과 리뷰어의
  `Decisions made` 판정으로 잡는다. 모든 판을 모으는 안은 되돌린 결정까지 남겨 기록이 사실과
  어긋나므로 고르지 않았다.
- 검증기를 엄격하게 하면 두 칸을 빠뜨리던 실행 명령이 시도 횟수를 쓴다. 계약 문서는 이미 두 칸을
  요구하고 있었다.

## Success criteria

- 드라이버로 닫은 카드의 Progress 에 승인된 마지막 판의 What changed, Why, Decisions made, Work not done 이 원문 그대로 남는다는 것을 테스트가 확인한다
- Decisions made 나 Work not done 이 빠진 실행 보고는 거절된다는 것을 테스트가 확인한다
- 실행자 계약이 마지막 판의 Decisions made 에 그때까지 유효한 결정을 모두 다시 적으라고 요구하고, 계약 문서 셋이 같은 뜻으로 적는다

## Next action

클라우드 세션이 DE-00000078 계약대로 고치고 `claude/w268-cloud` 에 push 한다. 로컬에서 범위 대조,
실행 보고를 작업 로그로 옮기기, 인수 명령과 scripts 전체 시험, codex 판정, 회고, 닫기를 한다.

## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: close_work.py copies the latest executor report's `What changed:`, `Why:`, `Decisions made:`, and `Work not done:` lines verbatim into the card's `## Progress` at close (fenced, fence-escaped); with no report it adds nothing, and with a report but no Progress section it refuses with the card unchanged. executor_report_error() now requires both judgment fields. The executor contract (stage-drive SKILL, SCHEMA_V4, settings.jsonc template, and this project's two executor prompts) asks every attempt to restate earlier decisions still in effect. The work-log preamble and operations/review.md state what the card now owns. Tests: the validator rejects each missing or empty field; close copies only the last report and none of the reviewer prose, changed paths, or review request; no report leaves Progress alone; a report without Progress refuses.
Why: W-00000287 - the card is the canonical home of executor decisions (user decision); failed attempts are digested by retrospectives.
Decisions made: Copy the last attempt only, with a cumulative-restatement contract, instead of collecting every attempt's decisions: collecting would keep decisions a later attempt reverted, so the record could contradict the code. Keep the copied lines in English, verbatim, inside a fenced block, matching the existing `Executed at close` evidence. Out of scope paths changed: `.stage/settings.json` (the project's real executor prompts; without it the cumulative rule would exist only in the template), `stage/operations/review.md` (its "What close writes on the card" section would otherwise be false), `stage/scripts/tests/test_template_v4.py` (pins the new prompt sentence in both prompts and the template), and `stage/scripts/tests/test_drive.py`, `test_drive_parallel.py`, `test_drive_unattended.py` (their executor fixtures lacked the two fields the validator now requires; each gained `None` values).
Work not done: None. Local: scope check against the card, move this report into the work log, verdict, retrospective, close.
```

## Verification

2026-10-31 클라우드 세션에서 닫았다. 이 세션에는 codex 가 없어, 사용자 지시("여기서는 코덱스가 하는 일을
니가 해야 한다")에 따라 이 프로젝트의 `reviewers.claude` 명령을 `implementation` 리뷰로 걸었다. 그
명령은 이 worktree 의 `.stage/settings.json` 에만 커밋하지 않고 덮어 썼다. 판정한 새 Claude 세션은
실행자와 맥락을 나누지 않지만 같은 모델 계열이므로 교차 venue 판정이 아니다. 리뷰가 받은 변경 경로는
W-00000287 코드 커밋 `3ce38592` 의 경로다. 실행 보고는 그 커밋 본문에서 작업 로그로 옮기며 칸마다
한 줄로 이었다.
scripts 전체 시험은 덮어 쓴 리뷰 명령이 `test_template_v4` 의 모델 고정 검사에 걸리므로, 같은 커밋을
설정 변경 없이 꺼낸 별도 worktree 에서 돌렸다(아래 `cd` 경로).
첫 리뷰는 세 기준 모두 PASS 로 판정했지만 권한이 없어 판정 파일을 쓰지 못했다. 판정 파일을 손으로
만들지 않고, 리뷰 명령에 `--permission-mode acceptEdits` 와 변경 경로 파일 폴더의 `--add-dir` 를
더해 다시 돌렸다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q
[exit 0]
----------------------------------------------------------------------
Ran 66 tests in 12.999s

OK

$ cd /tmp/claude-0/wt287-clean && python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793433543
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793433543. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmp5mkt2pvg/unattended/W-00000001-1793433543
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
Ran 671 tests in 118.128s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000287.md
Criteria:
- PASS: 드라이버로 닫은 카드의 Progress 에 승인된 마지막 판의 What changed, Why, Decisions made, Work not done 이 원문 그대로 남는다는 것을 테스트가 확인한다
  Reason: test_close_copies_the_last_executor_report_onto_the_card_progress runs close_work.py on a two-attempt log ending in an approved reviewer report and asserts Progress holds exactly the last report's four lines in a fenced block after the operator note, with no first-round text, reviewer prose, Changed paths, or Review request, and nothing in Verification; latest_executor_report_lines bounds the body at the next heading and the only alteration is the fence_safe escape the fenced block needs; companion tests cover no-report logs and a report with no Progress section.
- PASS: Decisions made 나 Work not done 이 빠진 실행 보고는 거절된다는 것을 테스트가 확인한다
  Reason: executor_report_error now iterates CARD_REPORT_LABELS plus Review request, and test_executor_report_requires_decisions_and_work_not_done asserts the exact rejection message for each of the two fields when the line is absent and when it is empty; the drive fixtures gained None values so the other suites stay valid.
- PASS: 실행자 계약이 마지막 판의 Decisions made 에 그때까지 유효한 결정을 모두 다시 적으라고 요구하고, 계약 문서 셋이 같은 뜻으로 적는다
  Reason: stage-drive SKILL.md:259-262, SCHEMA_V4.md:264-266, and the settings.jsonc template comment each require every attempt's Decisions made to restate each earlier decision still in effect because close copies only the latest report; both executor prompts in .stage/settings.json carry the same sentence and test_template_v4 pins it.
```

## Retrospective

[R-00000287](../../retrospectives/R-00000287.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000078)뿐이므로 `not_applicable`이다.
