---
id: W-00000412
title: 지휘와 닫기 절차가 오늘 손으로 메운 자리를 말한다
kind: development
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000412
promotion: not_applicable
review: passed
scope: stage/skills,stage/operations,stage/scripts/subsession_brief.py,stage/scripts/tests,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000412 지휘와 닫기 절차가 오늘 손으로 메운 자리를 말한다

## Purpose

다음 지휘자가 브리핑을 넘기고, 반려된 카드를 다시 가져오고, 기계 확인이 남은 카드를 병합하고, 릴리스를 낼 때 오늘처럼 스스로 길을 만들지 않는다

## Actions


## User value


## Scope

### Included


### Excluded

- 지휘 세션과 기기의 세션이 서로 모르고 카드를 여는 문제. 설계가 필요해 이 카드에서 다루지 않는다.
- `Order:` 줄을 스키마 필드로 바꾸는 일.


## Risks


## Success criteria

- 스킬과 브리핑 생성기가 작업 세션이 같은 명령으로 브리핑을 스스로 내어 읽는 길을 말하고, 토론, 계획, 규칙 후보 정리 세션의 브리핑을 생성한다
- cloud-execution.md 가 닫기 리뷰가 반려된 뒤 두 번째로 가져올 때 할 일과, 성공 기준이 사용자의 기계에서만 채워지는 카드를 열어 둔 채 병합하는 길을 말한다
- 릴리스 절차가 릴리스 커밋을 만들기 직전에 기본 브랜치를 받으라고 말한다
- stage-orchestrate 스킬이 이 카드를 시작할 때보다 길지 않다

## Next action

없음. 닫는다. 보관은 에픽과 함께 한다.


## Related truth

- O-00000061 의 "카드 여덟 장과 릴리스 하나를 묻지 않고 끌고 가며 본 것", W-00000406, W-00000410 의 후속 후보
- 검증 세션을 띄운 카드를 닫기 전에 `- Observed` 줄이 카드에 있는지 보는 것(W-00000408 의 후속 후보)도 절차에 넣을 수 있으면 넣는다.
- 사용자가 2026-11-23 에 남은 후보도 카드로 만들어 자율로 진행하라고 했다("남은 후보들도 카드로 만들어서 자율로 진행하세요"). 목적과 성공 기준은 지휘 세션이 후보 목록에서 옮겨 적었다.


## Sessions


## Progress

- 2026-11-23 에픽의 작업 세션 session_018VXR6PwLBPzLD6Y92UC31m 가 이 스토리를 5c95bed 로 보고했다. 성공 기준 1-4 를 주장했다. 지휘 세션이 cherry-pick 한 커밋(35ec2aa1)에서 scripts 965, hooks 483 통과와 audit 오류 0 을 다시 확인했다. 스킬은 322줄에서 320줄이 됐다. 범위 밖 변경은 루트 `CLAUDE.md` 한 곳이다(릴리스 절차의 단계).
- 2026-11-23 지휘 세션이 사용자의 위임으로 받은 것: 루트 `CLAUDE.md` 의 릴리스 단계, 토론·계획 세션이 기록을 쓰지 않는 것(DE-00000099 의 문장과 다르다), 기계 확인이 남은 카드를 병합하는 길의 조건.
- Follow-up candidate: `release_plugin.py --bump` 가 기본 브랜치가 HEAD 의 조상이 아니면 거부한다.
- Follow-up candidate: 새 브리핑 셋과 `--first-message` 를 실제 세션이 써 본다.
- Follow-up candidate: `subsession_brief.py` 가 705줄이다.


### Executor report at close — 2026-11-23

