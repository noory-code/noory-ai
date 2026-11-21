---
id: W-00000366
title: 도면의 위 두 층을 쓰고 도면 자리를 한 곳으로 정한다
kind: documentation
venue: claude
environment: local-no-codex
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000366
promotion: promoted
review: passed
scope: .stage/official/model,stage/docs/BLUEPRINT.md,stage/README.md,stage/CHANGELOG.md
promotes: .stage/official/model/overview.md
decision_refs: DE-00000090
---

# W-00000366 도면의 위 두 층을 쓰고 도면 자리를 한 곳으로 정한다

## Purpose

AI 가 문서 한 장에서 Stage 의 목표와 레이어와 코드가 말해 주지 않는 것을 읽는다

## Actions


## User value

2026-11-20 에 사용자와 정한 것이다.

- 설계는 둘이다. 일에 대한 계획은 카드와 함께 사라져도 된다. 시스템 도면은 남아야 하고 한곳에 모여야 한다.
- 도면은 층으로 나눈다: 목표, 레이어, 컴포넌트, 컴포넌트 설계. 손으로 쓸 것은 위 두 층과 코드가 말해 주지
  않는 것이다. 아래층은 결정 기록과 코드 위치로 가는 링크만 둔다.
- 레이어 초안: 기록 / 경로와 규칙 / 관문 / 절차 / 검증 / 드라이버 / 점검. 점검(기록이 계약대로인가)과
  검증(일이 목적에 닿았나)은 다른 레이어다.
- 초안을 쓰다 찾은 것: 공용 모듈이 `stage/hooks/` 에 있고 스크립트 46개 가운데 33개가 가져다 쓴다. 이유는
  모른다. `drive.py` 와 `close_work.py` 가 서로를 가져다 쓴다.
- `.stage/official/model/` 에는 빈 양식만 있다. 도면을 올린 적이 없다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 문서 한 장에 목표로 가는 링크와 레이어 일곱 개의 표와 코드가 말해 주지 않는 것이 있다
- 공용 모듈이 hooks 폴더에 있는 이유와 drive.py 와 close_work.py 가 서로를 가져다 쓰는 이유가 적혀 있거나 그 결정 기록으로 가는 링크가 있다
- 도면 노릇을 하는 자리가 한 곳이고 다른 자리는 그곳을 가리킨다

## Next action

## Related truth

## Progress

- `stage/docs/BLUEPRINT.md` 맨 위에 목표(`PHILOSOPHY.md` 로 가는 링크), 레이어 일곱 개의 표, 코드가 말해 주지
  않는 것 네 가지를 썼다. 기존 그림 열일곱 개는 "기록 레이어의 그림" 아래로 한 단계 내렸다. 그림의 내용은
  고치지 않았다.
- 공용 모듈이 `hooks/` 에 있는 이유를 적었다. 관문이 혼자 실행되어야 해서 관문이 쓰는 규칙은 `hooks/` 안에
  있고, 스크립트가 그 정의를 가져다 쓴다. 모듈이 생긴 기록은 `IMPLEMENTATION_AUDIT.md` 의 P33 이다.
- `close_work.py` 와 드라이버가 서로를 가져다 쓰는 이유를 표로 적었다. 드라이버는 `close_work.py` 로 카드를
  닫고, `close_work.py` 는 드라이버 쪽 도구 세 가지를 다시 만들지 않고 쓴다. 근거는 커밋 `55f42715`,
  `381c5cb7`, `244a2199` 의 본문이다. 카드는 `drive.py` 라고 적었지만 `close_work.py` 가 가져다 쓰는 것은
  `drive.py` 가 아니라 `driver_repository.py`, `driver_environment.py`, `driver_lifecycle.py` 다.
- 도면 자리를 `stage/docs/BLUEPRINT.md` 로 정했다(DE-00000090). `stage/README.md` 의 Design 이 이 문서를 도면이라고
  소개한다. `.stage/official/model/overview.md` 가 이 문서를 가리키는 줄은 카드를 닫은 바로 뒤에 쓴다. 승격
  관문이 닫힌 카드에만 `.stage/official/` 쓰기를 허용하기 때문이다. 쓸 내용은 DE-00000090 의 "Where this
  applies" 에 있고, 승격 의도는 만들어 두었다.
- 레이어마다 모듈을 배정하고 가져다 쓰는 방향을 스크립트로 세었다. 굵은 흐름과 다른 방향이 여덟 군데 있어서
  표로 적었다. 여섯 군데는 이유를 찾지 않고 사실만 적었다.
- 범위 밖으로 나간 것: `stage/CLAUDE.md` 와 `stage/AGENTS.md` 에 코드를 고치기 전에 도면을 읽으라는 문단을
  넣었다. AI 가 이 문서에 닿으려면 자동으로 읽히는 문서가 가리켜야 한다. `.stage/decisions/pending/DE-00000090.md`
  와 회고, 카드 파일도 범위 밖이다.

## Verification

맥북(macOS)에서 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest discover -s stage/hooks/tests -q` | 455개 통과 |
| `python3 -m unittest tests.test_plugin_contracts -q` | 7개 통과 |
| `python3 stage/scripts/audit_stage.py --project-root .` | 오류 0건 |

- 레이어 표의 파일 이름이 실제로 있는지는 스크립트로 맞춰 보았다. 어느 레이어에도 들지 않는 파일은
  `scripts/release_plugin.py` 하나이고 도면에 그렇게 적었다.
- 새 세션이 이 문서만 읽고 레이어를 맞게 말하는지는 확인하지 않았다.
- 문서의 링크와 제목 고리가 GitHub 화면에서 열리는지는 눈으로 보지 않았다.
- 닫을 때의 리뷰는 만든 쪽과 같은 계열(Claude)이 본다. 문서만 고친 카드라 리뷰 모델은 `sonnet` 으로 한다.

- Checks at close 2026-11-21: 2 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)
