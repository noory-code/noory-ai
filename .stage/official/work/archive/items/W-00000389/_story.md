---
id: W-00000389
title: W-00000381, W-00000382, W-00000384 에서 사용자가 정한 것을 기록에 남긴다
kind: documentation
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000389
promotion: not_applicable
review: passed
scope: .stage/decisions/pending/DE-00000091.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000389 W-00000381, W-00000382, W-00000384 에서 사용자가 정한 것을 기록에 남긴다

## Purpose

사용자가 2026-11-22 에 고른 다섯 가지가 결정 기록과 도면에 남아 다음 세션이 다시 묻지 않는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- DE-00000091 에 변경 기록 줄이 엉뚱한 절에 들어가는 세 번째 결과와 그 처리가 메모로 있다
- BLUEPRINT 에 hooks/stage_process.py 가 경로와 규칙 층에 있고, 리뷰 명령이 제어 터미널 없이 돈다는 한계가 적혀 있다
- git ls-files -t 를 쓰기로 한 것이 그 이유와 함께 기록에 있다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: BLUEPRINT.md lists hooks/stage_process.py, scripts/stage_id_blocks.py, and scripts/subsession_brief.py in the layer table and gains two "코드가 말해 주지 않는 것" sections (timeouts end the whole process group and run without a controlling terminal on POSIX; the driver relies on `git ls-files -t` on purpose, pinned by test_driver_repository.py); DE-00000091 gains a dated observation of the third union outcome, why the decision stands, how `--check-released` finds it, and the four historical stage entries it flags; stage/CHANGELOG.md has an Unreleased entry.
Why: W-00000389 records what the user chose on 2026-11-22 ("추천대로") so the next session does not ask again.
Decisions made: Recorded the `ls-files -t` and controlling-terminal choices in the blueprint rather than in a decision record, because the blueprint owns what the code does not say about itself and neither choice changes a contract; added stage_id_blocks.py and subsession_brief.py to the layer table in the same edit because they were missing for the same reason; left how to treat the historical changelog entries open in DE-00000091, since the user has not chosen yet.
Work not done: None.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 사용자가 2026-11-22 에 다섯 질문 모두 "추천대로"라고 답했다.
- 성공 기준 1: DE-00000091 의 "2026-11-22 에 더한 관측" 절.
- 성공 기준 2: BLUEPRINT 레이어 표의 경로와 규칙 줄에 `hooks/stage_process.py` 가 있고, "시간 제한은 프로세스 그룹 전체를
  끝낸다" 절이 제어 터미널 한계를 적는다. 코드와 맞춰 보았다(`stage_process.py` 의 `start_new_session`, `taskkill /T /F`, `killpg`).
- 성공 기준 3: BLUEPRINT 의 "드라이버는 `git ls-files -t` 에 기댄다" 절. `driver_repository.py` 124행의 `-t` 와 맞춰 보았다.
- 감사 오류 0건.

- Checks at close 2026-11-22: 1 passed — `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS, 4 PASS)
