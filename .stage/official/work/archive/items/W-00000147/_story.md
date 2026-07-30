---
id: W-00000147
title: 시도가 오를 때 누가 실행하고 판정하는가
kind: design
venue: claude
milestone:
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000147
promotion: promoted
review: not_required
scope: .stage/decisions/pending/
promotes: .stage/official/decisions/records/DE-00000044.md, .stage/official/decisions/index.md
decision_refs: DE-00000044
---

# W-00000147 시도가 오를 때 누가 실행하고 판정하는가

## Purpose

같은 모델이 같은 벽을 세 번 친다. 드라이버는 venue 마다 고정된 명령 하나를 갖고, 시도가 1에서
3으로 올라도 실행자와 리뷰어가 그대로다. 시도 상한(3)에 걸리면 카드가 막히고 스토리 설계로
되돌아간다(DE-00000038) — 그런데 막힌 이유가 "일이 어렵다"가 아니라 "이 등급이 못 푼다"일 수 있고,
지금은 그 둘을 가를 방법이 없다.

obra/superpowers 가 이 축을 명시적으로 갖는다: 역할마다 모델을 **반드시** 지정하고(생략하면 세션의
가장 비싼 모델이 조용히 붙는다), 고침 4~5바퀴는 막힌 실행자보다 한 등급 위로 올리고, 계획에 코드가
다 적힌 옮겨 쓰기 수준의 일은 가장 싼 등급에 준다. 근거로 "토큰 단가보다 턴 수가 비싸다 — 싼 모델이
다단계 일에서 2~3배 턴을 쓴다"를 적어 뒀다.

이 프로젝트에도 증거가 있다. R-00000127 이 claude venue 가 codex 보다 느려 900초 바닥이 문서 카드
에도 모자랐다고 기록했고, venue 별 시간 특성이 어디에도 없다는 것을 함께 적었다.

물음: **시도가 오를 때 누가 실행하고 누가 판정하는가.** 그리고 그 축을 설정 스키마의 어디에 두는가.

## Actions

- 결정 기록을 세운다. 물음 넷에 답한다:
  - **등급 축을 어디에 두나** — venue 마다 명령 여럿(예: `executors.codex` 를 시도별 목록으로)인가,
    아니면 명령 안의 자리표시자를 드라이버가 채우나. 뒤쪽은 명령 문법을 드라이버가 알아야 한다.
  - **언제 올리나** — 시도 2부터인가 3부터인가. 상한이 3이므로 3에서 올리면 한 번만 쓰인다.
  - **리뷰어도 올리나** — 판정이 흔들려서 막히는 경우와 실행이 못 해서 막히는 경우는 다르다.
  - **안 올리는 길을 남기나** — 프로젝트가 등급을 안 쓰겠다고 선언할 수 있어야 한다. 지금 설정으로
    돌던 프로젝트가 스키마 변경만으로 깨지면 안 된다.
- 기존 계약과의 관계를 명시한다 — DE-00000034(한 바퀴의 역할 계약), DE-00000037(시도는 액션마다,
  반복은 실행 전체), DE-00000017(에스컬레이션 1급 상태와 폭주 상한). 등급을 올리는 것이
  에스컬레이션과 어떻게 다른지 적는다. 안 적으면 두 장치가 같은 일을 두 번 한다.
- 적용 자리를 센다. 최소로 세어 둔 것: `.stage/settings.json` 의 `executors` **두 벌**,
  `review.reviewers` **두 벌**, `review.strengths` **네 벌**, 템플릿 `settings.jsonc`,
  `drive.py` 의 명령 고르는 자리와 시도 계수 자리, `stage/docs/`, `stage/scripts/tests/`.
- **비용을 정직하게 적는다.** 등급을 올리면 그 바퀴가 비싸진다. 값은 "막히는 카드가 줄어드는 것"
  이고, 그것을 재려면 지금 막힌 카드가 왜 막혔는지 기록이 있어야 한다. 없으면 이 결정은 추측 위에
  선다 — 그 사실을 적는다.

## Scope

`.stage/decisions/pending/`.

**안 하는 것**: 코드 변경. 구현은 뒤따르는 fix 카드(codex)가 받는다. W-00000146(재리뷰 범위)과
**같은 설정 항목을 건드리므로** 두 결정이 함께 "구현은 한 번에"를 적는다.

## Success criteria

- 결정 기록이 서고 `status: decided` 다. 위 물음 넷에 각각 답한다.
- **결정을 쓰기 전에 지금 어떤 모델로 도는지 설정에서 읽는다.** 초안이 "한 등급 위로 올린다"였는데
  실제로는 두 venue 다 각 surface 의 최상급이라 올릴 자리가 없었다. 현재 값을 안 읽고 쓴 설계는
  전제부터 틀린다.
- 결정이 **기존 설정으로 돌던 프로젝트가 안 깨지는 길**을 정한다.
- 적용 자리 표에 설정의 두 벌·두 벌·네 벌이 각각 적힌다.
- 값의 근거가 추측인지 실측인지 구분해 적는다. 지금 막힌 카드의 원인 기록이 없다면 그것을 한계로
  적고, **축을 다시 여는 조건**을 남긴다.

## Related truth

- R-00000127 — claude venue 가 codex 보다 느리고 900초 바닥이 문서 카드에도 모자랐다. venue 별
  시간 특성이 어디에도 없다.
- DE-00000034 / 37 / 17 — 한 바퀴의 역할 계약, 시도는 액션마다, 에스컬레이션 상한.
- DE-00000038 — 액션이 실패하면 스토리 설계로 되돌아간다. 등급 때문에 막힌 것과 설계가 틀려서
  막힌 것을 가르지 못하면 이 규칙이 잘못된 신호를 준다.
- obra/superpowers `skills/subagent-driven-development/SKILL.md` 의 Model Selection 절 — 원본
  근거. "생략하면 세션 모델이 붙는다", "단가보다 턴 수", "고침 4~5바퀴는 한 등급 위".
- [[reference_superpowers]] 의 후보 2번.

## Progress


## Verification


### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000147](../../retrospectives/R-00000147.md) — 값이 실측이 아니라는 것을 결정에 적었다.

## Promotion decision

FINAL: promoted. DE-00000044 는 앞으로의 실행을 구속하는 계약이므로 DE-00000030 의 판정에 따라
`official/decisions/records/` 로 승격한다.
