---
id: W-00000312
title: Stage 0.64.0 을 출시한다 — 리뷰 쓰기 검사와 범위 알림 정리
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
retrospective_ref: R-00000312
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/, stage/.codex-plugin/
promotes:
decision_refs:
---

# W-00000312 Stage 0.64.0 을 출시한다 — 리뷰 쓰기 검사와 범위 알림 정리

## Purpose

리뷰가 바꾼 트리를 승인하지 못하게 하는 검사와 거짓 범위 넘음 알림 정리를 사용자가 설치본으로 받을 수 있게 한다

## Actions

- `python3 stage/scripts/release_plugin.py stage --bump minor` 로 `## Unreleased` 의 W-00000309·310(리뷰 쓰기 검사)과
  W-00000311(범위 넘음 알림) 항목을 0.64.0 절로 옮기고 두 매니페스트를 올린다. 리뷰 결과가 달라지는 동작 변경이라
  패치가 아니라 마이너로 올린다.
- 설치본 업데이트(`claude plugin update stage@noory-ai`)는 사람이 로컬에서 한다. 이 클라우드 세션의 범위가 아니다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage 매니페스트 두 개의 버전이 0.64.0 이고, CHANGELOG 의 0.64.0 절에 리뷰 쓰기 검사와 범위 넘음 알림 항목이 있으며 그 위에 빈 Unreleased 절이 있다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-11-01

```
What changed: release_plugin.py titled the queued Unreleased entries as 0.64.0 — 2026-11-01, opened a new empty Unreleased section, and moved both Stage manifests from 0.63.5 to 0.64.0.
Why: W-00000312 - let users install the review write check and the scope-report cleanup.
Decisions made: Bump minor, not patch, because failing reviews that change repository files alters review outcomes for existing projects; leave updating installs to the person on their machine, which this cloud session cannot reach; out-of-scope paths changed: none.
Work not done: Installs are not updated (claude plugin update stage@noory-ai and a restart on the person's machine).
```

## Verification


### Executed at close — 2026-11-01

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q
[exit 0]
----------------------------------------------------------------------
Ran 8 tests in 0.360s

OK

$ python3 -m unittest discover -s stage/scripts/tests -p test_release_plugin.py -q
[exit 0]
----------------------------------------------------------------------
Ran 8 tests in 0.376s

OK
```

## Retrospective


## Promotion decision
