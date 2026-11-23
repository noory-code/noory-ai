---
id: W-00000409
title: 세션의 맨 위 층이 기록에서 만든 색인을 싣는다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000409
promotion: not_applicable
review: passed
scope: stage/hooks,stage/scripts,stage/skills,stage/operations,stage/templates,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md,.stage/decisions/index.md,.stage/research/README.md,.stage/work/current/_story.md,.stage/work/current/_epic.md,.stage/work/current/_template.md
promotes:
decision_refs:
---

# W-00000409 세션의 맨 위 층이 기록에서 만든 색인을 싣는다

## Purpose

기기의 세션과 클라우드 세션이 같은 작은 색인을 맨 위 층으로 받고, 필요한 결정과 기록의 본문을 거기서 찾아 꺼내 쓴다 (DE-00000100)

## Actions


## User value


## Scope

### Included

- DE-00000100 의 "Where this applies" 표의 줄. 색인을 쓰는 코드 가운데 실제로 줄을 쓰는 곳은 이 카드가 가린다.


### Excluded

- 매번 같은 규칙 문장을 줄이는 일. M-00000006 의 (가)가 빼 보며 판정한다. 줄이지 못해 결정 제목이 다 실리지 않으면 그렇다고 보고한다.
- 규칙 후보 66건의 첫 정리와 정리 세션을 실제로 띄우는 일.
- 작업 로그 원문을 커밋하는 일.


## Risks


## Success criteria

- 세션 시작에 싣는 글이 읽을 때 기록에서 만든 색인이고 본문을 싣지 않으며, 전체가 10,000자를 넘지 않는다
- 상한을 넘을 때는 지금 하는 일을 남기고 오래된 결정 제목부터 덜어내며, 덜어낸 건수와 읽을 자리를 한 줄로 남긴다
- 클라우드 작업 세션의 브리핑이 훅과 같은 색인을 받는다
- 결정 색인이 결정마다 제목을 싣는다
- 카드에 그 일을 한 세션의 번호를 적는 자리가 있고, 외부 자료의 자리(research/<주제>/sources.md)와 규칙 후보 정리 세션을 띄우는 때와 그 경계(본문을 고치지 않고 제안까지만)가 절차에 적혀 있다

## Next action

없음. 닫고 보관한 뒤 병합한다.


## Related truth

- DE-00000100, `.stage/research/memory-layers/`, W-00000400
- 알고 고른 약점: 상한 10,000자는 잰 값이 아니고, 색인의 효과를 잴 기록이 지금 없다. 세션이 실린 줄을 썼는지 잴 자리를 만들 수 있으면 만들고, 못 만들면 보고에 적는다.
- 클라우드 세션은 SessionStart 층을 받지 않는다(최근 닫힌 카드가 모두 클라우드다).
- 목적과 성공 기준은 지휘 세션이 사용자의 위임(2026-11-23)으로 DE-00000100 에서 옮겨 적었다.


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 691b177a 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6P2o521MckQ6RaB1e7 (`claude/w409-top-layer-index`)를 띄웠다. 번호 묶음은 잡지 않았다.


- 2026-11-23 작업 세션 session_018VXR6P2o521MckQ6RaB1e7 가 7acb9920 을 보고했다. 성공 기준 1-5 를 주장했다. 지휘 세션이 squash 커밋에서 scripts 945, hooks 480 통과와 audit 오류 0 을 다시 확인했다. 53개 경로가 바뀌었고 범위 밖은 다섯 곳이다(공식 결정 색인, 작업 보관 색인, `.stage/operations/session-hooks.md`, `mechanisms.md` 의 D1 행, `stage/docs/SCHEMA_V5.md`).
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: 규칙 후보 목록의 자리와 형식, 승격 의도 없이 채운 색인 397줄, DECISION005 가 오류라는 것, 첫 실행에 결정 제목 3건이 빠지는 것.
- 색인에 실려서 연 기록: 작업 세션은 보고하지 않았다(브리핑이 색인보다 먼저 쓰였다).
- Follow-up candidate: 지금 있는 규칙 후보 62-66건을 `.stage/state/rule-candidates.md` 로 처음 정리한다.
- Follow-up candidate: 정리 세션의 브리핑을 생성한다(`subsession_brief.py --role consolidate`).
- Follow-up candidate: 다른 프로젝트의 작업 보관 색인에 제목을 채우는 명령.
- Follow-up candidate: `## Current work hierarchy` 와 `### Active work` 가 같은 카드를 두 번 싣는다(약 550자). 줄이면 빠진 제목 3건이 들어간다.
- Follow-up candidate: Codex 쪽 훅이 같은 `session_context()` 를 쓰는지 확인한다.

