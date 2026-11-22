---
id: W-00000395
title: 새 코드 파일은 도면 레이어 표에 넣는다는 규칙을 올린다
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
retrospective_ref: R-00000395
promotion: not_applicable
review: passed
scope: stage/CLAUDE.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000395 새 코드 파일은 도면 레이어 표에 넣는다는 규칙을 올린다

## Purpose

Stage 에 새 코드 파일을 만드는 카드가 BLUEPRINT 레이어 표를 함께 고친다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage/CLAUDE.md 의 BLUEPRINT 규칙이 새 코드 파일을 레이어 표에 넣으라고 말하고 근거 회고 R-00000389 를 인용한다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: The BLUEPRINT rule in stage/CLAUDE.md now says a change that adds a code file under hooks/, scripts/, or skills/ (tests excepted) adds it to the blueprint's layer table in the same change, citing R-00000389; stage/CHANGELOG.md has an Unreleased entry.
Why: W-00000395 promotes R-00000389's rule candidate; it happened twice in one day (W-00000381, W-00000388), which meets the "happened twice" test in rule-promotion.md.
Decisions made: Amended the existing BLUEPRINT rule instead of adding a new one, as rule-promotion.md asks; placed it in stage/CLAUDE.md rather than .stage/operations/ or the plugin's operations/ because it binds work on the Stage plugin's own code in this repository, and stage/CLAUDE.md already owns the rule it extends; excepted tests because the layer table lists no test files; checked the current table: every hooks/ and scripts/ file is listed except scripts/release_plugin.py, which the blueprint already places outside the layers.
Work not done: None.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 성공 기준: `stage/CLAUDE.md` 의 도면 규칙이 `hooks/`, `scripts/`, `skills/` 에 새 코드 파일(시험 제외)을 만들면 같은 변경에서
  레이어 표에 넣으라고 말하고 R-00000389 를 인용한다.
- 지금 `hooks/*.py`, `scripts/*.py` 가운데 레이어 표에 없는 것은 `scripts/release_plugin.py` 하나이고, 도면이 그 파일을 레이어
  밖이라고 이미 적는다.
- 사용자가 2026-11-22 에 규칙으로 올리기로 했다("추천대로").
- 감사 오류 0건.

- Checks at close 2026-11-22: 1 passed — `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS)
