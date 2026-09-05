---
id: W-00000264
title: 한국어 규칙 1을 명사가 동작을 삼킨 문장까지 잡게 다시 쓴다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: plainly/hooks/inject_style.py, plainly/tests/, plainly/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000264 한국어 규칙 1을 명사가 동작을 삼킨 문장까지 잡게 다시 쓴다

## Purpose

꼬리만 찾던 검사를 바꿔 이사·방식·곳처럼 평범한 명사가 동작을 삼킨 문장도 걸리게 한다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 새 규칙으로 다시 쓴 문장들을 읽고 사람이 문제가 걸러졌다고 확인한다
- 이 대화에서 실제로 나온 어색한 문장이 규칙의 예시로 들어간다

## Next action


## Related truth


## Progress

규칙 1의 검사를 바꿨다. `-것`·`-함`·`-음`·`-화`·`-성` 꼬리와 명사 세 개 연속만 찾던 자리를
빼고, "여기서 뭘 한다는 건가"에 먼저 답한 다음 그 답이 서술어에 없으면 끌어내게 했다. 동작이
숨는 자리 두 곳을 이름 붙였다 — "X하다"가 말이 되는 명사가 되다·이다를 달고 앉는 자리, 그리고
동작을 관형절에 밀어 넣고 속이 빈 명사를 머리에 세운 자리. 예시는 이 대화에서 실제로 나온
문장으로 바꿨다.

처음에는 의심할 명사 목록에 곳·순서·부분도 넣었는데 뺐다. 셋 다 동작을 담는 명사가 아니라,
그대로 뒀으면 "세 군데"나 "그 자리에서" 같은 멀쩡한 말까지 고치게 된다. "아픈 곳"이 어색한
까닭은 곳이 동작을 삼켜서가 아니라 pain point 를 그대로 옮겨서다. 그 예시는 규칙 2로 보냈다.

규칙 본문은 나중에 `plainly/styles/fixed-rules.md` 로 옮겨 갔다(W-00000266). 훅이 사라졌기
때문이다.

## Verification

두 번째 기준은 충족됐다. 이 대화에서 나온 어색한 문장 네 개가 규칙 1과 규칙 2의 예시로 들어갔다.
테스트가 새 문구를 요구하고 옛 좁은 검사 두 개가 돌아오면 깨진다. 고침을 되돌려 검사가 실제로
깨지는 것도 확인했다.

첫 번째 기준은 아직 열려 있다. 사람이 다시 쓴 문장을 읽고 걸러졌다고 확인해야 하는데, 확인용
표를 보여 드린 뒤에 규칙을 한 번 더 고쳤다(곳·순서·부분을 목록에서 뺀 일). 고친 규칙으로 나온
문장은 아직 못 보셨다. W-00000267 에서 새 세션의 답을 보실 때 함께 판정한다.

## Retrospective


## Promotion decision
