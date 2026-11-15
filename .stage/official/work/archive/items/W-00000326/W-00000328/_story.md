---
id: W-00000328
title: 등급 표 설정을 읽어 등록하는 카드에 tier 를 적는다
kind: development
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_model_tiers.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000328
promotion: not_applicable
review: passed
scope: stage/hooks/stage_model_tiers.py, stage/hooks/stage_work.py, stage/skills/stage-work/, stage/scripts/start_work.py, stage/templates/project-stage/settings.json, stage/docs/SCHEMA_V5.md, stage/hooks/tests/test_model_tiers.py, stage/scripts/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000328 등급 표 설정을 읽어 등록하는 카드에 tier 를 적는다

## Purpose

일감을 등록하거나 시작할 때 설정의 등급 표가 고른 등급이 카드에 남게 한다

## Actions

하나의 구현 단위라 action 으로 나누지 않는다.

## User value

일감을 등록하는 사람이 모델을 따로 고르지 않아도 카드에 맞는 등급이 남는다. 나머지 story(드라이버·훅·감사)가 읽을 `tier:` 와 공용 모듈이 여기서 생긴다.

설계 SSOT: `.stage/work/current/W-00000326/W-00000327/_story.md` 의 `## Design` 중 "설정: model_tiers", "설정: tier_routing", "공용 모듈", "카드: frontmatter tier:" 를 먼저 읽는다.

## Scope

### Included

- `stage/hooks/stage_model_tiers.py` 새 공용 모듈: `model_tiers`·`tier_routing` 읽기, kind×크기로 등급 고르기, 등급과 venue 로 `model`·`effort` 꺼내기, 선언 순서로 등급 비교, 모델 별칭 비교(`[...]` 꼬리표 떼고 실제 id 에 별칭이 들어 있는지)
- `stage/hooks/stage_work.py` 의 `WorkItem` 에 `tier` 필드
- `register_work.py` 의 자동 등급과 `--tier`, `start_work.py` 의 빈 `tier:` 채우기
- 템플릿 `settings.json` 에 claude 칸만 채운 네 등급과 `tier_routing` (`"*": "standard"`)
- `stage/docs/SCHEMA_V5.md` 와 `stage/skills/stage-work/SKILL.md` 에 설정 모양·`tier:` 규칙
- 시험: `stage/hooks/tests/test_model_tiers.py`, 필요한 `stage/scripts/tests/` 시험
- `stage/CHANGELOG.md` 의 `## Unreleased` 한 줄 (매니페스트 버전은 바꾸지 않는다)

### Excluded

- 드라이버 환경 변수(W-00000329), Agent 훅(W-00000330), 감사(W-00000331)
- 이 저장소의 `.stage/settings.json`

## Risks

- 기존 카드 파서가 모르는 frontmatter 키를 거부하면 `tier:` 가 있는 카드가 깨진다. 파서와 감사의 허용 키 목록을 확인한다.
- `model_tiers` 가 없는 프로젝트의 등록 결과가 한 글자라도 바뀌면 안 된다.


## Success criteria

- model_tiers 와 tier_routing 을 둔 프로젝트에서 register_work.py 로 등록하거나 start_work.py 로 시작한 카드의 frontmatter 에 kind 와 크기로 고른 tier 가 적힌다
- --tier 로 등급을 직접 주거나 사람이 카드의 tier 를 고치면 그 값이 남고, 표에 없는 등급 이름은 등록이 거부된다
- model_tiers 가 없는 프로젝트에서 등록한 카드에는 tier 줄이 생기지 않는다

## Next action

이 세션의 Claude 가 local-no-codex 환경으로 직접 구현하고, 닫을 때 독립 리뷰를 받는다. 구현은 W-00000327 의 설계를 읽고 `stage_model_tiers.py` 와 그 시험부터 만든다.

## Related truth


## Progress


### Executor report at close — 2026-11-14

