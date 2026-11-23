---
id: W-00000417
title: 세션 시작의 고정 규칙 문장을 줄여 색인의 자리를 만든다
kind: development
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000417
promotion: not_applicable
review: passed
scope: stage/hooks/stage_context.py,stage/hooks/stage_memory_index.py,stage/hooks/tests,stage/hooks/README.md,stage/operations/hooks.md,.stage/operations/session-hooks.md,.stage/research/memory-layers,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000417 세션 시작의 고정 규칙 문장을 줄여 색인의 자리를 만든다

## Purpose

세션 시작 글에서 매번 같은 규칙 문장이 차지하던 자리가 줄어서, 진행 중인 카드가 여러 장이어도 결정 제목이 색인에서 빠지지 않는다 (DE-00000100)

## Actions


## User value


## Scope

### Included


### Excluded

- 훅이 막는 동작을 바꾸는 일.
- 상한 10,000자를 바꾸는 일. 줄여도 기준을 채울 수 없으면 그렇다고 보고한다.


## Risks


## Success criteria

- 세션 시작 글의 고정 규칙 문장이 지금보다 1,500자 넘게 줄고, 덜어낸 문장마다 그 내용을 이미 말하는 자리(훅의 거부 문구, 스킬, 운영 문서)가 연구 자료에 적혀 있다
- 진행 중인 카드 다섯 장과 규칙 후보 39건이 있는 상태에서 이 저장소의 결정 제목이 모두 실린다
- 훅이 막는 동작과 거부할 때 내는 문구는 바뀌지 않았다

## Next action

없음. 닫고 보관한 뒤 병합한다.


## Related truth

- `.stage/research/memory-layers/measurements.md`: 세션 시작 글의 68% 가 매번 같은 규칙 문장과 경로 목록이다(규칙 문장 3,373자).
- W-00000409, W-00000410, W-00000413: 색인의 여유가 40자였고, 진행 중 카드 다섯 장과 규칙 후보 39건이 있을 때 결정 제목 82건 가운데 63건이 실렸다.
- M-00000006 의 (가): 하중을 확인하지 못한 장치는 덜어낸다. 이 문장들의 하중은 잰 적이 없다. 클라우드 세션은 이 글을 받지 않고 브리핑의 색인만 받는다.
- 사용자가 2026-11-23 에 실기기에서 해야 할 일만 두고 나머지를 진행하라고 했다("실기기에서 해야할 일은 두고 나머지는 합시다"). 목적과 성공 기준은 지휘 세션이 옮겨 적었다.


## Sessions

- session_018VXR6RJNk1s8m8M3F7rQwV — work — 2026-11-23 — opened from the index: DE-00000100, DE-00000093


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 2401aebb 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6RJNk1s8m8M3F7rQwV (`claude/w417-shrink-rule-text`)를 띄웠다. 번호 묶음은 잡지 않았다.


- 2026-11-23 작업 세션 session_018VXR6RJNk1s8m8M3F7rQwV 가 8a339938 을 보고했다. 성공 기준 1-3 을 주장했다. 고정 규칙 글이 3,373자에서 1,384자가 됐다. 지휘 세션이 squash 커밋에서 hooks 489, scripts 1004 통과와 audit 오류 0 을 다시 확인했고, 이 체크아웃(진행 중 카드 네 장, 규칙 후보 39건)에서 색인을 내 보니 9,985자에 결정 제목 82건이 모두 실리고 후보 14건이 실렸다. 범위 밖 변경은 `stage/scripts/tests/test_schema_v4_consumers.py` 와 `stage/README.md` 다.
- 2026-11-23 사용자가 볼 것으로 남긴 것: 여섯 원칙의 요약과 산출물 지도를 기기에서 관찰하지 않고 뺀 것(O-00000062).
- Follow-up candidate: 생긴 자리를 규칙 후보가 가져가 전체가 다시 상한에 닿는다. 상한이나 싣는 후보의 수를 정한다.
- Follow-up candidate: 줄인 규칙으로 기기의 세션이 더 자주 거부되는지 관찰한다.
- Follow-up candidate: venue 줄이 `.stage/operations/claude-venue.md` 를 그 파일이 없어도 가리킨다. 라우팅 줄이 kind 수만큼 길어진다.

### Executor report at close — 2026-11-23

```
What changed: stage/hooks/stage_context.py builds the standing rules through a new standing_rule_lines(): one lifecycle line that names `.stage/index.md` and the principle catalog, one line for the two write gates, the inline-interpreter line (285 -> 203 characters), the venue routing line (947 -> 525), the document language line (338 -> 211). Removed: the space-axis line, the six principle summaries, "Cite the governing principles in every decision record and retrospective", the artifact map, the venue exception/split/planning-venue sentences. The legacy (v3) branch is shortened the same way. Measured in this repository with session_context(): rules 3,373 -> 1,384 characters (-1,989); with the four cards in progress now, 76 of 82 decision titles and 0 of 39 candidates before, 82 of 82 and 14 candidates after; with a fifth card added in a copy of `.stage/` outside the repository, 82 of 82 and 13 candidates, 9,983 characters in total. Two new tests in stage/hooks/tests/test_session_index.py (five cards + 39 candidates + 82 decisions list every title; the rules stay within 1,500 characters) fail on the old text and pass on the new. `.stage/research/memory-layers/rule-text.md` lists every old line, its size, what was done, and the place that already states it. Documents updated: stage/hooks/README.md, stage/operations/hooks.md, .stage/operations/session-hooks.md, stage/docs/BLUEPRINT.md, stage/README.md, stage/CHANGELOG.md.
Why: The card's purpose (DE-00000100): the fixed rule text took the room the index needs, so decision titles were left out when several cards were in progress. M-00000006 (a): a device whose load was never measured is removed.
Decisions made: (1) Kept, shortened, three lines that an earlier release added on purpose or that carry project settings: the inline-interpreter rule (0.66.1: "A session used to learn this only from the denial"), how each venue runs (teammate, driver, claude-venue.md), and the routing table and document language. (2) The registration and promotion gates became one line that leaves the command to the hook's refusal, which already names stage-work, register_work.py, stage-retrospective and promote_intent.py. (3) Removed "cite the governing principles in every ... retrospective" as wrong, not only as duplicate: since DE-00000093 a retrospective has no such section (stage/operations/retrospective.md). (4) The legacy topology branch got the same lines, so both topologies say one thing. (5) The removal rests on "another place states it", not on a measurement that sessions did not use the sentences; that load is still unmeasured and the research note says so. (6) Paths changed outside the card's scope: stage/scripts/tests/test_schema_v4_consumers.py, because two of its tests asserted folder names that only the removed artifact map carried (`decisions/pending`, `state/questions`, `work/planned`, `roadmap/`, `future/backlog/items`), and they now assert the registry-derived paths the rules still carry; stage/README.md, because its SessionStart line said the hook injects "core principles, and the artifact map", which is no longer true.
Work not done: No check on a device: hooks do not run in this cloud session, so the text was produced by calling session_context() directly, and whether a device session is refused more often with the shorter rules was not observed. No Windows run. The limit of 10,000 was not changed; the total is still 9,983 because rule candidates fill the freed room.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Checks at close 2026-11-23: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS ran, 4 PASS read)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
