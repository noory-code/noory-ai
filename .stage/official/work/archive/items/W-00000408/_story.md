---
id: W-00000408
title: 닫기 리뷰어가 실행해서 판정하고 판정 방법이 카드에 남는다
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
retrospective_ref: R-00000408
promotion: not_applicable
review: passed
scope: stage/scripts,stage/skills,stage/operations,stage/templates,.stage/settings.json,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000408 닫기 리뷰어가 실행해서 판정하고 판정 방법이 카드에 남는다

## Purpose

리뷰어가 기록만 읽고 승인하는 일이 없어진다: 실행이 필요한 기준은 리뷰어가 직접 실행해서 판정하고, 무엇으로 판정했는지가 커밋된 카드에 남는다 (DE-00000101)

## Actions


## User value


## Scope

### Included

- DE-00000101 의 "Where this applies" 표에서 코드, 설정, 절차 줄.


### Excluded

- 결함이 기록된 과거 변경으로 리뷰어를 재는 일(3-가). 다음 카드가 한다.
- 사용자가 카드 다섯 장을 직접 판정하는 일(3-나). O-00000062 에 있다.


## Risks


## Success criteria

- 대역 리뷰어가 카드의 검사 명령(예: audit_stage.py)과 스스로 고른 명령을 실행할 수 있고, 프로젝트 파일을 고친 리뷰는 지금처럼 닫기가 실패시킨다
- 판정 파일이 기준마다 판정 방법을 담고, 실행이 필요한 기준을 실행하지 못한 판정이면 닫기가 실패하며, 기준별 판정 방법이 카드에 남는다
- 설정과 템플릿의 리뷰 명령이 근거를 직접 보지 못한 기준은 FAIL 이라고 말하고, 닫기가 이미 돌린 검사의 반복 대신 리뷰어 자신의 탐침을 요구한다
- stage-orchestrate 와 검증 브리핑이 검증 세션은 닫기의 관문이 아니며 세션에서만 볼 수 있는 기준이 있을 때만 띄운다고 말한다

## Next action

없음. 닫고 보관한 뒤 병합한다.


## Related truth

- DE-00000101, `.stage/research/review-judgment/`, W-00000401, W-00000405(`- Load at close` 줄과 `work_load.py`)
- 리뷰어의 권한을 넓히면 저장소 밖 변경과 푸시는 닫기의 앞뒤 비교가 보지 못한다(DE-00000101 이 알고 고른 약점). 넓힌 범위와 남는 위험을 보고에 적는다.
- 목적과 성공 기준은 지휘 세션이 사용자의 위임(2026-11-23)으로 DE-00000101 에서 옮겨 적었다.
- 시작 커밋 ac85e8f0 의 제목은 W-00000407 이라고 적었지만 이 카드의 번호는 W-00000408 이다. W-00000407 은 다른 세션이 `claude/register-rag-python-314-card` 에서 먼저 썼다.


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 ae94a2ec 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6S2zox5g3mzb9De1SM (`claude/w408-reviewer-runs`)를 띄웠다. 번호 묶음은 잡지 않았다.


- 2026-11-23 작업 세션 session_018VXR6S2zox5g3mzb9De1SM 가 506f6650 을 보고했다. 성공 기준 1-4 를 주장했다. 지휘 세션이 squash 커밋에서 scripts 937, hooks 467 통과와 audit 오류 0 을 다시 확인했다. 범위 밖 변경은 `stage/docs/SCHEMA_V4.md` 한 곳이다(판정 항목의 키를 말하는 문장).
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: `method` 필수(이관 스크립트 없음), "`ran` 이 하나는 있어야 한다"는 바닥 없음, `git push` 와 `git commit` 거부 목록.
- Follow-up candidate: `LiveReviewerWriteProbeTest` 를 STAGE_LIVE_REVIEW_PROBE=1 로 돌려 결과를 남긴다.
- Follow-up candidate: 리뷰 명령의 문장이 `method` 를 말하지 않는 프로젝트를 알리는 audit 검사나 이관 단계.
- Follow-up candidate: 3-가의 재기에서 리뷰어가 실행이 필요한 기준을 `read` 로 통과시키면 "`ran` 이 하나는 있어야 한다"는 바닥을 넣는다.
- Follow-up candidate: 닫기가 돌린 검사의 출력을 리뷰어에게 넘긴다.
- Follow-up candidate: `work_load.py` 가 닫힌 카드의 `ran`, `read`, `unable` 수를 센다.
- Follow-up candidate: 검증 세션을 띄운 카드를 닫기 전에 `- Observed` 줄이 카드에 있는지 본다.