```
What changed: Added stage/hooks/stage_model_tiers.py (the one reader of model_tiers and tier_routing), WorkItem.tier, register_work.py --tier and routed tier on current and planned cards, start_work.py keeping and filling tier:, Claude-only tiers in the v4 settings template with comments free of backticks and free of driver or hook behavior that later cards add, the SCHEMA_V5 "Model and effort tiers" contract, the stage-work skill note, a CHANGELOG entry, and 20 tests in stage/hooks/tests/test_model_tiers.py.
Why: The card's purpose is that registering or starting work records the tier the settings table picks; the driver, hook, and audit stories need the card field and one shared reader.
Decisions made: Executed in this Claude session under environment local-no-codex because the Codex executor rejected gpt-6-astra on the current ChatGPT login (the user chose this). Edited the real init template stage/templates/v4/project-stage/settings.jsonc instead of the unused stage/templates/project-stage/settings.json named in scope, a scope boundary crossing. The template ships only claude columns because no codex or agy model name was verified. Invalid tier settings make registration and start refuse while runtime readers treat them as no tiers. Captured cards record the routed tier at capture; start fills only a missing tier. Template comments describe only what this card ships; W-00000329 and W-00000330 add their own behavior to them. Confirmed the start tests discriminate by removing the tier ordering line (two tests failed) and restoring it.
Work not done: None
```

## Verification

- 닫기 리뷰는 Codex 를 쓸 수 없어 `STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 대역으로 돌린 같은 모델(Claude) 리뷰다. venue 를 건너간 리뷰가 아니다.
- 첫 닫기 리뷰 지적(accept): 템플릿 주석에 넣은 백틱이 `test_template_v4` 의 백틱 금지 시험을 깨뜨렸는데 실행 보고가 드러내지 않았다. 주석의 백틱을 모두 없앴고, 다음 카드가 할 드라이버·훅 동작 설명도 주석에서 뺐다. scripts 시험 736개와 hooks 시험이 모두 통과한다.

### Executed at close — 2026-11-14

```
$ python3 -m unittest discover -s stage/hooks/tests -p test_model_tiers.py -q
[exit 0]
----------------------------------------------------------------------
Ran 20 tests in 1.722s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 418 tests in 11.597s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (270 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1794628369
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1794628369. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /private/var/folders/wg/6hnd_f255_z4ngk7ynwptym40000gn/T/tmpuc5sbsd5/unattended/W-00000001-1794628369
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 736 tests in 152.718s

OK (skipped=2)
```

### Review at close — 2026-11-14

```
Review report: .stage/.runtime/driver/logs/W-00000328.md
Criteria:
- PASS: model_tiers 와 tier_routing 을 둔 프로젝트에서 register_work.py 로 등록하거나 start_work.py 로 시작한 카드의 frontmatter 에 kind 와 크기로 고른 tier 가 적힌다
  Reason: Ran python3 -m unittest discover -s stage/hooks/tests -p test_model_tiers.py -v: 20 tests OK; subprocess tests run the real register_work.py and start_work.py and show story/action/epic cards get kind-and-scale routed tiers (standard, strong, scout) via TierConfig.route and fill_missing_tier.
- PASS: --tier 로 등급을 직접 주거나 사람이 카드의 tier 를 고치면 그 값이 남고, 표에 없는 등급 이름은 등록이 거부된다
  Reason: Same run passed test_explicit_tier_overrides_routing, test_captured_card_records_tier_and_start_keeps_it (hand-edited tier: strong survives start), and test_unknown_tier_name_is_refused / test_routing_to_unknown_tier_is_refused (nonzero exit, no card created); resolve_tier checks rank before any write.
- PASS: model_tiers 가 없는 프로젝트에서 등록한 카드에는 tier 줄이 생기지 않는다
  Reason: Same run passed test_without_model_tiers_no_tier_line_and_tier_flag_is_refused and test_start_without_model_tiers_writes_no_tier (no tier: in the card); set_optional_field skips an empty tier and route returns empty when tiers is None.
- PASS: Executor report follows the purpose and scope-boundary reporting contract (Decisions made / Work not done)
  Reason: Latest report restates every earlier decision, names the settings.jsonc-instead-of-settings.json scope crossing and the Claude-instead-of-Codex execution; Work not done: None is now true because I ran the full hooks suite (418 OK) and scripts suite (736 OK, 2 skipped) and the template has no backticks.
```

## Retrospective


## Promotion decision
