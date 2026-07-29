---
id: W-00000108
title: 규모가 생기면 실행 단위와 리뷰 지점이 어디인가
kind: design
venue: claude
priority: 4
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000105
promotion: not_applicable
review: not_required
scope: .stage/decisions/, .stage/state/, stage/templates/v4/project-stage/settings.json, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000037
---

# W-00000108 규모가 생기면 실행 단위와 리뷰 지점이 어디인가

## Purpose

DE-00000035 는 계층을 확정했지만 그 위에서 무엇을 한 번에 돌리고 어디서 리뷰하는지는 안 정했다.
`.stage/settings.json` 의 네 자리가 지금 "항목" 이 하나뿐이라는 전제 위에 서 있다. 규모가 셋이
되면 각각 어느 규모를 가리키는지 정해야 한다.

이 카드는 코드를 안 고친다. 결정만 낸다.

## Source

DE-00000035 의 `## Where this applies` 설정 표가 네 자리를 열거하고, 그중 `review.stages` 는
"정해야 한다" 로 열어 뒀다.

## User value

없다. 다음 카드가 무엇을 구현할지 정해진다.

## Scope

### Included

정해야 할 것 넷.

- `limits.max_attempts_per_item` 과 `max_iterations` 의 "항목" 이 액션인가 스토리인가 에픽인가.
- 실행자 프롬프트가 "카드가 지시 전부다" 라고 못박는데, 액션 카드는 혼자 맥락이 안 되고
  `_story.md` 가 쥔다. 실행하는 쪽에 무엇을 넘길 것인가. `executors.claude` 와 `executors.codex`
  가 같은 문장을 두 벌 갖고 있으므로 한 번 정하면 둘 다 바꿔야 한다.
- `review.stages` 의 design·implementation 이 지금 카드 한 장에 붙어 있다. 리뷰를 액션마다
  하는가 스토리가 끝날 때 하는가.
- `governance.exclude_paths` 와 `guidance_overrides` 가 경로 패턴이다. 폴더가 깊어져도 그대로
  되는가.

### Excluded

구현. 정한 것을 W-00000109 가 쓴다.

## Dependencies

W-00000107 — 계층이 실제로 서고 나서 정해야 한다. 그 전에 정하면 추측이 된다.

## Risks

액션마다 리뷰하면 한 스토리에 리뷰가 여러 번 돌아 비싸진다. 스토리 끝에만 하면 액션 하나가
어긋난 채로 다음 액션이 그 위에 쌓인다. 값과 어긋남 사이의 선택이다.

## Success criteria

- 결정 기록 하나가 위 네 자리에 각각 어느 규모가 대응하는지 정하고, `decisions/pending/` 에
  `status: decided` 로 있다.
- 그 결정의 `## Where this applies` 가 설정 키마다 그 값을 읽는 코드 자리를 적는다.
- 실행자 두 벌이 같은 문장을 갖는다는 것이 결정에 적혀 있다.

## Next action

W-00000107 이 끝난 뒤 실제 계층 위에서 드라이버를 한 바퀴 돌려 보고, 어디서 값이 어긋나는지
관측한 뒤 정한다.

## Progress

DE-00000037 이 물음 넷에 답한다. 코드를 안 고쳤다 — 이 카드는 결정만 낸다.

답의 절반이 "바꿀 것 없음"이다. 시도가 이미 액션마다 세고, 리뷰 단계는 수명 주기에 붙지 규모에
안 붙으며, 경로 패턴은 앞자리로 맞추므로 폴더가 깊어져도 그대로다. 그 셋을 확정해 적었다 —
안 적으면 다음 사람이 같은 물음을 다시 연다.

바뀌는 것은 둘이다. 실행자가 조상 문서를 함께 받고, 반복과 시간 총량이 서브트리 크기에서 나온다.

카드가 예고한 "드라이버를 한 바퀴 돌려 보고 정한다"는 이미 채워져 있었다. W-00000105·106·107 을
실제로 돌리며 값이 어긋나는 자리를 관측했고, 그것이 이 결정의 근거다.

## Verification

이 카드의 산출물은 결정이므로 검사 대신 결정이 요구하는 것을 갖췄는지로 확인한다.

