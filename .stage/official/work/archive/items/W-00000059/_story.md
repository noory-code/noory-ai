---
id: W-00000059
title: 플레인리 스타일에 한국어 문장 규칙 추가
kind: documentation
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000058
promotion: not_applicable
review: not_required
scope: .plainly/
promotes:
decision_refs:
---

# W-00000059 플레인리 스타일에 한국어 문장 규칙 추가

## Purpose

한국어 답변이 영어 직역체로 나오지 않도록 프로젝트 스타일 파일에 규칙을 넣는다

## Scope

`.plainly/style.md`에 한국어 문장 규칙을 더한다. 이 프로젝트가 쓰는 스타일은 내장 프로필이
아니라 이 파일이며, `.plainly/settings.json`이 그것을 가리킨다. 내장 프로필과 플러그인 코드는
건드리지 않는다.

## Success criteria

- 훅이 새 규칙을 포함한 스타일을 실제로 주입한다.
- 플레인리 테스트가 통과한다.

## Related truth

없음. 이 파일은 이 프로젝트의 대화 스타일이며 Stage 공식 진실이 아니다.

## Progress

세션 중 사용자 지적에서 나왔다 — "안내 산문의 드리프트는 감사가 감지하고"가 무슨 뜻인지
읽히지 않는다는 것. 원인은 어휘 수준이 아니라 영어 문장을 단어 단위로 옮긴 것이었다.

규칙 세 줄을 더했다: 영어 용어를 아무도 쓰지 않는 한자어로 치환하지 말 것, 이름보다 그것이
무엇이고 왜 문제인지를 먼저 말할 것, 영어 명사구를 흉내 낸 표현 대신 사람이 말하는 동사를
쓸 것. 실패한 문장을 그대로 예시로 박아 두었다.

훅을 직접 실행해 새 규칙이 주입되는 것을 확인했다.

## Verification


### Executed at close — 2026-07-25

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 38 tests in 0.946s

OK

$ python3 plainly/scripts/configure.py show --project-root .
[exit 0]
source: file:/Users/woogis/Workspace/repo/noory-ai/.plainly/style.md
profile: external
```

## Retrospective


## Promotion decision