### Executor report at close — 2026-11-23

```
What changed: The review verdict gained a required per-criterion `method` key (ran, read, unable) validated in close_work.normalize_review_verdict and carried through the driver's narrow re-review merge; close_work.py writes each method on the card's `- Review at close` line and names criteria judged `unable` in the failure message; claude_review_companion.py allows every Bash (and on Windows PowerShell) command while denying `git push` and `git commit` and keeping file edits to the verdict file; the six review prompts in .stage/settings.json and the template comment state the method key, that unseen evidence is FAIL, and that the reviewer runs its own probe; subsession_brief.py --role verify now requires --criterion and produces an observation brief; review.md, cloud-execution.md, stage-orchestrate, stage-handoff, BLUEPRINT.md, SCHEMA_V4.md, and CHANGELOG.md describe the new contract.
Why: DE-00000101 chose one judge (the close review), a self-reported judgment method per criterion with a failed close when a needed run did not happen, and the reviewer's own probes; the confirmed gap was that the stand-in reviewer could not run a card's checks such as audit_stage.py.
Decisions made: (1) `method` is required, not optional, so a project whose review prompts are not updated fails every review until they are; the CHANGELOG marks this breaking. (2) Method values are `ran`, `read`, `unable`; `unable` with PASS is an invalid verdict and `unable` with FAIL is a valid rejection, so a rejection line still lands on the card. (3) The stand-in reviewer gets every shell command rather than a list of card checks, because a self-chosen probe cannot be listed in advance; `git push` and `git commit` are denied as prefix rules, which stop a mistake and not a command hidden in `sh -c` or a script, and nothing detects a change outside the repository (the weakness DE-00000101 accepted). (4) Not built: the design note's floor that a card with stored checks needs at least one `ran` criterion; DE-00000101's chosen text does not include it and it would push reviewers of record-only cards to run a meaningless command. (5) Not built: handing the output of close's checks to the reviewer; the reviewer may run them itself. (6) A resumed driver run whose carried verdict has no method stops with a merge error instead of guessing a method. (7) The verify brief refuses to print without --criterion and refuses text the card or its stories do not state, which makes the start condition mechanical. (8) Changed outside the card's scope: stage/docs/SCHEMA_V4.md, because it states the verdict entry's keys and the merge rule and would have contradicted the code. (9) The live test LiveReviewerWriteProbeTest (skipped unless STAGE_LIVE_REVIEW_PROBE=1) was adapted to the widened permission but not run; a separate live run of the stand-in in a throwaway clone with claude 2.1.330 and model sonnet ran audit_stage.py and git log, was refused git push, git commit, a compound line ending in git commit, and a Write-tool file, and wrote the verdict file.
Work not done: Measuring the reviewer against past changes with recorded defects (3-ga) and the user's own judgment of five cards (3-na) are excluded by the card. Checks on Windows were not run: the PowerShell allow and deny rules and the Windows branch of test_template_v4 are covered only by platform-parameter unit tests here. Other projects' review prompts are not migrated by any script.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰이며, 이 카드가 바꾼 판정 계약(`method`)으로 도는 첫 리뷰다.

- Checks at close 2026-11-23: 1 passed — `python3 -m unittest discover -s stage/scripts/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS read, 4 PASS ran, 5 PASS read)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
