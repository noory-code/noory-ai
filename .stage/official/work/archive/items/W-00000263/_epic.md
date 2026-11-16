---
id: W-00000263
title: 플레인리 스타일을 클로드 코드 output style 로 내보낸다
kind: planning
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000263
promotion: not_applicable
review: not_required
scope: plainly/
promotes:
decision_refs:
---

# W-00000263 플레인리 스타일을 클로드 코드 output style 로 내보낸다

## Purpose

플레인리의 지침이 클로드의 문장에 실제로 걸리게 하고 한국어 답에서 영어 직역 문장을 없앤다.

## Stories

- W-00000264 — 한국어 규칙 1을 명사가 동작을 삼킨 문장까지 잡게 다시 쓴다
- W-00000265 — 스타일을 output style 로 낼 때 무엇을 어디에 둘지 정한다(DE-00000073)
- W-00000266 — 정한 대로 스타일 파일을 내고 훅을 물러나게 한다
- W-00000267 — 플레인리를 릴리스하고 새 세션에서 한국어 답을 확인한다
- W-00000271 — 시험한 Plainly 지침을 적용하고 새 질문으로 한국어를 확인한다

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 새 버전을 켠 세션에서 한국어 답을 받아 보고 동작이 명사에 갇힌 문장이 없다고 사람이 확인한다
- 스타일이 클로드 코드의 output style 목록에 뜨고 고르면 시스템 프롬프트로 들어간다
- 스타일을 켠 상태에서 기본 코딩 지침이 사라지지 않는다

## Next action


## Related truth


## Progress

다섯 스토리가 모두 닫혔다. 플레인리는 output style 로 나갔고(0.6.0), 한국어 지침을 0.7.1, 0.7.2,
0.7.3 으로 고쳤다. DE-00000073 은 W-00000265 가 공식 결정 기록으로 올렸다.

## Verification

- 첫째 기준(사람이 확인한다): 사용자가 2026-11-16 에 "ㅇㅋ 1 은 충분한듯"이라고 판정했다. 기준
  문구는 "명사에 갇힌 문장이 없다"이지만, 같은 날 0.7.1 이 켜진 긴 작업 세션에서 사용자가 그런
  문장을 여러 번 고쳐 줬다. 사용자는 그 문장들로 지침을 0.7.3 까지 고친 뒤 이 정도면 충분하다고
  판정했다. "하나도 없다"를 확인한 것이 아니라 사람이 충분하다고 받아들인 것이다.
- 둘째 기준(목록에 뜨고 시스템 프롬프트로 들어간다): W-00000267 이 확인했다. 실제 설정으로 띄운
  세션이 시스템 프롬프트에 `# Output Style: plainly:Plainly` 절이 있다고 인용했다. 지금 이 세션도
  같은 절을 싣고 있다. `claude plugin list` 는 0.7.3 을 읽는다.
- 셋째 기준(코딩 지침이 사라지지 않는다): 스타일 파일이 `keep-coding-instructions: true` 를 선언하고
  `plainly/tests/test_contract.py` 가 그 값을 확인한다. 2026-11-16 이 대화형 세션(스타일이 켜진
  상태)의 시스템 프롬프트에 도구 사용·커밋·파일 참조 같은 기본 작업 지침이 플레인리 절과 함께
  들어 있는 것을 Claude 가 직접 봤다. 스타일을 껐을 때와 나란히 비교한 것은 아니다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 19 tests in 0.002s

OK
```

## Retrospective

[R-00000263](../retrospectives/R-00000263.md)

## Promotion decision

`not_applicable` — 에픽 자체가 올릴 산출물은 없다. 에픽이 낸 결정 DE-00000073 은 W-00000265 가
올렸다.
