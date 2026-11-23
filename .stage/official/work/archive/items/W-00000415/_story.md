---
id: W-00000415
title: 쌓인 규칙 후보를 처음으로 한 목록에 묶는다
kind: documentation
venue: claude
environment: cloud
milestone: M-00000006
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000415
promotion: not_applicable
review: passed
scope: .stage/state/rule-candidates.md,.stage/index.md
promotes:
decision_refs:
---

# W-00000415 쌓인 규칙 후보를 처음으로 한 목록에 묶는다

## Purpose

회고마다 흩어진 규칙 후보가 한 목록에 묶여 있어서, 같은 일이 몇 번 관찰됐는지 보고 규칙으로 올릴지를 정할 수 있다 (DE-00000100)

## Actions


## User value


## Scope

### Included

- `stage/skills/stage-retrospective/rule-promotion.md` 의 "Consolidating candidates" 가 말하는 형식을 따른다.
- O-00000061 의 규칙 후보 세 건도 넣는다.


### Excluded

- 규칙으로 실제 올리는 일. 제안까지만 한다.
- 회고와 결정의 본문을 고치는 일.


## Risks


## Success criteria

- 지금 있는 회고의 규칙 후보가 .stage/state/rule-candidates.md 에 through 와 함께 묶여 있고, 묶음마다 근거 회고와 관측 횟수가 있다
- 회고, 결정, 규칙 파일의 본문은 바뀌지 않았고, 규칙으로 올리자는 것은 제안으로만 적혀 있다

## Next action

없음. 닫고 보관한다. W-00000413 의 색인 고침과 함께 병합한다.


## Related truth

- DE-00000100, W-00000409, `stage/operations/retrospective.md`
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions

- session_018VXR6R3gCWLNcaWhGyvLaD — work — 2026-11-23 — opened from the index: O-00000061


## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 d192365b 에서 카드를 등록해 시작하고 작업 세션 session_018VXR6R3gCWLNcaWhGyvLaD (`claude/w415-rule-candidates`)를 띄웠다. 번호 묶음은 잡지 않았다.


- 2026-11-23 작업 세션 session_018VXR6R3gCWLNcaWhGyvLaD 가 70302798 을 보고했다. 후보 39건(올리자는 제안 14, 보류 25)을 묶었다. 지휘 세션이 squash 커밋에서 audit 오류 0 을 다시 확인했다.
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: "하니스 밖"의 읽기(CI 는 포함, 닫기 리뷰어는 제외). 올리자는 제안 14건 가운데 무엇을 규칙으로 올릴지는 사용자가 정한다(O-00000062).
- Follow-up candidate: 색인이 싣는 규칙 후보의 수를 줄이거나 올리자는 제안만 싣는다(W-00000413 이 순서를 고친다).
- Follow-up candidate: R-00000368 의 후보는 O-00000058 이 고쳐지면 없어진다.

### Executor report at close — 2026-11-23

```
What changed: New .stage/state/rule-candidates.md with through: R-00000410 and 39 one-line bullets (14 proposed: promote, 25 proposed: hold), each carrying the behavior, "seen <n>: <R-ids>", and the proposal; .stage/index.md gains one routing row that points to the list.
Why: The card's purpose: candidates scattered across retrospectives are grouped in one list so a reader can see how often each was observed and decide whether to promote it (DE-00000100).
Decisions made: (1) Read every retrospective with a non-empty "## Rule candidate" section (R-00000241 to R-00000410; older ones have no such section) and followed the format in stage/skills/stage-retrospective/rule-promotion.md, "Consolidating candidates". (2) Merged only two pairs: R-00000241 with R-00000373 (moving a record's place, count its readers) and R-00000371 with R-00000402 (one question, one answer); R-00000266, R-00000398, R-00000243, R-00000365 and R-00000366 look related but stay separate bullets because a wrong merge would create a promotion. (3) "seen <n>" counts retrospectives only; where one retrospective itself records two occurrences or a catch outside the harness, the bullet says so in a short clause and is proposed: promote (R-00000246, R-00000247, R-00000255, R-00000258, R-00000282, R-00000326, R-00000334, R-00000337, R-00000368, R-00000374, R-00000393, R-00000394). I counted the PR's Windows CI as outside Stage's gates (R-00000393, R-00000394) and did not count Stage's own close reviewer unless the retrospective says so (R-00000300 stays hold, R-00000326 is promote because it says an outside party caught it). (4) O-00000061's three candidates are in the list: two were already stated by R-00000371/R-00000402 and R-00000404, and the encoding-contract one is merged into the R-00000394 bullet; each of those bullets names O-00000061. (5) Left out because a rule file already states them: R-00000242 (stage/skills/stage-decision/SKILL.md, "Counting is a run too"), R-00000244 and R-00000260 (stage/operations/verification.md, "A stored check must discriminate"), R-00000245 first candidate (stage-decision, "Promote the decision and close the record it answered"), R-00000245 second candidate, R-00000362 and R-00000364 (stage/skills/stage-work/SKILL.md, "Run the premise before turning an observation into a card"), R-00000248 and R-00000259 (stage/skills/stage-drive/SKILL.md, clean working tree), R-00000250 and R-00000358 (.stage/operations/parallel-sessions.md), R-00000287 and R-00000295 (stage/operations/cloud-execution.md, "Close" steps 4 and 3), R-00000300 first candidate (stage-drive executor report contract: changed paths across all attempts), R-00000354 (.stage/operations/verification.md), R-00000356 and R-00000359 (root CLAUDE.md, Cross-Platform table), R-00000386 (stage/skills/stage-orchestrate/SKILL.md, orchestrator_does_not), R-00000389 (stage/CLAUDE.md). (6) Not listed because the section states no candidate: R-00000262, R-00000265, R-00000274, R-00000369, and every "none" or driver-generated section. (7) Bullets are one physical line each, promote proposals first, because the session index shows only a bullet's first line and shortens the candidate block from the end. (8) No path outside the card's scope was changed; no retrospective, decision, rule file, skill or card was edited.
Work not done: Nothing was promoted. I did not open the full body of every retrospective to re-check its own "caught outside the harness" claim; the proposals follow what each Rule candidate section says. With the list in place the brief's session index shows 36 of 39 candidates and no decision title (82 not shown; 77 titles were shown before), because the fitter shortens decision titles before candidates; changing that order or the limit is code outside this card.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Checks at close 2026-11-23: 1 passed — `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS ran)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
