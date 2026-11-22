---
id: W-00000396
title: 릴리스된 절 점검이 기준 버전 이후만 보게 한다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000396
promotion: not_applicable
review: passed
scope: stage/scripts/release_plugin.py,stage/scripts/tests/test_release_plugin.py,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000396 릴리스된 절 점검이 기준 버전 이후만 보게 한다

## Purpose

릴리스된 절 점검을 기준 버전 이후에만 걸어 과거 기록 때문에 실패하지 않고 CI 에 넣을 수 있다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- release_plugin.py --check-released --since <버전> 이 그 버전보다 오래된 절을 건너뛰는 시험이 있고 통과한다
- 이 저장소에서 --since 를 지금 최신 버전으로 주면 stage 가 통과한다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: release_plugin.py takes `--since VERSION` with `--check-released`; check_released_sections(since=...) drops release sections whose heading version is below it before finding release commits, and new helpers version_key and heading_version parse the versions; parse_args exits 2 when `--since` comes without `--check-released` or is not x.y.z; test_release_plugin.py gains a twice-released fixture with a line slipped into the older section and three tests (a newer `--since` skips the old section and exits 0 while the unbounded check exits 1, `--since` equal to the old version still reports it, and the two argument errors leave files unchanged); stage/CHANGELOG.md has an Unreleased entry.
Why: The check could not run in CI because history from before it existed fails it; with a baseline it gates only releases from now on. On this repository's full history, `--check-released` exits 1 listing 0.51.0, 0.49.0, 0.43.5 and 0.14.0, and `--check-released --since 0.67.0` exits 0.
Decisions made: The bound is inclusive, so the named version is still checked; a heading below the bound that no commit added is skipped too rather than listed as not checked; `--since` is validated in argparse so misuse exits 2 like other argument errors; no path outside the card's scope was changed.
Work not done: CI is not wired to run the check; the check needs full git history, and in a shallow checkout (this session's clone was shallow until unshallowed) the old intrusions were invisible, so a CI job must fetch full depth; Windows and macOS runs are left to the main session's pull-request CI.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6NxS8KEi52xUp6uzt9)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w396-check-released-since` 의 f51102ab 를 squash 했다(44f0ab1b).
- 성공 기준 1: `test_release_plugin.py` 15개가 통과한다(`--since` 아래의 절을 건너뛰는 시험 포함).
- 성공 기준 2: 메인 세션의 1,200여 커밋 클론에서 `release_plugin.py stage --check-released --since 0.67.0` 은 0 으로 끝났다
  ("no released section gained lines"). `--since` 없이는 1 로 끝난다.
- 메인 세션이 다시 돌린 검사: scripts 전체 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
