---
id: W-00000410
title: 지난 카드들의 보고에 남은 작은 고침 넷을 넣는다
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
retrospective_ref: R-00000410
promotion: not_applicable
review: passed
scope: stage/scripts,stage/hooks,stage/skills,.github/workflows/stage.yml,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000410 지난 카드들의 보고에 남은 작은 고침 넷을 넣는다

## Purpose

지난 카드들의 보고에만 남아 있던 작은 고침 넷이 코드와 CI 에 들어가서, 같은 후보가 다음 보고에 다시 오르지 않는다 (O-00000061)

## Actions


## User value


## Scope

### Included


### Excluded

- 매번 같은 규칙 문장을 줄이는 일(M-00000006 의 (가)가 판정한다). 넷째 기준이 그것 없이는 채워지지 않으면 채워지지 않는다고 보고한다.
- 다른 프로젝트(Dasina)의 설정을 고치는 일, 규칙 후보의 첫 정리, 토론·계획 세션의 브리핑, 스킬 줄이기.


## Risks


## Success criteria

- CI 가 release_plugin.py --check-released --since 0.67.0 을 돌려, 릴리스된 변경 기록 절에 뒤늦게 더해진 줄이 있으면 실패한다
- 쓰인 기록 번호를 세는 코드가 한 곳에 있고 번호를 고르는 곳들이 그것을 쓴다
- model_fallbacks 를 선언했는데 그 명령에 $STAGE_MODEL 이 없으면 audit 가 경고한다
- 세션 색인이 같은 카드를 두 번 싣지 않고, 그렇게 줄어든 자리로 이 저장소의 결정 제목이 모두 실린다

## Next action

없음. 닫고 보관한 뒤 병합한다.


## Related truth

- O-00000061 의 "그 전 카드들에서 나온 것", W-00000409 의 후속 후보(같은 카드를 두 번 싣는 약 550자), W-00000392 와 W-00000396(`--check-released`, `fetch-depth: 0` 이 필요하다), W-00000386(`model_fallbacks`).
- 목적과 성공 기준은 지휘 세션이 사용자의 위임(2026-11-23)으로 그 목록에서 옮겨 적었다. 사용자가 고른 묶음이 아니다.


## Sessions

- session_018VXR6QTeKjAAj8MoTZaY5B — work — 2026-11-23 — opened from the index: O-00000061


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 340510d1 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6QTeKjAAj8MoTZaY5B (`claude/w410-small-fixes`)를 띄웠다. 브리핑이 색인을 달고 12,613바이트가 되어, 첫 메시지에 본문을 옮기지 않고 세션이 같은 명령으로 브리핑을 스스로 내어 읽게 했다.


- 2026-11-23 작업 세션 session_018VXR6QTeKjAAj8MoTZaY5B 가 5150d29b 를 보고했다. 성공 기준 1-4 를 주장했다(넷째는 여유 40자). 지휘 세션이 squash 커밋에서 scripts 950, hooks 483 통과와 audit 오류 0 을 다시 확인했다. 범위 밖 변경은 `stage/docs/SCHEMA_V5.md` 한 곳이다.
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: 얕은 체크아웃에서 `--check-released` 를 거부하는 것, 트리에 번호와 상태가 남는 것.
- 2026-11-23 닫기 리뷰가 둘째 기준을 반려했다: `register_work.existing_numbers` 와 `migrate_stage.next_work_number` 가 아직 따로 센다. 작업 세션에 돌려보냈다.
- 2026-11-23 작업 세션이 f5994ad8 을 보고했다. 따로 세던 자리를 모두 `used_numbers` 아래로 옮겼고 하나 더 찾아 없앴다(`stage_topology.next_artifact_id`). 지휘 세션이 두 번째 squash 에서 scripts 953, hooks 483 통과와 audit 오류 0 을 다시 확인했다. 두 번째 squash 는 충돌이 나서 작업 브랜치의 파일을 그대로 받아 풀었고 코드가 작업 브랜치와 같은 것을 확인했다.
- Follow-up candidate: 리뷰가 반려된 뒤의 두 번째 squash 는 충돌한다. `cloud-execution.md` 가 그때 할 일(작업 브랜치의 파일을 받는다)을 말하지 않는다.
- Follow-up candidate: 다른 브랜치에 파일 이름으로만 있는 옛 너비의 번호는 세지 않는다.
- Follow-up candidate: 색인의 여유가 40자다. 규칙 문장을 줄이거나 상한을 다시 정한다(M-00000006 의 (가)).
- Follow-up candidate: `register_work` 의 옛 구조 폴더 훑기와 `migrate_stage.next_work_number` 를 `used_numbers` 아래로 모으거나, 옛 구조는 범위 밖이라고 적는다.
- Follow-up candidate: `review.strengths` 명령의 TIER007 은 설정이 그 강도가 어느 venue 로 도는지 말해야 가능하다.

### Executor report at close — 2026-11-23

