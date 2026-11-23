---
id: W-00000414
title: 지금의 닫기 리뷰어를 결함이 기록된 과거 변경으로 잰다
kind: design
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000414
promotion: not_applicable
review: passed
scope: .stage/research/review-judgment
promotes:
decision_refs:
---

# W-00000414 지금의 닫기 리뷰어를 결함이 기록된 과거 변경으로 잰다

## Purpose

닫기 리뷰어의 판정이 사람이 남긴 과거의 판정과 얼마나 맞는지가 수로 있어서, 리뷰어를 더 조일지 말지를 그 수로 정한다 (DE-00000101 의 3-가)

## Actions


## User value


## Scope

### Included

- 재는 방법과 표본을 먼저 적는다. 쓸 수 있는 과거 변경이 몇 건인지부터 센다(닫기 리뷰가 반려한 기록, 닫은 뒤 고친 기록, 회고가 결함을 적은 카드).
- 리뷰어는 저장소의 리뷰 명령(`claude_review_companion.py`)으로 돌린다.


### Excluded

- 리뷰 코드나 설정을 고치는 일. 바닥을 넣는 것은 추천까지만 한다.
- 사용자가 카드 다섯 장을 직접 판정하는 일(3-나).


## Risks


## Success criteria

- 결함이 기록된 과거 변경의 목록과, 지금의 리뷰어를 그 변경과 통과한 최종판에 돌려 센 거짓 통과와 거짓 반려의 수가 연구 자료에 있다
- 그 결과에 비추어, 실행이 필요한 기준에 ran 이 하나는 있어야 한다는 바닥을 넣을지에 대한 추천이 근거와 함께 있다

## Next action

없음. 닫고 보관한 뒤 병합한다.


## Related truth

- DE-00000101, `.stage/research/review-judgment/design.md`, W-00000408, W-00000410(실행해서 판정하는 리뷰어의 첫 반려)
- 리뷰어를 여러 번 띄우므로 비용이 든다. 표본이 작으면 작다고 적고 수를 과하게 읽지 않는다.
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions

- session_018VXR6QZEBarY6p6PTVEZdb — work — 2026-11-23 — opened from the index: DE-00000101


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 d192365b 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6QZEBarY6p6PTVEZdb (`claude/w414-measure-reviewer`)를 띄웠다. 번호 묶음은 잡지 않았다.


- 2026-11-23 작업 세션 session_018VXR6QZEBarY6p6PTVEZdb 가 c2698516 을 보고했다. 성공 기준 1, 2 를 주장했다. 결함판 22번 중 반려 19, 거짓 통과 3. 통과판 16번 중 승인 11, 반려 5. 닫은 뒤 드러난 결함 4건은 8번 중 한 번도 짚지 못했다. 지휘 세션이 squash 커밋에서 audit 오류 0 을 다시 확인했다.
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: `ran` 바닥은 지금 넣지 않는다. 리뷰어가 저장소 밖을 읽은 일과 W-00000309 의 반려를 어떻게 셀지는 사용자가 볼 목록(O-00000062)에 올린다.
- Follow-up candidate: 닫은 뒤 드러난 결함 4건(W-00000295, W-00000332, W-00000291, W-00000392)을 codex 리뷰어나 검증 세션에 돌려 견준다.
- Follow-up candidate: 리뷰어가 볼 수 없는 기준(다른 OS 의 CI, 사용자 기기의 기록)을 카드에 적을 때 누가 어디서 보는지를 함께 적는다.
- Follow-up candidate: 리뷰어가 저장소 밖을 읽는 것(세션 기록 폴더, GitHub API)을 막을지 정한다. 앞뒤 비교는 쓰기만 보고, 무시되는 파일의 쓰기도 보지 않는다.
- Follow-up candidate: 측정 스크립트가 실제 닫기의 트리를 통과판으로 고를 수 있게 한다.
- Follow-up candidate: 판정 방법 칸을 리뷰어의 실제 명령과 대조한다(실행 기록 38개가 있다).

### Executor report at close — 2026-11-23

```
What changed: Whole card, all four commits, all under .stage/research/review-judgment. measurement.md states the method, the sample (records swept: 13 cards with a version sent back before close, 4 defects recorded after a passed close, 4 found after close by CI or use; measurable: 11 defective versions and 8 passing versions), the result of running today's reviewer twice on each (defective: 19 rejected, 3 false passes in 22 runs, the recorded defect named in 14; passing: 11 approved, 5 rejected in 16 runs, of which 2 come from a wrongly chosen sample commit, 1 from a criterion this environment cannot observe, 2 disagree with the record but show a real gap), the limits of the method, what was seen of DE-00000101's stated reasons to revisit, and the recommendation on the `ran` floor. cases.json lists the nineteen versions with commit, expected outcome and the record that states the defect. measure_reviewer.py checks a past commit out alone and runs the review command of the current checkout on it the way close_work.py does. summarize_runs.py prints the runs as tables. runs/ holds one JSON record per run (verdict with reasons, seconds, the reviewer's shell commands, tokens). README.md links the write-up and states the three headline numbers.
Why: The card's two success criteria: the list of past changes with a recorded defect and the counted false passes and false rejections are in the research material, and a recommendation on the floor is there with its grounds (DE-00000101, 3-가).
Decisions made: (1) Committed the measuring script and the raw runs in the research folder instead of keeping them in a temp folder, so the measurement can be repeated after the reviewer's prompt or permissions change and so the reviewer's reasons, which a real close does not commit, can be read. (2) Each past commit is checked out in a new repository that borrows this repository's objects and has no branch or tag, so the reviewer cannot see later commits by name; the reviewer's scripts and prompt come from the current checkout, not from the past tree. (3) The work log given to the reviewer holds only the executor report from the commit body; W-00000332 and W-00000335 have none in their commits, and the reviewer failed the reporting contract for that in 3 runs, which the write-up marks as made by the method. (4) Two runs per version, 38 runs, 7,688 seconds of reviewer time in total; no dollar cost is stated because no price was checked. (5) For a defect found after a passed close, the passing counterpart is the later card that fixed it, not a later version of the same card. (6) Whether a rejection named the recorded defect was judged by this session reading each reason; the scripts count outcomes only. (7) The record sweep was done by a subagent of this session; this session verified every commit, card path, card status and executor report of the nineteen versions, and did not re-read every record the subagent quoted for the versions left out. (8) Left out of the measurement and listed with the reason: Windows-only defects, versions overwritten by amend, criteria that need a new cloud session, and regressions outside the introducing card's criteria. (9) W-00000335 at its code commit is a wrongly chosen passing sample (its fourth criterion was met by a later record commit); it is kept and labelled instead of being replaced after seeing the result. (10) Recommendation, not a decision: do not add the `ran` floor now. (11) Fetched the full history of main and the branches claude/w382-fewer-git-calls and claude/w410-small-fixes into the local clone; nothing was pushed besides this branch. (12) No path outside the card's scope was changed. (13) No record was created.
Work not done: The five rejections of defective versions for a reason other than the recorded one (W-00000332 twice, W-00000291 twice, W-00000392 once) were not checked for being right. The `ran` marks were not matched against the reviewer's shell commands criterion by criterion; only the number of commands per run was counted. No verification session and no other venue was run on the same cases, so DE-00000101's condition for moving to 1-다 was not measured. Nothing was run on Windows or macOS; the two scripts were run on Linux only and have no tests. No reviewer code or settings were changed, as the card excludes it.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다. 이 카드가 잰 바로 그 리뷰어다.

- Checks at close 2026-11-23: 1 passed — `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS read, 3 PASS read)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
