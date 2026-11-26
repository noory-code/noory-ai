---
id: W-00000420
title: 사용자는 PO 세션하고만 이야기하고 그 아래 세션과 서브에이전트는 정한 이름과 자리로 일한다
kind: development
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000420
promotion: deferred
review: passed
scope: stage/skills/stage-orchestrate/SKILL.md,stage/scripts/subsession_brief.py,stage/scripts/started_cards.py,stage/operations/cloud-execution.md,stage/operations/review.md,stage/operations/retrospective.md,stage/skills/stage-retrospective,stage/skills/stage-handoff/SKILL.md,stage/skills/stage-drive/SKILL.md,stage/skills/README.md,stage/hooks/stage_memory_index.py,stage/hooks/tests,stage/scripts/tests,stage/docs/BLUEPRINT.md,stage/README.md,stage/CHANGELOG.md
promotes:
decision_refs: DE-00000103
---

# W-00000420 사용자는 PO 세션하고만 이야기하고 그 아래 세션과 서브에이전트는 정한 이름과 자리로 일한다

## Purpose

사용자가 PO 세션 하나하고만 이야기하고, 그 아래 계획·실행·검토·리서치 세션과 전문가 서브에이전트가 정해진 이름과 자리로 일한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 브리핑 스크립트가 plan, pm, verify, research 역할의 브리핑을 내고 discussion 과 consolidation 역할은 없다
- 어떤 하위 세션의 브리핑도 사용자에게 직접 묻지 말고 PO 세션에 보고하라고 한다
- PO 스킬이 대화를 갈무리해 계획 세션에 넘기고, 계획 세션이 일감 초안을 쓰고, PO 가 등록한다고 말한다
- 하위 세션의 브리핑이 DE-00000103 이 든 의사결정을 스스로 정하지 말고 만들기 전에 선택지와 추천을 PO 세션에 올리라고 한다
- PM 브리핑이 여러 조각으로 나뉘는 카드는 전문가 서브에이전트에 맡기고 검수하며 작은 카드는 직접 하라고 한다
- 세션 제목과 태그와 서브에이전트 이름이 DE-00000103 의 네이밍 룰을 따르고, 새 PO 가 옛 태그를 단 세션도 인수 목록에서 찾는다
- 규칙 후보 모으기는 Research 세션에 주는 과제이고 그 과제일 때만 목록 파일 하나를 쓴다

## Next action

닫기 리뷰를 받고 닫는다.

## Related truth

## Sessions

- session_018VXR6Rki1nPLNsnanfTae9 — work — 2026-11-25 — opened from the index: DE-00000103

## Progress

- 2026-11-25 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 구조와 이름은 사용자가 이 세션의 대화에서 정했고 DE-00000103 에 사용자의 말과 함께 적었다. 성공 기준 여섯 줄은 지휘 세션이 그 결정에서 옮겨 적었고, 사용자가 "왠만하면 니 추천을 따를 테니까 쭉쭉 진행해라"라고 한 위임으로 등록했다. 고칠 자리는 DE-00000103 의 "Where this applies" 에 있다.
- 범위 밖: 전문가별 읽을거리와 점검 기준, `stage-orchestrate` 스킬의 이름, 규칙 후보의 문턱(다음 카드), DE-00000101 의 닫기 관문.
- 이 카드의 작업 세션은 옛 브리핑(`--role work`)과 옛 제목으로 뜬다. 새 이름은 이 카드가 병합된 뒤의 세션부터 쓴다.
- 새 기록 번호는 잡아 두지 않았다. 이 카드는 새 기록을 만들지 않는다.
- 2026-11-25 사용자가 "모든 의사결정은 PO 에서 이뤄집니다."라고 했다. DE-00000103 에 "의사결정은 PO 에서 한다"를 더했고, 성공 기준 한 줄을 더했다. 작업 세션에 메시지로 알렸다.
- 2026-11-25 작업 세션 session_018VXR6Rki1nPLNsnanfTae9 가 b5d4ee33 을 보고했다. 처음 여섯 성공 기준을 채웠다고 했다(스크립트 시험 1036, 훅 시험 489 통과, audit 오류 0). 역할은 `pm`, `verify`, `plan`, `research` 이고 옛 이름은 거부한다. `--main-session` 은 `--po-session` 이 됐다. 범위 밖으로 `stage/scripts/stage_id_blocks.py` 와 `stage_record_ids.py` 의 설명과 오류 문구를 고쳤다. 새 브리핑으로 실제 세션을 돌려 본 적은 없다고 했다. 닫기 리뷰는 시작하지 않았다.
- 2026-11-25 지휘 세션이 작업 세션의 세 질문을 사용자의 위임으로 정했다: 사용자의 말에 목적과 성공 기준이 다 있으면 PO 가 바로 등록하고 아니면 계획 세션을 거친다. 비교할 선택지가 있는 조사는 리서치 세션, 답이 하나인 찾아보기는 서브에이전트. 옛 이름의 호환은 두지 않는다. 사용자가 보고 뒤집을 수 있다.
- 2026-11-25 지휘 세션이 일곱째 성공 기준("의사결정은 PO 에서")이 b5d4ee33 에 없어서 작업 세션에 둘째 커밋을 요청했다. 사용자가 같은 날 오늘 작업을 여기서 마무리하자고 했다.
- 2026-11-25 작업 세션 session_018VXR6Rki1nPLNsnanfTae9 가 둘째 커밋 4cca1ac 를 보고했다(앞 커밋 b5d4ee33 위). 일곱째 성공 기준을 채웠다고 했다: 다섯 브리핑 모두가 정할 것을 스스로 정하지 말고 만들기 전에 선택지와 추천을 PO 세션에 올리라고 하고, 스킬에 "Decide here" 가 생겼다. 스크립트 시험 1037, 훅 시험 489 통과, audit 오류 0 이라고 했다. 첫 커밋이 이미 만든 선택 넷(옛 이름의 호환 없음, PO 가 바로 등록하는 조건, 리서치 세션과 서브에이전트의 경계, 갈무리를 메시지로 넘김)을 선택지와 함께 다시 올렸다. 앞의 셋은 지휘 세션이 위임으로 정했고 사용자가 같은 날 "동의해요"라고 했다. 넷째도 지은 대로 둔다(위임). 닫기 리뷰는 시작하지 않았다. 사용자가 오늘 작업을 마무리했다.
- 2026-11-26 사용자가 작업을 이어가자고 했다. 지휘 세션이 두 커밋을 squash 커밋 3b88e47 로 가져와 훅 시험(489 통과), 스크립트 시험(1037 통과), `audit_stage.py`(오류 0)를 다시 돌렸다.
- 2026-11-26 지휘 세션이 스킬의 "Decide here" 가 더한 두 문장(이미 지은 결정은 정해지지 않은 것으로 본다, 위임이 없으면 PO 도 같은 목록에 묶인다)을 사용자의 위임으로 받았다.
- Follow-up candidates: registered 0, discarded 0

