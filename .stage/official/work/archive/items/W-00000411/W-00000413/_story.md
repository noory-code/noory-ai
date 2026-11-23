---
id: W-00000413
title: 리뷰와 닫기의 증거가 빠짐없이 남고 다른 프로젝트가 올릴 길이 있다
kind: development
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000413
promotion: not_applicable
review: passed
scope: stage/scripts,stage/skills/stage-retrospective,stage/skills/stage-audit,stage/hooks,stage/templates,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000413 리뷰와 닫기의 증거가 빠짐없이 남고 다른 프로젝트가 올릴 길이 있다

## Purpose

닫힌 카드의 기록만으로 리뷰어가 무엇을 실행했고 몇 번 만에 닫혔는지 알 수 있고, 다른 프로젝트가 이 판으로 올릴 때 막히는 자리를 도구가 알려 준다

## Actions


## User value


## Scope

### Included


### Excluded

- 닫은 뒤 뒤집힌 판정을 세는 일(DE-00000101 의 3-다), `review.strengths` 의 TIER007, 다른 브랜치에 파일 이름으로만 있는 옛 너비의 번호.
- 다른 프로젝트(Dasina)의 저장소를 고치는 일.


## Risks


## Success criteria

- audit 가 하중 줄이 없는 완료 카드와, 판정 방법(method)을 말하지 않는 리뷰 명령을 알린다
- import_executor_report.py 가 시도 수를 남기고 work_load.py 가 닫힌 카드의 ran, read, unable 수를 센다
- 닫기가 돌린 검사의 출력이 리뷰어에게 넘어간다
- 다른 프로젝트가 올릴 때 쓰는 명령 하나가 결정 색인과 작업 보관 색인의 제목을 채운다
- LiveReviewerWriteProbeTest 를 실제로 돌린 결과가 보고에 있다
- 색인이 줄여야 할 때 규칙 후보를 결정 제목보다 먼저 줄이고, 규칙 후보 39건이 있어도 이 저장소의 결정 제목이 실린다
- 열린 관측 O-00000058, O-00000059, O-00000060 마다 고침이 들어갔거나 고치지 않는 까닭이 보고에 있다

## Next action

없음. 닫는다. 보관은 에픽과 함께 한다.


## Related truth

- W-00000405, W-00000408, W-00000409 의 후속 후보, DE-00000101
- O-00000058(닫기 리뷰는 맨 위 커밋이 고친 파일만 본다), O-00000059(드라이버가 닫는 카드는 손으로 닫는 카드와 두 군데가 다르다), O-00000060(열린 카드가 없으면 관문이 머지 커밋도 막는다)
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions


## Progress

- 2026-11-23 에픽의 작업 세션 session_018VXR6PwLBPzLD6Y92UC31m 가 이 스토리를 cf87613 으로 보고했다. 성공 기준 1-7 을 주장했다. 지휘 세션이 cherry-pick 한 커밋(fe6bfd2a)에서 scripts 1004, hooks 487 통과와 audit 오류 0 을 다시 확인했다. 실제 규칙 후보 목록(39건)과 진행 중 카드 다섯 장으로 색인을 내 보니 9,993자에 결정 제목 63건이 실리고 후보는 한 줄로 남았다.
- 2026-11-23 `LiveReviewerWriteProbeTest` 를 실제로 돌린 결과: 2건 실행, 통과(1건 건너뜀). 대역 길은 통과했다. 프로젝트 리뷰어 길은 리뷰어가 스스로 `git checkout` 으로 트리를 되돌려 판정할 수 없었다.
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: O-00000059 와 O-00000060 을 고치지 않는 것, 새 audit 코드가 경고인 것, DE-00000100 의 글과 달라진 줄이는 순서.
- Follow-up candidate: 시험을 돌린 뒤 `git checkout` 으로 트리를 되돌린 리뷰어가 닫기의 앞뒤 비교를 통과한다. 관측으로 남기고 막을 길을 찾는다.
- Follow-up candidate: 검증 세션 줄이 있는 카드는 `- Observed` 줄이 있어야 닫히게 `close_work.py` 가 강제한다. "닫기 리뷰 없이 병합했다"가 Progress 의 산문에만 보인다.
- Follow-up candidate: `close_work.py` 1,349줄, `audit_stage.py` 2,065줄.
- Follow-up candidate: DE-00000100 의 글을 지금의 줄이는 순서에 맞게 고친다.


### Executor report at close — 2026-11-23

