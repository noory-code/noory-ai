---
id: W-00000139
title: 사용자에게 하는 말이 스타일 선택과 무관하게 존댓말로 선다
kind: fix
venue: codex
milestone:
source:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000139
promotion: not_applicable
review: passed
scope: plainly/hooks/inject_style.py, plainly/tests/, plainly/README.md, plainly/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000139 사용자에게 하는 말이 스타일 선택과 무관하게 존댓말로 선다

## Purpose

plainly 가 정하는 것은 문체다. 그런데 한국어는 상대를 어떻게 부르는지가 문법에 박혀 있어서,
어형을 아무도 정해 주지 않으면 남은 지시("짧게", "결론 먼저")만 작동해 평서체가 나온다. 지금
세 층 어디에도 어형이 없다 — 플러그인 `styles/baseline.md`, 이 저장소의 `.plainly/style.md`,
`inject_style.py` 가 스타일 경계 밖에 붙이는 고정 문장(정직성 규칙, 언어 규칙). 그래서 이
저장소가 사용자에게 반말체로 답하는 상태로 실제로 돌았고, 사용자가 그것을 지적했다.

문체는 고르는 것이지만 상대를 낮춰 부르지 않는 것은 고르는 것이 아니다. 아무도 안 정했을 때의
기본값이 무례하면 그것은 선택이 아니라 결함이다. 자리는 W-00000138 과 같다: 외부 스타일 파일은
baseline 을 통째로 대체하므로(`runtime.py` 의 `style_file` 갈래는 baseline 을 안 붙인다) 스타일
안에 넣으면 이 저장소에서 또 조용히 사라진다.

## Actions

- `inject_style.py` 의 `communication_context()` 에서 **스타일 센티널 밖** 고정 문장에 어형
  규칙을 붙인다. 언어 규칙이 이미 그 자리에 있으므로 새 구조가 아니라 그 규칙의 연장이다.
- 규칙이 담을 것 둘:
  - 문법적 공대 어형을 가진 언어(한국어, 일본어 등)로 답할 때는 읽는 사람을 높이는 정중한
    어형을 기본으로 쓴다.
  - 스타일 본문이 다른 어형을 명시적으로 지시하면 그 지시를 따른다. 어형은 스타일이 소유하는
    축이고, 고정 규칙은 아무도 안 정했을 때의 기본값만 정한다.
- 테스트로 고정한다 — 내장 프로필 경로와 외부 `style_file` 경로 둘 다.
- `CHANGELOG.md` 의 기존 `## Unreleased` 절에 항목을 더한다. **매니페스트 버전 둘은 0.4.1
  그대로다.**
- README 의 고정 규칙 서술에 어형 기본값을 함께 적는다. 지금 정직성과 언어 규칙만 "스타일과
  무관하게 적용된다"고 말한다.

## Scope

`plainly/hooks/inject_style.py`, `plainly/tests/`, `plainly/README.md`,
`plainly/CHANGELOG.md`.

**안 하는 것**: `plainly/styles/*.md` 와 `.plainly/style.md` 는 건드리지 않는다. 앞의 것은
같은 규칙을 두 번 싣게 되고(플러그인이 스스로 금지하는 반복), 뒤의 것은 사용자 소유 문서다.
외부 스타일이 baseline 을 대체하는 동작 자체도 안 건드린다 — W-00000138 이 판단한 대로 그것은
스타일 저자에게 전권을 주는 설계이고, 규칙이 고정 주입으로 올라가면 위험이 사라진다.

## Success criteria

- 주입 결과의 **스타일 센티널 밖**에 어형 규칙이 자기 단락으로 서고, 공대 어형이 있는 언어에서
  정중한 어형이 기본이라고 말한다. **스타일이 뒤집을 수 있다는 예외 조항은 넣지 않는다.**
- 한국어로 실제 답을 받아 어형을 눈으로 확인한다. 문자열이 실렸다는 것만으로는 이 카드의 목적이
  안 선다 — 사용자가 지적한 것은 문장이 아니라 나온 말투였다.
- 테스트가 두 경로를 각각 검사한다 — 내장 프로필로 해결된 경우와 프로젝트 `style_file` 로
  해결된 경우. 외부 파일 경로가 빠지면 이 카드는 목적을 못 세운다.
- 같은 규칙 문장이 `plainly/styles/` 의 어느 파일에도 없다. 테스트가 고정한다.
- `python3 -m unittest discover -s plainly/tests -q` 가 통과한다.
- `plainly/CHANGELOG.md` 의 `## Unreleased` 절 아래에 이 변경 항목이 있고, 매니페스트 버전
  둘은 `0.4.1` 그대로다.
- README 가 어형 기본값을 스타일과 무관한 고정 규칙으로 서술한다.

## Related truth

- W-00000138 (보관) — 정직성 규칙을 같은 자리로 옮긴 선례. 외부 스타일이 baseline 을 대체해
  규칙이 사라지는 경로를 그 카드가 확인했다.
