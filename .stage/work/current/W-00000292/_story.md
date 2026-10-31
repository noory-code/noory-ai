---
id: W-00000292
title: 실행 환경을 venue 와 나누고 클라우드 실행을 정책으로 허용한다
kind: development
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000292
promotion: deferred
review: passed
scope: stage/hooks/stage_paths.py, stage/hooks/stage_work.py, stage/skills/stage-work/register_work.py, stage/scripts/start_work.py, stage/scripts/audit_stage.py, stage/scripts/claude_review_companion.py, stage/scripts/tests/test_environment_venues.py, stage/operations/cloud-execution.md, stage/docs/SCHEMA_V4.md, stage/templates/v4/project-stage/settings.jsonc, .stage/settings.json, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000082, DE-00000083
---

# W-00000292 실행 환경을 venue 와 나누고 클라우드 실행을 정책으로 허용한다

## Purpose

클라우드에서 실행하는 카드마다 같은 venue 예외 결정을 세우지 않고, 실행한 쪽과 실행한 자리를 카드에 따로 정직하게 남긴다.

## Actions

DE-00000082 의 "Where this applies" 표가 바꿀 자리를 센다. 요약:

- 카드에 선택 칸 `environment`, 설정에 `environment_venues` 를 둔다.
- 등록·시작 도구와 감사가 같은 허용 조건(선언된 환경, 그 환경의 venue, `review` 가 `pending`·`passed`)을
  공유 함수 하나로 판정한다. 조건을 어기면 이유와 함께 거절하고, 감사는 VENUE006 을 낸다.
- 클라우드 실행 계약(세션 브랜치 커밋·push, 커밋 본문 실행 보고와 이관 도구, 코드 커밋 worktree 에서
  닫기, codex 대역 리뷰)을 `stage/operations/cloud-execution.md` 로 옮긴다. 대역 리뷰를 돌리는
  `stage/scripts/claude_review_companion.py` 를 저장소에 둔다.

## User value

클라우드에서 카드를 돌릴 때 결정 기록을 새로 쓰지 않아도 되고, 카드만 보면 누가 어디서 실행했는지가
읽힌다.

## Scope

### Included


### Excluded

- 섞인 종류(`split`) 규칙.
- 이미 닫힌 클라우드 카드(W-00000268~291)의 기록을 고치는 일.

## Risks


## Success criteria

- environment 가 선언된 환경을 가리키고 venue 가 그 환경의 venue 이며 독립 닫기 리뷰를 요구하는 카드는 예외 결정 없이 등록·시작되고 감사를 통과한다는 것을 테스트가 확인한다
- 선언되지 않은 환경, 환경과 다른 venue, 닫기 리뷰를 요구하지 않는 카드는 등록·시작·감사에서 이유와 함께 거절된다는 것을 테스트가 확인한다
- 클라우드 실행·이관·닫기 절차가 한 문서에 있고 그 절차가 쓰는 도구가 저장소에 있다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: Cards gain an optional `environment:` field and settings gain `environment_venues` (this project: cloud -> claude); stage_work.environment_venue_error() permits a venue_routing mismatch without an exception when the environment is declared, the card's venue is the one declared for it, and review is pending or passed, and register_work.py (--environment, filling an omitted venue), start_work.py (--environment, --review), and the audit (VENUE006 for a breaking card, no VENUE003 for a permitted one) share it; stage/operations/cloud-execution.md now owns the cloud procedure (register or start, execute on the session branch, import the report, close from a worktree at the code commit with the Claude stand-in reviewer, record the same-model review); stage/scripts/claude_review_companion.py is that stand-in, and codex_companion.py runs a .py override with Python; SCHEMA_V4, the settings template, and the changelog describe the field and setting; tests cover permitted register and start with a clean audit, refusals for an undeclared environment, a different venue, a missing review, and a planned card, audit VENUE006 and VENUE003 cases, the stand-in's command, and the Python override.
Why: W-00000292 - cloud-run cards should not need one venue exception each, and the card should record who executed and where separately.
Decisions made: Add an environment field instead of a `cloud` venue value, because a venue value would again mix who and where and leave the cross-venue reviewer undefined; require review pending or passed as the policy's price because the routed reviewer venue is absent there; keep the split-kind rule independent of environment because it separates design from implementation; refuse --environment on planned cards and apply it at start_work, where the venue contract already runs; write the stand-in reviewer in Python per the repository's script rule and teach codex_companion.py to run .py overrides; out-of-scope path changed: stage/scripts/codex_companion.py, because without it the Python stand-in cannot be used through STAGE_CODEX_COMPANION.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `23351a2e` 의 worktree 로, 이 카드가 만든
`stage/operations/cloud-execution.md` 절차대로 닫았다. 실행 보고는 `import_executor_report.py` 로 옮겼고,
리뷰는 `STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py` 로 이 프로젝트의 `implementation`
리뷰 명령을 설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_environment_venues.py -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 1.770s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793449742
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793449742. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpjqakqpd_/unattended/W-00000001-1793449742
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
Ran 701 tests in 135.643s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000292.md
Criteria:
- PASS: environment 가 선언된 환경을 가리키고 venue 가 그 환경의 venue 이며 독립 닫기 리뷰를 요구하는 카드는 예외 결정 없이 등록·시작되고 감사를 통과한다는 것을 테스트가 확인한다
  Reason: test_register_permits_the_environment_venue_without_an_exception and test_start_applies_the_same_policy_to_a_planned_card register/start a fix card routed to codex with --environment cloud --review, assert venue claude + environment cloud + review pending with empty decision_refs, and assert the audit emits neither VENUE003 nor VENUE006; audit_stage.py skips VENUE003 only when environment_venue_error returns ''.
- PASS: 선언되지 않은 환경, 환경과 다른 venue, 닫기 리뷰를 요구하지 않는 카드는 등록·시작·감사에서 이유와 함께 거절된다는 것을 테스트가 확인한다
  Reason: Register subtests refuse all three cases (plus a planned card) with the specific reason and no card written; start refuses the missing-review case with its reason; audit reports VENUE006 with the reason when review is dropped and VENUE003 when environment is removed; all three surfaces call the single stage_work.environment_venue_error, so the per-surface tests prove the shared reasons are wired.
- PASS: 클라우드 실행·이관·닫기 절차가 한 문서에 있고 그 절차가 쓰는 도구가 저장소에 있다
  Reason: stage/operations/cloud-execution.md covers policy, register/start, executing on the session branch, importing the report, and closing from a code-commit worktree with the same-model disclosure; every tool it names (register_work.py, start_work.py, stage_record_ids.py, import_executor_report.py, close_work.py, claude_review_companion.py) exists, and codex_companion.py now runs a .py override, which a test covers.
- PASS: Purpose and scope-boundary reporting contract (Decisions made / Work not done)
  Reason: Decisions made gives reasons for each choice and names the one out-of-scope path, stage/scripts/codex_companion.py, with its reason; this matches the changed paths, where it is the only path outside scope; Work not done is None, which holds because the Excluded items (split rule, closed cards W-00000268~291) were left untouched.
```

## Retrospective

[R-00000292](../../retrospectives/R-00000292.md).

## Promotion decision

DE-00000082 는 정책 결정이지만 정착한 뒤 `official/canon` 으로 승격하므로 지금은 `deferred` 다.
닫을 때 `approved` 로 닫았으나 승격 경로(`promotes:`)가 없어 감사가 WORK027 을 냈고, 실제 상태인
`deferred` 로 바로잡았다. DE-00000083 은 일회성 venue 예외다.
