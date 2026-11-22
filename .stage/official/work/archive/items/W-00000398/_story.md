---
id: W-00000398
title: 로드맵 기록 번호도 잡아 둔 번호와 다른 브랜치 번호를 피한다
kind: fix
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000398
promotion: not_applicable
review: passed
scope: stage/skills/stage-roadmap,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000398 로드맵 기록 번호도 잡아 둔 번호와 다른 브랜치 번호를 피한다

## Purpose

manage_roadmap.py 가 카드에 잡아 둔 번호나 다른 브랜치가 쓴 번호를 다시 고르지 않는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 잡아 둔 번호와 다른 브랜치의 번호를 건너뛰는 것을 보이는 시험이 있고, 고치기 전에는 실패하고 지금은 통과한다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: stage/skills/stage-roadmap/manage_roadmap.py `_create_atomic` now also counts, for the prefix it mints, every number `stage_record_ids.local_record_numbers` finds in the working tree's `.stage/` (record ids and card `reserved_ids:` lines) and every number `stage_record_ids.branch_record_numbers` finds on local and remote-tracking branches, before adding remote reservations and taking the next id; new stage/scripts/tests/test_roadmap_ids.py shows open-pursuit skipping DE ids a started card holds and create-theme/create-milestone skipping TH/M ids committed on another branch (all three fail on the previous code and pass now); CHANGELOG has an Unreleased entry.
Why: W-00000398's purpose is that manage_roadmap.py never re-picks a number held on a card or used by another branch, matching what stage_record_ids.py and register_work.py already count.
Decisions made: Reused the stage_record_ids.py counting functions instead of a roadmap-local copy (SSOT), keeping the existing per-family existing_ids and the next_artifact_id counter; the extra numbers are added as same-prefix ids so the legacy D-/DE- family rule still applies; no path outside the card scope was changed; no stage/docs/BLUEPRINT.md row was needed because no code file was added outside tests.
Work not done: Windows runs of the suites are left to the pull request's Windows CI; no new record ids were created.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6PM6PoHGZTqjZ5rWt3)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w398-roadmap-ids` 의 681231bd 를 squash 했다(494bc8dd).
- 성공 기준: `test_roadmap_ids.py` 3개(카드가 잡은 DE 번호, 다른 브랜치의 TH·M 번호를 건너뜀)가 고치기 전 코드에서 모두 실패하고
  지금 통과한다(서브세션이 확인). 메인 세션이 다시 돌린 scripts 전체 통과, 감사 오류 0건.
- Windows 는 PR CI 로 본다.

- Checks at close 2026-11-22: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_roadmap_ids.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_roadmap*.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS)
