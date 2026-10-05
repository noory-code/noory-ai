---
id: W-00000276
title: Avatar에서 선택의 이유와 개인 기준의 변화를 살펴보게 한다
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
scope: avatar/
promotes:
decision_refs:
---

# W-00000276 Avatar에서 선택의 이유와 개인 기준의 변화를 살펴보게 한다

## Purpose

사용자가 여러 프로젝트의 선택을 근거와 함께 돌아보고 개인 기준을 직접 확인하거나 고칠 수 있게 합니다

## Actions

W-00000273의 약속을 바탕으로 독립적인 로컬 기록·조회·수정부터 만듭니다.

## User value

자신이 밝힌 기준과 실제 선택, 생각이 달라진 시점을 근거와 함께 돌아볼 수 있습니다.

## Scope

### Included

- 사용자 입력과 명시적으로 받은 기록을 보관하고 원문 출처를 연결합니다.
- 개인 기준의 확인·수정·철회를 남기고 이전 버전과 변경 이유를 조회합니다.
- 다른 선택을 검토 후보로 보여주고 사용자의 판단을 기록합니다.
- 확인한 개인 기준을 내보내며 Claude와 Codex용 스킬·manifest·문서를 제공합니다.
- 로컬 데이터는 플러그인 설치 캐시 밖에 저장합니다.

### Excluded

- 성격이나 숨은 동기를 확정하지 않습니다.
- 기록을 허가 없이 전역 수집하거나 원격으로 전송하지 않습니다.
- 프로젝트 예외를 자동으로 개인의 일반 기준으로 올리지 않습니다.

## Risks

새 플러그인이 Distill의 전역 저장만 반복하면 독립적인 가치가 없습니다. 선택을 돌아보고 기준을 고치는 흐름을 검사합니다.
중복 입력과 동시 쓰기, 삭제된 원문과 형식이 다른 입력을 명시적으로 처리합니다.

## Success criteria

- 직접 입력하거나 다른 플러그인에서 받은 선택과 기준을 출처에 연결해 기록하고 다시 볼 수 있습니다
- 개인 기준을 확인하고 수정하면 이전 내용과 변경 이유가 남으며 프로젝트의 예외를 개인의 일반 기준으로 자동 확정하지 않습니다
- 달라진 선택을 검토할 후보로 보여주고 확인한 개인 기준을 다른 작업에서 사용할 수 있게 제공합니다
- Stage와 Distill 없이도 기본 기록과 조회·수정 기능을 사용할 수 있고 두 호스트용 플러그인 구성을 제공합니다

## Next action

설계 검토 뒤 독립 사용 사례부터 RED 테스트를 작성합니다. 첫 구현은 로컬 명령과 스킬로 제공하고 웹 UI는 요구하지 않습니다.

## Related truth

SSOT, AHA, KISS, TDD, Honesty를 적용합니다. 부모의 사용자 합의가 이전 Avatar 구현 보류를 이번 범위에서 갱신합니다.

## Progress

2026-10-05: 구현 작업을 등록했습니다. avatar 디렉터리는 아직 만들지 않았습니다.

## Verification

독립 실행·변경 이력·범위 제한·중복 입력을 검사하고 두 호스트에서 명시적인 스킬 호출을 확인합니다.

## Retrospective

첫 독립 기능과 연결 확인 뒤 작성합니다.

## Promotion decision

pending