### Executor report at close — 2026-11-26

```
What changed: Second commit of the card; the first is b5d4ee3. This commit: stage/scripts/subsession_brief.py adds `DECISION_RULE` to every brief (pm, verify, plan, research, the rule-candidates task): make no decision yourself; the five kinds DE-00000103 lists; before building what depends on one, send the PO session the options and the one you recommend and wait, send the ones seen ahead in one message, continue with what does not depend on them; a one-file how-detail stays with the session. The PM brief adds that a specialist decides nothing either and returns a decision to the PM. stage/skills/stage-orchestrate/SKILL.md gains "Decide here" and a `po_does` line: on a decision a session sends, the PO decides on a delegation the user gave and records it as such, else asks the user; a decision a report says was already built is treated as not decided. Tests pin the rule in every brief and the skill section. stage/CHANGELOG.md and stage/docs/BLUEPRINT.md say the same. First commit: stage/scripts/subsession_brief.py takes `--role pm` (default), `verify`, `plan`, `research`; `work` became `pm`, `planning` became `plan`, `discussion` and `consolidation` are gone and argparse refuses them; `--main-session` became `--po-session`; `--task rule-candidates` (research only) prints the brief that writes `.stage/state/rule-candidates.md`. Every brief carries the same two rules: do not ask the user in this session and put each question in the report to the PO session; pass on the user's words when the user writes there anyway. The PM brief has "Pieces and specialists": two or more pieces that can each be finished and checked alone go to specialist sub-agents and the PM inspects each against its completion condition, else the PM does the card itself; a specialist is one profession noun and a run is `<profession> <card id> <piece>`; an epic's stories follow the same naming. The plan brief drafts cards from the PO session's digest and registers nothing. The research brief returns options with evidence and writes nothing. stage/skills/stage-orchestrate/SKILL.md gives the PO role: new layer table, `po_does`/`po_does_not`, "Names" (titles, tags, sub-agent names, earlier tags), "Talk with the user", "Start a plan session" (digest and registration), "Start a research session" with "The rule-candidates task", "Start a PM session", "Start a verify session", "One PO session at a time"; the take-over keeps rows tagged `stage-po:<id>` or the earlier `stage-main-session:<id>` and finds an earlier PO by `stage-role:po` or `stage-orchestrator`. stage/scripts/started_cards.py prints `Role tags:` and `Earlier tags:` lines after `Project tag:` and its docstrings say PO and PM session. stage/hooks/stage_memory_index.py: the index line reads `Rule candidates are due (20 or more): give a research session the rule-candidates task`. stage/operations/cloud-execution.md, review.md, retrospective.md, stage/skills/stage-retrospective/SKILL.md and rule-promotion.md, stage-handoff, stage-drive, stage/skills/README.md and stage/docs/BLUEPRINT.md use the new names; "Close a sub-session's card" is "Close a PM session's card"; a `## Sessions` line takes `po`, `plan`, `pm`, `verify`, `research`; the observation line reads `by verify session`. Tests pin the roles, the refusals, the user rule in every brief, the PM split rule, the digest and registration sentences, the naming rule, the earlier tags, and the rule-candidates task. stage/CHANGELOG.md has the entry under Unreleased.
Why: The card's success criterion added at 525e41a on the PO session's branch: a session's brief tells it not to settle the decisions DE-00000103 lists and to send options and a recommendation to the PO session before building. The other six criteria: the brief script prints plan, pm, verify and research briefs and has no discussion or consolidation role; every brief sends questions for the user to the PO session; the PO skill says the PO digests the talk for the plan session, the plan session drafts, and the PO registers; the PM brief hands a card of several pieces to specialists and inspects, and does a small card itself; titles, tags and sub-agent names follow DE-00000103 and a new PO finds sessions with the earlier tags; gathering rule candidates is a research task and only that task writes one list file.
Decisions made: This commit: (a) the rule is in all five briefs, the ones that build nothing included, because the criterion says a session's brief without naming a role. (b) The list of what counts as a decision lives in the brief script; the skill points to it and does not repeat it. (c) "Decide here" also says how the PO treats a decision a report says was already built, and that the same list binds the PO without a delegation; DE-00000103 states neither. (d) The research brief still asks for options and evidence and no recommendation among them; the decision rule's recommendation covers decisions the session meets in its own work. First commit: (1) `--main-session` was renamed `--po-session` with no alias, and the old role names have no alias; a session started before this change already printed its brief. (2) The rule-candidates task is `--role research --task rule-candidates`; it refuses a W-id and a `--topic`, and `--task` refuses any other role. (3) "Small card" is stated as a condition: the card does not split into two or more pieces that can each be finished and checked on its own. (4) The plan session receives the digest as one message from the PO session after its first message and returns the drafts in its report; it writes no file, because a cloud session cannot reserve ids. (5) The skill lets the PO register a card itself, without a plan session, only when the user's own words already state that one card's purpose and each success criterion; follow-up candidates with evidence stay registered directly as before. DE-00000103 does not state this boundary. (6) Research session or sub-agent: a question whose answer is options to compare with evidence goes to a research session; a lookup with one answer goes to a sub-agent. DE-00000103 does not state this boundary either. (7) Every brief also tells the session to pass the user's words on, quoted, when the user writes in that session; DE-00000103 names that case as what went wrong. (8) A session taking the PO role is titled `PO <project>` with `<project>` the repository's name; a new PO tells each open session of the earlier PO that reports now go to it and does not retag old sessions. (9) `started_cards.py` prints the tag names so the PO copies them instead of spelling them. (10) The observation line and section names changed words (`verify session`, "Close a PM session's card"); lines already written on cards keep theirs and cloud-execution.md says so. (11) stage/README.md and stage/skills/stage-discuss/SKILL.md name no session role and were not changed. (12) Paths changed outside the card's scope: stage/scripts/stage_id_blocks.py and stage/scripts/stage_record_ids.py — their docstrings, one `--reserve-for` help text and one error message said "main session" and "sub-session" for the two sessions this card renames; only those words changed, and stage/scripts/tests/test_stage_id_blocks.py pins the error message. (13) No record was created.
Work not done: No session has run under the new briefs: whether a PM session splits a card and inspects specialists, whether a plan session drafts from a digest, and whether the user stays in one window are not observed; the tests pin text and refusals only. No specialist reading list or checklist exists (DE-00000103 excludes it). The skill keeps the name `stage-orchestrate`. Project files under `.stage/operations/` were not searched for the old names beyond a count that found none. `python3 stage/scripts/release_plugin.py stage --check-released` could not run: this checkout is shallow; the change only adds lines under `## Unreleased`. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. The first commit built three choices before sending them to the PO session (numbers 1, 5 and 6 above); they were reported after building and wait for the PO session's answer. Checks run on Linux at this commit: python3 -m unittest discover -s stage/scripts/tests -q (1037 tests, OK, skipped=2); python3 -m unittest discover -s stage/hooks/tests -q (489 tests, OK, skipped=2); python3 stage/scripts/audit_stage.py (errors=0, warnings=32).
```

## Verification

2026-11-26 지휘 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 닫기 리뷰를 돌린다. 이 리뷰는 같은 모델의 대역 리뷰이고 다른 venue 의 리뷰가 아니다. 리뷰가 받는 경로는 squash 커밋 `3b88e47` 의 것이다.

- Checks at close 2026-11-26: 3 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 -m unittest discover -s stage/scripts/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-26 by claude_review_companion: approved (1 PASS ran, 2 PASS ran, 3 PASS read, 4 PASS ran, 5 PASS ran, 6 PASS ran, 7 PASS ran)
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