- `plainly/src/plainly/runtime.py` 의 `_style_from_settings` — `style_file` 갈래가 baseline 을
  붙이지 않는다는 사실의 자리.


## Progress

- codex 실행자가 규칙을 고정 주입에 넣고 테스트·README·CHANGELOG 를 붙였다. claude 리뷰어가
  기준 6개 전부 PASS(`approved: true`)로 판정했다.
- **그 판정 뒤에 감독자(Claude 세션)가 문구를 고쳤다.** 리뷰어가 기준 밖 지적으로 남긴 두 가지가
  실제로 목적을 깨는 것이었다:
  - 예외 조항("스타일이 다른 어형을 명시하면 따른다")이 `professional.md` 의 "neutral workplace
    register" 와 부딪친다. 한국어에서 그 문구는 평서체로도 읽히므로, 탈출구가 이 카드가 막으려던
    결과를 그대로 허용한다. **조항을 없앴다** — 아무 내장 스타일도 어형을 지목하지 않으므로 쓰는
    데가 없고(AHA), 규칙의 일이 압력 아래에서 버티는 것인데 예외 조항은 그 협상을 다시 연다.
  - 규칙이 언어 규칙 문단의 꼬리에 붙어 있었다. 0.4.1 이 "문단 끝에 묻어서 안 물었다"를 실패
    원인으로 적어 둔 배치다. `Register rule:` 라벨을 준 독립 문단으로 꺼냈다.
- 리뷰어의 테스트 지적 둘도 받았다: 어형 테스트를 네 해결 경로 subTest 로 접어 `NOORY_STYLE_FILE`
  경로까지 덮고, 외부 `style_file` 테스트가 그 갈래를 실제로 탔다는 것(외부 본문 존재 + baseline
  부재)을 단언한다.
- 드라이버 단계의 판정은 예외 조항이 있던 문구를 본 것이다. 닫기가 구현 단계 리뷰를 최종 코드로
  다시 돌려 통과했으므로(아래 `Independent review at close`), 지금 코드에도 독립 판정이 서 있다.

## Verification

- `python3 -m unittest discover -s plainly/tests -q` → 44개 OK (문구 교체 후 재실행).
- **동작 확인**: 이 저장소에서 `claude -p "한국어로 한 문장만: plainly 플러그인은 무엇을
  하나요?"` → "…유지해 주는 플러그인입니다." 존댓말로 돌아왔다. 문자열이 실렸다는 것과 말투가
  바뀌었다는 것은 다른 주장이고, 사용자가 지적한 것은 뒤쪽이므로 따로 확인했다.
- RED 을 실제로 봤다: 표지 문구를 바꾼 테스트가 구현 전 3개 실패(이유 정확) → 구현 후 통과.
- `NOORY_STYLE_PROFILE=professional claude -p "한국어로 한 문장만: 이 저장소는 무엇인가요?"` →
  "…저장소입니다." 리뷰어가 잠복 위험으로 지목한 프로필에서도 어형이 선다.

### 리뷰 지적 처리

기계 판정은 기준 6개 전부 PASS(`approved: true`). 리뷰어가 기준 밖으로 남긴 지적 넷은 이렇게
처리했다.

| 지적 | 처리 | 이유 |
|---|---|---|
| 예외 조항이 `professional` 프로필의 "neutral workplace register" 와 부딪친다 | accept | 그 상황이 이 프로젝트에 온다 — 한국어에서 그 문구는 평서체로도 읽히고, 그러면 탈출구가 이 카드의 목적을 그대로 허용한다. 조항을 없앴고 그 프로필로 실측해 어형이 서는 것을 확인했다 |
| 규칙을 또 언어 규칙 문단 꼬리에 묻었다 | accept | 같은 파일의 0.4.1 항목이 그 배치를 실패 원인으로 적어 뒀다. `Register rule:` 독립 문단으로 꺼냈다 |
| 어형 테스트 둘이 표지를 복제하고 `NOORY_STYLE_FILE` 경로를 안 덮는다 | accept | 네 해결 경로 subTest 로 접었다. 정직성 규칙 테스트와 같은 모양이 됐다 |
| 외부 `style_file` 테스트가 그 갈래를 탔다는 것을 안 단언한다 | accept | 해결이 깨져 baseline 으로 떨어지면 테스트가 조용히 통과한다. 외부 본문 존재 + baseline 부재를 단언한다 |

### Executed at close — 2026-07-30

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 44 tests in 1.288s

OK

$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 44 tests in 1.324s

OK
```

### Independent review at close — 2026-07-30

```
Review report: .stage/.runtime/driver/logs/W-00000139.md
```

## Retrospective

[R-00000139](../../retrospectives/R-00000139.md) — 아무도 안 정한 기본값은 선택이 아니라 결함이다.

## Promotion decision

FINAL: not_applicable. plainly 플러그인 코드·문서 변경이고 `.stage/official/` 로 승격할 산출물이
없다.