### Executor report at close — 2026-11-23

```
What changed: New stage/hooks/stage_memory_index.py holds the decision-title lines, the rule-candidate lines, the find lines, and fit_blocks, the function that enforces the limit; stage_context.session_context is now the unchanged rule sentences plus stage_context.session_index, and the lifecycle view was removed; subsession_brief.py appends session_index to the work and verify briefs and keeps brief plus index within 10,000 characters, and the work brief asks for the ids of records opened from the index; refresh_decision_index.py renders a Title column in the pending index and fills a Title column in the hand-written official index (new audit code DECISION005 when it is missing or stale); manage_roadmap.py and migrate_stage.py write or refresh titled official rows; archive_work.py writes the card title as the last cell of a new archive row and widens a three-column header; start_work.py and the current-card templates add a Sessions section; cloud-execution.md, the stage-orchestrate skill, rule-promotion.md, the stage-retrospective skill, operations/retrospective.md, hooks docs, BLUEPRINT.md, CHANGELOG.md and .stage/research/README.md describe the index, the limit, the Sessions line, the place for external sources, and the consolidation session.
Why: DE-00000100 chose a record-derived index as the top layer for device and cloud sessions alike, a 10,000-character limit that sheds the oldest decision titles first, session ids on the card, research/<topic>/sources.md as the place for external sources, and a consolidation session that only proposes.
Decisions made: (1) The rule sentences are untouched (the card excludes shortening them), so in this repository the text is already at the limit: 79 of 82 decision titles are shown and the 3 oldest are left out (9,928 characters). (2) Shedding order after decision titles is rule candidates, the previous session handoff, the instruction-file list, the operations-file list; when the never-shortened lines alone exceed the limit the end is cut with a marker, which can cut the observation list that hooks/README.md calls complete by contract. (3) The index lists pending and official decisions and leaves out the decision archive, which holds closed records that no longer bind. (4) The index is built only for the current topology; the legacy topology gets the rules and the current-work blocks under the same limit, because the legacy-literal baseline test forbids new legacy path consumers. (5) Rule candidates are read from a new file .stage/state/rule-candidates.md with a required through: R-id; this card defines its place and format and does not create it, so today the index shows one line counting 62 retrospectives that state a candidate. The index says a consolidation is due when 20 or more retrospectives are newer than through. (6) Where a session used the index is recorded only as the session's own account: the work brief asks for the ids it opened from the index and the main session copies them to the card's Sessions line; no hook measures it, and cloud sessions have no hook. (7) Title columns: of the index writers DE-00000100 lists, the ones that write rows are refresh_decision_index.py (pending index), manage_roadmap.py (official decision rows for chain decisions), archive_work.py (work archive rows, decision archive rows) and close_record.py (moves an existing line); init_stage.py, the two migration scripts and stage_topology.py only name the paths or copy files. Titles were added to the pending index, the official decision index and work archive rows. The decision archive index and the state and proposal archive indexes were left as they are: the first lists spent venue exceptions and the others move lines that already carry a title. (8) refresh_index() stays pending-only so close, archive and escalate never rewrite the official index; refresh_decision_index.py's command line, manage_roadmap.py and migrate_stage.py refresh official titles explicitly. A project upgrading sees DECISION004 and DECISION005 until it runs the command once. (9) A consolidation session gets its first message from the orchestrator by hand; no subsession_brief role was added. (10) Changed outside the card's scope: .stage/official/decisions/index.md (67 rows gained the title column through refresh_decision_index.py, needed for the criterion that the decision index carries titles), .stage/official/work/archive/index.md (330 rows backfilled with titles by a one-off script that is not committed, so old and new rows have the same cells), .stage/operations/session-hooks.md and .stage/research/claude-fit/mechanisms.md (DE-00000100 names both as documents that state the composition and size), stage/docs/SCHEMA_V5.md (it lists the sections a started card gains).
Work not done: Shortening the rule sentences, the first consolidation of the existing candidates, starting a consolidation session, and committing raw work logs are excluded by the card. .stage/state/rule-candidates.md is not created and is not listed in .stage/index.md or the index templates. No backfill command exists for another project's work archive index; only its header is widened when the next row is written. The W-00000409 card itself has no Sessions section because it was started before the change and the main session owns the card. Nothing was run on Windows; the changed code uses pathlib and explicit utf-8 and has no platform branch, and the pull request's Windows CI job is the check. Whether a Codex-side hook calls the same session_context was not checked.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Checks at close 2026-11-23: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 -m unittest discover -s stage/hooks/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS ran, 4 PASS ran, 5 PASS ran, 6 PASS read)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
