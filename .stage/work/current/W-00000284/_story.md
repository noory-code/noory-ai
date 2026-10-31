---
id: W-00000284
title: 리뷰가 사례로 거부하면 그 종류 전체를 막도록 실행·리뷰 계약을 고친다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000284
promotion: not_applicable
review: not_required
scope: stage/skills/stage-drive/SKILL.md, stage/templates/v4/project-stage/settings.jsonc, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000284 리뷰가 사례로 거부하면 그 종류 전체를 막도록 실행·리뷰 계약을 고친다

## Purpose

드라이버가 판마다 리뷰어가 찾은 사례 하나만 고치다 시도 횟수를 다 쓰는 일을 막고, 한 판 안에서 같은 종류의 실패를 모두 고치게 한다.

## Actions

1. `stage/skills/stage-drive/SKILL.md`의 FAIL 처리 설명(Review dispositions 바로 뒤)에 한 문단을 더한다: 리뷰어는 사례로 거부할 때 그 사례가 속한 입력의 종류를 `reason`에 적고, 실행자는 accept할 때 그 종류 전체를 고치고 변형마다 시험한다.
2. `stage/templates/v4/project-stage/settings.jsonc`의 실행 명령 안내와 리뷰 명령 안내에 같은 뜻의 문장을 하나씩 더한다.
3. `stage/CHANGELOG.md` Unreleased에 적는다.

## User value

다시나 W-00000028과 W-00000031은 리뷰가 판마다 사례 하나씩을 새로 찾았고, 두 카드 모두 시도 3번을 다 쓴 뒤 Claude가 손으로 종류를 막아 닫았다(R-00000028, R-00000031). 규칙 승격 기준 "두 번 일어났다"에 맞는다.

## Scope

### Included

- 플러그인의 실행 계약(스킬)과 새 프로젝트가 받는 설정 템플릿 안내.

### Excluded

- 이미 있는 프로젝트(noory-ai, 다시나)의 `settings` 실행·리뷰 명령 문자열. Codex 실행자는 그 문자열과 카드만 읽으므로 실제 행동이 바뀌려면 거기에도 문장이 들어가야 한다. 프로젝트 설정은 사람이 정하므로 사용자에게 묻는다.

## Risks

- 리뷰어가 종류를 잘못 이름 지으면 실행자가 엉뚱한 범위를 고칠 수 있다. 실행자는 이름 붙인 종류를 보고서에 적으므로 다음 리뷰가 잡는다.

## Success criteria

- stage-drive 스킬의 실행 계약이 FAIL 기준을 accept할 때 리뷰가 든 사례가 속한 입력의 종류를 이름 짓고 그 종류 전체를 고치고 시험하라고 말하며, 리뷰어에게는 사례로 거부할 때 그 사례가 속한 종류를 이유에 적으라고 말한다
- 프로젝트 설정 템플릿의 실행·리뷰 명령 안내가 같은 두 문장을 담고, 근거로 다시나 R-00000028·R-00000031을 단다
- stage CHANGELOG Unreleased에 이 변경이 적히고 Stage 시험이 그대로 통과한다

## Next action


## Related truth


## Progress


## Verification

2026-10-15 Claude가 직접 했다(claude venue, 팀원 대신 이 세션이 실행 — 사용자가 16시까지 동시 작업을 두 갈래로 정했고 다른 갈래는 다시나 드라이버가 쓰고 있다).

- 세 파일을 고쳤다. 스킬 문단과 템플릿 두 문장은 근거로 다시나 R-00000028·R-00000031을 단다.
- `python3 -m unittest discover -s stage/hooks/tests -q` 통과. `python3 stage/scripts/audit_stage.py` errors=0.
- `python3 -m unittest discover -s stage/scripts/tests -q`는 659개 중 6개 실패. 모두 `test_template_v4.test_project_pins_the_current_model_in_all_eight_driver_commands`로, 이 저장소 `.stage/settings.json`의 Codex 명령에 `--model gpt-5.6-sol`이 있어야 한다는 시험이다. 2026-10-12 커밋 `5dcc858d`가 그 고정을 일부러 뺐고 시험은 고치지 않았다. 이 카드의 변경을 빼고(git stash) 돌려도 같은 6건이 실패하는 것을 확인했다. 이 카드 범위 밖이라 고치지 않았다.

### Executed at close — 2026-10-15

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 378 tests in 2.458s

OK

$ python3 stage/scripts/audit_stage.py
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective

[R-00000284](../../retrospectives/R-00000284.md).

## Promotion decision

이 작업 카드가 소유한 결정이나 승격 경로가 없으므로 `not_applicable`이다.
