---
id: W-00000405
title: 뺀 장치의 하중을 커밋된 기록으로 잴 수 있게 한다
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
retrospective_ref: R-00000405
promotion: not_applicable
review: passed
scope: stage/scripts,stage/skills,stage/operations,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md,.stage/research/claude-fit
promotes:
decision_refs:
---

# W-00000405 뺀 장치의 하중을 커밋된 기록으로 잴 수 있게 한다

## Purpose

장치를 하나 뺐을 때 그 장치가 하중을 받고 있었는지, 클라우드 작업 세션으로 도는 지금의 흐름에서도 커밋된 기록만으로 알 수 있다

## Actions


## User value


## Scope

### Included

- `.stage/research/claude-fit/mechanisms.md` 의 B11 행에 Dasina 사고 출처(R-00000028, R-00000031)를 적는다(W-00000403 의 후속 후보).
- DE-00000101 이 정한 판정 방법 칸과 리뷰어 권한은 다음 카드가 만든다. 이 카드는 지금의 판정 기록에서 남길 수 있는 것을 남긴다.


### Excluded

- 빼기 전 기준선을 Mac 의 `.stage/.runtime/driver/logs/` 에서 세는 일. 사용자의 기계가 필요하다.
- 빼기 실험을 시작하기 전에 잴 수 있는지 확인하는 절차. R-00000403 의 규칙 후보로 남기고 한 번 더 관찰되면 올린다.

## Risks


## Success criteria

- 카드 한 장이 닫힐 때 시도 수, 리뷰 FAIL 회차, 실패 기록이 커밋되는 자리에 남는다
- 그 기록으로 W-00000403(B11) 이후에 닫힌 카드들의 수치를 표로 낼 수 있고, .stage/research/claude-fit/b11-load.md 의 결과 표가 그 수치로 채워진다

## Next action

없음. 닫고 보관한 뒤 병합한다.

## Related truth

- W-00000403 과 R-00000403: 빼기 전후 비교를 이 카드로 옮겼다.
- DE-00000098, `.stage/research/claude-fit/b11-load.md`
- 사용자가 2026-11-23 에 목적("잴 수 있는지부터 정하기")과 성공 기준 두 개를 정했다("네 추천대로 1, 2만 등록하죠").

## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 61f9db1e 에서 카드를 시작하고 작업 세션 session_018VXR6NSkSuqDBpwudoBy37 (`claude/w405-committed-load`)를 띄웠다. 번호 묶음은 잡지 않았다.

- 2026-11-23 작업 세션 session_018VXR6NSkSuqDBpwudoBy37 가 4474c5e9 를 보고했다. 성공 기준 1 을 주장했고, 기준 2 는 커밋된 기록이 허락하는 만큼 채웠다고 보고했다. 지휘 세션이 squash 커밋에서 scripts 925, hooks 467 통과와 audit 오류 0 을 다시 확인했고, 사용자의 위임으로 기준 2 를 그 정도로 받았다.
- Follow-up candidate: 이 변경 뒤에 완료된 카드에 `- Load at close` 줄이 있는지 보는 audit 규칙.
- Follow-up candidate: `import_executor_report.py` 가 `--commit` 시도마다 보고 하나(또는 시도 수)를 남겨, squash 된 클라우드 카드의 시도 수를 작업 로그 없이 센다.
- Follow-up candidate: 카드가 더 닫힌 뒤 `b11-load.md` 의 표를 다시 낸다.
- Follow-up candidate: DE-00000101 의 3-다(닫은 뒤 뒤집힌 판정)를 이 줄에 얹는다.

### Executor report at close — 2026-11-23

```
What changed: close_work.py writes a `- Load at close` line (attempts, review FAIL rounds, repeated findings, driver rounds, driver failures with the timed-out count, one line per driver failure reason) into the card's `## Verification`; the new stage/scripts/work_load.py owns the counting, the line, its parser, and a Markdown table over closed cards (`--closed-since` or card ids); operations/review.md defines each count; operations/cloud-execution.md tells the main session to commit a rejected review line and keep the work log between attempts; the stage-retrospective skill, BLUEPRINT layer table, and CHANGELOG name the new line and file; mechanisms.md B11 row cites Dasina R-00000028 and R-00000031; b11-load.md gains the committed-record method and the table for cards closed after W-00000403.
Why: The card's purpose is that a removed control's load can be read from committed records in the cloud flow; the work log that held those events is not committed and does not exist in a cloud session.
Decisions made: Counting lives in a new module instead of close_work.py, which is already over 1200 lines. Review FAIL rounds take the larger of the card's rejected lines and the work log's answered rounds, not the sum, because one round can appear in both. Attempts take the larger of the log's executor reports and FAIL rounds + 1. Repeated findings are written as `unknown` when the log holds fewer answered rounds than FAIL rounds, instead of 0. A `driver rounds` count was added beyond the three items in the success criterion so a reader can tell driver-run cards (the only sample for the removed timeout table) from cloud cards. No path outside the card's scope was changed. No record needing a new id was created.
Work not done: The result table for cards closed after W-00000403 (W-00000406, W-00000401, W-00000400) holds only their rejected-review count (0 each); attempts and driver columns read `not recorded` because those cards closed before the line existed, so the second success criterion is met only to the extent the committed records allow. No driver-run card closed after B11, so the removed timeout table's load is still unmeasured. The pre-removal baseline on the Mac work logs and the judgement-method field of DE-00000101 are excluded by the card. Windows runs of the suite were not executed here; the pull request's CI jobs cover them.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰이며, 다른 venue 의 리뷰가 아니다.

- Checks at close 2026-11-23: 1 passed — `python3 -m unittest discover -s stage/scripts/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS, 2 PASS)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