```
What changed: Whole card, both commits. (1) .github/workflows/stage.yml gains a changelog job (ubuntu, fetch-depth 0) that runs release_plugin.py stage --check-released --since 0.67.0; release_plugin.py --check-released exits 2 on a shallow checkout. (2) stage_record_ids.used_numbers(project_root, prefix, reserver) is the one count of taken numbers: ids in the checkout's .stage records (id line, title heading, or file name at any id width), reserved_ids blocks, fetched branches, remote reservations, with prefixes that share a counter (DE and legacy D) counted together. next_record_id, stage_id_blocks.reserve_block, register_work, manage_roadmap._create_atomic, escalate_work.next_decision_id and migrate_stage.next_work_number pick from it and read no record folder of their own; register_work.existing_numbers, manage_roadmap's two existing-id scans and stage_topology.next_artifact_id are removed. (3) audit_model_tier.py reports warning TIER007 for each venue in model_fallbacks whose executors.<venue> or review.reviewers.<venue> command does not contain STAGE_MODEL. (4) stage_context.work_hierarchy_view takes listed_statuses; session_index passes the statuses of the two work tables, so a card with no parent and no child is left out of the tree, a card inside a tree is named by id and status only, and the section is omitted when nothing remains. Tests, the stage-audit skill, SCHEMA_V5.md, BLUEPRINT.md and CHANGELOG.md follow.
Why: The card's four success criteria, taken from O-00000061 and the W-00000409 follow-up candidate; the second commit answers the close review's FAIL on the second criterion.
Decisions made: (1) The changelog check is a job of its own so the eighteen matrix jobs keep their shallow checkout. (2) Added a shallow-checkout refusal to --check-released, which the card did not ask for: on a depth-1 checkout the oldest commit seems to add every heading, so every section is compared with itself and the check passes whatever was merged; the main session accepted it under the user's delegation of 2026-11-23. (3) used_numbers lives in stage_record_ids.py next to the functions it joins. (4) To bring the legacy readers under it, used_numbers was taught two things instead of each caller keeping a scan: a record file named <prefix>-<three or more digits>[-topic].md counts by its name (v3 cards such as W-012.md carry no eight-digit id line), and prefixes sharing a counter family in stage_topology.ARTIFACT_PREFIXES are counted together. The .runtime folder stays excluded. (5) Behaviour changes that follow: stage_record_ids.py DE and escalate_work no longer offer a number a legacy D- record holds (manage_roadmap already avoided it); an escalation decision id and a converted v3 backlog item skip numbers used on fetched branches and in reserved_ids blocks; escalation and migration reserve nothing on the remote; a file-named id of legacy width on another branch is not counted, because the branch scan reads id lines and headings of eight digits only, as before. (6) Removed stage_topology.next_artifact_id: after manage_roadmap moved to used_numbers it had no caller, and a second max-plus-one function invites the next picker to count on its own. Its refusal to mint the legacy D prefix went with it; no command mints D. (7) Searched hooks, scripts and skills for max(...) + 1 and :08d formatting: the remaining sites are next_record_id, reserve_block, register_work's two atomic creators (they receive used_numbers), manage_roadmap._create_atomic, escalate_work.next_decision_id and migrate_stage.next_work_number, all starting from used_numbers. Retrospective ids are derived from the card id (R-<card number>) and pick nothing. (8) TIER007 judges only commands that settings bind to a venue by name (executors, review.reviewers); a review.strengths command is not judged because settings do not say which venue it runs as. It is checked even without model_tiers, like TIER006, with the same test the driver uses at run time. (9) The index keeps the two work tables, which other skills and the index template name, and removes the repetition from the tree; a card inside an epic still appears in the tree by id and status, accepted by the main session under the same delegation. (10) Measured on this repository with this card active: the hook text went from 9,930 characters with 79 of 82 decision titles to 9,960 with all 82; the unbounded text was 10,038, so 40 characters are left and the next decision or a second current card drops titles again. The card excludes shortening the rule sentences, so the fourth criterion holds today and not durably. (11) Changed outside the card's scope: stage/docs/SCHEMA_V5.md, because it states the TIER code range and what happens when a command does not read STAGE_MODEL; both needed TIER007.
Work not done: Nothing was run on Windows or macOS; the pull request's CI jobs are the check, and the shallow-checkout test clones through a file URI there for the first time. The new changelog job itself has not run; its command was run locally (exit 0) and its shape is asserted by test_ci_workflows.py. stage/operations/cloud-execution.md still describes the index without saying a card is listed once; it is outside the scope and not wrong. No record was created.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Review at close 2026-11-23 by claude_review_companion: rejected (1 PASS ran, 2 FAIL read, 3 PASS ran, 4 PASS ran)

- Checks at close 2026-11-23: 2 passed — `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 -m unittest discover -s stage/hooks/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS ran, 4 PASS ran)
- Load at close 2026-11-23: attempts 2, review FAIL rounds 1, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
