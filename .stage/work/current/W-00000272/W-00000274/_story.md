---
id: W-00000274
title: Distill이 근거와 함께 현재 적용할 기준을 반환하게 한다
kind: development
venue: codex
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: /Users/woogis/Workspace/novel-workspace/novel-ai/plugins/distill/
promotes:
decision_refs:
---

# W-00000274 Distill이 근거와 함께 현재 적용할 기준을 반환하게 한다

## Purpose

새 선택에서 적용 범위에 맞는 현재 기준과 그 근거를 사용할 수 있게 합니다

## Actions

W-00000273에서 교환 형식을 정한 뒤 Distill 저장소에서 실패하는 테스트부터 작성합니다.

## User value

관련 없는 프로젝트의 규칙이나 바뀐 옛 기준 때문에 잘못 선택하는 일을 줄입니다.

## Scope

### Included

- 기존 저장소에 기준의 출처, 발언 주체, 확인 여부, 조건·예외와 변경 관계를 보존합니다.
- 현재 적용할 기준을 조회하고 근거를 함께 반환합니다.
- 기존 데이터의 읽기·이동·규칙 생성에 새 필드가 미치는 영향을 검사합니다.
- 해당 저장소의 버전·변경 기록·테스트 규칙을 따릅니다.

### Excluded

- Stage나 Avatar의 내부 코드를 import하지 않습니다.
- Codex 대화 전체의 자동 수집을 암묵적으로 추가하지 않습니다.

## Risks

현재 recall은 읽은 경로에서 supersedes 관계를 조회하지 않습니다. 실제 실패를 테스트로 재현한 뒤 고칩니다.
metadata.py의 insert와 move, 추출·규칙 생성·검색의 모든 필드 전달 경로를 확인해야 합니다.
noory-ai의 드라이버가 외부 저장소 변경을 자동으로 관측한다고 가정하지 않습니다.

## Success criteria

- 사람이 밝힌 기준과 AI의 추정을 저장하고 조회할 때 구별합니다
- 조건과 예외와 기준 변경을 보존하고 다른 프로젝트의 기준이나 대체된 기준을 현재 기준으로 반환하지 않습니다
- 기존 기록과 저장·검색 경로를 유지하고 두 호스트가 같은 형식으로 기준을 읽을 수 있습니다

## Next action

W-00000273의 설계를 검토한 뒤 Distill 저장소 안에서 실행할 항목과 좁은 검증 명령을 정합니다. 그 전에는 구현하지 않습니다.

## Related truth

SSOT, MECE, TDD, Fail Fast, Honesty를 적용합니다.
실제 경로와 독립성 규칙은 부모 카드에서 확인합니다. novel-ai에는 현재 .stage 디렉터리가 없습니다.

## Progress

2026-10-05: 현재 소스를 읽고 등록했습니다. 제품 파일은 바꾸지 않았습니다.

## Verification

변경 전 기준 확인: Distill 패키지에서 `uv run --frozen python -m pytest tests/test_metadata.py tests/test_tools_recall.py tests/test_r8_independence.py -q`를 실행해 기존 테스트 50개가 통과했습니다.
`uv run --frozen pytest ...`는 pytest 실행 파일을 시작하지 못했습니다. `uv sync --frozen --group dev` 뒤 모듈 실행 방식으로 확인했습니다.
이는 새 기준 기능의 검증이 아니라 기존 동작의 기준 기록입니다.

새 실패 사례의 RED와 수정 뒤 GREEN, 기존 테스트·mypy·ruff·독립성 검사를 기록합니다.

## Retrospective

해당 저장소의 실제 변경과 검증 뒤 작성합니다.

## Promotion decision

pending
