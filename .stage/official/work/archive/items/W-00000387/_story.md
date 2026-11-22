---
id: W-00000387
title: 다른 브랜치에서 이미 시작했거나 끝난 카드는 시작하지 않는다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000387
promotion: not_applicable
review: passed
scope: stage/scripts/start_work.py,stage/scripts/tests,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000387 다른 브랜치에서 이미 시작했거나 끝난 카드는 시작하지 않는다

## Purpose

두 세션이 같은 카드를 따로 하는 일이 시작하는 순간에 막힌다

## Actions


## User value

DE-00000094 의 "맡은 카드 표시"를 구현한다. 2026-11-21 에 메인 세션이 main 만 받아 온 채로 W-00000367 을 시작했는데, 그 카드는 `claude/w367-parallel-session-collisions` 브랜치에서 이미 닫히고 보관되어 있었다. `stage_record_ids.py` 가 이미 받아 온 모든 브랜치에서 번호를 세는 방식을 참고한다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 받아 온 다른 브랜치에서 같은 카드가 active 이거나 보관된 상태면 start_work.py 가 시작하지 않고 그 브랜치 이름을 출력하는 시험이 있고 통과한다
- 다른 브랜치에 같은 카드가 계획된 상태로만 있으면 지금처럼 시작된다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: start_work.py lists fetched local and remote-tracking branches that HEAD has not merged (`git for-each-ref --no-merged=HEAD`), reads each one's card locations with `git ls-tree`, and refuses with the branch name and `started`/`archived` when one holds the card under work/current or the work archive; a new test file covers started, archived, planned-only, and merged-then-replanned branches; stage/CHANGELOG.md has an Unreleased entry.
Why: W-00000387 implements the "맡은 카드 표시" part of DE-00000094; the main session restarted W-00000367 on 2026-11-21 while another branch had already archived it.
Decisions made: Read only branches HEAD has not merged, so a merged branch's state counts as already in this checkout and a card planned again after a merge stays startable; no override flag, the message tells the user to merge or delete the other branch; refs ending in /HEAD are skipped; when git is missing or the project is not a repository the check is skipped and start_work behaves as before; the v3 topology checks past/work/archive/items.
Work not done: None.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- `python3 -m unittest discover -s stage/scripts/tests -p test_start_work_other_branches.py -v`: 4개 통과. 다른 브랜치가 시작한 카드와 보관한 카드는 막고, 계획만 된 브랜치와 합친 뒤 다시 계획한 카드는 시작한다.
- 검사를 끄고(`if other_branches:` 를 `if False:` 로) 돌리면 막는 시험 2개가 실패한다.
- 이 저장소에서 계획된 카드 7장과 보관된 카드 2장으로 돌려 보니 잘못 막는 경우는 없었다. HEAD 가 합치지 않은 브랜치는 5개였고 한 번에 0.02~0.06초였다.
- 전체 시험: hooks 와 scripts 모두 통과, 감사 오류 0건.

- Checks at close 2026-11-22: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_start_work*.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
