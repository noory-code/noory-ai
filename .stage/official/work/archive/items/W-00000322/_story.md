---
id: W-00000322
title: Stage 0.65.0 을 출시한다 — 버그 정리와 CI 복구
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000322
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/, stage/.codex-plugin/
promotes:
decision_refs:
---

# W-00000322 Stage 0.65.0 을 출시한다 — 버그 정리와 CI 복구

## Purpose

이번 버그 정리(번호 도구, 되돌릴 때 작업 정리, 목록 기호, 실패한 리뷰가 남긴 파일, 리뷰 실행 여부, Windows /dev/null)를 사용자가 설치본으로 받을 수 있게 한다

## Actions

- `python3 stage/scripts/release_plugin.py stage --bump minor` 로 `## Unreleased` 의 일곱 항목(W-00000314~W-00000321)을 0.65.0 절로
  옮기고 두 매니페스트를 올린다. 실패한 리뷰가 남긴 파일로 다음 판을 막는 것과 리뷰 프롬프트 변경은 동작이 바뀌므로 마이너로 올린다.
- 설치본 업데이트(`claude plugin update stage@noory-ai`)는 사람이 로컬에서 한다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage 매니페스트 두 개의 버전이 0.65.0 이고, CHANGELOG 의 0.65.0 절에 이번 일곱 항목이 있으며 그 위에 빈 Unreleased 절이 있다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-04

```
What changed: release_plugin.py titled the seven queued Unreleased entries as 0.65.0 — 2026-11-04, opened a new empty Unreleased section, and moved both Stage manifests from 0.64.0 to 0.65.0.
Why: W-00000322 - let users install this round's Stage fixes.
Decisions made: Bump minor, not patch, because a supervised round can now be refused until a failed review's files are restored and every review command asks for run disclosure; leave updating installs to the person on their machine, which this cloud session cannot reach; out-of-scope paths changed: none.
Work not done: Installs are not updated (claude plugin update stage@noory-ai and a restart on the person's machine).
```

## Verification


### Executed at close — 2026-11-04

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q
[exit 0]
----------------------------------------------------------------------
Ran 8 tests in 0.673s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q
[exit 0]
----------------------------------------------------------------------
Ran 8 tests in 0.743s

OK
```

## Retrospective


## Promotion decision
