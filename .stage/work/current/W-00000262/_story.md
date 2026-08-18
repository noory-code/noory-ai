---
id: W-00000262
title: Plainly의 한국어 지침을 비유 없이 다시 쓴다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest plainly.tests.test_hook -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000262
promotion: pending
review: not_required
scope: plainly/hooks/inject_style.py, plainly/tests/test_hook.py, plainly/CHANGELOG.md, plainly/.claude-plugin/plugin.json, plainly/.codex-plugin/plugin.json, .stage
promotes:
decision_refs:
---

# W-00000262 Plainly의 한국어 지침을 비유 없이 다시 쓴다

## Purpose

Plainly가 한국어 문장을 고치는 규칙을 비유나 영어식 문장 없이 직접 설명하게 한다

## Actions

- 네 가지 스타일 설정 경로에서 어색한 문장을 잡는 테스트를 먼저 쓴다.
- 공통 한국어 지침이 주어와 동사를 직접 밝히게 고친다.
- 지침 안에서 쓰던 물리적 비유와 불분명한 주어를 없앤다.
- Plainly 전체 테스트와 실제 훅 출력을 확인한다.
- 두 플러그인 버전을 함께 올리고 설치본을 갱신한다.

## User value

사용자는 AI가 자연스러운 한국어를 쓰라는 지침을 읽고도 그 지침에 든 어색한 표현을 따라 하는
일을 줄일 수 있다.

## Scope

### Included

- 모든 스타일에 공통으로 들어가는 한국어 문장 규칙을 다시 쓴다.
- 기본 스타일, 환경 변수로 고른 스타일, 프로젝트 설정, 외부 스타일 파일을 모두 테스트한다.
- 출시 전 변경 기록에 이번 수정을 적는다.

### Excluded

- 영어권과 다른 언어의 문장 규칙은 바꾸지 않는다.
- 프로젝트마다 정한 말투와 표현 목록은 이 저장소에서 바꾸지 않는다.

## Risks

- 새 문장이 뜻을 줄이면 기존 한국어 검사 기준이 약해질 수 있다. 기존 네 가지 규칙과 예시는
  유지하고 설명만 바꾼다.
- 한 설정 경로만 테스트하면 외부 스타일에서 공통 규칙이 빠질 수 있다. 네 가지 경로를 모두
  같은 테스트로 확인한다.
- 원본을 고쳐도 설치된 0.4.1은 바로 바뀌지 않는다. 커밋과 출시, 다시 설치하기 전까지 현재
  세션은 예전 공통 지침을 받는다.

## Success criteria

- Plainly는 주어와 동사를 분명히 적으라고 자연스러운 한국어로 안내하고 지침 안에서도 비유를 쓰지 않는다
- 어떤 스타일을 골라도 같은 한국어 문장 규칙과 존댓말 기준을 받는다
- 출시한 버전을 설치하면 새 한국어 지침이 실제 대화에 들어간다

## Next action

Plainly 패치 버전을 출시하고 설치한 뒤 실제 훅 출력을 다시 확인한다.

## Related truth

- `plainly/hooks/inject_style.py` — 어떤 스타일을 골라도 함께 넣는 공통 지침을 만든다.
- `plainly/tests/test_hook.py` — 네 가지 스타일 설정 경로와 두 가지 주입 시점을 확인한다.
- `plainly/CHANGELOG.md` — 다음 출시에 들어갈 변경을 적는다.

## Progress

- 기존 지침에서 새 테스트를 먼저 돌렸다. 네 가지 스타일 설정 경로가 모두 실패했다.
- `읽는 쪽`, `명사 안에 갇혀 있다`, `꺼내서 서술어로 세워라`, `그 바닥`, `갈래를 막는 규칙`을
  직접 설명하는 문장으로 바꿨다.
- AI가 하는 일, 동작을 나타내는 동사, 실제로 용어를 쓰는 사람을 주어로 밝혔다.
- 새 테스트와 기존 훅 테스트 열네 개가 통과했다.
- 두 플러그인 버전을 `0.4.2`로 함께 올리고 원격 저장소에 출시했다.
- Claude와 Codex에 `0.4.2`를 설치했다.

## Verification

- RED: 새 테스트 한 개가 네 가지 스타일 설정 경로에서 모두 실패했다.
- GREEN: 같은 테스트가 네 가지 경로에서 모두 통과했다.
- `python3 -m unittest plainly.tests.test_hook -q` — 테스트 열네 개가 통과했다.
- `python3 -m unittest discover -s plainly/tests -q` — 테스트 쉰두 개가 통과했다.
- `python3 -m compileall -q plainly/hooks plainly/scripts plainly/src plainly/tests` — 통과했다.
- 원본 훅으로 현재 프로젝트의 실제 주입 내용을 만들었다. 새 문장은 한 번만 들어갔고 없애기로 한
  표현 다섯 개는 들어가지 않았다.
- Claude와 Codex의 설치본에서 버전이 `0.4.2`인지 확인했다. 두 설치본이 만든 실제 주입 내용은
  필수 문장을 모두 담았고 없애기로 한 표현 다섯 개는 담지 않았다.
- 새 Claude 프로세스에서 한국어 답변을 한 번 확인했다. 답변은 읽을 수 있었지만 “설정 경로 네
  가지를 다 눌러 봤고”라는 어색한 표현이 한 군데 남았다. 지침이 들어간 사실과 Claude가 매번
  지침을 따르는지는 구별해야 한다.
- Stage 감사 결과 오류는 0개다. 기존 경고는 32개다.

## Retrospective

공통 지침 자체는 자연스러운 문장으로 고쳤고 설치본에도 반영했다. 실제 Claude 답변 한 번에서는
어색한 표현이 한 군데 남았다. Plainly가 품질을 높일 수는 있지만 한 번의 지침으로 모든 답변을
보장한다고 말할 수는 없다.

## Promotion decision

공식 문서로 옮길 내용이 없으므로 `not_applicable`로 닫는다.
