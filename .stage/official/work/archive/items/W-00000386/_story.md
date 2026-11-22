---
id: W-00000386
title: 실행자 모델이 사용량 한도에 걸리면 같은 venue의 다른 모델로 넘어가는 순서를 둔다
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
retrospective_ref: R-00000386
promotion: not_applicable
review: passed
scope: stage/hooks/stage_model_tiers.py,stage/scripts,stage/docs/SCHEMA_V5.md,stage/templates,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000386 실행자 모델이 사용량 한도에 걸리면 같은 venue의 다른 모델로 넘어가는 순서를 둔다

## Purpose

한 모델이 사용량 한도에 걸려도 드라이버가 같은 실행자의 다른 모델로 이어 가서, 감독자가 실행자 전체가 막혔다고 잘못 보지 않게 한다

## Actions

- 한 스토리로 끝나는 일이라 하위 action을 두지 않는다.

## User value

실행자 하나가 여러 회사 모델을 고를 수 있을 때(예: agy), 한 모델의 한도 때문에 일이 멈추거나 다른 venue로 잘못 넘어가지 않는다.

## Scope

### Included

- 설정에서 venue마다 모델 순서를 적는 자리. `model_tiers`가 고른 모델을 첫 모델로 둘지, 순서를 등급마다 둘지는 시작할 때 정한다.
- 드라이버가 실행자·리뷰어 출력에서 사용량 한도 오류를 알아보는 방법. 아래 근거의 agy 오류 모양을 처음 대상으로 한다.
- 다음 모델로 넘어갈 때 그 실행을 시도 횟수에 셀지 정하고 문서에 적는다.
- 스키마 문서와 템플릿 설정의 예.

### Excluded

- 다른 venue로 넘어가는 일(예: agy에서 claude로). 그것은 venue 예외 결정 기록을 거친다.
- 프로젝트마다 어떤 모델을 어떤 순서로 쓸지 정하는 일. 그것은 각 프로젝트의 설정 몫이다.

## Risks

- 한도 오류의 모양은 실행자 CLI마다 다르고 바뀔 수 있다. 오류를 잘못 알아보면 진짜 실패를 다른 모델로 되풀이한다.
- 한도가 모델 묶음으로 걸린다. agy에서는 Claude 모델과 GPT-OSS가 한 한도를 함께 쓰고, Gemini 4 Argon은 주간 한도, Gemini 3.8 Flash는 따로다(다시나에서 2026-11-07~08에 본 것). 같은 묶음의 다음 모델로 넘어가면 다시 막힌다.
- 짧은 확인 질문은 통과해도 긴 실행은 바로 한도에 걸린 적이 있다(다시나 W-00000074, W-00000075). 넘어가기 전에 미리 확인하는 방법은 믿기 어렵다.

## Related truth

- 2026-11-22 다시나 W-00000193(build 등급): 드라이버가 agy `claude-sonnet-5-5-high`로 실행했고 `RESOURCE_EXHAUSTED (code 429): Individual quota reached ... Resets in 69h26m36s`로 끝났다. 시도 1/3을 썼다. 감독자(Claude)는 agy 전체가 막혔다고 보고 Claude venue로 넘기려 했다가, Gemini 모델을 시도하지 않았다는 것을 알고 되돌렸다. 2회차는 감독자가 `DASINA_AGY_MODEL=gemini-4-argon-medium`을 손으로 넣어 실행했다.
- 다시나 `.stage/settings.jsonc`에는 agy 모델 다섯 개와 쓰임이 주석으로만 적혀 있고, 드라이버는 한 단계에 모델 하나만 쓴다.
- 2026-11-22 사용자: "agy 에게 맞길 때 agy 가 가진 모델들이 매우 많던데 그거 다 활용하는거죠?", "모델 넘어가는 순서 일감으로 등록해 두세요".

## Success criteria

- 프로젝트 설정에 venue마다 모델을 넘어갈 순서를 적을 수 있다
- 실행자나 리뷰어가 사용량 한도 오류로 끝나면 드라이버가 순서의 다음 모델로 다시 실행하고, 어떤 모델로 실행했는지와 넘어간 까닭이 작업 기록에 남는다
- 순서의 모델이 모두 한도에 걸리면 드라이버가 그렇다고 알리고 멈춘다

