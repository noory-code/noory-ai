---
id: W-00000050
title: Plainly 주입 문구에 언어 자연스러움 공통 규칙 추가
kind: fix
venue: codex
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000049
promotion: not_applicable
review: not_required
scope: plainly/hooks/, plainly/tests/, plainly/README.md, plainly/CHANGELOG.md, plainly/.claude-plugin/plugin.json, plainly/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000050 Plainly 주입 문구에 언어 자연스러움 공통 규칙 추가

## Purpose

비영어 답변이 영어 직역투로 나오고 용어가 불필요하게 어렵게 쓰이는 문제를 모든 스타일 경로에서 막는다

## Scope

`plainly/hooks/inject_style.py`의 훅 고정 문구(`communication_context`)에 언어 자연스러움 규칙을
추가한다. 규칙은 스타일 센티널 바깥의 불변 영역에 두어 내장 프로필과 외부 스타일 파일
(`NOORY_STYLE_FILE`, `.plainly/settings.json`의 `style_file`) 모두에 적용된다. 스타일 본문
(`plainly/styles/*.md`)은 외부 스타일 파일이 baseline 전체를 치환하므로 규칙의 위치가 아니다.

회귀 테스트, README의 규칙 설명, CHANGELOG, 두 플러그인 매니페스트의 버전 상향을 포함한다.

## Success criteria

- 훅 출력에 언어 규칙이 네 가지 해석 경로(기본값, `NOORY_STYLE_PROFILE`, 프로젝트 설정,
  `NOORY_STYLE_FILE`) 모두에서 나타난다.
- 외부 스타일 파일을 지정한 경우에도 규칙이 사라지지 않는 테스트가 존재하고 통과한다.
- `python3 -m unittest discover -s plainly/tests -q` 전체 통과.
- `plainly/.claude-plugin/plugin.json`과 `.codex-plugin/plugin.json` 버전이 동일하게 상향되고
  CHANGELOG에 항목이 추가된다.

## Related truth

- 규칙 문구는 영어 직역투(어순·수동태 복사)와 불필요하게 어려운 용어를 함께 금지하되, 실무자가
  실제로 원어로 쓰는 기술 용어는 억지로 번역하지 않도록 예외를 명시한다.
- SSOT: 언어 규칙의 소유 위치는 훅 고정 문구 한 곳이다. 스타일 본문에 중복 기술하지 않는다.


## Progress

- 훅 고정 문구(`plainly/hooks/inject_style.py`의 `communication_context`)에 언어 규칙 추가.
  센티널 바깥이므로 내장 프로필과 외부 스타일 파일 모두에 적용된다.
- `plainly/tests/test_hook.py`에 네 해석 경로 회귀 테스트 추가. 규칙이 스타일 센티널 종료 뒤에
  나타나는지까지 검사해 스타일 본문이 아닌 불변 영역임을 고정한다.
- README에 규칙 설명 1문단, CHANGELOG 0.4.0 항목, 두 매니페스트 버전 0.3.0 → 0.4.0.

## Verification

`python3 -m unittest discover -s plainly/tests -q` → 38 tests, OK (2026-07-24).
Plainly는 선언된 린터/포매터가 없다(스탠다드 라이브러리 전용 패키지).


### Executed at close — 2026-07-24

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 38 tests in 0.986s

OK

$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 38 tests in 0.970s

OK
```

## Retrospective


## Promotion decision
