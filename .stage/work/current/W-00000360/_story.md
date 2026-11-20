---
id: W-00000360
title: 훅 고침 브랜치에 main을 합쳐 PR #69의 충돌을 푼다
kind: chore
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "cd evonest && uv run python -m pytest tests/test_hooks_json.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: evonest/CHANGELOG.md,evonest
promotes:
decision_refs:
---

# W-00000360 훅 고침 브랜치에 main을 합쳐 PR #69의 충돌을 푼다

## Purpose

PR #69가 main과 충돌 없이 머지된다

## Actions

액션으로 나누지 않는다. 머지 커밋 하나를 만드는 일이다.

## User value

PR #69(훅 명령이 Windows 에서 `python` 을 부르게 한 고침)는 PR #70 이 먼저 머지되면서 main 과 충돌한다.
이 일이 끝나면 PR #69 를 머지할 수 있다.

## Scope

### Included

- 브랜치 `claude/hook-python-on-windows` 에 main 을 합친 머지 커밋.
- 보관 목록(`official/work/archive/index.md`)의 충돌은 양쪽 줄을 모두 남겨 푼다.
- evonest 변경 기록에 두 개가 된 `## Unreleased` 절을 하나로 합친다.

### Excluded

- main 에서 온 evonest 파일들의 내용은 고치지 않는다. PR #70 에서 이미 리뷰를 받고 머지된 것이다.
- 관문이 머지 커밋을 구분하지 못하는 것은 이 카드에서 고치지 않는다.

## Risks

- 이 카드를 닫는 동안 main 이 또 바뀌면 다시 충돌할 수 있다. 닫은 뒤 바로 머지한다.

## Success criteria

- main을 합친 브랜치에서 감사와 Stage 훅 테스트, evonest 테스트가 통과한다
- evonest 변경 기록에 Unreleased 절이 하나만 있고 훅 고침과 PR #70의 고침이 모두 그 안에 있다
- 보관 목록에 W-00000356, W-00000357, W-00000358 줄이 모두 있다

## Next action

머지 커밋을 만들어 push 하고, 닫기 리뷰를 받아 닫은 뒤 PR #69 를 머지한다.

## Related truth

- 변경 기록 규칙: 루트 `CLAUDE.md` 의 `Plugin Changes`.
- 충돌한 고침의 카드: W-00000358(훅 명령), W-00000356 과 W-00000357(PR #70).

## Progress

- W-00000358 을 닫고 보관한 뒤에 충돌을 알았다. 열린 카드가 없어 관문이 머지 커밋을 막았고, 사용자가
  2026-11-20 에 "카드 등록해 진행" 이라고 해서 이 카드를 등록했다.
- 카드 번호는 W-00000360 이다. Windows 세션의 PR #71 이 W-00000359 를 쓰고 있어서 건너뛰었다.
- 보관 목록은 W-00000356, W-00000357, W-00000358 순서로 세 줄을 남겼다.
- evonest 변경 기록은 훅 고침 줄을 main 쪽 `## Unreleased` 의 `### Fixed` 끝으로 옮기고, 아래쪽에 있던
  두 번째 `## Unreleased` 절을 지웠다.

## Verification

맥북(macOS)에서 main 을 합친 작업 폴더로 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 stage/scripts/audit_stage.py` | errors=0, warnings=32 였다. |
| `python3 -m unittest discover -s stage/hooks/tests -q` | 통과했다(`OK`). |
| `uv run python -m pytest -q` (evonest) | 441개가 통과했다. |
| `grep -c '^## Unreleased' evonest/CHANGELOG.md` | 1 이 나왔다. |

- Windows 에서는 실행하지 않았다. 이 카드는 Windows 동작을 고치지 않는다.
- 닫기 리뷰는 Claude 대역(`claude_review_companion.py`)으로 받는다. 같은 모델의 리뷰다(DE-00000086).
- 고친 경로는 evonest 변경 기록과 보관 목록이고 관문 경로가 아니다. DE-00000087 의 사용자 확인 대상이 아니다.

## Retrospective

## Promotion decision