## Next action

계획 카드로 둔다. 시작할 때 Included의 정할 것 두 가지(순서를 두는 자리, 시도 횟수에 셀지)를 먼저 정한다.

## Progress

### 2026-11-22 시작할 때 정한 것

사용자가 고른 것:

- **순서를 두는 자리: venue 마다 한도 묶음의 목록.** 설정 키는 `model_fallbacks` 다. venue 이름 아래에 모델 묶음의 목록을
  순서대로 둔다. 한 묶음은 사용량 한도를 함께 쓰는 모델들이다.

  ```json
  "model_fallbacks": {
    "agy": [
      ["claude-sonnet-5-5-high", "gpt-oss"],
      ["gemini-4-argon-medium"],
      ["gemini-3.8-flash"]
    ]
  }
  ```

  드라이버는 카드 등급이 고른 모델(`STAGE_MODEL`)로 먼저 실행한다. 한도에 걸리면 그 모델이 든 묶음을 건너뛰고, 아직 쓰지
  않은 다음 묶음의 첫 모델로 다시 실행한다. 등급의 모델이 어느 묶음에도 없으면 목록의 첫 묶음부터 쓴다.
- **시도 횟수: 세지 않는다.** 한도 때문에 다음 모델로 다시 돌린 실행은 카드의 시도 횟수에 들지 않는다. 넘어갈 수 있는 횟수는
  목록의 길이로 끝난다. 모든 묶음이 한도에 걸리면 드라이버가 그렇다고 알리고 멈춘다.

메인 세션이 정한 것:

- **한도 오류를 알아보는 법: venue 마다 설정에 적은 문구.** 설정 키는 `usage_limit_patterns` 다. venue 이름 아래에 정규식 목록을
  두고, 실행자나 리뷰어가 0 이 아닌 코드로 끝났고 그 출력이 한 문구에 맞을 때만 한도로 본다. 오류 모양은 실행자 CLI 마다
  다르고 바뀔 수 있어서 Stage 코드에 박지 않는다. 처음 대상은 이 카드의 근거에 있는 agy 오류다
  (`RESOURCE_EXHAUSTED`, `code 429`).
- 실행자와 리뷰어 모두에 적용한다. 감독 드라이버(`driver_supervised.py`)와 무인 드라이버(`driver_unattended.py`) 모두에 적용한다.
- 어떤 모델로 실행했는지와 넘어간 까닭은 작업 기록에 한 줄씩 남긴다.
- 두 키 모두 `stage/hooks/stage_model_tiers.py` 가 읽는다(설정을 읽는 자리가 하나). 스키마 문서(`docs/SCHEMA_V5.md`)와 템플릿
  설정 예를 고친다.

### Executor report at close — 2026-11-22