- DE-00000037 이 `decisions/pending/` 에 `status: decided` 로 있고 `work_item` 이 W-00000108 을
  가리킨다.
- 카드가 물은 넷에 각각 답이 있다.
- `## Where this applies` 가 바뀌는 자리 일곱과 **안 바뀌는 자리 셋**을 함께 적는다.
- 실행자 설정 두 벌이 같은 문장을 갖는다는 것이 결정에 적혀 있다.
- `python3 stage/scripts/audit_stage.py --project-root .` — errors=0.

리뷰는 안 붙였다. 이 카드는 `review: not_required` 이고, 결정 기록의 근거가 이번 세션에서 직접
관측한 값이라 다른 쪽이 다시 볼 자료가 카드 밖에 없다.

**소유자 승인 (2026-07-29).** 이 저장소가 정한 설계 완료 기준이 소유자의 리뷰와 승인이다.
결정의 다섯 항목(시도 단위·실행자가 받는 것·리뷰 지점·반복과 시간 상한·경로 패턴)을 소유자에게
보이고 승인받았다. 닫기가 검사 없이 통과하는 것을 막았고, 그래서 이 승인이 기록으로 남았다.

### Executed at close — 2026-07-29

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
WARNING TEMPLATE004 [.stage/official/work/archive/items/README.md]: Stage guidance differs from the current localized template. Run `python3 stage/scripts/refresh_guidance.py --project-root <project-root> official/work/archive/items/README.md` or declare the path in settings.json guidance_overrides.
WARNING TEMPLATE002 [.stage/official/work/archive/items/_epic.md]: Stage template artifact file is missing. Re-run stage-init to repair.
WARNING TEMPLATE002 [.stage/official/work/archive/items/_story.md]: Stage template artifact file is missing. Re-run stage-init to repair.
WARNING TEMPLATE004 [.stage/official/work/archive/items/_template.md]: Stage guidance differs from the current localized template. Run `python3 stage/scripts/refresh_guidance.py --project-root <project-root> official/work/archive/items/_template.md` or declare the path in settings.json guidance_overrides.
WARNING TEMPLATE004 [.stage/work/current/README.md]: Stage guidance differs from the current localized template. Run `python3 stage/scripts/refresh_guidance.py --project-root <project-root> work/current/README.md` or declare the path in settings.json guidance_overrides.
WARNING TEMPLATE002 [.stage/work/current/_epic.md]: Stage template artifact file is missing. Re-run stage-init to repair.
WARNING TEMPLATE002 [.stage/work/current/_story.md]: Stage template artifact file is missing. Re-run stage-init to repair.
WARNING TEMPLATE004 [.stage/work/current/_template.md]: Stage guidance differs from the current localized template. Run `python3 stage/scripts/refresh_guidance.py --project-root <project-root> work/current/_template.md` or declare the path in settings.json guidance_overrides.
WARNING TEMPLATE004 [.stage/work/planned/README.md]: Stage guidance differs from the current localized template. Run `python3 stage/scripts/refresh_guidance.py --project-root <project-root> work/planned/README.md` or declare the path in settings.json guidance_overrides.
WARNING TEMPLATE002 [.stage/work/planned/_epic.md]: Stage template artifact file is missing. Re-run stage-init to repair.
WARNING TEMPLATE002 [.stage/work/planned/_story.md]: Stage template artifact file is missing. Re-run stage-init to repair.
WARNING TEMPLATE004 [.stage/work/planned/_template.md]: Stage guidance differs from the current localized template. Run `python3 stage/scripts/refresh_guidance.py --project-root <project-root> work/planned/_template.md` or declare the path in settings.json guidance_overrides.
Summary: errors=0, warnings=12
```

## Retrospective

[R-00000105](retrospectives/R-00000105.md) 가 본문을 쥔다.

물음 넷 중 둘은 지금 동작이 이미 옳았다. 그것을 확인하고 "안 바뀐다"로 닫는 것이 이 카드가 한
일의 절반이다.

## Promotion decision

**official 로 안 올린다.** 결정 기록 자체가 산출물이고 `decisions/pending/` 에 있다. 카드와
회고는 보관으로 간다.
