---
id: W-00000386
title: 실행자 모델이 사용량 한도에 걸리면 같은 venue의 다른 모델로 넘어가는 순서를 둔다
kind: development
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/
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
