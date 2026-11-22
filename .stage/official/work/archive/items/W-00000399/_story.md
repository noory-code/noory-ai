---
id: W-00000399
title: Stage 의 통제 장치와 그것이 담은 가정을 목록으로 만든다
kind: planning
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000399
promotion: deferred
review: passed
scope: .stage/research/claude-fit/mechanisms.md
promotes:
decision_refs: DE-00000098
---

# W-00000399 Stage 의 통제 장치와 그것이 담은 가정을 목록으로 만든다

## Purpose

어떤 장치를 빼 볼지 고를 수 있도록 Stage 의 장치마다 '모델이 혼자서는 못 한다'는 가정이 무엇인지 보인다

## Actions


## User value

출발점이 된 글(사용자가 2026-11-23 에 준 주소):

- https://www.anthropic.com/research/components-of-agent-memory
- https://www.anthropic.com/research/managed-agents
- https://www.anthropic.com/research/building-c-compiler
- https://www.anthropic.com/research/harness-design-long-running-apps

마일스톤은 `.stage/roadmap/milestones/M-00000006.md` 다. Stage 의 지킬 강점은 세션이 끝나도 남는 장기 기억과 결정 기록이다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 장치 목록과 장치마다의 가정, 빼 볼 때 무엇으로 하중을 확인할지가 연구 자료에 있다
- 사용자가 먼저 빼 볼 장치를 골랐고 그 결정이 결정 기록에 있다

## Next action

## Related truth

## Progress

### Executor report at close — 2026-11-22

```
What changed: Added .stage/research/claude-fit/mechanisms.md (about 40 mechanisms in five groups with assumption, assumption kind, source incident, and load-check evidence, plus first-removal candidates with counter-arguments) and one index row in .stage/research/README.md.
Why: W-00000399 purpose: show, per Stage mechanism, the "model cannot do this alone" assumption so the user can choose which mechanism to remove first.
Decisions made: Classified assumptions into capability/independence/memory/accident/platform so only capability ones are removal candidates and the milestone's protected strengths (long-term memory, decision records) are kept out; used existing environment: cloud cards (50, counted by grep) as a ready control group for hook mechanisms because cloud sessions run without Stage hooks; measured the current SessionStart context by running the hook in this session (6,634 chars, 62 lines); proposed B1, B3, B11, A4/B7 as first candidates with counter-arguments but left the choice to the user; summarized the four source articles only through the milestone's sentence and did not fetch them; crossed the card scope by adding one row to .stage/research/README.md because that file is the research folder index and the new folder would otherwise be unreachable from it.
Work not done: The user's choice of the first mechanism to remove and its decision record (second success criterion; needs the user and a reserved decision id); the actual cloud-vs-local comparison; mapping retrospectives to the model that produced them; per-audit-check firing frequency.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6NWiJwbfntceZ1cdZs)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 커밋 e5abbbaf 의 변경 그대로를
  담은 로컬 커밋 3a3f5bb7 에서 닫았다. 브랜치에서는 메인 세션이 연구 색인 충돌을 풀며 줄을 하나로 합쳤다(1f779178).
- 성공 기준 1: `.stage/research/claude-fit/mechanisms.md` 에 장치 약 40개, 장치마다의 가정과 그 종류, 빼 볼 때 하중을 볼 자리가 있다.
- 성공 기준 2: 사용자가 2026-11-23 에 B11 을 먼저 빼 보기로 골랐다("추천대로 B11부터 해주세요"). DE-00000098 에 있다.
- 감사 오류 0건.

- Checks at close 2026-11-22: 1 passed — `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS)