```
What changed: hooks/stage_model_tiers.py reads two new settings, `model_fallbacks` (per venue, model groups sharing one usage limit, in preference order) and `usage_limit_patterns` (per venue, regexes marking a failed run's output as a usage limit), through FallbackConfig/parse_fallback_config/load_fallback_config; new scripts/driver_model_fallback.py runs a turn and, on a non-zero exit whose output matches a venue pattern, reruns it with STAGE_MODEL set to the first model of the first group holding no model that already hit a limit, writing one `### Driver model` work-log line per run and per fallback, and ends with a `[stage: every model group hit its usage limit]` marker when no group remains; driver_supervised.py (executor and reviewer), driver_unattended.py (executor), and close_work.run_close_review (the close review, which the unattended driver uses) run through it; driver_review.infrastructure_failure treats the marker as infrastructure so no attempt is spent; on exhaustion the supervised driver stops the round, the unattended driver discards the item output and stops the run, and an exhausted close review restores the card and stops, each with `Outcome: blocked` and a new RECOMMEND_USAGE_LIMIT next action (driver_worklog.print_usage_limit_blocker) instead of escalating the card; audit_model_tier.py reports invalid settings as TIER006; docs/SCHEMA_V5.md gains "Model fallbacks on usage limits"; the v4 settings template shows both keys empty with an agy example in comments; tests/test_model_fallbacks.py and a TIER006 case in tests/test_audit_model_tier.py cover parsing, group skipping, exhaustion, a command that does not read $STAGE_MODEL, both drivers, and the close review; CHANGELOG has an Unreleased entry.
Why: W-00000386's purpose is that a usage limit on one model lets the driver continue on the same venue's other models, so the supervisor does not wrongly judge the whole executor blocked, and that the run records which model ran and why it moved.
Decisions made: Followed the card's recorded choices (per-venue group lists under `model_fallbacks`, reruns not counted as attempts, detection by per-venue `usage_limit_patterns`, both roles in both drivers, one log line each, stage_model_tiers.py as the single reader); the next model is the first model of the first unspent group in list order, so a tier model outside every group starts from the first group and a tier model inside a group skips that group; groups and limited models are compared by lowercase alias without a trailing [...] qualifier, exact match rather than the tier substring match, so gemini-4-argon never spends gemini-4-argon-medium; patterns are case-sensitive Python regexes matched on the raw (unclipped) output, and only when the command exited non-zero; a command whose text does not name STAGE_MODEL cannot switch model, so its first usage limit ends the turn as exhausted, and patterns without fallbacks likewise stop on the first limit instead of spending an attempt; the executor's partial output from a limited run stays in the tree for the next model (as with other in-turn state), while a reviewer's partial verdict is removed before a rerun; exhaustion stops the run rather than escalating the card, because the card is not at fault and moving venue needs a venue exception decision; invalid settings make the runtime fall back for no venue and the audit reports TIER006 even without model_tiers; the reviewer fallback lives in close_work.run_close_review because the unattended driver reviews only through close_work.py; crossed the card scope for stage/skills/stage-retrospective/close_work.py (the unattended and manual close review run there), stage/docs/BLUEPRINT.md (stage/CLAUDE.md requires recording close_work's new import of a driver module in the reverse-import table), stage/skills/stage-audit/SKILL.md (the TIER006 code row), and stage/skills/stage-drive/SKILL.md (one paragraph pointing drivers to the new contract).
Work not done: Windows runs of tests/test_model_fallbacks.py (its commands append " # $STAGE_MODEL", a shell comment on POSIX and an ignored python argument under cmd.exe) and the rest of the suites are left to the pull request's Windows CI; no live agy run was made, so the default agy patterns in the docs are taken from the card's recorded error text only; the parallel driver (drive_parallel.py) is covered only through the shared supervised/unattended paths it calls.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 서브세션(session_018VXR6RCneV51b9QRAjuKL3)이 만들고 메인 세션이 닫았다(DE-00000094). 서브세션 브랜치
  `claude/w386-model-fallbacks` 의 88f788c3 을 squash 했다(5755d287).
- 성공 기준 1: `model_fallbacks` 와 `usage_limit_patterns` 를 프로젝트 설정에 적을 수 있고 `stage_model_tiers.py` 가 읽는다.
  `docs/SCHEMA_V5.md` 와 템플릿 설정에 예가 있다. 잘못 적으면 감사가 TIER006 을 낸다.
- 성공 기준 2: `test_model_fallbacks.py` 15개가 한도 오류 뒤 다음 묶음의 첫 모델로 다시 실행하는 것, 작업 기록의
  `### Driver model` 줄, 시도 횟수에 세지 않는 것을 본다.
- 성공 기준 3: 모든 묶음이 한도에 걸리면 드라이버가 `Outcome: blocked` 와 다음 행동을 출력하고 멈춘다. 같은 시험 파일이 본다.
- 메인 세션이 다시 돌린 검사: hooks 와 scripts 전체 통과(scripts 889개), 감사 오류 0건. PR #105 의 CI 30개가 모두 통과했다
  (windows-latest 샤드 12개 포함, 영어 로캘). 이 카드는 Windows 동작을 고치지 않아서 한국어 Windows 실행을 따로 하지 않는다.
- agy 의 실제 실행으로는 확인하지 않았다. 이 저장소에는 agy 가 없다. 다시나에 설정할 때 확인한다.
- 사용자가 2026-11-22 에 서브세션의 확인 거리 셋을 "추천대로" 받아들였다.

- Checks at close 2026-11-22: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_model_fallbacks.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_audit_model_tier.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-22 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