```
What changed: (1) stage/scripts/subsession_brief.py gains --first-message, which builds the brief (so a refusal shows in the caller's session) and prints instead a short first message naming the role and the same command without that flag; it gains --role discussion and --role planning (both require --topic, the W-id is optional) and --role consolidation (a W-id is refused). (2) stage/skills/stage-orchestrate/SKILL.md gains "Give a session its brief" (command, first_message if/else, one table row per role) and "Start a discussion or planning session"; "send the brief unedited as the first message" remains only as the else branch for a host without the script; the consolidation session's rules, the "Boundary with the driver" section, the started_cards.py output description, the Sessions line format, and the verify command block are removed or reduced to pointers. The file is 320 lines, was 322. (3) stage/operations/cloud-execution.md gains "Import again after a rejected close review" (the first squash commit stays; conflicts take the sub-session's file with git checkout FETCH_HEAD -- <path>; git diff FETCH_HEAD over the scope and report paths must print nothing before committing; import with one --commit per squash commit; the retrospective keeps its id), "Merge a card that waits for the user's machine" (when it applies, no close review before the merge, what is written on the card and in the deferred-checks observation, how the card closes when the user's check arrives), and a before_closing block in step 4 that confirms the `- Observed` line is on a card that had a verification session. (4) Root CLAUDE.md "Plugin Changes" gains step 3: fetch and merge the default branch immediately before creating the release commit and not after; old steps 3 to 5 are 4 to 6. (5) stage/skills/README.md, stage/docs/BLUEPRINT.md and stage/CHANGELOG.md follow; tests in test_subsession_brief.py (10 new) and test_orchestrate_skill.py (2 new, 2 adjusted).
Why: The story's four success criteria, taken from O-00000061's last block and the follow-up candidates of W-00000404, W-00000406, W-00000408, W-00000409 and W-00000410.
Decisions made: (1) Role names are discussion, planning, consolidation (not consolidate), the names cloud-execution.md already uses on a card's Sessions line, so the line's role is the --role value. (2) Discussion and planning sessions write no record: they report what the user chose and the cards they propose, and the orchestrator writes decisions and registers cards, because a cloud session cannot reserve ids (DE-00000094) and one session registers cards. DE-00000099 says the discussion session "leaves its conclusion as decision records and cards"; this narrows who writes them and needs the user's confirmation. (3) The consolidation session's rules moved from the skill into the generated brief; the skill keeps when to start it and what follows its report. (4) The machine-check merge path requires the user's word to merge without waiting; otherwise the orchestrator asks. Both precedents (W-00000372, W-00000407) rested on a delegation. (5) No test caps the skill's line count; a fixed cap invites over-long lines. (6) --first-message quotes the command with shlex.join (POSIX); when the plugin is outside the project the command shows a placeholder path and a line telling the session to replace it. (7) Changed outside the story's scope: CLAUDE.md (repository root), because the numbered release procedure exists only there; stage/CLAUDE.md "Release" names only the command and no file under stage/skills or stage/operations holds a release procedure. The rule therefore binds every plugin's release, not only Stage's; this needs the user's confirmation. (8) Changed stage/skills/README.md (inside scope) so its one-line description of stage-orchestrate names the new session kinds.
Work not done: No real session has run --first-message end to end or used a discussion, planning or consolidation brief; the tests run the command taken from the first message and compare its output with the pasted brief for all five roles. The second-import and machine-check paths are documents only; no command enforces them. subsession_brief.py is now 705 lines, over the 500-line review threshold; splitting it needs a new file and is left as a follow-up. Nothing was run on Windows or macOS; the pull request's CI jobs are that check. Checks run on Linux by the work session after the sub-agent finished: python3 -m unittest discover -s stage/scripts/tests -q (965 tests, OK, skipped=2), python3 -m unittest discover -s stage/hooks/tests -q (483 tests, OK, skipped=2), python3 stage/scripts/audit_stage.py (errors=0, warnings=32, the same as before the change). No record was created.
```

## Verification

- 닫기 리뷰는 Claude 대역으로 돌린 같은 모델 리뷰다.

- Checks at close 2026-11-23: 1 passed — `python3 -m unittest discover -s stage/scripts/tests -q`
- Review at close 2026-11-23 by claude_review_companion: approved (1 PASS ran, 2 PASS read, 3 PASS read, 4 PASS ran)
- Load at close 2026-11-23: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)
