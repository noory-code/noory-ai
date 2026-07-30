---
id: W-00000138
title: 정직성 규칙이 스타일 선택과 무관하게 살아남는다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s plainly/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: plainly/hooks/inject_style.py, plainly/styles/baseline.md, plainly/tests/, plainly/README.md, plainly/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000138 정직성 규칙이 스타일 선택과 무관하게 살아남는다

## Purpose

plainly 는 이미 어떤 스타일을 골라도 살아남는 고정 규칙 자리를 갖고 있다 — 언어 품질 규칙이 그 자리에 있고 README 가 그렇게 선언한다. 그런데 정직성 규칙(추측을 사실로 말하지 않는다, 확인 안 된 주장은 표시한다)은 그 자리가 아니라 baseline.md 안에 있다. 외부 스타일 파일은 baseline 을 통째로 대체하므로(runtime.py 의 style_file 갈래는 baseline 을 안 붙인다) 그 규칙이 아무 경고 없이 사라진다. 이 저장소가 그 상태다 — .plainly/style.md 25 줄에 해당 문장이 없고, 오늘 하루 그대로 돌았다. 문체는 고르는 것이고 안 속이는 것은 고르는 것이 아니다. 0.4.0 이 언어 규칙을 스타일에서 고정 주입으로 옮긴 것과 같은 판단을 정직성에도 적용한다.

## Actions

- 정직성 규칙을 고정 주입으로 옮긴다 — `inject_style.py` 의 `communication_context()` 가
  경계 밖에 붙이는 문장들 자리다. 언어 규칙이 이미 거기 있으므로 새 구조가 아니다.
- `baseline.md` 에서 같은 문장을 뺀다. 두 자리에 두면 매 응답에 두 번 실린다 — 이 플러그인이
  스스로 금지하는 반복이다.
- **CHANGELOG 맨 위에 `## Unreleased` 절을 만든다.** plainly 가 이 저장소의 새 릴리스 규칙
  (카드는 미출시 절에만 적고 버전은 릴리스가 정한다)을 처음 받는 자리다. 루트 `CLAUDE.md` 가
  "처음 도입할 때 제목 바로 아래 만들라"고 지시한다. **매니페스트 버전은 안 건드린다.**
- README 의 고정 규칙 서술을 고친다. 지금 언어 규칙만 "모든 스타일에 적용된다"고 말하는데,
  정직성도 같은 자리에 서므로 함께 적는다.
- 테스트로 고정한다.

## Scope

`plainly/hooks/inject_style.py`, `plainly/styles/baseline.md`, `plainly/tests/`,
`plainly/README.md`, `plainly/CHANGELOG.md`.

**안 하는 것**: 외부 스타일 파일이 baseline 을 대체하는 동작 자체. 그것은 스타일 저자에게
전권을 주는 설계 선택이고, 정직성이 고정 주입으로 올라가면 위험이 사라진다. `.plainly/style.md`
(이 저장소의 스타일)도 안 건드린다 — 사용자 소유 문서다.

## Success criteria

- 정직성 규칙(추측을 사실로 말하지 않음, 확인 안 된 주장 표시)이 **스타일 경계 밖** 고정
  문장에 있다. 내장 프로필이든 외부 파일이든 주입 결과에 그 문장이 있는 것을 테스트가
  고정한다 — 외부 파일 경우를 반드시 포함한다.
- 같은 문장이 `baseline.md` 에 남아 두 번 실리지 않는다. 테스트가 고정한다.
- `plainly/CHANGELOG.md` 맨 위에 `## Unreleased` 절이 서 있고 이 변경 항목이 그 아래 있다.
  **매니페스트 버전 둘은 0.4.1 그대로다.**
- README 가 정직성도 모든 스타일에 적용되는 고정 규칙으로 서술한다.
- `python3 -m unittest discover -s plainly/tests -q` 가 통과한다.

## Related truth

- `plainly/CHANGELOG.md` 의 0.4.0·0.4.1 — 언어 규칙을 스타일에서 고정 주입으로 옮긴 선례
- 루트 `CLAUDE.md` 의 Plugin Changes — 미출시 절과 릴리스 시점 버전 매기기


## Progress


## Verification


## Retrospective


## Promotion decision
