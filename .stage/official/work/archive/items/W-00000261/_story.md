---
id: W-00000261
title: 한국어 쓰는 법을 한국어로, 낱말 목록이 아니라 규칙으로 다시 적는다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "cd plainly && env -u NOORY_STYLE_FILE -u NOORY_STYLE_PROFILE python3 -m unittest discover -s tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000261
promotion: not_applicable
review: not_required
scope: plainly
promotes:
decision_refs:
---

# W-00000261 한국어 쓰는 법을 한국어로, 낱말 목록이 아니라 규칙으로 다시 적는다

## Purpose

한국어를 어떻게 쓰라는 지침이 영어로 적혀 있어서, 그 지침 자체가 막으려는 방식으로 쓰여 있다.

## Actions


## User value

이 지침은 한국어로 답을 받는 사람이 매번 읽는 글의 질을 정한다. 어색하면 그 사람이 한 줄씩
짚어 줘야 하고, 짚어 준 말만 막히니 다음 대화에서 다른 어색함이 또 나온다.

## Scope

### Included

- 한국어 쓰는 법을 한국어로 다시 적는다.
- 갈래를 막는 규칙 넷으로 다시 세운다 — 동사·이름·세는 말·문장 끊기. 각각에 돌려볼 수 있는
  검사와 앞뒤 짝을 붙인다.
- 그 절이 한국어로 남아 있는지 테스트로 못박는다.

### Excluded

- 프로젝트의 `.plainly/style.md`. 사용자 파일이고, 거기 쌓인 표는 실제 이력이다. 이 카드가
  고치려는 것은 플러그인에 박힌 쪽이다.
- 쓴 글을 검사해서 막는 장치. 그건 따로 볼 일이다.
- 한국어 말고 다른 언어. 겪은 것이 없다.

## Risks

- 지침을 한국어로 적으면 읽는 쪽이 영어 문장을 먼저 세우는 습관을 덜 탄다 — 이건 내가 세운
  설명이지 재 본 것이 아니다. 효과는 다음 세션에서만 보인다.
- 규칙이 늘어 지침이 길어졌다. 다음에 규칙을 더할 때는 갈래가 정말 새로운지 먼저 봐야 한다.

## Success criteria

- 한국어 쓰는 법이 한국어로 적혀 있고 예시도 한국어 앞뒤 짝으로 있다
- 짚어 준 말 하나가 아니라 그 말이 속한 갈래를 막는 규칙으로 적혀 있다
- 읽는 사람이 실제로 돌려볼 수 있는 검사만 적혀 있다 — 소리 내어 읽으라는 식이 아니라

## Next action


## Related truth


## Progress

### 무엇이 어디 있었나

한국어 어투에 영향을 주는 것은 세 군데였다. Plainly 훅이 대화마다 지침을 끼워 넣고(거의
전부가 여기), `novel-ai/CLAUDE.md` 가 "주인과는 한국어로" 한 줄, Stage 가 기록 문서 언어를
`ko` 로 준다. 쓴 글을 검사하는 것은 하나도 없다.

Plainly 가 끼워 넣는 지침은 둘로 갈려 있었다. 프로젝트의 `.plainly/style.md` 는 사용자가
고칠 수 있고, 나머지 절반은 `hooks/inject_style.py` 에 박혀 있어 프로젝트에서 못 고친다.
한국어 절이 그 박힌 쪽에 있었다.

### 무엇을 고쳤나

한국어 절을 한국어로 다시 적었다. 영어로 "한국어는 이렇게 써라"를 적어 두면 읽는 쪽이 영어
문장을 세우고 한국어 낱말을 끼우게 되는데, 그게 바로 그 절이 막으려던 것이다.

앞뒤 짝 셋을 나열하던 것을 갈래 넷으로 세웠다.

1. 동작은 서술어에 둔다 — 검사: 서술어를 찾아라. `-이다`·`-있다`·`-하다`뿐이면 동작이 명사
   안에 갇혀 있다.
2. 이름을 새로 만들지 않는다 — 검사: 이 말을 나 말고 누가 쓰나.
3. 수를 세면 세는 말을 붙인다 — 검사: 숫자 뒤에 명사가 바로 오면 빠뜨린 것이다.
4. 길면 끊는다 — 검사: 주어와 서술어 사이에 다른 서술어가 둘 이상 끼면 나눠라.

"소리 내어 읽어 보고 어색하면 고쳐라"를 뺐다. 읽는 쪽이 소리를 못 낸다. 그 자리에 실제로
돌려볼 수 있는 검사를 넣었다.

마지막 줄에 "고칠 낱말 목록이 아니라 갈래를 막는 규칙"이라고 못박았다. 목록은 그 목록을
만들게 한 낱말만 잡는다.

### 테스트

한국어 절이 플러그인과 함께 다니는지 보던 테스트가 영어 문장으로 못박고 있었다. 한국어
문장으로 바꿨다 — 영어로 못박아 두면 절이 영어로 되돌아가도 통과한다.

## Verification

`plainly` 테스트 51개가 통과한다. 훅을 직접 돌려 끼워지는 글도 눈으로 확인했다.

여기까지가 확인한 것이다. **한국어가 나아졌는지는 확인하지 않았다** — 지금 도는 세션은 옛
지침을 이미 받아 두었고, 새 지침은 다음 세션부터 들어간다. 테스트가 통과한다는 것은 글이
제대로 끼워진다는 뜻이지 효과가 있다는 뜻이 아니다.

### Executed at close — 2026-08-17

```
$ cd plainly && env -u NOORY_STYLE_FILE -u NOORY_STYLE_PROFILE python3 -m unittest discover -s tests -q
[exit 0]
----------------------------------------------------------------------
Ran 51 tests in 1.496s

OK

$ cd plainly && env -u NOORY_STYLE_FILE -u NOORY_STYLE_PROFILE python3 -m unittest discover -s tests -q
[exit 0]
----------------------------------------------------------------------
Ran 51 tests in 1.637s

OK
```

## Retrospective


## Promotion decision