```
What changed: (1) New stage/scripts/audit_close_evidence.py, called from audit_stage.py: WORK030 (warning) for a card with a `- Checks at close` line and no `- Load at close` line whose last close day is later than the earliest load-line day among the project's own cards; REVIEW003 (warning) for a non-empty review.reviewers or review.strengths command that lacks any of the whole words method, ran, read, unable. (2) import_executor_report.py ends the imported report with `Attempt commits: <n> (<sha>, ...)`, counting distinct resolved commits; work_load.count_load takes attempts as the largest of the reports in the log, FAIL rounds plus one, and that number, so close_work.py writes it into `- Load at close`; the work_load.py table gains Ran, Read, Unable, counted from the card's last `- Review at close` line. (3) close_work.py keeps each passed check's output and, before a review command starts, appends a `### Checks at close` section to the work log that review commands already read through STAGE_WORK_LOG_PATH (new stage/skills/stage-retrospective/review_material.py): the last 60 lines and 6000 bytes per check, 30000 bytes per close, lines indented four spaces. (4) New stage/scripts/refresh_index_titles.py --project-root . renders the pending-decision index, fills the official decision index's titles, and fills work-archive rows that have no title; it replaces no existing title and is idempotent. DECISION005 names the command; new ARCHIVE005 (warning) counts fillable rows per index. (5) close_work.py --review-commit <rev> (repeatable) hands the review the union of those commits' paths instead of HEAD's; without it a WARNING is printed when every HEAD path is under .stage/. (6) stage_context.session_index sheds rule candidates before decision titles, and stage_memory_index.rule_candidate_lines lists `proposed: promote` bullets first. (7) The LiveReviewerWriteProbeTest fixture points the project reviewer command at this plugin's scripts instead of a partial copy. Tests, stage-audit and stage-retrospective skills, hooks/README.md, the settings template, operations/review.md, operations/cloud-execution.md, BLUEPRINT.md and CHANGELOG.md follow.
Why: The story's six success criteria (follow-up candidates of W-00000405, W-00000408, W-00000409; O-00000058, O-00000059, O-00000060) and a seventh the main session added during the run: with 39 rule candidates the index showed 36 candidates and no decision title.
Decisions made: (1) WORK030's cut-off is the project's own first load-line day, not a fixed date or card id, because another project updates on another day; cards closed on that same day are not judged, so this repository has no finding. (2) REVIEW003 reads reviewers and strengths, not executors; executors are not review commands. (3) Check output goes into the work log, not a new variable and file, so existing review prompts hand it over without a settings change; the card still keeps the commands only. (4) Method counts come from the last review line, the verdict the close rests on, not from all rounds. (5) WORK030, REVIEW003 and ARCHIVE005 are warnings; DECISION005 stays an error. (6) The title fill never replaces a title, so hand-written titles survive. (7) O-00000058 is fixed with an explicit flag and a warning; the close does not read commits from the work log by itself, which would be more gate logic than the problem needs. (8) O-00000059 is not fixed: the observation says to leave it until the driver is used again, and the driver is unused while Codex is absent. (9) O-00000060 is not fixed: stage_guard.commit_target_files lists staged files with no merge handling and does what hooks/README.md states, so it is policy and not a plain bug; whether a merge commit passes with no open card is the user's choice. (10) With 39 candidates on this repository every candidate leaves the index before any decision title does (9,993 characters, 63 of 82 titles, 0 candidates, measured with a temporary fixture that was removed); the promote-first order shows only when some candidates fit. DE-00000100's text records the old order (oldest decision titles first); the code and documents now differ from that record, which this session may not edit. (11) Changed outside the story's scope, inside the epic's: stage/operations/cloud-execution.md and stage/operations/review.md, because they own the contracts this change alters (the shortening order, the source of attempts, the `Checks at close` section, --review-commit, the new table columns). (12) Fixed the live probe's fixture because without it the project reviewer path ran no reviewer: run_review.py failed at `from close_work import DEFAULT_REVIEW_TIMEOUT` in the throwaway repository.
Work not done: LiveReviewerWriteProbeTest was run with STAGE_LIVE_REVIEW_PROBE=1 and claude 2.1.330 (python3 -m unittest -v test_claude_review_guard.LiveReviewerWriteProbeTest, from stage/scripts/tests). Before the fixture fix: Ran 2 tests, OK (skipped=1); test_cloud_stand_in_path ok (the direct Write was refused, shell writes landed as " M tracked.txt", "?? bash-write.txt", "?? chained.txt", and the comparison removed the verdict); test_project_claude_reviewer_path skipped as inconclusive because no reviewer ran. After the fix: Ran 2 tests in 50.761s, OK (skipped=1); the stand-in path ok again; on the project path the reviewer ran (passed true, changed [], verdict kept) and the test was skipped as inconclusive, because the reviewer ran the fixture's tests, saw them overwrite tracked.txt, ran git checkout -- tracked.txt and deleted tests/__pycache__, so the before-and-after comparison saw nothing. The project path's write check is therefore not exercised live, and a reviewer that restores the tree passes the comparison. refresh_index_titles.py was not run on this repository (it writes .stage/); an in-memory check showed 0 fillable rows. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. close_work.py is 1,349 lines and audit_stage.py 2,065; new logic went into new modules. Checks run on Linux by the work session after the sub-agent finished: python3 -m unittest discover -s stage/scripts/tests -q (1004 tests, OK, skipped=2), python3 -m unittest discover -s stage/hooks/tests -q (487 tests, OK, skipped=2), python3 stage/scripts/audit_stage.py (errors=0, warnings=32, no new finding). No record was created.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Checks at close 2026-11-23: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 -m unittest discover -s stage/hooks/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS ran, 4 PASS ran, 5 PASS read, 6 PASS ran, 7 PASS read)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
